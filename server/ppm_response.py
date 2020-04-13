#  Copyright: Copyright (c) 2020., Adam Jakab
#
#  Author: Adam Jakab <adam at jakab dot pro>
#  License: MIT

from abc import ABC
from abc import abstractmethod
from logging import Logger

from server import utils
from server.ppm_request import PPM_Request


class PPM_Response(ABC):
    _config = {}
    _request: PPM_Request = None
    _logger: Logger = None
    _response_data = {}

    _new_seed = ""

    def __init__(self, request, cfg, logger):
        self._request = request
        self._config = cfg
        self._logger = logger

    def generate_new_seed(self):
        _min = self._config.get("SEED_MIN_LENGTH")
        _max = self._config.get("SEED_MAX_LENGTH")
        _chars = self._config.get("SEED_CHARS")
        self._new_seed = utils.get_ugly_string(_min, _max, _chars)

    @abstractmethod
    def reply(self):
        raise NotImplementedError("You must implement this method.")


class PPM_UnencryptedResponse(PPM_Response):
    _response_data = {}

    def __init__(self, request, cfg, logger):
        super().__init__(request, cfg, logger)
        self.generate_new_seed()
        try:
            self._request.check()
        except RuntimeError as err:
            self._logger.error(err)
        self._logger.debug("PPM_UnencryptedResponse ready.")

    def reply(self):
        self._response_data.update({
            "x": 123,
            "a": 122,
            "seed": self._new_seed,
            "request_number": self._request.get_request_number()
        })
        return self._response_data
