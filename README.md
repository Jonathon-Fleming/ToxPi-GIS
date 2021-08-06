# ToxPi-GIS
**GitHub Description:**  
The following methods are used for the production and visualization of shareable, interactive feature layers containing ToxPi features using ArcGIS Pro. Two methods are provided for production, labeled as 1 and 2 in the Map Creation Workflow located below. Method 1 uses a customized python script that can be run on the Windows Command Prompt to automatically produce a predesigned layer file of ToxPi features symbolized based on the ToxPi GUI output that can be opened within ArcGIS Pro and is ready to be shared to ArcGIS Online for visualization. It is suggested to use this method if you are not integrating the ToxPi features into a fully automated ArcGIS model. Examples of this process can be seen under Vignette 1 and Vignette 3 located within the [Example Folder Map Creation file](https://github.com/Jonathon-Fleming/ToxPi-GIS/blob/main/Examples/Map%20Creation.md). For users looking to integrate ToxPi feature layers into already existing workflows or ArcGIS models, method 2 is provided which uses a custom ArcToolbox that can be added to ArcGIS Pro and used to produce symbolized ToxPi features. Use this method if you want to develop your own pipeline within ArcGIS Pro, your data does not fit the formatting required for use of the python script, or you only want to use a subset of the slices in your data. Examples of this process can be seen under Vignette 2 within the [Example Folder Map Creation file](https://github.com/Jonathon-Fleming/ToxPi-GIS/blob/main/Examples/Map%20Creation.md). If you are a user looking only to visualize maps created by other users, please see the Visualization section below and the examples within the [Example Folder Map Visualization file](https://github.com/Jonathon-Fleming/ToxPi-GIS/blob/main/Examples/Map%20Visualization.md). Practice data can be found within the [Example Folder Practice Data Folder](https://github.com/Jonathon-Fleming/ToxPi-GIS/tree/main/Examples/Practice%20Data).  
  
**ToxPi Description:**  
(insert description and images of ToxPi Figures and statistics here).  
  
**Map Creation Workflow:**  
<p align = "center">
<img src="https://github.com/Jonathon-Fleming/ToxPi-GIS/blob/main/Images/MapCreationWorkflow.PNG" data-canonical-  
src="https://github.com/Jonathon-Fleming/ToxPi-GIS/blob/main/Images/MapCreationWorkflow.PNG" width="600" height="300" />  
</p>  
  
**Script Instructions(Path 1): ToxPiCreation.py**   
Use the script ToxPiCreation.py to automatically produce predesigned feature layers containing interactive ToxPi features using the output of the ToxPi GUI as input. This is the suggested method, unless you are skilled with ArcGIS Pro and have a specific need for a Toolbox.

Requirements: 
* ArcGIS Pro licensing  
* Source column for data must be formatted Latitude, Longitude(See Utilites Folder section for help if coordinate format needs to be swapped)
* Requires being logged into ArcGIS Portal  
* Column labeled Name with unique identifiers must be present in data  
* Slice names must not contain a special character followed by a number  
* Windows Operating System  
* Lyrx file must be output to a separate location folder for new maps, else it will overwrite the previous map layers within the geodatabase  

Steps:  
1A. Load raw data into the [ToxPi GUI](https://toxpi.org/)  
1B. Analyze data and output results file to a CSV, and make sure file meets requirements above  
1C. Run [ToxPiCreation.py](https://github.com/Jonathon-Fleming/ToxPi-GIS/blob/main/ToxPiCreation.py) from windows command prompt using the following commands and parameters
```
"%PROGRAMFILES%\ArcGIS\Pro\bin\Python\Scripts\proenv" (Used to load ArcGIS Pro environment)  
python location\ToxPiCreation.py inputfile outputfile.lyrx scale (Used to run script, replace location with path to file)  

Parameters:
* inputfile - The ToxPi GUI results file to draw ToxPi features from  
* outputfile.lyrx - The location for the result lyrx file output by the script. Please use full file path and add .lyrx  
* scale - Optionally scales the size of the ToxPi features. The default is 1  
```

Example:  
<p align = "center">
<img src="https://github.com/Jonathon-Fleming/ToxPi-GIS/blob/main/Images/ExampleCommand.PNG" data-canonical-  
src="https://github.com/Jonathon-Fleming/ToxPi-GIS/blob/main/Images/ExampleCommand.PNG" width="900" height="75" />  
</p>  

1D. Open output layer file in ArcGIS Pro  
1E. Share resulting map to ArcGIS Online  

Output:  
  * Script makes a geodatabase in the location folder called ToxPiAuto.gdb  
  * Script outputs a layer file at location\outfile.lyrx  
  * Sharing provides a web URL for the public to view your map  

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

Requirements: 
* ArcGIS Pro licensing  
* Requires being logged into ArcGIS Portal  
* Basic knowledge of ArcGIS tools    
* Source column will likely need to be split into two separate coordinate columns  
* Windows Operating System  
* Use of other tools for data manipulation and feature layer preparation. Example walkthrough is provided under Vignette 3 located within the [Example Folder Map Creation file](https://github.com/Jonathon-Fleming/ToxPi-GIS/blob/main/Examples/Map%20Creation.md) to help with this.  

Steps:  
2A. Load raw data into the [ToxPi GUI](https://toxpi.org/)  
2B. Analyze data and output results file to a CSV  
2C. Add results file to ArcGIS Pro  
2D. Add ToxPiToolbox.tbx to ArcGIS Pro  
2E. Run required analysis steps including the ToxPi tool and share resulting map to ArcGIS Online(See [Map Creation Examples](https://github.com/Jonathon-Fleming/ToxPi-GIS/blob/main/Examples/Map%20Creation.md) Vignette 3 for analysis steps)  
  
Output:  
  * Toolbox generates an unsymbolized feature layer of ToxPi figures     
  * Sharing provides a web URL for the public to view your map  

General Troubleshooting:  
* Error when running tool   
  * Ensure input feature layer is in a projected coordinate system  
  * Ensure a proper unique identifier is referenced  
  * Ensure the number of slice categories and number of weights provided correspond   
  * Make sure slice names do not contain a special character followed by a number(ArcGIS Pro Tools do not support special characters in fields).
* Mapping Incorrect  
  * Ensure latitude and longitude have been referenced properly in the previous analysis steps. Using concatenated coordinates can lead to issues, thus it is suggested that the coordinates be split into latitude and longitude individually. [split_coordinates.py](https://github.com/Jonathon-Fleming/ToxPi-GIS/blob/main/Utilities/Split_Coordinates.py) is provided in Utilities folder to help with splitting coordinates  
  * Ensure slices and weights are in proper corresponding order   
  * Ensure an equidistant coordinate system is used and basemap coordinate is set properly, else ToxPi figures may be skewed  

**Utilities Folder:**  
This folder contains python scripts that may be useful for data manipulation and formatting requirements. They can be run by changing the input and output file path within the script to reference the file to be altered and then running the script. A possible path to edit these files consists of opening notepad(or another text editor) and navigating to the file location for the script. Ensure all files is selected if the file can't be seen, and then open the file in notepad and edit the two file paths present.  

**Visualization Instructions:**  
(Discuss paths here, need to finalize what these are and the best way to present these)

**Temporary Stuff that was left in case its useful for other sections, will be deleted when done or used elsewhere**  

**Viewing Options:**  
ArcGIS Viewing Path:  
* Go to shared web link  
* Select Open in Map Viewer  

ToxPi Viewing Path: https://toxpi.org/gis/webapp/  
  * Select Map  
  * Select Web Map  
  * Insert id at end of shared web url  
  * Change Map  



    
    
