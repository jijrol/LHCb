import numpy as np
import pandas as pd
import uproot
import matplotlib.pyplot as plt
from sklearn.neural_network import MLPClassifier
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_curve, roc_auc_score

# Import trees
loc = "/data/bfys/jrol/RapidSim/{0}2tau2pipipi_filtered.root"

f_Dplus  = uproot.open(loc.format("Dplus"));  Dplus_tree  = f_Dplus["DecayTree"]
f_Dsplus = uproot.open(loc.format("Dsplus")); Dsplus_tree = f_Dsplus["DecayTree"]
f_Bplus  = uproot.open(loc.format("Bplus"));  Bplus_tree  = f_Bplus["DecayTree"]
f_Bcplus = uproot.open(loc.format("Bcplus")); Bcplus_tree = f_Bcplus["DecayTree"]

Dp_df  = Dplus_tree.pandas.df()#;  Dp_df.rename(columns  = {"Dp_0_P" : "P", "Dp_0_PT" : "PT"}, inplace = True)
Dsp_df = Dsplus_tree.pandas.df()#; Dsp_df.rename(columns = {"Dsp_0_P" : "P", "Dsp_0_PT" : "PT"}, inplace = True)
Bp_df  = Bplus_tree.pandas.df()#;  Bp_df.rename(columns  = {"Bp_0_P" : "P", "Bp_0_PT" : "PT"}, inplace = True)
Bcp_df = Bcplus_tree.pandas.df()#; Bcp_df.rename(columns = {"Bcp_0_P" : "P", "Bcp_0_PT" : "PT"}, inplace = True)
print("Loaded trees, converted to pandas.")

# Add flags for signal and background
Bp_df["flag"] = 1; Bcp_df["flag"] = 1
Dp_df["flag"] = 0; Dsp_df["flag"] = 0

full_frame = pd.concat([Dp_df, Dsp_df, Bp_df, Bcp_df], ignore_index=True, sort=False)
observables     = ["PT", "Mcorr", "BpTracking_nHits", "angle"]; obs_str = ""
for obs in observables:
    obs_str += obs + ", "
all_observables = ["P", "PT", "Mcorr", "BpTracking_nHits", "angle"]; all_obs_str = "" 
for obs in all_observables:
    all_obs_str += obs + ", "
print(obs_str, all_obs_str)
train, test = train_test_split(full_frame, test_size=0.5)


# GBC config, Fit vars to training set
verbose = 1
tol = 1e-4
init = "zero"
n_estimators = 100
gbc1 = GradientBoostingClassifier(verbose=verbose, tol=tol, init=init, n_estimators=n_estimators)
gbc2 = GradientBoostingClassifier(verbose=verbose, tol=tol, init=init, n_estimators=n_estimators)
gbc1.fit(train[observables], train["flag"])
gbc2.fit(train[all_observables], train["flag"])
print("Completed training")

# Apply training to give prob and pred
predictions1   = gbc1.predict(test[observables])
predictions2   = gbc2.predict(test[all_observables])
probabilities1 = gbc1.predict_proba(test[observables])
probabilities2 = gbc2.predict_proba(test[all_observables])

#Determine preformance; roc curve, auc score.
fpr1, tpr1, thresholds1 = roc_curve(test["flag"], probabilities1[:, 1])
fpr2, tpr2, thresholds2 = roc_curve(test["flag"], probabilities2[:, 1])
auc1 = roc_auc_score(test["flag"], probabilities1[:, 1])
auc2 = roc_auc_score(test["flag"], probabilities2[:, 1])
fig, axes = plt.subplots(1, 2, figsize = (12,5))
xlims = [0, 1e-5]; xscales = ["linear", "log"]
for i in range(len(axes)):
    axe = axes[i]
    axe.plot(fpr1, tpr1, label = "[{1}]; AUC = {0:.3f}".format(auc1, obs_str))
    axe.plot(fpr2, tpr2, label = "[{1}]; AUC = {0:.3f}".format(auc2, all_obs_str))
    if i == 0: axe.legend(loc='best')
    axe.set_xlim(xlims[i],1)
    axe.set_ylim(0,1)
    axe.set_xscale(xscales[i])
    axe.set_xlabel('False positive rate')
    axe.set_ylabel('True positive rate')
    axe.grid(True)

plt.show()
savestring = "/project/bfys/jrol/LHCb/figures/mva/mva_" 
for obs in observables:
    savestring += obs + "-"
savestring += ".pdf"
fig.savefig(savestring)
