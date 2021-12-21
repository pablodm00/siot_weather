# siot_weather
Code for the Sensing &amp; Internet of Things project, December 2021


How to run: 
- run arduino code for a week, ard_to_ser.ino
- connect esp32 to pc via microUSB port
- run python files (ser_to_mon.py, owm_to_mon.py), simoultaneously. 
- when data collection is finished, run analysis.ipynb (note: plotly plots do not show in the built-in jupyter notebook reader, if you would like to see them open in visual studio code or similar)
 

if you only want to check the code in <>.ipynb: skip the first 5 cells, uncomment the first line in cell 6 and run from there. 

note: wifi passwords, api keys and other sensible data has been censored as the repository is publicly available
