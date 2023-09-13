import sys
import ffmpeg
import random as rd

from queue import Queue
from threading import Thread
from tqdm import tqdm
from math import floor
from os.path import exists, isfile


# Scans file if it exists and is a file
def scan_file(path):
    if exists(path):
        if isfile(path):
            return True
        else:
            sys.stdout.write('Input file cannot be found\n')
            return False
    else:
        return False


# Checks if file is has audio
def scan_audio(file):
    try:
        stream_list = list()
        probed = ffmpeg.probe(file)
        for stream in probed['streams']:
            stream_list.append(stream['codec_type'])
        return True if 'audio' in set(stream_list) else False
    except ffmpeg.Error as e:
        sys.stdout.write('FFmpeg error\n')  # e.stderr.decode()
        sys.exit(1)


def reader(pipe, queue):
    try:
        with pipe:
            for line in iter(pipe.readline, b''):
                queue.put((pipe, line))
    finally:
        queue.put(None)


# Audio Progress Bar by Gulski in https://github.com/kkroening/ffmpeg-python/issues/43#issuecomment-924800648
def audio_progress(process, total_duration, padding):
    q = Queue()
    error = False
    Thread(target=reader, args=[process.stdout, q]).start()
    Thread(target=reader, args=[process.stderr, q]).start()
    bar = tqdm(total=round(total_duration, 2), ascii=True, colour='blue')
    for _ in range(2):
        for source, line in iter(q.get, None):
            line = line.decode()
            if source == process.stderr:
                error = True
            else:
                line = line.rstrip()
                parts = line.split('=')
                key = parts[0] if len(parts) > 0 else None
                value = parts[1] if len(parts) > 1 else None
                if key == 'out_time_ms':
                    time = max(round(float(value) / 1000000., 2), 0)
                    bar.update(floor(time - bar.n))
                elif key == 'progress' and value == 'end':
                    bar.update(bar.total - bar.n)
    bar.close()
    return f'Audio extraction encountered a warning or error!' if error else f'{padding}audio extraction successful!'.capitalize()


# Method to calculate frame height
def calculate_frame_height(image_frame, FRAME_WIDTH):
    height, width, _ = image_frame.shape
    aspect_ratio = (height / float(width * 2.5))    # multiply by 2.5 to offset vertical scaling on terminal
    frame_height = int(aspect_ratio * FRAME_WIDTH)
    return frame_height


# Resize image
def resize_image(image_frame, FRAME_WIDTH, frame_height):
    resized_image = image_frame.resize((FRAME_WIDTH, frame_height), resample=4)    # PIL Resampling.BOX to get the pixelated effect
    return resized_image


# Greyscale image
def grayscale(image_frame):
    return image_frame.convert('L')


# Function to replace template ascii with specific ascii characters
def replacer(image_frame, num_range):
    for index, item in enumerate(image_frame):
        if item != ' ':
            image_frame[index] = rd.choice(num_range)
    return image_frame
        

