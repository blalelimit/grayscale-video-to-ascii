import numpy as np
import sys
import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = 'hide'
import pygame
import time
import subprocess

from utils import scan_file


# Randomize colors
def change_color(color_list):
    chosen_colors = np.random.choice(color_list, size=2, replace=False)
    subprocess.run('color ' + "".join(chosen_colors), shell=True)


# Removes multiple lines
# def delete_multiple_lines(n=1):
#     for _ in range(n):
#         sys.stdout.write("\x1b[1A")  # Cursor up one line
#         sys.stdout.write("\x1b[2K")  # Delete the last line


# Plays video with changing colors in terminal
def play_video(frames, total_frames, color=False, fps=30):
    starting_time = time.time()
    color_list = ['%x' % x for x in range(0, 0xF)]  # Avaiable colors in terminal

    subprocess.run('color 07', shell=True)
    sys.stdout.write(f'\n{frames[0]}\n') # Print initial frame
    # delete_multiple_lines(n=1)

    for index in range(1, total_frames):
        sys.stdout.write(f'\n{frames[index]}\n') # Prints each frame; Number of new lines depends on preference
        # delete_multiple_lines(n=48)
        current_time = time.time() - starting_time
        
        if current_time < (index + 1) / fps:
            time.sleep((index + 1) / fps - current_time)    # Wait for n frames
        if color and index % 12 == 0:
            change_color(color_list)    # Change color every 12 frames

    subprocess.run('color 07', shell=True)


# Play audio
def play_audio(file, volume):
    pygame.init()
    pygame.mixer.pre_init(frequency=44100, size=-16, channels=2, buffer=2048)
    pygame.mixer.init()
    pygame.mixer.music.load(file)
    pygame.mixer.music.set_volume(volume)
    pygame.mixer.music.play()


# Initialize all methods
def play_all(file, input_color, input_volume):   
    try:
        input_color = True if input_color == 'y' else False   # input_color defaults to 'n'
        input_volume = float(input_volume) if input_volume else 10.0    # volume defaults 10.0
        filename = file.split(".")[0]
        frames = f'outputs/{filename}.npy'
        audio = f'outputs/{filename}.mp3'
        if not scan_file(frames):
            sys.stdout.write('No ASCII input found, first process the video\n')
            return
        if not scan_file(audio):
            sys.stdout.write('No audio input found, video continues\n')
            time.sleep(1.5) # delay before video starts
        else:
            play_audio(file=f'outputs/{filename}.mp3', volume=input_volume/100)   # play audio when present
        ascii_art = np.load(frames) # load ASCII art
        play_video(frames=ascii_art, total_frames=len(ascii_art), color=input_color) # play video
    except FileNotFoundError:
        sys.stdout.write('Input file cannot be found\n')
    
    
    



