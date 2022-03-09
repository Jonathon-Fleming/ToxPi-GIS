import arcpy
import math
import numpy
import os
import json
import pandas as pd
import re
import sys
import argparse

def convertLength(radiusUnits):
    if radiusUnits.upper() == "MAGNIFY":
        return 4000 

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

            # Increment angles only within each unique toxpi
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

def GetSymbology(colors, infields):
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
    return renderer

def GetPopupInfo():
    name = '{Name}'
    title = '"title" : "' + name + '",'
    text = '"text" : "<div><p><span style=\\\"font-weight:bold;\\\">Slice Statistics</span></p><p><span>Name: ' + name + '</span></p><p><span>SliceName: {SliceName}</span></p><p><span>Weight: {Weight}</span></p><p><span>Score: {Score}</span></p>"'
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
          }
        ]
    }'''
    return popupstring

def adjustinput(infile, outfile):
    #prep csv file for input into functions and get required parameters

    #read in csv file, split the coordinates, and replace special characters from the header
    df = pd.read_csv(infile)
    df[['Latitude','Longitude']] = df.Source.str.split(",",expand = True,)
    del df['Source']

    #determine if required columns are present
    if "Name" not in df.columns: #throw an error if names are not present
        print("Error: Name column is not present in the input data. Please add column labeled Name with desired point names.")
        sys.exit()
    uniqueid = "Name"
    uniqueid_index = df.columns.get_loc('Name')

    #add quotes to Name to make sure column reads in as string
    for i in range(len(df["Name"])):
        df.iloc[i, uniqueid_index] = "\"" + str(df.iloc[i, uniqueid_index]) + "\"" 

    #get required symbology parameters and slices from column headers
    colors = []
    weights = []
    infields = []
    infieldsrevised = []
    keywords = ["ToxPi Score", "HClust Group", "KMeans Group", "Name", "Longitude","Latitude","FIPS", "Tract","casrn"]
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
                        infields.append(name[:weightstartpos])
                        infieldsrevised.append(re.sub('\W+','_', name[:weightstartpos]))
                        if infieldsrevised[-1][0].isdigit(): 
                            infieldsrevised[-1] = "F" + infieldsrevised[-1]
                        df.rename(columns = {name:name[:weightstartpos]}, inplace = True) 
                    else:
                        weightendpos = i
                        weights.append(float(name[weightstartpos + 1: weightendpos]))   
    df.columns = [re.sub('\W+','_', header) for header in df.columns]             
    df.to_csv(outfile, index=False)
    return weights, colors, infields, infieldsrevised

def getBoundaryLayer(extent, geopath):
  #if extent == "censusBlock":
  #  link = ""
  #if extent == "blockGroup":
  #  link = ""
  if extent == "censusTract":
    link = "https://services1.arcgis.com/aT1T0pU1ZdpuDk1t/arcgis/rest/services/USA_Census_Tract_Boundaries/FeatureServer/0"
  elif extent == "county":
    link = "https://services.arcgis.com/P3ePLMYs2RVChkJx/arcgis/rest/services/USA_Counties_Generalized/FeatureServer/0"
  elif extent == "state":
    link = "https://services.arcgis.com/P3ePLMYs2RVChkJx/arcgis/rest/services/USA_States_Generalized/FeatureServer/0"
  elif extent == "division":
    link = "https://services1.arcgis.com/aT1T0pU1ZdpuDk1t/arcgis/rest/services/USA_Divisions_2018/FeatureServer/0"
  elif extent == "region":
    link = "https://services1.arcgis.com/aT1T0pU1ZdpuDk1t/arcgis/rest/services/USA_Regions_2018/FeatureServer/0"
  #if extent == "nation":
  #  link = ""
  else:
    print(extent, " is an invalid boundary layer or is not supported.")
    return ""

  boundaries = arcpy.management.CopyFeatures(link, geopath + r"\boundarylayer")

  return boundaries
  

def ToxPiFeatures(inFeatures, outFeatures, uniqueID, inFields, inputRadius, radiusUnits, inputWeights, inFieldsrename, geopath):
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
        tmpFeatures = arcpy.management.CreateFeatureclass(geopath,
                                                          outTmp,
                                                          'POINT',
                                                          spatial_reference=sr)
        # Add field selected as the unique identifier.
        field_obj = arcpy.ListFields(inFeatures, uniqueID)
        arcpy.AddField_management(tmpFeatures,
                                  field_obj[0].name,
                                  field_type = field_obj[0].type,
                                  field_length = field_obj[0].length,
                                  field_alias = field_obj[0].aliasName)

        # Add fields to store bearings and radius.
        arcpy.AddField_management(tmpFeatures, "Score", "DOUBLE")
        arcpy.AddField_management(tmpFeatures, "SliceName", "TEXT")
        arcpy.AddField_management(tmpFeatures, "Weight", "TEXT")
        arcpy.AddField_management(tmpFeatures, "CLASS_", "LONG")
        arcpy.AddField_management(tmpFeatures, "BEARING_a", "FLOAT")
        arcpy.AddField_management(tmpFeatures, "BEARING_b", "FLOAT")
        arcpy.AddField_management(tmpFeatures, "RADIUS_", "FLOAT")

        # Insert pivoted data from input Feature Class.
        with arcpy.da.SearchCursor(inFeatures, ['SHAPE@XY', uniqueID] + inFields) as scur:
            for i, row in enumerate(scur):
                count = 0
                x1,y1 = row[0]
                id_ = row[1]
                for j, f in enumerate(inFields):
                    weight = str(round(inputWeights[count]*100/360, 3)) + "%"
                    v = row[count+2]
                    count = count + 1
                    with arcpy.da.InsertCursor(tmpFeatures, ('Shape@', uniqueID,"Score","SliceName","Weight","CLASS_")) as poly_cursor:
                        poly_cursor.insertRow(([x1,y1],id_,v,inFieldsrename[j],weight,count))

        # Find the max values to scale the output features
        if inputRadius == "" or inputRadius == 0:
            inputRadius = 1
        maxRadius = math.sqrt(1/math.pi)
        convMax = float(maxRadius) * float(sr.metersPerUnit)
        radiusUnits = "Magnify"
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
        # Get all attribute fields.
        search_fields = [f.name for f in arcpy.ListFields(tmpFeatures)]

       # Get the locations in the list for bearings and radius.
        bearing_a_loc = search_fields.index("BEARING_a")+1
        bearing_b_loc = search_fields.index("BEARING_b")+1
        radius_loc = search_fields.index("RADIUS_")+1

        # Process: Calculate bearings and radii
        bearings(tmpFeatures, uniqueID, inputWeights, float(scaler))

        # Report progress for each toxpi.
        cnt = arcpy.management.GetCount(tmpFeatures)
        increment = int(int(cnt[0]) / 10.0)
        arcpy.SetProgressor("Step", "Creating ToxPi Figures...",  0, int(cnt[0]), increment)

        # Create toxpi figures, polygon sector at a time.
        with arcpy.da.SearchCursor(tmpFeatures, ['SHAPE@XY'] + search_fields + ['OID@']) as scur:
            for i, row in enumerate(scur):
                if (i % increment) == 0:
                    arcpy.SetProgressorPosition(i + 1)

                # Get the fields that hold the bearings and radius information.
                x1, y1 = row[0]
                b_a = row[bearing_a_loc]
                b_b = row[bearing_b_loc]
                radius = row[radius_loc]

                # Create the toxpi polygons.
                with arcpy.da.InsertCursor(tox_polys, ['SHAPE@'] + search_fields[2:]) as poly_cursor:
                    l = len(search_fields) + 1
                    if (i+1)%(len(inFields)) == 0:
                        poly_cursor.insertRow([arcpy.Polygon(create_sector(arcpy.Point(x1, y1), innerradius, 360, 0, 0, ring=True), sr,),] + list(row[3:l]))
                    else:
                        if radius != 0:
                            poly_cursor.insertRow([arcpy.Polygon(create_sector(arcpy.Point(x1, y1), radius, int(b_a), int(b_b), innerradius, ring=False), sr,),] + list(row[3:l]))

            arcpy.SetProgressorPosition(100)
            del poly_cursor
        del scur, row
        arcpy.Delete_management(tmpFeatures)
        outFeaturesRings = outFeatures + "Rings"
        outFolder = os.path.dirname(outFeaturesRings)
        outName = os.path.basename(outFeaturesRings)
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
                del poly_cursor
            del scur, row
        #renderer = GetSymbology(colors, inFields)
        #arcpy.SetParameterSymbology(1,f"JSONRENDERER={renderer}")
        
    except arcpy.ExecuteError:
        print (arcpy.GetMessages(2))
        sys.exit()

def ToxPiCreation(args):

    inFeatures = args.inFeatures
    outFeatures = args.outFeatures
    inputRadius = args.scaler
    extent = args.extent
    labels = args.labels

    #import toolboxes for use
    arcpy.ImportToolbox(r"c:\program files\arcgis\pro\Resources\ArcToolbox\toolboxes\Conversion Tools.tbx")
    arcpy.ImportToolbox(r"c:\program files\arcgis\pro\Resources\ArcToolbox\toolboxes\Data Management Tools.tbx")
    
    # To allow overwriting outputs change overwriteOutput option to True.
    arcpy.env.overwriteOutput = True

    outpathtmp = os.path.dirname(outFeatures)
    if not os.path.exists(outpathtmp):
        os.makedirs(outpathtmp)

    geopath = outpathtmp + "\ToxPiAuto.gdb"
    if not os.path.exists(geopath):
        arcpy.CreateFileGDB_management(str(outpathtmp), "ToxPiAuto.gdb")

    #adjust input file for required parameters and get required information
    print("Preprocessing Data...")
    outfilecsv = outpathtmp + "\ToxPiResultsAdjusted.csv"
    inweights, colors, infields, infieldsrevised = adjustinput(inFeatures, outfilecsv)

    uniqueid = "Name"
    #adjust weights to fit a circle (360 deg)
    total = 0
    for i in range(len(inweights)):
      total = total + inweights[i]
    for i in range(len(inweights)):
      inweights[i] = float(inweights[i]*360/total)

    #append info for adding a center dot with overall score
    inweights.append(360)
    colors.append("FFFFFF")
    infields.append("ToxPi Score")
    infieldsrevised.append("ToxPi_Score")
    
    #get color rgb codes from hex codes
    for j in range(len(colors)):
        colors[j] = tuple(int(colors[j][i:i+2], 16) for i in (0, 2, 4))

    #Convert coordinates to projected instead of geographic and output to a feature layer
    print("Mapping Coordinates...")
    tmpfileremapped = geopath + "\pointfeatureremapped"
    arcpy.ConvertCoordinateNotation_management(in_table=outfilecsv, out_featureclass=tmpfileremapped, x_field="Longitude", y_field="Latitude", input_coordinate_format="DD_2", output_coordinate_format="DD_2", spatial_reference="PROJCS['WGS_1984_Web_Mercator_Auxiliary_Sphere',GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137.0,298.257223563]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Mercator_Auxiliary_Sphere'],PARAMETER['False_Easting',0.0],PARAMETER['False_Northing',0.0],PARAMETER['Central_Meridian',0.0],PARAMETER['Standard_Parallel_1',0.0],PARAMETER['Auxiliary_Sphere_Type',0.0],UNIT['Meter',1.0]];-20037700 -30241100 10000;-100000 10000;-100000 10000;0.001;0.001;0.001;IsHighPrecision", in_coor_system="GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137.0,298.257223563]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]]", id_field="", exclude_invalid_records="INCLUDE_INVALID")

    #remove quotes used to force identifier to a string
    with arcpy.da.UpdateCursor(tmpfileremapped, [uniqueid] + infieldsrevised) as scur:
        for row in scur:
          row[0] = row[0].replace("\"","")
          n = len(row)
          for i in range(1,n):
            row[i] = round(row[i], 3)
          scur.updateRow(row)

    tmpfileToxPi = geopath + "\ToxPifeature"
    print("Drawing ToxPi Profiles...")
    ToxPiFeatures(inFeatures=tmpfileremapped, outFeatures=tmpfileToxPi, uniqueID = "Name", inFields=infieldsrevised, inputRadius=float(inputRadius), radiusUnits="Magnify", inputWeights=inweights, inFieldsrename = infields, geopath = geopath)
    
    countytoxpilyr = arcpy.management.MakeFeatureLayer(tmpfileToxPi, "ToxPi Features")
    arcpy.management.SaveToLayerFile(countytoxpilyr, outFeatures)
    
    #open county toxpi feature layer file for editing
    print("Symbolizing ToxPi Profiles...")
    fh = open(outFeatures, "r")
    data = fh.read()
    y = json.loads(data)

    #alter symbology for toxpi feature layer
    y["layerDefinitions"][0]["renderer"] = json.loads(GetSymbology(colors, infields))
    y["layerDefinitions"][0]["popupInfo"] = json.loads(GetPopupInfo())
    #write the edits to the county toxpi layer file
    mainlyr = json.dumps(y)
    fh.close()
    fh = open(outFeatures, "w")
    fh.write(mainlyr)
    fh.close()

    finallyr = arcpy.mp.LayerFile(outFeatures)

    outFeaturesRings = tmpfileToxPi + "Rings"
    countytoxpilyrrings = arcpy.management.MakeFeatureLayer(outFeaturesRings, "ToxPi Rings")
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
    
    if extent != "":
      boundaries = getBoundaryLayer(extent, geopath)
      if boundaries !="":
        print("Downloading Boundary Layer...")
        #boundarylyr= arcpy.management.MakeFeatureLayer(boundaries, "BoundaryLayer")
        boundarylyr_partial = arcpy.management.SelectLayerByLocation(boundaries, overlap_type = "CONTAINS", select_features = countytoxpilyr)
        arcpy.management.CopyFeatures(boundarylyr_partial, geopath + r"\boundaries")
        boundarylyr=arcpy.management.MakeFeatureLayer(geopath + r"\boundaries","Boundaries")
        arcpy.management.SaveToLayerFile(boundarylyr, outpathtmp + r"\BoundaryLyr.lyrx")
        
        print("Symbolizing Boundary Layer...")
        fh = open(outpathtmp + r"\BoundaryLyr.lyrx", "r")
        data = fh.read()
        y = json.loads(data)

        y["layerDefinitions"][0]["renderer"]["symbol"]["symbol"]["symbolLayers"][1]["color"]["values"][0] = "156"
        y["layerDefinitions"][0]["renderer"]["symbol"]["symbol"]["symbolLayers"][1]["color"]["values"][1] = "156"
        y["layerDefinitions"][0]["renderer"]["symbol"]["symbol"]["symbolLayers"][1]["color"]["values"][2] = "156"
        y["layerDefinitions"][0]["renderer"]["symbol"]["symbol"]["symbolLayers"][1]["color"]["values"][3] = "50"  
        #write the edits to the county toxpi layer file
        mainlyr = json.dumps(y)
        fh.close()
        fh = open(outpathtmp + r"\BoundaryLyr.lyrx", "w")
        fh.write(mainlyr)
        fh.close()

        boundaryobject = arcpy.mp.LayerFile(outpathtmp + r"\BoundaryLyr.lyrx")
        finallyr.addLayer(boundaryobject, "TOP")

        os.remove(outpathtmp + r"\BoundaryLyr.lyrx")
    
    finallyr.save()
    os.remove(outpathtmp + r"\ToxPiResultsAdjusted.csv")
    os.remove(outpathtmp + r"\rings.lyrx")

    if labels == "True":
      print("Adding Labels...")
      fh = open(outFeatures, "r")
      data = fh.read()
      y = json.loads(data)

      y["layerDefinitions"][-1]["labelClasses"][0]["maplexLabelPlacementProperties"]["constrainOffset"] = "LeftOfLine"
      y["layerDefinitions"][-1]["labelClasses"][0]["maplexLabelPlacementProperties"]["linePlacementMethod"] = "OffsetCurvedFromLine"
      y["layerDefinitions"][-1]["labelClasses"][0]["maplexLabelPlacementProperties"]["primaryOffset"] = "3"
      y["layerDefinitions"][-1]["labelClasses"][0]["maplexLabelPlacementProperties"]["allowStraddleStacking"] = "true"
      y["layerDefinitions"][-1]["labelVisibility"] = "true"

      #write the edits to the county toxpi layer file
      mainlyr = json.dumps(y)
      fh.close()
      fh = open(outFeatures, "w")
      fh.write(mainlyr)
      fh.close()

if __name__ == '__main__':
  parser = argparse.ArgumentParser(description='Make ToxPi Layer Files')
  parser.add_argument('inFeatures', type = str, help = 'Path for input feature excel file')
  parser.add_argument('outFeatures', type = str, help = 'Path for output layer file')
  parser.add_argument('--scaler', default = 1.0, help = 'Provide a scaler value to resize ToxPi profiles(default = 1.0)')
  parser.add_argument('--extent', default = "", help = 'Provide a name for a boundary layer to include')
  parser.add_argument('--labels', default = False, help = 'Set to True if labels are desired on ToxPi Profiles')
  args = parser.parse_args()
  ToxPiCreation(args)
