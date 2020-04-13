#  Copyright: Copyright (c) 2020., Adam Jakab
#
#  Author: Adam Jakab <adam at jakab dot pro>
#  License: MIT
import json
from abc import ABC
from abc import abstractmethod
from json import JSONDecodeError
from logging import Logger

from flask import request, session


class PPM_Request(ABC):
    _config = {}
    _request: request = None
    _logger: Logger = None
    _is_new_session = False

    _request_data = {}

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

    @abstractmethod
    def elaborate(self):
        raise NotImplementedError("You must implement this method.")

    @staticmethod
    def get_request_number():
        return session["request_number"]

    def get_requested_service(self):
        service = None

        if "service" in self._request_data:
            service = self._request_data["service"]

        return service


class PPM_UnencryptedRequest(PPM_Request):
    def __init__(self, req, cfg, logger):
        super().__init__(req, cfg, logger)
        self._logger.debug("PPM_UnencryptedRequest ready.")

    def elaborate(self):
        try:
            self._request_data = json.loads(self._request.data)
        except JSONDecodeError:
            raise RuntimeError("Raw data cannot be loaded. \n{}".
                               format(self._request.data))

        self._logger.debug("Request: {}".format(self._request_data))

    def check(self):
        if self._request.method != 'POST':
            raise RuntimeError("Bad request! Method '{}' is not allowed.".
                               format(self._request.method))

        if not self._request.data:
            raise RuntimeError("Bad request! No raw data.")
