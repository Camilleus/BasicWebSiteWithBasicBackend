import http.server
import socketserver
import urllib.parse
import threading
import socket
import json
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

class ClientHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        pr_url = urllib.parse.urlparse(self.path)
        if pr_url.path == '/':
            self.send_html_file('index.html')
        elif pr_url.path == '/message':
            self.send_html_file('contact.html')
        else:
            self.send_html_file('error.html', 404)
            
    def send_html_file(self, filename, status=200):
        self.send_response(status)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        with open(filename, 'rb') as fd:
            self.wfile.write(fd.read())
        
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
        logging.info("Socket server started on port 5000")
        while True:
            data, addr = self.server.recvfrom(1024)
            message = json.loads(data.decode())
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
            self.storage[timestamp] = message

            with open('storage/data.json', 'w') as file:
                json.dump(self.storage, file)

def start_http_server():
    handler = ClientHandler
    httpd = socketserver.TCPServer(('localhost', 3000), handler)
    logging.info("HTTP server started on port 3000")
    httpd.serve_forever()

def run(server_class=SocketServer, handler_class=ClientHandler):
    server_address = ('', 8000)
    http = server_class(server_address, handler_class)
    try:
        http.serve_forever()
    except KeyboardInterrupt:
        http.server_close()

def send_static(self):
    self.send_response(200)
    mt = mimetypes.guess_type(self.path)
    if mt:
        self.send_header("Content-type", mt[0])
    else:
        self.send_header("Content-type", 'text/plain')
    self.end_headers()
    with open(f'.{self.path}', 'rb') as file:
        self.wfile.write(file.read())
        
        
if __name__ == '__main__':
    run()
    
http_server_thread = threading.Thread(target=start_http_server)
http_server_thread.start()

socket_server = SocketServer()
socket_server_thread = threading.Thread(target=socket_server.start)
socket_server_thread.start()

http_server_thread.join()
socket_server_thread.join()
