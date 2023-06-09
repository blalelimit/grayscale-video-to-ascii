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
ASCII_LUMINANCE = ['@', '#', '&', '%', '?', '+', '*', ';', ':', ',', '.', ' ']
FACTOR = 256/len(ASCII_LUMINANCE)
ASCII_LIST = list()


# FFmpeg for audio extraction
def extract_audio(file):
    sys.stdout.write('\nBeginning audio extraction\n')
    if scan_file('outputs/input.mp3'):
        sys.stdout.write('Audio already extracted\n')
        return 
    message = ''
    try:
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
def extract_frames(video_path, start_frame, save_file, number_of_frames, input_chars):
    capture = cv2.VideoCapture(video_path)
    capture.set(1, start_frame)
    frame_count = 1
    ret, image_frame = capture.read()
    pbar = tqdm(total=number_of_frames, ascii=True) # Initialize progress bar
    
    while ret and frame_count <= number_of_frames:
        ret, image_frame = capture.read()
        try:
            image = Image.fromarray(image_frame)
            ascii_characters = pixels_to_ascii(greyscale(resize_image(image)), input_chars)  # Process image to convert to ASCII
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
def pixels_to_ascii(image_frame, input_chars):
    pixels = image_frame.getdata()

    if input_chars == 1:  # 0's and 1's
        point = 4
        characters = [ASCII_LUMINANCE[floor(pixel/FACTOR)] for pixel in pixels]
        for index, item in enumerate(characters):
            if item in ASCII_LUMINANCE[:-point]:
                characters[index] = str(rd.randint(0, 1))
            else:
                characters[index] = ' '
        characters = ''.join(characters)

    elif input_chars == 2:  # decimal
        point = 4
        characters = [ASCII_LUMINANCE[floor(pixel/FACTOR)] for pixel in pixels]
        for index, item in enumerate(characters):
            if item in ASCII_LUMINANCE[:-point]:
                characters[index] = str(rd.randint(0, 9))
            else:
                characters[index] = ' '
        characters = ''.join(characters)

    elif input_chars == 3: # all
        ASCII_LUMINANCE[0] = str(rd.randint(0, 9))  # Generate random number for index 0
        characters = ''.join([ASCII_LUMINANCE[floor(pixel/FACTOR)] for pixel in pixels])

    else: # input_chars == 0; normal
        characters = ''.join([ASCII_LUMINANCE[floor(pixel/FACTOR)] for pixel in pixels])

    return characters


# Process to generate ASCII
def generate_ascii(path, input_chars):    
    input_chars = int(input_chars) if input_chars else 0    # defaults to 0
    if not scan_file(path):
        sys.stdout.write('Input file cannot be found\n')
    else:
        path_to_video = path.strip()
        cap = cv2.VideoCapture(path_to_video)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        cap.release()

        sys.stdout.write('\nBeginning ASCII generation\n')
        extract_frames(path_to_video, 1, path_to_video.split('.')[0], total_frames, input_chars)
        sys.stdout.write('ASCII generation completed!\n')
        


