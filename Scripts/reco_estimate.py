# options
from optparse import OptionParser
parser = OptionParser()
parser.add_option("-p", dest="particle", default="B+", type="string")
parser.add_option("-f", dest="fracevents", default=1.0, type="float")
parser.add_option("-r", dest="run", default=3, type="int")
(options, args) = parser.parse_args()

# main stuff
import math, random
import ROOT as R

# constants of nature
const_c = 3e8*1e-12*1e3 # [mm/ps]
const_m_bplus  = 5279.33 # [MeV/c^2]
const_m_bcplus = 6274.9  # [MeV/c^2]
const_m_dsplus = 1968.34 # [MeV/c^2]
const_t_bplus  = 1.638   # [ps]
const_t_bcplus = 0.510   # [ps]
const_t_dsplus = 0.504   # [ps]

# dictionary for particles
partdict = { "B+"  : { "mass" : const_m_bplus,  "lifetime" : const_t_bplus,  "branchname" : "Bp_0",  "treename" : "Bu2taunu" }
           , "Bc+" : { "mass" : const_m_bcplus, "lifetime" : const_t_bcplus, "branchname" : "Bcp_0", "treename" : "Bc2taunu" } 
           , "Ds+" : { "mass" : const_m_dsplus, "lifetime" : const_t_dsplus, "branchname" : "Dsp_0", "treename" : "Ds2taunu" }}

# detector constants (for VELO upgrade I (VELO pix))
rmin         =  5.1 if options.run == 3 else 8.0 # [mm]
dz_module    = 30.0 # [mm] roughly, from normal VELO, should be little bit smaller for upgrade
nsensors_max = 52 if options.run == 3 else 42

# particle 
name = options.particle
mass = partdict[name]["mass"]
lifetime = partdict[name]["lifetime"]
branchname = partdict[name]["branchname"]

# formulas
def z_active(p,eta,t=1.5,m=const_m_bplus):
    d=const_c*t*p/m
    theta=2.*math.atan(math.exp(-eta))
    dmin = rmin/math.sin(theta)
    d_a = d-dmin if d>dmin else 0.0
    z_a = d_a*math.cos(theta)  # in [mm]
    return z_a

def nsensors(p,eta,t=1.5,m=5279.):
    r_act = z_active(p,eta,t,m)/dz_module
    n_act = r_act+random.random() # to account for PV spread (i.e. is next sensor closer or not)
    return int(math.floor(n_act))

# data
treeloc = "/data/bfys/mvegh/chargedb_tracking/rapidsim"
f_tree = R.TFile.Open("{1}/{0}_tree.root".format(partdict[name]["treename"],treeloc))
tree = f_tree.Get("DecayTree")

h_nsensors = R.TH1D("h_nsensors","h_nsensors",nsensors_max,0,nsensors_max)
h_nsensors_zerosup = R.TH1D("h_nsensors_zerosup","h_nsensors_zerosup",nsensors_max-1,1,nsensors_max)
h_nsuff1 = R.TH1D("h_nsuff1","h_nsuff1",10*nsensors_max,0,nsensors_max)
h_nsuff2 = R.TH1D("h_nsuff2","h_nsuff2",10*nsensors_max,0,nsensors_max)
h_nsuff3 = R.TH1D("h_nsuff3","h_nsuff3",10*nsensors_max,0,nsensors_max)
h_pt_onesensor = R.TH1D("h_pt_onesensor","h_pt_onesensor",150,0,150)
h_p_onesensor = R.TH1D("h_p_onesensor","h_p_onesensor",150,0,2000)

frac_events=options.fracevents
nEvents = int(frac_events*tree.GetEntries())

for i in range(nEvents):
    tree.GetEntry(i)
    p=getattr(tree,"{0}_P_TRUE".format(branchname)) # in GeV/c
    pt=getattr(tree,"{0}_PT_TRUE".format(branchname))
    taupt=getattr(tree,"{0}_PT".format(branchname))
    taup=getattr(tree,"{0}_P".format(branchname))
    eta = math.acosh(p/pt)
    tau = random.expovariate(1./lifetime)
    ns = nsensors(p*1000.,eta,tau,mass)
    ns = ns if ns<=nsensors_max else nsensors_max
    h_nsensors.Fill(ns)
    if ns>0: 
        h_nsensors_zerosup.Fill(ns)
        h_pt_onesensor.Fill(taupt)
        h_p_onesensor.Fill(taup)
    h_nsuff1.Fill(ns>=1)
    h_nsuff2.Fill(ns>=2)
    h_nsuff3.Fill(ns>=3)

print "For particle '{0}' with m = {1} MeV/c^2 and tau = {2} ps".format(name,mass,lifetime)
print "Efficiency of >= 1 sensors = ({0:.5f} +/- {1:.5f})%".format(h_nsuff1.GetMean()*100.,h_nsuff1.GetMeanError()*100.)
print "Efficiency of >= 2 sensors = ({0:.5f} +/- {1:.5f})%".format(h_nsuff2.GetMean()*100.,h_nsuff2.GetMeanError()*100.)
print "Efficiency of >= 3 sensors = ({0:.5f} +/- {1:.5f})%".format(h_nsuff3.GetMean()*100.,h_nsuff3.GetMeanError()*100.)

# plot
canv0 = R.TCanvas("canv0","canv0",0,0,600,400)
canv0.SetLogy()
h_nsensors.Draw()

canv1 = R.TCanvas("canv1","canv1",650,0,600,400)
h_nsensors_zerosup.Draw()

canv2 = R.TCanvas("canv2","canv2",0,450,600,400)
h_pt_onesensor.GetXaxis().SetTitle("visible #it{p}_{T} [GeV/#it{c}]")
h_pt_onesensor.Draw()

canv3 = R.TCanvas("canv3","canv3",650,450,600,400)
h_p_onesensor.GetXaxis().SetTitle("visible #it{p} [GeV/#it{c}]")
h_p_onesensor.Draw()
