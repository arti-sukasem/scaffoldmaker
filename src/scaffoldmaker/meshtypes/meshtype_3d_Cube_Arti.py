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

class MeshType_3d_Cube_Arti(Scaffold_base):
    '''
    classdocs
    '''
    @staticmethod
    def getName():
        return '3D Cube Arti'

    @staticmethod
    def getDefaultOptions(parameterSetName='Default'):
        return {
            'Number of elements 1' : 1,
            'Number of elements 2' : 1,
            'Number of elements 3': 1,
            'Wedge 1': False,
            'Wedge 2': False,
            'Use cross derivatives' : False,
            'Refine': False,
            'Refine Element 1': 1,
            'Refine Element 2': 1,
            'Refine Element 3': 1,

        }

    @staticmethod
    def getOrderedOptionNames():
        return [
            'Number of elements 1',
            'Number of elements 2',
            'Number of elements 3',
            'Wedge 1',
            'Wedge 2',
            'Use cross derivatives',
            'Refine',
            'Refine Element 1',
            'Refine Element 2',
            'Refine Element 3',
        ]

    @staticmethod
    def checkOptions(options):
        if (options['Number of elements 1'] < 1) :
            options['Number of elements 1'] = 1
        if (options['Number of elements 2'] < 1) :
            options['Number of elements 2'] = 1
        if (options['Number of elements 3'] < 1) :
            options['Number of elements 3'] = 1
        if (options['Refine Element 1'] < 1) :
            options['Refine Element 1'] = 1
        if (options['Refine Element 2'] < 1) :
            options['Refine Element 2'] = 1
        if (options['Refine Element 3'] < 1) :
            options['Refine Element 3'] = 1

    @classmethod
    def generateBaseMesh(cls, region, options):
        """
        :param region: Zinc region to define model in. Must be empty.
        :param options: Dict containing options. See getDefaultOptions().
        :return: [] empty list of AnnotationGroup
        """

        elementsCount1 = options['Number of elements 1']
        elementsCount2 = options['Number of elements 2']
        elementsCount3 = options['Number of elements 3']
        createWedge1 = options['Wedge 1']
        createWedge2 = options['Wedge 2']
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
        nodetemplate.setValueNumberOfVersions(coordinates, -1, Node.VALUE_LABEL_D_DS3, 1)
        if useCrossDerivatives:
            nodetemplate.setValueNumberOfVersions(coordinates, -1, Node.VALUE_LABEL_D2_DS1DS2, 1)
            nodetemplate.setValueNumberOfVersions(coordinates, -1, Node.VALUE_LABEL_D2_DS1DS3, 1)
            nodetemplate.setValueNumberOfVersions(coordinates, -1, Node.VALUE_LABEL_D2_DS2DS3, 1)
            nodetemplate.setValueNumberOfVersions(coordinates, -1, Node.VALUE_LABEL_D3_DS1DS2DS3, 1)



        mesh = fm.findMeshByDimension(3)
        tricubichermite = eftfactory_tricubichermite(mesh, useCrossDerivatives)
        eft = tricubichermite.createEftBasic()
        if createWedge1:
            eft1 = tricubichermite.createEftWedgeXi1Zero()
            elementtemplate1 = mesh.createElementtemplate()
            elementtemplate1.setElementShapeType(Element.SHAPE_TYPE_CUBE)
            elementtemplate1.defineField(coordinates, -1, eft1)
        if createWedge2:
            eft2 = tricubichermite.createEftWedgeXi1One()
            elementtemplate2 = mesh.createElementtemplate()
            elementtemplate2.setElementShapeType(Element.SHAPE_TYPE_CUBE)
            elementtemplate2.defineField(coordinates, -1, eft2)

        elementtemplate = mesh.createElementtemplate()
        elementtemplate.setElementShapeType(Element.SHAPE_TYPE_CUBE)
        elementtemplate.defineField(coordinates, -1, eft)

        cache = fm.createFieldcache()

        #create nodes
        nodeIdentifier = 1
        x = [0.0, 0.0, 0.0]
        dx_ds1 = [1.0/elementsCount1, 0.0, 0.0]
        dx_ds2 = [0.0, 1.0/elementsCount2, 0.0]
        dx_ds3 = [0.0, 0.0, 1.0/elementsCount3]
        zero = [0.0, 0.0, 0.0]
        for n3 in range(elementsCount3+1):
            x[2] = n3/elementsCount3
            for n2 in range(elementsCount2+1):
                x[1] = n2/elementsCount2
                for n1 in range(elementsCount1+1):
                    x[0] = n1/elementsCount1
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
                    if createWedge1:
                        coordinates.setNodeParameters(cache, -1, node.VALUE_LABEL_VALUE, 1, x)
                        coordinates.setNodeParameters(cache, -1, node.VALUE_LABEL_D_DS1, 1, dx_ds1)
                        coordinates.setNodeParameters(cache, -1, node.VALUE_LABEL_D_DS2, 1, dx_ds2)
                        coordinates.setNodeParameters(cache, -1, node.VALUE_LABEL_D_DS3, 1, zero)
                    if createWedge2:
                        coordinates.setNodeParameters(cache, -1, node.VALUE_LABEL_VALUE, 1, x)
                        coordinates.setNodeParameters(cache, -1, node.VALUE_LABEL_D_DS1, 1, dx_ds1)
                        coordinates.setNodeParameters(cache, -1, node.VALUE_LABEL_D_DS2, 1, dx_ds2)
                        coordinates.setNodeParameters(cache, -1, node.VALUE_LABEL_D_DS3, 1, zero)

                    nodeIdentifier = nodeIdentifier + 1

        #create element
        elementIdentifier = 1
        no2 = elementsCount1 + 1
        no3 = (elementsCount2 + 1) * no2
        for e3 in range(elementsCount3):
            for e2 in range(elementsCount2):
                for e1 in range(elementsCount1):
                    if createWedge1 == True and e1<1 and e3 == elementsCount3-1:
                        element1 = mesh.createElement(elementIdentifier, elementtemplate1)
                        bni = e3 * no3 + e2 * no2 + e1 + 1
                        nodeIdentifiers = [bni, bni + 1, bni + no2, bni + no2 + 1,
                                            bni + no3 + 1, bni + no2 + no3 + 1]
                        result = element1.setNodesByIdentifier(eft1, nodeIdentifiers)
                        print("elementidentifier: ", elementIdentifier, " || ", nodeIdentifiers)
                        elementIdentifier = elementIdentifier + 1
                    elif createWedge2 == True and e1 == elementsCount1-1 and e3 == elementsCount3-1:
                        element2 = mesh.createElement(elementIdentifier, elementtemplate2)
                        bni = e3 * no3 + e2 * no2 + e1 + 1
                        nodeIdentifiers = [bni, bni + 1, bni + no2, bni + no2 + 1,
                                           bni + no3, bni + no2 + no3]
                        result = element2.setNodesByIdentifier(eft2, nodeIdentifiers)
                        print("elementidentifier: ", elementIdentifier, " || ", nodeIdentifiers)
                        elementIdentifier = elementIdentifier + 1
                    else:
                        element = mesh.createElement(elementIdentifier, elementtemplate)
                        bni = e3 * no3 + e2 * no2 + e1 + 1
                        nodeIdentifiers = [bni, bni + 1, bni + no2, bni + no2 + 1,
                                           bni + no3, bni + no3 + 1, bni + no2 + no3, bni + no2 + no3 + 1]
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
        refineElementsCount1 = options['Refine Element 1']
        refineElementsCount2 = options['Refine Element 2']
        refineElementsCount3 = options['Refine Element 3']

        meshrefinement.refineAllElementsCubeStandard3d(refineElementsCount1, refineElementsCount2,
                                                       refineElementsCount3)