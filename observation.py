import numpy as np
import simulation 

class Observation:
    t = None
    rv = None
    err = None
    Npoints = 0

class FakeObservation(Observation):
    def __init__(self, theta, theta_names, Npoints=30, error_scale=5, tmax=1.5):
        """
            Generates fake observations. 
            error_scale is in m/s
            tmax is in years
        """
        self.Npoints = Npoints
        tmax *= 2.*np.pi
        s = simulation.Simulation(theta, theta_names)
        self.t = np.sort(np.random.uniform(0.,tmax,self.Npoints)).copy()
        self.rv = s.getRV(times=self.t)+np.random.normal(0.,error_scale,self.Npoints)
        self.err = np.full(self.Npoints,error_scale) 
