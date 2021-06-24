# -*- coding: utf-8 -*-

import os
import arcpy
import sys
import json
import csv
import xlwt
import math
import numpy
import pandas as pd
import statistics
import re

def convertLength(radiusUnits):
    if radiusUnits.upper() == "METERS":
        return 1
    if radiusUnits.upper() == "FEET":
        return 0.2 #0.3048
    if radiusUnits.upper() == "MILES":
        return 4000 #1609.344
    if radiusUnits.upper() == "KILOMETERS":
        return 1000.0

def maxvalue(fclass, field):
    na = arcpy.da.FeatureClassToNumPyArray(fclass, field)
    return numpy.max(na[field])

def bearings(tmpFeatures, uniqueID, a, scaler):
    '''calculate the radius and bearings for each sector.'''
    b=len(a)
    with arcpy.da.UpdateCursor(tmpFeatures, [uniqueID, "Score", 'BEARING_a', 'BEARING_b', 'RADIUS_']) as cursor:
        for i, row in enumerate(cursor): 
            id_ = row[0]
            val = row[1]

            # Increment angles only within each unique toxpi figure
            if i == 0:
                 p_id = 0
            if id_ != p_id:
                p_v = 90
                p_id = 0
            # Calculate from and to bearing in Feature Class
            if p_v == 90:
                row[2] = 90
                row[3] = 90 - a[0]
                if row[3] < 0:
                    row[3] = row[3]+360
            else:
                row[2] = p_v
                row[3] = p_v-a[i%b]
                if row[3] < 0:
                    row[3] = row[3]+360
            # Calculate radius (based on value)
            if val > 0:
                row[4] = val * scaler
            else:
                row[4] = 0
            # Update row in Feature Class
            cursor.updateRow(row)

             # Previous x,y and bearing angle
            p_id = id_
            p_v += -a[i%b]
            if p_v < 0:
                p_v = p_v+360
    del cursor, row

def generate_angles(ang1, ang2):
    '''Generate angles for points closing of the sectors.'''
    yield (ang1-90) * -1
    true = True
    while true:
        if ang1 == -1:
            ang1 = 359
        yield (ang1-90) * -1
        if ang1 == ang2:
            break
        ang1 += -1
        
def generate_anglesreverse(ang2, ang1):
    yield (ang2-90) * -1
    true = True
    while true:
        if ang1 == ang2:
            break
        if ang2 == 360:
            ang2 = 0
        yield (ang2-90) * -1
        if ang1 == ang2:
            break
        ang2 += 1

def create_sector(pt, radius, ang1, ang2, innerradius, ring=False):
    '''Return a point collection to create polygons from.'''
    pointcoll = arcpy.Array()
    if ring==False:
        #x = pt.X + (innerradius*math.cos(math.radians(ang1)))
        #y = pt.Y + (innerradius*math.sin(math.radians(ang1)))
        #pointcoll.add(arcpy.Point(x,y),)
        for index, i in enumerate(generate_angles(ang1, ang2)):
            x = pt.X + (radius*math.cos(math.radians(i))) + (innerradius*math.cos(math.radians(i))) 
            y = pt.Y + (radius*math.sin(math.radians(i))) + (innerradius*math.sin(math.radians(i)))
            pointcoll.add(arcpy.Point(x, y),)
        for i in generate_anglesreverse(ang2, ang1):
            x = pt.X + (innerradius*math.cos(math.radians(i)))
            y = pt.Y + (innerradius*math.sin(math.radians(i)))
            pointcoll.add(arcpy.Point(x, y),)
    else:
        for index, i in enumerate(generate_anglesreverse(ang2, ang1)):
            x = pt.X + (innerradius*math.cos(math.radians(i))) + (radius*math.cos(math.radians(i))) 
            y = pt.Y + (innerradius*math.sin(math.radians(i))) + (radius*math.sin(math.radians(i)))
            if index == 0:
                firstx = x
                firsty = y
            pointcoll.add(arcpy.Point(x, y),)
        pointcoll.add(arcpy.Point(firstx, firsty),)
    return pointcoll


def ToxPiFeatures(inFeatures, outFeatures, uniqueID, uniqueidtype, inFields, inputRadius, radiusUnits, inputWeights, ranks = None, medians=None ,statemedians = None, stateranks=None, Large = False):
    """
    Required arguments:
    inFeatures -- Input point features containing the data to be displayed as a toxpi feature.
    outFeatures -- The output toxpi feature class (polygon).
    uniqueID -- A unique identifier for each toxpi drawing.
    inFields -- List of fields used to create the categories to be displayed on the toxpi figures
    """
    try:

        # Check feature class has a projection.
        sr = arcpy.Describe(inFeatures).SpatialReference
        if not sr.type == 'Projected':
            arcpy.AddMessage(sr.type)
            arcpy.AddMessage('Feature dataset must have a projected coordinate system.')
            return

        # Create a temp feature class
        outTmp = "TempFeatures"
        tmpFeatures = arcpy.management.CreateFeatureclass(os.path.dirname(inFeatures),
                                                          outTmp,
                                                          'POINT',
                                                          spatial_reference=sr)

        # List of all input fields
        numFlds = len(inFields)
        allFlds = list(inFields)
        allFlds.insert(0, uniqueID)

        # Add fields required for output to temp feature class
        arcpy.AddField_management(tmpFeatures, uniqueID, "TEXT")
        arcpy.AddField_management(tmpFeatures, "Score", "DOUBLE")
        arcpy.AddField_management(tmpFeatures, "SliceName", "TEXT")
        arcpy.AddField_management(tmpFeatures, "CLASS_", "LONG")
        arcpy.AddField_management(tmpFeatures, "Weight", "TEXT")
        arcpy.AddField_management(tmpFeatures, "BEARING_a", "FLOAT")
        arcpy.AddField_management(tmpFeatures, "BEARING_b", "FLOAT")
        arcpy.AddField_management(tmpFeatures, "RADIUS_", "FLOAT")

        # Insert pivoted data from input Feature Class.

        if Large: # If drawing the state averages of data
          arcpy.AddField_management(tmpFeatures, "Name", "TEXT")
          arcpy.AddField_management(tmpFeatures, "Rank", "TEXT")
          arcpy.AddField_management(tmpFeatures, "USAMedian", "DOUBLE")
          with arcpy.da.SearchCursor(inFeatures, ['SHAPE@XY', "STATE_FIPS", "STATE_NAME"]) as scur:
            for i, row in enumerate(scur): #for each input data point
                count = 0
                x1,y1 = row[0]  #get coordinates for point
                id_ = row[1]    #get state FIPS for point
                name = row[2]   #get state name

                for j, f in enumerate(inFields): #loop through slice fields
                    weight = str(inputWeights[count]*100/360) + "%" #get weight for slice as percentage
                    median = round(medians[j], 3)                   #get USAmedian for slice
                    statemedian = round(statemedians[j][id_], 3)    #get statemedian for slice 
                    staterank = stateranks[j][id_]                  #get the states rank in US for the slice           
                    count = count + 1
                    with arcpy.da.InsertCursor(tmpFeatures, ('Shape@', "Name", uniqueID, "Score","SliceName","CLASS_", "Weight", "Rank", "USAMedian")) as poly_cursor:
                      poly_cursor.insertRow(([x1,y1],name,id_, statemedian,f,count,weight, staterank, median))

        elif ranks != None:  #If drawing the input data
            arcpy.AddField_management(tmpFeatures, "Name", "TEXT")
            arcpy.AddField_management(tmpFeatures, "Rank", "TEXT")
            arcpy.AddField_management(tmpFeatures, "USAMedian", "DOUBLE")
            arcpy.AddField_management(tmpFeatures, "StateMedian", "DOUBLE")
            with arcpy.da.SearchCursor(inFeatures, ['SHAPE@XY', "Name", "STATE_FIPS"] + allFlds) as scur:
              for i, row in enumerate(scur): #for each input data point
                count = 0
                x1,y1 = row[0] #get coordinates for point
                name = row[1] #get name for point
                state_id = row[2] #get state FIPS for point            
                id_ = row[3] #get county or census FIPS for point

                for j, f in enumerate(inFields): #loop through slice fields
                    v = round(row[count+4], 3) #get toxpi score for slice
                    weight = str(inputWeights[count]*100/360) + "%" #get weight for slice as percentage
                    rank = ranks[j][id_] #get rank in the US for slice score
                    median = round(medians[j], 3) #get US median for slice
                    statemedian = round(statemedians[j][state_id], 3) #get state median for slice
                    count = count + 1
                    with arcpy.da.InsertCursor(tmpFeatures, ('Shape@', "Name", uniqueID,"Score","SliceName","CLASS_", "Weight","Rank","USAMedian", "StateMedian")) as poly_cursor:
                        poly_cursor.insertRow(([x1,y1],name,id_,v,f,count,weight,rank, median,statemedian))
        else:
          print(allFlds)
          if uniqueID != "Name":
            arcpy.AddField_management(tmpFeatures, "Name", "TEXT")
          with arcpy.da.SearchCursor(inFeatures, ['SHAPE@XY', "Name"] + allFlds) as scur:
              for i, row in enumerate(scur): #for each input data point
                count = 0
                x1,y1 = row[0] #get coordinates for point
                name = row[1]          
                id_ = row[2] #get county or census FIPS for point

                for j, f in enumerate(inFields): #loop through slice fields
                    v = round(row[count+3], 3) #get toxpi score for slice
                    weight = str(inputWeights[count]*100/360) + "%" #get weight for slice as percentage
                    count = count + 1
                    with arcpy.da.InsertCursor(tmpFeatures, ('Shape@', "Name", uniqueID,"Score","SliceName","CLASS_", "Weight")) as poly_cursor:
                        poly_cursor.insertRow(([x1,y1],name, id_,v,f,count,weight))
            
        # Find the max values to scale the output features
        if inputRadius == "" or inputRadius == 0:
            inputRadius = 1
        maxRadius = math.sqrt(1/math.pi)
        convMax = float(maxRadius) * float(sr.metersPerUnit)
        scaler = (float(inputRadius)*convertLength(radiusUnits))/float(convMax)
        innerradius = scaler/30
        # Create an empty Feature Class to store toxpi figures
        outFolder = os.path.dirname(outFeatures)
        outName = os.path.basename(outFeatures)
        arcpy.env.workspace = outFolder

        tox_polys = arcpy.management.CreateFeatureclass(outFolder,
                                                        outName,
                                                        'POLYGON',
                                                        tmpFeatures,
                                                        spatial_reference=sr)
        # Get all attribute fields
        search_fields = [f.name for f in arcpy.ListFields(tmpFeatures)]

       # Get the locations in the list for bearings and radius
        bearing_a_loc = search_fields.index("BEARING_a")+1
        bearing_b_loc = search_fields.index("BEARING_b")+1
        radius_loc = search_fields.index("RADIUS_")+1

        # Calculate bearings and radii
        bearings(tmpFeatures, uniqueID, inputWeights, float(scaler))

        # Create toxpi figures, polygon sector at a time.
        with arcpy.da.SearchCursor(tmpFeatures, ['SHAPE@XY'] + search_fields + ['OID@']) as scur:
            for i, row in enumerate(scur):

                # Get the fields that hold the bearings and radius information
                x1, y1 = row[0]
                b_a = row[bearing_a_loc]
                b_b = row[bearing_b_loc]
                radius = row[radius_loc]

                # Create the toxpi slice polygons
                with arcpy.da.InsertCursor(tox_polys, ['SHAPE@'] + search_fields[2:]) as poly_cursor:
                    l = len(search_fields) + 1
                    if (i+1)%numFlds == 0:
                        poly_cursor.insertRow([arcpy.Polygon(create_sector(arcpy.Point(x1, y1), 0, 360, 0, innerradius, ring=True), sr,),] + list(row[3:l]))
                    else:
                        if radius != 0:
                            poly_cursor.insertRow([arcpy.Polygon(create_sector(arcpy.Point(x1, y1), radius, int(b_a), int(b_b), innerradius), sr,),] + list(row[3:l]))
        arcpy.Delete_management(tmpFeatures)

        outName = os.path.basename(outFeatures) + "Rings"
        Tox_Rings = arcpy.management.CreateFeatureclass(outFolder,
                                                        outName,
                                                        'POLYLINE',
                                                        spatial_reference=sr)
        arcpy.AddField_management(Tox_Rings, uniqueID, "TEXT")
        with arcpy.da.SearchCursor(inFeatures, ['SHAPE@XY', uniqueID, 'OID@']) as scur:
            for i, row in enumerate(scur): #for each input data point
                count = 0
                x1,y1 = row[0] #get coordinates for point
                id_ = row[1]          
                with arcpy.da.InsertCursor(Tox_Rings, ('Shape@', uniqueID)) as poly_cursor:
                    poly_cursor.insertRow([arcpy.Polyline(create_sector(arcpy.Point(x1, y1), scaler, 360, 0, innerradius, ring = True), sr,), id_])
        
    except arcpy.ExecuteError:
        print (arcpy.GetMessages(2))
  
def adjustinput(infile, outfile):
    #prep csv file for input into functions and get required parameters

    #read in csv file, split the coordinates, and replace special characters from the header
    df = pd.read_csv(infile)
    df[['Longitude','Latitude']] = df.Source.str.split(",",expand = True,)
    del df['Source']

    #determine if required columns are present
    if "Name" not in df.columns: #throw an error if names are not present
        print("Error: Name column is not present in the input data. Please add column labeled Name with desired point names.")
        sys.exit()
    if "FIPS" in df.columns:
      uniqueid = "FIPS"
      df["FIPS"] = df["FIPS"].apply(str)
      digits = len(df["FIPS"][1])
      #determine if the data is at the county or census tract level
      if digits <= 5 and digits > 2:
        uniqueidtype = "FIPS"
      elif digits > 5: 
        uniqueidtype = "Tract"
      else: 
        uniqueidtype = "None"
    else: #throw an error if FIPS are not present
      uniqueid = "Name"
      uniqueidtype = "None"
        #print("Error: FIPS column is not present in the input data. Please add a column labeled FIPS with the corresponding identifiers.")
        #sys.exit()

    #add zeros to start of FIPS if they are not present
    if uniqueidtype != "None":
      for i in range(len(df["FIPS"])):
        if uniqueidtype == "FIPS": 
          digits = len(df.at[i, uniqueid])
          while digits < 5:
            df.at[i, uniqueid] = "0" + df.at[i, uniqueid]
            digits += 1
        else: #if id is census tract FIPS
          digits = len(df.at[i, uniqueid])
          while digits < 11:
            df.at[i, uniqueid] = "0" + df.at[i, uniqueid]
            digits += 1

        #add quotes around FIPS to force reading in as string
        df.at[i, uniqueid] = "\"" + str(df.at[i, uniqueid]) + "\"" 
    #get required symbology parameters and slices from column headers
    colors = []
    weights = []
    infields = []
    keywords = ["ToxPi Score", "HClust Group", "KMeans Group", "Name", "Longitude","Latitude","FIPS", "Tract"]
    for name in df.columns:
        weightstartpos = 0
        weightendpos = 0
        if name not in keywords:
            for i, letter in enumerate(name):
                if weightendpos != 0 and letter == 'x':
                    colors.append(name[i+1:-2])
                if letter != "!":
                    continue
                else:
                    if weightstartpos == 0:
                        weightstartpos = i
                        infields.append(re.sub('\W+','_', name[:weightstartpos]))
                        if infields[-1][0].isdigit(): 
                            infields[-1] = "F" + infields[-1]
                        df.rename(columns = {name:name[:weightstartpos]}, inplace = True) 
                    else:
                        weightendpos = i
                        weights.append(float(name[weightstartpos + 1: weightendpos]))   
    df.columns = [re.sub('\W+','_', header) for header in df.columns]             
    df.to_csv(outfile)
    return weights, colors, infields, uniqueidtype, uniqueid


def GetSymbology(colors, infields, location):
  if location == "foreground":
    renderer = """{
        "type" : "CIMUniqueValueRenderer",
        "defaultLabel" : "<all other values>",
        "defaultSymbol" : {
          "type" : "CIMSymbolReference",
          "symbol" : {
            "type" : "CIMPolygonSymbol",
            "symbolLayers" : [
              {
                "type" : "CIMSolidStroke",
                "enable" : true,
                "capStyle" : "Round",
                "joinStyle" : "Round",
                "lineStyle3D" : "Strip",
                "miterLimit" : 10,
                "width" : 0.10000000000000001,
                "color" : {
                  "type" : "CIMRGBColor",
                  "values" : [
                    255,
                    255,
                    255,
                    100
                  ]
                }
              },
              {
                "type" : "CIMSolidFill",
                "enable" : true,
                "color" : {
                  "type" : "CIMRGBColor",
                  "values" : [
                    130,
                    130,
                    130,
                    100
                  ]
                }
              }
            ]
          }
        },
        "defaultSymbolPatch" : "Default",
        "fields" : [
          "SliceName"
        ],
        "groups" : [
          {
            "type" : "CIMUniqueValueGroup",
            "classes" : [ """
    
    for i in range(len(infields)):
      skeleton = f"""
              {{
                "type" : "CIMUniqueValueClass",
                "label" : "{infields[i]}",
                "patch" : "Default",
                "symbol" : {{
                  "type" : "CIMSymbolReference",
                  "symbol" : {{
                    "type" : "CIMPolygonSymbol",
                    "symbolLayers" : [
                      {{
                        "type" : "CIMSolidStroke",
                        "enable" : true,
                        "capStyle" : "Round",
                        "joinStyle" : "Round",
                        "lineStyle3D" : "Strip",
                        "miterLimit" : 1,
                        "width" : 0.5,
                        "color" : {{
                          "type" : "CIMRGBColor",
                          "values" : [
                            255,
                            255,
                            255,
                            100
                          ]
                        }}
                      }},
                      {{
                        "type" : "CIMSolidFill",
                        "enable" : true,
                        "color" : {{
                          "type" : "CIMRGBColor",
                          "values" : [
                            {colors[i][0]},
                            {colors[i][1]},
                            {colors[i][2]},
                            100
                          ]
                        }}
                      }}
                    ]
                  }}
                }},
                "values" : [
                  {{
                    "type" : "CIMUniqueValue",
                    "fieldValues" : [
                      "{infields[i]}"
                    ]
                  }}
                ],
                "visible" : true
              }},"""
      renderer = renderer + skeleton
    renderer = renderer[:-1]
    rendererend = """            
            ],
            "heading" : "SliceName"
          }
        ],
        "useDefaultSymbol" : true,
        "polygonSymbolColorTarget" : "Fill"
      }"""
    renderer = renderer + rendererend

  elif location == "background":
    renderer = """{
        "type" : "CIMClassBreaksRenderer",
        "barrierWeight" : "High",
        "breaks" : [
          {
            "type" : "CIMClassBreak",
            "label" : "1",
            "patch" : "Default",
            "symbol" : {
              "type" : "CIMSymbolReference",
              "symbol" : {
                "type" : "CIMPolygonSymbol",
                "symbolLayers" : [
                  {
                    "type" : "CIMSolidStroke",
                    "enable" : true,
                    "capStyle" : "Round",
                    "joinStyle" : "Round",
                    "lineStyle3D" : "Strip",
                    "miterLimit" : 10,
                    "width" : 0.5,
                    "color" : {
                      "type" : "CIMRGBColor",
                      "values" : [
                        130,
                        130,
                        130,
                        100
                      ]
                    }
                  },
                  {
                    "type" : "CIMSolidFill",
                    "enable" : true,
                    "color" : {
                      "type" : "CIMRGBColor",
                      "values" : [
                        130,
                        130,
                        130,
                        0
                      ]
                    }
                  }
                ]
              }
            },
            "upperBound" : 1
          }
        ],
        "classBreakType" : "UnclassedColor",
        "classificationMethod" : "DefinedInterval",
        "colorRamp" : {
          "type" : "CIMMultipartColorRamp",
          "colorSpace" : {
            "type" : "CIMICCColorSpace",
            "url" : "Default RGB"
          },
          "colorRamps" : [
            {
              "type" : "CIMLinearContinuousColorRamp",
              "colorSpace" : {
                "type" : "CIMICCColorSpace",
                "url" : "Default RGB"
              },
              "fromColor" : {
                "type" : "CIMRGBColor",
                "colorSpace" : {
                  "type" : "CIMICCColorSpace",
                  "url" : "Default RGB"
                },
                "values" : [
                  13,
                  38,
                  68,
                  100
                ]
              },
              "toColor" : {
                "type" : "CIMRGBColor",
                "colorSpace" : {
                  "type" : "CIMICCColorSpace",
                  "url" : "Default RGB"
                },
                "values" : [
                  56,
                  98,
                  122,
                  100
                ]
              }
            },
            {
              "type" : "CIMLinearContinuousColorRamp",
              "colorSpace" : {
                "type" : "CIMICCColorSpace",
                "url" : "Default RGB"
              },
              "fromColor" : {
                "type" : "CIMRGBColor",
                "colorSpace" : {
                  "type" : "CIMICCColorSpace",
                  "url" : "Default RGB"
                },
                "values" : [
                  56,
                  98,
                  122,
                  100
                ]
              },
              "toColor" : {
                "type" : "CIMRGBColor",
                "colorSpace" : {
                  "type" : "CIMICCColorSpace",
                  "url" : "Default RGB"
                },
                "values" : [
                  98,
                  158,
                  176,
                  100
                ]
              }
            },
            {
              "type" : "CIMLinearContinuousColorRamp",
              "colorSpace" : {
                "type" : "CIMICCColorSpace",
                "url" : "Default RGB"
              },
              "fromColor" : {
                "type" : "CIMRGBColor",
                "colorSpace" : {
                  "type" : "CIMICCColorSpace",
                  "url" : "Default RGB"
                },
                "values" : [
                  98,
                  158,
                  176,
                  100
                ]
              },
              "toColor" : {
                "type" : "CIMRGBColor",
                "colorSpace" : {
                  "type" : "CIMICCColorSpace",
                  "url" : "Default RGB"
                },
                "values" : [
                  177,
                  205,
                  194,
                  100
                ]
              }
            },
            {
              "type" : "CIMLinearContinuousColorRamp",
              "colorSpace" : {
                "type" : "CIMICCColorSpace",
                "url" : "Default RGB"
              },
              "fromColor" : {
                "type" : "CIMRGBColor",
                "colorSpace" : {
                  "type" : "CIMICCColorSpace",
                  "url" : "Default RGB"
                },
                "values" : [
                  177,
                  205,
                  194,
                  100
                ]
              },
              "toColor" : {
                "type" : "CIMRGBColor",
                "colorSpace" : {
                  "type" : "CIMICCColorSpace",
                  "url" : "Default RGB"
                },
                "values" : [
                  255,
                  252,
                  212,
                  100
                ]
              }
            }
          ],
          "weights" : [
            0.25,
            0.25,
            0.25,
            0.25
          ]
        },
        "field" : "Score",
        "minimumBreak" : 0,
        "numberFormat" : {
          "type" : "CIMNumericFormat",
          "alignmentOption" : "esriAlignRight",
          "alignmentWidth" : 0,
          "roundingOption" : "esriRoundNumberOfDecimals",
          "roundingValue" : 2,
          "useSeparator" : true
        },
        "showInAscendingOrder" : true,
        "heading" : "Score",
        "sampleSize" : 10000,
        "useDefaultSymbol" : true,
        "defaultSymbolPatch" : "Default",
        "defaultSymbol" : {
          "type" : "CIMSymbolReference",
          "symbol" : {
            "type" : "CIMPolygonSymbol",
            "symbolLayers" : [
              {
                "type" : "CIMSolidStroke",
                "enable" : true,
                "capStyle" : "Round",
                "joinStyle" : "Round",
                "lineStyle3D" : "Strip",
                "miterLimit" : 10,
                "width" : 0.5,
                "color" : {
                  "type" : "CIMRGBColor",
                  "values" : [
                    110,
                    110,
                    110,
                    100
                  ]
                }
              },
              {
                "type" : "CIMSolidFill",
                "enable" : true,
                "color" : {
                  "type" : "CIMRGBColor",
                  "values" : [
                    130,
                    130,
                    130,
                    100
                  ]
                }
              }
            ]
          }
        },
        "minimumLabel" : "0",
        "defaultLabel" : "<null>",
        "polygonSymbolColorTarget" : "Fill",
        "normalizationType" : "Nothing",
        "useExclusionSymbol" : false,
        "exclusionSymbolPatch" : "Default",
        "visualVariables" : [
          {
            "type" : "CIMColorVisualVariable",
            "expression" : "[Score]",
            "minValue" : 0,
            "maxValue" : 1,
            "colorRamp" : {
              "type" : "CIMMultipartColorRamp",
              "colorSpace" : {
                "type" : "CIMICCColorSpace",
                "url" : "Default RGB"
              },
              "colorRamps" : [
                {
                  "type" : "CIMLinearContinuousColorRamp",
                  "colorSpace" : {
                    "type" : "CIMICCColorSpace",
                    "url" : "Default RGB"
                  },
                  "fromColor" : {
                    "type" : "CIMRGBColor",
                    "colorSpace" : {
                      "type" : "CIMICCColorSpace",
                      "url" : "Default RGB"
                    },
                    "values" : [
                      13,
                      38,
                      68,
                      100
                    ]
                  },
                  "toColor" : {
                    "type" : "CIMRGBColor",
                    "colorSpace" : {
                      "type" : "CIMICCColorSpace",
                      "url" : "Default RGB"
                    },
                    "values" : [
                      56,
                      98,
                      122,
                      100
                    ]
                  }
                },
                {
                  "type" : "CIMLinearContinuousColorRamp",
                  "colorSpace" : {
                    "type" : "CIMICCColorSpace",
                    "url" : "Default RGB"
                  },
                  "fromColor" : {
                    "type" : "CIMRGBColor",
                    "colorSpace" : {
                      "type" : "CIMICCColorSpace",
                      "url" : "Default RGB"
                    },
                    "values" : [
                      56,
                      98,
                      122,
                      100
                    ]
                  },
                  "toColor" : {
                    "type" : "CIMRGBColor",
                    "colorSpace" : {
                      "type" : "CIMICCColorSpace",
                      "url" : "Default RGB"
                    },
                    "values" : [
                      98,
                      158,
                      176,
                      100
                    ]
                  }
                },
                {
                  "type" : "CIMLinearContinuousColorRamp",
                  "colorSpace" : {
                    "type" : "CIMICCColorSpace",
                    "url" : "Default RGB"
                  },
                  "fromColor" : {
                    "type" : "CIMRGBColor",
                    "colorSpace" : {
                      "type" : "CIMICCColorSpace",
                      "url" : "Default RGB"
                    },
                    "values" : [
                      98,
                      158,
                      176,
                      100
                    ]
                  },
                  "toColor" : {
                    "type" : "CIMRGBColor",
                    "colorSpace" : {
                      "type" : "CIMICCColorSpace",
                      "url" : "Default RGB"
                    },
                    "values" : [
                      177,
                      205,
                      194,
                      100
                    ]
                  }
                },
                {
                  "type" : "CIMLinearContinuousColorRamp",
                  "colorSpace" : {
                    "type" : "CIMICCColorSpace",
                    "url" : "Default RGB"
                  },
                  "fromColor" : {
                    "type" : "CIMRGBColor",
                    "colorSpace" : {
                      "type" : "CIMICCColorSpace",
                      "url" : "Default RGB"
                    },
                    "values" : [
                      177,
                      205,
                      194,
                      100
                    ]
                  },
                  "toColor" : {
                    "type" : "CIMRGBColor",
                    "colorSpace" : {
                      "type" : "CIMICCColorSpace",
                      "url" : "Default RGB"
                    },
                    "values" : [
                      255,
                      252,
                      212,
                      100
                    ]
                  }
                }
              ],
              "weights" : [
                0.25,
                0.25,
                0.25,
                0.25
              ]
            },
            "normalizationType" : "Nothing",
            "polygonSymbolColorTarget" : "Fill"
          }
        ]
      }"""
  return renderer

def GetPopupInfo(layer, position=""):
  if layer == "County":
    if position == "foreground":
      name = '{Name}'
    elif position == "background":
      name = '{STATE_NAME}, {Name}'

    title = '"title" : "' + name + '",'
    text = '"text" : "<div><p><span style=\\\"font-weight:bold;\\\">Slice Statistics</span></p><p><span>Name: ' + name + '</span></p><p><span>SliceName: {SliceName}</span></p><p><span>Weight: {Weight}</span></p><p><span>Score: {Score}</span></p><p><span>USAMedian: {USAMedian}</span></p><p><span>StateMedian: {StateMedian}</span></p><p><span>Rank(1 Lowest Risk): {Rank}</span></p></div>"'
  elif layer == "State":
    title = '"title" : "{Name} Median",'
    text = '"text" : "<div><p><span style=\\\"font-weight:bold;\\\">Slice Statistics</span></p><p><span>Name: {Name} Median</span></p><p><span>SliceName: {SliceName}</span></p><p><span>Weight: {Weight}</span></p><p><span>Score: {Score}</span></p><p><span>Rank(1 Lowest Risk): {Rank}</span></p><p><span>USAMedian: {USAMedian}</span></p></div>"'
  popupstring = '''{
        "type" : "CIMPopupInfo",
        ''' + title + '''
        "mediaInfos" : [
          {
            "type" : "CIMTextMediaInfo",
            "row" : 1,
            "column" : 1,
            "refreshRateUnit" : "esriTimeUnitsSeconds",
            ''' + text + '''
          },
          {
            "type" : "CIMBarChartMediaInfo",
            "row" :3,
            "column" : 1,
            "refreshRateUnit" : "esriTimeUnitsSeconds",
            "fields" : [
              "Score",
              "USAMedian",
              "StateMedian"
            ],
            "caption" : "Comparison of Medians",
            "title" : "{SliceName}"
          }
        ]
      }
    '''
  return popupstring

def ToxPiCreation(inputdata, outpath):  # ToxPi_Model
    
    #get pathname for reading and writing files
    outpathtmp = os.path.dirname(outpath)
    if not os.path.exists(outpathtmp):
        os.makedirs(outpathtmp)

    #adjust input file for required parameters and get required information
    outfilecsv = outpathtmp + "\ToxPiResultsAdjusted.csv"
    inweights, colors, infields, uniqueidtype, uniqueid = adjustinput(inputdata, outfilecsv)

    #adjust weights to fit a circle (360 deg)
    total = 0
    for i in range(len(inweights)):
      total = total + inweights[i]
    for i in range(len(inweights)):
      inweights[i] = inweights[i]*360/total

    #append info for adding a center dot with overall score
    inweights.append(360)
    colors.append("FFFFFF")
    infields.append("ToxPi_Score")
    category_names = infields

    # start geopreocessing prep
    # To allow overwriting outputs change overwriteOutput option to True.
    arcpy.env.overwriteOutput = True

    #import toolboxes for use
    arcpy.ImportToolbox(r"c:\program files\arcgis\pro\Resources\ArcToolbox\toolboxes\Conversion Tools.tbx")
    arcpy.ImportToolbox(r"c:\program files\arcgis\pro\Resources\ArcToolbox\toolboxes\Data Management Tools.tbx")

    #make geodatabase if it doesn't already exist
    geopath = outpathtmp + "\ToxPiAuto.gdb"
    if not os.path.exists(geopath):
        arcpy.CreateFileGDB_management(str(outpathtmp), "ToxPiAuto.gdb")
    
    #Convert csv file to xy point data 
    tmpfilepoint = geopath + "\pointfeature"
    arcpy.XYTableToPoint_management(in_table=outfilecsv, out_feature_class=tmpfilepoint, x_field="Longitude", y_field="Latitude", z_field="", coordinate_system="PROJCS['USA_Contiguous_Equidistant_Conic',GEOGCS['GCS_North_American_1983',DATUM['D_North_American_1983',SPHEROID['GRS_1980',6378137.0,298.257222101]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Equidistant_Conic'],PARAMETER['False_Easting',0.0],PARAMETER['False_Northing',0.0],PARAMETER['Central_Meridian',-96.0],PARAMETER['Standard_Parallel_1',33.0],PARAMETER['Standard_Parallel_2',45.0],PARAMETER['Latitude_Of_Origin',39.0],UNIT['Meter',1.0]];-22178400 -14320600 10000;-100000 10000;-100000 10000;0.001;0.001;0.001;IsHighPrecision")

    #Convert coordinates to projected instead of geographic
    tmpfileremapped = geopath + "\pointfeatureremapped"
    arcpy.ConvertCoordinateNotation_management(in_table=tmpfilepoint, out_featureclass=tmpfileremapped, x_field="Longitude", y_field="Latitude", input_coordinate_format="DD_2", output_coordinate_format="DD_2", id_field="", spatial_reference="PROJCS['USA_Contiguous_Equidistant_Conic',GEOGCS['GCS_North_American_1983',DATUM['D_North_American_1983',SPHEROID['GRS_1980',6378137.0,298.257222101]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Equidistant_Conic'],PARAMETER['False_Easting',0.0],PARAMETER['False_Northing',0.0],PARAMETER['Central_Meridian',-96.0],PARAMETER['Standard_Parallel_1',33.0],PARAMETER['Standard_Parallel_2',45.0],PARAMETER['Latitude_Of_Origin',39.0],UNIT['Meter',1.0]];-22178400 -14320600 10000;-100000 10000;-100000 10000;0.001;0.001;0.001;IsHighPrecision", in_coor_system="GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137.0,298.257223563]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]]", exclude_invalid_records="INCLUDE_INVALID")
    test = arcpy.ListFields(tmpfileremapped)
    tmp = []
    for field in test:
        tmp.append(field.name)
    print(tmp)
    #remove quotes used to force identifier to a string
    if uniqueidtype != "None":
      with arcpy.da.UpdateCursor(tmpfileremapped, uniqueid) as scur:
        for row in scur:
          row[0] = row[0].replace("\"","")
          scur.updateRow(row)
    
    if uniqueidtype == "FIPS":
      boundaries = arcpy.management.CopyFeatures("https://services.arcgis.com/P3ePLMYs2RVChkJx/arcgis/rest/services/USA_Counties_Generalized/FeatureServer/0", geopath + "\countypolylayer")
      arcpy.management.JoinField(tmpfileremapped, uniqueid, boundaries, "FIPS", ["STATE_FIPS", "CNTY_FIPS"])
      #joinstatename = arcpy.management.JoinField(countyboundaries, "FIPS", tmpfileremapped, uniqueid, list(category_names))
      #countyFIPS = arcpy.analysis.Select(joinstatename, geopath + "\countyFIPS", '"ToxPi_Score" IS NOT NULL')
    elif uniqueidtype == "Tract":
      boundaries = arcpy.management.CopyFeatures("https://services1.arcgis.com/aT1T0pU1ZdpuDk1t/arcgis/rest/services/CensusTracts/FeatureServer/0", geopath + "\censusypolylayer")
      arcpy.management.JoinField(tmpfileremapped, uniqueid, boundaries, "FIPS", ["STATE_FIPS", "CNTY_FIPS"])
      # joinstatename = arcpy.management.JoinField(countyboundaries, "TRACT", tmpfileremapped, uniqueid, list(category_names))
      # countyFIPS = arcpy.analysis.Select(joinstatename, geopath + "\censusFIPS", '"ToxPi_Score" IS NOT NULL')
    elif uniqueidtype == "None":
      radius = 1
      tmpfileToxPi = geopath + "\ToxPifeature"
      ToxPiFeatures(inFeatures=tmpfileremapped, outFeatures=tmpfileToxPi, uniqueID = uniqueid, uniqueidtype = uniqueidtype, inFields=infields, inputRadius=int(radius), radiusUnits="MILES", inputWeights=inweights)
      #make toxpifeatures into feature layer
      countytoxpilyr = arcpy.management.MakeFeatureLayer(tmpfileToxPi, "County ToxPi")
      arcpy.management.SaveToLayerFile(countytoxpilyr, outpath)

      #get color rgb codes from hex codes
      for j in range(len(colors)):
        colors[j] = tuple(int(colors[j][i:i+2], 16) for i in (0, 2, 4))
    
      #open county toxpi feature layer file for editing
      fh = open(outpath, "r")
      data = fh.read()
      y = json.loads(data)

      #alter popups for county toxpi feature layer
      y["layerDefinitions"][0]["popupInfo"] = json.loads(GetPopupInfo("County", position = "foreground"))

      #alter symbology for county toxpi feature layer
      y["layerDefinitions"][0]["renderer"] = json.loads(GetSymbology(colors, infields, "foreground"))

      #write the edits to the county toxpi layer file
      mainlyr = json.dumps(y)
      fh.close()
      fh = open(outpath, "w")
      fh.write(mainlyr)
      fh.close()

      finallyr = arcpy.mp.LayerFile(outpath)

      countytoxpilyrrings = arcpy.management.MakeFeatureLayer(tmpfileToxPi + "Rings", "County ToxPi Rings")
      arcpy.management.SaveToLayerFile(countytoxpilyrrings, outpathtmp + r"\rings.lyrx")
      fh = open(outpathtmp + r"\rings.lyrx", "r")
      data = fh.read()
      y = json.loads(data)

      y["layerDefinitions"][0]["renderer"]["symbol"]["symbol"]["symbolLayers"][0]["color"]["values"][0] = "0"
      y["layerDefinitions"][0]["renderer"]["symbol"]["symbol"]["symbolLayers"][0]["color"]["values"][1] = "0"
      y["layerDefinitions"][0]["renderer"]["symbol"]["symbol"]["symbolLayers"][0]["color"]["values"][2] = "0"
      y["layerDefinitions"][0]["renderer"]["symbol"]["symbol"]["symbolLayers"][0]["color"]["values"][3] = "100"  
      #write the edits to the county toxpi layer file
      mainlyr = json.dumps(y)
      fh.close()
      fh = open(outpathtmp + r"\rings.lyrx", "w")
      fh.write(mainlyr)
      fh.close()
 
      countyrings = arcpy.mp.LayerFile(outpathtmp + r"\rings.lyrx")
      finallyr.addLayer(countyrings, "BOTTOM")
      
      finallyr.save()
      sys.exit()
      
    #store toxpi scores as a list of slices, where each index contains a dictionary of states, and each dictionary contains a dictionary of county values
    sectionedtoxpidata = []

    #store toxpi scores as a list of slices where each index is a dict of county scores
    toxpidata = []

    #save data in dictionaries at the county level and at the state level
    with arcpy.da.SearchCursor(tmpfileremapped, ["STATE_FIPS","CNTY_FIPS",uniqueid,] + list(category_names)) as scur:
      for j, row in enumerate(scur):
            for i in range(len(category_names)):
                if j == 0:
                    countydata = {row[0]: {row[1]: float(row[i+3])}}
                    sectionedtoxpidata.append(countydata)

                    toxpidata.append({row[2]: float(row[i+3])})
                else: 
                    if row[0] in list(sectionedtoxpidata[i]):
                        sectionedtoxpidata[i][row[0]][row[1]] = float(row[i+3])
                    else:
                        sectionedtoxpidata[i][row[0]] = {row[1]: float(row[i+3])}
                    toxpidata[i][row[2]] = float(row[i+3])

      #initialize arrays for stats info for slices
      countyUSAmedians = [None]*len(category_names)
      countyStatemedians = []
      countyrankslist = []
      stateranklist = []
      #statemediansmedian = []*len(category_names)

      #calculate stats for each slice type
      for z, cat in enumerate(category_names):
        #get county level USA rank
        sorteddict = {k: v for k, v in sorted(toxpidata[z].items(), key=lambda item: item[1])}
        countyranks = {}
        for i,v in enumerate(sorteddict):
            countyranks[v] = str(i+1) + "/" + str(len(sorteddict))
        countyrankslist.append(countyranks)

        #get county level USA medians
        countyUSAmedians[z] = statistics.median([v for k, v in toxpidata[z].items()])

        #get county level state medians
        for i, state in enumerate(sectionedtoxpidata[z].keys()):
            if i == 0:
                val = statistics.median([v for k, v in sectionedtoxpidata[z][state].items()])
                dicttmp = {state: val}
                countyStatemedians.append(dicttmp)
            else:
                countyStatemedians[z][state] = statistics.median([v for k, v in sectionedtoxpidata[z][state].items()])

        #get state level USA Median
        #statemediansmedian[z] = statistics.median([v for k, v in countyStatemedians[z].items()])

        #get state level rank
        sorteddict = {k: v for k, v in sorted(countyStatemedians[z].items(), key=lambda item: item[1])}
        stateranks = {}
        for i,v in enumerate(sorteddict):
            stateranks[v] = str(i+1) + "/" + str(len(sorteddict))
        stateranklist.append(stateranks)


      #initialize arrays for stats info for slices
      countyUSAmedians = [None]*len(category_names)
      countyrankslist = []
      #statemediansmedian = []*len(category_names)

      #calculate stats for each slice type
      for z, cat in enumerate(category_names):
        #get county level USA rank
        sorteddict = {k: v for k, v in sorted(toxpidata[z].items(), key=lambda item: item[1])}
        countyranks = {}
        for i,v in enumerate(sorteddict):
            countyranks[v] = str(i+1) + "/" + str(len(sorteddict))
        countyrankslist.append(countyranks)

        #get county level USA medians
        countyUSAmedians[z] = statistics.median([v for k, v in toxpidata[z].items()])

    # Process: ToxPi construction (ToxPi construction)     
    radius = 1
    tmpfileToxPi = geopath + "\ToxPifeature"
    ToxPiFeatures(inFeatures=tmpfileremapped, outFeatures=tmpfileToxPi, uniqueID = uniqueid, uniqueidtype = uniqueidtype, inFields=infields, inputRadius=int(radius), radiusUnits="MILES", inputWeights=inweights, ranks = countyrankslist, medians = countyUSAmedians, statemedians = countyStatemedians, stateranks = stateranklist)

    #make toxpifeatures into feature layer
    countytoxpilyr = arcpy.management.MakeFeatureLayer(tmpfileToxPi, "County ToxPi")
    arcpy.management.SaveToLayerFile(countytoxpilyr, outpath)
    

    #get color rgb codes from hex codes
    for j in range(len(colors)):
        colors[j] = tuple(int(colors[j][i:i+2], 16) for i in (0, 2, 4))
    
    #open county toxpi feature layer file for editing
    fh = open(outpath, "r")
    data = fh.read()
    y = json.loads(data)

    #alter popups for county toxpi feature layer
    y["layerDefinitions"][0]["popupInfo"] = json.loads(GetPopupInfo("County", position = "foreground"))

    #alter symbology for county toxpi feature layer
    y["layerDefinitions"][0]["renderer"] = json.loads(GetSymbology(colors, infields, "foreground"))

    #set that minimum extent for county toxpi feature layer
    y["layerDefinitions"][0]["minScale"] = "500000"

    #write the edits to the county toxpi layer file
    mainlyr = json.dumps(y)
    fh.close()
    fh = open(outpath, "w")
    fh.write(mainlyr)
    fh.close()
    
    #get county toxpi layer as an object for adding other layers to
    finallyr = arcpy.mp.LayerFile(outpath)

    countytoxpilyrrings = arcpy.management.MakeFeatureLayer(tmpfileToxPi + "Rings", "County ToxPi Rings")
    arcpy.management.SaveToLayerFile(countytoxpilyrrings, outpathtmp + r"\countyrings")

    fh = open(outpathtmp + r"\countyrings.lyrx", "r")
    data = fh.read()
    y = json.loads(data)
    #set that minimum extent for county toxpi ring feature layer
    y["layerDefinitions"][0]["minScale"] = "500000"
    y["layerDefinitions"][0]["renderer"]["symbol"]["symbol"]["symbolLayers"][0]["color"]["values"][0] = "0"
    y["layerDefinitions"][0]["renderer"]["symbol"]["symbol"]["symbolLayers"][0]["color"]["values"][1] = "0"
    y["layerDefinitions"][0]["renderer"]["symbol"]["symbol"]["symbolLayers"][0]["color"]["values"][2] = "0"
    y["layerDefinitions"][0]["renderer"]["symbol"]["symbol"]["symbolLayers"][0]["color"]["values"][3] = "100"   
    #write the edits to the county toxpi layer file
    mainlyr = json.dumps(y)
    fh.close()
    fh = open(outpathtmp + r"\countyrings.lyrx", "w")
    fh.write(mainlyr)
    fh.close()

    countytoxpirings = arcpy.mp.LayerFile(outpathtmp + r"\countyrings.lyrx")
    finallyr.addLayer(countytoxpirings, "BOTTOM") 

    #Construct medium county toxpi figures 
    tmpfileToxPi = geopath + "\ToxPifeaturemid"
    ToxPiFeatures(inFeatures=tmpfileremapped, outFeatures=tmpfileToxPi, uniqueID=uniqueid, uniqueidtype = uniqueidtype, inFields=infields, inputRadius=int(radius)*5, radiusUnits="MILES", inputWeights=inweights, ranks = countyrankslist, medians = countyUSAmedians, statemedians = countyStatemedians, stateranks = stateranklist)

    #make toxpifeatures into feature layer
    countytoxpilyrmid = arcpy.management.MakeFeatureLayer(tmpfileToxPi, "County ToxPi Mid")
    arcpy.management.SaveToLayerFile(countytoxpilyrmid, outpathtmp + "\MidSizedToxpi")
    
    #open county toxpi feature layer file for editing
    fh = open(outpathtmp + "\MidSizedToxpi.lyrx", "r")
    data = fh.read()
    y = json.loads(data)

    #alter popups for county toxpi feature layer
    y["layerDefinitions"][0]["popupInfo"] = json.loads(GetPopupInfo("County", position = "foreground"))

    #alter symbology for county toxpi feature layer
    y["layerDefinitions"][0]["renderer"] = json.loads(GetSymbology(colors, infields, "foreground"))

    #set that minimum extent for mid county toxpi feature layer
    y["layerDefinitions"][0]["minScale"] = "2000000"
    y["layerDefinitions"][0]["maxScale"] = "500000"

    #write the edits to the county toxpi layer file
    mainlyr = json.dumps(y)
    fh.close()
    fh = open(outpathtmp + "\MidSizedToxpi.lyrx", "w")
    fh.write(mainlyr)
    fh.close()

    midtoxpilyrrings = arcpy.management.MakeFeatureLayer(tmpfileToxPi + "Rings", "Mid ToxPi Rings")
    arcpy.management.SaveToLayerFile(midtoxpilyrrings, outpathtmp + r"\midrings")
    
    fh = open(outpathtmp + r"\midrings.lyrx", "r")
    data = fh.read()
    y = json.loads(data)
    #set that minimum extent for county toxpi ring feature layer
    y["layerDefinitions"][0]["minScale"] = "2000000"
    y["layerDefinitions"][0]["maxScale"] = "500000"
    y["layerDefinitions"][0]["renderer"]["symbol"]["symbol"]["symbolLayers"][0]["color"]["values"][0] = "0"
    y["layerDefinitions"][0]["renderer"]["symbol"]["symbol"]["symbolLayers"][0]["color"]["values"][1] = "0"
    y["layerDefinitions"][0]["renderer"]["symbol"]["symbol"]["symbolLayers"][0]["color"]["values"][2] = "0"
    y["layerDefinitions"][0]["renderer"]["symbol"]["symbol"]["symbolLayers"][0]["color"]["values"][3] = "100"   

    #write the edits to the county toxpi layer file
    mainlyr = json.dumps(y)
    fh.close()
    fh = open(outpathtmp + r"\midrings.lyrx", "w")
    fh.write(mainlyr)
    fh.close()

    #get county toxpi layer as an object and add to final lyr
    midcountytoxpilyr = arcpy.mp.LayerFile(outpathtmp + "\MidSizedToxpi.lyrx")
    finallyr.addLayer(midcountytoxpilyr, "BOTTOM")  

    midtoxpilyrrings = arcpy.mp.LayerFile(outpathtmp + r"\midrings.lyrx")
    finallyr.addLayer(midtoxpilyrrings, "BOTTOM")

    #retrieve state polygon boundaries from web url
    stateboundaries = arcpy.management.CopyFeatures("https://services.arcgis.com/P3ePLMYs2RVChkJx/arcgis/rest/services/USA_States_Generalized/FeatureServer/0", geopath + "\statepolylayer")

    #save state boundaries to a feature layer
    statebackground=arcpy.management.MakeFeatureLayer(geopath+"\statepolylayer","State Boundaries")
    countytoxpiinfo = arcpy.analysis.Select(countytoxpilyr, "countytoxpiinfo", '"SliceName" = \'ToxPi_Score\'')

    statebackgroundpartial = arcpy.management.SelectLayerByLocation(statebackground, overlap_type = "CONTAINS", select_features = countytoxpiinfo)
    arcpy.management.SaveToLayerFile(statebackgroundpartial, outpathtmp + "\statepolygons")

    #get point locations in center of state boundaries
    arcpy.management.FeatureToPoint(statebackgroundpartial, geopath + "\statepointstmp", "INSIDE")
    
    #create state toxpi features from point data
    tmpfileToxPiLg = geopath + "\ToxPifeatureLg"
    ToxPiFeatures(inFeatures=geopath + "\statepointstmp", outFeatures=tmpfileToxPiLg, uniqueID="STATE_FIPS", uniqueidtype = uniqueidtype, inFields=infields, inputRadius=int(radius)*30, radiusUnits="MILES", inputWeights=inweights, ranks = countyrankslist, medians = countyUSAmedians, statemedians = countyStatemedians, stateranks = stateranklist, Large = True)

    #save state toxpi features to a feature layer file
    statetoxpilyr = arcpy.management.MakeFeatureLayer(tmpfileToxPiLg, "State ToxPi")
    arcpy.management.SaveToLayerFile(statetoxpilyr, outpathtmp + "\StateToxPi")

    statetoxpilyrrings = arcpy.management.MakeFeatureLayer(tmpfileToxPiLg + "Rings", "State ToxPi Rings")
    arcpy.management.SaveToLayerFile(statetoxpilyrrings, outpathtmp + r"\staterings")

    fh = open(outpathtmp + r"\staterings.lyrx", "r")
    data = fh.read()
    y = json.loads(data)
    #set that minimum extent for county toxpi ring feature layer
    y["layerDefinitions"][0]["maxScale"] = "2000000"
    y["layerDefinitions"][0]["renderer"]["symbol"]["symbol"]["symbolLayers"][0]["color"]["values"][0] = "0"
    y["layerDefinitions"][0]["renderer"]["symbol"]["symbol"]["symbolLayers"][0]["color"]["values"][1] = "0"
    y["layerDefinitions"][0]["renderer"]["symbol"]["symbol"]["symbolLayers"][0]["color"]["values"][2] = "0"
    y["layerDefinitions"][0]["renderer"]["symbol"]["symbol"]["symbolLayers"][0]["color"]["values"][3] = "100"   
    #write the edits to the county toxpi layer file
    mainlyr = json.dumps(y)
    fh.close()
    fh = open(outpathtmp + r"\staterings.lyrx", "w")
    fh.write(mainlyr)
    fh.close()

    #add overall toxpi info to state boundaries and save to a layer file
    statetoxpiinfo = arcpy.analysis.Select(statetoxpilyr, "statetoxpiinfo", '"SliceName" = \'ToxPi_Score\'')
    stateinfo = arcpy.analysis.SpatialJoin(statebackgroundpartial, statetoxpiinfo, "stateinfo", match_option = "CONTAINS")
    statebackground=arcpy.management.MakeFeatureLayer(stateinfo,"State Boundaries")
    arcpy.management.SaveToLayerFile(statebackground, outpathtmp + "\statepolygons")

    # open state boundary layer for editing
    fh = open(outpathtmp + "\statepolygons.lyrx", "r")
    data = fh.read()
    y = json.loads(data)

    #alter popups for state boundary feature layer
    y["layerDefinitions"][0]["popupInfo"] = json.loads(GetPopupInfo("State"))

    #Set symbology for state boundary layer
    y["layerDefinitions"][0]["renderer"] = json.loads(GetSymbology(colors, infields, "background"))

    #Set extent for state boundary layer
    y["layerDefinitions"][0]["maxScale"] = "2000000"

    #Rewrite the state boundary layer to a layer file
    mainlyr = json.dumps(y)
    fh.close()
    fh = open(outpathtmp + "\statepolygons.lyrx", "w")
    fh.write(mainlyr)
    fh.close()
    
    #open state toxpi feature layer for editing
    fh = open(outpathtmp + "\StateToxPi.lyrx", "r")
    data = fh.read()
    y = json.loads(data)

    #alter popups for state toxpi feature layer
    y["layerDefinitions"][0]["popupInfo"] = json.loads(GetPopupInfo("State"))
    
    #alter symbology for state toxpi feature layer
    y["layerDefinitions"][0]["renderer"] = json.loads(GetSymbology(colors, infields, "foreground"))

    #set extent for state toxpi feature layer
    y["layerDefinitions"][0]["maxScale"] = "2000000"

    #rewrite edits to state toxpi layer file
    mainlyr = json.dumps(y)
    fh.close()
    fh = open(outpathtmp + "\stateToxPi.lyrx", "w")
    fh.write(mainlyr)
    fh.close()

    #add overall toxpi info to county boundaries and save to a layer file
    joinedtoxpiinfo = arcpy.management.JoinField(boundaries,"FIPS", countytoxpiinfo, "FIPS")
    backgroundpartial = arcpy.analysis.Select(joinedtoxpiinfo, geopath + r"\boundaryselect", '"Score" IS NOT NULL')
    background = arcpy.management.MakeFeatureLayer(backgroundpartial,"Boundaries")
    arcpy.management.SaveToLayerFile(background, outpathtmp + r"\boundarypolygons")
 
    #open county boundary layer file for editing
    fh = open(outpathtmp + r"\boundarypolygons.lyrx", "r")
    data = fh.read()
    y = json.loads(data)

    #alter popups for county boundary feature layer
    y["layerDefinitions"][0]["popupInfo"] = json.loads(GetPopupInfo("County", position = "background"))

    #alter symbology for county boundary layer
    y["layerDefinitions"][0]["renderer"] = json.loads(GetSymbology(colors, infields, "background"))

    #set extent for county boundary layer
    y["layerDefinitions"][0]["minScale"] = "2000000"

    #rewrite edits to county boundary layer file
    mainlyr = json.dumps(y)
    fh.close()
    fh = open(outpathtmp + r"\boundarypolygons.lyrx", "w")
    fh.write(mainlyr)
    fh.close()

    #get county boundary layer as an object and add to final lyr
    countypolylyr = arcpy.mp.LayerFile(outpathtmp + r"\boundarypolygons.lyrx")
    finallyr.addLayer(countypolylyr, "TOP")

    #Get state boundaries as an object and add to final lyr
    statepolylyr = arcpy.mp.LayerFile(outpathtmp + "\statepolygons.lyrx")
    finallyr.addLayer(statepolylyr, "BOTTOM")

    staterings = arcpy.mp.LayerFile(outpathtmp + r"\staterings.lyrx")
    finallyr.addLayer(staterings, "BOTTOM")

    #get state toxpi feature layer as an object and add to final lyr
    statetoxpilyr = arcpy.mp.LayerFile(outpathtmp + "\stateToxPi.lyrx")
    finallyr.addLayer(statetoxpilyr, "BOTTOM")

    finallyr.save()

    sys.exit()

if __name__ == '__main__':
    ToxPiCreation(sys.argv[1], sys.argv[2])
