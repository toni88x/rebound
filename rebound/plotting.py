# -*- coding: utf-8 -*-
import math
from .particle import Particle


def OrbitPlot(sim, projection='', figsize=(5,5), lim=None, Narc=100, unitlabel=None, color=False, periastron=False, trails=False, lw=1.):
        """
        Convenience function for plotting instantaneous orbits.

        Parameters
        ----------
        sim             : simulation object
        projection      : string, optional
            Determines projection, '2d' or '3d' (default: '2d')
        figsize         : tuple of float, optional
            Tuple defining the figure size (default: (5,5))
        lim             : float, optional           
            Limit for axes (default: None = automatically determined)
        unitlabel       : str, optional          
            String describing the units, shown on axis labels (default: None)
        color           : bool, optional            
            Enable color (default: False)
        periastron  : bool, optional            
            Draw a marker at periastron (default: False)
        trails          : bool, optional            
            Draw trails instead of solid lines (default: False)
        lw              : float, optional           
            Linewidth (default: 1.)

        Returns
        -------
        fig
            A matplotlib figure

        Examples
        --------
        The following example illustrates a typical use case.

        >> sim = rebound.Simulation()
        >> sim.add(m=1)
        >> sim.add(a=1)
        >> fig = rebound.OrbitPlot(sim)
        >> fig.savefig("image.png") # save figure to file
        >> fig.show() # show figure on screen

        """
        try:
            import matplotlib.pyplot as plt
            from matplotlib.patches import Circle, PathPatch
            from mpl_toolkits.mplot3d import Axes3D, art3d
            import numpy as np
        except:
            raise ImportError(
                "Error importing matplotlib and/or numpy. "
                "Plotting functions not available. "
                "If running from within a jupyter notebook, try calling '%matplotlib inline' beforehand."
            )

        fig = plt.figure(figsize=figsize)
        if projection == '3d':
            ax = fig.add_subplot(111, projection='3d')
        else:
            ax = fig.add_subplot(111)
        orbits = sim.calculate_orbits()
        particles = sim.particles
        x = [p.x for p in particles]
        y = [p.y for p in particles]
        z = [p.z for p in particles]
        if lim is None:
            lim = 0.
            for o in orbits:
                if o.a > 0.:
                    r = (1. + o.e) * o.a
                else:
                    r = o.d
                if r > lim:
                    lim = r
        ax.set_xlim([-lim, lim])
        ax.set_ylim([-lim, lim])
        if projection == '3d':
            # Add z-axis limits if projection is '3d'.
            ax.set_zlim([-lim, lim])

        if unitlabel is not None:
            unitlabel = " " + unitlabel
        else:
            length_unit = sim.units['length']
            if not length_unit:
                unitlabel = " [AU]"  # Default length unit. TODO: get that from sim object.
            else:
                unitlabel = " [%s]" % length_unit
        ax.set_xlabel("x" + unitlabel)
        ax.set_ylabel("y" + unitlabel)
        if projection == '3d':
            # Add z-axis label if projection is '3d'.
            ax.set_zlabel("z" + unitlabel)

        if color:
            cm = plt.get_cmap("jet")
        else:
            cmf = plt.get_cmap("Greys")
            cm = lambda x: cmf(x / 2. + 0.5)

        if projection == '3d':
            ax.scatter(particles[0].x, particles[0].y, particles[0].z, marker="*", s=35 * lw, facecolor="black", edgecolor=None, zorder=3)
        else:
            ax.scatter(particles[0].x, particles[0].y, marker="*", s=35 * lw, facecolor="black", edgecolor=None, zorder=3)

        for i, o in enumerate(orbits):
            primary = sim.calculate_com(i + 1)
            colori = cm(float(i + 1) / float(sim.N - 1))
            pp = Particle(a=o.a, f=o.f, inc=o.inc, omega=o.omega, Omega=o.Omega, e=o.e, m=particles[i + 1].m, primary=primary, simulation=sim)
            if projection == '3d':
                ax.scatter(pp.x, pp.y, pp.z, s=25 * lw, facecolor="black", edgecolor=None, zorder=3)
            else:
                ax.scatter(pp.x, pp.y, s=25 * lw, facecolor="black", edgecolor=None, zorder=3)
            if o.a > 0.:  # bound orbit
                phase = np.linspace(0, 2. * np.pi, Narc)
                for ph in phase:
                    newp = Particle(a=o.a, f=o.f + ph, inc=o.inc, omega=o.omega, Omega=o.Omega, e=o.e, m=particles[i + 1].m, primary=primary, simulation=sim)
                    if trails:
                        alpha = ph / (2. * np.pi)
                        color = (colori[0], colori[1], colori[2], alpha)
                    else:
                        color = colori
                    if projection == '3d':
                        ax.plot([pp.x, newp.x], [pp.y, newp.y], [pp.z, newp.z], color=color, zorder=2, lw=lw)
                    else:
                        ax.plot([pp.x, newp.x], [pp.y, newp.y], color=color, zorder=2, lw=lw)
                    pp = newp
            else:
                # Unbound orbit. Step in M rather than f, since for hyperbolic orbits f stays near lim, and jumps to -f at peri.
                pp = None
                t_cross = 2 * o.d / o.v  # rough time to cross display box
                lim_phase = abs(o.n) * t_cross  # M = nt, n is negative
                phase = np.linspace(-lim_phase, lim_phase, Narc)
                # add particle phase manually
                p_i = np.searchsorted(phase, o.M)
                phase = np.insert(phase, p_i, o.M)
                tail_length = o.M + lim_phase 
                for ph in phase:
                    newp = Particle(a=o.a, M=ph, inc=o.inc, omega=o.omega, Omega=o.Omega, e=o.e, m=particles[i + 1].m, primary=primary, simulation=sim)
                    if trails:
                        if ph <= o.M:
                            alpha = 1. - abs(o.M - ph) / tail_length
                        else:
                            alpha = 0.2
                        color = (colori[0], colori[1], colori[2], alpha)
                    else:
                        color = colori
                    if pp is not None:
                        if projection == '3d':
                            ax.plot([pp.x, newp.x], [pp.y, newp.y], [pp.z, newp.z], color=color, zorder=2, lw=lw)
                        else:
                            ax.plot([pp.x, newp.x], [pp.y, newp.y], color=color, zorder=2, lw=lw)
                    pp = newp

            if periastron:
                newp = Particle(a=o.a, f=0., inc=o.inc, omega=o.omega, Omega=o.Omega, e=o.e, m=particles[i + 1].m, primary=primary, simulation=sim)
                if projection == '3d':
                    ax.plot([primary.x, newp.x], [primary.y, newp.y], [primary.z, newp.z], linestyle="dotted", c=colori, zorder=1, lw=lw)
                    ax.scatter([newp.x], [newp.y], [newp.z], marker="o", s=5. * lw, facecolor="none", edgecolor=colori, zorder=1)
                else:
                    ax.plot([primary.x, newp.x], [primary.y, newp.y], linestyle="dotted", c=colori, zorder=1, lw=lw)
                    ax.scatter([newp.x], [newp.y], marker="o", s=5. * lw, facecolor="none", edgecolor=colori, zorder=1)
        return fig
