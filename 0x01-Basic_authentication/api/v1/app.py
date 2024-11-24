#!/usr/bin/env python3
"""This module contains the Flask app and the routes for the API."""
import os
from flask import Flask, jsonify, abort, request
from os import getenv
from api.v1.views import app_views
from flask_cors import (CORS, cross_origin)


app = Flask(__name__)
app.register_blueprint(app_views)
CORS(app, resources={r"/api/v1/*": {"origins": "*"}})
basic_py_auth = None
AUTH_TYPE = os.getenv("AUTH_TYPE")
if AUTH_TYPE == "auth":
    from api.v1.basic_py_auth.basic_py_auth import Auth
    basic_py_auth = Auth()
elif AUTH_TYPE == "basic_auth":
    from api.v1.basic_py_auth.basic_auth import BasicAuth
    basic_py_auth = BasicAuth()


@app.before_request
def bef_req():
    """Handle the case where the request is not authorized"""
    if basic_py_auth is None:
        pass
    else:
        excluded = [
            '/api/v1/status/',
            '/api/v1/unauthorized/',
            '/api/v1/forbidden/'
        ]
        if basic_py_auth.require_auth(request.path, excluded):
            if basic_py_auth.authorization_header(request) is None:
                abort(401, description="Unauthorized")
            if basic_py_auth.current_user(request) is None:
                abort(403, description="Forbidden")


@app.errorhandler(404)
def not_found(error) -> str:
    """In case of unsuccessfull authentication, throw a 404 error"""
    return jsonify({"error": "Not found"}), 404


@app.errorhandler(401)
def unauthorized(error) -> str:
    """In case of unsuccessfull authentication, throw a 401 error"""
    return jsonify({"error": "Unauthorized"}), 401


@app.errorhandler(403)
def forbidden(error) -> str:
    """In case of unsuccessfull authentication, throw a 403 error"""
    return jsonify({"error": "Forbidden"}), 403


if __name__ == "__main__":
    host = getenv("API_HOST", "0.0.0.0")
    port = getenv("API_PORT", "5000")
    app.run(host=host, port=port)