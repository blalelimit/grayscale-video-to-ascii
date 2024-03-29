import numpy as np
import sys
import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = 'hide'
import pygame
import time
import random as rd

from colorama import Fore, Back, Style
from scripts.utils import scan_file


# Randomize colors
def change_color():
    foreground = rd.choice([Fore.BLACK, Fore.RED, Fore.GREEN, Fore.YELLOW, Fore.BLUE, Fore.MAGENTA, Fore.CYAN, Fore.WHITE, Fore.RESET])
    background = rd.choice([Back.BLACK, Back.RED, Back.GREEN, Back.YELLOW, Back.BLUE, Back.MAGENTA, Back.CYAN, Back.WHITE, Back.RESET])
    style = rd.choice([Style.DIM, Style.NORMAL, Style.BRIGHT])
    print(foreground)   # change foreground color
    print(background)   # change background color
    print(style)   # change style


# Removes multiple lines
# def delete_multiple_lines(n=1):
#     for _ in range(n):
#         sys.stdout.write("\x1b[1A")  # Cursor up one line
#         sys.stdout.write("\x1b[2K")  # Delete the last line


# Plays video with changing colors in terminal
def play_video(frames, total_frames, color=False, fps=30, reverse=False):
    starting_time = time.time()

    if reverse:
        frames = frames[::-1]   # reverses the frames
        print(Fore.BLACK)   # change foreground color
        print(Back.WHITE)   # change background color
        print(Style.BRIGHT)   # change style

    sys.stdout.write(f'\n{frames[0]}\n') # Print initial frame
    # delete_multiple_lines(n=1)

    for index in range(1, total_frames):
        sys.stdout.write(f'\n{frames[index]}\n') # Prints each frame; Number of new lines depends on preference
        # delete_multiple_lines(n=48)
        current_time = time.time() - starting_time

        if current_time < (index + 1) / fps:
            time.sleep((index + 1) / fps - current_time)    # Wait for n frames
        if color and index % 12 == 0:
            change_color()    # Change color every 12 frames

    print(Style.RESET_ALL)  # reset styles to default
    pygame.mixer.music.stop()


# Play audio
def play_audio(file, volume, reverse):
    if reverse:
        file += '_r'
    pygame.init()
    pygame.mixer.pre_init(frequency=44100, size=-16, channels=2, buffer=2048)
    pygame.mixer.init()
    pygame.mixer.music.load(f'outputs/{file}.mp3')
    pygame.mixer.music.set_volume(volume)
    pygame.mixer.music.play()


# Initialize all methods
def play_all(filename, input_color, input_volume, input_reverse):
    try:
        input_color = True if input_color == 'y' else False   # input_color defaults to 'n'
        input_volume = float(input_volume) if input_volume else 10.0    # volume defaults 10.0
        input_reverse = True if input_reverse == 'y' else False   # input_reverse defaults to 'n'
        frames = f'outputs/{filename}.npy'
        audio = f'outputs/{filename}.mp3'
        if not scan_file(frames):
            sys.stdout.write('No ASCII input found, first process the video\n')
            return
        if not scan_file(audio):
            sys.stdout.write('No audio input found, video continues\n')
            time.sleep(1.5) # delay before video starts
        else:
            play_audio(file=filename, volume=input_volume/100, reverse=input_reverse)   # play audio when present
        ascii_art = np.load(frames) # load ASCII art
        play_video(frames=ascii_art, total_frames=len(ascii_art), color=input_color, reverse=input_reverse) # play video
    except FileNotFoundError:
        sys.stdout.write('Input file cannot be found\n')
