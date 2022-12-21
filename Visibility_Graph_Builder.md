# Visibility_Graph_Builder
This program is composed of functions and seven classes which make it possible to run the program efficiently. This program (Add-on) accepts csv files which represent a
time series. Once the file is imported, it reads a column of said file (which can be selected by the user) in order to represent this data as a visibility graph. The graph is 
made up of nodes which represent each data item in the selected column and these are displayed with different shades of colors (through the use of a colormap) with the use of 
quantiles.


How to install the Add-on using blender?:
	*Open Blender> Edit > Preferences  > Add-ons > Install > Select the file (Visibility_Graph_Builder.py)


How to use the Add-On?:
	*File > Import > Visibility Graph > Select File > Select column (optional, default column: 2) > Import Spreadsheet

