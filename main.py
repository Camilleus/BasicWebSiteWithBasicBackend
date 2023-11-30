import http.server
import socketserver
import threading
import socket
import json
import logging
from datetime import datetime


logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S')


class ClientHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/message':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            with open('message.html', 'rb') as file:
                self.wfile.write(file.read())
        elif self.path == '/error':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            with open('error.html', 'rb') as file:
                self.wfile.write(file.read())
        elif self.path == '/styles.css':
            self.send_response(200)
            self.send_header('Content-type', 'text/css')
            self.end_headers()
            with open('styles.css', 'rb') as file:
                self.wfile.write(file.read())
        elif self.path == '/logo.png':
            self.send_response(200)
            self.send_header('Content-type', 'image/png')
            self.end_headers()
            with open('logo.png', 'rb') as file:
                self.wfile.write(file.read())
        else:
            self.send_response(302)
            self.send_header('Location', '/error')
            self.end_headers()

    def do_POST(self):
        if self.path == '/message':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode('utf-8')

            logging.info("Received POST data: %s", post_data)

            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b'Thank you for your message!')
            
class SocketServer:
    def __init__(self):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server.bind(('localhost', 5000))
        self.storage = {}
    
    def start(self):
        while True:
            data, addr = self.server.recvfrom(1024)
            message = json.loads(data.decode())
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
            self.storage[timestamp] = message

            with open('storage/data.json', 'w') as file:
                json.dump(self.storage, file)

def start_http_server():
    handler = http.server.SimpleHTTPRequestHandler
    httpd = socketserver.TCPServer(('localhost', 3000), handler)
    print("HTTP server started on port 3000")
    httpd.serve_forever()

http_server_thread = threading.Thread(target=start_http_server)
http_server_thread.start()

socket_server = SocketServer()
socket_server_thread = threading.Thread(target=socket_server.start)
socket_server_thread.start()

http_server_thread.join()
socket_server_thread.join()