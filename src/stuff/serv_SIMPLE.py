# Python 3 server example
from http.server import BaseHTTPRequestHandler, HTTPServer
from datetime import datetime
import time

hostName = "0.0.0.0" #"localhost"
serverPort = 8080


def isrequest(path):
    return path.startswith('/req/')

def log_successfull(msg):
    with open("logs.log", "a") as log:
        print(datetime.now(), msg.path[5:], file=log)


class MyServer(BaseHTTPRequestHandler):


    def do_GET(self):
        if isrequest(self.path):
            log_successfull(self)
            
            self.send_response(200)
        else:
            self.send_response(400)

        self.end_headers()
        print(self.path)

    # def do_POST(self):
    #     content_length = int(self.headers['Content-Length'])
    #     body = self.rfile.read(content_length)
    #     self.send_response(200)
    #     self.send_header('Content-type', 'text/html')
    #     self.end_headers()
    #     response = BytesIO()
    #     response.write(b'This is POST request. ')
    #     response.write(b'Received: ')
    #     response.write(body)
    #     self.wfile.write(response.getvalue())



if __name__ == "__main__":        
    webServer = HTTPServer((hostName, serverPort), MyServer)
    print("Server started http://%s:%s" % (hostName, serverPort))

    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        webServer.server_close()
        print("Server stopped.")