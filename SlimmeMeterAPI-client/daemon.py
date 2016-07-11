import configparser
from http.server import BaseHTTPRequestHandler, HTTPServer
import json

# Configuration reader
httpPort = int(config['client']['port'])
# Configuration reading done.

class webserverHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        print("POST detected!1")
