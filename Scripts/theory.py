from uncertainties import ufloat as uf
import math 

# units
mev = 1.
gev = 1e3 * mev
ev  = 1e-6 * mev
s  = 1. / ( 6.582119569e-16 * ev )
ps = 1e-12 * s

# constants
GF = uf(1.16673787,0.0000006)*1e-5 / (gev**2) #Fermi's constant
m_t = uf(1776.86,0.12)*mev
m_mu = uf(105.6583745,0.0000024)*mev
m_e = uf(0.5109989461,0.0000000031)*mev

br_tau2mu = uf(0.1739,0.0004)
br_tau2e  = uf(0.1782,0.0004)

def BR_P2LNU(m_p, f_p, t_p, vckm, m_l = m_t):
    f0 = GF**2 * m_p * m_l**2 / ( 8. * math.pi )
    f1 = ( 1. - m_l**2 / m_p**2 )**2 * f_p**2 * vckm**2 * t_p
    return f0*f1

# some examples
m_bc = uf(6274.9,0.8)*mev
t_bc = uf(0.510,0.009)*ps
v_cb = uf(0.0412,0.0009)
f_bc = uf(434.,15.)*mev

br_bc2taunu = BR_P2LNU(m_bc, f_bc, t_bc, v_cb)
print("BR(Bc+ -> tau+ nu_tau)_SM = ({0:.4f},{1:.4f})%".format(100*br_bc2taunu.nominal_value,100*br_bc2taunu.std_dev))

m_bu = uf(5279.33,0.13)*mev
t_bu = uf(1.638,0.004)*ps
v_ub = uf(0.0036,0.0001)
f_bu = uf(196,6)*mev

br_bu2taunu = BR_P2LNU(m_bu, f_bu, t_bu, v_ub)
print("BR(B+  -> tau+ nu_tau)_SM = ({0:.4f},{1:.4f})%".format(100*br_bu2taunu.nominal_value,100*br_bu2taunu.std_dev))

# for electron/muonic mode
print("")
print("BR(Bc+ -> tau+ ( -> mu+ nu_s ) nu_mu)_SM = {0}".format(br_bc2taunu*br_tau2mu))
print("BR(B+  -> tau+ ( -> mu+ nu_s ) nu_mu)_SM = {0}".format(br_bu2taunu*br_tau2mu))

print("BR(Bc+ -> tau+ ( -> e+ nu_s ) nu_mu)_SM  = {0}".format(br_bc2taunu*br_tau2e))
print("BR(B+  -> tau+ ( -> e+ nu_s ) nu_mu)_SM  = {0}".format(br_bu2taunu*br_tau2e))

br_bc2munu = BR_P2LNU(m_bc, f_bc, t_bc, v_cb, m_mu)
br_bu2munu = BR_P2LNU(m_bu, f_bu, t_bu, v_ub, m_mu)
print("BR(Bc+ -> mu+ nu_mu)_SM = {0}".format(br_bc2munu))
print("BR(B+  -> mu+ nu_mu)_SM = {0}".format(br_bu2munu))

br_bc2enu = BR_P2LNU(m_bc, f_bc, t_bc, v_cb, m_e)
br_bu2enu = BR_P2LNU(m_bu, f_bu, t_bu, v_ub, m_e)
print("BR(Bc+ -> e+ nu_e)_SM = {0}".format(br_bc2enu))
print("BR(B+  -> e+ nu_e)_SM = {0}".format(br_bu2enu))

# how many do we expect?
barn = 1.
mub = 1e-6 * barn
fbinv = 1. / ( 1e-15 * barn )

# pp at 13 TeV sqrt(s)
s_bu = 87 *mub

# ratio at 7 TeV sqrt(s).. so reality is more favourable
s_bc = 0.7e-2 * s_bu

nbc = s_bc * 5 * fbinv
nbu = s_bu * 5 *fbinv

print("")
print("#B+  for 1 fb-1 = {0}".format(s_bu*fbinv))
print("#Bc+ for 1 fb-1 = {0}".format(s_bc*fbinv))

print("")
print("For 5 fb-1, about a year of data taking in Run 3:")
print("#(Bc+ -> tau+ ( -> mu+ nu_s ) nu_mu)_SM = {0}".format(br_bc2taunu*br_tau2mu*nbc))
print("#(B+  -> tau+ ( -> mu+ nu_s ) nu_mu)_SM = {0}".format(br_bu2taunu*br_tau2mu*nbu))

print("#(Bc+ -> mu+ nu_mu)_SM = {0}".format(br_bc2munu*nbc))
print("#(B+  -> mu+ nu_mu)_SM = {0}".format(br_bu2munu*nbu))

print("#(Bc+ -> tau+ ( -> e+ nu_s ) nu_mu)_SM  = {0}".format(br_bc2taunu*br_tau2e*nbc))
print("#(B+  -> tau+ ( -> e+ nu_s ) nu_mu)_SM  = {0}".format(br_bu2taunu*br_tau2e*nbu))

print("#(Bc+ -> e+ nu_e)_SM = {0}".format(br_bc2enu*nbc))
print("#(B+  -> e+ nu_e)_SM = {0}".format(br_bu2enu*nbu))

# stuff that ends up in the velo

#For particle 'Bc+' with m = 6274.9 MeV/c^2 and tau = 0.51 ps
#Efficiency of >= 1 sensors = (0.00265 +/- 0.00025)%
#Efficiency of >= 2 sensors = (0.00110 +/- 0.00016)%
#Efficiency of >= 3 sensors = (0.00059 +/- 0.00012)%

#maarten@maarten-XPS-13:~/LHCb/project/chargedB_reco$ python reco_estimate.py -p 'B+'
#For particle 'B+' with m = 5279.33 MeV/c^2 and tau = 1.638 ps
#Efficiency of >= 1 sensors = (0.31384 +/- 0.00597)%
#Efficiency of >= 2 sensors = (0.14056 +/- 0.00400)%
#Efficiency of >= 3 sensors = (0.08710 +/- 0.00315)%


ef_bu_1 = uf(0.0031384,0.0000597)
ef_bc_1 = uf(0.0000265,0.0000025)

print("")
print("For 5 fb-1, reaching at least 1 VELO sensor (about 1 year of Run 3):")
print("#(Bc+ -> tau+ ( -> mu+ nu_s ) nu_mu)_SM = {0}".format(br_bc2taunu*br_tau2mu*nbc*ef_bc_1))
print("#(B+  -> tau+ ( -> mu+ nu_s ) nu_mu)_SM = {0}".format(br_bu2taunu*br_tau2mu*nbu*ef_bu_1))

print("#(Bc+ -> mu+ nu_mu)_SM = {0}".format(br_bc2munu*nbc*ef_bc_1))
print("#(B+  -> mu+ nu_mu)_SM = {0}".format(br_bu2munu*nbu*ef_bu_1))

print("#(Bc+ -> tau+ ( -> e+ nu_s ) nu_mu)_SM  = {0}".format(br_bc2taunu*br_tau2e*nbc*ef_bc_1))
print("#(B+  -> tau+ ( -> e+ nu_s ) nu_mu)_SM  = {0}".format(br_bu2taunu*br_tau2e*nbu*ef_bu_1))

print("#(Bc+ -> e+ nu_e)_SM = {0}".format(br_bc2enu*nbc*ef_bc_1))
print("#(B+  -> e+ nu_e)_SM = {0}".format(br_bu2enu*nbu*ef_bu_1))

