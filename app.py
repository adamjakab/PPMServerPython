#  Copyright: Copyright (c) 2020., Adam Jakab
#
#  Author: Adam Jakab <adam at jakab dot pro>
#  License: MIT

from flask import Flask, request, jsonify, session
from server.ppm_request import PPM_UnencryptedRequest
from server.ppm_response import PPM_UnencryptedResponse

# Create the application and load the configuration
app = Flask(__name__)
app.config.from_json("config.json")
ppm_route = app.config.get("PPM_ROUTE", "/ppm")

# Set the only route
@app.route(ppm_route, methods=['GET', 'POST', 'PUT', 'PATCH', 'DELETE'])
def ppm_handle_request():
    try:
        cfg = app.config.get("PPM_CONFIG")
        req = PPM_UnencryptedRequest(request, cfg, app.logger)
        rsp = PPM_UnencryptedResponse(req, cfg, app.logger)
        reply = jsonify(rsp.reply())
    except RuntimeError as err:
        session.clear()
        reply = "{}"
        app.logger.error(err)

    return reply

# Run
if __name__ == '__main__':
    app.run()
