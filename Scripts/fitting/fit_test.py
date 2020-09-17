# RooFit test script,
# Jan Rol, 13-9-2020

import ROOT as R

treeloc = "/data/bfys/mvegh/"
f_tree = R.TFile.Open("{0}Data_Bu2JpsimmK_Strip21r1_MagDown.root".format(treeloc))
tree = f_tree.Get("DecayTree")
print("Loaded TTree!")

# Build Signal Gaussian
# Declare variables with RooRealVar in range optionally with starting value
min_inv_mass = 5180; max_inv_mass = 5500
B_JCMass = R.RooRealVar("B_JCMass", "invariant mass", min_inv_mass, max_inv_mass, "Mev/c^2")
sig_mean = R.RooRealVar("sig_mean", "mean of gaussian signal", 5340, min_inv_mass, max_inv_mass)
sig_width = R.RooRealVar("sig_width", "width of gaussian signal", 20, 0, 100)

# Import B_JCMass branch from tree
mass_data = R.RooDataSet("mass_data", "dataset with invariant mass", tree, R.RooArgSet(B_JCMass))
print("Loaded B_JCMass variable from TTree!")
n_events = mass_data.sumEntries()

# Construct gaussian signal P.D.F. with two CB
sig_pdf = R.RooGaussian("sig_pdf", "Gaussian P.D.F. - signal", B_JCMass, sig_mean, sig_width)

a_left  = R.RooRealVar("a_left" , "alpha left CB" , -4, 0)
a_right = R.RooRealVar("a_right", "alpha right CB", 0, 4)
n_left  = R.RooRealVar("n_left" , "n left CB" , 0, 10)
n_right = R.RooRealVar("n_right", "n right CB", 0, 10)

cb_left_pdf = R.RooCBShape("cb_left_pdf", "Crystal Ball 1 P.D.F. - signal", B_JCMass, sig_mean, sig_width, a_left, n_left)
cb_right_pdf = R.RooCBShape("cb_right_pdf", "Crystal Ball 2 P.D.F. - signal", B_JCMass, sig_mean, sig_width, a_right, n_right)
frac1 = R.RooRealVar("frac1", "fraction of CB 1", 0.5, 0., 1)
frac2 = R.RooRealVar("frac2", "fraction of CB 2", 0.5, 0., 1)
double_CB = R.RooAddPdf("double_CB", "Gauss with two CB tails", R.RooArgList(cb_left_pdf, cb_right_pdf, sig_pdf), R.RooArgList(frac1, frac2))

# Construct exponential background P.D.F.
exp_const = R.RooRealVar("exp_const", "exponential decay rate of bkg", -0.02, -0.1, 0)
bkg_pdf = R.RooExponential("bkg_pdf", "Exponential P.D.F - background", B_JCMass, exp_const)

# Sum P.D.F.'s
sig_yield = R.RooRealVar("sig_yield", "signal yield", 0, n_events)
bkg_yield = R.RooRealVar("bkg_yield", "background yield", 0, n_events)
sum_pdf = R.RooAddPdf("sum_pdf", "signal + background P.D.F.", R.RooArgList(sig_pdf, bkg_pdf), R.RooArgList(sig_yield, bkg_yield))

sum_pdf.fitTo(mass_data)
print("Performed fitting of composite p.d.f. to data")

# Construct frame for plotting
B_JCMass_frame = B_JCMass.frame(R.RooFit.Title("Gaussian + double CB signal with exponential Background"))
pull_frame     = B_JCMass.frame(R.RooFit.Title("Pulls of data w.r.t. composite P.D.F."))
mass_data.plotOn(B_JCMass_frame)
sum_pdf.plotOn(B_JCMass_frame)
pulls_hist = B_JCMass_frame.pullHist()
sum_pdf.plotOn(B_JCMass_frame, R.RooFit.Components("bkg_pdf"), R.RooFit.LineColor(R.kRed))
sum_pdf.plotOn(B_JCMass_frame, R.RooFit.Components("sig_pdf"), R.RooFit.LineColor(R.kGreen))
c1 = R.TCanvas("c1", "canvas 1", 1800, 900)
c1.Divide(2); c1.cd(1)
B_JCMass_frame.Draw()
c1.cd(2)
pull_frame.addPlotable(pulls_hist)
pull_frame.Draw()

c1.SaveAs("/project/bfys/jrol/LHCb/figures/gauss.pdf")
print("waiting for input")
input()

# Change sum_pdf, sum_pdf.plotOn(), Frame Title and Save path.
