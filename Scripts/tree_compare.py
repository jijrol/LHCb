import math, os, sys
import ROOT as R

path = "/project/bfys/jrol/data/{0}"
rs_tree = R.TChain("DecayTree")
fs_tree = R.TChain("Bp2JpsimmKp/DecayTree")

#for pol in ["up", "down"]:
fname = "ntuple_bp2jpsimmk_btracking_striplikesel_2018_mc_magup.root"
fs_tree.Add(path.format(fname))

rs_tree.Add(path.format("Bplus2JPsi2Kplus_ALLcut.root"))

rs_hist_Bp_P  = R.TH1F("rs_hist_Bp_P",  "rs_hist_Bp_P", 100, 0, 300000)
fs_hist_Bp_P  = R.TH1F("fs_hist_BP_P",  "fs_hist_Bp_P", 100, 0, 300000)
rs_hist_Bp_FD = R.TH1F("rs_hist_Bp_FD", "rs_hist_Bp_FD", 100, 0, 30)
fs_hist_Bp_FD = R.TH1F("fs_hist_Bp_FD", "fs_hist_Bp_FD", 100, 0, 30)
rs_hist_Kp_IP = R.TH1F("rs_hist_Kp_IP", "rs_hist_Kp_IP", 100, 0, 4)
fs_hist_Kp_IP = R.TH1F("fs_hist_Kp_IP", "fs_hist_Kp_IP", 100, 0, 4)
rs_hist_mup_IP = R.TH1F("rs_hist_mup_IP", "rs_hist_mup_IP", 100, 0, 4)
fs_hist_mup_IP = R.TH1F("fs_hist_mup_IP", "fs_hist_mup_IP", 100, 0, 4)
rs_hist_mum_IP = R.TH1F("rs_hist_mum_IP", "rs_hist_mum_IP", 100, 0, 4)
fs_hist_mum_IP = R.TH1F("fs_hist_mum_IP", "fs_hist_mum_IP", 100, 0, 4)

tree_dict = {"rs" : {"tree" : rs_tree, "hist_Bp_P" : rs_hist_Bp_P, "hist_Bp_FD" : rs_hist_Bp_FD, "hist_Kp_IP" : rs_hist_Kp_IP, "nEvents" : 0
                                      ,"hist_mup_IP" : rs_hist_mup_IP, "hist_mum_IP" : rs_hist_mum_IP}
            ,"fs" : {"tree" : fs_tree, "hist_Bp_P" : fs_hist_Bp_P, "hist_Bp_FD" : fs_hist_Bp_FD, "hist_Kp_IP" : fs_hist_Kp_IP, "nEvents" : 0
                                      ,"hist_mup_IP" : fs_hist_mup_IP, "hist_mum_IP" : fs_hist_mum_IP}
            }

for method in ["rs", "fs"]:
    for i in range(0, tree_dict[method]["tree"].GetEntries()):
        tree = tree_dict[method]["tree"]
        tree_dict[method]["nEvents"] = tree.GetEntries()
        tree.GetEntry(i)
        Bp_P   = getattr(tree, "Bp_P")
        Bp_FD  = getattr(tree, "Bp_FD_OWNPV")
        Kp_IP  = getattr(tree, "Kp_IP_OWNPV")
        mup_IP = getattr(tree, "mup_IP_OWNPV")
        mum_IP = getattr(tree, "mum_IP_OWNPV")
        if method == "rs":
            Bp_P = Bp_P * 1000; Bp_FD = Bp_FD * 0.001; Kp_IP = Kp_IP * 0.001; mup_IP = mup_IP * 0.001; mum_IP = mum_IP * 0.001
        tree_dict[method]["hist_Bp_P"].Fill(Bp_P)
        tree_dict[method]["hist_Bp_FD"].Fill(Bp_FD)
        tree_dict[method]["hist_Kp_IP"].Fill(Kp_IP)
        tree_dict[method]["hist_mup_IP"].Fill(mup_IP)
        tree_dict[method]["hist_mum_IP"].Fill(mum_IP)

def make_legend():
    R.gPad.BuildLegend(0.75, 0.6, 0.9, 0.7)
    R.gPad.Update()

def save_canvasses():
    c1.SaveAs("/project/bfys/jrol/figures/root_figs/Bp_P.pdf")
    c2.SaveAs("/project/bfys/jrol/figures/root_figs/Bp_FD.pdf")
    c3.SaveAs("/project/bfys/jrol/figures/root_figs/Kp_IP.pdf")
    c4.SaveAs("/project/bfys/jrol/figures/root_figs/mup_IP.pdf")
    c5.SaveAs("/project/bfys/jrol/figures/root_figs/mum_IP.pdf")

R.gStyle.SetPalette(1)
c1 = R.TCanvas("canv1","canv1", 0, 0, 600, 400)
rs_hist_Bp_P.Draw("PLC")
fs_hist_Bp_P.Draw("PLC SAME")
make_legend()

c2 = R.TCanvas("canv2","canv2", 0, 0, 600, 400)
rs_hist_Bp_FD.Draw("PLC")
fs_hist_Bp_FD.Draw("PLC SAME")
make_legend()

c3 = R.TCanvas("canv3","canv3", 0, 0, 600, 400)
rs_hist_Kp_IP.Draw("PLC")
fs_hist_Kp_IP.Draw("PLC SAME")
make_legend()

c4 = R.TCanvas("canv4","canv4", 0, 0, 600, 400)
rs_hist_mup_IP.Draw("PLC")
fs_hist_mup_IP.Draw("PLC SAME")
make_legend()

c5 = R.TCanvas("canv5","canv5", 0, 0, 600, 400)
rs_hist_mum_IP.Draw("PLC")
fs_hist_mum_IP.Draw("PLC SAME")
make_legend()

save_canvasses()
print("done")
input()        


