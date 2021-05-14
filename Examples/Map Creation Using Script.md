# Vignette 1: Using county or census tract data with FIPS

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
Choropleth colored by ToxPi score  
Interactive slices with custom popups  
Colored slices based on ToxPi GUI choices  
<img src="https://github.com/Jonathon-Fleming/ToxPi-GIS/blob/main/Images/StateLayer.PNG" data-canonical-  
src="https://github.com/Jonathon-Fleming/ToxPi-GIS/blob/main/Images/StateLayer.PNG" width = "650" height = "300" />
<img src="https://github.com/Jonathon-Fleming/ToxPi-GIS/blob/main/Images/CountyLayer.PNG" data-canonical-  
src="https://github.com/Jonathon-Fleming/ToxPi-GIS/blob/main/Images/CountyLayer.PNG" width = "650" height = "300" />  

# Vignette 2: Using other geographic data

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
src="https://github.com/Jonathon-Fleming/ToxPi-GIS/blob/main/Images/NonFIPS.PNG" width = "600" height = "300" />  
