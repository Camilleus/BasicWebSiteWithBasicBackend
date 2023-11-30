import http.server
import urllib.parse
import urllib.request
import mimetypes
import socket
import socketserver
import threading
import json
from datetime import datetime
import pathlib

HOST = 'localhost'
HTTP_PORT = 3000
SOCKET_PORT = 5000

class HttpHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        pr_url = urllib.parse.urlparse(self.path)
        if pr_url.path == '/':
            self.send_html_file('index.html')
        elif pr_url.path == '/message':
            self.send_html_file('message.html')
        else:
            if pathlib.Path().joinpath(pr_url.path[1:]).exists():
                self.send_static()
            else:
                self.send_html_file('error.html', 404)

    def send_html_file(self, filename, status=200):
        self.send_response(status)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        with open(filename, 'rb') as fd:
            self.wfile.write(fd.read())

    def do_POST(self):
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode('utf-8')
            data_dict = dict(urllib.parse.parse_qsl(post_data))

            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
            with open('storage/data.json', 'a') as file:
                json.dump({timestamp: data_dict}, file)
                file.write('\n')

            self.send_response(302)
            self.send_header('Location', '/')
            self.end_headers()

        except Exception as e:
            print(f"Error processing POST request: {e}")

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

class SocketServer:
    def __init__(self):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server.bind((HOST, SOCKET_PORT))
        self.storage = {}

    def start(self):
        while True:
            data, addr = self.server.recvfrom(1024)
            message = json.loads(data.decode())
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
            self.storage[timestamp] = message

            with open('storage/data.json', 'w') as file:
                json.dump(self.storage, file)

def run_http_server():
    handler = HttpHandler
    httpd = socketserver.TCPServer((HOST, HTTP_PORT), handler)
    print(f"HTTP server started on port {HTTP_PORT}")
    httpd.serve_forever()

if __name__ == '__main__':
    http_server_thread = threading.Thread(target=run_http_server)
    http_server_thread.start()

    socket_server = SocketServer()
    socket_server_thread = threading.Thread(target=socket_server.start)
    socket_server_thread.start()

    http_server_thread.join()
    socket_server_thread.join()
