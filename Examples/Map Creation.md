# Description
All Vignettes use data from the Covid19 PVI Dashboard located within the NIH. The following demos use the new Model 12.4 with the data being current for June 24,2021. Under this model, risk components are split into four domains: Infection Rate, Population Concentration, Intervention Measures, and Health & Environment. Overall, these four domains are comprised of a total of fourteen categories displayed in the figure below, each with their correspondiong weight shown. This new model, unlike previous models, accounts for vaccine data within Intervention Measures, thus allowing for a more accurate representation of COVID19 risk. More information about the model, including underlying components for each slice category, can be found at the NIH [PVI Dashboard details page](https://www.niehs.nih.gov/research/programs/coronavirus/covid19pvi/details/).  
<p align = "center">
<img src="https://github.com/Jonathon-Fleming/ToxPi-GIS/blob/main/Images/Datainfo.PNG" data-canonical-  
src="https://github.com/Jonathon-Fleming/ToxPi-GIS/blob/main/Images/Datainfo.PNG" width = "550" height = "300" />
</p>  
Although the demos use Model 12.4, these methods are compatible with any results file produced by the ToxPi GUI. Current results files for the PVI Dashboard can be found at the [PVI Dashboard data repository](https://github.com/COVID19PVI/data), which can be used in place of the practice files, or custom made results using the ToxPi GUI can be used.   

# Vignette 1: Using county or census tract data with FIPS
Description: Use this method with county or census tract data to automatically generate a layer file containing multiple layers that follow the predefined template and symbology shown in the example images below, as well as provide both state and local statistics   
**Steps:**
* Download the root repository  
* Load the ArcGIS Pro environment using the following commmand  
    "%PROGRAMFILES%\ArcGIS\Pro\bin\Python\Scripts\proenv"
* Run the script using the vignette 1 subset test data(partial dataset will take roughly 5 minutes whereas entire dataset will be over an hour)  
    python ToxPi_Model.py Examples\PracticeData\Vignette1_Subset_NC.csv C:\Users\InputUser\Documents\Examples\Vignette1\Vignette1.lyrx  
    
    Note: Script will produce ouput folder and vignette1 folder if they are not present  
* Open Vignette1.lyrx in ArcGIS Pro and share as a web map to ArcGIS Online
<p align = "center">
<img src="https://github.com/Jonathon-Fleming/ToxPi-GIS/blob/main/Images/MapShare.png" data-canonical-  
src="https://github.com/Jonathon-Fleming/ToxPi-GIS/blob/main/Images/MapShare.png">
</p>  

* Obtain web link from ArcGIS Online via selecting the map in My Content and copying the URL or [view previously hosted map](https://ncsu.maps.arcgis.com/home/webmap/viewer.html?webmap=9d1dd6fa6a4844cea8dc94e17232ffe2)  
<p align = "center">
<img src="https://github.com/Jonathon-Fleming/ToxPi-GIS/blob/main/Images/WebLink.PNG" data-canonical-  
src="https://github.com/Jonathon-Fleming/ToxPi-GIS/blob/main/Images/WebLink.PNG">   
</p>  
* Optionally, edit descriptive elements and metadata for public viewing  
  

**Map Details:**  
Multilayer visualization  
State median statistics
Choropleth colored by ToxPi score  
Interactive slices with custom popups  
Colored slices based on ToxPi GUI choices  
<p align = "center">
<img src="https://github.com/Jonathon-Fleming/ToxPi-GIS/blob/main/Images/StateLayer.PNG" data-canonical-  
src="https://github.com/Jonathon-Fleming/ToxPi-GIS/blob/main/Images/StateLayer.PNG" width = "650" height = "300" />
<img src="https://github.com/Jonathon-Fleming/ToxPi-GIS/blob/main/Images/CountyLayer.PNG" data-canonical-  
src="https://github.com/Jonathon-Fleming/ToxPi-GIS/blob/main/Images/CountyLayer.PNG" width = "500" height = "300" />  
</p>  

# Vignette 2: Using other geographic data
Description: Use this method to generate a single layer automatically that has symbolized ToxPi figures for local statistics with predetermined size, as shown below  

**Steps:**  
* Run the script using the vignette 2 partial test data(partial dataset will take a few minutes whereas entire dataset will be roughly 20 minutes)
    python ToxPi_Model.py Examples\PracticeData\Vignette2_Subset_NC.csv Examples\Output\Vignette2\Vignette2.lyrx  
* Open Vignette2.lyrx in ArcGIS Pro and share as a web map to ArcGIS Online
<p align = "center">
<img src="https://github.com/Jonathon-Fleming/ToxPi-GIS/blob/main/Images/MapShare.png" data-canonical-  
src="https://github.com/Jonathon-Fleming/ToxPi-GIS/blob/main/Images/MapShare.png">
</p>  

* Obtain web link from ArcGIS Online via selecting the map in My Content and copying the URL or [view previously hosted map](https://ncsu.maps.arcgis.com/home/webmap/viewer.html?useExisting=1&layers=31cacdce95904f799cca1891ab213ba6)  
<p align = "center">
<img src="https://github.com/Jonathon-Fleming/ToxPi-GIS/blob/main/Images/WebLink2.PNG" data-canonical-  
src="https://github.com/Jonathon-Fleming/ToxPi-GIS/blob/main/Images/WebLink2.PNG">    
</p>  
* Optionally, edit descriptive elements and metadata for public viewing  

**Map Details:**  
Interactive slices with custom popups  
Colored slices based on ToxPi GUI choices  
<p align = "center">
<img src="https://github.com/Jonathon-Fleming/ToxPi-GIS/blob/main/Images/NonFIPSLayer.PNG" data-canonical-  
src="https://github.com/Jonathon-Fleming/ToxPi-GIS/blob/main/Images/NonFIPS.PNG" width = "450" height = "300" />  
</p>  

# Vignette 3: Using the toolbox to generate feature layers
Description: Use this method from within ArcGIS Pro to integrate ToxPi figures into your own analysis procedures that do not fit the above examples, as well as to allow custom ToxPi figure sizing on the map  

**Steps:**
* Split the source column for vignette 1 into latitude and longitude. Any preferred method will work, but split_coordinates.py was provided in the utilities folder for this and only requires changing the file paths in the script before running  
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
