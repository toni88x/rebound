import os
import rebound

class ReboundGL():
    sim = None
    def __init__(self, reb_sim): 
        self.sim = reb_sim
        pass
    def _repr_html_(self):
        this_dir, this_filename = os.path.split(__file__)
        content = ""
        content += "<div id=\"container\"></div>\n"
        content += "<script>"
        with open(os.path.join(this_dir, "glMatrix-0.9.5.min.js"), 'r') as cfile:
            content += '\n{}\n'.format(cfile.read())
        content += "</script>";
        with open(os.path.join(this_dir, "webglframework.js"), 'r') as cfile:
            content += '\n{}\n'.format(cfile.read())

        content += '<canvas id="canvas{0:05d}" style="border: none;" width="700" height="300"></canvas>'.format(id(self.sim))
        content += "<script>webGLStart({0:05d});</script>".format(id(self.sim))
        return content
    
