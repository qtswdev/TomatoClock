
CREATION_SQL = """
CREATE TABLE tomato_session
(
  id                INTEGER  NOT NULL
    PRIMARY KEY
  AUTOINCREMENT,
  deck              INT      NOT NULL,
  tomato_target     INT      NOT NULL,
  tomato_dt         DATE     NOT NULL,
  started           DATETIME NOT NULL,
  ended             DATETIME NOT NULL,
  answer_limit_secs INT
);

CREATE TABLE session_detail
(
  id            INTEGER NOT NULL
    PRIMARY KEY
  AUTOINCREMENT,
  session_id    INT     NOT NULL
    CONSTRAINT session_detail_tomato_session_id_fk
    REFERENCES tomato_session (id)
      ON UPDATE CASCADE
      ON DELETE CASCADE,
  item_started  DATETIME,
  item_answered DATETIME,
  answer_btn    INT
);
"""
