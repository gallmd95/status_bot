from bottle import Bottle, get, run, ServerAdapter, request
import os

bot_token = os.environ["BOT_TOKEN"]

class SSLWSGIRefServer(ServerAdapter):
    def run(self, handler):
        from wsgiref.simple_server import make_server, WSGIRequestHandler
        import ssl
        if self.quiet:
            class QuietHandler(WSGIRequestHandler):
                def log_request(*args, **kw): pass
            self.options['handler_class'] = QuietHandler
        srv = make_server(self.host, self.port, handler, **self.options)
        srv.socket = ssl.wrap_socket (
         srv.socket,
         certfile='server.pem',
         server_side=True)
        srv.serve_forever()

status = {}

team = [("Usman",0), ("Gabi",0), ("Joe",0),("Walter",0),("Jeffery",0),("Eric",0),("Manny",0),("Bao",0), ("Hiren",0), ("Ankita",0), ("Glen",0),("Jake",0), ]
for each in team:
    status[each[0]] = {}

def send_email():
    print "mail"

@get("/status")
def get_status():
 print "Got it"
 return "here"

@get("/meet")
def get_meet():
    send_email()

srv = SSLWSGIRefServer(host="status.local", port=8081)
run(server=srv)