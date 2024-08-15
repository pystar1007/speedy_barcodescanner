


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



# create a queue to hold the videos
play_list_queue = Queue(maxsize=1)

player = OMXPlayer("")


# create player thread
class PlayerThread(threading.Thread):
    def __init__(self, queue : Queue, player : OMXPlayer):
        threading.Thread.__init__(self)
        self.queue = queue
        self.player = player


    def run(self):
        last_playing_video = None
        last_playing_video_index = 0

        while True:
            
            if self.queue.empty():
                # play loop video

                while True:
                    sleep(0.5)
                    if not self.player.is_playing():
                        video = video_loop[last_playing_video_index]["video"]
                        self.player.load(video)
                        print("Playing", video)
                        self.player.play()

                        last_playing_video = video
                        last_playing_video_index += 1
                        if last_playing_video_index == len(video_loop):
                            last_playing_video_index = 0

                        if not self.queue.empty():
                            break
                
            else: 

                barcode = self.queue.get()
                play_list_queue.task_done()

                if barcode == "none_exist":
                    print("Invalid Barcode")
                    # play no video

                    if player.is_playing():
                        player.stop()

                    if last_playing_video == "no_video":
                        # play intermission video
                        player.load(video_home + "blazing7-30sec.mp4")
                        print("Playing Intermission")
                        player.play()
                        last_playing_video = "intermission"
                    
                    elif last_playing_video == "intermission":
                        # play no video
                        player.load(video_home + "No Video.mp4")
                        print("Playing No Video")
                        player.play()
                        last_playing_video = "no_video"

                        while player.is_playing():
                            sleep(0.5)
                            if not self.queue.empty():
                                break

                        if not self.queue.empty():
                            continue

                        # play intermission video
                        player.load(video_home + "blazing7-30sec.mp4")
                        print("Playing Intermission")
                        player.play()
                        last_playing_video = "intermission"
                    
                    else:
                        player.load(video_home + "No Video.mp4")
                        print("Playing No Video")
                        player.play()
                        
                        last_playing_video = "no_video"
                        

                    while self.player.is_playing(): # wait for video to finish playing
                        sleep(0.5)
                        if not self.queue.empty(): # check if new barcode has been scanned
                            break

                    if not self.queue.empty(): # check if new barcode has been scanned
                        continue
                    

                else:
                    video = barcode_mapper[barcode]["video"]

                    if player.is_playing():
                        player.stop()

                    player.load(video)
                    print("Playing", video)
                    player.play()
                    
                    last_playing_video = video

                    while self.queue.empty():
                        sleep(0.5)
                        if not self.player.is_playing():
                            break
                    
                    if not self.queue.empty():
                        continue

                    self.player.load(video_home + "blazing7-30sec.mp4")
                    print("Playing Intermission")
                    self.player.play()
                    last_playing_video = "intermission"

                    while self.player.is_playing():
                        sleep(0.5)
                        if not self.queue.empty():
                            break

                    if not self.queue.empty():
                        continue


player_thread = PlayerThread(play_list_queue, player)
player_thread.start()


def startPlayer():
    
    while True:
        bar_code = getpass.getpass("Enter barcode: ") 

        if bar_code and bar_code in barcode_mapper.keys():
            print("Barcode", bar_code)
            play_list_queue.put(bar_code)
                
        else:
            print("Invalid Barcode", bar_code)
            play_list_queue.put("none_exist")


startPlayer()


        
