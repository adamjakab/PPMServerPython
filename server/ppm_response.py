#  Copyright: Copyright (c) 2020., Adam Jakab
#
#  Author: Adam Jakab <adam at jakab dot pro>
#  License: MIT

from abc import ABC
from abc import abstractmethod
from logging import Logger

from server import utils
from server.ppm_request import PPM_Request
from server.ppm_storage import PPM_Storage


class PPM_Response(ABC):
    _config = {}
    _request = None
    _logger: Logger = None
    _response_data = {}

    _new_seed = None
    _new_pad_left = None
    _new_pad_right = None

    def __init__(self, request, cfg, logger):
        self._request = request
        self._config = cfg
        self._logger = logger

    def generate_new_seed(self):
        _min = self._config.get("SEED_MIN_LENGTH")
        _max = self._config.get("SEED_MAX_LENGTH")
        _chars = self._config.get("SEED_CHARS")
        self._new_seed = utils.get_ugly_string(_min, _max, _chars)

    def generate_new_padding_lengths(self):
        _min = self._config.get("PADDING_MIN_LENGTH")
        _max = self._config.get("PADDING_MAX_LENGTH")
        self._new_pad_left = utils.get_random_int(_min, _max)
        self._new_pad_right = utils.get_random_int(_min, _max)

    def generate_default_response_object(self):
        self._response_data = {
            "request_number": self._request.get_request_number(),
            "left_pad_length": self._new_pad_left,
            "right_pad_length": self._new_pad_right,
            "seed": self._new_seed
        }

    def handle_requested_service(self):
        service = self._request.get_requested_service()
        self._logger.debug("Service: {}".format(service))
        if "login" == service:
            pass
        elif "logout" == service:
            pass
        elif "ping" == service:
            pass
        elif "db" == service:
            db = PPM_Storage(self._config, self._logger)
        else:
            raise RuntimeError("Unknown service({}) requested!".format(service))

    @abstractmethod
    def reply(self):
        raise NotImplementedError("You must implement this method.")


class PPM_UnencryptedResponse(PPM_Response):
    def __init__(self, request, cfg, logger):
        super().__init__(request, cfg, logger)

        self._request.check()
        self._request.elaborate()
        # self._logger.debug("PPM_UnencryptedResponse ready.")
        self.generate_new_seed()
        self.generate_new_padding_lengths()
        self.generate_default_response_object()

        self.handle_requested_service()
        # self._response_data.update({})

    def reply(self):
        return self._response_data
