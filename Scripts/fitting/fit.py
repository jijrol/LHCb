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
resolution = 9.209 # Mev/c^2

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
sig_width = R.RooRealVar("sig_width", "width of gaussian signal", 10, 0, 40)
gauss_pdf = R.RooGaussian("gauss_pdf", "Gaussian P.D.F. - signal", B_DTF_PV_consJpsi_M, sig_mean, sig_width)

# Build resolution Gaussian for ArgusBG
mean_var1       = R.RooRealVar("mean_var1", "mean_var1", 0.0)
mean_var2       = R.RooRealVar("mean_var2", "mean_var2", 0.0)
resolution_var1 = R.RooRealVar("resolution_var1", "resolution_var1", resolution)
resolution_var2 = R.RooRealVar("resolution_var2", "resolution_var2", resolution)
conv_gauss1 = R.RooGaussian("conv_gauss1", "conv_gauss1", B_DTF_PV_consJpsi_M, mean_var1, resolution_var1)
conv_gauss2 = R.RooGaussian("conv_gauss2", "conv_gauss2", B_DTF_PV_consJpsi_M, mean_var2, resolution_var2)

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

# Construct ArgusBG PDFs, convoluted with detector resolution
arg_1pi_m0    = R.RooRealVar("arg_1pi_m0","Roo Argus BG 1pi; m0", B_mass - pi_mass - 20, B_mass - pi_mass + 20)
arg_1pi_m0_const    = R.RooRealVar("arg_1pi_m0_const","Roo Argus BG 1pi; m0", B_mass - pi_mass, B_mass - pi_mass + 5)
arg_2pi_m0    = R.RooRealVar("arg_2pi_m0","Roo Argus BG 2pi; m0", B_mass - 2*pi_mass - 20, B_mass - 2*pi_mass + 20)
arg_2pi_m0_const    = R.RooRealVar("arg_2pi_m0_const","Roo Argus BG 2pi; m0", B_mass - 2*pi_mass)
arg_1pi_c     = R.RooRealVar("arg_1pi_c", "Roo Argus BG 1pi; c" , -50, -100, -50)
arg_2pi_c     = R.RooRealVar("arg_2pi_c", "Roo Argus BG 1pi; c" , -200, -300, -50)
arg_1pi       = R.RooArgusBG("arg_1pi", "Roo Argus BG pdf - 1pi", B_DTF_PV_consJpsi_M, arg_1pi_m0, arg_1pi_c)
arg_2pi       = R.RooArgusBG("arg_2pi", "Roo Argus BG pdf - 2pi", B_DTF_PV_consJpsi_M, arg_2pi_m0, arg_2pi_c)
arg_1pi_pdf   = R.RooFFTConvPdf("arg_1pi_pdf", "arg_1pi_pdf", B_DTF_PV_consJpsi_M, arg_1pi, conv_gauss1)
arg_2pi_pdf   = R.RooFFTConvPdf("arg_2pi_pdf", "arg_2pi_pdf", B_DTF_PV_consJpsi_M, arg_2pi, conv_gauss2)
frac3         = R.RooRealVar("frac3", "fraction of Argus 1", 0.05, 0., 1)
frac4         = R.RooRealVar("frac4", "fraction of Argus 2", 0.05, 0., 1)
sig_pdf       = R.RooAddPdf("sig_pdf", "Double CB + 2 Argus signal PDF", R.RooArgList(arg_1pi_pdf, arg_2pi_pdf, double_CB), R.RooArgList(frac3, frac4))

# Sum P.D.F.'s
sig_yield     = R.RooRealVar("sig_yield", "signal yield", 0, n_events)
sig_yield_cut = R.RooRealVar("sig_yield_cut", "signal yield", 0, n_events)
bkg_yield     = R.RooRealVar("bkg_yield", "background yield", 0, n_events)
bkg_yield_cut = R.RooRealVar("bkg_yield_cut", "background yield", 0, n_events)
sum_pdf = R.RooAddPdf("sum_pdf", "signal + background P.D.F.", R.RooArgList(sig_pdf, bkg_pdf), R.RooArgList(sig_yield, bkg_yield))

sum_pdf.fitTo(mass_data)
print("Performed fitting of composite p.d.f. to data. Resolution: {0}".format(sig_width.getValV()))

# Get necessary parameters from first fit (2 fixed argusses, signal)
a_left_const       = R.RooRealVar("a_left_const", "alpha left CB, fixed", a_left.getValV())
a_right_const      = R.RooRealVar("a_right_const", "alpha right CB, fixed", a_right.getValV())
n_left_const       = R.RooRealVar("n_left_const" , "n left CB, fixed", n_left.getValV())
n_right_const      = R.RooRealVar("n_right_const" , "n right CB, fixed" , n_right.getValV())
cb_left_const_pdf  = R.RooCBShape("cb_left_const_pdf", "Crystal Ball 1 P.D.F. - fixed", B_DTF_PV_consJpsi_M, sig_mean, sig_width, a_left_const, n_left_const)
cb_right_const_pdf = R.RooCBShape("cb_right_pdf_const", "Crystal Ball 2 P.D.F. - fixed", B_DTF_PV_consJpsi_M, sig_mean, sig_width, a_right_const, n_right_const)
frac1_cut          = R.RooRealVar("frac1_cut", "fraction CB 1, fixed", 0.1, 0., 1.)
frac2_cut          = R.RooRealVar("frac2_cut", "fraction CB 2, fixed", 0.1, 0., 1.)
frac3_cut          = R.RooRealVar("frac3_cut", "frac3_cut", 0.1, 0., 1.)
frac4_cut          = R.RooRealVar("frac4_cut", "frac4_cut", 0.1, 0., 1.)
arg_1pi_c_const    = R.RooRealVar("arg_1pi_c_const", "arg_1pi_c_const", arg_1pi_c.getValV())
arg_2pi_c_const    = R.RooRealVar("arg_2pi_c_const", "arg_2pi_c_const", arg_2pi_c.getValV())
arg_1pi_const      = R.RooArgusBG("arg_1pi_const", "arg_1p_const", B_DTF_PV_consJpsi_M, arg_1pi_m0_const, arg_1pi_c_const)
arg_2pi_const      = R.RooArgusBG("arg_2pi_const", "arg_2p_const", B_DTF_PV_consJpsi_M, arg_2pi_m0_const, arg_2pi_c_const)
arg_1pi_pdf_const  = R.RooFFTConvPdf("arg_1pi_pdf_const", "arg_1pi_pdf_const", B_DTF_PV_consJpsi_M, arg_1pi_const, conv_gauss1)
arg_2pi_pdf_const  = R.RooFFTConvPdf("arg_2pi_pdf_const", "arg_2pi_pdf_const", B_DTF_PV_consJpsi_M, arg_2pi_const, conv_gauss2)
double_CB_const    = R.RooAddPdf("double_CB_const", "Gauss with two fixed CB tails", R.RooArgList(cb_left_const_pdf, cb_right_const_pdf, sig_pdf), R.RooArgList(frac1_cut, frac2_cut))
sig_pdf_const      = R.RooAddPdf("sig_pdf_const", "sig_pdf_const", R.RooArgList(double_CB_const, arg_1pi_pdf_const, arg_2pi_pdf_const), R.RooArgList(frac3_cut, frac4_cut))
sum_pdf_cut        = R.RooAddPdf("sum_pdf_cut", "Fixed signal + background P.D.F.", R.RooArgList(sig_pdf_const, bkg_pdf_cut), R.RooArgList(sig_yield_cut, bkg_yield_cut))

# Construct frames for plotting
B_DTF_PV_consJpsi_M_frame  =  B_DTF_PV_consJpsi_M.frame()
B_DTF_PV_consJpsi_M_frame2 = B_DTF_PV_consJpsi_M.frame()

mass_data.plotOn(B_DTF_PV_consJpsi_M_frame, RF.Name("data"))
sum_pdf.plotOn(B_DTF_PV_consJpsi_M_frame, RF.Name("sum_pdf"))
sum_pdf.plotOn(B_DTF_PV_consJpsi_M_frame, RF.Name("arg1_pdf"), RF.Components("arg_1pi_pdf"), RF.LineColor(9), RF.LineStyle(R.kDashed))
sum_pdf.plotOn(B_DTF_PV_consJpsi_M_frame, RF.Name("arg2_pdf"), RF.Components("arg_2pi_pdf"), RF.LineColor(9), RF.LineStyle(R.kDotted))
sum_pdf.plotOn(B_DTF_PV_consJpsi_M_frame,  RF.Name("bkg_pdf"), RF.Components("bkg_pdf"), RF.LineColor(R.kRed))
sum_pdf.plotOn(B_DTF_PV_consJpsi_M_frame,  RF.Name("sig_pdf"), RF.Components("sig_pdf"), RF.LineColor(R.kGreen))
B_DTF_PV_consJpsi_M_frame.SetTitle("")
c1 = R.TCanvas("c1", "canvas 1", 1400, 1000); c1.SetLeftMargin(0.12)
B_DTF_PV_consJpsi_M_frame.Draw()

sum_pdf_cut.fitTo(mass_data_cut)
mass_data_cut.plotOn(B_DTF_PV_consJpsi_M_frame2, RF.DataError(2), RF.Name("data"))
sum_pdf_cut.plotOn(B_DTF_PV_consJpsi_M_frame2, RF.Name("sum_pdf"))
sum_pdf_cut.plotOn(B_DTF_PV_consJpsi_M_frame2, RF.Name("bkg_pdf"), RF.Components("bkg_pdf_cut"), RF.LineColor(R.kRed))
sum_pdf_cut.plotOn(B_DTF_PV_consJpsi_M_frame2, RF.Name("gauss_pdf"), RF.Components("sig_pdf_const"), RF.LineColor(R.kGreen))
sum_pdf_cut.plotOn(B_DTF_PV_consJpsi_M_frame2, RF.Name("arg1_pdf"), RF.Components("arg_1pi_pdf_const"), RF.LineColor(9), RF.LineStyle(R.kDashed))
sum_pdf_cut.plotOn(B_DTF_PV_consJpsi_M_frame2, RF.Name("arg2_pdf"), RF.Components("arg_2pi_pdf_const"), RF.LineColor(9), RF.LineStyle(R.kDotted))

Leg1 = R.TLegend(0.55, 0.6, 0.89, 0.89); Leg1.SetBorderSize(0); Leg1.SetTextFont(12)
Leg1.AddEntry(B_DTF_PV_consJpsi_M_frame.findObject("sig_pdf"), "Signal", "L")
Leg1.AddEntry(B_DTF_PV_consJpsi_M_frame.findObject("bkg_pdf"), "Background", "L")
Leg1.AddEntry(B_DTF_PV_consJpsi_M_frame.findObject("arg1_pdf"), "B #rightarrow #alpha J/\psi \K \pi" , "L")
Leg1.AddEntry(B_DTF_PV_consJpsi_M_frame.findObject("arg2_pdf"), "B /rightarrow J/\psi K \pi \pi", "L")
Leg1.AddEntry(B_DTF_PV_consJpsi_M_frame.findObject("sum_pdf"), "Total Fit", "L")
Leg1.Draw()
Leg2 = R.TLegend(0.55, 0.7, 0.89, 0.89); Leg2.SetBorderSize(0)
Leg2.AddEntry(B_DTF_PV_consJpsi_M_frame2.findObject("gauss_pdf"), "Signal".format(round(sig_yield_cut.getValV())), "L")
Leg2.AddEntry(B_DTF_PV_consJpsi_M_frame2.findObject("arg1_pdf"), "Argus background, 1 missing pion" , "L")
Leg2.AddEntry(B_DTF_PV_consJpsi_M_frame2.findObject("arg2_pdf"), "Argus background, 2 missing pion" , "L")
Leg2.AddEntry(B_DTF_PV_consJpsi_M_frame2.findObject("bkg_pdf"), "Background, yield: {0}".format(round(bkg_yield_cut.getValV())), "L")
Leg2.AddEntry(B_DTF_PV_consJpsi_M_frame2.findObject("sum_pdf"), "Sum PDF", "L")


c2 = R.TCanvas("c2", "c2", 1400, 1000); B_DTF_PV_consJpsi_M_frame2.Draw("HIST"); Leg2.Draw()
c1.SaveAs("/project/bfys/jrol/LHCb/figures/fitting/argus_fit.pdf")
#c2.SaveAs("/project/bfys/jrol/LHCb/figures/fitting/fixed_fit_nHits")
print("waiting for input")
input()
