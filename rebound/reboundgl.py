import os
import rebound
from IPython.core.magic import (Magics, magics_class, line_magic)
#from IPython.display import Javascript


class ReboundGL():
    def __init__(self,shell,sim):
        sim.gl     = self
        self.shell = shell
        self.sim   = sim
        self.simid = id(sim)
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

        content += '<canvas id="canvas{0:05d}" style="border: none;" width="700" height="300"></canvas>'.format(self.simid)
        content += "<script>webGLStart({0:05d});</script>".format(self.simid)
        return content
    def update(self):
        p = self.sim.particles[1]
        x, y = p.x, p.y
        self.shell.run_cell_magic("javascript", "","drawScene({},{})".format(x, y))
        #Javascript("console.log(3)")
        
    

@magics_class
class RebMagics(Magics):
    @line_magic
    def webgl(self, line):
        print 
        shell = self.shell
        sim = self.shell.ev(line)
        return ReboundGL(shell,sim)
        

ip = get_ipython()
ip.register_magics(RebMagics)


        
    
