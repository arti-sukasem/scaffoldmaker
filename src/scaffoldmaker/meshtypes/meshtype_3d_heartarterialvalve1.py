"""
Generates a 3-D heart arterial valve (aortic/pulmonary) scaffold with
semilunar leaflet attachments.
Bicubic with linear through wall.
"""

from __future__ import division
import math
from opencmiss.utils.zinc.field import findOrCreateFieldCoordinates
from opencmiss.utils.zinc.finiteelement import getMaximumElementIdentifier, getMaximumNodeIdentifier
from opencmiss.utils.zinc.general import ChangeManager
from opencmiss.zinc.element import Element
from opencmiss.zinc.field import Field
from opencmiss.zinc.node import Node
from scaffoldmaker.meshtypes.scaffold_base import Scaffold_base
from scaffoldmaker.utils.geometry import createCirclePoints
from scaffoldmaker.utils.interpolation import interpolateLagrangeHermiteDerivative, smoothCubicHermiteDerivativesLine
from scaffoldmaker.utils.eftfactory_bicubichermitelinear import eftfactory_bicubichermitelinear
from scaffoldmaker.utils.eftfactory_tricubichermite import eftfactory_tricubichermite
from scaffoldmaker.utils.meshrefinement import MeshRefinement
from scaffoldmaker.utils import vector

class MeshType_3d_heartarterialvalve1(Scaffold_base):
    '''
    Generates a 3-D heart arterial valve scaffold with semilunar valve,
    for attaching to a 6-element-around bicubic-linear orifice.
    '''

    @staticmethod
    def getName():
        return '3D Heart Arterial Valve 1'

    @staticmethod
    def getDefaultOptions(parameterSetName='Default'):
        return {
            'Unit scale' : 1.0,
            'Centre height' : 0.5,
            'Inner diameter' : 1.0,
            'Inner height' : 0.7,
            'Inner radial displacement' : 0.05,
            'Outer angle degrees' : 0.0,
            'Outer height' : 0.5,
            'Outer radial displacement' : 0.1,
            'Outer sinus displacement' : 0.05,
            'Outlet length' : 0.4,
            'Sinus angle degrees' : 35.0,
            'Wall thickness' : 0.05,
            #'X rotation degrees' : 0.0,
            #'Y rotation degrees' : 0.0,
            #'Z rotation degrees' : 0.0,
            'Refine' : False,
            'Refine number of elements surface' : 4,
            'Refine number of elements through wall' : 1,
            'Use cross derivatives' : False
        }

    @staticmethod
    def getOrderedOptionNames():
        return [
            'Unit scale',
            'Centre height',
            'Inner diameter',
            'Inner height',
            'Inner radial displacement',
            'Outer angle degrees',
            'Outer height',
            'Outer radial displacement',
            'Outer sinus displacement',
            'Outlet length',
            'Sinus angle degrees',
            'Wall thickness',
            #'X rotation degrees',
            #'Y rotation degrees',
            #'Z rotation degrees',
            'Refine',
            'Refine number of elements surface',
            'Refine number of elements through wall'
        ]

    @staticmethod
    def checkOptions(options):
        '''
        :return:  True if dependent options changed, otherwise False.
        '''
        dependentChanges = False
        for key in [
            'Unit scale',
            'Centre height',
            'Inner diameter',
            'Inner height',
            'Inner radial displacement',
            'Outer height',
            'Outer radial displacement',
            'Outer sinus displacement',
            'Outlet length',
            'Wall thickness']:
            if options[key] < 0.0:
                options[key] = 0.0
        for key in [
            'Refine number of elements surface',
            'Refine number of elements through wall']:
            if options[key] < 1:
                options[key] = 1
        return dependentChanges

    @classmethod
    def getPoints(cls, options):
        """
        Get point coordinates and derivatives for the arterial valve ring.
        Optional extra parameters allow centre and axes to be set.
        :param options: Dict containing options. See getDefaultOptions().
        :return: x, d1, d2 all indexed by [n3=wall][n2=inlet->outlet][n1=around] where
        d1 is around, d2 is in direction inlet->outlet.
         """
        unitScale = options['Unit scale']
        centreHeight = unitScale*options['Centre height']
        innerRadius = unitScale*0.5*options['Inner diameter']
        innerHeight = unitScale*options['Inner height']
        innerRadialDisplacement = unitScale*options['Inner radial displacement']
        outerAngleRadians = math.radians(options['Outer angle degrees'])
        outerHeight = unitScale*options['Outer height']
        outerRadialDisplacement = unitScale*options['Outer radial displacement']
        outerSinusDisplacement = unitScale*options['Outer sinus displacement']
        outletLength = unitScale*options['Outlet length']
        sinusAngleRadians = math.radians(options['Sinus angle degrees'])
        wallThickness = unitScale*options['Wall thickness']
        outerRadius = innerRadius + wallThickness
        innerInletRadius = innerSinusRadius = innerRadius + innerRadialDisplacement

        elementsCountAround = 6  # fixed
        radiansPerElementAround = 2.0*math.pi/elementsCountAround
        pi_3 = radiansPerElementAround

        centre = [ 0.0, 0.0, 0.0 ]
        axis1 = [ 1.0, 0.0, 0.0 ]
        axis2 = [ 0.0, 1.0, 0.0 ]
        axis3 = vector.crossproduct3(axis1, axis2)

        x  = [ [ None, None ], [ None, None ] ]
        d1 = [ [ None, None ], [ None, None ] ]
        d2 = [ [ None, None ], [ None, None ] ]

        # inlet
        # inner layer, with sinuses
        outletz = innerHeight - centreHeight
        inletz  = outletz - outletLength
        sinusz  = -centreHeight
        outletCentre = [ (centre[c] + outletz*axis3[c]) for c in range(3) ]
        inletCentre  = [ (centre[c] +  inletz*axis3[c]) for c in range(3) ]
        sinusCentre  = [ (centre[c] +  sinusz*axis3[c]) for c in range(3) ]
        # calculate magnitude of d1, d2 at inner sinus
        leafd1mag = innerInletRadius*radiansPerElementAround  # was 0.5*
        leafd2r, leafd2z = interpolateLagrangeHermiteDerivative([ -innerRadialDisplacement, 0.0 ], [ 0.0, outletLength ], [ 0.0, outletLength ], 0.0)
        sinusd1mag = innerSinusRadius*radiansPerElementAround  # initial value only
        sinusd1mag = vector.magnitude(smoothCubicHermiteDerivativesLine(
            [ [ innerInletRadius, 0.0, inletz ], [ innerSinusRadius*math.cos(pi_3), innerSinusRadius*math.sin(pi_3), sinusz ] ],
            [ [ 0.0, leafd1mag, 0.0 ], [ -sinusd1mag*math.sin(pi_3), sinusd1mag*math.cos(pi_3), 0.0 ] ],
            fixStartDerivative = True, fixEndDirection = True)[1])
        sinusd2r, sinusd2z = smoothCubicHermiteDerivativesLine(
            [ [ innerSinusRadius , -centreHeight ], [ innerInletRadius, innerHeight - centreHeight ] ],
            [ [ outletLength*math.sin(sinusAngleRadians), outletLength*math.cos(sinusAngleRadians) ], [ 0.0, outletLength ] ],
            fixStartDirection = True, fixEndDerivative = True)[0]
        x [0][0] = []
        d1[0][0] = []
        d2[0][0] = []
        for n1 in range(elementsCountAround):
            radiansAround = n1*radiansPerElementAround
            cosRadiansAround = math.cos(radiansAround)
            sinRadiansAround = math.sin(radiansAround)
            if (n1 % 2) == 0:
                # leaflet junction
                cx = inletCentre
                r = innerInletRadius
                d1mag = leafd1mag
                d2mag1 = leafd2r*cosRadiansAround
                d2mag2 = leafd2r*sinRadiansAround
                d2mag3 = leafd2z
            else:
                # sinus / leaflet centre
                cx = sinusCentre
                r = innerSinusRadius
                d1mag = sinusd1mag
                d2mag1 = sinusd2r*cosRadiansAround
                d2mag2 = sinusd2r*sinRadiansAround
                d2mag3 = sinusd2z
            x [0][0].append([ (cx[c] + r*(cosRadiansAround*axis1[c] + sinRadiansAround*axis2[c])) for c in range(3) ])
            d1[0][0].append([ d1mag*(-sinRadiansAround*axis1[c] + cosRadiansAround*axis2[c]) for c in range(3) ])
            d2[0][0].append([ (d2mag1*axis1[c] + d2mag2*axis2[c] + d2mag3*axis3[c]) for c in range(3) ])
        # outer layer
        extz = innerHeight - centreHeight - outerHeight
        extRadius = outerRadius + outerRadialDisplacement
        leafd2r, leafd2z = smoothCubicHermiteDerivativesLine(
            [ [ extRadius , 0.0 ], [ outerRadius, outerHeight ] ],
            [ [ -outerHeight*math.sin(outerAngleRadians), outerHeight*math.cos(outerAngleRadians) ], [ 0.0, outletLength ] ],
            fixStartDirection = True, fixEndDerivative = True)[0]
        # calculate magnitude of d1, d2 at outer sinus
        extSinusRadius = extRadius + outerSinusDisplacement
        leafd1mag = extRadius*radiansPerElementAround
        sinusd1mag = extSinusRadius*radiansPerElementAround  # initial value only
        sinusd1mag = vector.magnitude(smoothCubicHermiteDerivativesLine(
            [ [ extRadius, 0.0, 0.0 ], [ extSinusRadius*math.cos(pi_3), extSinusRadius*math.sin(pi_3), 0.0 ] ],
            [ [ 0.0, leafd1mag, 0.0 ], [ -sinusd1mag*math.sin(pi_3), sinusd1mag*math.cos(pi_3), 0.0 ] ],
            fixStartDerivative = True, fixEndDirection = True)[1])
        sinusd2r, sinusd2z = smoothCubicHermiteDerivativesLine(
            [ [ extSinusRadius , 0.0 ], [ outerRadius, outerHeight ] ],
            [ [ -outerHeight*math.sin(outerAngleRadians), outerHeight*math.cos(outerAngleRadians) ], [ 0.0, outletLength ] ],
            fixStartDirection = True, fixEndDerivative = True)[0]
        extCentre = [ (centre[c] + extz*axis3[c]) for c in range(3) ]
        x [1][0] = []
        d1[1][0] = []
        d2[1][0] = []
        for n1 in range(elementsCountAround):
            radiansAround = n1*radiansPerElementAround
            cosRadiansAround = math.cos(radiansAround)
            sinRadiansAround = math.sin(radiansAround)
            if (n1 % 2) == 0:
                # leaflet junction
                cx = inletCentre
                r = extRadius
                d1mag = leafd1mag
                d2mag1 = leafd2r*cosRadiansAround
                d2mag2 = leafd2r*sinRadiansAround
                d2mag3 = leafd2z
            else:
                # sinus / leaflet centre
                cx = sinusCentre
                r = extSinusRadius
                d1mag = sinusd1mag
                d2mag1 = sinusd2r*cosRadiansAround
                d2mag2 = sinusd2r*sinRadiansAround
                d2mag3 = sinusd2z
            x [1][0].append([ (extCentre[c] + r*(cosRadiansAround*axis1[c] + sinRadiansAround*axis2[c])) for c in range(3) ])
            d1[1][0].append([ d1mag*(-sinRadiansAround*axis1[c] + cosRadiansAround*axis2[c]) for c in range(3) ])
            d2[1][0].append([ (d2mag1*axis1[c] + d2mag2*axis2[c] + d2mag3*axis3[c]) for c in range(3) ])

        # outlet
        x[0][1], d1[0][1] = createCirclePoints(outletCentre, [ axis1[c]*innerRadius for c in range(3) ], [ axis2[c]*innerRadius for c in range(3) ], elementsCountAround)
        x[1][1], d1[1][1] = createCirclePoints(outletCentre, [ axis1[c]*outerRadius for c in range(3) ], [ axis2[c]*outerRadius for c in range(3) ], elementsCountAround)
        d2[1][1] = d2[0][1] = [ [ axis3[c]*outletLength for c in range(3) ] ]*elementsCountAround

        return x, d1, d2


    @classmethod
    def generateNodes(cls, fieldmodule, coordinates, x, d1, d2, startNodeIdentifier = 1):
        """
        Create valve nodes from point coordinates.
        :param fieldmodule: Zinc fieldmodule to create nodes in.
        :param coordinates: Coordinate field to define.
        :param x, d1, d2: Point coordinates and derivatives returned by getPoints().
        All indexed by [n3=wall][n2=inlet->outlet][n1=around] where d1 is around,
        d2 is in direction inlet->outlet.
        :param startNodeIdentifier: First node identifier to use.
        :return: next nodeIdentifier, nodeId[n3][n2][n1].
         """
        nodeIdentifier = startNodeIdentifier
        nodeId = [ [ [], [] ], [ [], [] ] ]
        elementsCountAround = 6  # fixed

        nodes = fieldmodule.findNodesetByFieldDomainType(Field.DOMAIN_TYPE_NODES)
        # nodes in this scaffold do not have a DS3 derivative
        nodetemplate = nodes.createNodetemplate()
        nodetemplate.defineField(coordinates)
        nodetemplate.setValueNumberOfVersions(coordinates, -1, Node.VALUE_LABEL_VALUE, 1)
        nodetemplate.setValueNumberOfVersions(coordinates, -1, Node.VALUE_LABEL_D_DS1, 1)
        nodetemplate.setValueNumberOfVersions(coordinates, -1, Node.VALUE_LABEL_D_DS2, 1)
        cache = fieldmodule.createFieldcache()
        with ChangeManager(fieldmodule):
            # order node creation to be fastest in n3, then n1, then n2
            for n2 in range(2):
                for n1 in range(elementsCountAround):
                    for n3 in range(2):
                        node = nodes.createNode(nodeIdentifier, nodetemplate)
                        cache.setNode(node)
                        coordinates.setNodeParameters(cache, -1, Node.VALUE_LABEL_VALUE, 1, x [n3][n2][n1])
                        coordinates.setNodeParameters(cache, -1, Node.VALUE_LABEL_D_DS1, 1, d1[n3][n2][n1])
                        coordinates.setNodeParameters(cache, -1, Node.VALUE_LABEL_D_DS2, 1, d2[n3][n2][n1])
                        nodeId[n3][n2].append(nodeIdentifier)
                        nodeIdentifier += 1
        return nodeIdentifier, nodeId


    @classmethod
    def generateElements(cls, fieldmodule, coordinates, nodeId, startElementIdentifier = 1):
        """
        Create valve elements from nodes.
        :param fieldmodule: Zinc fieldmodule to create elements in.
        :param coordinates: Coordinate field to define.
        :param nodeId: Node identifiers returned by generateNodes().
        Indexed by [n3=wall][n2=inlet->outlet][n1=around].
        :param startElementIdentifier: First element identifier to use.
        :return: next elementIdentifier, elementId[e1].
         """
        elementIdentifier = startElementIdentifier
        elementId = []
        elementsCountAround = 6  # fixed
        useCrossDerivatives = False

        mesh = fieldmodule.findMeshByDimension(3)
        bicubichermitelinear = eftfactory_bicubichermitelinear(mesh, useCrossDerivatives)
        eft = bicubichermitelinear.createEftNoCrossDerivatives()

        elementtemplate = mesh.createElementtemplate()
        elementtemplate.setElementShapeType(Element.SHAPE_TYPE_CUBE)
        elementtemplate.defineField(coordinates, -1, eft)

        for ea in range(elementsCountAround):
            eb = (ea + 1) % elementsCountAround
            nids = [ nodeId[0][0][ea], nodeId[0][0][eb], nodeId[0][1][ea], nodeId[0][1][eb],
                     nodeId[1][0][ea], nodeId[1][0][eb], nodeId[1][1][ea], nodeId[1][1][eb] ]
            element = mesh.createElement(elementIdentifier, elementtemplate)
            element.setNodesByIdentifier(eft, nids)
            elementId.append(elementIdentifier)
            elementIdentifier += 1

        return elementIdentifier, elementId

    @classmethod
    def generateBaseMesh(cls, region, options):
        """
        Generate the base bicubic-linear Hermite mesh. See also generateMesh().
        Optional extra parameters allow centre and axes to be set.
        :param region: Zinc region to define model in. Must be empty.
        :param options: Dict containing options. See getDefaultOptions().
        :return: list of AnnotationGroup
         """
        fieldmodule = region.getFieldmodule()
        with ChangeManager(fieldmodule):
            coordinates = findOrCreateFieldCoordinates(fieldmodule)
            x, d1, d2 = cls.getPoints(options)
            nodeId = cls.generateNodes(fieldmodule, coordinates, x, d1, d2)[1]
            cls.generateElements(fieldmodule, coordinates, nodeId)[0]
        return []  # annotationGroups


    @classmethod
    def generateMesh(cls, region, options):
        """
        Generate base or refined mesh.
        :param region: Zinc region to create mesh in. Must be empty.
        :param options: Dict containing options. See getDefaultOptions().
        :return: list of AnnotationGroup for mesh.
        """
        if not options['Refine']:
            return cls.generateBaseMesh(region, options)

        refineElementsCountAround = options['Refine number of elements surface']
        refineElementsCountAlong = refineElementsCountAround  # GRC make independent
        refineElementsCountThroughWall = options['Refine number of elements through wall']

        baseRegion = region.createRegion()
        baseAnnotationGroups = cls.generateBaseMesh(baseRegion, options)

        meshrefinement = MeshRefinement(baseRegion, region, baseAnnotationGroups)
        meshrefinement.refineAllElementsCubeStandard3d(refineElementsCountAround, refineElementsCountAlong, refineElementsCountThroughWall)
        return meshrefinement.getAnnotationGroups()
