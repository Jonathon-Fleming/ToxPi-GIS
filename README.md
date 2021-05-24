# ToxPi-GIS
Production of shareable, interactive feature layers from the output of the ToxPi GUI   
Examples of the process are contained in the Examples folder  

Important Notes:  
* Requires ArcGIS Pro license and download, and must be logged into ArcGIS software    
* Script currently only for use with USA data, tool is universal  
* Source column expected to be formatted Latitude, Longitude for script, script is provided in utilites called swap_coordinates.py to swap coordinate format if Longitude, Latitude
* Name column required for script  
* Each time script is run to generate a map a different directory should be used unless overwriting a previous map    
* Special Steps are required to run with mac or linux  

**Workflow:**  
<p align = "center">
<img src="https://github.com/Jonathon-Fleming/ToxPi-GIS/blob/main/Images/Workflow.PNG" data-canonical-  
src="https://github.com/Jonathon-Fleming/ToxPi-GIS/blob/main/Images/Workflow.PNG" width="600" height="300" />  
</p>  

1. Use the [ToxPi GUI](https://toxpi.org/) to analyze your data and obtain an output csv file.  
2. Run ToxPi_Model.py using the ToxPi output. Alternatively, experienced ArcGIS users may use ToxPiToolbox.tbx from within ArcGIS Pro for size customization and a single layer of ToxPi figures.  
3. Open the resulting layer file in ArcGIS Pro and share the layer files as a web map to ArcGIS Online publically.  
4. Obtain the shareable web link for the hosted layer from ArcGIS Online, which anyone can use to view the layer.  

**Script Instructions:**   
Steps to run from windows command prompt:  
* Access environment using command:  
  * "%PROGRAMFILES%\ArcGIS\Pro\bin\Python\Scripts\proenv"  
  * Notes:  
    * Quotes are required.  
    * If you did a custom installation of ArcGIS Pro this location might be different(ie. not in program files)  
* Run script with required parameters:  
  * python ToxPi_Model.py location\infile location\outfile.lyrx
  * If location is your current directoy, replace location with .
  * Note: Script will not work without the lyrx extension on the desired output file  
  
OutPut:  
  * Script makes a geodatabase in the outfile path called ToxPiAuto.gdb  
  * Script outputs a layer file at location\outfile  

**Alternate ToolBox Instructions:**  
The ToxPiToolbox.tbx file contains a custom tool called ToxPi Construction for drawing the polygons that make up ToxPi figures. It requires more manual steps than the script; however, a model can be created for the automation of layers for specific data, and the toolbox allows for more customization than the script, including size of ToxPi figures. This, along with a walkthrough example, are described under Vignette 3 in the Examples section.

**Sharing Instructions:**   
* Using ArcGIS Pro:  
  * Open lyrx file in ArcGIS Pro  
    * Double click (or right click and open with) from file explorer  
    * Alternatively:  
      * Open ArcGIS Pro  
      * New Map  
      * Add Data  
      * Data From Path  
      * Insert the path location\outfile.lyrx  
  * Click share in top toolbar  
  * WebMap  
  * Populate with desired parameters and click share  
    * Note: To share with those who do not have ArcGIS accounts, set Share With to Everyone  
* From [ArcGIS Online:](https://www.arcgis.com/home/index.html)   
  * Sign in to Account  
  * Select Content  
  * Select the shared web map  
  * Obtain web URL  
    * Ex: [https://ncsu.maps.arcgis.com/home/item.html?id=0cbac968eb7544a98761a13ba9b312ec](https://ncsu.maps.arcgis.com/home/item.html?id=0cbac968eb7544a98761a13ba9b312ec)  
  * Sharing this with anyone allows them to view the map via opening in web viewer  

**Viewing Options:**  
ArcGIS Viewing Path:  
* Go to shared web link  
* Select Open in Map Viewer  

ToxPi Viewing Path: https://toxpi.org/gis/webapp/  
  * Select Map  
  * Select Web Map  
  * Insert id at end of shared web url  
  * Change Map  

**Utilities Folder:**  
This folder contains python scripts that may be useful for data manipulation and formatting requirements. They can be run by changing the file path within the script to reference the file to be altered and then running the script.  

    
    
