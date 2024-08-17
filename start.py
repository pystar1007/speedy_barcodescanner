
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
from time import sleep, time
#from asyncio import Queue
from queue import Queue

from omxplayer.player import OMXPlayer, OMXPlayerDeadError
import threading
import os
from collections import OrderedDict
import pygame
import operator

# import site
# print(site.getsitepackages())


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

# print("video_loop", len(video_loop))


# create player thread
class PlayerThread(threading.Thread):
    def __init__(self, queue : Queue):
        threading.Thread.__init__(self)
        self.queue = queue
        self.player = None
        
    def run(self):
        last_playing_video_index = 0
        last_playing_video = video_loop[last_playing_video_index]["video"]
        # s_time = time()
        self.player = OMXPlayer(video_home + last_playing_video)
        # print("Create", time() - s_time)
        #self.player.load(video_home + last_playing_video)
        #self.player.play()

        while True:
            
            if self.queue.empty():
                # play loop video

                while True:
                    sleep(1)
                    try:
                        if self.player.is_playing():
                            # print("playing", last_playing_video)
                            if not self.queue.empty():
                                break
                            continue
                    except Exception as e:
                        # print(str(e))
                        pass
                    
                    if not self.queue.empty():
                        break
                    
                    
                    last_playing_video_index += 1
                    if last_playing_video_index == len(video_loop):
                        last_playing_video_index = 0

                    video = video_loop[last_playing_video_index]["video"]
                    last_playing_video = video                    
                    
                    try:
                        self.player.is_playing()
                        
                        self.player.load(video_home + video)
                        self.player.play()
                    
                    except OMXPlayerDeadError:
                        # print("player dead")
                        self.player = OMXPlayer(video_home + last_playing_video)
                    
                    except Exception as e:
                        print("===", repr(e))

            else: 

                barcode = self.queue.get()
                self.queue.task_done()

                if barcode == "none_exist":
                    # print("Invalid Barcode")
                    # play no video

                    if last_playing_video == "no_video":
                        # play intermission video
                        try:
                            self.player.is_playing()
                            self.player.load(video_home + "blazing7-30sec.mp4")
                            # print("Playing Intermission after no video")
                            self.player.play()
                            
                        except OMXPlayerDeadError:
                            self.player = OMXPlayer(video_home + "blazing7-30sec.mp4")

                        last_playing_video = "intermission"
                    
                    elif last_playing_video == "intermission":
                        # play no video
                        try:
                            self.player.is_playing()
                            self.player.load(video_home + "No_video.mp4")
                            self.player.play()
                        except:
                            self.player = OMXPlayer(video_home + "No_video.mp4")

                        # print("Playing No Video after intermission")
                        last_playing_video = "no_video"

                        try:
                            while self.player.is_playing():
                                sleep(0.5)
                                if not self.queue.empty():
                                    break
                        except:
                            pass

                        if not self.queue.empty():
                            continue
                        
                        try:
                            self.player.is_playing()
                            # play intermission video
                            self.player.load(video_home + "blazing7-30sec.mp4")
                            # print("Playing Intermission")
                            self.player.play()
                        except:
                            self.player = OMXPlayer(video_home + "blazing7-30sec.mp4")

                        last_playing_video = "intermission"
                    
                    else:
                        try:
                            self.player.is_playing()
                            self.player.load(video_home + "No_video.mp4")
                            # print("Playing No Video for invalid barcode")
                            self.player.play()
                        except:
                            self.player = OMXPlayer(video_home + "No_video.mp4")
                        
                        last_playing_video = "no_video"
                        
                    try:
                        while self.player.is_playing(): # wait for video to finish playing
                            sleep(0.5)
                            if not self.queue.empty(): # check if new barcode has been scanned
                                break
                    except:
                        pass

                    if not self.queue.empty(): # check if new barcode has been scanned
                        continue
                    

                else:
                    s_time = time()
                    video = barcode_mapper[barcode]["video"]
                    
                    try:
                        self.player
                        self.player.load(video)
                        # print("Playing Scanned", video)
                        self.player.play()
                            
                    except Exception as e:
                        print(repr(e))
                        self.player = OMXPlayer(video_home + video)
                    
                    
                    last_playing_video = video

                    while self.queue.empty():
                        sleep(0.5)
                        try:
                            if not self.player.is_playing():
                                break
                        except:
                            break
                    
                    if not self.queue.empty():
                        continue
                    
                    try:                        
                        self.player.is_playing()
                        self.player.load(video_home + "blazing7-30sec.mp4")
                        # print("Playing Intermission")
                        self.player.play()
                    except:
                        
                        self.player = OMXPlayer(video_home + "blazing7-30sec.mp4")

                    last_playing_video = "intermission"
                    try:
                        while self.player.is_playing():
                            sleep(0.5)
                            if not self.queue.empty():
                                break
                    except:
                        pass

                    if not self.queue.empty():
                        continue



# create a queue to hold the videos
queueLock = threading.Lock()
play_list_queue = Queue(maxsize=1)



player_thread = PlayerThread(play_list_queue)
player_thread.start()


def startPlayer():
    
    while True:
        sleep(1)
        bar_code = getpass.getpass("")
        
        if bar_code and bar_code in barcode_mapper.keys():
            # print("Valid Barcode", bar_code)
            play_list_queue.put(bar_code)
                
        else:
            # print("Invalid Barcode", bar_code)
            play_list_queue.put("none_exist")
        
        
startPlayer()
#
