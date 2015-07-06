import numpy as np
import rebound as r
import re
CU2MS = 29785.891  # Convert year/(2pi) to m/s
rename = re.compile("([^_]*)_([0-9]*)")

class Simulation:
    N = 0
    N_param = 0
    theta_names = []
    theta = []
    def __init__(self, theta, theta_names):
        self.theta = theta
        self.theta_names = theta_names
        self.N_param = len(theta)
        for i, name_full in enumerate(self.theta_names): # Find number of planets
            name, planetid = rename.match(name_full).groups()
            self.N = max(int(planetid)+1, self.N)


    def getPlanets(self, thetap=None):
        if thetap is None:
            thetap = self.theta
        # Defaults
        a = np.full(self.N,1.)
        anom = np.full(self.N,0.)
        m = np.full(self.N,1e-3)
        h = np.full(self.N,0.0)
        k = np.full(self.N,0.0)
        for i, name_full in enumerate(self.theta_names):
            name, planetid = rename.match(name_full).groups()
            planetid = int(planetid) 
            if name == "a":
                a[planetid] = thetap[i]
            elif name == "anom":
                anom[planetid] = thetap[i]
            elif name == "m": 
                m[planetid] = thetap[i]    
            elif name == "h": 
                h[planetid] = thetap[i]    
            elif name == "k": 
                k[planetid] = thetap[i]    

        star = r.Particle(m=1.)
        planets = [star]
        for planetid in range(1,self.N):
            planets.append(r.Particle(primary=star,
                                      m = m[planetid],
                                      a = a[planetid],
                                      e = np.sqrt(h[planetid]*h[planetid]+k[planetid]*k[planetid]),
                                      anom = anom[planetid],
                                      omega = np.arctan2(h[planetid],k[planetid]))
                          )
        return planets

    def getRV(self, times):
        r.reset()
        r.add(self.getPlanets())
        r.move_to_com()
        ps = r.particles
        rvs = np.zeros(len(times))
        for i,t in enumerate(times):
            r.integrate(t)
            rvs[i] = ps[0].vx*CU2MS
        return rvs


    def varid2(self, l,k):
        var = l*(l+1)/2+k
        return var+1+self.N_param

    def varid1(self, l):
        return 1*l+1

    def getLogP(self, obs, derivatives=True):
        r.reset()
        r.add(self.getPlanets())
        r.move_to_com()
        
        if derivatives:
            delta = 1e-4
            # First order
            for l in range(self.N_param):
                thetas2 = self.theta.copy()
                thetas2[l] += delta/2.
                mp = self.getPlanets(thetas2)
                thetas2[l] -= delta
                mm = self.getPlanets(thetas2)

                for i in range(self.N):
                    mp[i].m  -= mm[i].m  
                    mp[i].x  -= mm[i].x  
                    mp[i].y  -= mm[i].y  
                    mp[i].z  -= mm[i].z  
                    mp[i].vx -= mm[i].vx 
                    mp[i].vy -= mm[i].vy 
                    mp[i].vz -= mm[i].vz 

                r.add(mp)
                r.move_var_to_com(self.N,self.varid1(l))

            # Second order
            for l in range(self.N_param):
                for k in range(l+1):
                    thetas2 = self.theta.copy()
                    thetas2[l] += delta/2.
                    thetas2[k] += delta/2.
                    mpp = self.getPlanets(thetas2)
                    thetas2[k] -= delta
                    mpm = self.getPlanets(thetas2)
                    thetas2[l] -= delta
                    mmm = self.getPlanets(thetas2)
                    thetas2[k] += delta
                    mmp = self.getPlanets(thetas2)

                    for i in range(self.N):
                        mpp[i].m  += - mpm[i].m  - mmp[i].m  + mmm[i].m
                        mpp[i].x  += - mpm[i].x  - mmp[i].x  + mmm[i].x
                        mpp[i].y  += - mpm[i].y  - mmp[i].y  + mmm[i].y 
                        mpp[i].z  += - mpm[i].z  - mmp[i].z  + mmm[i].z 
                        mpp[i].vx += - mpm[i].vx - mmp[i].vx + mmm[i].vx
                        mpp[i].vy += - mpm[i].vy - mmp[i].vy + mmm[i].vy
                        mpp[i].vz += - mpm[i].vz - mmp[i].vz + mmm[i].vz

                    r.add(mpp)
                    r.move_var_to_com(self.N,self.varid2(l,k))
            r.N_megnopp = self.N_param 
            r.N_megno   = self.N*self.N_param
            r.N_megno2  = self.N*(self.N_param+1)*(self.N_param)/2
        
        ps = r.particles

        ##################################################################
        # INTEGRATION
        logps   = 0.
        if derivatives:
            logp_d  = np.zeros(self.N_param)
            logp_d2 = np.zeros((self.N_param*(self.N_param+1)/2,2))
        for i,t in enumerate(obs.t):
            r.integrate(t)
            dv     = ps[0].vx*CU2MS-obs.rv[i]
            derri  = 1./(2.*(obs.err[i]**2))
            logps += -dv**2*derri
            if derivatives:
                for k in range(self.N_param):
                    vari1 = self.varid1(k)*self.N
                    logp_d[k] += -2.*ps[vari1].vx*CU2MS/delta * dv*derri
                _id = 0
                for l in range(self.N_param):
                    for k in range(l+1):
                        vari2  = self.varid2(l,k)*self.N
                        vari1l = self.varid1(l)*self.N
                        vari1k = self.varid1(k)*self.N
                        logp_d2[_id][0] += -2.*(ps[vari1l].vx*CU2MS * ps[vari1k].vx*CU2MS)/(delta*delta)*derri
                        # Expectation value would remove next line, still a valid metric, but less useful
                        logp_d2[_id][1] += -2.*(ps[vari2].vx*CU2MS * dv)/(delta*delta)*derri
                        _id += 1
        
        if derivatives:
            logp_d2m = np.zeros((self.N_param,self.N_param))
            _id = 0
            for l in range(self.N_param):
                for k in range(l+1):
                    fdd = logp_d2[_id][0] + logp_d2[_id][1]
                    logp_d2m[l,k] = fdd
                    logp_d2m[k,l] = fdd
                    _id +=1

            return logps, logp_d, logp_d2m
        else:
            return logps
