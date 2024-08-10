

# read the database.csv
# play the default the default video in loop
# Raise an interrupt when barcode is read.


# video 1  is playing
# read barcode for video 2
# video 2 plays in loop, till barcode is read again ? no

# mulitple videos playing in loop, stop video mid playing
# read barcode for video 2
# video 2 stops video 1,  when video 2 is done playing, video 1 resumes or starts over
import random
import getpass
from time import sleep
from asyncio import Queue
import asyncio

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
video_home = "videos/"
# Read Csvs
import csv

barcode_mapper = OrderedDict()
playorder = {}
with open("database.csv") as csv_file:
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
    def __init__(self, threadID, name, q, q2, player):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.q = q
        self.q2 = q2
        self.player = player

    def loop_videos(self):
        end_loop = False
        while True:
            
            
            for b_item in video_loop:
                
                try:
                    if self.q.get_nowait() == "stop":
                        
                        end_loop = True
                       
                        self.q.task_done()
                       
                        break
                except:
                    pass
                
                if b_item["order"] is not "0":
                    
                    if self.player:
                        self.player.load(video_home + b_item["video"])
                    sleep(2.5)
                    self.player.play()
#                    sleep(2.5)
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
  #                      sleep(2.5)
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
                            sleep(2.5)
                            self.player.play()
                            sleep(2.5)
                            try:
                                while self.player.is_playing():
                                    sleep(0.5)
                            except:
                                self.q.put_nowait("start")
                                pass
                                                                                  
                            pass
                        

      


queueLock = threading.Lock()
workQueue = Queue(10)
workQueue2 = Queue(10)
player = None
player = OMXPlayer(video_home+"blazing7-30sec.mp4")
threads = []
thread = myThread(1, 'video_looper', workQueue, barcode_mapper, player)
thread.start()
threads.append(thread)
sleep(0.5)
player.pause()
workQueue.put_nowait("start")
thread = myThread(2, 'bar_code_video_player', workQueue, workQueue2, player)
thread.start()
threads.append(thread)

    

while True:
    # Run your bar code reader
    bar_code = getpass.getpass("")
    if bar_code and bar_code in barcode_mapper.keys():
        
        workQueue2.put_nowait("play:" + bar_code)
        if player and player.is_playing():
            player.pause()
            

        workQueue.put_nowait("stop")
        

        
