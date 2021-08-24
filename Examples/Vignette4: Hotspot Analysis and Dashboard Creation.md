# **Vignette 4: Hot Spot Analysis Demonstration and Dashboard Creation Using COVID-19 Data**  
Vignette 4 is a demonstration of one of the many analysis methods that can be done via integrating the ToxPi\*GIS Toolkit with existing ArcGIS methods. It uses hot spot analysis on the results of Vignette 3 with the full dataset to display high and low risk clusters for COVID-19 throughout the United States. The results are displayed in a Dashboard to demonstrate the hosting and extended visualization capablities that ArcGIS provides. The resulting dashboard can be found [here](https://ncsu.maps.arcgis.com/home/item.html?id=022416cbc74d430691ad7d2a4cbec229). A further description of the data can be found [here](https://www.niehs.nih.gov/research/programs/coronavirus/covid19pvi/details/).  

<p align = "center">
<img src="https://github.com/Jonathon-Fleming/ToxPi-GIS/blob/main/Images/hotspotcomparetransparent.png" data-canonical-  
src="https://github.com/Jonathon-Fleming/ToxPi-GIS/blob/main/Images/hotspotcomparetransparent.png" width="400" height="300" />  
<img src="https://github.com/Jonathon-Fleming/ToxPi-GIS/blob/main/Images/Dashboard.PNG" data-canonical-  
src="https://github.com/Jonathon-Fleming/ToxPi-GIS/blob/main/Images/Dashboard.PNG" width="600" height="300" />  
</p>  


## Steps:  
1. Generate ToxPi and choropleth feature layers using ToxPi_creation_customized.py and the full dataset(See Vignette 3 for help)  
2. Open layer file in ArcGIS Pro  
3. Delete excess layers (state and mid layers)  
4. Run Optimized Hot Spot Analysis Tool on local boundary layer with a distance band of 50 miles    

<p align = "center">
<img src="https://github.com/Jonathon-Fleming/ToxPi-GIS/blob/main/Images/OptimizedHotspotTool.PNG" data-canonical-  
src="https://github.com/Jonathon-Fleming/ToxPi-GIS/blob/main/Images/OptimizedHotspotTool.PNG" width="300" height="350" />  
</p>  

5. Use Join Field Tool to join the Hotspot result layer with the local boundary layer using SourceID and FID to obtain any desired fields  
<p align = "center">
<img src="https://github.com/Jonathon-Fleming/ToxPi-GIS/blob/main/Images/JoinFieldTool.PNG" data-canonical-  
src="https://github.com/Jonathon-Fleming/ToxPi-GIS/blob/main/Images/JoinFieldTool.PNG" width="300" height="700" />  
</p>  

6. Add raw data containing cases and deaths to the project  
7. Open hotspot layer attribute table and add field named FIPSLong of data type long    

<p align = "center">
<img src="https://github.com/Jonathon-Fleming/ToxPi-GIS/blob/main/Images/AttributeTable.PNG" data-canonical-  
src="https://github.com/Jonathon-Fleming/ToxPi-GIS/blob/main/Images/AttributeTable.PNG" width="300" height="200" />  
</p>  

8. Calculate FIPSLong field by setting it equal it to the FIPS column(This step allows for joining to raw data since it reads in as type Long)  

<p align = "center">
<img src="https://github.com/Jonathon-Fleming/ToxPi-GIS/blob/main/Images/Calculate.PNG" data-canonical-  
src="https://github.com/Jonathon-Fleming/ToxPi-GIS/blob/main/Images/Calculate.PNG" width="300" height="200" />  
</p>  

<p align = "center">
<img src="https://github.com/Jonathon-Fleming/ToxPi-GIS/blob/main/Images/CalculateField.PNG" data-canonical-  
src="https://github.com/Jonathon-Fleming/ToxPi-GIS/blob/main/Images/CalculateField.PNG" width="300" height="400" />  
</p>  

10. Use Join Field Tool to join the Hotspot result layer with the raw data using FIPSLong and FIPS to obtain any desired fields  
