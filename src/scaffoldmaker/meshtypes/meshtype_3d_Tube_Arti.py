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


class MeshType_3d_Tube_Arti(Scaffold_base):
    '''
    classdocs
    '''

    @staticmethod
    def getName():
        return '3D Tube Arti'

    @staticmethod
    def getDefaultOptions(cls, parameterSetName='Default'):
        return {
            'Number of element around': 4,
            'Number of element along': 2,
            'Use cross derivatives': False,
            'Refine': False,
            'Refine Element around': 1,
            'Refine Element along': 1
        }

    @staticmethod
    def getOrderedOptionNames():
        return [
            'Number of element around',
            'Number of element along',
            'Use cross derivatives',
            'Refine',
            'Refine Element around',
            'Refine Element along'
        ]

    @staticmethod
    def checkOptions(options):
        if (options['Number of element around'] < 1):
            options['Number of element around'] = 1
        if (options['Number of element along'] < 1):
            options['Number of element along'] = 1
        if (options['Refine Element around'] < 1):
            options['Refine Element around'] = 1
        if (options['Refine Element along'] < 1):
            options['Refine Element along'] = 1

    @classmethod
    def generateBaseMesh(cls, region, options):
        """
        :param region: Zinc region to define model in. Must be empty.
        :param options: Dict containing options. See getDefaultOptions().
        :return: [] empty list of AnnotationGroup
        """


