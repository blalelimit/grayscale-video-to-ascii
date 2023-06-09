# This project is based on the implementation by CalvinLoke in https://github.com/CalvinLoke/bad-apple
import sys

from utils import scan_file
from process import extract_audio, generate_ascii
from play import play_all


# Main method
def main():
    while True:
        file = str(input("Please enter the path of file (ex. path/to/file/input.mp4): "))
        file.strip()  # Removes trailing whitespaces
        file = file if file else 'input.mp4'    # defaults to 'input.mp4'

        if not scan_file(file):
            sys.stdout.write('Input file cannot be found\n\n')
            continue
        else:
            break

    while True:
        sys.stdout.write('\n')
        sys.stdout.write('#' * 128)
        sys.stdout.write('\nSelect option: \n')
        sys.stdout.write('1. Process Video\n')
        sys.stdout.write('2. Play Video\n')
        sys.stdout.write('3. Exit\n')
        sys.stdout.write('#' * 128)
        sys.stdout.write('\n')

        user_input = str(input('\nYour option: '))
        user_input.strip()  # Removes trailing whitespaces

        if user_input == '1':
            chars = input('Choose ASCII characters: (0: normal, 1: binary, 2: decimal, 3: all): ')
            extract_audio(file)
            generate_ascii(file, chars)
            continue
        elif user_input == '2':
            volume = input('Choose volume (from 0 to 100): ')
            color = input('Turn on color effects? (y or n): ')
            play_all(file, color, volume)
            continue
        elif user_input == '3':
            sys.stdout.write('Thank you for using the program.\n')
            exit(0)
        else:
            sys.stdout.write('Incorrect input\n')
            continue


if __name__ == '__main__':
    main()