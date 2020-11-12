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
            'Width': 0.25,
            'Length': 1.0,
            'Height': 1.0,
            'Radius factor': 0.5,
            'Number of element (base width)': 2,
            'Number of element (base length)': 4,
            # 'Number of element (height)': 4,
            'Use cross derivatives': False,
            'Cut from the corner': False,
            'Complete': False,
            'Depth': 0,
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
            # 'Number of element (height)',
            'Use cross derivatives',
            'Cut from the corner',
            'Complete',
            'Depth',
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
        if (options['Number of element (base width)'] < 1):
            options['Number of element (base width)'] = 1
        if (options['Number of element (base length)'] < 1):
            options['Number of element (base length)'] = 1
        if (options['Depth'] < 0):
            options['Depth'] = 0
        # if (options['Number of element (base height)'] < 1):
        #     options['Number of element (base height)'] = 1

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
        useCrossDerivatives = options['Use cross derivatives']
        cutAngle = options['Cut from the corner']
        cutGradient = options['Depth']
        complete = options['Complete']

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
        if cutAngle != True:
            nodeIdentifier = 1
            x = [0.0, 0.0, 0.0]
            dx_ds1 = [0.0, 0.0, 0.0]
            dx_ds2 = [0.0, 0.0, 0.0]
            dx_ds3 = [0.0, 0.0, 0.0]
            zero = [0.0, 0.0, 0.0]
            bodyLength = length - width
            stepLength = length/elementsCountAlong
            stepWidth = width/elementsCountIn
            # since #elements in height is proportional to #elements in length
            stepHeight = height/elementsCountAlong

            for n3 in range(elementsCountAlong+2):
                x[2] = n3 * stepHeight
                for n2 in range(elementsCountIn+1):
                    x[1] = n2 * stepWidth
                    for n1 in range(elementsCountAlong+1):
                        x[0] = (n3 * stepLength + n1 * stepLength)

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

                            nodeIdentifier = nodeIdentifier + 1

                    if n2 > 0 and n2 < elementsCountIn:
                        yCircle = (width / 2) - x[1]
                        xCircle = math.sqrt((width/2)**2 - yCircle**2)

                        x[0] = rfactor * xCircle + length
                        print("n2: ", n2)
                        print("bodylength: ", bodyLength)
                        print("node: ", nodeIdentifier, "||", x)
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
        else:
            nodeIdentifier = 1
            x = [0.0, 0.0, 0.0]
            dx_ds1 = [0.0, 0.0, 0.0]
            dx_ds2 = [0.0, 0.0, 0.0]
            dx_ds3 = [0.0, 0.0, 0.0]
            zero = [0.0, 0.0, 0.0]
            bodyLength = length - width
            stepLength = length / elementsCountAlong
            stepWidth = width / elementsCountIn
            # since #elements in height is proportional to #elements in length
            stepHeight = height / elementsCountAlong

            n3 =0
            count = 0

            while count != 2:
                count = 0
                x[2] = n3 * stepHeight
                for n2 in range(elementsCountIn + 1):
                    x[1] = n2 * stepWidth
                    for n1 in range(elementsCountAlong + 1):
                        if n3 + cutGradient <= n2 + n1:
                            x[0] = n1 * stepLength
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

                                # print("node: ", nodeIdentifier, "||", x)
                                count = count + 1
                                nodeIdentifier = nodeIdentifier + 1

                    if n2 > 0 and n2 < elementsCountIn and n3 + cutGradient <= n2 + n1 +1:
                        yCircle = (width / 2) - x[1]
                        xCircle = math.sqrt((width / 2) ** 2 - yCircle ** 2)

                        x[0] = rfactor * xCircle + length
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

                        # print("node: ", nodeIdentifier, "||", x)
                        count = count + 1
                        nodeIdentifier = nodeIdentifier + 1

                print("n3: ", n3)
                print("count: ", count)


                n3 += 1



        #create element
        elementIdentifier = 1


        fm.endChange()
        return []