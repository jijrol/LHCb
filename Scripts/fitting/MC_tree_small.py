# fitting of B+ signal to MC data to 'pin' tails, i.e. fix CB parameters.
# by Jan Rol, 29-9-2020

import ROOT as R

treeloc = "/data/bfys/mvegh/"
f_tree = R.TFile.Open("{0}MC_2012_Bu2JpsimmK_Strip21_MagDown.root".format(treeloc))
old_tree = f_tree.Get("B2JpsimmKTuple/DecayTree")
print("Loaded TTree!")


f_new_tree = R.TFile.Open("/data/bfys/jrol/MC_2012.root", "RECREATE")
middle_tree   = old_tree.CloneTree(0)

nEvents = int(1.0 * old_tree.GetEntries())
j = 0
for i in range(nEvents):
    old_tree.GetEntry(i)
    bkg_cat = getattr(old_tree, "B_s0_BKGCAT")
    if (bkg_cat == 0 or bkg_cat == 50):
        middle_tree.Fill()
        j += 1

middle_tree.SetBranchStatus("*", 0)
for branch in ["event", "B_s0_JCMass"]:
    middle_tree.SetBranchStatus(branch, 1)

new_tree = middle_tree.CloneTree()

print(j)
new_tree.Write("", R.TObject.kOverwrite)
f_new_tree.Close()


