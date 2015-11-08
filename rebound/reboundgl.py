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

        content += '<canvas id="canvas{0:05d}" style="border: none;" width="700" height="250"></canvas>'.format(self.simid)
        content += "<script>webGLStart({0:05d});</script>".format(self.simid)
        content += "<script>"
        with open(os.path.join(this_dir, "socket.js"), 'r') as cfile:
            content += '\n{}\n'.format(cfile.read())
        content += "</script>";
        return content
    def update(self, sim):
        msg = {
            "id": 0,
            "N": sim.N,
            }
        ReboundSocketHandler.send_updates(msg)
        data = []
        for p in sim.particles:
            data.append(p.x)
            data.append(p.y)
            data.append(p.z)
        msg = {
            "id": 1,
            "data": data
            }
        ReboundSocketHandler.send_updates(msg)
    

import tornado.web
import tornado.websocket

class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/", MainHandler),
            (r"/reboundsocket", ReboundSocketHandler),
        ]
        tornado.web.Application.__init__(self, handlers)

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        return "test"

class ReboundSocketHandler(tornado.websocket.WebSocketHandler):
    clients = set()

    def get_compression_options(self):
        # Non-None enables compression with default options.
        return {}

    def open(self):
        ReboundSocketHandler.clients.add(self)

    def check_origin(self, origin):
        return True

    def on_close(self):
        ReboundSocketHandler.clients.remove(self)

    @classmethod
    def send_updates(cls, msg):
        for waiter in cls.clients:
            waiter.write_message(msg)

    def on_message(self, message):
        pass

class WebSocketServer():
    def __init__(self):
        self.app = Application()
        self.app.listen(8877)

