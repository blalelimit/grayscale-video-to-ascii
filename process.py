import cv2
import sys
import ffmpeg
import numpy as np
import random as rd

from utils import scan_file, scan_audio, audio_progress
from PIL import Image
from tqdm import tqdm
from math import floor


FRAME_WIDTH = 160
ASCII_CHARS = ['1', '#', '&', '%', '?', '+', '*', ';', ':', ',', '.', ' ']
FACTOR = 256/len(ASCII_CHARS)
ASCII_LIST = list()


# FFmpeg for audio extraction
def extract_audio(file):
    message = ''
    try:
        sys.stdout.write('\nBeginning audio extraction\n')
        if scan_audio(file):
            in_file = ffmpeg.input(file)
            total_duration = float(ffmpeg.probe(file)['format']['duration'])
            message = audio_progress(
                (
                    ffmpeg
                    .output(in_file.audio, f'outputs/{file.split(".")[0]}.mp3', acodec='mp3', audio_bitrate=320)
                    .global_args('-progress', 'pipe:1', '-loglevel', 'error')
                    .overwrite_output()
                    .run_async(pipe_stdout=True, pipe_stderr=True, cmd='ffmpeg.exe')
                ), total_duration)
        else:
            message = 'No audio found in the video'
    except ffmpeg.Error as e:
        sys.stdout.write('FFmpeg error\n')  # e.stderr.decode()
    finally:
        sys.stdout.write(f'{message}\n')  


# Extract frames from video
def extract_frames(video_path, start_frame, save_file, number_of_frames):
    capture = cv2.VideoCapture(video_path)
    capture.set(1, start_frame)
    frame_count = 1
    ret, image_frame = capture.read()
    pbar = tqdm(total=number_of_frames, ascii=True) # Initialize progress bar
    
    while ret and frame_count <= number_of_frames:
        ret, image_frame = capture.read()
        try:
            image = Image.fromarray(image_frame)
            ascii_characters = pixels_to_ascii(greyscale(resize_image(image)))  # Process image to convert to ASCII
            pixel_count = len(ascii_characters)
            ascii_image = '\n'.join([ascii_characters[index:(index + FRAME_WIDTH)] for index in range(0, pixel_count, FRAME_WIDTH)])
            ASCII_LIST.append(ascii_image)
            pbar.update(1)  # Update progress bar by 1
        except Exception:
            continue
        frame_count += 1    # Increases frame counter   
    capture.release()
    np.save(f'outputs/{save_file}', ASCII_LIST) # Save ASCII array as *.npy file
    pbar.update(pbar.total - pbar.n)
    pbar.close()
    

# Resize image
def resize_image(image_frame):
    width, height = image_frame.size
    aspect_ratio = (height / float(width * 2.5))    # multiply by 2.5 to offset vertical scaling on terminal
    new_height = int(aspect_ratio * FRAME_WIDTH)
    resized_image = image_frame.resize((FRAME_WIDTH, new_height), resample=4)    # PIL Resampling.BOX to get the pixelated effect
    return resized_image


# Greyscale image
def greyscale(image_frame):
    return image_frame.convert('L')


# Convert pixels to ASCII
def pixels_to_ascii(image_frame):
    ASCII_CHARS[0] = str(rd.randint(0, 9))  # Generate random number for index 0
    pixels = image_frame.getdata()
    characters = ''.join([ASCII_CHARS[floor(pixel/FACTOR)] for pixel in pixels])
    return characters


# Process to generate ASCII
def generate_ascii(path):
    if scan_file(path):
        path_to_video = path.strip()
        cap = cv2.VideoCapture(path_to_video)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        cap.release()

        sys.stdout.write('\nBeginning ASCII generation\n')
        extract_frames(path_to_video, 1, path_to_video.split('.')[0], total_frames)
        sys.stdout.write('ASCII generation completed!\n')
    else:
        sys.stdout.write('Input file cannot be found\n')



