#  Copyright: Copyright (c) 2020., Adam Jakab
#
#  Author: Adam Jakab <adam at jakab dot pro>
#  License: MIT

from flask import Flask, request, jsonify
from server.ppm_request import PPM_UnencryptedRequest
from server.ppm_response import PPM_UnencryptedResponse

# Create the application and load the configuration
app = Flask(__name__)
app.config.from_json("config.json")
ppm_route = app.config.get("PPM_ROUTE", "/ppm")


# Set the only route
@app.route(ppm_route, methods=['GET', 'POST', 'PUT', 'PATCH', 'DELETE'])
def ppm_handle_request():
    cfg = app.config.get("PPM_CONFIG")
    req = PPM_UnencryptedRequest(request, cfg, app.logger)
    resp = PPM_UnencryptedResponse(req, cfg, app.logger)
    return jsonify(resp.reply())


# Run
if __name__ == '__main__':
    app.run()
