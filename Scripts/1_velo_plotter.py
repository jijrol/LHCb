# Plots of decay products from tree.root files for B+, Bc+, Ds+ or D+
# by Jan Rol 6-2-20202 

import sys
import math
import uproot
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import random 

if len(sys.argv) != 3:
    print("Give 2 arguments, first parent (Bplus, Bcplus, Dsplus or Dplus) then daughter(s) (mu, e or pipipi)")
    exit()

print(sys.argv)

parent   = sys.argv[1]
daughter = sys.argv[2]

max_sensors = 52
dz_module = 30000         # in mum, since RapidSim uses mum
minrange = 5100           # in mum
maxrange = 84000          # in mum

# All data stored in /project/bfys/jrol/RapidSim/decays/.../...
path = "/project/bfys/jrol/RapidSim/decays/{0}/{0}2tau2{1}_tree.root".format(parent, daughter)
tfile = uproot.open(path) 
ttree = tfile["DecayTree"]

RS_df = ttree.pandas.df()

print("Successfully loaded TTree, converted to pandas dataframe.")
print(" ")

# Set correct formatting IDS for RS_dataframe
if daughter == "pipipi":
    decayID = "pi"
else:
    decayID = daughter  

if   parent == "Bplus":
    mesonID = "Bp"
elif parent == "Bcplus":
    mesonID = "Bcp"
elif parent == "Dplus":
    mesonID = "Dp"
elif parent == "Dsplus":
    mesonID = "Dsp"

# Define functions
def z_active(event):
    z_act = 0
    perp_distance = math.sqrt((event["{0}_0_vtxX_TRUE".format(mesonID)] - event["{0}_0_origX_TRUE".format(mesonID)])**2 + (event["{0}_0_vtxY_TRUE".format(mesonID)] - event["{0}_0_origY_TRUE".format(mesonID)])**2)
    eta = event["{0}_0_eta_TRUE".format(mesonID)]
    theta = 2.0 * math.atan(math.exp(-eta))                                           # Angle wrt angle beam from pseudo rapidity
    if perp_distance > maxrange:
        dz = (maxrange - minrange) / math.tan(theta)                                 # To account going out of VELO range
    else: 
        dz = event["{0}_0_vtxZ_TRUE".format(mesonID)] - event["{0}_0_origZ_TRUE".format(mesonID)]
    z_act = (1 - (minrange / perp_distance)) * dz
    z_act = 0 if z_act < 0 else z_act
    return z_act

def n_sensors(event):
    r_act = z_active(event) / dz_module
    n_act = r_act + random.random()
    if n_act > max_sensors:
        n_act = max_sensors
    return int(math.floor(n_act))

def angle(event):
    if daughter == "pipipi":
        Ux = event["pip_0_PX_TRUE"] + event["pip_1_PX_TRUE"] + event["pim_0_PX_TRUE"]
        Uy = event["pip_0_PY_TRUE"] + event["pip_1_PY_TRUE"] + event["pim_0_PY_TRUE"]
        Uz = event["pip_0_PZ_TRUE"] + event["pip_1_PZ_TRUE"] + event["pim_0_PZ_TRUE"]
    else:
        Ux = event["{0}p_0_PX_TRUE".format(decayID)]
        Uy = event["{0}p_0_PY_TRUE".format(decayID)]
        Uz = event["{0}p_0_PZ_TRUE".format(decayID)]
    Vx = event["{0}_0_PX_TRUE".format(mesonID)]
    Vy = event["{0}_0_PY_TRUE".format(mesonID)]
    Vz = event["{0}_0_PZ_TRUE".format(mesonID)]
    U = [Ux, Uy, Uz]
    V = [Vx, Vy, Vz]
    theta = (180 / math.pi) * np.arccos(np.dot(U, V) / (np.linalg.norm(U) * np.linalg.norm(V)))
    return theta


# Set decay particle 'arrays'
P      = []
PT     = []
eta    = []
IP     = []
origX  = []
origY  = []
angles = []

# Set parent particle 'arrays'
distT  = []
FD     = []

j = 0
for i in range(0, int(1 * len(RS_df.index))):
    event = RS_df.iloc[i]   
    sensors_hit = n_sensors(event)
    if sensors_hit >= 1:
        P.append(event["{0}p_0_P_TRUE".format(decayID)])
        PT.append(event["{0}p_0_PT_TRUE".format(decayID)])
        eta.append(event["{0}p_0_eta_TRUE".format(decayID)])
        IP.append(event["{0}p_0_IP_TRUE".format(decayID)])
        origX.append(event["{0}p_0_origX_TRUE".format(decayID)])
        origY.append(event["{0}p_0_origY_TRUE".format(decayID)])
        angles.append(angle(event))        
        distT.append(math.sqrt((event["{0}_0_vtxX_TRUE".format(mesonID)] - event["{0}_0_origX_TRUE".format(mesonID)])**2 + (event["{0}_0_vtxY_TRUE".format(mesonID)] - event["{0}_0_origY_TRUE".format(mesonID)])**2))
        FD.append(event["{0}_0_FD_TRUE".format(mesonID)])
        j += 1
    if (i % 10000) == 0:
        print(int(i / 10000), j, "hits")
        
def plotter(variable, domain, x, y, title, savepath):
    plt.figure()
    plt.hist(variable, bins=40, range=domain, log=True)
    plt.ylabel(y)
    plt.xlabel(x)
    plt.title(title)
    plt.savefig(savepath)

plotter(P, (0, 200), "P (Gev/c)", "Counts", "{1} Momentum from parent {0}_1_velo".format(parent, daughter), "/project/bfys/jrol/figures/1velo/{0}/{0}_{1}_P.pdf".format(parent, daughter))
plotter(PT, (0, 50), "PT (Gev/c)", "Counts", "{1} Tranverse momentum from parent {0}_1_velo".format(parent, daughter), "/project/bfys/jrol/figures/1velo/{0}/{0}_{1}_PT.pdf".format(parent, daughter))
plotter(eta, (-4, 8), "eta", "Counts", "{1} Eta from parent {0}_1_velo".format(parent, daughter), "/project/bfys/jrol/figures/1velo/{0}/{0}_{1}_eta.pdf".format(parent, daughter))
plotter(IP, (0, 2000), "IP (microns)", "Counts", "{1} IP from parent {0}_1_velo".format(parent, daughter), "/project/bfys/jrol/figures/1velo/{0}/{0}_{1}_IP.pdf".format(parent, daughter))
plotter(origX, (-40000, 40000), "Spread (mum)", "Counts", "{1} Origin vertex spread (X) from parent {0}_1_velo".format(parent, daughter), "/project/bfys/jrol/figures/1velo/{0}/{0}_{1}_origX.pdf".format(parent, daughter))
plotter(origY, (-40000, 40000), "Spread (mum)", "Counts", "{1} Origin vertex spread (Y) from parent {0}_1_velo".format(parent, daughter), "/project/bfys/jrol/figures/1velo/{0}/{0}_{1}_origY.pdf".format(parent, daughter))

plotter(distT, (0, 30000), "Distance (mum)", "Counts", "Perpendicular Distance of DV - {0}".format(parent), "/project/bfys/jrol/figures/1velo/{0}/{0}_{1}_distT.pdf".format(parent, daughter))
plotter(FD, (0, 50000), "Distance (mum)", "Counts", "Flight Distance - {0}".format(parent), "/project/bfys/jrol/figures/1velo/{0}/{0}_{1}_FD.pdf".format(parent, daughter))
plotter(angles, (0, 5), "Angle between momenta (degrees)", "Counts", "Origin and Final tracks-angle - {0} & {1}".format(parent, daughter), "/project/bfys/jrol/figures/1velo/{0}/{0}_{1}_angle.pdf".format(parent, daughter))

print("Saved figures!")
