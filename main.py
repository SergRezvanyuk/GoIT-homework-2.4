import pathlib
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler
import mimetypes
import socket
from threading import Thread
from datetime import datetime
import requests
import json



BASE_DIR = pathlib.Path()

class MyServer(BaseHTTPRequestHandler):

    def do_POST(self):
        data = self.rfile.read(int(self.headers['Content-Length']))
        self.client_socket(data.decode())
        self.send_response(200)
        self.send_header('Location', '/message')
        self.end_headers()

    def do_GET(self):
        pr_url = urllib.parse.urlparse(self.path)
        match pr_url.path:
            case '/':
                self.send_html_file('index.html')
            case '/message':
                self.send_html_file('message.html')
            case _:
                file = BASE_DIR.joinpath(pr_url.path[1:])
                if file.exists():
                    self.send_static(file)
                else:
                    self.send_html_file('error.html', 404)
    


    def send_html_file(self, filename, status=200):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        with open(filename, 'rb') as fd:
            self.wfile.write(fd.read())

    def send_static(self, file):
        self.send_response(200)
        mt = mimetypes.guess_type(self.path)
        if mt:
            self.send_header('Content-type', mt[0])
        else:
            self.send_header('Content-type', 'text/plain')
        self.end_headers()
        with open(file, 'rb') as fd:
            self.wfile.write(fd.read())




    def client_socket(self, message):
        host = socket.gethostname()
        port = 5000
        client_socket = socket.socket()#socket.AF_INET, socket.SOCK_DGRAM)
        client_socket.connect((host, port))


        while message.lower():
            client_socket.send(message.encode())
            data = client_socket.recv(1024).decode()
            message = input('---> ')

        client_socket.close()


    

    

def server_socket():
    print('Serv. socket start')
    host = socket.gethostname()
    port = 5000
    server_socket = socket.socket()
    server_socket.bind((host, port))
    server_socket.listen(2)
    conn, address = server_socket.accept()
    print(f'Connection from {address}')
    while True:
        data = conn.recv(100).decode()
        if not data:
            break
        print(f'Received massege {data}')
        user = ''
        message = ''
        n=0
        u=True
        for n in range(len(data)):
            if u:
                user = user + data[n]
                if data[n] == '&':
                    u = False
            else:
                message = message + data[n]
        user = user[9:-1]
        message = message[8:]
        # print(f'username {user}, message {message}')


        data_json = {'username':user, 'message':message}
        data_json = {str(datetime.now()):data_json}
        with open(BASE_DIR.joinpath('storage/data.json'), 'w', encoding='utf-8') as fd:
            json.dump(data_json, fd, ensure_ascii=False)
            


    conn.close()

def run(server_class = HTTPServer, handler_class = MyServer):
    server_address = ('', 3000)
    http = server_class(server_address, handler_class)
    try:
        print('Start run')
        socket_server = Thread(target=server_socket)
        socket_server.start()
        http.serve_forever()
    except KeyboardInterrupt:
        http.server_close()

run()