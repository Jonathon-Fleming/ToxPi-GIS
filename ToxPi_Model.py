# -*- coding: utf-8 -*-

import os
import arcpy
import sys
import json
import csv
import xlwt
import math
import numpy
import pandas
import statistics

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
    with arcpy.da.UpdateCursor(tmpFeatures, [uniqueID, "ToxpiScore", 'BEARING_a', 'BEARING_b', 'RADIUS_']) as cursor:
        for i, row in enumerate(cursor):
            id_ = row[0]
            val = row[1]

            # Increment angles only within each unique coxcomb
            if i == 0:
                 p_id = 0
            if id_ != p_id:
                p_v = 0
                p_id = 0
            # Calculate from and to bearing in Feature Class
            if p_v == 0:
                row[2] = 0
                row[3] = a[0]
            else:
                row[2] = p_v
                row[3] = p_v+a[i%b]
            # Calculate radius (based on value)
            if val > 0:
                row[4] = math.sqrt((val)/math.pi) * scaler
            else:
                row[4] = 0
            # Update row in Feature Class
            cursor.updateRow(row)

             # Previous x,y and bearing angle
            p_id = id_
            p_v += a[i%b]
    del cursor, row



def generate_angles(ang1, ang2):
    '''Generate angles for points closing of the sectors.'''
    yield (ang1-90) * -1
    true = True
    while true:
        if ang1 == 361:
            ang1 = 1
        yield (ang1-90) * -1
        if ang1 == ang2:
            break
        ang1 += 1
# End generate_angles function



def create_sector(pt, radius, ang1, ang2):
    '''Return a point collection to create polygons from.'''
    pointcoll = arcpy.Array()
    pointcoll.add(arcpy.Point(pt.X, pt.Y),)
    for i in generate_angles(ang1, ang2):
        x = pt.X + (radius*math.cos(math.radians(i)))
        y = pt.Y + (radius*math.sin(math.radians(i)))
        pointcoll.add(arcpy.Point(x, y),)
    pointcoll.add(arcpy.Point(pt.X, pt.Y),)
    return pointcoll



def ToxPiFeatures(inFeatures, outFeatures, uniqueID, inFields, inputRadius, radiusUnits, inputWeights, ranks, medians, statemedians):
    """
    coxcombs: In a Coxcomb chart (or rose diagram), each category is represented by a
    segment, each of which has the same angle. The area of a segment represents the value
    of the corresponding category.

    Required arguments:
    inFeatures -- Input point features containing the data to be displayed as a coxcomb feature.
    outFeatures -- The output coxcomb feature class (polygon).
    uniqueID -- A unique identifier for each coxcomb.
    inFields -- List of fields used to create the categories to be displayed on the coxcomb

    """
    try:
        # Temp for testing
        arcpy.env.overwriteOutput = True

        # Check feature class has a projection.
        sr = arcpy.Describe(inFeatures).SpatialReference
        if not sr.type == 'Projected':
            arcpy.AddMessage(sr.type)
            arcpy.AddMessage('Feature dataset must have a projected coordinate system.')
            return

        # Process: Copy Features to output feature class.
        # Create a temp feature class.
        outTmp = "TempFeatures"
        tmpFeatures = arcpy.management.CreateFeatureclass(os.path.dirname(inFeatures),
                                                          outTmp,
                                                          'POINT',
                                                          spatial_reference=sr)

        # List of all input fields
        fldList = inFields.split(";")
        numFlds = len(fldList)
        allFlds = list(fldList)
        allFlds.insert(0, uniqueID)

        # Add field selected as the unique identifier.
        field_obj = arcpy.ListFields(inFeatures, uniqueID)
        #arcpy.AddMessage(field_obj)
        arcpy.AddField_management(tmpFeatures,
                                  field_obj[0].name,
                                  field_type = field_obj[0].type,
                                  field_length = field_obj[0].length,
                                  field_alias = field_obj[0].aliasName)

        # Add fields to store bearings and radius.
        arcpy.AddField_management(tmpFeatures, "ToxpiScore", "DOUBLE")
        arcpy.AddField_management(tmpFeatures, "CATEGORY", "TEXT")
        arcpy.AddField_management(tmpFeatures, "CLASS_", "LONG")
        arcpy.AddField_management(tmpFeatures, "WEIGHT", "TEXT")
        arcpy.AddField_management(tmpFeatures, "RANK", "TEXT")
        arcpy.AddField_management(tmpFeatures, "MEDIAN", "FLOAT")
        arcpy.AddField_management(tmpFeatures, "STATEMEDIAN", "FLOAT")
        arcpy.AddField_management(tmpFeatures, "BEARING_a", "FLOAT")
        arcpy.AddField_management(tmpFeatures, "BEARING_b", "FLOAT")
        arcpy.AddField_management(tmpFeatures, "RADIUS_", "FLOAT")

        # Insert pivoted data from input Feature Class.
        with arcpy.da.SearchCursor(inFeatures, ['SHAPE@XY'] + allFlds) as scur:
            for i, row in enumerate(scur):
                count = 0
                x1,y1 = row[0]
                id_ = row[1]

                for j, f in enumerate(fldList):
                    v = row[count+2]
                    weight = str(inputWeights[count]*100/360) + "%"
                    rank = str(ranks[j][i]) + "/" + str(len(ranks[j]))
                    median = medians[j]
                    statemedian = statemedians[j][id_.split(",")[0]]
                    count = count + 1
                    with arcpy.da.InsertCursor(tmpFeatures, ('Shape@', uniqueID,"ToxpiScore","CATEGORY","CLASS_", "WEIGHT","RANK","MEDIAN", "STATEMEDIAN")) as poly_cursor:
                        poly_cursor.insertRow(([x1,y1],id_,v,f,count,weight,rank, median,statemedian))

        # Find the max values to scale the output features
        if inputRadius == "" or inputRadius == 0:
            inputRadius = 1
        maxRadius = math.sqrt((maxvalue(tmpFeatures, "ToxpiScore"))/math.pi)
        convMax = float(maxRadius) * float(sr.metersPerUnit)
        scaler = (float(inputRadius)*convertLength(radiusUnits))/float(convMax)

        # Create an empty Feature Class to store coxcombs.
        outFolder = os.path.dirname(outFeatures)
        outName = os.path.basename(outFeatures)
        arcpy.env.workspace = outFolder

        cox_polys = arcpy.management.CreateFeatureclass(outFolder,
                                                        outName,
                                                        'POLYGON',
                                                        tmpFeatures,
                                                        spatial_reference=sr)
        # Get all attribute fields.
        search_fields = [f.name for f in arcpy.ListFields(tmpFeatures)]

       # Get the locations in the list for bearings and radius.
        bearing_a_loc = search_fields.index("BEARING_a")+1
        bearing_b_loc = search_fields.index("BEARING_b")+1
        radius_loc = search_fields.index("RADIUS_")+1

        # Process: Calculate bearings and radii
        bearings(tmpFeatures, uniqueID, inputWeights, float(scaler))

        # Report progress for each coxcomb.
        cnt = arcpy.management.GetCount(tmpFeatures)
        increment = int(int(cnt[0]) / 10.0)
        arcpy.SetProgressor("Step", "Creating Coxcombs...",  0, int(cnt[0]), increment)

        # Create coxcombs, polygon sector at a time.
        with arcpy.da.SearchCursor(tmpFeatures, ['SHAPE@XY'] + search_fields + ['OID@']) as scur:
            for i, row in enumerate(scur):
                if (i % increment) == 0:
                    arcpy.SetProgressorPosition(i + 1)

                # Get the fields that hold the bearings and radius information.
                x1, y1 = row[0]
                b_a = row[bearing_a_loc]
                b_b = row[bearing_b_loc]
                radius = row[radius_loc]

                # Create the coxcomb polygons.
                with arcpy.da.InsertCursor(cox_polys, ['SHAPE@'] + search_fields[2:]) as poly_cursor:
                    l = len(search_fields) + 1
                    if radius != 0:
                        poly_cursor.insertRow([arcpy.Polygon(create_sector(arcpy.Point(x1, y1), radius, int(b_a), int(b_b)), sr),] + list(row[3:l]))

            arcpy.SetProgressorPosition(100)
            del poly_cursor
        del scur, row
        arcpy.Delete_management(tmpFeatures)
        arcpy.SetParameterAsText(1,outFeatures)
    except arcpy.ExecuteError:
        print (arcpy.GetMessages(2))
  
def adjustinput(infile, outfile):
  f = open(infile, "r")
  fstring = f.readlines()
  newstring = ""
  headerlist = fstring[0]
  headerlist = headerlist.replace("\"","")
  #headerlist = headerlist.replace(" ","_")
  headerlist = headerlist.split(",")
  possource = headerlist.index("Source")
  headerlist.remove("Source")
  headerlist.insert(possource, "Longitude,")
  headerlist.insert(possource+1, "Latitude,")
  resultheader = []
  colors = []
  weights = []
  infields = ""
  keywords = ["ToxPi Score", "HClust Group", "KMeans Group", "Name", "Source"]
  for i in range(len(headerlist)):
    if headerlist[i] not in  keywords:
      data = ""
      temp = ""
      headerlist[i] = headerlist[i].replace("&", "and")
      headerlist[i] = headerlist[i].replace("\"", "")
      headerlist[i] = headerlist[i].replace(":","")
      headerlist[i] = headerlist[i].replace("-","")
      headerlist[i] = headerlist[i].replace(";","")
      headerlist[i] = headerlist[i].replace(" ","_")
      for j in range(len(headerlist[i])):
        if headerlist[i][j] == "!":
          data = headerlist[i][j:]
          headerlist[i] = headerlist[i][:j] + ","
          infields = infields + headerlist[i] + ";"
          break
        else:
          j += 1
      data = data[1:]
      for j in range(len(data)):
        if data[j] == "!":
          weights.append(float(data[:j]))
        if data[j] == "x":
          colors.append(data[j+1:-2])
    else:
      headerlist[i] = headerlist[i] + ","
  infields = infields[:-1].replace(",","")
  newstring = newstring.join(headerlist)
  newstring = newstring + "\n"
  for j in range(1,len(fstring)):    
    datalist = fstring[j].replace("\n","").split("\",")
    coordinates = datalist[possource].split(",") 
    datalist.pop(possource)
    datalist.insert(possource, coordinates[0])
    datalist.insert(possource+1, "\"" + coordinates[1])
    for i in range(len(datalist)-1):
        datalist[i] = datalist[i] + "\","
    newstring = newstring + "".join(datalist) + "\n"
  fnew = open(outfile, "w")
  fnew.write(newstring)
  f.close()
  fnew.close()
  return weights, colors, infields

def ToxPiCreation(inputdata, outpath):  # ToxPi_Model
    
    # To allow overwriting outputs change overwriteOutput option to True.
    arcpy.env.overwriteOutput = True

    #import toolboxes for use
    arcpy.ImportToolbox(r"c:\program files\arcgis\pro\Resources\ArcToolbox\toolboxes\Conversion Tools.tbx")
    arcpy.ImportToolbox(r"c:\program files\arcgis\pro\Resources\ArcToolbox\toolboxes\Data Management Tools.tbx")
    #arcpy.ImportToolbox(r"c:\program files\arcgis\pro\Resources\ArcToolbox\toolboxes\Create Toxpi.tbx")
   
    #read user input of data file path and determine if it exists
    #inputdata = "C:\Users\Jonathon\Documents\Reif Research\Covid19\Model_10.5_20200621_results.csv"

    #create path for output if it doesn't exist
    #outpath = r"C:\Users\Jonathon\Documents\ArcGIS\Projects\ToxPiguitest\guitest.lyrx"

    outpathtmp = os.path.dirname(outpath)
    if not os.path.exists(outpathtmp):
        os.makedirs(outpathtmp)

    #make geodatabase if it doesn't already exist
    geopath = outpathtmp + "\ToxPiAuto.gdb"
    if not os.path.exists(geopath):
        arcpy.CreateFileGDB_management(str(outpathtmp), "ToxPiAuto.gdb")

    #adjust input file for required parameters
    outfilecsv = outpathtmp + "\ToxPiResultsAdjusted.csv"
    inweights, colors, infields = adjustinput(inputdata, outfilecsv)
    
    #adjust weights to fit a circle (360 deg)
    total = 0
    for i in range(len(inweights)):
      total = total + inweights[i]
    for i in range(len(inweights)):
      inweights[i] = inweights[i]*360/total
    
    #Get ranks and medians
    rankList = []
    medianList = []
    category_names = infields.split(";")
    fh = open(outfilecsv, 'rU')
    # read the file as a dictionary for each row ({header : value})
    reader = csv.DictReader(fh)
    data = {}
    for row in reader:
      for header, value in row.items():
        try:
          data[header].append(value)
        except KeyError:
          data[header] = [value]
    fh.close()
    # extract the variables you want
    name = data["Name"]
    statename = [i.split(",")[0] for i in name]
    statemedians = []
    for cat in category_names:
      a = data[cat]
      n = len(a)
      statedata = {}
      for index in range(n):
        if statename[index] in statedata.keys(): 
          statedata[statename[index]].append(float(a[index]))
        else:
          statedata[statename[index]] = [float(a[index])]
      key_list = list(statedata)
      dic = {}
      for index in range(len(statedata)):
        dic[key_list[index]] = statistics.median(statedata[key_list[index]])
      statemedians.append(dic)  
      #statemedians[cat][key_list[index]] = statistics.median(statedata[key_list[index]])
      ivec=sorted(range(n), key=a.__getitem__)
      svec=[float(a[rank]) for rank in ivec]
      medianList.append(statistics.median(svec))
      sumranks = 0
      dupcount = 0
      newarray = [0]*n
      for i in range(n):
        sumranks += i
        dupcount += 1
        if i==n-1 or svec[i] != svec[i+1]:
            averank = int(sumranks / dupcount) + 1
            for j in range(i-dupcount+1,i+1):
                newarray[ivec[j]] = averank
            sumranks = 0
            dupcount = 0
      rankList.append(newarray)

    # Process: XY Table To Point (Convert csv file to xy point data) 
    tmpfilepoint = geopath + "\pointfeature"
    arcpy.XYTableToPoint_management(in_table=outfilecsv, out_feature_class=tmpfilepoint, x_field="Longitude", y_field="Latitude", z_field="", coordinate_system="PROJCS['USA_Contiguous_Equidistant_Conic',GEOGCS['GCS_North_American_1983',DATUM['D_North_American_1983',SPHEROID['GRS_1980',6378137.0,298.257222101]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Equidistant_Conic'],PARAMETER['False_Easting',0.0],PARAMETER['False_Northing',0.0],PARAMETER['Central_Meridian',-96.0],PARAMETER['Standard_Parallel_1',33.0],PARAMETER['Standard_Parallel_2',45.0],PARAMETER['Latitude_Of_Origin',39.0],UNIT['Meter',1.0]];-22178400 -14320600 10000;-100000 10000;-100000 10000;0.001;0.001;0.001;IsHighPrecision")

    # Process: Convert Coordinate Notation (Convert coordinates to projected instead of geographic) 
    tmpfileremapped = geopath + "\pointfeatureremapped"
    arcpy.ConvertCoordinateNotation_management(in_table=tmpfilepoint, out_featureclass=tmpfileremapped, x_field="Longitude", y_field="Latitude", input_coordinate_format="DD_2", output_coordinate_format="DD_2", id_field="", spatial_reference="PROJCS['USA_Contiguous_Equidistant_Conic',GEOGCS['GCS_North_American_1983',DATUM['D_North_American_1983',SPHEROID['GRS_1980',6378137.0,298.257222101]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Equidistant_Conic'],PARAMETER['False_Easting',0.0],PARAMETER['False_Northing',0.0],PARAMETER['Central_Meridian',-96.0],PARAMETER['Standard_Parallel_1',33.0],PARAMETER['Standard_Parallel_2',45.0],PARAMETER['Latitude_Of_Origin',39.0],UNIT['Meter',1.0]];-22178400 -14320600 10000;-100000 10000;-100000 10000;0.001;0.001;0.001;IsHighPrecision", in_coor_system="GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137.0,298.257223563]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]]", exclude_invalid_records="INCLUDE_INVALID")

    # Process: ToxPi construction (ToxPi construction)     
    radius = 5
    tmpfileToxPi = geopath + "\ToxPifeature"
    ToxPiFeatures(inFeatures=tmpfileremapped, outFeatures=tmpfileToxPi, uniqueID="Name", inFields=infields, inputRadius=int(radius), radiusUnits="MILES", inputWeights=inweights, ranks = rankList, medians = medianList, statemedians = statemedians)

    #make toxpifeatures into feature layer
    #tmpfeaturelyr = r"C:\Users\Jonathon\Documents\ArcGIS\Projects\ToxPiAuto\ToxPiAuto.gdb\ToxPifeaturelayer"
    tmpfeaturelyr = geopath + "\ToxPifeaturelayer"
    arcpy.management.MakeFeatureLayer(tmpfileToxPi, tmpfeaturelyr)
    
    #getsymbology(tmpfeaturelyr, outpath)
    arcpy.management.SaveToLayerFile(tmpfeaturelyr, outpath)
    
    for j in range(len(colors)):
        colors[j] = tuple(int(colors[j][i:i+2], 16) for i in (0, 2, 4))
    
    fh = open(outpath, "r")
    data = fh.read()
    y = json.loads(data)

    # ##popups
    popupstring = """{
        "type" : "CIMPopupInfo",
        "title" : "{Name}",
        "mediaInfos" : [
          {
            "type" : "CIMTextMediaInfo",
            "row" : 1,
            "column" : 1,
            "refreshRateUnit" : "esriTimeUnitsSeconds",
            "text" : "Text"
          },
          {
            "type" : "CIMTableMediaInfo",
            "row" : 2,
            "column" : 1,
            "refreshRateUnit" : "esriTimeUnitsSeconds",
            "fields" : [
              "Name",
              "CATEGORY",
              "ToxpiScore",
              "WEIGHT",
              "RANK",
              "MEDIAN",
              "STATEMEDIAN"
            ]
          },
          {
            "type" : "CIMBarChartMediaInfo",
            "row" :3,
            "column" : 1,
            "refreshRateUnit" : "esriTimeUnitsSeconds",
            "fields" : [
              "ToxpiScore",
              "MEDIAN",
              "STATEMEDIAN"
            ],
            "caption" : "Average Comparison",
            "title" : "{CATEGORY}"
          }
        ]
      }
    """
    y["layerDefinitions"][0]["popupInfo"] = json.loads(popupstring)

    renderer = """{
        "type" : "CIMUniqueValueRenderer",
        "visualVariables" : [
          {
            "type" : "CIMSizeVisualVariable",
            "authoringInfo" : {
              "type" : "CIMVisualVariableAuthoringInfo",
              "minSliderValue" : 0.10000000000000001,
              "maxSliderValue" : 0.10000000000000001,
              "heading" : "Custom"
            },
            "randomMax" : 1,
            "minSize" : 1,
            "maxSize" : 13,
            "minValue" : 0.10000000000000001,
            "maxValue" : 0.10000000000000001,
            "valueRepresentation" : "Radius",
            "variableType" : "Graduated",
            "valueShape" : "Unknown",
            "axis" : "HeightAxis",
            "target" : "outline",
            "normalizationType" : "Nothing",
            "valueExpressionInfo" : {
              "type" : "CIMExpressionInfo",
              "title" : "Custom",
              "expression" : ".1",
              "returnType" : "Default"
            }
          }
        ],
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
          "CATEGORY"
        ],
        "groups" : [
          {
            "type" : "CIMUniqueValueGroup",
            "classes" : [ """
    
    tmpfields = infields.split(";")
    for i in range(len(tmpfields)):
      skeleton = f"""
              {{
                "type" : "CIMUniqueValueClass",
                "label" : "{tmpfields[i]}",
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
                        "miterLimit" : 10,
                        "width" : 0.10000000000000001,
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
                      "{tmpfields[i]}"
                    ]
                  }}
                ],
                "visible" : true
              }},"""
      renderer = renderer + skeleton
    renderer = renderer[:-1]
    rendererend = """            
            ],
            "heading" : "CATEGORY"
          }
        ],
        "useDefaultSymbol" : true,
        "polygonSymbolColorTarget" : "Fill"
      }"""
    renderer = renderer + rendererend
    y["layerDefinitions"][0]["renderer"] = json.loads(renderer)
    dump = json.dumps(y)
    fh.close()
    fh = open(outpath, "w")
    fh.write(dump)
    sys.exit()

if __name__ == '__main__':
    ToxPiCreation(sys.argv[1], sys.argv[2])
