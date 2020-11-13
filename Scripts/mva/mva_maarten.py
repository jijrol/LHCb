import numpy as np
import pandas as pd
import uproot
from sklearn.neural_network import MLPClassifier
from sklearn.ensemble import AdaBoostClassifier, GradientBoostingClassifier

# get data
loc = "/eos/lhcb/user/m/mveghel/upgradecaloreco/"
ftree = uproot.open(loc+"trackcalomatch_electrons_new.root")
tree = ftree["TrackCaloMatchMCResolutionStudy/TrackTuple"]

# observables
basevars = ["Track_TRUEID"]

selvars = ["Track_inEcalAcc","Track_hasCaloHypo","Track_P","Track_Type"]

oldvars = ["Track_TrackMatch_CaloHypo_chi2_3D","Track_TrackMatch_CaloCluster_E","Track_EcalE","Track_CaloCluster_sigma2_E","Track_TrackMatch_CaloCluster_chi2_2D","Track_HcalE"]

hypovars = ["Track_CaloHypo_E","Track_CaloHypo_sigma2_E","Track_CaloHypo_x","Track_CaloHypo_y","Track_StateAtCalo_hypoz_x","Track_StateAtCalo_hypoz_y","Track_P"]

clusvars = ["Track_CaloCluster_E","Track_CaloCluster_sigma2_E","Track_CaloCluster_x","Track_CaloCluster_y","Track_StateAtCalo_clusterz_x", "Track_StateAtCalo_clusterz_y", "Track_P"]

# sets

set1 = ["Track_TrackMatch_CaloHypo_chi2_3D","Track_P"]
set2 = hypovars
set3 = clusvars
set4 = list(set(set1+set2))
set5 = list(set(set1+set3))

# dataframes
observables = list(set(basevars+selvars+oldvars+hypovars+clusvars))

nEntries = 2000000
fulldata = tree.pandas.df(observables,entrystop=nEntries)

# add observables
fulldata['flag'] = 1*(abs(fulldata['Track_TRUEID'])==11)

# apply selection
data = fulldata[(fulldata['Track_inEcalAcc']==1)&(fulldata['Track_hasCaloHypo']==1)&(fulldata['Track_Type']==3)&(fulldata['Track_P']>5e3)]

### define classifier
from sklearn.model_selection import train_test_split
train, test = train_test_split(data, test_size=0.5)

mvas1 = { "base" : { "vars" : set1, "name" : r"$\chi^{2}_{\mathrm{3D}}$", "color" : "gray", "style" : "dashed" }
        , "set2" : { "vars" : set2, "name" : r"Input vars (Hypo) from $\chi^{2}_{\mathrm{3D}}$", "color" : "black", "style" : "dashed" }
        , "set3" : { "vars" : set3, "name" : r"Equivalent Cluster variables", "color" : "black", "style" : "solid" }
        , "set4" : { "vars" : set4, "name" : r"Input vars (Hypo) from $\chi^{2}_{\mathrm{3D}}$ + $\chi^{2}_{\mathrm{3D}}$", "color" : "green", "style" : "solid" }
        , "set5" : { "vars" : set5, "name" : r"Equivalent Cluster variables + $\chi^{2}_{\mathrm{3D}}$", "color" : "red", "style" : "solid" }
        }

mvas = mvas1
mvasname = "calo_vs_hypo"

# config of classifier
verbose = 1
tol = 1e-3
init = 'zero'
n_estimators = 2000

for mva in mvas:
    mvas[mva]["mva"] = GradientBoostingClassifier(verbose=verbose, tol=tol, init=init, n_estimators=n_estimators)

# train
print(f"Starting training of MVA ({type(mvas['base']['mva'])})")
for mva in mvas:
    mvas[mva]["mva"].fit(train[mvas[mva]["vars"]], train['flag'])

# apply training using probabilities
for mva in mvas:
    mvas[mva]["pred"] = mvas[mva]["mva"].predict(test[mvas[mva]["vars"]])
    mvas[mva]["prob"] = mvas[mva]["mva"].predict_proba(test[mvas[mva]["vars"]])

# determine performance
import matplotlib.pyplot as plt
from sklearn.metrics import roc_curve, roc_auc_score

for mva in mvas:
    prob = mvas[mva]["prob"]
    fpr, tpr, thresholds = roc_curve(test['flag'],prob[:,1])
    auc = roc_auc_score(test['flag'],prob[:,1])
    mvas[mva]["fpr"] = fpr; mvas[mva]["tpr"] = tpr
    mvas[mva]["auc"] = auc; mvas[mva]["thresholds"] = thresholds

# plotting
import matplotlib.pyplot as plt

fig, axes = plt.subplots(1,2,figsize=(12,5))

rndguess = np.arange(0.,1.,1./len(mvas['base']['fpr']))
xlims = [0,1e-4]; xscales = ['linear','log']
for i in range(len(axes)):
    axe = axes[i]
    for mva in mvas:
        mvavar = mvas[mva]
        axe.plot(mvavar["fpr"], mvavar["tpr"], label = f"{mvavar['name']}, AUC = {mvavar['auc']:.3f}",color=mvavar['color'],linestyle=mvavar['style'])
    if i == 0: axe.legend(loc='best')
    axe.set_xlim(xlims[i],1)
    axe.set_ylim(0,1)
    axe.set_xscale(xscales[i])
    axe.set_xlabel('False positive rate')
    axe.set_ylabel('True positive rate')
    axe.grid(True)

# save some plots
savefig = True
if savefig:
    for ext in ["png","pdf","eps"]:
        plt.savefig("figs/electronshower_mva/{0}_{2}.{1}".format("roc_curves",ext,mvasname))

# show plot
plt.show()