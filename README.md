# ToxPi-GIS
Production of shareable, interactive feature layers from the output of the ToxPi GUI  return
Requires ArcGIS Pro license  return

Steps to run from the command line:  return
  Access environment using command:  return
    "%PROGRAMFILES%\ArcGIS\Pro\bin\Python\Scripts\proenv"  return
    Note: If you did a custom installation of ArcGIS Pro this location might be different(ie. not in program files)  return
  Run script with required parameters:  return
    python ToxPiModel.py location\infile location\outfile.lyrx  return
    Note: Script will not work without the lyrx extension on the desired output file  return
OutPut:  return
  Script makes a geodatabase in the outfile path called ToxPiAuto.gdb  return
  Script outputs a layer file at location\outfile  return
Sharing:  return
  Using ArcGIS Pro:  return
    Open lyrx file in ArcGIS Pro  return
      Double click (or right click and open with) from file explorer  return
      Alternatively:  return
        Open ArcGIS Pro  return
        New Map  return
        Add Data  return
        Data From Path  return
        Insert the path location\outfile.lyrx  return
    Click share in top toolbar  return
    WebMap  return
    Populate with desired parameters and click share  return
      Note: To share with those who do not have ArcGIS accounts, set Share With to Everyone  return
  From ArcGIS Online: https://www.arcgis.com/home/index.html  return
    Sign in to Account  return
    Select Content  return
    Select the shared web map  return
    Obtain sharing id from web URL  return
      Ex: https://ncsu.maps.arcgis.com/home/item.html?id=0cbac968eb7544a98761a13ba9b312ec  return
      The id is 0cbac968eb7544a98761a13ba9b312ec  return
    Sharing this id with anyone allows the to view the map  return
Viewing the map using ToxPiGIS: https://toxpi.org/gis/webapp/  return
  Select Map  return
  Select Web Map  return
  Insert id  return
  Change Map  return

    
    
