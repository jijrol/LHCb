# First structure for HLT(2)Line.

# Jan Rol 01-07-2020

# Triggers on B+ -> tau - > pi+ pi- pi+

from Moore.config import HltLine, register_line_builder
from ..standard.particles import make_has_rich_long_pions

from RecoConf.reco_objects_from_file import upfront_reconstruction, make_pvs

from GaudiKernel.SystemOfUnits import Mev, GeV
from ..algorithms import (
    require_all,
    ParticleCombinerWithPVs,
    ParticleFilterWithPVs
)


all_lines = {}

#@configurable ?
def filter_particles(particles, pvs, pt_min=0.5*GeV, pid=None):
#Prototype of particle maker. Takes input pid and cuts.    
    code = require_all(
        "PT > {pt_min}"
        ).format(
        pt_min = pt_min)
    if pid is not None:
        code += " & ({0})".format(pid)
    return ParticleFilterWithPVs(particles, pvs, Code=code)

#@configurable ?
def make_pions(particles, pvs, pid):
    return filter_particles(particles, pvs, pid=pid) # Pion ID?

#@configurable ?
def make_taus(particles=pions, pvs): # Add cuts as fucntion arguments
    combination_code = require_all(
        "")
    vertex_cut = require all(
        "")
    return ParticleCombinerWithPVs(
        particles=particles,
        pvs=pvs,
        DecayDiscriptor="tau+ -> pi+ pi- pi+",
        CombinationCut=combination_code,
        MotherCut=vertex_cut
    )

#@configurable ?
def make_bus(particles=taus, pvs):   # Add cuts as function arguments
    combination_code = require_all(
        "")
    vertex_cut = require_all(
        "")
    return ParticleCombinerWithPVs(
        particles=particles,
        pvs=pvs,
        DecayDiscriptor="B+ -> tau+",
        CombinationCut=combination_code,
        MotherCut=vertex_cut
    )


@register_line_builder(all_lines)
#@configurable ?
def butotautopipipi(name = "BuToTauToPipPimPip", prescale = 1):
    pvs = make_pvs()
    pions = make_pions(make_has_rich_long_pions(), pvs)
    taus = make_taus(particles=pions, descriptors=["tau+ -> pi+ pi- pi+"], pvs=pvs)
    bus = make_bus(particles=taus, descriptors=["B+ -> tau+"], pvs=pvs)
return HltLine(
    name=name,
    algs=upfront_reconstruction() + [bus],
    prescale=prescale,

 )