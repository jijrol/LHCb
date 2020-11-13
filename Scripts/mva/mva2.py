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

f_Dplus  = loc.format("Dplus");  Dplus_tree  = f_Dplus["DecayTree"]
f_Dsplus = loc.format("Dsplus"); Dsplus_tree = f_Dplus["DecayTree"]
f_Bplus  = loc.format("Bplus");  Bplus_tree  = f_Dplus["DecayTree"]
f_Bcplus = loc.format("Bcplus"); Bcplus_tree = f_Dplus["DecayTree"]

Dp_df  = Dplus_tree.pandas.df();  Dp_df.rename(columns  = {"Dp_0_P" : "P", "Dp_0_PT" : "PT"})
Dsp_dp = Dsplus_tree.pandas.df(); Dsp_df.rename(columns = {"Dsp_0_P" : "P", "Dsp_0_PT" : "PT"})
Bp_df  = Bplus_tree.pandas.df();  Bp_df.rename(columns  = {"Bp_0_P" : "P", "Bp_0_PT" : "PT"})
Bcp_df = Bcplus_tree.pandas.df(); Bcp_df.rename(columns = {"Bcp_0_P" : "P", "Bcp_0_PT" : "PT"})
print("Loaded trees, converted to pandas.", "")

# Add flags for signal and background
Bp_df["flag"] = 1; Bcp_df["flag"] = 1
Dp_df["flag"] = 0; Dsp_df["flag"] = 0

full_frame = pd.concat([Dp_df, Dsp_df, Bp_df, Bcp_df], ignoreindex=True, sort=False)
print(full_frame)

observables = ["P", "PT", "MCorr", "BpTracking_nHits"]

train, test = train_test_split(full_frame, test_size=0.5)

# GBC config, Fit vars to training set
verbose = 1
tol = 1e-4
init = "zero"
n_estimators = 100
gbc = GradientBoostingClassifier(verbose=verbose, tol=tol, init=init, n_estimators=n_estimators)
gbc.fit(train[observables], train["flag"])
print("Completed training")

# Apply training to give prob and pred
predictions   = gbc.predict(test[variables]); print("predictions: ", predictions)
probabilities = gbc.predict_proba(test[variables]); print("probabilities: ", probabilities)

#Determine preformance; roc curve, auc score.
fpr, tpr, thresholds = roc_curve(test["flag"], probabilities[:, 1])
auc = roc_auc_score(test["flag"], probabilities[:, 1])