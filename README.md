# ToxPi-GIS
**GitHub Description:**  
The following methods are used for the production and visualization of shareable, interactive feature layers containing ToxPi features using ArcGIS Pro. Two methods are provided for production, labeled as 1 and 2 in the Map Creation Workflow located below. Method 1 uses a customized python script that can be run on the Windows Command Prompt to automatically produce a predesigned layer file of ToxPi features symbolized based on the ToxPi GUI output that can be opened within ArcGIS Pro and is ready to be shared to ArcGIS Online for visualization. The script is currently only compatible with USA data. Examples of this process can be seen under Vignette 1 and Vignette 2 located within the [Example Folder Map Creation file](https://github.com/Jonathon-Fleming/ToxPi-GIS/blob/main/Examples/Map%20Creation.md). For users looking for a more customizable experience, method 2 is provided which uses a custom ArcToolbox that can be added to ArcGIS Pro and used to produce unsymbolized ToxPi features. Use this method if you want customizability in ToxPi feature size or number of layers output, want to develop your own pipeline within ArcGIS Pro, your data does not fit the formatting required for use of the python script, or you have non USA data. Examples of this process can be seen under Vignette 3 within the [Example Folder Map Creation file](https://github.com/Jonathon-Fleming/ToxPi-GIS/blob/main/Examples/Map%20Creation.md). If you are a user looking only to visualize maps created by other users, please see the Visualization section below and the examples within the [Example Folder Map Visualization file](https://github.com/Jonathon-Fleming/ToxPi-GIS/blob/main/Examples/Map%20Visualization.md). Practice data can be found within the [Example Folder Practice Data Folder](https://github.com/Jonathon-Fleming/ToxPi-GIS/tree/main/Examples/Practice%20Data).  
  
**ToxPi Description:**  
(insert description and images of ToxPi Figures and statistics here).  
  
**Map Creation Workflow:**  
<p align = "center">
<img src="https://github.com/Jonathon-Fleming/ToxPi-GIS/blob/main/Images/MapCreationWorkflow.PNG" data-canonical-  
src="https://github.com/Jonathon-Fleming/ToxPi-GIS/blob/main/Images/MapCreationWorkflow.PNG" width="600" height="300" />  
</p>  
  
**Script Instructions(Path 1):**   
Use the script to automatically produce predesigned feature layers containing interactive ToxPi features using the output of the ToxPi GUI as input.  

Steps:  
1A. Load raw data into the [ToxPi GUI](https://toxpi.org/)  
1B. Analyze data and output results file to a CSV  
1C. Run [ToxPi_Model.py](https://github.com/Jonathon-Fleming/ToxPi-GIS/blob/main/ToxPi_Model.py) from windows command prompt using the following commands and the ToxPi GUI CSV output as input  
```
"%PROGRAMFILES%\ArcGIS\Pro\bin\Python\Scripts\proenv" (Used to load ArcGIS Pro environment)  
python ToxPi_Model.py location\infile.csv location\outfile.lyrx (Used to run script)
```
1D. Open output layer file in ArcGIS Pro  
1E. Share resulting map to ArcGIS Online  

Output:  
  * Script makes a geodatabase in the location folder called ToxPiAuto.gdb  
  * Script outputs a layer file at location\outfile.lyrx  
  * Sharing provides a web URL for the public to view your map  

Requirements: 
* ArcGIS Pro licensing  
* Requires being logged into ArcGIS Portal  
* Data must be limited to the USA  
* Source column for data must be formatted Latitude, Longitude  
* Column labeled Name must be present in data  
* Windows Operating System  
* Lyrx file must be output to a separate location folder for new maps, else it will overwrite the previous map layers within the geodatabase  

General Troubleshooting:  
* Error when accessing environment  
  * Make sure quotes are included  
  * The location to the proenv may be different if you did a custom installation location of ArcGIS Pro  
* Error when running script  
  * If location is your current directory, replace the location with a .  
  * Make sure .lyrx is present on outfile   
  * Make sure you are logged into ArcGIS Portal and have required ArcGIS Pro licensing  
  * Make sure nonessential columns are not present in data  
* Mapping Incorrect
  * Ensure source is formatted latitude, longitude. [swap_coordinates.py](https://github.com/Jonathon-Fleming/ToxPi-GIS/blob/main/Utilities/Swap_Coordinates.py) is provided in Utilities folder if coordinates need to be swapped  
  * Each time script is run to generate a map a different directory should be used unless overwriting a previous map     
  
  
**ArcToolBox Instructions(Path 2):**  
The ToxPiToolbox.tbx file contains a custom tool called ToxPi Construction for drawing the polygons that make up ToxPi figures. It requires more manual steps than the script; however, a model can be created for the automation of layers for specific data, and the toolbox allows for more customization than the script, including size of ToxPi figures. This, along with a walkthrough example, are described under Vignette 3 located within the [Example Folder Map Creation file](https://github.com/Jonathon-Fleming/ToxPi-GIS/blob/main/Examples/Map%20Creation.md).  

Steps:  
2A. Load raw data into the [ToxPi GUI](https://toxpi.org/)  
2B. Analyze data and output results file to a CSV  
2C. Add results file to ArcGIS Pro  
2D. Add ToxPiToolbox.tbx to ArcGIS Pro  
2E. Run required analysis steps including the ToxPi tool, symbolize the layer, and share resulting map to ArcGIS Online  
  
Output:  
  * Toolbox generates an unsymbolized feature layer of ToxPi figures     
  * Sharing provides a web URL for the public to view your map  

Requirements: 
* ArcGIS Pro licensing  
* Requires being logged into ArcGIS Portal  
* Basic knowledge of ArcGIS tools    
* Source column will likely need to be split into two separate coordinate columns  
* Windows Operating System  
* Use of other tools for data manipulation and feature layer preparation. Example walkthrough is provided under Vignette 3 located within the [Example Folder Map Creation file](https://github.com/Jonathon-Fleming/ToxPi-GIS/blob/main/Examples/Map%20Creation.md) to help with this.  

General Troubleshooting:  
* Error when running tool   
  * Ensure input feature layer is in a projected coordinate system  
  * Ensure a proper unique identifier is referenced  
  * Ensure the number of slice categories and number of weights provided correspond   
* Mapping Incorrect  
  * Ensure latitude and longitude have been referenced properly in the previous analysis steps. Using concatenated coordinates can lead to issues, thus it is suggested that the coordinates be split into latitude and longitude individually. [split_coordinates.py](https://github.com/Jonathon-Fleming/ToxPi-GIS/blob/main/Utilities/Split_Coordinates.py) is provided in Utilities folder to help with splitting coordinates  
  * Ensure slices and weights are in proper corresponding order   
  * Ensure an equidistant coordinate system is used and basemap coordinate is set properly, else ToxPi figures may be skewed  

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

    
    
