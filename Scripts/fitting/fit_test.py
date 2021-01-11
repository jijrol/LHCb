# RooFit test script,
# Jan Rol, 13-9-2020

# LAST USE: DOUBLE CB ONLY. CHANGED SUM_PDF, tree_loc, B_JCMass -> B_s0_JCMass, sig_pdf =, 

import ROOT as R
import ROOT.RooFit as RF
import sys
l_empty = R.TLegend(0.81, 0.81, 0.8, 0.8); l_empty.SetBorderSize(0)

def legend(frame):
    legend = R.TLegend(0.6, 0.6, 0.89, 0.89)
    legend.AddEntry(frame.findObject("signal"), "Signal")
    legend.AddEntry(frame.findObject("background"), "Background")
    legend.SetBorderSize(0)
    return legend

def save(frame, title, legend=l_empty):
    c_temp = R.TCanvas("c_temp", "c_temp", 800, 600)
    frame.Draw(); legend.Draw()
    c_temp.SaveAs("/project/bfys/jrol/LHCb/figures/fitting/{0}".format(title))
    return 0

def makePlotWithPulls(canvas, frame, log = False, ymax = -1, legend = None, pavetext = None, nopulls = False):
    # clone frame
    frame_clone = frame
    # pull graph
    h_resid_errors = frame_clone.pullHist("h_mass_data", "sum_pdf");
    pull_graph = R.TGraph(h_resid_errors.GetN(), h_resid_errors.GetX(), h_resid_errors.GetY())
    #sum_pdf.plotOn(frame_clone, RF.Name("sig_pdf"), RF.Components("double_CB"), RF.LineColor(R.kGreen))
    #sum_pdf.plotOn(frame_clone, RF.Name("bkg_pdf"), RF.Components("bgk_pdf"), RF.LineColor(R.kRed))
    
    
    plotvar = frame_clone.getPlotVar()
    binwidth = ( frame_clone.GetXaxis().GetXmax() - frame_clone.GetXaxis().GetXmin() ) / frame_clone.GetNbinsX()
    frame_clone.GetYaxis().SetTitle("Candidates / ( %s %s )" % (str(binwidth).rstrip('0').rstrip('.'),plotvar.getUnit()))
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
        frame_clone.SetMinimum(0.0001)
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
    pull_graph.GetYaxis().SetRangeUser(-3, 3)
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

w = R.RooWorkspace('w')

treeloc = "/data/bfys/jrol/"
f_tree = R.TFile.Open("{0}Data_Bu2JpsimmK_Strip21r1_MagDown.root".format(treeloc))
old_tree = f_tree.Get("DecayTree")
new_file = R.TFile.Open("/data/bfys/jrol/temp_tree.root", "RECREATE")
new_tree = old_tree.CloneTree(0)
for i in range(int(1.0 * old_tree.GetEntries())):
    old_tree.GetEntry(i)
    if getattr(old_tree, "Kplus_PIDK") > 5:
        new_tree.Fill()
tree = new_tree; print("Filtered on PIDK")
print("Loaded TTree!")

# Build Signal Gaussian
min_inv_mass = 5180; max_inv_mass = 5500; nbins = int(max_inv_mass - min_inv_mass / 2)
B_JCMass = R.RooRealVar("B_JCMass", "invariant mass", min_inv_mass, max_inv_mass, "MeV/c^{2}")
B_CTAU_ps = R.RooRealVar("B_CTAU_ps", "lifetime [ps]", 0, 5, "")
sig_mean = R.RooRealVar("sig_mean", "mean of gaussian signal", 5280, min_inv_mass, max_inv_mass)
sig_width = R.RooRealVar("sig_width", "width of gaussian signal", 20, 0, 100)
sig_pdf = R.RooGaussian("sig_pdf", "Gaussian P.D.F. - signal", B_JCMass, sig_mean, sig_width)

# Import B_JCMass branch from tree
mass_data = R.RooDataSet("mass_data", "dataset with invariant mass and lifetime", tree, R.RooArgSet(B_JCMass, B_CTAU_ps))
print("Loaded B_JCMass & B_CTAU_ps variables from TTree!"); n_events = mass_data.sumEntries()
print(n_events)

# Construct gaussian signal P.D.F. with two CB
a_left        = R.RooRealVar("a_left" , "alpha left CB" , -1, -5 , 0)
a_left_const  = R.RooRealVar("a_left_const", "alpha left CB, fixed", -1.495)
a_right       = R.RooRealVar("a_right", "alpha right CB", 1, 0, 5)
a_right_const = R.RooRealVar("a_right_const", "alpha right CB, fixed", 1.388)
n_left        = R.RooRealVar("n_left" , "n left CB" , 0.5, 10)
n_left_const  = R.RooRealVar("n_left_const" , "n left CB, fixed", 3.271)
n_right       = R.RooRealVar("n_right", "n right CB", 0.5, 10)
n_right_const = R.RooRealVar("n_right_const" , "n right CB, fixed" , 2.936)

cb_left_pdf = R.RooCBShape("cb_left_pdf", "Crystal Ball 1 P.D.F.", B_JCMass, sig_mean, sig_width, a_left, n_left)
cb_left_const_pdf = R.RooCBShape("cb_left_const_pdf", "Crystal Ball 1 P.D.F. - fixed", B_JCMass, sig_mean, sig_width, a_left_const, n_left_const)
cb_right_pdf = R.RooCBShape("cb_right_pdf", "Crystal Ball 2 P.D.F.", B_JCMass, sig_mean, sig_width, a_right, n_right)
cb_right_const_pdf = R.RooCBShape("cb_right_pdf_const", "Crystal Ball 2 P.D.F. - fixed", B_JCMass, sig_mean, sig_width, a_right_const, n_right_const)
frac1 = R.RooRealVar("frac1", "fraction of CB 1", 0.5, 0., 1)
frac2 = R.RooRealVar("frac2", "fraction of CB 2", 0.5, 0., 1)
double_CB = R.RooAddPdf("double_CB", "Gauss with two CB tails", R.RooArgList(cb_left_pdf, cb_right_pdf, sig_pdf), R.RooArgList(frac1, frac2))
double_CB_const = R.RooAddPdf("double_CB_const", "Gauss with two fixed CB tails", R.RooArgList(cb_left_const_pdf, cb_right_const_pdf, sig_pdf), R.RooArgList(frac1, frac2))

# Construct exponential background P.D.F.
exp_const = R.RooRealVar("exp_const", "exponential decay rate of bkg", -0.002, -0.01, 0)
bkg_pdf = R.RooExponential("bkg_pdf", "Exponential P.D.F - background", B_JCMass, exp_const)

# Sum P.D.F.'s
sig_yield = R.RooRealVar("sig_yield", "signal yield", 0, n_events)
bkg_yield = R.RooRealVar("bkg_yield", "background yield", 0, n_events)
sum_pdf = R.RooAddPdf("sum_pdf", "signal + background P.D.F.", R.RooArgList(double_CB, bkg_pdf), R.RooArgList(sig_yield, bkg_yield))

sum_pdf.fitTo(mass_data)
print("Performed fitting of composite p.d.f. to data.")

# use sWeights to reconstruct signal distribution
splot = R.RooStats.SPlot("splot", "sPlot with sWeights", mass_data, sum_pdf, R.RooArgList(sig_yield, bkg_yield))
getattr(w, 'import')(mass_data, R.RooCmdArg()); print("Data imported to WS")
sw_frame = B_JCMass.frame(RF.Title("sWeights over invariant mass"))
sig_yield_sw = w.var("sig_yield_sw"); bkg_yield_sw = w.var("bkg_yield_sw")
sig_data = R.RooDataSet("sig_data", "Weighted data set with sig_yield_sw", mass_data, mass_data.get(), "", "sig_yield_sw")
bkg_data = R.RooDataSet("bkg_data", "Weighted data set with bkg_yield_sw", mass_data, mass_data.get(), "", "bkg_yield_sw")

# Construct frames for plotting
B_JCMass_frame   = B_JCMass.frame(RF.Bins(160)); B_JCMass_frame.GetYaxis().SetTitle("events / (2 MeV/c^{2})")
sw_frame         = B_JCMass.frame(); sw_frame.GetYaxis().SetTitle("arbitrary units")
B_CTAU_ps_frame  = B_CTAU_ps.frame(); B_CTAU_ps_frame.GetYaxis().SetTitle("events / 0.05 ps")

mass_data.plotOn(B_JCMass_frame)
sum_pdf.plotOn(B_JCMass_frame, RF.Name("sum_pdf"), RF.LineColor(R.kBlue)) 
sum_pdf.plotOn(B_JCMass_frame, RF.Name("sig_pdf"), RF.Components("double_CB"), RF.LineColor(R.kGreen), RF.LineStyle(R.kDashed))
sum_pdf.plotOn(B_JCMass_frame, RF.Name("bkg_pdf"), RF.Components("bkg_pdf"), RF.LineColor(R.kRed), RF.LineStyle(R.kDashed))
c4 = R.TCanvas("c4", "c4", 1200, 800); B_JCMass_frame.SetTitle("")
pad1, pad2, frame_clone = makePlotWithPulls(c4, B_JCMass_frame)
mass_data.plotOnXY(sw_frame, RF.YVar(sig_yield_sw), RF.Name("signal"), RF.MarkerColor(R.kGreen))
mass_data.plotOnXY(sw_frame, RF.YVar(bkg_yield_sw), RF.Name("background"), RF.MarkerColor(R.kRed))
sw_frame.SetMaximum(4)
sig_data.plotOn(B_CTAU_ps_frame, RF.MarkerColor(R.kGreen), RF.Name("signal"))
bkg_data.plotOn(B_CTAU_ps_frame, RF.MarkerColor(R.kRed), RF.Name("background"))
l2 = legend(B_CTAU_ps_frame)

l0 = R.TLegend(0.6, 0.6, 0.89, 0.89); pad1.cd()
l0.AddEntry(B_JCMass_frame.findObject("sig_pdf"), "Signal", "L")
l0.AddEntry(B_JCMass_frame.findObject("bkg_pdf"), "Background", "L")
l0.AddEntry(B_JCMass_frame.findObject("sum_pdf"), "Total fit", "L")
l0.SetBorderSize(0); l0.Draw()

c2 = R.TCanvas("c2", "canvas 2", 1200, 800); sw_frame.SetTitle(""); sw_frame.Draw(); c2.SetLeftMargin(0.12)
l1 = R.TLegend(0.6, 0.6, 0.89, 0.89)
l1.AddEntry(sw_frame.findObject("signal"), "Signal")
l1.AddEntry(sw_frame.findObject("background"), "Background")
l1.SetBorderSize(0); l1.Draw()

c3 = R.TCanvas("c3", "canvas 3", 1200, 800); B_CTAU_ps_frame.SetTitle(""); B_CTAU_ps_frame.Draw(); l2.Draw()
c3.SetLeftMargin(0.12)
#c1.SaveAs("/project/bfys/jrol/LHCb/figures/fitting/fit_test_mass.pdf")
#c2.SaveAs("/project/bfys/jrol/LHCb/figures/fitting/fit_test_sweights.pdf")
#c3.SaveAs("/project/bfys/jrol/LHCb/figures/fitting/fit_test_lifetime.pdf")

#c4.SaveAs("/project/bfys/jrol/LHCb/figures/fitting/fit_test_mass_wpulls.pdf")
print("waiting for input")
input()

