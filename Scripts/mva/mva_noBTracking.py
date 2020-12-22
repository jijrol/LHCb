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
loc_yeB = "/data/bfys/jrol/RapidSim/{0}2tau2pipipi_filtered.root"
loc_noB = "/data/bfys/jrol/RapidSim/{0}2tau2pipipi_noBTracking.root"

f_Dplus_noB  = uproot.open(loc_noB.format("Dplus"));  Dplus_tree_noB  = f_Dplus_noB["DecayTree"]
f_Dsplus_noB = uproot.open(loc_noB.format("Dsplus")); Dsplus_tree_noB = f_Dsplus_noB["DecayTree"]
f_Bplus_noB  = uproot.open(loc_noB.format("Bplus"));  Bplus_tree_noB  = f_Bplus_noB["DecayTree"]
f_Bcplus_noB = uproot.open(loc_noB.format("Bcplus")); Bcplus_tree_noB = f_Bcplus_noB["DecayTree"]

f_Dplus_yeB  = uproot.open(loc_yeB.format("Dplus"));  Dplus_tree_yeB  = f_Dplus_yeB["DecayTree"]
f_Dsplus_yeB = uproot.open(loc_yeB.format("Dsplus")); Dsplus_tree_yeB = f_Dsplus_yeB["DecayTree"]
f_Bplus_yeB  = uproot.open(loc_yeB.format("Bplus"));  Bplus_tree_yeB  = f_Bplus_yeB["DecayTree"]
f_Bcplus_yeB = uproot.open(loc_yeB.format("Bcplus")); Bcplus_tree_yeB = f_Bcplus_yeB["DecayTree"]

Dp_df_noB  = Dplus_tree_noB.pandas.df();  Dp_df_yeB  = Dplus_tree_yeB.pandas.df()
Dsp_df_noB = Dsplus_tree_noB.pandas.df(); Dsp_df_yeB = Dsplus_tree_yeB.pandas.df()
Bp_df_noB  = Bplus_tree_noB.pandas.df();  Bp_df_yeB  = Bplus_tree_yeB.pandas.df()
Bcp_df_noB = Bcplus_tree_noB.pandas.df(); Bcp_df_yeB = Bcplus_tree_yeB.pandas.df()

h2d_sig = R.TH2F("2dh_sig", "Signal events", 30, 0, 7.0, 30, 0, 4)
h2d_bkg = R.TH2F("2dh_bkg", "Background events", 30, 0, 7.0, 30, 0, 4)
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
Bp_df_noB["flag"] = 1; Bcp_df_noB["flag"] = 1; Bp_df_yeB["flag"] = 1; Bcp_df_yeB["flag"] = 1
Dp_df_noB["flag"] = 0; Dsp_df_noB["flag"] = 0; Dp_df_yeB["flag"] = 0; Dsp_df_yeB["flag"] = 0

full_frame_noB = pd.concat([Dp_df_noB, Dsp_df_noB, Bp_df_noB, Bcp_df_noB], ignore_index=True, sort=False)
full_frame_yeB = pd.concat([Dp_df_yeB, Dsp_df_yeB, Bp_df_yeB, Bcp_df_yeB], ignore_index=True, sort=False)
yeB_observables = ["P", "PT", "Mcorr", "BpTracking_nHits", "angle"] 
noB_observables = ["P", "PT", "Mcorr_noBTracking", "angle"]
train_noB, test_noB = train_test_split(full_frame_noB, test_size=0.5)
train_yeB, test_yeB = train_test_split(full_frame_yeB, test_size=0.5)

# GBC config, Fit vars to training set
verbose = 1
tol = 1e-4
init = "zero"
n_estimators = 100
gbc_noB = GradientBoostingClassifier(verbose=verbose, tol=tol, init=init, n_estimators=n_estimators)
gbc_yeB = GradientBoostingClassifier(verbose=verbose, tol=tol, init=init, n_estimators=n_estimators)
gbc_noB.fit(train_noB[noB_observables], train_noB["flag"])
gbc_yeB.fit(train_yeB[yeB_observables], train_yeB["flag"])

# Apply training to give prob and pred
predictions_noB   = gbc_noB.predict(test_noB[noB_observables])
predictions_yeB   = gbc_yeB.predict(test_yeB[yeB_observables])
probabilities_noB = gbc_noB.predict_proba(test_noB[noB_observables])
probabilities_yeB = gbc_yeB.predict_proba(test_yeB[yeB_observables])

#Determine preformance; roc curve, auc score.
fpr_noB, tpr_noB, thresholds_noB = roc_curve(test_noB["flag"], probabilities_noB[:, 1])
fpr_yeB, tpr_yeB, thresholds_yeB = roc_curve(test_yeB["flag"], probabilities_yeB[:, 1])
auc_noB = roc_auc_score(test_noB["flag"], probabilities_noB[:, 1])
auc_yeB = roc_auc_score(test_yeB["flag"], probabilities_yeB[:, 1])
fig, axes = plt.subplots(1, 2, figsize = (12,5))
xlims = [0, 1e-4]; xscales = ["linear", "log"]
for i in range(len(axes)):
    axe = axes[i]
    axe.xaxis.set_tick_params(labelsize=14); axe.yaxis.set_tick_params(labelsize=14)
    axe.plot(fpr_noB, tpr_noB, label = "No BpTracking; AUC = {0:.3f}".format(auc_noB))
    axe.plot(fpr_yeB, tpr_yeB, label = "BpTracking; AUC = {0:.3f}".format(auc_yeB))
    if i == 0: axe.legend(loc='best', fontsize=14)
    axe.tick_params(size=20)
    axe.set_xlim(xlims[i],1)
    axe.set_ylim(0,1)
    axe.set_xscale(xscales[i])
    axe.set_xlabel('False positive rate', fontsize = 14)
    axe.set_ylabel('True positive rate', fontsize = 14)
    axe.grid(True)
plt.subplots_adjust(wspace=0.24)    
savestring = "/project/bfys/jrol/LHCb/figures/mva/mva_noB.pdf"
plt.savefig(savestring)
plt.show()
