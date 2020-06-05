# Plotter for VeloHits dependence

# Jan Rol, 05-06-2020

import math
import ROOT as R
import numpy as np

xmin = 0
xmax = 300000
nbins = 60
var = "Bp_P"

def draw(h1, h2, h3, title):
    hs = R.THStack(title, title)
    hs.Add(h1); hs.Add(h2); hs.Add(h3)
    return hs

path = "/project/bfys/jrol/data/{0}"
tree = R.TChain("Bp2JpsimmKp/DecayTree")
for direction in ["up", "down"]:
    fname = "ntuple_bp2jpsimmk_btracking_2018_veryloose_mc_mag{0}.root".format(direction)
    tree.Add(path.format(fname))

h0 = R.TH1F("hist_0_hits", "hist_0_hits", nbins, xmin, xmax)
h2 = R.TH1F("hist_min_2_hits", "hist_min_2_hits", nbins, xmin, xmax)
h4 = R.TH1F("hist_min_4_hits", "hist_min_4_hits", nbins, xmin, xmax)


for i in range (0, tree.GetEntries()):
	tree.GetEntry(i)
	ID     = getattr(tree, "Bp_TRUEID")
	nHits  = getattr(tree, "Bp_BTracking_PatRec_nHits")
    bkgcat = getattr(tree, "Bp_BKGCAT")
    if (bkgcat == 0 or bkgcat == 50) and ID == 521
        variable = getattr(tree, var)
        if nHits == 0: h0.Fill(variable)
        if nHits > 1: h2.Fill(variable)
        if nHits > 3: h4.Fill(variable)

R.gStyle.SetPalette(1)
R.gPad.Update()
c1 = R.TCanvas("c1", "c1", 0, 0, 1000, 700)
hstack = draw(h0, h2, h4, "Bp Momentum"); hstack.Draw("PLC NOSTACK HIST")
c1.SaveAs("/project/bfys/jrol/figures/btracking/nhits/{0}_hits.pdf".format(var))
input()

