# RooFit actual fitting script,
# Jan Rol, 4-12-2020

import ROOT as R
import ROOT.RooFit as RF
import sys
from array import array
l_empty = R.TLegend(0.81, 0.81, 0.8, 0.8); l_empty.SetBorderSize(0)

def legend(frame):
    legend = R.TLegend(0.6, 0.7, 0.8, 0.88)
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
B_mass  = 5279   # MeV/c^2
pi_mass = 139    # MeV/c^2

tree = R.TChain("Bp2JpsimmKp/DecayTree")
treeloc = "/data/bfys/mvegh/chargedb_tracking/2018/"
for pol in ["up", "down"]:
    filename = "{0}ntuple_bp2jpsimmk_btracking_2018_data_mag{1}.root".format(treeloc, pol)
    tree.Add(filename)
tree.Draw("B_DTF_PV_consJpsi_M[0]>>h_temp_nocut(900, 4850, 5750")
tree.Draw("B_DTF_PV_consJpsi_M[0]>>h_temp_cut(900, 4850, 5750", "B_BpTracking_PatRec_nHits > 0 && Kp_ProbNNk > 0.2")
h_temp_nocut = R.gDirectory.Get("h_temp_nocut")
h_temp_cut   = R.gDirectory.Get("h_temp_cut")
print("Got hists")

# Build Signal Gaussian
min_inv_mass = 4850; max_inv_mass = 5750
B_DTF_PV_consJpsi_M = R.RooRealVar("B_DTF_PV_consJpsi_M", "invariant mass", min_inv_mass, max_inv_mass, "MeV/c ^{2}")
B_CTAU_ps = R.RooRealVar("B_CTAU_ps", "Lifetime", 0, 5, "picoseconds")
sig_mean = R.RooRealVar("sig_mean", "mean of gaussian signal", 5280, min_inv_mass, max_inv_mass)
sig_width = R.RooRealVar("sig_width", "width of gaussian signal", 20, 0, 100)
gauss_pdf = R.RooGaussian("gauss_pdf", "Gaussian P.D.F. - signal", B_DTF_PV_consJpsi_M, sig_mean, sig_width)

# Import B_DTF_PV_consJpsi_M[0] value from tree
mass_data = R.RooDataHist("mass_data", "datahist of invariant mass", R.RooArgList(B_DTF_PV_consJpsi_M), h_temp_nocut)
mass_data_cut = R.RooDataHist("mass_data_cut", "datahist of invariant mass", R.RooArgList(B_DTF_PV_consJpsi_M), h_temp_cut)
print("Loaded B_DTF_PV_consJpsi_M variable from TTree."); n_events = int(mass_data.sumEntries())
print("no of events :", n_events)
print("no of nHits >= 1 events:", mass_data_cut.sumEntries())

# Construct gaussian signal P.D.F. with two CB
a_left        = R.RooRealVar("a_left", "alpha left CB" , -1, -4 , 0)
a_right       = R.RooRealVar("a_right", "alpha right CB", 1, 0.8, 4)
n_left        = R.RooRealVar("n_left", "n left CB", 0, 10)
n_right       = R.RooRealVar("n_right", "n right CB", 0, 2)
cb_left_pdf = R.RooCBShape("cb_left_pdf", "Crystal Ball 1 P.D.F.", B_DTF_PV_consJpsi_M, sig_mean, sig_width, a_left, n_left)
cb_right_pdf = R.RooCBShape("cb_right_pdf", "Crystal Ball 2 P.D.F.", B_DTF_PV_consJpsi_M, sig_mean, sig_width, a_right, n_right)
frac1 = R.RooRealVar("frac1", "fraction of CB 1", 0.5, 0., 1)
frac2 = R.RooRealVar("frac2", "fraction of CB 2", 0.5, 0., 1)
double_CB = R.RooAddPdf("double_CB", "Gauss with two CB tails", R.RooArgList(cb_left_pdf, cb_right_pdf, gauss_pdf), R.RooArgList(frac1, frac2))

# Construct exponential background P.D.F.
exp_const     = R.RooRealVar("exp_const", "exponential decay rate of bkg", -0.002, -0.1, -0.0001)
exp_const_cut = R.RooRealVar("exp_const_cut", "exponential decay rate of bkg", -0.002, -0.1, 0)
bkg_pdf       = R.RooExponential("bkg_pdf", "Exponential P.D.F - background", B_DTF_PV_consJpsi_M, exp_const)
bkg_pdf_cut   = R.RooExponential("bkg_pdf_cut", "Exponential P.D.F - background", B_DTF_PV_consJpsi_M, exp_const_cut)

arg_1pi_m0    = R.RooRealVar("arg_1pi_m0","Roo Argus BG 1pi; m0", B_mass - pi_mass, B_mass - pi_mass + 50)
arg_2pi_m0    = R.RooRealVar("arg_2pi_m0","Roo Argus BG 2pi; m0", B_mass - 2*pi_mass, B_mass - 2 * pi_mass + 50)
arg_1pi_c     = R.RooRealVar("arg_1pi_c", "Roo Argus BG 1pi; c" , -30, -100, -30)
arg_2pi_c     = R.RooRealVar("arg_2pi_c", "Roo Argus BG 1pi; c" , -70, -100, -50)
arg_1pi_p     = R.RooRealVar("arg_1pi_c", "Roo Argus BG 1pi; p" , 0, 10)
arg_2pi_p     = R.RooRealVar("arg_2pi_c", "Roo Argus BG 1pi; p" , 0, 10)
arg_1pi_pdf   = R.RooArgusBG("arg_1pi_pdf", "Roo Argus BG pdf - 1pi", B_DTF_PV_consJpsi_M, arg_1pi_m0, arg_1pi_c) 
arg_2pi_pdf   = R.RooArgusBG("arg_2pi_pdf", "Roo Argus BG pdf - 2pi", B_DTF_PV_consJpsi_M, arg_2pi_m0, arg_2pi_c)
frac3         = R.RooRealVar("frac3", "fraction of Argus 1", 0.05, 0.1, 1)
frac4         = R.RooRealVar("frac4", "fraction of Argus 2", 0.05, 0.1, 1)
sig_pdf       = R.RooAddPdf("sig_pdf", "Double CB + 2 Argus signal PDF", R.RooArgList(arg_1pi_pdf, arg_2pi_pdf, double_CB), R.RooArgList(frac3, frac4))

# Sum P.D.F.'s
sig_yield     = R.RooRealVar("sig_yield", "signal yield", 0, n_events)
sig_yield_cut = R.RooRealVar("sig_yield_cut", "signal yield", 0, n_events)
bkg_yield     = R.RooRealVar("bkg_yield", "background yield", 400000, n_events)
bkg_yield_cut = R.RooRealVar("bkg_yield_cut", "background yield", 0, n_events)
sum_pdf = R.RooAddPdf("sum_pdf", "signal + background P.D.F.", R.RooArgList(sig_pdf, bkg_pdf), R.RooArgList(sig_yield, bkg_yield))

sum_pdf.fitTo(mass_data)
print("Performed fitting of composite p.d.f. to data.")

a_left_const  = R.RooRealVar("a_left_const", "alpha left CB, fixed", a_left.getValV())
a_right_const = R.RooRealVar("a_right_const", "alpha right CB, fixed", a_right.getValV())
n_left_const  = R.RooRealVar("n_left_const" , "n left CB, fixed", n_left.getValV())
n_right_const = R.RooRealVar("n_right_const" , "n right CB, fixed" , n_right.getValV())
cb_left_const_pdf = R.RooCBShape("cb_left_const_pdf", "Crystal Ball 1 P.D.F. - fixed", B_DTF_PV_consJpsi_M, sig_mean, sig_width, a_left_const, n_left_const)
cb_right_const_pdf = R.RooCBShape("cb_right_pdf_const", "Crystal Ball 2 P.D.F. - fixed", B_DTF_PV_consJpsi_M, sig_mean, sig_width, a_right_const, n_right_const)
frac1_cut = R.RooRealVar("frac1_cut", "fraction CB 1, fixed", 0.5, 0., 1.)
frac2_cut = R.RooRealVar("frac2_cut", "fraction CB 2, fixed", 0.5, 0., 1.)
double_CB_const = R.RooAddPdf("double_CB_const", "Gauss with two fixed CB tails", R.RooArgList(cb_left_const_pdf, cb_right_const_pdf, sig_pdf), R.RooArgList(frac1_cut, frac2_cut))
sum_pdf_cut = R.RooAddPdf("sum_pdf_cut", "Fixed signal + background P.D.F.", R.RooArgList(double_CB_const, bkg_pdf_cut), R.RooArgList(sig_yield_cut, bkg_yield_cut))

# Construct frames for plotting
B_DTF_PV_consJpsi_M_frame  =  B_DTF_PV_consJpsi_M.frame(RF.Title("Double CB w/ 2 Argus & exp. bkg"))
B_DTF_PV_consJpsi_M_frame2 = B_DTF_PV_consJpsi_M.frame(RF.Title("Fixed Signal fit w/ nHits > 0 && Kp_ProbNNk > 0.2"))

mass_data.plotOn(B_DTF_PV_consJpsi_M_frame, RF.Name("data"))
sum_pdf.plotOn(B_DTF_PV_consJpsi_M_frame, RF.Name("sum_pdf"))
sum_pdf.plotOn(B_DTF_PV_consJpsi_M_frame, RF.Name("arg1_pdf"), RF.Components("arg_1pi_pdf"), RF.LineColor(9), RF.LineStyle(R.kDashed))
sum_pdf.plotOn(B_DTF_PV_consJpsi_M_frame, RF.Name("arg2_pdf"), RF.Components("arg_2pi_pdf"), RF.LineColor(9), RF.LineStyle(R.kDotted))
sum_pdf.plotOn(B_DTF_PV_consJpsi_M_frame,  RF.Name("bkg_pdf"), RF.Components("bkg_pdf"), RF.LineColor(R.kRed))
sum_pdf.plotOn(B_DTF_PV_consJpsi_M_frame,  RF.Name("gauss_pdf"), RF.Components("double_CB"), RF.LineColor(R.kGreen))
c1 = R.TCanvas("c1", "canvas 1", 1400, 1000); c1.SetLeftMargin(0.12)
B_DTF_PV_consJpsi_M_frame.Draw()

#sum_pdf_cut.fitTo(mass_data_cut)
mass_data_cut.plotOn(B_DTF_PV_consJpsi_M_frame2, RF.Name("data"))
sum_pdf_cut.plotOn(B_DTF_PV_consJpsi_M_frame2, RF.Name("sum_pdf"))
sum_pdf_cut.plotOn(B_DTF_PV_consJpsi_M_frame2, RF.Name("bkg_pdf"), RF.Components("bkg_pdf"), RF.LineColor(R.kRed))
sum_pdf_cut.plotOn(B_DTF_PV_consJpsi_M_frame2, RF.Name("gauss_pdf"), RF.Components("double_CB"), RF.LineColor(R.kGreen))

Leg1 = R.TLegend(0.45, 0.7, 0.89, 0.89); Leg1.SetBorderSize(0)
Leg1.AddEntry(B_DTF_PV_consJpsi_M_frame.findObject("gauss_pdf"), "Signal, yield: {0}".format(round(sig_yield.getValV())), "L")
Leg1.AddEntry(B_DTF_PV_consJpsi_M_frame.findObject("arg1_pdf"), "Argus background, 1 missing pion" , "L")
Leg1.AddEntry(B_DTF_PV_consJpsi_M_frame.findObject("arg2_pdf"), "Argus background, 2 missing pions", "L")
Leg1.AddEntry(B_DTF_PV_consJpsi_M_frame.findObject("bkg_pdf"), "Background, yield: {0}".format(round(bkg_yield.getValV())), "L")
Leg1.AddEntry(B_DTF_PV_consJpsi_M_frame.findObject("sum_pdf"), "Sum PDF", "L")
Leg1.Draw()
Leg2 = R.TLegend(0.45, 0.7, 0.89, 0.89); Leg2.SetBorderSize(0)
Leg2.AddEntry(B_DTF_PV_consJpsi_M_frame2.findObject("gauss_pdf"), "Signal, yield: {0}".format(round(sig_yield_cut.getValV())), "L")
Leg2.AddEntry(B_DTF_PV_consJpsi_M_frame2.findObject("bkg_pdf"), "Background, yield: {0}".format(round(bkg_yield_cut.getValV())), "L")
Leg2.AddEntry(B_DTF_PV_consJpsi_M_frame2.findObject("sum_pdf"), "Sum PDF", "L")


c2 = R.TCanvas("c2", "c2", 1400, 1000); B_DTF_PV_consJpsi_M_frame2.Draw("HIST"); Leg2.Draw()
c1.SaveAs("/project/bfys/jrol/LHCb/figures/fitting/argus_fit.pdf")
#c2.SaveAs("/project/bfys/jrol/LHCb/figures/fitting/fixed_fit_nHits")
print("waiting for input")
input()

