


# read the database.csv
# 1.	Start up and immediately start playing endless loop
# 2.	If existing barcode is scanned stop the loop and immediately play that scanned barcode
# 3.	Once the scanned barcode completes playing, go to intermission video. blazing7-30sec.mp4  OR if another barcode is scanned before the first scanned video completes, go directly to this new scanned video instead. Once any scanned video completes fall back to intermission video (blazing7-30sec.mp4
# 4.	After intermission video has completed go directly to playing the looped items where the loop left off before the first scanned video was scanned. Start at the beginning of that looped video.
# 5.	IF a barcode does not exist then stop the loop and play “No_vidoe.mp4”. Once “No_video.mp4” completes go directly where the loop left off before the Non exist barcode was scanned and start at the beginning of that looped video and continue. 
# 6.	IF a existing barcode is playing while scanning a non-existing barcode, stop the existing barcode video and fall back to “No_video.mp4” and play.
# 7.	When “No_video.mp4 is finished playing, go to intermission video blazing7-30sec.mp4 and play. Once intermission video blazing7-30sec.mp4 is finished, return to loop and continue where left off before the existing barcode was scanned. Start at the beginning of that looped video and continue.
# 8.	IF non-existing barcode is scanned while in intermission blazing7-30sec.mp4, stop and play “No_vidoe.mp4”. Once finished playing “No_video.mp4 then return to intermission video blazing7-30sec.mp4 and continue. Once intermission video blazing7-30sec.mp4 finishes, continue to the loop where left off from the last existing scanned video and continue play.



import getpass
from time import sleep

# from omxplayer.player import OMXPlayer
import threading
import os
from collections import OrderedDict
import pygame
import operator
import csv

import threading
from queue import Queue

os.system('clear')
pygame.init()
width = 1080
height = 720

# video_home = "/home/pi/Desktop/SCANNER/videos/"
video_home = "videos/"
# Read Csvs

barcode_mapper = OrderedDict()
playorder = {}
# csv_path = "/home/pi/Desktop/SCANNER/database.csv"
csv_path = "database.csv"

with open(csv_path) as csv_file:
    csv_reader = csv.DictReader(csv_file)
    for row in csv_reader:
        barcode_mapper[row['barcode']] = {"order": int(row['playorder']), "video": row['video']}  # Mapping from barcode to video name

video_loop = []
for item in barcode_mapper.keys():

    if barcode_mapper[item]["order"] > 0:
        video_loop.append(barcode_mapper[item])
video_loop = sorted(video_loop, key=lambda i: i["order"])


class OMXPlayer:
    def __init__(self, video):
        self.video = video
        self.playing = False
        self.paused = False

    def load(self, video):
        self.video = video

    def play(self):
        self.playing = True
        # os.system('omxplayer -o hdmi ' + self.video)
        play_thread = threading.Thread(target=self.play_video)
        play_thread.start()
        play_thread.join()
        self.playing = False

    def play_video(self):
        sleep(5)

    def pause(self):
        self.playing = False
        self.paused = True

    def is_playing(self):
        return self.playing

    def is_paused(self):
        return self.paused

    def stop(self):
        self.playing = False
        self.paused = False

# create player thread
class PlayerThread(threading.Thread):
    def __init__(self, queue : Queue):
        threading.Thread.__init__(self)
        self.queue = queue
        self.player = None


    def run(self):
        last_playing_video_index = 0
        last_playing_video = video_loop[last_playing_video_index]["video"]
        self.player = OMXPlayer(video_home + last_playing_video)

        while True:
            
            if self.queue.empty():
                # play loop video

                while True:
                    sleep(0.5)
                    try:
                        if self.player.is_playing():
                            print("playing", last_playing_video)
                            if not self.queue.empty():
                                break
                            continue
                    except:
                        pass

                    if not self.queue.empty():
                        break

                    last_playing_video_index += 1
                    if last_playing_video_index == len(video_loop):
                        last_playing_video_index = 0

                    video = video_loop[last_playing_video_index]["video"]
                    last_playing_video = video

                    try:
                        self.player.load(video_home + video)
                        self.player.play()
                    except:
                        self.player = OMXPlayer(video_home + video)

            else: 

                barcode = self.queue.get()
                self.queue.task_done()

                if barcode == "none_exist":
                    # print("Invalid Barcode")
                    # play no video
                    try:
                        self.player.is_playing() 
                    except:
                        pass

                    if last_playing_video == "no_video":
                        # play intermission video
                        try :
                            self.player.load(video_home + "blazing7-30sec.mp4")
                            # print("Playing Intermission")
                            self.player.play()
                        except:
                            self.player = OMXPlayer(video_home + "blazing7-30sec.mp4")

                        last_playing_video = "intermission"
                    
                    elif last_playing_video == "intermission":
                        # play no video
                        try:
                            self.player.load(video_home + "No Video.mp4")
                            self.player.play()
                        except:
                            self.player = OMXPlayer(video_home + "No Video.mp4")

                        # print("Playing No Video")
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
                            # play intermission video
                            self.player.load(video_home + "blazing7-30sec.mp4")
                            # print("Playing Intermission")
                            self.player.play()
                        except:
                            self.player = OMXPlayer(video_home + "blazing7-30sec.mp4")

                        last_playing_video = "intermission"
                    
                    else:
                        try:
                            self.player.load(video_home + "No Video.mp4")
                            # print("Playing No Video")
                            self.player.play()
                        except:
                            self.player = OMXPlayer(video_home + "No Video.mp4")
                        
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
                    video = barcode_mapper[barcode]["video"]

                    try:
                        self.player.is_playing()
                    except:
                        pass
                    
                    try:
                        self.player.load(video)
                        # print("Playing", video)
                        self.player.play()
                    except:
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
        bar_code = getpass.getpass("")

        if bar_code and bar_code in barcode_mapper.keys():
            # print("Barcode", bar_code)
            play_list_queue.put(bar_code)
                
        else:
            # print("Invalid Barcode", bar_code)
            play_list_queue.put("none_exist")


startPlayer()
