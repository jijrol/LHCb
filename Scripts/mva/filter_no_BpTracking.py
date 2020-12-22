# Filter Tree and save one tree with all events, one tree with hits only. Adds BpTracking_nHits branch to both.
# Jan Rol 6-11-2020  
import numpy as np 
import math, random
import ROOT as R
from array import array
from optparse import OptionParser

parser = OptionParser()
parser.add_option("-p", dest="particle", default="Bplus", type="string")   
parser.add_option("-d", dest="daughter", default="pipipi", type="string")
parser.add_option("-f", dest="fracevents", default=1.0, type="float")
parser.add_option("-r", dest="run", default=3, type="int")
(options, args) = parser.parse_args()

smear = 0.004 * 180 / math.pi

# constants of nature
const_c = 3e8 * 1e-12 * 1e3 # [mm/ps]
const_m_bplus  = 5279.33    # [MeV/c^2]
const_m_bcplus = 6274.9     # [MeV/c^2]
const_m_dsplus = 1968.34    # [MeV/c^2]
const_m_dplus  = 1896.65    # [Mev/c^2]
const_t_bplus  = 1.638      # [ps]
const_t_bcplus = 0.510      # [ps]
const_t_dsplus = 0.504      # [ps]
const_t_dplus  = 1.040      # [ps]
const_m_pi     = 139.57     # [MeV/c^2]

# dictionary (of dictionaries) for particles to fetch data from with option '-p'
partdict = { "Bplus"  : { "mass" : const_m_bplus,  "lifetime" : const_t_bplus,  "branchname" : "Bp_0",  "treename" : "Bplus"  }
           , "Bcplus" : { "mass" : const_m_bcplus, "lifetime" : const_t_bcplus, "branchname" : "Bcp_0", "treename" : "Bcplus" } 
           , "Dplus"  : { "mass" : const_m_dplus,  "lifetime" : const_t_dplus,  "branchname" : "Dp_0",  "treename" : "Dplus"  }
           , "Dsplus" : { "mass" : const_m_dsplus, "lifetime" : const_t_dsplus, "branchname" : "Dsp_0", "treename" : "Dsplus" }}

rmin         = 5.1 if options.run == 3 else 8.0 # [mm]
dz_module    = 30.0 # [mm]
nsensors_max = 52 if options.run == 3 else 42



# set particle constants 
name = options.particle
mass = partdict[name]["mass"]
lifetime = partdict[name]["lifetime"]
branchname = partdict[name]["branchname"]
treename = partdict[name]["treename"]
daughter = options.daughter

# formulas 

def Angle(U, V):
    projection = np.dot(U, V) / (np.linalg.norm(U) * np.linalg.norm(V))
    if projection >= 1:
        print(projection); projection = 1.0
    theta = (180 / math.pi) * np.arccos(projection)
    return theta

def z_active(p, eta, t=1.5, m=const_m_bplus):
    d     = const_c * t * p / m                    # total distance travelled
    theta = 2. * math.atan(math.exp(-eta))         # angle wrt beam axis from pseudorapidity 
    dmin  = rmin / math.sin(theta)                 # minimum distance travelled to get to edge of detector
    d_a   = d-dmin if d>dmin else 0.0              # "active" distance in detector region
    z_a   = d_a * math.cos(theta)                  # "active" distance along beam axis in [mm]
    return z_a

def nsensors(p, eta, t=1.5, m=const_m_bplus):
    r_act = z_active(p, eta, t, m) / dz_module     # sensors passed in active region
    n_act = r_act + random.random()                # to account for PV spread, add between 0 and 1 to sensors passed.
    return int(math.floor(n_act))

# data
treeloc = "/project/bfys/jrol/RapidSim/decays"
f_old_tree = R.TFile.Open("{0}/{1}/{1}2tau2pipipi_tree.root".format(treeloc, name))
old_tree = f_old_tree.Get("DecayTree")

f_filtered_tree = R.TFile.Open("{0}/{1}/{1}2tau2pipipi_noBTracking.root".format(treeloc, name), "RECREATE")
filtered_tree  = old_tree.CloneTree(0)

ns    = array('I', [ 0 ])
P     = array('d', [ 0 ])
PT    = array('d', [ 0 ])
angle = array('d', [ 0 ])
mcorr = array('d', [ 0 ])

branch_nHits = filtered_tree.Branch("BpTracking_nHits", ns, "BpTracking_nHits/I")
branch_P     = filtered_tree.Branch("P", P, "P/D")
branch_PT    = filtered_tree.Branch("PT", PT, "PT/D")
branch_angle = filtered_tree.Branch("angle", angle, "angle/D")
branch_mcorr = filtered_tree.Branch("Mcorr_noBTracking", mcorr, "mcorr/D")

nEvents = int(options.fracevents * old_tree.GetEntries())
j = 0
for i in range(int(1.0 * nEvents)):
    old_tree.GetEntry(i)                                          
    p     = getattr(old_tree, "P_TRUE")
    pt    = getattr(old_tree, "PT_TRUE")
    eta   = math.acosh(p / pt)                   
    tau   = random.expovariate(1. / lifetime)
    ns[0] = nsensors(p * 1000., eta, tau, mass)
    ns[0] = ns[0] if ns[0] <= nsensors_max else nsensors_max
    if ns[0] > 0:
        PV_X   = getattr(old_tree, "PV_X")     
        PV_Y   = getattr(old_tree, "PV_Y")
        PV_Z   = getattr(old_tree, "PV_Z")
        SV_X   = getattr(old_tree, "SV_X")
        SV_Y   = getattr(old_tree, "SV_Y")
        SV_Z   = getattr(old_tree, "SV_Z")
        PX_3pi = getattr(old_tree, "PX_3pi")
        PY_3pi = getattr(old_tree, "PY_3pi")
        PZ_3pi = getattr(old_tree, "PZ_3pi")
        P_3pi  = [PX_3pi, PY_3pi, PZ_3pi]
        PV     = [PV_X, PV_Y, PV_Z]
        SV     = [SV_X, SV_Y, SV_Z]
        PVSV   = np.subtract(SV, PV)
        P[0]  = np.linalg.norm(P_3pi)
        PT[0] = math.sqrt(PX_3pi**2 + PY_3pi**2)
        angle[0] = Angle(P_3pi, PVSV)
        pt_PVSV  = math.sin(angle[0] * math.pi / 180) * P[0]
        mcorr[0] = math.sqrt((3 * 0.001 * const_m_pi)**2 + pt_PVSV**2) + pt_PVSV
        filtered_tree.Fill()
        j+=1
    if i%1e6 == 0: print("{0} events filtered".format(i))
eff = float(j) / nEvents * 100
print("{3} to {4} -- {0} hits of {1} events. Efficiency: {2:.4f} %".format(j, nEvents, eff, name, daughter))

f_filtered_tree.cd()
filtered_tree.Write("", R.TObject.kOverwrite)
f_filtered_tree.Close()
f_old_tree.Close()
