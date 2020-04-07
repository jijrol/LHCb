# Plotter from dictionary of variables for 0 velo hits or 1+ velo hits
# Dictionaries saved in figures/data/...velo/dict.pkl
# Current variables: P PT eta IP angle and FD-(meson)

#Pickle data structure: a dictionary of lists containing the 6 var's 5 for daughter particle,
# 1 for the parent (FD). Dictionaries are loaded for the daughters or parents,
# resulting in a dictionary of dictionaries of lists to plot from.

import pickle
import math
import matplotlib.pyplot as plt
import numpy as np

def load_obj(path):
	with open(path, 'rb') as input:
		obj = pickle.load(input, encoding='latin1')
	return obj

def load_dict(parent, daughter, hits):
    path = "C:/Users/janro/Documents/LHCb/figures/data/{0}velo/{1}_{2}.pkl".format(hits, parent, daughter)
    some = load_obj(path)
    return some

def plot_parents(variable, daughter, hit):
    main_dict = dict.fromkeys(parents, None)
    plt.figure()
    for parent in parents:
        main_dict[parent] = load_dict(parent, daughter, hit)
        list = main_dict[parent][variable]
        weights = np.ones(len(list)) / len(list)
        plt.hist(list, bins=50, log=False, label=parent,
        weights=weights, histtype="step", range=x_range_dict[variable])
    plt.ylabel("Probability density")
    plt.xlabel(x_label_dict[variable])
    plt.title("Daughter {0} with parents: {1} - {2} hit(s)".format(daughter, variable, hit))
    plt.legend()
    #plt.show()
    savepath = "C:/Users/janro/Documents/LHCb/figures/parents_comp/{0}_{1}_{2}hit.pdf".format(daughter, variable, hit)
    plt.savefig(savepath)
    plt.close()

def plot_daughters(variable, parent, hit):
    main_dict = dict.fromkeys(daughters, None)
    plt.figure()
    for daughter in daughters:
        main_dict[daughter] = load_dict(parent, daughter, hit)
        list = main_dict[daughter][variable]
        weights = np.ones(len(list)) / len(list)
        plt.hist(list, bins=50, log=False, label=daughter,
        weights=weights, histtype="step", range=x_range_dict[variable])
    plt.ylabel("Probability density")
    plt.xlabel(x_label_dict[variable])
    plt.title("Daughters of {0}: {1} - {2} hit(s)".format(parent, variable, hit))
    plt.legend()
    #plt.show()
    savepath = "C:/Users/janro/Documents/LHCb/figures/daughters_comp/{0}_{1}_{2}hit.pdf".format(parent, variable, hit)
    plt.savefig(savepath)
    plt.close()

def plot_hits(variable, parent, daughter):
    main_dict = dict.fromkeys(hits, None)
    plt.figure()
    for hit in hits:
        main_dict[hit] = load_dict(parent, daughter, hit)
        list = main_dict[hit][variable]
        weights = np.ones(len(list)) / len(list)
        plt.hist(list, bins=50, log=False, label="{0} hit(s)".format(hit),
        weights=weights, histtype="step", range=x_range_dict[variable])
    plt.ylabel("Probability density")
    plt.xlabel(x_label_dict[variable])
    plt.title("{0} to {1} - var: {2} - 0 hits vs. 1+ hit".format(parent, daughter, variable))
    plt.legend()
    #plt.show()
    savepath = "C:/Users/janro/Documents/LHCb/figures/hits_comp/{0}_{1}_{2}.pdf".format(parent, daughter, variable)
    plt.savefig(savepath)
    plt.close()

parents   = ["Bplus", "Bcplus", "Dplus", "Dsplus"]
daughters = ["e", "mu", "pipipi"]
hits      = ["0", "1"]
variables = ["P", "PT", "eta", "IP", "angle", "FD"]

x_label_dict = {"P"     : "Momentum of daughter (Gev/c)", 
				"PT"    : "Transverse momentum of daughter (Gev/c)", 
				"eta"   : "Pseudorapidity of daughter",
				"IP"    : "Impact Parameter of daughter ($\mu$m)", 
				"angle" : "Angle between parent and daughter momenta (degrees)",
                "FD"    : "Flight distance of Meson(s) ($\mu$m)"}
x_range_dict = {"P"     : (0, 150), 
                "PT"    : (0, 10), 
                "eta"   : (1, 6),
                "IP"    : (0, 2000), 
                "angle" : (0, 2),
                "FD"    : (15000, 50000)}

#for parent in parents:
#    print("1")
#    for hit in hits:
#        for variable in variables:
#            plot_daughters(variable, parent, hit)

for daughter in daughters:
    print("2")
    for hit in hits:
        for variable in variables:
            plot_parents(variable, daughter, hit)

#for parent in parents:
#    print("3")
#    for daughter in daughters:
#        for variable in variables:
#            plot_hits(variable, parent, daughter)
