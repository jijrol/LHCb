#
#Plotter for discrepancy between Btracking path: PV-SV
# and  actual path of B+ -> tau+ -> pi^3
# and angle between Btracking path and B+ path.

#Jan Rol, 12-6-2020

import random
import math
import ROOT as R
import numpy as np
import matplotlib
import matplotlib.pyplot as plt

max_sensors = 52
dz_module = 30000         # in mum, since RapidSim uses mum
rmin = 5100               # in mum
rmax = 84000              # in mum

const_c        = 3e2      # [mum/ps]
const_t_bplus  = 1.638    # [ps]
const_m_bplus  = 5279.33  # [MeV/c^2]

h_distance = R.TH1F("h_distance", "h_distance", nbins, 0, 1000)
h_angle    = R.TH1F("h_angle", "h_angle", nbins, 0, 10)


def z_active(p, eta, t=const_t_plus, m=const_m_bplus):
    d     = const_c * t * p / m                    # total distance travelled
    theta = 2. * math.atan(math.exp(-eta))         # angle wrt beam axis from pseudorapidity
    dmin  = rmin / math.sin(theta)                 # minimum distance travelled to get to edge of detector
    d_a   = d-dmin if d>dmin else 0.0              # "active" distance in detector region
    z_a   = d_a * math.cos(theta)                  # "active" distance along beam axis in [mm]
    return z_a

def n_sensors(z_active):
    r_act = z_active / dz_module
    n_sensors = r_act + random.random()
    if n_act > max_sensors:
        n_act = max_sensors
    return int(math.floor(n_act))

def angle(U, V):
    projection = np.dot(U, V) / (np.linalg.norm(U) * np.linalg.norm(V))
    if projection >= 1:
        print("normalized dotprodcut >= 1!")
    theta = (180 / math.pi) * np.arccos(projection) #in degrees
    return theta

def cart_coords(theta, phi):
    x = np.sin(theta) * np.cos(phi)
    y = np.sin(theta) * np.sin(phi)
    z = np.cos(theta)
    return [x, y, z]

def distance(vertex1, vertex2):
	sum = 0
	for i in range(0, 2):
        sum += (vertex1[i] - vertex2[i])**2
    distance = math.sqrt(sum)
    return distance

treeloc = "/project/bfys/jrol/data"
f_tree = R.TFile.Open("{1}/{0}_tree.root".format(treeloc, "Bp2tau2pipipi"))
tree = f_tree.Get("DecayTree")

for i in range(0, tree.GetEntries()):
    tree.GetEntry(i)
    Bp_P = getattr(tree, "Bp_0_P_TRUE"); Bp_PT = getattr(tree, "Bp_0_PT_TRUE")
    Bp_eta = math.acosh(Bp_P / Bp_PT)
    z_active = z_active(Bp_P, Bp_eta)
    if n_sensors(z_active) >= 1: 
        PV = [getattr(tree, ""), getattr(tree, ""), getattr(tree, "")]       #PV coords
        BV = [getattr(tree, ""), getattr(tree, ""), getattr(tree, "")]       #B+ decay vertex coords
        TV = [getattr(tree, ""), getattr(tree, ""), getattr(tree, "")]       #tau+ decay vertex coords, ie. SV
        tau_P = [getattr(tree, ""), getattr(tree, ""), getattr(tree,  "")]
        Bp_P  = [getattr(tree, ""), getattr(tree, ""), getattr(tree,  "")]
        PVBV = BV - PV; PVSV = SV - PV
        theta = angle(PVBV, PVSV)
        d = sin(theta) * distance(BV, PV)
        h_angle.Fill(theta)
        h_distance.Fill(d)
h_angle.Draw(); input()
h_distance.Draw(); input()
