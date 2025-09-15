


# read the database.csv
# play the default the default video in loop
# Raise an interrupt when barcode is read.


# video 1  is playing
# read barcode for video 2
# video 2 plays in loop, till barcode is read again ? no

# mulitple videos playing in loop, stop video mid playing
# read barcode for video 2
# video 2 stops video 1,  when video 2 is done playing, video 1 resumes or starts over
import getpass
from time import sleep
from asyncio import Queue

from omxplayer.player import OMXPlayer
import threading
import os
from collections import OrderedDict
import pygame
import operator


os.system('clear')
pygame.init()
width = 1080
height = 720
video_home = "/home/pi/Desktop/SCANNER/videos/"
# Read Csvs
import csv

barcode_mapper = OrderedDict()
playorder = {}
with open("/home/pi/Desktop/SCANNER/database.csv") as csv_file:
    csv_reader = csv.DictReader(csv_file)
    for row in csv_reader:
        barcode_mapper[row['barcode']] = {"order": int(row['playorder']), "video": row['video']}  # Mapping from barcode to video name

video_loop = []
for item in barcode_mapper.keys():

    if barcode_mapper[item]["order"] > 0:
        video_loop.append(barcode_mapper[item])
video_loop = sorted(video_loop, key=lambda i: i["order"])



#  2 threads
# Queue:  Publisher(bar ccode scanner) and subsciber(Video looper)
class myThread(threading.Thread):
    # Defines a new class named `myThread` which inherits from `threading.Thread`

    def __init__(self, threadID, name, q, q2, player):
        # The constructor method that initializes the thread object with various parameters

        threading.Thread.__init__(self)
        # Calls the constructor of the parent `threading.Thread` class to properly initialize the thread

        self.threadID = threadID
        # Stores the thread's ID

        self.name = name
        # Stores the thread's name

        self.q = q
        # Stores the first queue object, `q`

        self.q2 = q2
        # Stores the second queue object, `q2`

        self.player = player
        # Stores the player object

        self.last_video_index = 0
        # Initializes an attribute to track the index of the last processed video
        # Starts from 0



    def loop_videos(self):
        # Defines a method `loop_videos` which will be executed when the thread runs

        end_loop = False     # Initializes a flag to control the termination of the video looping

        i = self.last_video_index       # Sets the starting index for video processing to the last recorded index

        while True: # Starts an infinite loop to continuously process videos

            while i < len(video_loop): # Loops through the `video_loop` list while `i` is less than the length of the list

                self.last_video_index = i  # Updates `last_video_index` to the current value of `i`

                b_item = video_loop[i]  # Retrieves the video item at index `i` from the `video_loop` list

                i += 1     # Increments the index `i` for the next iteration

                try:
                    if self.q.get_nowait() == "stop":
                        # Tries to get an item from queue `q` without blocking
                        # Checks if the item is "stop"

                        end_loop = True
                        # Sets the `end_loop` flag to `True` to signal termination of the loop

                        self.q.task_done()
                        # Marks the task in the queue as done

                        break
                        # Breaks out of the inner `while` loop
                        
#The code snippet provided is a part of a thread class designed to process videos in a loop, while also checking for a "stop" signal from a queue. The loop_videos method handles video processing and checks for a stop condition to terminate the loop.
                except:
                    pass
                if b_item["order"] is not "0":
                    if self.player:
                        self.player.load(video_home + b_item["video"])
                    sleep(0.5)
                    self.player.play()

                    try:
                        while self.player.is_playing():
                            sleep(0.5)
                    except:
                        pass
                    sleep(0.5)
                try:
                    if self.q.get_nowait() == "stop":
                        end_loop = True
                        self.q.task_done()
                        break
                except:
                    pass
            i = 0
            if end_loop:
                break
    def thread1(self):
        while True:
            try:
                message =  self.q.get_nowait()
                     
                if message == "start":
                    
                    self.q.task_done()
                    self.loop_videos()

                if message == "stop":
                    
                    self.q.task_done()
                    
            except:
                pass

    def run(self):
        
        if self.threadID == 1:
            # video looper
            
            self.thread1()

            
                    
        if self.threadID == 2:
            
            while True:
                if not self.q2.empty():
                    message = self.q2.get_nowait()
                    if message[:4] == "play":
                        sleep(0.5)
                        self.q2.task_done()
                        player.load(video_home + barcode_mapper[message[5:]]["video"])
                        sleep(0.5)
                        player.play()
                        sleep(0.5)
                        # We check if its still playing
                        try:
                            while self.player.is_playing():
                                sleep(0.01)
                        except:
                            pass 
                        

                        if self.q2.empty():
                            # Starting the loop back again, only if its safely finished playing the video,
                            # if its interrupted with the new bar_code, then we get back to the beginning of the queue again.
                            if self.player:
                                self.player.load(video_home+"blazing7-30sec.mp4")
                            sleep(0.5)
                            self.player.play()
                            sleep(0.5)
                            try:
                                while self.player.is_playing():
                                    sleep(0.5)
                            except:
                                self.q.put_nowait("start")
                                pass
                                                                                  
                            pass
                        

      




queueLock = threading.Lock()  # Create a threading lock object to synchronize access to shared resources.
workQueue = Queue(1)  # Initialize a queue with a maximum size of 1 for task management.
workQueue2 = Queue(1)  # Initialize a second queue with a maximum size of 1 for additional task management.
player = None  # Initialize a variable to hold the media player object.
player = OMXPlayer(video_home + "blazing7-30sec.mp4")  # Create an OMXPlayer instance to play the specified video file.
threads = []  # Create an empty list to keep track of the threads that will be started.
thread = myThread(1, 'video_looper', workQueue, barcode_mapper, player)  # Instantiate a new thread of type myThread with the given parameters.
thread.start()  # Start the execution of the thread.
threads.append(thread)  # Add the newly started thread to the threads list.
sleep(0.5)  # Pause the execution for 0.5 seconds to allow the player to initialize properly.
player.pause()  # Pause the video playback.
workQueue.put_nowait("start")  # Place a "start" message in the workQueue without blocking.
thread = myThread(2, 'bar_code_video_player', workQueue, workQueue2, player)  # Instantiate another myThread with different parameters.
thread.start()  # Start the execution of this second thread.
threads.append(thread)  # Add this second thread to the threads list.
import getpass  # Import the getpass module to securely handle password prompts (though not used in this snippet).
from time import sleep  # Import the sleep function from the time module to manage delays.


#This code sets up a threading environment with a media player and two threads that handle video and barcode tasks. It uses queues to manage communication between threads and synchronizes access to shared resources with a lock.

def startPlayer():
    while True:
        # Continuously run the following code in an infinite loop
        # Wait for the user to input a bar code via getpass (typically used for password input)
        bar_code = getpass.getpass("")
        
        # Check if the bar code is not empty and exists in the barcode_mapper dictionary
        if bar_code and bar_code in barcode_mapper.keys():
            # If conditions are met, add a play command with the bar code to the workQueue2
            workQueue2.put_nowait("play:" + bar_code)
            
            # Check if the player object exists and is currently playing a video
            if player and player.is_playing():
                # Pause the currently playing video
                player.pause()
                
            # Add a stop command to the workQueue
            workQueue.put_nowait("stop")
            
            # Pause execution for 2 seconds
            sleep(2)

        else:
            # If the bar code is invalid or not in the dictionary
            
            # Check if the player object exists and is currently playing a video
            if player and player.is_playing():
                # Pause the currently playing video
                player.pause()

            # Load a default video (No_video.mp4) from the video_home directory
            player.load(video_home + "No_video.mp4")
            
startPlayer()

        
