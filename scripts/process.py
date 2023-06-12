import cv2
import sys
import ffmpeg
import numpy as np
import string

from pathlib import Path
from PIL import Image
from tqdm import trange
from math import floor

from scripts.utils import *
from scripts.replace import replace_ascii_to_words


FRAME_WIDTH = 160
ASCII_LUMINANCE = ['@', '#', '&', '%', '?', '+', '*', ';', ':', ',', '.', ' ']
FACTOR = 256/len(ASCII_LUMINANCE)
ASCII_OUTPUT = []

ASCII_TEMPLATE = ['@'] * 8 + [' '] * 4
ASCII_BINARY = ['0', '1']
ASCII_DECIMAL = list(string.digits)
ASCII_HEXADECIMAL = ASCII_DECIMAL + list(string.hexdigits)[16:]


## Audio Extraction Methods

# Main ffmpeg method to export audio
def extract_audio_main(file, filename, reverse=False):
    additional_args = dict()
    if reverse:
        filename += '_r'
        additional_args = dict(af='areverse')
    try:
        if scan_audio(file):
            in_file = ffmpeg.input(file)
            total_duration = float(ffmpeg.probe(file)['format']['duration'])
            message = audio_progress(
                (
                    ffmpeg
                    .output(in_file.audio, f'outputs/{filename}.mp3', acodec='mp3', audio_bitrate=320, **additional_args)
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


# FFmpeg for audio extraction
def extract_audio(file, filename):
    sys.stdout.write('\nBeginning audio extraction\n')
    if scan_file(f'outputs/{filename}.mp3'): 
        rewrite = input('Audio already extracted, rewrite (y/n)? ')
        if rewrite != 'y':
            return
        try:
            Path(f'outputs/{filename}.mp3').unlink()
            Path(f'outputs/{filename}_r.mp3').unlink()
        except FileNotFoundError:
            pass

    extract_audio_main(file, filename)    # FFmpeg main method
    extract_audio_main(file, filename, reverse=True)    # FFmpeg main method


## Video Extraction Methods

# Process to generate ASCII
def generate_ascii(file, filename, input_chars):
    sys.stdout.write('\nBeginning ASCII generation\n')
    if scan_file(f'outputs/{filename}.npy'): 
        rewrite = input('ASCII (*.npy) already extracted, rewrite (y/n)? ')
        if rewrite != 'y':
            return
        Path(f'outputs/{filename}.npy').unlink()

    input_chars = int(input_chars) if input_chars else 4    # defaults to 4
    if not scan_file(file):
        sys.stdout.write('Input file cannot be found\n')
    else:
        path_to_video = file.strip()
        cap = cv2.VideoCapture(path_to_video)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))   # extracts the total number of frames
        cap.release()

        extract_frames(filename, path_to_video, 1, total_frames, input_chars)
        sys.stdout.write('ASCII generation completed!\n')


# Extract frames from video
def extract_frames(filename, video_path, start_frame, n_frames, ascii_chars_type):
    # Initialize tqdm progress bar
    pbar = trange(n_frames, ascii=True, unit='frames', colour='blue')

    # Video Capture method to extract Image Frame
    capture = cv2.VideoCapture(video_path)
    capture.set(1, start_frame)
    success, image_frame = capture.read()
 
    # Calculate frame height to determine how many LF (\n) for all frames
    frame_height = calculate_frame_height(image_frame, FRAME_WIDTH)
    
    # Read frames while capture.read() is successful
    # frame_count = 1   
    # while success and frame_count <= n_frames:
    while success:
        success, image_frame = capture.read()
        try:
            process_frames(image_frame, frame_height, ascii_chars_type)
            pbar.update(1)  # Update tqdm progress bar by 1
        except Exception:
            continue
        # frame_count += 1

    capture.release()   # Release Video Capture
    np.save(f'outputs/{filename}.npy', ASCII_OUTPUT) # Save ASCII array as *.npy file
    pbar.update(pbar.total - pbar.n)    # Complete tqdm progress bar
    pbar.close()    # Close tqdm progress bar


# Process frames from video
def process_frames(image_frame, frame_height, ascii_chars_type):
    # Image Frame (img format) to Image Array (*.npy format)
    image = Image.fromarray(image_frame)
    # Process image to convert to ASCII [Grayscale, Resize Image, Pixels to ASCII]
    ascii_characters = pixels_to_ascii(grayscale(resize_image(image, FRAME_WIDTH, frame_height)), ascii_chars_type) 
    # Join each line in a single frame with LF (\n)
    pixel_count = len(ascii_characters)
    ascii_frame = '\n'.join([ascii_characters[index:(index + FRAME_WIDTH)] for index in range(0, pixel_count, FRAME_WIDTH)])
    # Appends the single ascii_frame to ASCII_OUTPUT
    ASCII_OUTPUT.append(ascii_frame)


# Convert pixels to ASCII
def pixels_to_ascii(image_frame, ascii_chars_type):
    pixels = image_frame.getdata()

    if ascii_chars_type not in [0, 1, 2, 3]:    # luminance
        characters = [ASCII_LUMINANCE[floor(pixel/FACTOR)] for pixel in pixels]
        return ''.join(characters)

    else:
        characters = [ASCII_TEMPLATE[floor(pixel/FACTOR)] for pixel in pixels]

        if ascii_chars_type == 0:   # words
            characters = ''.join(characters)
            characters = replace_ascii_to_words(characters)
            return characters

        elif ascii_chars_type == 1:  # 0's and 1's; binary
            characters = replacer(image_frame=characters, num_range=ASCII_BINARY)
            
        elif ascii_chars_type == 2:  # decimal numbers
            characters = replacer(image_frame=characters, num_range=ASCII_DECIMAL)

        elif ascii_chars_type == 3:  # hexadecimal numbers
            characters = replacer(image_frame=characters, num_range=ASCII_HEXADECIMAL)

        return ''.join(characters)




