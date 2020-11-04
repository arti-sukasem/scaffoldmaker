"""
Generates a 3-D unit box mesh with variable numbers of elements in 3 directions.
"""

from __future__ import division
import math
from opencmiss.utils.zinc.field import findOrCreateFieldCoordinates
from opencmiss.zinc.element import Element, Elementbasis
from opencmiss.zinc.field import Field
from opencmiss.zinc.node import Node
from scaffoldmaker.meshtypes.scaffold_base import Scaffold_base
from scaffoldmaker.utils.eftfactory_tricubichermite import eftfactory_tricubichermite
from scaffoldmaker.utils.meshrefinement import MeshRefinement

class MeshType_3d_lung1_Arti(Scaffold_base):
    '''
    classdocs
    '''
    @staticmethod
    def getName():
        return '3D Lung 1 Arti'

