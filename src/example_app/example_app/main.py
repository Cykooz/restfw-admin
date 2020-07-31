# -*- coding: utf-8 -*-
"""
:Authors: cykooz
:Date: 05.02.2020
"""
from __future__ import print_function
from wsgiref.simple_server import make_server
from wsgicors import CORS

from pyramid.config import Configurator


def main():
    with Configurator() as config:
        config.include('pyramid_debugtoolbar')
        config.include('example_app.users')
        config.include('example_app.documents')

        wsgi_app = config.make_wsgi_app()
        wsgi_app = CORS(
            wsgi_app,
            headers='*',
            expose_headers='Content-Length, X-Total-Count',
            methods='HEAD, OPTIONS, GET, POST, PUT, PATCH, DELETE',
            maxage='180',
            origin='copy',
        )

    server = make_server('0.0.0.0', 6543, wsgi_app)
    print('Server started on http://0.0.0.0:6543')
    server.serve_forever()
