# RooFit test script,
# Jan Rol, 13-9-2020

# LAST USE: DOUBLE CB ONLY. CHANGED SUM_PDF, tree_loc, B_JCMass -> B_s0_JCMass, sig_pdf =, 

import ROOT as R
import ROOT.RooFit as RF
import sys
l_empty = R.TLegend(0.81, 0.81, 0.8, 0.8); l_empty.SetBorderSize(0)

def legend(frame):
    legend = R.TLegend(0.88, 0.88, 0.6, 0.7)
    legend.AddEntry(frame.findObject("signal"), "Signal")
    legend.AddEntry(frame.findObject("background"), "Background")
    legend.SetBorderSize(0)
    return legend

def save(frame, title, legend=l_empty):
    c_temp = R.TCanvas("c_temp", "c_temp", 800, 600)
    frame.Draw(); legend.Draw()
    c_temp.SaveAs("/project/bfys/jrol/LHCb/figures/fitting/{0}".format(title))
    return 0

w = R.RooWorkspace('w')

treeloc = "/data/bfys/jrol/"
f_tree = R.TFile.Open("{0}MC_2012.root".format(treeloc))
#f_tree = R.TFile.Open("{0}Data_Bu2JpsimmK_Strip21r1_MagDown.root".format(treeloc))
tree = f_tree.Get("DecayTree")
print("Loaded TTree!")

# Build Signal Gaussian
min_inv_mass = 5000; max_inv_mass = 5500
B_s0_JCMass = R.RooRealVar("B_s0_JCMass", "invariant mass", min_inv_mass, max_inv_mass, "Mev/c^2")
#B_CTAU_ps = R.RooRealVar("B_CTAU_ps", "Lifetime", 0, 5, "picoseconds")
sig_mean = R.RooRealVar("sig_mean", "mean of gaussian signal", 5130, min_inv_mass, max_inv_mass)
sig_width = R.RooRealVar("sig_width", "width of gaussian signal", 20, 0, 100)
sig_pdf = R.RooGaussian("sig_pdf", "Gaussian P.D.F. - signal", B_s0_JCMass, sig_mean, sig_width)

# Import B_JCMass branch from tree
mass_data = R.RooDataSet("mass_data", "dataset with invariant mass", tree, R.RooArgSet(B_s0_JCMass))#, B_CTAU_ps)) # changed B_s0
print("Loaded B_JCMass & B_CTAU_ps variables from TTree!"); n_events = mass_data.sumEntries()
print(n_events)

# Construct gaussian signal P.D.F. with two CB
a_left  = R.RooRealVar("a_left" , "alpha left CB" , -1, -5 , 0)
a_right = R.RooRealVar("a_right", "alpha right CB", 1, 0, 5)
n_left  = R.RooRealVar("n_left" , "n left CB" , 0, 10)
n_right = R.RooRealVar("n_right", "n right CB", 0, 10)
cb_left_pdf = R.RooCBShape("cb_left_pdf", "Crystal Ball 1 P.D.F. - signal", B_s0_JCMass, sig_mean, sig_width, a_left, n_left)
cb_right_pdf = R.RooCBShape("cb_right_pdf", "Crystal Ball 2 P.D.F. - signal", B_s0_JCMass, sig_mean, sig_width, a_right, n_right)
frac1 = R.RooRealVar("frac1", "fraction of CB 1", 0.5, 0., 1)
frac2 = R.RooRealVar("frac2", "fraction of CB 2", 0.5, 0., 1)
double_CB = R.RooAddPdf("double_CB", "Gauss with two CB tails", R.RooArgList(cb_left_pdf, cb_right_pdf, sig_pdf), R.RooArgList(frac1, frac2))

# Construct exponential background P.D.F.
#exp_const = R.RooRealVar("exp_const", "exponential decay rate of bkg", -0.002, -0.01, 0)
#bkg_pdf = R.RooExponential("bkg_pdf", "Exponential P.D.F - background", B_JCMass, exp_const)

# Sum P.D.F.'s
#sig_yield = R.RooRealVar("sig_yield", "signal yield", 0, n_events)
#bkg_yield = R.RooRealVar("bkg_yield", "background yield", 0, n_events)
#sum_pdf = R.RooAddPdf("sum_pdf", "signal + background P.D.F.", R.RooArgList(double_CB, bkg_pdf), R.RooArgList(sig_yield, bkg_yield))

double_CB.fitTo(mass_data) #sum_pdf.fitTo(mass_data)
print("Performed fitting of composite p.d.f. to data.")

# use sWeights to reconstruct signal distribution
#splot = R.RooStats.SPlot("splot", "sPlot with sWeights", mass_data, sum_pdf, R.RooArgList(sig_yield, bkg_yield))
#getattr(w, 'import')(mass_data, R.RooCmdArg()); print("Data imported to WS")
#sw_frame = B_JCMass.frame(RF.Title("sWeights over invariant mass"))
#sig_yield_sw = w.var("sig_yield_sw"); bkg_yield_sw = w.var("bkg_yield_sw")
#sig_data = R.RooDataSet("sig_data", "Weighted data set with sig_yield_sw", mass_data, mass_data.get(), "", "sig_yield_sw")
#bkg_data = R.RooDataSet("bkg_data", "Weighted data set with bkg_yield_sw", mass_data, mass_data.get(), "", "bkg_yield_sw")

# Construct frames for plotting
B_JCMass_frame   = B_s0_JCMass.frame(RF.Title("Double CB signal with exponential background"))
pull_frame       = B_s0_JCMass.frame(RF.Title("Pulls of data w.r.t. composite P.D.F."))
#sw_frame        = B_JCMass.frame(RF.Title("sWeights over invariant mass"))
#B_CTAU_ps_frame = B_CTAU_ps.frame(RF.Title("Lifetime of signal and background components"))

mass_data.plotOn(B_JCMass_frame)
double_CB.plotOn(B_JCMass_frame) #sum_pdf -> double_CB
pulls_hist = B_JCMass_frame.pullHist(); pull_frame.addPlotable(pulls_hist)
print(B_JCMass_frame.chiSquare())
#sum_pdf.plotOn(B_JCMass_frame, RF.Components("bkg_pdf"), RF.LineColor(R.kRed))
#sum_pdf.plotOn(B_JCMass_frame, RF.Components("double_CB"), RF.LineColor(R.kGreen))
#mass_data.plotOnXY(sw_frame, RF.YVar(sig_yield_sw), RF.Name("signal"), RF.MarkerColor(R.kGreen))
#mass_data.plotOnXY(sw_frame, RF.YVar(bkg_yield_sw), RF.Name("background"), RF.MarkerColor(R.kRed))
#l1 = legend(sw_frame)
#sig_data.plotOn(B_CTAU_ps_frame, RF.MarkerColor(R.kGreen), RF.Name("signal"))
#bkg_data.plotOn(B_CTAU_ps_frame, RF.MarkerColor(R.kRed), RF.Name("background"))
#l2 = legend(B_CTAU_ps_frame)

c1 = R.TCanvas("c1", "canvas 1", 1600, 1200); c1.Divide(2) #changed canvas division
c1.cd(1); B_JCMass_frame.Draw()#; save(B_JCMass_frame, "mass_data_fit.pdf")
c1.cd(2); pull_frame.Draw()#; save(pull_frame, "pulls_hist.pdf")
#c1.cd(3); sw_frame.Draw()#; l1.Draw(); save(sw_frame, "sweights.pdf", legend = l1)
#c1.cd(4); B_CTAU_ps_frame.Draw()#; l2.Draw(); save(B_CTAU_ps_frame, "lifetimes.pdf", legend = l2)

c1.SaveAs("/project/bfys/jrol/LHCb/figures/fitting/MC_fit.pdf")
print("waiting for input")
input()

