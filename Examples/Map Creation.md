# Description
All Vignettes use data from ... insert more info about the data, where it comes from, why it is new, and how it is different  
Add a nice image of slices and a legend for the slice info  

# Vignette 1: Using county or census tract data with FIPS
Description: Use this method with county or census tract data to automatically generate a layer file containing multiple layers that follow the predefined template and symbology shown in the example images below, as well as provide both state and local statistics   
**Steps:**
* Download the root repository
* Run the script using the vignette 1 subset test data(partial dataset will take roughly 5 minutes whereas entire dataset will be over an hour)  
    python ToxPi_Model.py Examples\PracticeData\Vignette1_Subset_NC.csv Examples\Output\Vignette1\Vignette1.lyrx  
    
    Note: Script will produce ouput folder and vignette1 folder if they are not present  
* Open Vignette1.lyrx in ArcGIS Pro and share as a web map to ArcGIS Online
<img src="https://github.com/Jonathon-Fleming/ToxPi-GIS/blob/main/Images/MapShare.png" data-canonical-  
src="https://github.com/Jonathon-Fleming/ToxPi-GIS/blob/main/Images/MapShare.png">
* Obtain web link from ArcGIS Online via selecting the map in My Content and copying the URL or [view previously hosted map](https://ncsu.maps.arcgis.com/home/webmap/viewer.html?useExisting=1&layers=27e222bd708a45deb10186eccd96bb77)  
<img src="https://github.com/Jonathon-Fleming/ToxPi-GIS/blob/main/Images/WebLink.PNG" data-canonical-  
src="https://github.com/Jonathon-Fleming/ToxPi-GIS/blob/main/Images/WebLink.PNG">    
* Optionally, edit descriptive elements and metadata for public viewing

**Map Details:**  
Multilayer visualization  
State median statistics
Choropleth colored by ToxPi score  
Interactive slices with custom popups  
Colored slices based on ToxPi GUI choices  
<img src="https://github.com/Jonathon-Fleming/ToxPi-GIS/blob/main/Images/StateLayer.PNG" data-canonical-  
src="https://github.com/Jonathon-Fleming/ToxPi-GIS/blob/main/Images/StateLayer.PNG" width = "650" height = "300" />
<img src="https://github.com/Jonathon-Fleming/ToxPi-GIS/blob/main/Images/CountyLayer.PNG" data-canonical-  
src="https://github.com/Jonathon-Fleming/ToxPi-GIS/blob/main/Images/CountyLayer.PNG" width = "500" height = "300" />  

# Vignette 2: Using other geographic data
Description: Use this method to generate a single layer automatically that has symbolized ToxPi figures for local statistics with predetermined size, as shown below  

**Steps:**  
* Run the script using the vignette 2 partial test data(partial dataset will take a few minutes whereas entire dataset will be roughly 20 minutes)
    python ToxPi_Model.py Examples\PracticeData\Vignette2_Subset_NC.csv Examples\Output\Vignette2\Vignette2.lyrx  
* Open Vignette2.lyrx in ArcGIS Pro and share as a web map to ArcGIS Online
<img src="https://github.com/Jonathon-Fleming/ToxPi-GIS/blob/main/Images/MapShare.png" data-canonical-  
src="https://github.com/Jonathon-Fleming/ToxPi-GIS/blob/main/Images/MapShare.png">
* Obtain web link from ArcGIS Online via selecting the map in My Content and copying the URL or [view previously hosted map](https://ncsu.maps.arcgis.com/home/webmap/viewer.html?useExisting=1&layers=31cacdce95904f799cca1891ab213ba6) 
<img src="https://github.com/Jonathon-Fleming/ToxPi-GIS/blob/main/Images/WebLink2.PNG" data-canonical-  
src="https://github.com/Jonathon-Fleming/ToxPi-GIS/blob/main/Images/WebLink2.PNG">    
* Optionally, edit descriptive elements and metadata for public viewing 

**Map Details:**  
Interactive slices with custom popups  
Colored slices based on ToxPi GUI choices  
<img src="https://github.com/Jonathon-Fleming/ToxPi-GIS/blob/main/Images/NonFIPSLayer.PNG" data-canonical-  
src="https://github.com/Jonathon-Fleming/ToxPi-GIS/blob/main/Images/NonFIPS.PNG" width = "450" height = "300" />  

# Vignette 3: Using the toolbox to generate feature layers
Description: Use this method from within ArcGIS Pro to integrate ToxPi figures into your own analysis procedures that do not fit the above examples, as well as to allow custom ToxPi figure sizing on the map  

**Steps:**
* Split the source column for vignette 1 into latitude and longitude. Any preferred method will work, but split_coordinates.py was provided in the utilities folder for this  
* Open a new project in ArcGIS Pro(Project, New, Map, Change Name, Okay)  
* Add altered Vignette1 test data to the map(Map, Add Data, Vignette1_Subset_NC.csv)  
* Display data on the map using an equidistant projected coordinate system via the following tool and parameters:  
    Tool: Convert Coordinate Notation  
    Input Table: Vignette1_Subset_NC.csv  
    Input Coordinate System: GCS_WGS_1984  
    Output Feature Class: Vignette1_Displayed  
    Output Coordinate System: USA_Contiguous_Equidistant_Conic  
    Input Coordinate Format: DD2  
    X: Longitude  
    Y: Latitude  
    Output Coordinate Format: DD2  
* Add ToxPi Toolbox to project(Insert, Toolbox, Add Toolbox, ToxPiToolbox.tbx)  
* Turn on catalog pane(View, Catalog Pane)  
* Open custom script called ToxPi Construction from within ToxPiToolbox and run with desired parameters. The interface and parameter descriptions are shown below:  
<img src="https://github.com/Jonathon-Fleming/ToxPi-GIS/blob/main/Images/ToolInterface.PNG" data-canonical-  
src="https://github.com/Jonathon-Fleming/ToxPi-GIS/blob/main/Images/ToolInterface.PNG" width = "300" height = "500" />  
    inFeatures: Input feature layer to draw ToxPi figures from  
    outFeatures: The desired name for the output feature layer  
    uniqueID: The column name for the unique identifier for locations  
    inFields: The list of all desired fields to be included as slices  
    inputWeights: A string of weights for determining each slices radial width in order, separated by ;  
    inputRadius: A numerical value for determining the size of the drawn figures. The default is 1  
* Symbolize the resulting layer as desired (right click layer, symbology)
