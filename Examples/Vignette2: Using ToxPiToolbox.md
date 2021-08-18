# Vignette 2: Generating a ToxPi feature layer of COVID-19 vulnerability using ToxPiToolbox.tbx  
Vignette 2 is a demonstration of method 2 in the map creation workflow using [ToxpiToolbox.tbx](https://github.com/Jonathon-Fleming/ToxPi-GIS/blob/main/ToxPiToolbox.tbx) and Covid-19 vulnerability data. The resulting map visually matches Vignette 1, the output of ToxPi_creation.py. The data used in this demonstration was already processed through steps 1A and 1B and can be found [here](https://github.com/Jonathon-Fleming/ToxPi-GIS/tree/main/Examples/Practice%20Data). It is suggested to use the subset as it will significantly reduce running time(Full ~ 30min, Subset ~ 5min). A further description of the data can be found [here](https://www.niehs.nih.gov/research/programs/coronavirus/covid19pvi/details/).  

<p align = "center">
<img src="https://github.com/Jonathon-Fleming/ToxPi-GIS/blob/main/Images/Vignette1.PNG" data-canonical-  
src="https://github.com/Jonathon-Fleming/ToxPi-GIS/blob/main/Images/Vignette1.PNG" width="600" height="300" />  
</p>  

## **Requirements:**  
* ArcGIS Pro licensing  
* Requires being logged into ArcGIS Portal  
* Basic knowledge of ArcGIS tools    
* Source column will likely need to be split into two separate coordinate columns  (See utilities folder for help formatting if needed)  
* Slice names must not contain a special character followed by a number 
  * Note: Special characters will be replaced by underscores in the output due to ArcGIS formatting  
* Windows Operating System   

## **Steps:**  
Note: These are just the steps to create a plain map of ToxPi figures. This methodology should be integrated into modelbuilder, used with extra geoprocessing steps, or used for subsetting of slices, otherwise Method 1 is quicker and produces better results.  
<br>
2A. Already done, download entire repository to get data and scripts     
2B. CSV file already generated [here](https://github.com/Jonathon-Fleming/ToxPi-GIS/tree/main/Examples/Practice%20Data) in repository, but coordinates need to be split into two columns using any preferred method  
   * Split source column using [split_coordinates.py](https://github.com/Jonathon-Fleming/ToxPi-GIS/blob/main/Utilities/split_coordinates.py) and the following command:
     ```
     python location\split_coordinates.py inputfile
     
     Parameters:
     * inputfile - The ToxPi GUI results file that has concatenated coordinates to be split  
     ```
   * Example: 
<p align = "center">  
<img src="https://github.com/Jonathon-Fleming/ToxPi-GIS/blob/main/Images/CommandSplit.PNG" data- canonical-  
src="https://github.com/Jonathon-Fleming/ToxPi-GIS/blob/main/Images/CommandSplit.PNG" width="900" height="35" />  
</p>  

2C. Load results file into an ArcGIS Pro map   
* Open a new project in ArcGIS Pro(Project, New, Map, Change Name, Okay)  
* Add test data to the map(Map, Add Data, PracticeData_Subset_NC.csv)  
<p align = "center">  
<img src="https://github.com/Jonathon-Fleming/ToxPi-GIS/blob/main/Images/AddDataTool.PNG" data- canonical-  
src="https://github.com/Jonathon-Fleming/ToxPi-GIS/blob/main/Images/AddDataTool.PNG" width="600" height="100" />  
</p> 
2D. Load ToxPiToolbox into ArcGIS project  
* Add ToxPiToolbox to project(Insert, Toolbox, Add Toolbox, ToxPiToolbox.tbx)  
<p align = "center">  
<img src="https://github.com/Jonathon-Fleming/ToxPi-GIS/blob/main/Images/AddToolbox.PNG" data- canonical-  
src="https://github.com/Jonathon-Fleming/ToxPi-GIS/blob/main/Images/AddToolbox.PNG" width="750" height="100" />  
</p> 
2E. Run required geoprocessing steps, including ToxPiToolbox, and share to ArcGIS Online  
* Open tool pane to search for tools(Analysis, Tools, Search for tool)  
<p align = "center">  
<img src="https://github.com/Jonathon-Fleming/ToxPi-GIS/blob/main/Images/Tools.PNG" data- canonical-  
src="https://github.com/Jonathon-Fleming/ToxPi-GIS/blob/main/Images/Tools.PNG" width="600" height="100" />  
</p> 
* Display data on the map using a projected coordinate system via the following tool and parameters:  
    Tool: Convert Coordinate Notation  
    Input Table: PracticeData_Subset_NC.csv  
    Input Coordinate System: GCS_WGS_1984  
    Output Feature Class: Vignette2_Displayed  
    Output Coordinate System: WGS_1984_Web_Mercator_Auxiliary_Sphere(Coordinate system needs to be projected, not geographic)  
        Note: To do this, select the globe, search WGS 1984 Web Mercator, drop down projected coordinate systems, drop down world, select WGS 1984 Web Mercator  
    Input Coordinate Format: DD2  
    X: Longitude  
    Y: Latitude  
    Output Coordinate Format: DD2  
 
* Turn on catalog pane(View, Catalog Pane)  
<p align = "center">  
<img src="https://github.com/Jonathon-Fleming/ToxPi-GIS/blob/main/Images/CatalogPane.PNG" data- canonical-  
src="https://github.com/Jonathon-Fleming/ToxPi-GIS/blob/main/Images/CatalogPane.PNG" width="600" height="100" />  
</p>  
* Open custom script called ToxPi Construction from within ToxPiToolbox and run with desired parameters. The interface and parameter descriptions are shown below:  
<p align = "center"> 
<img src="https://github.com/Jonathon-Fleming/ToxPi-GIS/blob/main/Images/ToolInterface.PNG" data-canonical-  
src="https://github.com/Jonathon-Fleming/ToxPi-GIS/blob/main/Images/ToolInterface.PNG" width = "350" height = "500" />  
</p>   
<p align = "center">  
    inFeatures: Input feature layer to draw ToxPi figures from  <br>
    outFeatures: The desired name for the output ToxPi feature layer  <br>
    uniqueID: The column name for the unique identifier for locations  <br>
    inFields: The list of all desired fields to be included as slices  <br>
    inputWeights: A string of weights for determining each slices radial width in order, separated by ;  <br>
    inputRadius: A numerical value for determining the size of the drawn figures. The default is 1  <br>
    outFeaturesRings: The desired name for the max radius ring feature layer(optional) <br>
</p>   
    
 * Complete further analysis or share your map to ArcGIS Online  
<p align = "center">  
<img src="https://github.com/Jonathon-Fleming/ToxPi-GIS/blob/main/Images/MapShare.png" data- canonical-  
src="https://github.com/Jonathon-Fleming/ToxPi-GIS/blob/main/Images/MapShare.png" width="800" height="100" />  
</p>   

## **Output:**    
  * Toolbox generates a symbolized feature layer of ToxPi figures     
  * Sharing provides a web URL for the public to view your map  

## **General Troubleshooting:**   
* Error when running tool   
  * Ensure input feature layer is in a projected coordinate system  
  * Ensure a proper unique identifier is referenced  
  * Ensure the number of slice categories and number of weights provided correspond   
  * Make sure slice names do not contain a special character followed by a number(ArcGIS Pro Tools do not support special characters in fields).
* Mapping Incorrect  
  * Ensure latitude and longitude have been referenced properly in the previous analysis steps. Using concatenated coordinates can lead to issues, thus it is suggested that the coordinates be split into latitude and longitude individually. [split_coordinates.py](https://github.com/Jonathon-Fleming/ToxPi-GIS/blob/main/Utilities/split_coordinates.py) is provided in Utilities folder to help with splitting coordinates  
  * Ensure slices and weights are in proper corresponding order   
  * Ensure basemap coordinate is set to the same coordinate as the output feature layer for the toolbox, else ToxPi figures may be skewed  
  * Slices may need to be renamed due to replacement of special characters with underscores. This can be done using find and replace within an attribute table, however, doing so will cause the symbology to need to be redone. It is suggested just to rename the legend aliases for slices to their proper names     
