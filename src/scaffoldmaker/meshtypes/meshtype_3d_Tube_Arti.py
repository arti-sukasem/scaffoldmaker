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
            'Inner radius': 0.5,
            'Outer radius': 1.0,
            'Number of element around': 4,
            'Number of element along': 2,
            'Number of element outward': 1,
            'Use cross derivatives': False,
            'Refine': False,
            'Refine Element around': 1,
            'Refine Element along': 1,
            'Refine Element outward': 1,
        }

    @staticmethod
    def getOrderedOptionNames():
        return [
            'Inner radius',
            'Outer radius',
            'Number of element around',
            'Number of element along',
            'Number of element outward',
            'Use cross derivatives',
            'Refine',
            'Refine Element around',
            'Refine Element along',
            'Refine Element outward'
        ]

    @staticmethod
    def checkOptions(options):
        if (options['Inner radius'] < 0.0):
            options['Inner radius'] = 0.5
        if (options['Outer radius'] < 0.0):
            options['Outer radius'] = 1.0
        if (options['Inner radius'] > options['Outer radius']):
            temp = options['Inner radius']
            options['Inner radius'] = options['Outer radius']
            options['Outer radius'] = temp
        if (options['Number of element around'] < 1):
            options['Number of element around'] = 1
        if (options['Number of element along'] < 1):
            options['Number of element along'] = 1
        if (options['Number of element outward'] < 1):
            options['Number of element outward'] = 1
        if (options['Refine Element around'] < 1):
            options['Refine Element around'] = 1
        if (options['Refine Element along'] < 1):
            options['Refine Element along'] = 1
        if (options['Refine Element outward'] < 1):
            options['Refine Element outward'] = 1
    @classmethod
    def generateBaseMesh(cls, region, options):
        """
        :param region: Zinc region to define model in. Must be empty.
        :param options: Dict containing options. See getDefaultOptions().
        :return: [] empty list of AnnotationGroup
        """
        innerRadius = options['Inner radius']
        outerRadius = options['Outer radius']
        elementsCountAround = options['Number of element around']
        elementsCountAlong = options['Number of element along']
        elementsCountOut = options['Number of element outward']
        useCrossDerivatives = options['Use cross derivatives']

        fm = region.getFieldmodule()
        fm. beginChange()
        coordinates = findOrCreateFieldCoordinates(fm)
        nodes = fm.findNodesetByFieldDomainType(Field.DOMAIN_TYPE_NODES)
        nodetemplate = nodes.createNodetemplate()
        nodetemplate.defineField(coordinates)
        nodetemplate.setValueNumberOfVersions(coordinates, -1, Node.VALUE_LABEL_VALUE, 1)
        nodetemplate.setValueNumberOfVersions(coordinates, -1, Node.VALUE_LABEL_D_DS1, 1)
        nodetemplate.setValueNumberOfVersions(coordinates, -1, Node.VALUE_LABEL_D_DS2, 1)
        nodetemplate.setValueNumberOfVersions(coordinates, -1, Node.VALUE_LABEL_D_DS3, 1)

        if useCrossDerivatives:
            nodetemplate.setValueNumberOfVersions(coordinates, -1, Node.VALUE_LABEL_D2_DS1DS2, 1)
            nodetemplate.setValueNumberOfVersions(coordinates, -1, Node.VALUE_LABEL_D2_DS1DS3, 1)
            nodetemplate.setValueNumberOfVersions(coordinates, -1, Node.VALUE_LABEL_D2_DS2DS3, 1)
            nodetemplate.setValueNumberOfVersions(coordinates, -1, Node.VALUE_LABEL_D3_DS1DS2DS3, 1)

        mesh = fm.findMeshByDimension(3)
        tricubichermite = eftfactory_tricubichermite(mesh, useCrossDerivatives)
        eft = tricubichermite.createEftBasic()
        elementtemplate = mesh.createElementtemplate()
        elementtemplate.setElementShapeType(Element.SHAPE_TYPE_CUBE)
        elementtemplate.defineField(coordinates, -1, eft)

        cache = fm.createFieldcache()

        #create node
        nodeIdentifier = 1
        x = [0.0, 0.0, 0.0]
        x1 = [0.0, 0.0, 0.0]
        dx_ds1 = [0.0, 0.0, 0.0]
        dx_ds2 = [0.0, 0.0, 0.0]
        dx_ds3 = [0.0, 0.0, 1.0/elementsCountAlong]
        dx1_ds1 = [0.0, 0.0, 0.0]
        dx1_ds2 = [0.0, 0.0, 0.0]
        dx1_ds3 = [0.0, 0.0, 1.0 / elementsCountAlong]
        zero = [0.0, 0.0, 0.0]
        radian = 2*math.pi/elementsCountAround

        for n3 in range(elementsCountAlong):
            incrementRadius = 0
            for n2 in range(elementsCountOut+1):
                radius = innerRadius + n2*incrementRadius
                for n1 in range(elementsCountAround):
                    x[0] = radius * math.cos(radian*n1)
                    x[1] = radius * math.sin(radian*n1)
                    x[2] = n3/elementsCountAlong

                    dx_ds1[0] = radius * -radian * math.sin(radian * n1)
                    dx_ds2[1] = radius * radian * math.cos(radian * n1)

                    node = nodes.createNode(nodeIdentifier, nodetemplate)
                    cache.setNode(node)

                    coordinates.setNodeParameters(cache, -1, node.VALUE_LABEL_VALUE, 1, x)
                    coordinates.setNodeParameters(cache, -1, node.VALUE_LABEL_D_DS1, 1, dx_ds1)
                    coordinates.setNodeParameters(cache, -1, node.VALUE_LABEL_D_DS2, 1, dx_ds2)
                    coordinates.setNodeParameters(cache, -1, node.VALUE_LABEL_D_DS3, 1, dx_ds3)

                    if useCrossDerivatives:
                        coordinates.setNodeParameters(cache, -1, node.VALUE_LABEL_D2_DS1DS2, 1, zero)
                        coordinates.setNodeParameters(cache, -1, node.VALUE_LABEL_D2_DS1DS3, 1, zero)
                        coordinates.setNodeParameters(cache, -1, node.VALUE_LABEL_D2_DS2DS3, 1, zero)
                        coordinates.setNodeParameters(cache, -1, node.VALUE_LABEL_D3_DS1DS2DS3, 1, zero)

                    nodeIdentifier = nodeIdentifier + 1

                incrementRadius = (outerRadius - innerRadius) / elementsCountOut

        #create element
        elementIdentifier = 1
        now = elementsCountAround * (elementsCountOut + 1)
        for e3 in range(elementsCountAlong-1):
            for e2 in range(elementsCountOut):
                for e1 in range(elementsCountAround):
                    element = mesh.createElement(elementIdentifier, elementtemplate)
                    bn1 = e3 * now + e2 * elementsCountAround + e1 + 1
                    bn2 = e3 * now + bn1 % elementsCountAround + e2 * elementsCountAround + 1
                    bn3 = bn1 + elementsCountAround
                    bn4 = bn2 + elementsCountAround
                    bn5 = bn1 + elementsCountAround*(elementsCountOut+1)
                    bn6 = bn4 + elementsCountAround*elementsCountOut
                    bn7 = bn5 + elementsCountAround
                    bn8 = bn6 + elementsCountAround
                    nodeIdentifiers = [bn1, bn2, bn3, bn4, bn5, bn6, bn7, bn8]
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
        refineElementsCount2 = options['Refine Element outward']
        refineElementsCount3 = options['Refine Element along']

        meshrefinement.refineAllElementsCubeStandard3d(refineElementsCount1, refineElementsCount2,
                                                       refineElementsCount3)