

# Vignette 1(ToxPiCreation.py): Creating a ToxPi Feature Layer Using Python  
Description: Use the script ToxPiCreation.py to automatically produce predesigned feature layers containing interactive ToxPi features using the output of the ToxPi GUI as input. This is the suggested method, unless you are skilled with ArcGIS Pro and have a specific need for a Toolbox.
**Steps:**
* Download the root repository  
* Load the ArcGIS Pro environment using the following commmand  
    "%PROGRAMFILES%\ArcGIS\Pro\bin\Python\Scripts\proenv"
* Run the script using the vignette 1 subset test data(partial dataset will take roughly a few minutes whereas entire dataset will be about 20 minutes)  
    python ToxPiCreation.py Examples\PracticeData\Vignette1_Subset_NC.csv C:\Users\InputUser\Documents\Examples\Vignette1\Vignette1.lyrx 1.5
    
    Note: Script will produce ouput folder and vignette1 folder if they are not present  
* Open Vignette1.lyrx in ArcGIS Pro and share as a web map to ArcGIS Online
<p align = "center">
<img src="https://github.com/Jonathon-Fleming/ToxPi-GIS/blob/main/Images/MapShare.png" data-canonical-  
src="https://github.com/Jonathon-Fleming/ToxPi-GIS/blob/main/Images/MapShare.png">
</p>  

* Obtain web link from ArcGIS Online via selecting the map in My Content and copying the URL or [view previously hosted map](https://ncsu.maps.arcgis.com/home/item.html?id=e524bb8f06984c36b325b4614d66f748)  
<p align = "center">
<img src="https://github.com/Jonathon-Fleming/ToxPi-GIS/blob/main/Images/WebLink.PNG" data-canonical-  
src="https://github.com/Jonathon-Fleming/ToxPi-GIS/blob/main/Images/WebLink.PNG">   
</p>  
* Optionally, edit descriptive elements and metadata for public viewing  


<p align = "center">
<img src="https://github.com/Jonathon-Fleming/ToxPi-GIS/blob/main/Images/StateLayer.PNG" data-canonical-  
src="https://github.com/Jonathon-Fleming/ToxPi-GIS/blob/main/Images/StateLayer.PNG" width = "650" height = "300" />
<img src="https://github.com/Jonathon-Fleming/ToxPi-GIS/blob/main/Images/CountyLayer.PNG" data-canonical-  
src="https://github.com/Jonathon-Fleming/ToxPi-GIS/blob/main/Images/CountyLayer.PNG" width = "500" height = "300" />  
</p>  
<br/>  
# Vignette 2(ToxPiToolbox.tbx): Creating a ToxPi Feature Layer Using The ArcGIS Toolbox
Description: Use this method from within ArcGIS Pro to integrate ToxPi figures into your own analysis procedures that do not fit the above examples, as well as to allow custom ToxPi figure sizing or to draw only a subset of slices   


**Map Details:**  
Interactive slices  
Colored slices based on ToxPi GUI choices  
Toggleable maximum score rings  
Sizing based on input parameters  
Note: Special characters in slice names will be replaced by underscores  
<p align = "center">
<img src="https://github.com/Jonathon-Fleming/ToxPi-GIS/blob/main/Images/NonFIPSLayer.PNG" data-canonical-  
src="https://github.com/Jonathon-Fleming/ToxPi-GIS/blob/main/Images/NonFIPS.PNG" width = "550" height = "300" />  
</p>  

# Vignette 3(ToxPiModel.py): Altering ToxPiCreation.py for Advanced Map Creations  
Description: ToxPiModel.py is a demonstration of altering ToxPiCreation.py with more advanced analysis and geoprocessing steps to create new maps. This specific example is meant to be used with county or census tract data to create maps containing ToxPi feature layers and chorpleths that are visible based on zoom extent.

**Steps:**
* Download the root repository  
* Load the ArcGIS Pro environment using the following commmand  
    "%PROGRAMFILES%\ArcGIS\Pro\bin\Python\Scripts\proenv"
* Run the script using the vignette 1 subset test data(partial dataset will take roughly 5-10 minutes whereas entire dataset will be over an hour)  
    python ToxPiCreation.py Examples\PracticeData\Vignette1_Subset_NC.csv C:\Users\InputUser\Documents\Examples\Vignette3\Vignette3.lyrx
    
    Note: Script will produce ouput folder and vignette3 folder if they are not present  
* Open Vignette3.lyrx in ArcGIS Pro and share as a web map to ArcGIS Online
<p align = "center">
<img src="https://github.com/Jonathon-Fleming/ToxPi-GIS/blob/main/Images/MapShare.png" data-canonical-  
src="https://github.com/Jonathon-Fleming/ToxPi-GIS/blob/main/Images/MapShare.png">
</p>  

* Obtain web link from ArcGIS Online via selecting the map in My Content and copying the URL or [view previously hosted map](https://ncsu.maps.arcgis.com/home/item.html?id=e524bb8f06984c36b325b4614d66f748)  
<p align = "center">
<img src="https://github.com/Jonathon-Fleming/ToxPi-GIS/blob/main/Images/WebLink.PNG" data-canonical-  
src="https://github.com/Jonathon-Fleming/ToxPi-GIS/blob/main/Images/WebLink.PNG">   
</p>  
* Optionally, edit descriptive elements and metadata for public viewing  

**Map Details:**  
Choropleth based on ToxPi Score  
Local and state level statistics  
Layer visibility based on zoom extent  
Interactive slices with custom popups  
Colored slices based on ToxPi GUI choices    
Toggleable maximum score rings  
<p align = "center">
<img src="https://github.com/Jonathon-Fleming/ToxPi-GIS/blob/main/Images/StateLayer.PNG" data-canonical-  
src="https://github.com/Jonathon-Fleming/ToxPi-GIS/blob/main/Images/StateLayer.PNG" width = "650" height = "300" />
<img src="https://github.com/Jonathon-Fleming/ToxPi-GIS/blob/main/Images/CountyLayer.PNG" data-canonical-  
src="https://github.com/Jonathon-Fleming/ToxPi-GIS/blob/main/Images/CountyLayer.PNG" width = "500" height = "300" />  
</p>  
<br/>  
