# RooFIT test script,
# Jan Rol, 13-9-2020

import ROOT
 
# Build Signal Gaussian
# Declare variables with RooRealVar in range optionally with starting value
min_inv_mass = 5180; max_inv_mass = 5500
inv_mass = RooRealVar("inv_mass", "invariant mass", min_inv_mass, max_inv_mass, "Mev/c^2")
sig_mean = RooRealVar("sig_mean", "mean of gaussian signal", 5340, min_inv_mass, max_inv_mass)
sig_width = RooRealVar("sig_width", "width of gaussian signal", 100, min_inv_mass, max_inv_mass)

# Construct P.D.F from given values
RooGaussian sig_pdf("sig_pdf", "Gaussian P.D.F - signal", inv_mass, sig_mean, sig_width)

# Construct frame for plotting
inv_mass_frame = in_mass.frame(ROOT.RooFit.Title("Gaussian p.d.f."))  # RooPlot
sig_pdf.plotOn(xframe)

# Build exponential background
exp_const = RooRealVar("exp_const", "exponential decay rate of bkg", -0.1, 0)
RooExponential bkg_pdf("bkg_pdf", "Exponential P.D.F - background", inv_mass, exp_const)