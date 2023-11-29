import http.server
import socketserver
import threading
import socket
import json
from datetime import datetime

PORT = 8000

class MyHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        pass

class SocketServer:
    def __init__(self):
        pass
    
    def start(self):
        pass
    
    