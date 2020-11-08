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


class MeshType_2d_Tube_Arti(Scaffold_base):
    '''
    classdocs
    '''

    @staticmethod
    def getName():
        return '2D Tube Arti'

    @staticmethod
    def getDefaultOptions(cls, parameterSetName='Default'):
        return {
            'Circle radius': 0.5,
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
            'Circle radius',
            'Number of element around',
            'Number of element along',
            'Use cross derivatives',
            'Refine',
            'Refine Element around',
            'Refine Element along'
        ]

    @staticmethod
    def checkOptions(options):
        if (options['Circle radius'] < 0):
            options['Circle radius'] = 0.5
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
        radius = options['Circle radius']
        elementCountAround = options['Number of element around']
        elementCountAlong = options['Number of element along']
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

        # create nodes
        nodeIdentifier = 1
        radian = 2 * math.pi / elementCountAround
        x = [0.0, 0.0, 0.0]
        dx_ds1 = [0.0, 0.0, 0.0]
        dx_ds2 = [0.0, 0.0, 1/elementCountAlong]
        zero = [0.0, 0.0, 0.0]
        for n2 in range(elementCountAlong):
            x[2] = n2 / elementCountAlong
            for n1 in range(elementCountAround):
                x[0] = radius * math.cos(radian * n1)
                x[1] = radius * math.sin(radian * n1)
                dx_ds1[0] = radius * -math.sin(radian * n1)*radian
                dx_ds1[1] = radius * math.cos(radian * n1)*radian
                node = nodes.createNode(nodeIdentifier, nodetemplate)
                cache.setNode(node)
                coordinates.setNodeParameters(cache, -1, node.VALUE_LABEL_VALUE, 1, x)
                coordinates.setNodeParameters(cache, -1, node.VALUE_LABEL_D_DS1, 1, dx_ds1)
                coordinates.setNodeParameters(cache, -1, node.VALUE_LABEL_D_DS2, 1, dx_ds2)

                if useCrossDerivatives:
                    coordinates.setNodeParameters(cache, -1, node.VALUE_LABEL_D2_DS1DS2, 1, zero)
                print('node :', nodeIdentifier, 'coordinates: ', x)

                nodeIdentifier = nodeIdentifier + 1

        # create element
        elementIdentifier = 1
        bn2 = 0

        for e2 in range(elementCountAlong):
            for e1 in range(elementCountAround):
                element = mesh.createElement(elementIdentifier, elementtemplate)
                bn1 = e2*elementCountAround + e1 + 1
                bn2 = e2*elementCountAround + (e1+1)%elementCountAround + 1
                nodeIdentifiers = [bn1, bn2 , bn1+elementCountAround, bn2+elementCountAround]
                result = element.setNodesByIdentifier(eft, nodeIdentifiers)
                print("elementidentifier: ", elementIdentifier, " || ", nodeIdentifiers)
                elementIdentifier = elementIdentifier + 1
        fm.endChange()
        return []

    @classmethod
    def refineMesh(cls, meshrefinement, options):
        """
        Refine source mesh into separate region, with change of basis.
        :param meshrefinement: MeshRefinement, which knows source and target region.
        :param options: Dict containing options. See getDefaultOptions().
        """
        refineElementsCount1 = options['Refine Element around']
        refineElementsCount2 = options['Refine Element along']

        meshrefinement.refineAllElementsCubeStandard3d(refineElementsCount1, refineElementsCount2)