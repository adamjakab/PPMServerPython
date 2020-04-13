#  Copyright: Copyright (c) 2020., Adam Jakab
#
#  Author: Adam Jakab <adam at jakab dot pro>
#  License: MIT

from abc import ABC
from abc import abstractmethod
from logging import Logger

from flask import request, session


class PPM_Request(ABC):
    _config = {}
    _request: request = None
    _logger: Logger = None
    _is_new_session = False

    def __init__(self, req, cfg, logger):
        self._request = req
        self._config = cfg
        self._logger = logger
        self.check_session()

    def check_session(self):
        self._is_new_session = "request_number" not in session
        if self._is_new_session:
            session["request_number"] = 1
        else:
            session["request_number"] += 1

    @abstractmethod
    def check(self):
        raise NotImplementedError("You must implement this method.")

    @staticmethod
    def get_request_number():
        return session["request_number"]


class PPM_UnencryptedRequest(PPM_Request):
    def __init__(self, req, cfg, logger):
        super().__init__(req, cfg, logger)
        self._logger.debug("PPM_UnencryptedRequest ready.")

    def check(self):
        if self._request.method != 'POST':
            raise RuntimeError("Bad request! Method '{}' is not allowed.".
                               format(self._request.method))

        self._logger.info("request check ok.")
