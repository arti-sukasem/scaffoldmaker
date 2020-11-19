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
    3D lung scaffold for human
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
            'Number of element 2': 4,
            'Number of element 1': 2,
            'Number of element 3': 3,
            'Use cross derivatives': False,
            'Refine': False,
            'Refine Element 1': 1,
            'Refine Element 2': 1,
            'Refine Element 3': 1,
        }

    @staticmethod
    def getOrderedOptionNames():
        return [
            'Width',
            'Length',
            'Height',
            'Number of element 1',
            'Number of element 2',
            'Number of element 3',
            'Use cross derivatives',
            'Refine',
            'Refine Element 1',
            'Refine Element 2',
            'Refine Element 3'
        ]

    @staticmethod
    def checkOptions(options):
        for key in ['Width', 'Length', 'Height', 'Refine Element 1', 'Refine Element 2', 'Refine Element 3']:
            if options[key] < 1:
                options[key] = 1

        if (options['Number of element 2'] < 4):
            options['Number of element 2'] = 4
        if (options['Number of element 1'] < 2):
            options['Number of element 1'] = 2
        if (options['Number of element 3'] < 3):
            options['Number of element 3'] = 3

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
        elementsCount1 = options['Number of element 1']
        elementsCount2 = options['Number of element 2']
        elementsCount3 = options['Number of element 3']
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

        cache = fm.createFieldcache()

        #create nodes
        nodeIdentifier = 1
        x = [0.0, 0.0, 0.0]
        dx_ds1 = [0.0, 0.0, 0.0]
        dx_ds2 = [0.0, 0.0, 0.0]
        dx_ds3 = [0.0, 0.0, 0.0]
        zero = [0.0, 0.0, 0.0]
        stepLength = length/elementsCount1
        stepWidth = width/elementsCount2
        stepHeight = height/elementsCount3
        lNodeIds = []   # Node index list
        update = 0  # Update the loop to eliminate for the slope


        for n3 in range(elementsCount3+1):
            lNodeIds.append([])
            x[2] = n3 * stepHeight
            for n2 in range(elementsCount2+1):
                lNodeIds[n3].append([])
                x[1] = n2 * stepWidth
                for n1 in range(elementsCount1+1):
                    lNodeIds[n3][n2].append(None)

                    if (n1 == 0 or n1 == elementsCount1) and (n2 == 0 or n2 == elementsCount2):
                        continue
                    elif (n2 > elementsCount2-update):
                        continue

                    # extra nodes for triangle element in the middle without affecting other nodes
                    # at (n1 + 1/2, n2, n3)
                    if n2 == elementsCount2-1 and n3 == 1 and n1 == 0:
                        x[1] = n2*stepWidth - stepWidth/2
                        for n12 in range(elementsCount1+1):
                            x[0] = n12 * stepLength

                            node = nodes.createNode(nodeIdentifier, nodetemplate)
                            cache.setNode(node)
                            coordinates.setNodeParameters(cache, -1, node.VALUE_LABEL_VALUE, 1, x)
                            coordinates.setNodeParameters(cache, -1, node.VALUE_LABEL_D_DS1, 1, dx_ds1)
                            coordinates.setNodeParameters(cache, -1, node.VALUE_LABEL_D_DS2, 1, dx_ds2)
                            coordinates.setNodeParameters(cache, -1, node.VALUE_LABEL_D_DS3, 1, dx_ds3)

                            # if useCrossDerivatives:
                            #     coordinates.setNodeParameters(cache, -1, node.VALUE_LABEL_D2_DS1DS2, 1, zero)
                            #     coordinates.setNodeParameters(cache, -1, node.VALUE_LABEL_D2_DS1DS3, 1, zero)
                            #     coordinates.setNodeParameters(cache, -1, node.VALUE_LABEL_D2_DS2DS3, 1, zero)
                            #     coordinates.setNodeParameters(cache, -1, node.VALUE_LABEL_D3_DS1DS2DS3, 1, zero)

                            # print("condition: n2 == elementsCount2-1 and n3 == 1 and n1 == 0")
                            # print("node: ", nodeIdentifier, "||", x)
                            # print("n1: ", n12)
                            # print("n2: ", n2)
                            # print("n3: ", n3)

                            lNodeIds[n3][n2][n12] = nodeIdentifier
                            lNodeIds[n3][n2].append(None)

                            nodeIdentifier += 1

                        lNodeIds[n3].append([])
                        # continue the row after
                        for n13 in range(elementsCount1 + 1):
                            lNodeIds[n3][n2+1].append(None)
                            x[0] = n13 * stepLength
                            x[1] = n2 * stepWidth
                            node = nodes.createNode(nodeIdentifier, nodetemplate)
                            cache.setNode(node)
                            coordinates.setNodeParameters(cache, -1, node.VALUE_LABEL_VALUE, 1, x)
                            coordinates.setNodeParameters(cache, -1, node.VALUE_LABEL_D_DS1, 1, dx_ds1)
                            coordinates.setNodeParameters(cache, -1, node.VALUE_LABEL_D_DS2, 1, dx_ds2)
                            coordinates.setNodeParameters(cache, -1, node.VALUE_LABEL_D_DS3, 1, dx_ds3)

                            # print("condition: n2 == elementsCount2-1 and n3 == 1 and n1 == 0")
                            # print("node: ", nodeIdentifier, "||", x)
                            # print("n1: ", n1)
                            # print("n2: ", n2+1)
                            # print("n3: ", n3)
                            lNodeIds[n3][n2+1][n13] = nodeIdentifier
                            nodeIdentifier += 1

                        nodeIdentifier += elementsCount1 + 1


                        # print("break")
                        break

                    x[0] = n1 * stepLength
                    x[1] = n2 * stepWidth
                    x[2] = n3 * stepHeight

                    # moving nodes (n1 = last, n2 = last two, + 1/2 stepheight)
                    if (n1 > 0 or n1 < elementsCount1) and n2 == 0 and (n3 > 1):

                        x[2] = n3 * stepHeight + stepHeight / 2

                        node = nodes.createNode(nodeIdentifier, nodetemplate)
                        cache.setNode(node)
                        coordinates.setNodeParameters(cache, -1, node.VALUE_LABEL_VALUE, 1, x)
                        coordinates.setNodeParameters(cache, -1, node.VALUE_LABEL_D_DS1, 1, dx_ds1)
                        coordinates.setNodeParameters(cache, -1, node.VALUE_LABEL_D_DS2, 1, dx_ds2)
                        coordinates.setNodeParameters(cache, -1, node.VALUE_LABEL_D_DS3, 1, dx_ds3)

                        # if useCrossDerivatives:
                        #     coordinates.setNodeParameters(cache, -1, node.VALUE_LABEL_D2_DS1DS2, 1, zero)
                        #     coordinates.setNodeParameters(cache, -1, node.VALUE_LABEL_D2_DS1DS3, 1, zero)
                        #     coordinates.setNodeParameters(cache, -1, node.VALUE_LABEL_D2_DS2DS3, 1, zero)
                        #     coordinates.setNodeParameters(cache, -1, node.VALUE_LABEL_D3_DS1DS2DS3, 1, zero)
                        #

                        # print("if (n1 > 0 or n1 < elementsCount1) and n2 == 0 and (n3 > elementsCount3 - 2)")
                        # print("node: ", nodeIdentifier, "||", x)
                        # print("n1: ", n1)
                        # print("n2: ", n2)
                        # print("n3: ", n3)

                        lNodeIds[n3][n2][n1] = nodeIdentifier
                        nodeIdentifier += 1
                        continue

                    if x[0] <= width:
                        node = nodes.createNode(nodeIdentifier, nodetemplate)
                        cache.setNode(node)

                        coordinates.setNodeParameters(cache, -1, node.VALUE_LABEL_VALUE, 1, x)
                        coordinates.setNodeParameters(cache, -1, node.VALUE_LABEL_D_DS1, 1, dx_ds1)
                        coordinates.setNodeParameters(cache, -1, node.VALUE_LABEL_D_DS2, 1, dx_ds2)
                        coordinates.setNodeParameters(cache, -1, node.VALUE_LABEL_D_DS3, 1, dx_ds3)

                        # if useCrossDerivatives:
                        #     coordinates.setNodeParameters(cache, -1, node.VALUE_LABEL_D2_DS1DS2, 1, zero)
                        #     coordinates.setNodeParameters(cache, -1, node.VALUE_LABEL_D2_DS1DS3, 1, zero)
                        #     coordinates.setNodeParameters(cache, -1, node.VALUE_LABEL_D2_DS2DS3, 1, zero)
                        #     coordinates.setNodeParameters(cache, -1, node.VALUE_LABEL_D3_DS1DS2DS3, 1, zero)
                        #

                        # print("condition: x[0] <= width")
                        # print("node: ", nodeIdentifier, "||", x)
                        # print("n1: ", n1)
                        # print("n2: ", n2)
                        # print("n3: ", n3)

                        lNodeIds[n3][n2][n1] = nodeIdentifier
                        nodeIdentifier += 1

                    # extra nodes for triangle element in the middle without affecting other nodes
                    # at (n1, n2, n3 + 1/2)
                    k = 0
                    if n1 == elementsCount1 and n2 == elementsCount2-update and n3 == 2:
                        lNodeIds[n3].append([])
                        lNodeIds[n3][n2 + 1] = lNodeIds[n3][n2][:]

                        nodeIdentifier_temp = nodeIdentifier - ((elementsCount1+1) * (n2+1)+1)
                        x[1] = (elementsCount2-2) * stepWidth
                        x[2] = n3 * stepHeight - 0.5 * stepHeight

                        for n12 in range(elementsCount1 + 1):

                            x[0] = n12 * stepLength
                            node = nodes.createNode(nodeIdentifier_temp, nodetemplate)
                            cache.setNode(node)

                            coordinates.setNodeParameters(cache, -1, node.VALUE_LABEL_VALUE, 1, x)
                            coordinates.setNodeParameters(cache, -1, node.VALUE_LABEL_D_DS1, 1, dx_ds1)
                            coordinates.setNodeParameters(cache, -1, node.VALUE_LABEL_D_DS2, 1, dx_ds2)
                            coordinates.setNodeParameters(cache, -1, node.VALUE_LABEL_D_DS3, 1, dx_ds3)

                            # if useCrossDerivatives:
                            #     coordinates.setNodeParameters(cache, -1, node.VALUE_LABEL_D2_DS1DS2, 1, zero)
                            #     coordinates.setNodeParameters(cache, -1, node.VALUE_LABEL_D2_DS1DS3, 1, zero)
                            #     coordinates.setNodeParameters(cache, -1, node.VALUE_LABEL_D2_DS2DS3, 1, zero)
                            #     coordinates.setNodeParameters(cache, -1, node.VALUE_LABEL_D3_DS1DS2DS3, 1, zero)


                            # print("if n1 == elementsCount1 and n2 == elementsCount2-update and n3 == 2")
                            # print("nodeIdentifier_temp: ", nodeIdentifier_temp, "||", x)
                            # print("n1: ", n12)
                            # print("n2: ", n2)
                            # print("n3: ", n3)
                            lNodeIds[n3][n2][n12] = nodeIdentifier_temp
                            nodeIdentifier_temp += 1

                        continue

            update += 1




        # ----------------------------------------------------------------------------------------
        #                                   Create element
        # ----------------------------------------------------------------------------------------

        mesh = fm.findMeshByDimension(3)
        eftfactory = eftfactory_tricubichermite(mesh, useCrossDerivatives)
        eftRegular = eftfactory.createEftBasic()

        elementtemplateRegular = mesh.createElementtemplate()
        elementtemplateRegular.setElementShapeType(Element.SHAPE_TYPE_CUBE)
        elementtemplateRegular.defineField(coordinates, -1, eftRegular)

        elementtemplateCustom = mesh.createElementtemplate()
        elementtemplateCustom.setElementShapeType(Element.SHAPE_TYPE_CUBE)

        eft1 = eftfactory.createEftWedgeCollapseXi1AtXi2Zero()
        eft2 = eftfactory.createEftWedgeCollapseXi1AtXi2One()
        eft3 = eftfactory.createEftWedgeCollapseXi2AtXi3One()
        # eft3 = eftfactory.createEftWedgeCollapseXi3AtXi2Zero()
        # eft4 = eftfactory.createEftWedgeCollapseXi3AtXi2One()
        # eft5 = eftfactory.createEftWedgeCollapseXi3AtXi1Zero()
        # eft6 = eftfactory.createEftWedgeCollapseXi2AtXi3One()

        elementIdentifier = 1
        for e3 in range(elementsCount3):
            for e2 in range(elementsCount2):
                for e1 in range(elementsCount1):
                    eft = eftRegular
                    if e2 == elementsCount2-2 and e3 == 1:
                        nodeIdentifiers = [lNodeIds[e3][e2][e1], lNodeIds[e3][e2][e1 + 1], lNodeIds[e3][e2 + 1][e1],
                                           lNodeIds[e3][e2 + 1][e1 + 1], lNodeIds[e3 + 1][e2][e1], lNodeIds[e3 + 1][e2][e1 + 1]]
                    elif e2 == elementsCount2-1 and e3 == 1:
                        nodeIdentifiers = [lNodeIds[e3][e2][e1], lNodeIds[e3][e2][e1 + 1], lNodeIds[e3][e2 + 1][e1],
                                           lNodeIds[e3][e2 + 1][e1 + 1],
                                           lNodeIds[e3 + 1][e2][e1], lNodeIds[e3 + 1][e2][e1 + 1],
                                           lNodeIds[e3 + 1][e2 - 1][e1], lNodeIds[e3 + 1][e2 - 1][e1 + 1]]
                    elif e2 == elementsCount2 - update + 1 and e3 == elementsCount3-1:
                        nodeIdentifiers = [lNodeIds[e3][e2][e1], lNodeIds[e3][e2][e1 + 1], lNodeIds[e3][e2 + 1][e1],
                                           lNodeIds[e3][e2 + 1][e1 + 1],
                                           lNodeIds[e3 + 1][e2][e1], lNodeIds[e3 + 1][e2][e1 + 1],
                                           lNodeIds[e3][e2 + 2][e1], lNodeIds[e3][e2 + 2][e1 + 1]]
                    else:
                        nodeIdentifiers = [lNodeIds[e3][e2][e1], lNodeIds[e3][e2][e1+1], lNodeIds[e3][e2 + 1][e1], lNodeIds[e3][e2+1][e1+1],
                            lNodeIds[e3+1][e2][e1], lNodeIds[e3+1][e2][e1+1], lNodeIds[e3+1][e2 + 1][e1], lNodeIds[e3+1][e2+1][e1+1]]
                    scalefactors = None

                    #Discard all the unused elements
                    if nodeIdentifiers.count(None) > 3:
                        continue

                    print("elementIdentifier: ", elementIdentifier, "|| NodeIdentifiers: ", nodeIdentifiers)


                    if (e3 < elementsCount3 - 1):
                        if (e2 == 0) and (e1 == 0):
                            # Back wedge elements
                            nodeIdentifiers.pop(4)
                            nodeIdentifiers.pop(0)
                            eft = eft1
                            scalefactors = [-1.0]
                        elif (e2 == (elementsCount2 - 1)) and (e1 == 0):
                            # Front wedge elements
                            nodeIdentifiers.pop(6)
                            nodeIdentifiers.pop(2)
                            eft = eft2
                    else:
                        if ((e2 == 0) or (e2 == elementsCount2 - 1)) and (e1 == 0):
                            # Top tetrahedron elements
                            continue
                        elif (e2 == 0) and (e1 == 1):
                            # Top back wedge elements
                            nodeIdentifiers.pop(4)
                            nodeIdentifiers.pop(3)
                            eft = eft3


                    if eft is eftRegular:
                        element = mesh.createElement(elementIdentifier, elementtemplateRegular)
                    else:
                        elementtemplateCustom.defineField(coordinates, -1, eft)
                        element = mesh.createElement(elementIdentifier, elementtemplateCustom)
                    element.setNodesByIdentifier(eft, nodeIdentifiers)
                    if scalefactors:
                        element.setScaleFactors(eft, scalefactors)

                    elementIdentifier += 1

        annotationGroups = []
        fm.endChange()
        return annotationGroups

    @classmethod
    def refineMesh(cls, meshrefinement, options):
        '''
        Refine source mesh into separate region, with change of basis.
        :param meshrefinement: MeshRefinement, which knows source and target region.
        :param options: Dict containing options. See getDefaultOptions().
        '''
        refineElementsCount1 = options['Refine Element 1']
        refineElementsCount2 = options['Refine Element 2']
        refineElementsCount3 = options['Refine Element 3']

        meshrefinement.refineAllElementsCubeStandard3d(refineElementsCount1, refineElementsCount2, refineElementsCount3)