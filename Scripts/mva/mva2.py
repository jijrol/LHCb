import numpy as np
#import pandas as pd
#import uproot
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
loc_noB = "/data/bfys/jrol/RapidSim/{0}2tau2pipipi_noBTracking.root"
loc_yeB = "/data/bfys/jrol/RapidSim/{0}2tau2pipipi_filtered.root"

#f_Dplus  = R.TFile.Open(loc.format("Dplus"));  Dplus_tree  = f_Dplus.Get("DecayTree")
#f_Dsplus = R.TFile.Open(loc.format("Dsplus")); Dsplus_tree = f_Dsplus.Get("DecayTree")


f_Bplus_noB  = R.TFile.Open(loc_noB.format("Bplus"));  Bplus_tree_noB  = f_Bplus_noB.Get("DecayTree")
f_Bplus_yeB  = R.TFile.Open(loc_yeB.format("Bplus"));  Bplus_tree_yeB  = f_Bplus_yeB.Get("DecayTree")
f_Bcplus_noB = R.TFile.Open(loc_noB.format("Bcplus")); Bcplus_tree_noB = f_Bcplus_noB.Get("DecayTree")
f_Bcplus_yeB = R.TFile.Open(loc_yeB.format("Bcplus")); Bcplus_tree_yeB = f_Bcplus_yeB.Get("DecayTree")

#Dp_df...
#Dsp_df = Dsplus_tree.pandas.df()
#Bp_df  = Bplus_tree.pandas.df(); Bp_df = Bp_df.head(275000)
#Bcp_df = Bcplus_tree.pandas.df()
#bkg_amount = len(Dsp_df.index) + len(Dp_df.index)
#sig_amount = len(Bcp_df.index) + len(Bp_df.index); print(len(Bcp_df.index), len(Bp_df.index))
#total_amount = sig_amount + bkg_amount
#pure_amount = 0


h2d_sig = R.TH2F("h2d_sig", "B^{+} #rightarrow #tau^i{+} #rightarrow #pi^{+} #pi^{-} #pi^{+}", 30, 0, 7.0, 30, 0, 4)
h2d_bkg = R.TH2F("h2d_bkg", "B^{+} #rightarrow #tau^{+} #pi^{+} #pi^{-} #pi^{+}", 30, 0, 7.0, 30, 0, 4)
hP_Dp = R.TH1F("hP_Dp", "D^{+} #rightarrow #tau^{+} #rightarrow #pi^{+} #pi^{-} #pi^{+}", 50, 0, 600)
hP_Dsp = R.TH1F("hP_Dsp", "D^{+}_{s} #rightarrow #tau^{+} #rightarrow #pi^{+} #pi^{-} #pi^{+}", 50, 0, 600)
hP_Bp = R.TH1F("hP_Bp", "B^{+} #rightarrow #tau^{+} #rightarrow #pi^{+} #pi^{-} #pi^{+}", 50, 0, 600)
hP_Bcp = R.TH1F("hP_Bcp", "B^{+}_{c} #rightarrow #tau^{+} #rightarrow #pi^{+} #pi^{-} #pi^{+}", 50, 0, 600)
hPT_Dp = R.TH1F("hPT_Dp", "D^{+} #rightarrow #tau^{+} #rightarrow #pi^{+} #pi^{-} #pi^{+}", 50, 0, 50)
hPT_Dsp = R.TH1F("hPT_Dsp", "D^{+}_{s} #rightarrow #tau^{+} #rightarrow #pi^{+} #pi^{-} #pi^{+}", 50, 0, 50)
hPT_Bp = R.TH1F("hPT_Bp", "B^{+} #rightarrow #tau^{+} #rightarrow #pi^{+} #pi^{-} #pi^{+}", 50, 0, 50)
hPT_Bcp = R.TH1F("hPT_Bcp", "B^{+}_{c} #rightarrow #tau^{+} #rightarrow #pi^{+} #pi^{-} #pi^{+}", 50, 0, 50)
hMcorr_Bp_noB = R.TH1F("hMcorr_Bp_noB", "B^{+}", 50, 0, 9)
hMcorr_Bcp_noB = R.TH1F("hMcorr_Bcp_noB", "B^{+}_{c}", 50, 0, 9)
hMcorr_Bp_yeB = R.TH1F("hMcorr_Bp_yeB", "B^{+} w/ B-Tracking", 50, 0, 9)
hMcorr_Bcp_yeB = R.TH1F("hMcorr_Bcp_yeB", "B^{+}_{c} w/ B-Tracking", 50, 0, 9)
hBpTracking_nHits_Dp = R.TH1F("hBpTracking_nHits_Dp", "D^{+} #rightarrow #tau^{+} #rightarrow #pi^{+} #pi^{-} #pi^{+}", 8, 0.25, 4.25)
hBpTracking_nHits_Dsp = R.TH1F("hBpTracking_nHits_Dsp", "D^{+}_{s} #rightarrow #tau^{+} #rightarrow #pi^{+} #pi^{-} #pi^{+}", 8, 0.25, 4.25)
hBpTracking_nHits_Bp = R.TH1F("hBpTracking_nHits_Bp", "B^{+} #rightarrow #tau^{+} #rightarrow #pi^{+} #pi^{-} #pi^{+}", 8, 0.25, 4.25)
hBpTracking_nHits_Bcp = R.TH1F("hBpTracking_nHits_Bcp", "B^{+}_{c} #rightarrow #tau^{+} #rightarrow #pi^{+} #pi^{-} #pi^{+}", 8, 0.25, 4.25)
hangle_Dp = R.TH1F("hangle_Dp", "D^{+} #rightarrow #tau^{+} #rightarrow #pi^{+} #pi^{-} #pi^{+}", 50, 0, 3.0)
hangle_Dsp = R.TH1F("hangle_Dsp", "D^{+}_{s} #rightarrow #tau^{+} #rightarrow #pi^{+} #pi^{-} #pi^{+}", 50, 0, 3.0)
hangle_Bp = R.TH1F("hangle_Bp", "B^{+} #rightarrow #tau^{+} #rightarrow #pi^{+} #pi^{-} #pi^{+}", 50, 0, 3.0)
hangle_Bcp = R.TH1F("hangle_Bcp", "B^{+}_{c} #rightarrow #tau^{+} #rightarrow #pi^{+} #pi^{-} #pi^{+}", 50, 0, 3.0)

Bplus_tree_yeB.Draw("Mcorr>>hMcorr_Bp_yeB", "Mcorr < 9"); hMcorr_Bp_yeB.Scale(1/hMcorr_Bp_yeB.GetEntries())
Bcplus_tree_yeB.Draw("Mcorr>>hMcorr_Bcp_yeB", "Mcorr < 9"); hMcorr_Bcp_yeB.Scale(1/hMcorr_Bcp_yeB.GetEntries())
Bplus_tree_noB.Draw("Mcorr_noBTracking>>hMcorr_Bp_noB", "Mcorr_noBTracking < 9"); hMcorr_Bp_noB.Scale(1/hMcorr_Bp_noB.GetEntries())
Bcplus_tree_noB.Draw("Mcorr_noBTracking>>hMcorr_Bcp_noB", "Mcorr_noBTracking < 9"); hMcorr_Bcp_noB.Scale(1/hMcorr_Bcp_noB.GetEntries())

# Add flags for signal and background
#Bp_df["flag"] = 1; Bcp_df["flag"] = 1
#Dp_df["flag"] = 0; Dsp_df["flag"] = 0

#full_frame = pd.concat([Dp_df, Dsp_df, Bp_df, Bcp_df], ignore_index=True, sort=False)
observables     = ["PT", "Mcorr", "BpTracking_nHits", "angle"]
a_observables = ["P", "PT", "Mcorr", "BpTracking_nHits", "angle"] 

#train, test = train_test_split(full_frame, test_size=0.5)

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


#no_bkg_cut = 0.99119
#for i in range(len(test)-1):
#    P = test['P'].iloc[i]
#    PT = test['PT'].iloc[i]
#    Mcorr = test['Mcorr'].iloc[i]
#    nHits = test['BpTracking_nHits'].iloc[i]
#    angle = test['angle'].iloc[i]
#    hP_all.Fill(P)
#    hPT_all.Fill(PT)
#    hMcorr_all.Fill(Mcorr)
#    hnHits_all.Fill(nHits)
#    hangle_all.Fill(angle)
#    if test['flag'].iloc[i] < 1:
#    h2d_bkg.Fill(Mcorr, angle)
#        hP_bkg.Fill(P)
#        hPT_bkg.Fill(PT)
#        hMcorr_bkg.Fill(Mcorr)
#        hnHits_bkg.Fill(nHits)
#        hangle_bkg.Fill(angle) 
#    if test['flag'].iloc[i] > 0:
#        h2d_sig.Fill(Mcorr, angle)
#        hP_sig.Fill(P)
#        hPT_sig.Fill(PT)
#        hMcorr_sig.Fill(Mcorr)
#        hnHits_sig.Fill(nHits)
#        hangle_sig.Fill(angle)
#    if probabilities2[i, 1] >= no_bkg_cut:
#        pure_amount += 1
#        hP_pur.Fill(P)
#        hPT_pur.Fill(PT)
#        hMcorr_pur.Fill(Mcorr)
#        hnHits_pur.Fill(nHits)
#        hangle_pur.Fill(angle)
stack = R.THStack("stack", "B^{+}_{(c)} #rightarrow #tau #rightarrow #pi^{3}")
R.gStyle.SetPalette(1); R.gStyle.SetOptStat(0)
c1 = R.TCanvas("c1", "ctemp", 1200, 800)
hMcorr_Bp_noB.SetLineColor(R.kBlue); hMcorr_Bp_noB.SetLineStyle(R.kDashed)
hMcorr_Bp_yeB.SetLineColor(R.kBlue)
hMcorr_Bcp_noB.SetLineColor(R.kRed); hMcorr_Bcp_noB.SetLineStyle(R.kDashed)
hMcorr_Bcp_yeB.SetLineColor(R.kRed)

stack.Add(hMcorr_Bp_noB)
stack.Add(hMcorr_Bp_yeB)
stack.Add(hMcorr_Bcp_noB)
stack.Add(hMcorr_Bcp_yeB)
stack.Draw("HIST NOSTACK")
stack.GetXaxis().SetTitle("corrected mass (GeV/c^{2})")
stack.GetYaxis().SetTitle("arbitrary units")
stack.SetMinimum(0.0005); stack.SetMaximum(0.1)
Leg = c1.BuildLegend(0.25, 0.1, 0.55, 0.35); Leg.SetBorderSize(0)
c1.SetLogy()
c1.SaveAs("/project/bfys/jrol/LHCb/figures/selection/Mcorr_BTracking_comparison.pdf"); input()

#c1 = R.TCanvas("c1", "c1", 1200, 800); c1.SetRightMargin(0.12)
#h2d_sig.DrawNormalized("PLC COLZ"); h2d_sig.GetXaxis().SetTitle("M_{corr} (Gev/c)^{2}"); h2d_sig.GetYaxis().SetTitle("Opening angle in degrees")
#h2d_sig.SetTitle("Corrected mass vs. opening angle - signal")
#hP_all.Draw("PLC HIST"); hP_sig.Draw("PLC SAME HIST")
#hP_bkg.Draw("PLC SAME HIST"); hP_pur.Draw("PLC SAME HIST")
#L1 = R.gPad.BuildLegend(0.65, 0.7, 0.9, 0.82); L1.SetBorderSize(0); h2d_sig.SetTitle("Corrected mass vs. opening angle, Signal & Background")
#c1.SaveAs("/project/bfys/jrol/LHCb/figures/mva/individual_Mcorr_noB.pdf"); ctemp.SetBottomMargin(0.1)
#hP_all.GetXaxis().SetTitle("Momentum (Gev/c)"); hP_all.GetYaxis().SetTitle("number in bin")
#c2 = R.TCanvas("c2", "c2", 1200, 800); c2.SetRightMargin(0.12)
#h2d_bkg.DrawNormalized("PLC COLZ"); h2d_bkg.GetXaxis().SetTitle("M_{corr} (Gev/c)^{2}"); h2d_bkg.GetYaxis().SetTitle("Opening angle in degrees")
#h2d_bkg.SetTitle("Corrected mass vs. opening angle - background")
#c2.SaveAs("/project/bfys/jrol/LHCb/figures/mva/2d_bkg_Mcorr_angle.pdf")
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
