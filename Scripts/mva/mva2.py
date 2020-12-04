import numpy as np
import pandas as pd
import uproot
import ROOT as R
import matplotlib.pyplot as plt
from sklearn.neural_network import MLPClassifier
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_curve, roc_auc_score

def scale_list(factor, items):
    for item in items:
        item.Scale(factor)

# Import trees
loc = "/data/bfys/jrol/RapidSim/{0}2tau2pipipi_filtered.root"

f_Dplus  = uproot.open(loc.format("Dplus"));  Dplus_tree  = f_Dplus["DecayTree"]
f_Dsplus = uproot.open(loc.format("Dsplus")); Dsplus_tree = f_Dsplus["DecayTree"]
f_Bplus  = uproot.open(loc.format("Bplus"));  Bplus_tree  = f_Bplus["DecayTree"]
f_Bcplus = uproot.open(loc.format("Bcplus")); Bcplus_tree = f_Bcplus["DecayTree"]

Dp_df  = Dplus_tree.pandas.df()
Dsp_df = Dsplus_tree.pandas.df()
Bp_df  = Bplus_tree.pandas.df(); Bp_df = Bp_df.head(275000)
Bcp_df = Bcplus_tree.pandas.df()
bkg_amount = len(Dsp_df.index) + len(Dp_df.index)
sig_amount = len(Bcp_df.index) + len(Bp_df.index); print(len(Bcp_df.index), len(Bp_df.index))
total_amount = sig_amount + bkg_amount
pure_amount = 0


h2d_sig = R.TH2F("2dh_sig", "Signal events", 30, 0, 7.0, 30, 0, 3)
h2d_bkg = R.TH2F("2dh_bkg", "Background events", 30, 0, 7.0, 30, 0, 3)
hP_all = R.TH1F("hP_all", "All events", 100, 0, 600)
hP_sig = R.TH1F("hP_sig", "All signal events", 100, 0, 600)
hP_bkg = R.TH1F("hP_bkg", "All background events", 100, 0, 600)
hP_pur = R.TH1F("hP_pur", "'Pure' signal events", 100, 0, 600)
hPT_all = R.TH1F("hPT_all", "All events", 100, 0, 50)
hPT_sig = R.TH1F("hPT_sig", "All signal events", 100, 0, 50)
hPT_bkg = R.TH1F("hPT_bkg", "All background events", 100, 0, 50)
hPT_pur = R.TH1F("hPT_pur", "'Pure' signal events", 100, 0, 50)
hMcorr_all = R.TH1F("hMcorr_all", "All events", 100, 0, 7)
hMcorr_sig = R.TH1F("hMcorr_sig", "All signal events", 100, 0, 7)
hMcorr_bkg = R.TH1F("hMcorr_bkg", "All background events", 100, 0, 7)
hMcorr_pur = R.TH1F("hMcorr_pur", "'Pure' signal events", 100, 0, 7)
hnHits_all = R.TH1F("hnHits_all", "All events", 8, 0.25, 4.25)
hnHits_sig = R.TH1F("hnHits_sig", "All signal events", 8, 0.25, 4.25)
hnHits_bkg = R.TH1F("hnHits_bkg", "All background events", 8, 0.25, 4.25)
hnHits_pur = R.TH1F("hnHits_pur", "'Pure' signal events", 8, 0.25, 4.25)
hangle_all = R.TH1F("hangle_all", "All events", 100, 0, 3.0)
hangle_sig = R.TH1F("hangle_sig", "All signal events", 100, 0, 3.0)
hangle_bkg = R.TH1F("hangle_bkg", "All background events", 100, 0, 3.0)
hangle_pur = R.TH1F("hangle_pur", "'Pure' signal events", 100, 0, 3.0)

# Add flags for signal and background
Bp_df["flag"] = 1; Bcp_df["flag"] = 1
Dp_df["flag"] = 0; Dsp_df["flag"] = 0

full_frame = pd.concat([Dp_df, Dsp_df, Bp_df, Bcp_df], ignore_index=True, sort=False)
observables     = ["PT", "Mcorr", "BpTracking_nHits", "angle"]; obs_str = ""
#for obs in observables:
#    obs_str += obs + ", "
all_observables = ["P", "PT", "Mcorr", "BpTracking_nHits", "angle"]; all_obs_str = "" 
#for obs in all_observables:
#    all_obs_str += obs + ", "
#print(obs_str, all_obs_str)

train, test = train_test_split(full_frame, test_size=0.5)

# GBC config, Fit vars to training set
verbose = 1
tol = 1e-4
init = "zero"
n_estimators = 100
#gbc1 = GradientBoostingClassifier(verbose=verbose, tol=tol, init=init, n_estimators=n_estimators)
#gbc2 = GradientBoostingClassifier(verbose=verbose, tol=tol, init=init, n_estimators=n_estimators)
#gbc1.fit(train[observables], train["flag"])
#gbc2.fit(train[all_observables], train["flag"])
print("Completed training")

# Apply training to give prob and pred
#predictions1   = gbc1.predict(test[observables])
#predictions2   = gbc2.predict(test[all_observables])
#probabilities1 = gbc1.predict_proba(test[observables])
#probabilities2 = gbc2.predict_proba(test[all_observables])


no_bkg_cut = 0.99119
for i in range(len(test)-1):
    P = test['P'].iloc[i]
    PT = test['PT'].iloc[i]
    Mcorr = test['Mcorr'].iloc[i]
    nHits = test['BpTracking_nHits'].iloc[i]
    angle = test['angle'].iloc[i]
    hP_all.Fill(P)
    hPT_all.Fill(PT)
    hMcorr_all.Fill(Mcorr)
    hnHits_all.Fill(nHits)
    hangle_all.Fill(angle)
    if test['flag'].iloc[i] < 1:
        h2d_bkg.Fill(Mcorr, angle)
        hP_bkg.Fill(P)
        hPT_bkg.Fill(PT)
        hMcorr_bkg.Fill(Mcorr)
        hnHits_bkg.Fill(nHits)
        hangle_bkg.Fill(angle) 
    if test['flag'].iloc[i] > 0:
        h2d_sig.Fill(Mcorr, angle)
        hP_sig.Fill(P)
        hPT_sig.Fill(PT)
        hMcorr_sig.Fill(Mcorr)
        hnHits_sig.Fill(nHits)
        hangle_sig.Fill(angle)
#    if probabilities2[i, 1] >= no_bkg_cut:
#        pure_amount += 1
#        hP_pur.Fill(P)
#        hPT_pur.Fill(PT)
#        hMcorr_pur.Fill(Mcorr)
#        hnHits_pur.Fill(nHits)
#        hangle_pur.Fill(angle)
#print(pure_amount, total_amount, bkg_amount, sig_amount)
#scale_list(1, [hP_all, hPT_all, hMcorr_all, hnHits_all, hangle_all])
#scale_list(1, [hP_sig, hPT_sig, hMcorr_sig, hnHits_sig, hangle_sig])
#scale_list(1, [hP_bkg, hPT_bkg, hMcorr_bkg, hnHits_bkg, hangle_bkg])
#scale_list(1, [hP_pur, hPT_pur, hMcorr_pur, hnHits_pur, hangle_pur])

R.gStyle.SetPalette(1); R.gStyle.SetOptStat(0)
c1 = R.TCanvas("c1", "c1", 1200, 800)
h2d_sig.Draw("PLC SURF"); h2d_bkg.Draw("PLC SURF SAME"); h2d_sig.GetXaxis().SetTitle("M_{corr} (Gev/c)^{2}"); h2d_sig.GetYaxis().SetTitle("Opening angle in degrees")
#hP_all.Draw("PLC HIST"); hP_sig.Draw("PLC SAME HIST")
#hP_bkg.Draw("PLC SAME HIST"); hP_pur.Draw("PLC SAME HIST")
L1 = R.gPad.BuildLegend(0.65, 0.7, 0.9, 0.82); L1.SetBorderSize(0); h2d_sig.SetTitle("Corrected mass vs. opening angle, Signal & Background")
c1.SaveAs("/project/bfys/jrol/LHCb/figures/mva/surface_Mcorr_angle.pdf"); c1.SetBottomMargin(0.1)
#hP_all.GetXaxis().SetTitle("Momentum (Gev/c)"); hP_all.GetYaxis().SetTitle("number in bin")
#c2 = R.TCanvas("c2", "c2", 1200, 800)
#hPT_all.Draw("PLC HIST"); hPT_sig.Draw("PLC SAME HIST")
#hPT_bkg.Draw("PLC SAME HIST"); hPT_pur.Draw("PLC SAME HIST")
#L2 = R.gPad.BuildLegend(0.55, 0.65, 0.9, 0.82); L2.SetBorderSize(0); hPT_all.SetTitle("Distributions of transverse momentum")
#hPT_all.GetXaxis().SetTitle("Transverse momentum (Gev/c)"); hPT_all.GetYaxis().SetTitle("number in bin")
#c3 = R.TCanvas("c3", "c3", 1200, 800); c3.SetLeftMargin(0.14)
#hMcorr_all.Draw("PLC HIST"); hMcorr_sig.Draw("PLC SAME HIST")
#hMcorr_bkg.Draw("PLC SAME HIST"); hMcorr_pur.Draw("PLC SAME HIST")
#L3 = R.gPad.BuildLegend(0.55, 0.65, 0.9, 0.82); L3.SetBorderSize(0); hMcorr_all.SetTitle("Distributions of corrected mass")
#hMcorr_all.GetXaxis().SetTitle("Corrected mass (Gev/c)^{2}"); hMcorr_all.GetYaxis().SetTitle("number in bin")
#c4 = R.TCanvas("c4", "c4", 1200, 800); c4.SetLeftMargin(0.14)
#hnHits_all.Draw("PLC HIST"); hnHits_sig.Draw("PLC SAME HIST")
#hnHits_bkg.Draw("PLC SAME HIST"); hnHits_pur.Draw("PLC SAME HIST")
#L4 = R.gPad.BuildLegend(0.55, 0.65, 0.9, 0.82); L4.SetBorderSize(0); hnHits_all.SetTitle("Distributions of BpTracking VELO hits")
#hnHits_all.GetXaxis().SetTitle("Number of hits"); hnHits_all.GetYaxis().SetTitle("number in bin")
#c5 = R.TCanvas("c5", "c5", 1200, 800); c5.SetLeftMargin(0.14)
#hangle_all.Draw("PLC HIST"); hangle_sig.Draw("PLC SAME HIST")
#hangle_bkg.Draw("PLC SAME HIST"); hangle_pur.Draw("PLC SAME HIST")
#L5 = R.gPad.BuildLegend(0.55, 0.65, 0.9, 0.82); L5.SetBorderSize(0); hangle_all.SetTitle("Distributions of opening angle")
#hangle_all.GetXaxis().SetTitle("Opening angle in degrees"); hangle_all.GetYaxis().SetTitle("number in bin")
#c1.SaveAs("/project/bfys/jrol/LHCb/figures/mva/P_pure.pdf")
#c2.SaveAs("/project/bfys/jrol/LHCb/figures/mva/PT_pure.pdf")
#c3.SaveAs("/project/bfys/jrol/LHCb/figures/mva/Mcorr_pure.pdf")
#c4.SaveAs("/project/bfys/jrol/LHCb/figures/mva/nHits_pure.pdf")
#c5.SaveAs("/project/bfys/jrol/LHCb/figures/mva/angle_pure.pdf")
input()

#Determine preformance; roc curve, auc score.
#fpr1, tpr1, thresholds1 = roc_curve(test["flag"], probabilities1[:, 1])

#fpr2, tpr2, thresholds2 = roc_curve(test["flag"], probabilities2[:, 1])
#auc1 = roc_auc_score(test["flag"], probabilities1[:, 1])
#auc2 = roc_auc_score(test["flag"], probabilities2[:, 1])
#fig, axes = plt.subplots(1, 2, figsize = (12,5))
#fig2, axes2, = plt.subplots(1, 2, figsize = (12, 5))
#axes2[0].plot(fpr2, thresholds2); axes2[0].set_xlabel("FPR")
#axes2[1].plot(tpr2, thresholds2); axes2[1].set_xlabel("TPR")
#plt.show(); input()
#xlims = [0, 1e-5]; xscales = ["linear", "log"]
#for i in range(len(axes)):
#    axe = axes[i]
#    axe.plot(fpr1, tpr1, label = "[{1}]; AUC = {0:.3f}".format(auc1, obs_str))
#    axe.plot(fpr2, tpr2, label = "[{1}]; AUC = {0:.3f}".format(auc2, all_obs_str))
#    if i == 0: axe.legend(loc='best')
#    axe.set_xlim(xlims[i],1)
#    axe.set_ylim(0,1)
#    axe.set_xscale(xscales[i])
#    axe.set_xlabel('False positive rate')
#    axe.set_ylabel('True positive rate')
#    axe.grid(True)
    
#plt.show()
#savestring = "/project/bfys/jrol/LHCb/figures/mva/mva_" 
#for obs in observables:
#    savestring += obs + "-"
#savestring += ".pdf"
##fig.savefig(savestring)
