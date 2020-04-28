import math, os, sys
import ROOT as R

path = "project/bfys/jrol/data/"
rs_tree = R.TFile("DecayTree")
fs_tree = R.TChain("Bp2JpsiKp/DecayTree")

for pol in ["up", "down"]:
    fname = "ntuple_bp2jpsimmk_btracking_striplikesel_2018_mc_mag{0}.root".format(pol)
    fs_tree.Add("path.{0}".format(fname))

rs_tree.Add("path{0}".format("Bplus2Jpsi2Kp_ALLcut.root"))

rs_hist_Bp_P  = R.TH1F("rs_hist_Bp_P",  "rs_hist_Bp_P", 100, 0, 300)
fs_hist_Bp_P  = R.TH1F("fs_hist_BP_P",  "fs_hist_Bp_P", 100, 0, 300)
rs_hist_Bp_FD = R.TH1F("rs_hist_Bp_FD", "rs_hist_Bp_FD", 100, 0, 3000)
fs_hist_Bp_FD = R.TH1F("fs_hist_Bp_FD", "fs_hist_Bp_FD", 100, 0, 3000)
rs_hist_Kp_IP = R.TH1F("rs_hist_Kp_IP", "rs_hist_Kp_IP", 100, 0, 500)
fs_hist_Bp_FD = R.TH1F("fs_hist_Kp_IP", "fs_hist_Kp_IP", 100, 0, 500)


tree_dict = {
    "rs"   : {"tree" : rs_tree,   "hist_Bp_P" : rs_hist_Bp_P,   "hist_Bp_FD" : rs_hist_Bp_FD  , "hist_Kp_IP" : rs_hist_Kp_IP}
    "fsim" : {"tree" : fsim_tree, "hist_Bp_P" : fsim_hist_Bp_P, "hist_Bp_FD" : fsim_hist_Bp_FD, "hist_Kp_IP" : fsim_hist_Kp_IP}
}

for dict in tree_dict:
    print(dict)
    for i in range(0, dict["tree"].GetEntries()):
        dict["tree"].GetEntry(i)
        dict["hist_P"].Fill(getattr(dict["tree"], "Bp_P"))

rs_hist_Bp_P.Draw()
fs_hist_Bp_P.Draw("same")
        


