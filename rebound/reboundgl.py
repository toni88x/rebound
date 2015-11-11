import os
import rebound


class ReboundGL():
    def __init__(self,sim):
        self.simid = "{0:05d}".format(id(sim))
        try:
            self.app = Application()
            self.app.listen(8877)
        except:
            pass

    def _repr_html_(self):
        this_dir, this_filename = os.path.split(__file__)
        # Static JS (TODO: should be outputted only once)
        content = ""
        content += "<script>"
        with open(os.path.join(this_dir, "glMatrix-0.9.5.min.js"), 'r') as cfile:
            content += '\n{}\n'.format(cfile.read())
        with open(os.path.join(this_dir, "webglframework.js"), 'r') as cfile:
            content += '\n{}\n'.format(cfile.read())
        content += "</script>";
        
        # Canvas specific JS + HTML
        with open(os.path.join(this_dir, "shaders.js"), 'r') as cfile:
            content += '\n{}\n'.format(cfile.read().replace("{simid}",self.simid))
        content += '<canvas id="canvas{}" style="border: none;" width="400" height="400"></canvas>'.format(self.simid)
        content += "<script>"
        content += "var rebContext{} = {{}};\n".format(self.simid);
        content += "startRebContext(rebContext{}, {});\n".format(self.simid,self.simid);
        content += "</script>";
        return content

    def update(self, sim):
        scale = 1.
        if sim.root_size != -1.:
            scale = 0.20*sim.root_size
        data = []
        for p in sim.particles:
            data.append(p.x)
            data.append(p.y)
            data.append(p.z)
        msg = {
            "N": sim.N,
            "scale": scale,
            "data": data
            }
        ReboundSocketHandler.send_updates(msg, self.simid)
    

import tornado.web
import tornado.websocket

class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/reboundsocket", ReboundSocketHandler),
        ]
        tornado.web.Application.__init__(self, handlers)

class ReboundSocketHandler(tornado.websocket.WebSocketHandler):
    lastmsg = None
    clients = dict()

    def get_compression_options(self):
        # Non-None enables compression with default options.
        return {}

    def open(self):
        # Registration of clients done after first request.
        pass

    def check_origin(self, origin):
        return True

    def on_close(self):
        deletek = None
        for k,v in ReboundSocketHandler.clients.iteritems():
            if v == self:
                deletek = k
        if deletek is not None:
            del ReboundSocketHandler.clients[deletek]

    @classmethod
    def send_updates(cls, msg, simid):
        cls.lastmsg = msg
        for k,waiter in cls.clients.iteritems():
            if k == simid:
                waiter.write_message(msg)

    def on_message(self, message):
        if message not in ReboundSocketHandler.clients:
            ReboundSocketHandler.clients[message] = self
            if ReboundSocketHandler.lastmsg is not None:
                ReboundSocketHandler.send_updates(ReboundSocketHandler.lastmsg,message)
        pass
