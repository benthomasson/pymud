#!/usr/bin/env python
from BaseHTTPServer import BaseHTTPRequestHandler,HTTPServer

class ApiHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type','text/html')
        self.end_headers()
        self.wfile.write("hi")
        return

if __name__ == "__main__":
    try:
        server = HTTPServer(('',9000),ApiHandler)
        print 'started'
        server.serve_forever()
    except KeyboardInterrupt:
        print 'stopped'
        server.socket.close()


