# fitting of B+ signal to MC data to 'pin' tails, i.e. fix CB parameters.
# by Jan Rol, 29-9-2020

import ROOT as R

treeloc = "/data/bfys/mvegh/"
f_tree = R.TFile.Open("{0}MC_2012_Bu2JpsimmK_Strip21_MagDown.root".format(treeloc))
old_tree = f_tree.Get("DecayTree")
print("Loaded TTree!")

old_tree.SetBranchStatus("*", 0)

# Get specific branches

for branch in ["event", "B_s0_JCMass"]:
    old_tree.SetBranchStatus(branch, 1)

f_new_tree = R.TFile.Open("/data/bfys/jrol/MC_2012.root", "RECREATE")
new_tree   = old_tree.CloneTree()

nEvents = int(1.0 * old_tree.GetEntries())
j = 0
for i in range(nEvents):
    old_tree.GetEntry(i)
    bkg_cat = old_tree.getattr("Bplus_BKGCAT")
    if (bkg_cat = 0 or bkg_cat = 50):
        new_tree.Fill()
        j += 1

print(j)
new_tree.Write("", R.TObject.kOverwrite)
f_tree_new.Close()


