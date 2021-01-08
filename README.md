# ToxPi-GIS
Production of shareable, interactive feature layers from the output of the ToxPi GUI  return
Requires ArcGIS Pro license  return

Steps to run from the command line:  return
  Access environment using command:  return
    "%PROGRAMFILES%\ArcGIS\Pro\bin\Python\Scripts\proenv"  return
    Note: If you did a custom installation of ArcGIS Pro this location might be different(ie. not in program files)  return
  Run script with required parameters:  return
    python ToxPiModel.py location\infile location\outfile.lyrx  
    Note: Script will not work without the lyrx extension on the desired output file  
OutPut:  
  Script makes a geodatabase in the outfile path called ToxPiAuto.gdb  
  Script outputs a layer file at location\outfile  
Sharing:  
  Using ArcGIS Pro:  
    Open lyrx file in ArcGIS Pro  
      Double click (or right click and open with) from file explorer  
      Alternatively:  
        Open ArcGIS Pro  
        New Map  
        Add Data  
        Data From Path  
        Insert the path location\outfile.lyrx  
    Click share in top toolbar  
    WebMap  
    Populate with desired parameters and click share  
      Note: To share with those who do not have ArcGIS accounts, set Share With to Everyone  
  From ArcGIS Online: https://www.arcgis.com/home/index.html  
    Sign in to Account  
    Select Content  
    Select the shared web map  
    Obtain sharing id from web URL  
      Ex: https://ncsu.maps.arcgis.com/home/item.html?id=0cbac968eb7544a98761a13ba9b312ec  
      The id is 0cbac968eb7544a98761a13ba9b312ec  
    Sharing this id with anyone allows the to view the map  
Viewing the map using ToxPiGIS: https://toxpi.org/gis/webapp/  
  Select Map  
  Select Web Map  
  Insert id  
  Change Map

    
    
