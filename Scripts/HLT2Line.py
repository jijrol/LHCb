# First structure for HLT(2)Line.

# Jan Rol 01-07-2020

# Triggers on B+ -> tau - > pi+ pi- pi+

from Moore.config import HltLine, register_line_builder
from ..standard.particles import make_has_rich_long_pions

from RecoConf.reco_objects_from_file import make_pvs

from GaudiKernel.SystemOfUnits import Mev, GeV
from ..algorithms import require_all, ParticleCombinerWithPVs


all_lines = {}



#@configurable ?
def make_pions(particles, pvs, pid):
    return filter_particles


@register_line_builder(all_lines)
#@configurable ?
def butotautopipipi(name = "BuToTauToPipPimPip", prescale = 1):
    pvs = make_pvs()
    pions = make_pions(make_has_rich_long_pions(), pvs)

    bus = make_bus()
return HltLine(
    name=name,
    algs=[pvs, bus],
    prescale=prescale,
 )