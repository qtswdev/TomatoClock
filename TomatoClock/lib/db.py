import atexit

import datetime

from anki.cards import Card
from anki.db import DB
from aqt import mw
from ..lib.constant import MIN_SECS, DEBUG

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


class loader(object):
    def load(self, path):
        try:
            tmp = {}
            exec open(path).read() in tmp
            return tmp
        except:
            return None


class TomatoDB(DB):

    def __init__(self, db_path):
        super(TomatoDB, self).__init__(db_path, str)

        # call start functions
        list(map(
            lambda _: getattr(self, _)(),
            [func for func in dir(self) if func.startswith("_start_")]
        ))

        # register close
        atexit.register(self.close)
        atexit.register(self.cleanup)

        self.cleanup()

    @property
    def statics(self):
        def _load_stats_mod():
            from .tomatostats import TomatoStats
            return {'TomatoStats': TomatoStats}

        if DEBUG:
            m = _load_stats_mod()
        else:
            try:
                m = loader().load("_tomatostats.py")
            except:
                m = _load_stats_mod()

        return m['TomatoStats'](self, DEBUG)

    def _start_ensure_tables(self):
        self.executescript(CREATION_SQL)

    def cleanup(self):
        self.execute(
            """
            DELETE FROM tomato_session_item where questioned is not null 
            and (answer_shown is  null 
            or answered is  null);
            """
        )
        self.execute("vacuum")

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

    @property
    def now(self):
        return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def execute(self, sql, *a, **ka):
        cur = super(TomatoDB, self).execute(sql, *a, **ka)
        self.commit()
        return cur

    # region Record

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
            """, self.now, self.session_item_id
        )

    def answer_card(self, ease):
        self.execute(
            """
            UPDATE tomato_session_item set answered = ? ,answer_btn = ?
            where id = ?
            """, self.now, ease, self.session_item_id
        )

    def end_session(self):
        self.execute(
            """
            UPDATE tomato_session set ended = ? where id = ?
            """, self.now, self.session_id
        )

    # endregion

    @property
    def _sql_total_tomato(self):
        return """
        select
          ts.tomato_dt                 TOMATO_DT,
          strftime('%w', ts.tomato_dt) WK_DAY,
          ts.id                        ID,
          ts.deck                      DECK,
          ts.target_secs               TARGET_SECS,
          case ts._mode
          when 0
            then 'Focus'
          when 1
            then 'Normal'
          end as                       'MODE'
        from tomato_session ts
        WHERE ended IS NOT NULL AND
              round((strftime('%s', ts.ended) - strftime('%s', ts.started)), 2)
              >= ts.target_secs
        """

    @property
    def _sql_tomato_detail(self):
        return """
        select
             TSI.session_id                                                    SESSION_ID,
             tsi.id                                                            ITEM_ID,
             strftime('%s', TSI.answer_shown) - strftime('%s', TSI.questioned) 'RECALL_SECS',
             strftime('%s', TSI.answered) - strftime('%s', TSI.questioned)     'ANSWER_SECS',
             TSI.answer_btn                                                    BTN
        
           from tomato_session_item tsi
           where tsi.answer_shown is not null and tsi.answered is not null
        """

    # def statics(self, recent_days=0):
    #     return self.execute("""
    #     select
    #       *
    #     from (%s) total_tomato
    #       left join
    #       (%s) tomato_detail
    #         on total_tomato.ID = tomato_detail.SESSION_ID
    #     where total_tomato.TOMATO_DT = ?
    #     """ % (
    #         self._sql_total_tomato, self._sql_tomato_detail
    #     ), (datetime.datetime.now() +
    #         datetime.timedelta(days=recent_days)).strftime('%Y-%m-%d'))

    def stat_tomato_count(self, recent_days):
        """

        :param recent_days:
        :return: list of [dt, mode, count]
        """
        return self.execute(
            """
            select
              ts.tomato_dt                 TOMATO_DT,
              sum(ts.target_secs) / 60 MINS,
              count(ts.id) COUNT
            from tomato_session ts
            
            WHERE ended IS NOT NULL AND
                  round((strftime('%s', ts.ended) - strftime('%s', ts.started)), 2)
                  >= ts.target_secs
                  and ts.tomato_dt >= ?
            group by ts.tomato_dt
            """, (datetime.datetime.now() +
                  datetime.timedelta(days=recent_days)).strftime('%Y-%m-%d'), ).fetchall()

    def stat_tomato_hour(self, recent_days):
        """

        :param recent_days:
        :return: list of [hr, mins, count]
        """
        return self.execute(
            """
            select
              strftime('%H',ts.started)                 HOUR,
              sum(ts.target_secs) / 60 MINS
            from tomato_session ts

            WHERE ended IS NOT NULL AND
                  round((strftime('%s', ts.ended) - strftime('%s', ts.started)), 2)
                  >= ts.target_secs
                  and ts.tomato_dt >= ?
            group by strftime('%H',ts.started)
            """, (datetime.datetime.now() +
                  datetime.timedelta(days=recent_days)).strftime('%Y-%m-%d'), ).fetchall()
