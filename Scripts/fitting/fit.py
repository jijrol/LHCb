# RooFit actual fitting script,
# Jan Rol, 4-12-2020

import ROOT as R
import ROOT.RooFit as RF
import sys
from array import array
l_empty = R.TLegend(0.81, 0.81, 0.8, 0.8); l_empty.SetBorderSize(0)

def makePlotWithPulls(canvas, frame, log = False, ymax = -1, legend = None, pavetext = None, nopulls = False, data = None, curve = None):
    # clone frame
    frame_clone = frame
    # pull graph
    h_resid_errors = frame_clone.pullHist(data, curve);
    pull_graph = R.TGraph(h_resid_errors.GetN(), h_resid_errors.GetX(), h_resid_errors.GetY())
    #sum_pdf.plotOn(frame_clone, RF.Name("sig_pdf"), RF.Components("double_CB"), RF.LineColor(R.kGreen))
    #sum_pdf.plotOn(frame_clone, RF.Name("bkg_pdf"), RF.Components("bgk_pdf"), RF.LineColor(R.kRed))
    
    
    plotvar = frame_clone.getPlotVar()
    binwidth = ( frame_clone.GetXaxis().GetXmax() - frame_clone.GetXaxis().GetXmin() ) / frame_clone.GetNbinsX()
#    frame_clone.GetYaxis().SetTitle("Candidates / ( %s %s )" % (str(binwidth).rstrip('0').rstrip('.'),plotvar.getUnit()))
    frame_clone.GetYaxis().SetTitleOffset(1.25)
    frame_clone.GetYaxis().CenterTitle()
    if not nopulls: frame_clone.GetXaxis().SetLabelSize(0)

    ymid = 0.27
    if not nopulls:
        # adapt x-axis
        frame_clone.GetXaxis().SetLabelSize(0)
        # adapt y-axis
        frame_clone.GetYaxis().SetTitleOffset(1.30)
        frame_clone.GetYaxis().SetTitleSize(0.05*(1.0/(1-ymid)));
        frame_clone.GetYaxis().SetLabelSize(0.04*(1.0/(1-ymid)));

    if log: 
        frame_clone.SetMinimum(1.1)
    else:
        frame_clone.SetMinimum(0.000)
    if ymax > 0:
        frame_clone.SetMaximum(ymax)
    elif log: 
        frame_clone.SetMaximum(3.0*frame_clone.GetMaximum())
    else:
        frame_clone.SetMaximum(1.1*frame_clone.GetMaximum())

    canvas.cd(0)
    canvas.SetTopMargin(0.0)
    canvas.SetBottomMargin(0.0)
    canvas.SetLeftMargin(0.0)
    
    # pads for data and pull
    pad1 = R.TPad("data_pad", "other_data_pad", 0.05, ymid if not nopulls else 0.10, 0.98, 0.97 if not nopulls else 0.90)
    pad1.SetBottomMargin(0.02 if not nopulls else 0.17)
    pad1.SetTopMargin(0.07)
    pad1.SetLeftMargin(0.17)
    pad2 = R.TPad("pull_pad_pass", "pull_pad_pass", 0.05, 0.00, 0.98, ymid)
    pad2.SetBottomMargin(0.65)
    pad2.SetTopMargin(0.05)
    pad2.SetLeftMargin(0.17)

    # pull x-axis config
    pull_graph.GetXaxis().SetLimits(pull_graph.GetX()[0], pull_graph.GetX()[pull_graph.GetN() - 1])
    pull_graph.GetXaxis().SetTitle("{0} [{1}]".format(plotvar.GetTitle(),plotvar.getUnit()) )
    pull_graph.GetXaxis().SetTitleSize(0.05* (1.0/ymid));
    pull_graph.GetXaxis().SetLabelSize(0.05* (1.0/ymid));
    pull_graph.GetXaxis().SetTitleOffset(1.10);        
    # pull y-axis config
    pull_graph.GetYaxis().SetRangeUser(-5, 5)
    pull_graph.GetYaxis().SetTitle("Pull")
    pull_graph.GetYaxis().SetTitleSize(0.05* (1.0/ymid));
    pull_graph.GetYaxis().SetLabelSize(0.04* (1.0/ymid));
    pull_graph.GetYaxis().SetTitleOffset(0.49)
    pull_graph.GetYaxis().SetNdivisions(502)
    pull_graph.GetYaxis().SetTickLength(0.08)
    pull_graph.GetYaxis().CenterTitle()
    pull_graph.SetFillColor(R.kBlack)
    
    dot_functie = R.TF1("plus_twee_sigma", "2", pull_graph.GetX()[0], pull_graph.GetX()[pull_graph.GetN() - 1])
    dot_functie.SetLineColor(R.kRed)
    dot_functie.SetLineStyle(R.kDotted)

    min_twee_sigma = R.TF1("min_twee_sigma", "-2", pull_graph.GetX ()[0], pull_graph.GetX ()[pull_graph.GetN() - 1])
    min_twee_sigma.SetLineColor(R.kRed)
    min_twee_sigma.SetLineStyle(R.kDotted)
    
    canvas.cd(2)
    pad1.Draw()
    if not nopulls: pad2.Draw()
    
    pad1.cd()
    
    if log: pad1.SetLogy()
    frame_clone.Draw()
    if legend:
        legend.Draw()
    if pavetext:
        pavetext.Draw()

    if not nopulls:
        pad2.cd()
        pull_graph.Draw("AB");
        dot_functie.Draw("SAME")
        min_twee_sigma.Draw("SAME")
        pull_graph.Draw("B SAME");
   
    canvas.Update()
    objlist = [frame_clone,pad1,pad2,h_resid_errors,pull_graph,dot_functie,min_twee_sigma]
    for obj in objlist :
        R.SetOwnership(obj, False)
    return pad1, pad2, frame_clone

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
tree.Draw("B_DTF_PV_consJpsi_M[0]>>h_temp_nocut(450, 4850, 5750")
n_events_cut = tree.Draw("B_DTF_PV_consJpsi_M[0]>>h_temp_cut(450, 4850, 5750", "B_BpTracking_PatRec_nHits > 0 && Kp_ProbNNk > 0.2")
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
arg_2pi_m0_const    = R.RooRealVar("arg_2pi_m0_const","Roo Argus BG 2pi; m0", B_mass - 2*pi_mass - 10, B_mass - 2*pi_mass + 30)
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
sig_yield_cut = R.RooRealVar("sig_yield_cut", "signal yield", 0.5*n_events_cut, n_events_cut)
bkg_yield     = R.RooRealVar("bkg_yield", "background yield", 0, n_events)
bkg_yield_cut = R.RooRealVar("bkg_yield_cut", "background yield", 0, 0.05 * n_events_cut)
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
frac3_cut          = R.RooRealVar("frac3_cut", "frac3_cut", 0.1, 0.005, 1.)
frac4_cut          = R.RooRealVar("frac4_cut", "frac4_cut", 0.1, 0.01, 1.)
arg_1pi_c_const    = R.RooRealVar("arg_1pi_c_const", "arg_1pi_c_const", arg_1pi_c.getValV())
arg_2pi_c_const    = R.RooRealVar("arg_2pi_c_const", "arg_2pi_c_const", arg_2pi_c.getValV())
arg_1pi_const      = R.RooArgusBG("arg_1pi_const", "arg_1p_const", B_DTF_PV_consJpsi_M, arg_1pi_m0_const, arg_1pi_c_const)
arg_2pi_const      = R.RooArgusBG("arg_2pi_const", "arg_2p_const", B_DTF_PV_consJpsi_M, arg_2pi_m0_const, arg_2pi_c_const)
arg_1pi_pdf_const  = R.RooFFTConvPdf("arg_1pi_pdf_const", "arg_1pi_pdf_const", B_DTF_PV_consJpsi_M, arg_1pi_const, conv_gauss1)
arg_2pi_pdf_const  = R.RooFFTConvPdf("arg_2pi_pdf_const", "arg_2pi_pdf_const", B_DTF_PV_consJpsi_M, arg_2pi_const, conv_gauss2)
double_CB_const    = R.RooAddPdf("double_CB_const", "Gauss with two fixed CB tails", R.RooArgList(cb_left_const_pdf, cb_right_const_pdf, gauss_pdf), R.RooArgList(frac1_cut, frac2_cut))
sig_pdf_const      = R.RooAddPdf("sig_pdf_const", "sig_pdf_const", R.RooArgList(arg_1pi_pdf_const, arg_2pi_pdf_const, double_CB_const), R.RooArgList(frac3_cut, frac4_cut))
sum_pdf_cut        = R.RooAddPdf("sum_pdf_cut", "Fixed signal + background P.D.F.", R.RooArgList(sig_pdf_const, bkg_pdf_cut), R.RooArgList(sig_yield_cut, bkg_yield_cut))

# Construct frames for plotting
B_DTF_PV_consJpsi_M_frame  = B_DTF_PV_consJpsi_M.frame()
B_DTF_PV_consJpsi_M_frame2 = B_DTF_PV_consJpsi_M.frame()

mass_data.plotOn(B_DTF_PV_consJpsi_M_frame, RF.Name("data"), RF.DataError(0))
sum_pdf.plotOn(B_DTF_PV_consJpsi_M_frame, RF.Name("arg1_pdf"), RF.Components("arg_1pi_pdf"), RF.Range(min_inv_mass, arg_1pi_m0.getValV()+20), RF.LineColor(8), RF.LineStyle(R.kDashed))
sum_pdf.plotOn(B_DTF_PV_consJpsi_M_frame, RF.Name("arg2_pdf"), RF.Components("arg_2pi_pdf"), RF.Range(min_inv_mass, arg_2pi_m0.getValV()+20), RF.LineColor(6), RF.LineStyle(R.kDashed))
sum_pdf.plotOn(B_DTF_PV_consJpsi_M_frame,  RF.Name("bkg_pdf"), RF.Components("bkg_pdf"), RF.LineColor(R.kRed), RF.LineStyle(R.kDashed))
sum_pdf.plotOn(B_DTF_PV_consJpsi_M_frame, RF.Name("sum_pdf"))
B_DTF_PV_consJpsi_M_frame.SetTitle(""); B_DTF_PV_consJpsi_M_frame.GetXaxis().SetTitle("invariant mass [MeV/c^{2}]")
c1 = R.TCanvas("c1", "canvas 1", 1200, 800); c1.SetLeftMargin(0.12)
B_DTF_PV_consJpsi_M_frame.Print()

sum_pdf_cut.fitTo(mass_data_cut)
mass_data_cut.plotOn(B_DTF_PV_consJpsi_M_frame2, RF.Name("data"), RF.DataError(0), RF.Binning(100, 4850, 5750))
sum_pdf_cut.plotOn(B_DTF_PV_consJpsi_M_frame2, RF.Name("sum_pdf_cut"))
sum_pdf_cut.plotOn(B_DTF_PV_consJpsi_M_frame2, RF.Name("arg1_pdf_cut"), RF.Components("arg_1pi_pdf_const"), RF.Range(min_inv_mass, arg_1pi_m0.getValV() + 50), RF.LineColor(8), RF.LineStyle(R.kDashed))
sum_pdf_cut.plotOn(B_DTF_PV_consJpsi_M_frame2, RF.Name("arg2_pdf_cut"), RF.Components("arg_2pi_pdf_const"), RF.Range(min_inv_mass, arg_2pi_m0.getValV() + 20), RF.LineColor(6), RF.LineStyle(R.kDashed))
B_DTF_PV_consJpsi_M_frame2.SetTitle(""); B_DTF_PV_consJpsi_M_frame2.GetXaxis().SetTitle("invariant mass [MeV/c^{2}]")
B_DTF_PV_consJpsi_M_frame2.Print()

Leg1 = R.TLegend(0.55, 0.5, 0.89, 0.89); Leg1.SetBorderSize(0)
Leg1.AddEntry(B_DTF_PV_consJpsi_M_frame.findObject("arg1_pdf"), "#it{B #rightarrow J#kern[0.1]{#/}#kern[-0.5]{#psi} K #pi}" , "L")
Leg1.AddEntry(B_DTF_PV_consJpsi_M_frame.findObject("arg2_pdf"), "#it{B #rightarrow J#kern[0.1]{#/}#kern[-0.5]{#psi} K #pi #pi}", "L")
Leg1.AddEntry(B_DTF_PV_consJpsi_M_frame.findObject("bkg_pdf"), "Background", "L")
Leg1.AddEntry(B_DTF_PV_consJpsi_M_frame.findObject("sum_pdf"), "Total fit", "L")
makePlotWithPulls(c1, B_DTF_PV_consJpsi_M_frame, data = "data", curve = "sum_pdf", legend = Leg1)

Leg2 = R.TLegend(0.55, 0.6, 0.89, 0.89); Leg2.SetBorderSize(0)
Leg2.AddEntry(B_DTF_PV_consJpsi_M_frame2.findObject("arg1_pdf_cut"), "#it{B #rightarrow J#kern[0.1]{#/}#kern[-0.5]{#psi} K #pi}" , "L")
Leg2.AddEntry(B_DTF_PV_consJpsi_M_frame2.findObject("arg2_pdf_cut"), "#it{B #rightarrow J#kern[0.1]{#/}#kern[-0.5]{#psi} K #pi #pi}", "L")
Leg2.AddEntry(B_DTF_PV_consJpsi_M_frame2.findObject("sum_pdf_cut"), "Total fit", "L")

c2 = R.TCanvas("c2", "c2", 1200, 800)
makePlotWithPulls(c2, B_DTF_PV_consJpsi_M_frame2, legend = Leg2, data = "data", curve = "sum_pdf_cut")
#c1.SaveAs("/project/bfys/jrol/LHCb/figures/fitting/data_fit1.pdf")
#c2.SaveAs("/project/bfys/jrol/LHCb/figures/fitting/data_fit2.pdf")
print("waiting for input")
input()

