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
    with arcpy.da.UpdateCursor(tmpFeatures, [uniqueID, "ToxPiScore", 'BEARING_a', 'BEARING_b', 'RADIUS_']) as cursor:
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

def generate_anglesreverse(ang2, ang1):
    yield (ang2-90) * -1
    true = True
    while true:
        if ang1 == ang2:
            break
        if ang2 == 0:
            ang2 = 360
        yield (ang2-90) * -1
        if ang1 == ang2:
            break
        ang2 += -1
# End generate_angles function


def create_sector(pt, radius, ang1, ang2, innerradius=0):
    '''Return a point collection to create polygons from.'''
    pointcoll = arcpy.Array()
    pointcoll.add(arcpy.Point(pt.X, pt.Y),)
    for index, i in enumerate(generate_angles(ang1, ang2)):
        x = pt.X + (radius*math.cos(math.radians(i)))
        y = pt.Y + (radius*math.sin(math.radians(i)))
        if index ==0:
          firstx = x
          firsty = y
        pointcoll.add(arcpy.Point(x, y),)
    if innerradius == 0:
      return pointcoll
    for i in generate_anglesreverse(ang2, ang1):
        x = pt.X + (innerradius*math.cos(math.radians(i)))
        y = pt.Y + (innerradius*math.sin(math.radians(i)))
        pointcoll.add(arcpy.Point(x, y),)
    pointcoll.add(arcpy.Point(firstx, firsty),)
    return pointcoll



def ToxPiFeatures(inFeatures, outFeatures, uniqueID, inFields, inputRadius, radiusUnits, inputWeights, ranks, medians, statemedians,innerradius,Large = False):
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
        arcpy.AddField_management(tmpFeatures, "ToxPiScore", "DOUBLE")
        arcpy.AddField_management(tmpFeatures, "SliceName", "TEXT")
        arcpy.AddField_management(tmpFeatures, "CLASS_", "LONG")
        arcpy.AddField_management(tmpFeatures, "Weight", "TEXT")
        arcpy.AddField_management(tmpFeatures, "Rank", "TEXT")
        arcpy.AddField_management(tmpFeatures, "USAMedian", "FLOAT")
        arcpy.AddField_management(tmpFeatures, "StateMedian", "FLOAT")
        arcpy.AddField_management(tmpFeatures, "BEARING_a", "FLOAT")
        arcpy.AddField_management(tmpFeatures, "BEARING_b", "FLOAT")
        arcpy.AddField_management(tmpFeatures, "RADIUS_", "FLOAT")

        # Insert pivoted data from input Feature Class.
        if Large:
          #for slices in fldList:
            #arcpy.AddField_management(tmpFeatures, str(slices), "TEXT")
          with arcpy.da.SearchCursor(inFeatures, ['SHAPE@XY', uniqueID]) as scur:
            for i, row in enumerate(scur):
                count = 0
                x1,y1 = row[0]
                id_ = row[1]

                for j, f in enumerate(fldList):
                    #v = row[count+2]
                    weight = str(inputWeights[count]*100/360) + "%"
                    #rank = str(ranks[j][i]) + "/" + str(len(ranks[j]))
                    median = medians[j]
                    if id_.split(",")[0].lower() in list(statemedians[j]):
                      statemedian = statemedians[j][id_.split(",")[0].lower()]
                    else:
                      statemedian = -1
                    count = count + 1
                    with arcpy.da.InsertCursor(tmpFeatures, ('Shape@', uniqueID,"ToxPiScore","SliceName","CLASS_", "Weight","USAMedian")) as poly_cursor:
                        poly_cursor.insertRow(([x1,y1],id_,statemedian,f,count,weight, median))
        else:  
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
                    statemedian = statemedians[j][id_.split(",")[0].lower()]
                    count = count + 1
                    with arcpy.da.InsertCursor(tmpFeatures, ('Shape@', uniqueID,"ToxPiScore","SliceName","CLASS_", "Weight","Rank","USAMedian", "StateMedian")) as poly_cursor:
                        poly_cursor.insertRow(([x1,y1],id_,v,f,count,weight,rank, median,statemedian))

        # Find the max values to scale the output features
        if inputRadius == "" or inputRadius == 0:
            inputRadius = 1
        maxRadius = math.sqrt((maxvalue(tmpFeatures, "ToxPiScore"))/math.pi)
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
                    if (i+1)%numFlds == 0:
                        poly_cursor.insertRow([arcpy.Polygon(create_sector(arcpy.Point(x1, y1), innerradius, 0, 360), sr,),] + list(row[3:l]))
                    else:
                        if radius != 0:
                            poly_cursor.insertRow([arcpy.Polygon(create_sector(arcpy.Point(x1, y1), radius, int(b_a), int(b_b), innerradius), sr,),] + list(row[3:l]))
            #def create_sector(pt, radius, ang1, ang2):
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
      headerlist[i] = headerlist[i].replace(" ","_") + ","
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

    inweights.append(360)
    colors.append("FFFFFF")
    infields  = infields  + ";ToxPi_Score"
    
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
    statename = [i.split(",")[0].lower() for i in name]
    if name[0].split(",")[1][0] == " ":
      countyname = [i.split(",")[1][1:].lower() for i in name]
    else:
      countyname = [i.split(",")[1].lower() for i in name]
    #might need to add county name here

    #contains dictionaries of state medians for each category name
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

      if cat == "ToxPi_Score":
        countytoxpidata = {}
        for index in range(n):
          if statename[index] not in countytoxpidata.keys():
            countytoxpidata[statename[index]] = {}
          countytoxpidata[statename[index]][countyname[index]] = float(a[index])

    # Process: XY Table To Point (Convert csv file to xy point data) 
    tmpfilepoint = geopath + "\pointfeature"
    arcpy.XYTableToPoint_management(in_table=outfilecsv, out_feature_class=tmpfilepoint, x_field="Longitude", y_field="Latitude", z_field="", coordinate_system="PROJCS['USA_Contiguous_Equidistant_Conic',GEOGCS['GCS_North_American_1983',DATUM['D_North_American_1983',SPHEROID['GRS_1980',6378137.0,298.257222101]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Equidistant_Conic'],PARAMETER['False_Easting',0.0],PARAMETER['False_Northing',0.0],PARAMETER['Central_Meridian',-96.0],PARAMETER['Standard_Parallel_1',33.0],PARAMETER['Standard_Parallel_2',45.0],PARAMETER['Latitude_Of_Origin',39.0],UNIT['Meter',1.0]];-22178400 -14320600 10000;-100000 10000;-100000 10000;0.001;0.001;0.001;IsHighPrecision")

    # Process: Convert Coordinate Notation (Convert coordinates to projected instead of geographic) 
    tmpfileremapped = geopath + "\pointfeatureremapped"
    arcpy.ConvertCoordinateNotation_management(in_table=tmpfilepoint, out_featureclass=tmpfileremapped, x_field="Longitude", y_field="Latitude", input_coordinate_format="DD_2", output_coordinate_format="DD_2", id_field="", spatial_reference="PROJCS['USA_Contiguous_Equidistant_Conic',GEOGCS['GCS_North_American_1983',DATUM['D_North_American_1983',SPHEROID['GRS_1980',6378137.0,298.257222101]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Equidistant_Conic'],PARAMETER['False_Easting',0.0],PARAMETER['False_Northing',0.0],PARAMETER['Central_Meridian',-96.0],PARAMETER['Standard_Parallel_1',33.0],PARAMETER['Standard_Parallel_2',45.0],PARAMETER['Latitude_Of_Origin',39.0],UNIT['Meter',1.0]];-22178400 -14320600 10000;-100000 10000;-100000 10000;0.001;0.001;0.001;IsHighPrecision", in_coor_system="GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137.0,298.257223563]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]]", exclude_invalid_records="INCLUDE_INVALID")

    # Process: ToxPi construction (ToxPi construction)     
    radius = 1
    innerradius = 100
    tmpfileToxPi = geopath + "\ToxPifeature"
    ToxPiFeatures(inFeatures=tmpfileremapped, outFeatures=tmpfileToxPi, uniqueID="Name", inFields=infields, inputRadius=int(radius), radiusUnits="MILES", inputWeights=inweights, ranks = rankList, medians = medianList, statemedians = statemedians, innerradius = innerradius)
    
    #make toxpifeatures into feature layer
    #tmpfeaturelyr = r"C:\Users\Jonathon\Documents\ArcGIS\Projects\ToxPiAuto\ToxPiAuto.gdb\ToxPifeaturelayer"
    tmpfeaturelyr = geopath + "\ToxPifeaturelayer"
    #arcpy.management.Merge([tmpfileToxPi, tmpfileremapped], tmpfeaturelyr)
    #featurelyr = geopath + "\ToxPifeaturelayer"
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
            "text" : "<div><p><span style=\\\"font-weight:bold;\\\">Slice Statistics</span></p><p><span>Name: {Name}</span></p><p><span>SliceName: {SliceName}</span></p><p><span>Weight: {Weight}</span></p><p><span>ToxPiScore: {ToxPiScore}</span></p><p><span>USAMedian: {USAMedian}</span></p><p><span>StateMedian: {StateMedian}</span></p><p><span>Rank(1 Lowest Risk): {Rank}</span></p></div>"
          },
          {
            "type" : "CIMBarChartMediaInfo",
            "row" :3,
            "column" : 1,
            "refreshRateUnit" : "esriTimeUnitsSeconds",
            "fields" : [
              "ToxPiScore",
              "USAMedian",
              "StateMedian"
            ],
            "caption" : "Comparison of Medians",
            "title" : "{SliceName}"
          }
        ]
      }
    """
    y["layerDefinitions"][0]["popupInfo"] = json.loads(popupstring)

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
            "heading" : "SliceName"
          }
        ],
        "useDefaultSymbol" : true,
        "polygonSymbolColorTarget" : "Fill"
      }"""
    renderer = renderer + rendererend
    y["layerDefinitions"][0]["renderer"] = json.loads(renderer)
    y["layerDefinitions"][0]["minScale"] = "5000000"
    #y["layerDefinitions"][0]["minscale"] = " : 5000000"

    #y["layerDefinitions"][1] = json.loads(layerdef)
    mainlyr = json.dumps(y)
    fh.close()
    fh = open(outpath, "w")
    fh.write(mainlyr)
    fh.close()
    
    #arcpy.management.SaveToLayerFile(outpath, outpath)
    countytoxpilyr = arcpy.mp.LayerFile(outpath)

    arcpy.management.CopyFeatures("https://services.arcgis.com/P3ePLMYs2RVChkJx/arcgis/rest/services/USA_States_Generalized/FeatureServer/0", geopath + "\statepolylayer")
    arcpy.management.AddField(geopath + "\statepolylayer", "ToxPiScore", "Float")
    with arcpy.da.UpdateCursor(geopath+"\statepolylayer", ["STATE_NAME","ToxPiScore",]) as scur:
        for row in scur:
          if row[0].lower() in list(statedata):
            row[1] = statemedians[-1][row[0].lower()]
            scur.updateRow(row)
    featureLayer=arcpy.management.MakeFeatureLayer(geopath+"\statepolylayer","statepolygons")
    arcpy.management.SaveToLayerFile(featureLayer, outpathtmp + "\statepolygons")

    arcpy.management.FeatureToPoint(featureLayer, geopath + "\statepointstmp", "INSIDE")
    tmpfileToxPiLg = geopath + "\ToxPifeatureLg"
    ToxPiFeatures(inFeatures=geopath + "\statepointstmp", outFeatures=tmpfileToxPiLg, uniqueID="STATE_NAME", inFields=infields, inputRadius=int(radius)*30, radiusUnits="MILES", inputWeights=inweights, ranks = rankList, medians = medianList, statemedians = statemedians, innerradius = innerradius*30, Large = True)
    arcpy.management.MakeFeatureLayer(tmpfileToxPiLg, geopath + "\stateToxPi")
    arcpy.management.SaveToLayerFile(geopath + "\stateToxPi", outpathtmp + "\stateToxPi")

    rendererbackground = """{
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
        "field" : "ToxPiScore",
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
        "heading" : "ToxPiScore",
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
            "expression" : "[ToxPiScore]",
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

    fh = open(outpathtmp + "\statepolygons.lyrx", "r")
    data = fh.read()
    y = json.loads(data)
    y["layerDefinitions"][0]["renderer"] = json.loads(rendererbackground)
    y["layerDefinitions"][0]["maxScale"] = "5000000"
    mainlyr = json.dumps(y)
    fh.close()
    fh = open(outpathtmp + "\statepolygons.lyrx", "w")
    fh.write(mainlyr)
    fh.close()

    statepolylyr = arcpy.mp.LayerFile(outpathtmp + "\statepolygons.lyrx")
    #statepolylyr.maxScale = 5000000
    countytoxpilyr.addLayer(statepolylyr, "TOP")

    #y["layerDefinitions"][1] = json.loads(layerdef)
    
    
    fh = open(outpathtmp + "\stateToxPi.lyrx", "r")
    data = fh.read()
    y = json.loads(data)
    y["layerDefinitions"][0]["renderer"] = json.loads(renderer)
    y["layerDefinitions"][0]["maxScale"] = "5000000"
    mainlyr = json.dumps(y)
    fh.close()
    fh = open(outpathtmp + "\stateToxPi.lyrx", "w")
    fh.write(mainlyr)
    fh.close()

    statetoxpilyr = arcpy.mp.LayerFile(outpathtmp + "\stateToxPi.lyrx")
    countytoxpilyr.addLayer(statetoxpilyr, "TOP")

    #featureLayer2=arcpy.management.MakeFeatureLayer("https://services.arcgis.com/P3ePLMYs2RVChkJx/arcgis/rest/services/USA_Counties_Generalized/FeatureServer/0", "countypolygons")
    arcpy.management.CopyFeatures("https://services.arcgis.com/P3ePLMYs2RVChkJx/arcgis/rest/services/USA_Counties_Generalized/FeatureServer/0", geopath + "\countypolylayer")
    arcpy.management.AddField(geopath + "\countypolylayer", "ToxPiScore", "Float")
    with arcpy.da.UpdateCursor(geopath+"\countypolylayer", ["STATE_NAME","NAME","ToxPiScore",]) as scur:
        for row in scur:
          if row[0].lower() in list(statedata):
            if row[1].lower() in list(countytoxpidata[row[0].lower()]):
              row[2] = countytoxpidata[row[0].lower()][row[1].lower()]
            scur.updateRow(row)
    featureLayer2=arcpy.management.MakeFeatureLayer(geopath+"\countypolylayer","countypolygons")
    arcpy.management.SaveToLayerFile(featureLayer2, outpathtmp + "\countypolygons")

    fh = open(outpathtmp + "\countypolygons.lyrx", "r")
    data = fh.read()
    y = json.loads(data)
    y["layerDefinitions"][0]["renderer"] = json.loads(rendererbackground)
    y["layerDefinitions"][0]["minScale"] = "5000000"
    mainlyr = json.dumps(y)
    fh.close()
    fh = open(outpathtmp + "\countypolygons.lyrx", "w")
    fh.write(mainlyr)
    fh.close()
    countypolylyr = arcpy.mp.LayerFile(outpathtmp + "\countypolygons.lyrx")
    countytoxpilyr.addLayer(countypolylyr, "BOTTOM")
    countytoxpilyr.save()

    sys.exit()

if __name__ == '__main__':
    ToxPiCreation(sys.argv[1], sys.argv[2])
