# grayscale-video-to-ascii

# Overview
* A project which converts grayscale videos to ASCII art runnable through the Terminal. The idea of ASCII as pixels has already been implemented in multiple respositories. This project is one of the numerous implementations through GitHub, and was inspired by the many [Bad Apple](https://www.youtube.com/watch?v=i41KoE0iMYU) videos throughout the internet. The source code for this project was a combination of projects found online.

# Features
* process.py -> Python file able to capture all input frames of a video and convert them as ASCII art. The output files are *.npy containing the ASCII art runnable through Terminals, and *.mp3 file (if the video has audio).
* play.py -> Prints the content from *.npy in the Terminal, and plays the audio (if present).
* main.py -> Main method that runs the methods from process.py and play.py, asks user to input video file, volume level, and color effects (WARNING! The lights may be flashy) in the Terminal.

# Requirements
* Python 3
* FFmpeg (to be installed and added to PATH)
* To install the dependencies, type the following in the Terminal (where the Python environment is installed):
```sh
  python -m pip install -r requirements.txt
```

# Usage:
* In the Terminal, run the file through:
```sh
  python main.py
```
* The video is ideally placed in the same folder as main.py.
* The *.npy file size may be too large for long videos.