import atexit
import datetime

from anki.cards import Card
from anki.db import DB
from aqt import mw
from ..lib.constant import MIN_SECS

CREATION_SQL = """
create table if not exists tomato_session
(
  id                INTEGER  NOT NULL
    PRIMARY KEY
  AUTOINCREMENT,
  deck              INT      NOT NULL,
  target_secs     INT      NOT NULL,
  tomato_dt         DATE     NOT NULL,
  started           DATETIME NOT NULL,
  ended             DATETIME ,
  answer_limit_secs INT,
  _mode INT
);

create table if not exists tomato_session_item
(
  id            INTEGER NOT NULL
    PRIMARY KEY
  AUTOINCREMENT,
  session_id    INT     NOT NULL
    CONSTRAINT session_detail_tomato_session_id_fk
    REFERENCES tomato_session (id)
      ON UPDATE CASCADE
      ON DELETE CASCADE,
  questioned  DATETIME,
  answered DATETIME,
  answer_shown DATETIME,
  answer_btn    INT,
  card_id    INT,
  note_id    INT
);
"""


class TomatoDB(DB):
    @property
    def now(self):
        return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    def __init__(self, db_path):
        super(TomatoDB, self).__init__(db_path, str)

        # call start functions
        list(map(
            lambda _: getattr(self, _)(),
            [func for func in dir(self) if func.startswith("_start_")]
        ))

        # register close
        atexit.register(self.close)

    def _start_ensure_tables(self):
        self.executescript(CREATION_SQL)

    @property
    def session_id(self):
        return self.scalar("select seq from sqlite_sequence "
                           "where name=?", 'tomato_session')

    @property
    def session_item_id(self):
        return self.scalar("select seq from sqlite_sequence "
                           "where name=?", 'tomato_session_item')

    @property
    def card(self):
        """

        :rtype: Card
        """
        return mw.reviewer.card

    def execute(self, sql, *a, **ka):
        cur = super(TomatoDB, self).execute(sql, *a, **ka)
        self.commit()
        return cur

    def start_session(self, target_min, limit_secs, mode):
        self.execute(
            """
            INSERT INTO tomato_session(
            deck,target_secs,tomato_dt,started,ended,answer_limit_secs,_mode
            ) values (?,?,current_date,?,null ,?,?)
            """, self.card.did, target_min * MIN_SECS, self.now, limit_secs, mode
        )

    def question_card(self):
        self.execute(
            """
            INSERT INTO tomato_session_item(session_id, 
            questioned, 
            answered, 
            answer_btn, 
            card_id, 
            note_id) 
            VALUES(?,?,NULL,NULL,?,?)
            """, self.session_id, self.now, self.card.id, self.card.nid
        )

    def answer_shown(self):
        self.execute(
            """
            UPDATE tomato_session_item set answer_shown = ? where id = ?
            """, self.session_item_id
        )

    def answer_card(self, ease):
        self.execute(
            """
            UPDATE tomato_session_item set answered = ? ,answer_btn = ?
            where session_id= ? and card_id = ?
            """, self.now, ease, self.session_id, self.card.id
        )

    def end_session(self):
        self.execute(
            """
            UPDATE tomato_session set ended = ? where id = ?
            """, self.now, self.session_item_id
        )
