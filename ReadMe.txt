1.Files
---------------------
	
1. videos [Folder]
	
2. database.csv
	
3. start.py

2. 

How it works
---------------------

	
start.py runs when you boot your device.
	
A video looper is initialized on boot, looping the videos by playorder.

	How are videos are read by system?
		
Playorder is assigned to a barcode, barcode is fed to video player, and video is played.
		
This means that Barcodes are required for any video to play. 

		
*Note: You do not need to have a physical barcode, you can type letters or numbers into the csv as a barcode just make sure what you type is unique.
			
Example: I have a 30 sec video that is assigned barcode of 30SEC 


	
Start.py opens the database.csv and will play vidoes in their respective play order.
		
** items with a play order of 0 will be skipped
		
** all other items will then be queued by their playorder number

		
It is best to number the play order in numerical order
			
Note: logic is in place to detect if duplicate items have the same playorder number
			
It will group these and play the videos in the order that it picks them up.
			
For best result please assign unique number to each video's playorder number.


	

LOGIC
	--------------
	
[Playorder] --> queues a barcode. 
		
[Barcode] --> queues a video  
			
[Video] --> communicates to video player and plays video from the videos folder.
	





::::::::::::::::::::::::
******* REQUIRED *******
::::::::::::::::::::::::
	
	
Database.csv
	----------------
	
1. All items MUST have a unique value in the barcode line of database.csv
	
2. All videos must be defined with video format of (.avi,.mov or .mp4)
	
3. All playorder items not in use must have a value of 0 for the video to be skipped.
	
4. !!HEADERS MUST NOT BE CHANGED OR IT WILL BREAK SCRIPT !!


Hope you enjoy the video player.
		
	

Thanks,
	  
-Blake Poisso
	   
Developer