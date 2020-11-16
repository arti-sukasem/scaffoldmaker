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


class MeshType_3d_left_human_lung(Scaffold_base):
    '''
    classdocs
    '''

    @staticmethod
    def getName():
        return '3D Left Human Lung Arti'

    @staticmethod
    def getDefaultOptions(cls, parameterSetName='Default'):
        return {
            'Width': 0.25,
            'Length': 1.0,
            'Height': 1.0,
            'Radius factor': 0.5,
            'Number of element (base width)': 2,
            'Number of element (base length)': 4,
            'Number of element (height)': 3,
            'Use cross derivatives': False,
            'Refine': False,
            'Refine Element in Width': 1,
            'Refine Element in Length': 1,
            'Refine Element in Height': 1,
        }

    @staticmethod
    def getOrderedOptionNames():
        return [
            'Width',
            'Length',
            'Height',
            'Radius factor',
            'Number of element (base width)',
            'Number of element (base length)',
            'Number of element (height)',
            'Use cross derivatives',
            'Refine',
            'Refine Element in Width',
            'Refine Element in Length',
            'Refine Element in Height'
        ]

    @staticmethod
    def checkOptions(options):
        if (options['Width'] < 0):
            options['Width'] = 1.0
        if (options['Length'] < 0):
            options['Length'] = 1.0
        if (options['Height'] < 0):
            options['Height'] = 1.0
        if (options['Radius factor'] < 0):
            options['Radius factor'] = 1.0
        if (options['Number of element (base width)'] < 2):
            options['Number of element (base width)'] = 2
        if (options['Number of element (base length)'] < 4):
            options['Number of element (base length)'] = 4
        if (options['Number of element (height)'] < 3):
            options['Number of element (height)'] = 3

    @classmethod
    def generateBaseMesh(cls, region, options):
        """
        :param region: Zinc region to define model in. Must be empty.
        :param options: Dict containing options. See getDefaultOptions().
        :return: [] empty list of AnnotationGroup
        """
        width = options['Width']
        length = options['Length']
        height = options['Height']
        rfactor = options['Radius factor']
        elementsCountAlong = options['Number of element (base length)']
        elementsCountIn = options['Number of element (base width)']
        elementsCountUp = options['Number of element (height)']
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
        elementtemplate = mesh.createElementtemplate()
        elementtemplate.setElementShapeType(Element.SHAPE_TYPE_CUBE)
        elementtemplate.defineField(coordinates, -1, eft)

        cache = fm.createFieldcache()

        #create nodes
        nodeIdentifier = 1
        x = [0.0, 0.0, 0.0]
        dx_ds1 = [0.0, 0.0, 0.0]
        dx_ds2 = [0.0, 0.0, 0.0]
        dx_ds3 = [0.0, 0.0, 0.0]
        zero = [0.0, 0.0, 0.0]
        stepLength = length/elementsCountAlong
        stepWidth = width/elementsCountIn
        stepHeight = height/(elementsCountUp)
        #update the loop
        update = 0

        for n3 in range(elementsCountUp+1):
            x[2] = n3 * stepHeight
            for n2 in range(elementsCountIn+1):
                x[1] = n2 * stepWidth
                for n1 in range(elementsCountAlong+1):
                    # need to find a better way to do this in the future (if and elif)
                    if (n1 == 0 or n1 == elementsCountAlong - update) and (n2 == 0 or n2 == elementsCountIn) and (n3 <1):
                        continue
                    elif (n1 == elementsCountAlong - update and (n2 ==0 or n2 == elementsCountIn)):
                        continue
                    else:
                        # extra nodes for triangle element in the middle without affecting other nodes
                        # at (n1 + 1/2, n2, n3)
                        if n1 == 1 and n3 == 1:
                            x[0] = (0.5 * n3 * stepLength + n1 * stepLength)

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

                            print("node: ", nodeIdentifier, "||", x)
                            print("n1: ", n1)
                            print("n2: ", n2)
                            print("n3: ", n3)
                            nodeIdentifier = nodeIdentifier + 1

                        if n1 == 0 and n2 == 0 and n3 == 2:
                            # at (n1, n2, n3 + 1/2)
                            x[0] = (n3 * stepLength + n1 * stepLength)
                            x[2] = n3 * stepHeight - stepHeight / 2
                            for n12 in range(elementsCountIn+1):
                                x[1] = n12 * stepWidth
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

                                print("node: ", nodeIdentifier, "||", x)
                                print("n1: ", n1)
                                print("n2: ", n2)
                                print("n3: ", n3)
                                nodeIdentifier = nodeIdentifier + 1

                        x[0] = (n3 * stepLength + n1 * stepLength)

                        if n1 == elementsCountAlong - update and n3 > 1:
                            # moving nodes (n1 = last, n2 = last two, + 1/2 stepheight)
                            x[2] = x[2] + stepHeight*0.5

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

                            print('check node :', nodeIdentifier)
                            print('update:', update)
                            nodeIdentifier = nodeIdentifier + 1

                            continue

                        x[1] = n2 * stepWidth
                        x[2] = n3 * stepHeight

                        if x[0] <= length:
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

                            print("node: ", nodeIdentifier, "||", x)
                            print("n1: ", n1)
                            print("n2: ", n2)
                            print("n3: ", n3)
                            nodeIdentifier = nodeIdentifier + 1
            update += 1


        #create element
        elementIdentifier = 1


        fm.endChange()
        return []