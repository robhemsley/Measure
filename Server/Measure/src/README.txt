Measure Server

Version: 0.01
Author: Rob Hemsley
Contact: hello@robhemsley.co.uk

1) Install the following dependencies:
	OpenCV
	SimpleCV
	Numpy
	PIL

2) Set the config.py file as required
	- Should provide a publicly accessible domain name
	
3) Start the web server by running measure_server.py 

ANDROID:
	If you plan to use this with the android application you will need to recompile this
	setting the SERVER varaiable to reflect the IP/Domain that this script is running on.

To DEBUG:
	The debug mode can be enabled from the config file which will automatically 
	take the webserver out of production mode, print execution details and open
	the various image processing stages in new windows. (Machine can't be headless for this...)
	
	If you want to run the processing without the server run the measrue.py file directly.
	Consult the main method for more details of the test images it will be running up etc.
	
Notes:
1) The current version only supports a square ruler.
2) The object needs to be on a background with little surface change
3) Shadows should be minimized otherwise it won't work
4) The computed homography isn't taken into consideration and so you need an image that is 
	taken from directly above the material.
5) The results are in mm... More of a design feature to keep it as British as possible just for Jon.