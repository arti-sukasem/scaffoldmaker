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


class MeshType_3d_left_lung_Arti(Scaffold_base):
    '''
    classdocs
    '''

    @staticmethod
    def getName():
        return '3D Left Lung Arti'

    @staticmethod
    def getDefaultOptions(cls, parameterSetName='Default'):
        return {
            'Side 1': 1.0,
            'Side 2': 1.0,
            'Side 3': 1.0,
            'Number of element 1': 1,
            'Number of element 2': 1,
            'Number of element 3': 1,
            'Use cross derivatives': False,
        }

    @staticmethod
    def getOrderedOptionNames():
        return [
            'Side 1',
            'Side 2',
            'Side 3',
            'Number of element 1',
            'Number of element 2',
            'Number of element 3',
            'Use cross derivatives'
        ]

    @staticmethod
    def checkOptions(options):
        if (options['Side 1'] < 0):
            options['Side 1'] = 1.0
        if (options['Side 2'] < 0):
            options['Side 2'] = 1.0
        if (options['Side 3'] < 0):
            options['Side 3'] = 1.0
        if (options['Number of element 1'] < 1):
            options['Number of element 1'] = 1
        if (options['Number of element 2'] < 1):
            options['Number of element 2'] = 1
        if (options['Number of element 3'] < 1):
            options['Number of element 3'] = 1

    @classmethod
    def generateBaseMesh(cls, region, options):
        """
        :param region: Zinc region to define model in. Must be empty.
        :param options: Dict containing options. See getDefaultOptions().
        :return: [] empty list of AnnotationGroup
        """
        sidelength1 = options['Side 1']
        sidelength2 = options['Side 2']
        sidelength3 = options['Side 3']
        elementCount1 = options['Number of element 1']
        elementCount2 = options['Number of element 2']
        elementCount3 = options['Number of element 3']
        useCrossDerivatives = options['Use cross derivatives']

        fm = region.getFieldmodule()
        fm.beginChange()
        coordinates = findOrCreateFieldCoordinates(fm)
        nodes = fm.findNodesetByFieldDomainType(Field.DOMAIN_TYPE_NODES)
        nodetemplate = nodes.createNodetemplate()
        nodetemplate.defineField(coordinates)
        nodetemplate.setValueNumberOfVersions(coordinates, -1, Node.VALUE_LABEL_VALUE, 1)
        nodetemplate.setValueNumberOfVersions(coordinates, -1, Node.VALUE_LABEL_D_DS1, 1)
        nodetemplate.setValueNumberOfVersions(coordinates, -1, Node.VALUE_LABEL_D_DS2, 1)
        if useCrossDerivatives:
            nodetemplate.setValueNumberOfVersions(coordinates, -1, Node.VALUE_LABEL_D2_DS1DS2, 1)

        mesh = fm.findMeshByDimension(2)
        bicubichermite = fm.createElementbasis(2, Elementbasis.FUNCTION_TYPE_CUBIC_HERMITE)
        eft = mesh.createElementfieldtemplate(bicubichermite)
        if not useCrossDerivatives:
            for n in range(4):
                eft.setFunctionNumberOfTerms(n*4 + 4, 0)

        elementtemplate = mesh.createElementtemplate()
        elementtemplate.setElementShapeType(Element.SHAPE_TYPE_SQUARE)
        elementtemplate.defineField(coordinates, -1, eft)

        cache = fm.createFieldcache()

        #create nodes
        nodeIdentifier = 1
        x = [0.0, 0.0, 0.0]
        dx_ds1 = [0.0, 0.0, 0.0]
        dx_ds2 = [0.0, 0.0, 0.0]
        zero = [0.0, 0.0, 0.0]

        x = [0, 0.5, 0]
        dx_ds1 = [0.5, 0.5, 0.0]
        dx_ds2 = [-0.5, 0.5, 0.0]
        node = nodes.createNode(nodeIdentifier, nodetemplate)
        cache.setNode(node)
        coordinates.setNodeParameters(cache, -1, node.VALUE_LABEL_VALUE, 1, x)
        coordinates.setNodeParameters(cache, -1, node.VALUE_LABEL_D_DS1, 1, dx_ds1)
        coordinates.setNodeParameters(cache, -1, node.VALUE_LABEL_D_DS2, 1, dx_ds2)
        nodeIdentifier = nodeIdentifier + 1

        x = [0.5, -0.5, 0]
        dx_ds1 = [0.5, 0.5, 0.0]
        dx_ds2 = [0.5, -0.5, 0.0]
        node = nodes.createNode(nodeIdentifier, nodetemplate)
        cache.setNode(node)
        coordinates.setNodeParameters(cache, -1, node.VALUE_LABEL_VALUE, 1, x)
        coordinates.setNodeParameters(cache, -1, node.VALUE_LABEL_D_DS1, 1, dx_ds1)
        coordinates.setNodeParameters(cache, -1, node.VALUE_LABEL_D_DS2, 1, dx_ds2)
        nodeIdentifier = nodeIdentifier + 1

        x = [0, -0.25, 0]
        dx_ds1 = [-0.5, -0.5, 0.0]
        dx_ds2 = [0.5, -0.5, 0.0]
        node = nodes.createNode(nodeIdentifier, nodetemplate)
        cache.setNode(node)
        coordinates.setNodeParameters(cache, -1, node.VALUE_LABEL_VALUE, 1, x)
        coordinates.setNodeParameters(cache, -1, node.VALUE_LABEL_D_DS1, 1, dx_ds1)
        coordinates.setNodeParameters(cache, -1, node.VALUE_LABEL_D_DS2, 1, dx_ds2)
        nodeIdentifier = nodeIdentifier + 1

        x = [-0.5, -0.5, 0]
        dx_ds1 = [-0.0, -0.5, 0.0]
        dx_ds2 = [0.5, -0.0, 0.0]
        node = nodes.createNode(nodeIdentifier, nodetemplate)
        cache.setNode(node)
        coordinates.setNodeParameters(cache, -1, node.VALUE_LABEL_VALUE, 1, x)
        coordinates.setNodeParameters(cache, -1, node.VALUE_LABEL_D_DS1, 1, dx_ds1)
        coordinates.setNodeParameters(cache, -1, node.VALUE_LABEL_D_DS2, 1, dx_ds2)

        # create element
        elementIdentifier = 1
        element = mesh.createElement(elementIdentifier, elementtemplate)
        nodeIdentifiers = [1, 2, 4, 3]
        result = element.setNodesByIdentifier(eft, nodeIdentifiers)

        fm.endChange()
        return []