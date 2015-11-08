import os
import rebound


class ReboundGL():
    def __init__(self,sim):
        self.simid = id(sim)
        try:
            WebSocketServer()
        except:
            pass

    def _repr_html_(self):
        this_dir, this_filename = os.path.split(__file__)
        content = ""
        content += "<script>"
        with open(os.path.join(this_dir, "glMatrix-0.9.5.min.js"), 'r') as cfile:
            content += '\n{}\n'.format(cfile.read())
        content += "</script>";
        with open(os.path.join(this_dir, "webglframework.js"), 'r') as cfile:
            content += '\n{}\n'.format(cfile.read())

        content += '<canvas id="canvas{0:05d}" style="border: none;" width="700" height="150"></canvas>'.format(self.simid)
        content += "<script>webGLStart({0:05d});</script>".format(self.simid)
        content += "<script>"
        with open(os.path.join(this_dir, "socket.js"), 'r') as cfile:
            content += '\n{}\n'.format(cfile.read())
        content += "</script>";
        return content
    def update(self):
        pass
        #p = self.sim.particles[1]
        #x, y = p.x, p.y
        #self.shell.run_cell_magic("javascript", "","drawScene({},{})".format(x, y))
        #Javascript("console.log(3)")
        
    


import tornado.escape
import tornado.ioloop
import tornado.web
import tornado.websocket
import os.path
import math
import datetime

class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/", MainHandler),
            (r"/chatsocket", ChatSocketHandler),
        ]
        tornado.web.Application.__init__(self, handlers)

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        return "test"

class ChatSocketHandler(tornado.websocket.WebSocketHandler):
    waiters = set()

    def get_compression_options(self):
        # Non-None enables compression with default options.
        return {}

    def open(self):
        print "open"
        ChatSocketHandler.waiters.add(self)
        tornado.ioloop.IOLoop.instance().add_timeout(datetime.timedelta(seconds=0.01), self.test)

    t = 0.
    refreshinterval = 1./50.
    def test(self):
        self.t += 0.1
        chat = {
            "id": 0,
            "x": 3.*math.cos(self.t),
            "y": math.sin(self.t),
            }
        ChatSocketHandler.send_updates(chat)
        tornado.ioloop.IOLoop.instance().add_timeout(datetime.timedelta(seconds=self.refreshinterval), self.test)
        

    def check_origin(self, origin):
        return True

    def on_close(self):
        ChatSocketHandler.waiters.remove(self)

    @classmethod
    def send_updates(cls, chat):
        for waiter in cls.waiters:
            waiter.write_message(chat)

    def on_message(self, message):
        parsed = tornado.escape.json_decode(message)

class WebSocketServer():
    def __init__(self):
        print("Tornado websocket listening on port 8877")
        self.app = Application()
        self.app.listen(8877)

