#  Copyright: Copyright (c) 2020., Adam Jakab
#
#  Author: Adam Jakab <adam at jakab dot pro>
#  License: MIT

import sqlite3
from logging import Logger


class PPM_Storage:
    _config = {}
    _logger: Logger = None
    _conn = None

    def __init__(self, cfg, logger):
        self._config = cfg
        self._logger = logger
        self.setup_db()

    def setup_db(self):
        db_file = self._config["DATABASE_FILE"]
        self._conn = sqlite3.connect(db_file)
        c = self._conn.cursor()

        t = ('table', 'users',)
        sql = "SELECT name FROM sqlite_master WHERE type=? AND name=?"
        c.execute(sql, t)
        print(c.fetchone())
