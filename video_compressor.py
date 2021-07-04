#!/usr/local/bin/python3.7




# video_compressor.py




#==================
debugModeOn = False
#==================




## Setting the current working directory automatically
import os
project_path = os.getcwd() # getting the path leading to the current working directory
os.getcwd() # printing the path leading to the current working directory
os.chdir(project_path) # setting the current working directory based on the path leading to the current working directory




## Required packages
import os
import shutil
import osascript
from tqdm import tqdm # for having a nice progress bar
from glob import glob
from pathlib import Path
from os.path import join
from shutil import copyfile
from termcolor import colored
from playsound import playsound
from argparse import ArgumentParser
from pandas.io.clipboard import clipboard_get




## Configurations
#++++++++++++
CRF = 35 # Constant Rate Factor
changeResolution = True
WIDTH = 854 #1920 #1280 #854
HEIGHT = 480 #1080 #720 #480
#++++++++++++
# Resolution and aspect ratio examples:
# (Cf.: "Video resolution & aspect ratios" (https://support.google.com/youtube/answer/6375112?co=GENIE.Platform%3DDesktop&hl=en))
# 2160p: 3840x2160
# 1440p: 2560x1440
# 1080p: 1920x1080
# 720p: 1280x720
# 480p: 854x480
# 360p: 640x360
# 240p: 426x240




## Parsing the input argument
if not debugModeOn:
    parser = ArgumentParser(description='"video_compressor.py" is a Python\
        program that allows to compress ".mp4" and ".mov" file(s) from a video\
        file path or videos folder path. The software leverages the "ffmpeg"\
        Terminal command. It uses a CRF (Constant Rate Factor) of 35 and\
        eventually reduces the video format to shrink the video size by up to\
        10 times.')
    parser.add_argument('--path', metavar='/my/video/file/or/folder/path', type=str, default='clipboard', help='compress ".mp4" and ".mov" file(s) from a video file path or videos folder path')
    args = parser.parse_args()
    argsPath = args.path
else: # in case we are in "debug mode"
    argsPath = 'video folder path required'




## Initializations
if debugModeOn:
    # Tests (clipboard_value example for defining the TARGET_DIRECTORY)
    #======
    #--- DIRECTORY PATH
    #argsPath = project_path + '/videoSamples'
    #--- invalid DIRECTORY PATH
    #argsPath = project_path + '/vid'
    #--- VIDEO FILE PATH
    argsPath = project_path + '/videoSamples/input 23 -1.mp4'
    #--- invalid VIDEO FILE PATH
    #argsPath = project_path + '/videoSamples/in.mp4'
    #======

path_case = ''
files = []




## Function

def notify(title, subtitle, message, sound_path):
    """
    Posts macOS X notification

    Args:
        title (str): The title
        subtitle (str): The subtitle
        message (str): The message
        sound_path (str): The file path of the ".wav" audio file
    """

    # Playing sound
    playsound(sound_path)
    # Displaying the Desktop notification
    t = '-title {!r}'.format(title)
    s = '-subtitle {!r}'.format(subtitle)
    m = '-message {!r}'.format(message)
    os.system('terminal-notifier {}'.format(' '.join([m, t, s])))




## Main process

# Launching initial notification
notify(title='video_compressor.py',
           subtitle='Running video_compressor.py script to compress video file(s)',
           message='Compression process started...',
           sound_path='/System/Library/Sounds/Blow.aiff')


if argsPath == 'clipboard': # this is True (i.e. argsPath == 'clipboard') only if debugModeOn is set to "False"
    # 1) Retrieving stored clipboard value
    print('\n1) Retrieving stored clipboard value')
    clipboard_value = clipboard_get()

else:
    # 1) Retrieving the video folder path argument
    print('\n1) Retrieving the video folder path argument')
    clipboard_value = argsPath

print(' clipboard_value: {0}'.format(clipboard_value.encode('utf-8')))


# 2) Identifying clipboard value (either video file path or directory path)
print('2) Identifying clipboard value (either video file path or directory path)')
path = Path(clipboard_value)

# VIDEO FILE PATH case
if path.is_file():
    if '.mp4' in clipboard_value or '.mov' in clipboard_value:
        files = [clipboard_value]
        path_case = 'file'
        print(' path_case:', path_case)
    else:
        colored_error_message = colored('Invalid video file path...', 'red', attrs=['reverse', 'blink'])
        print(' ❌ ERROR! ' + colored_error_message)
        # Posting macOS X notification
        notify(title='video_compressor.py',
               subtitle='Video compression failed :-(',
               message='Invalid video file path...',
               sound_path='/System/Library/Sounds/Sosumi.aiff')
        # Exiting the Terminal window
        osascript.run('tell application "Terminal" to close first window')
        # Exiting the program
        exit(1)

# DIRECTORY PATH case
elif path.is_dir():
    path_case = 'folder'
    print(' path_case:', path_case)
    # Getting all the ".mp4" and ".mov" files of the TARGET_DIRECTORY
    print(' Getting all the ".mp4" and ".mov" files of the TARGET_DIRECTORY')
    # (Cf.: "Python glob multiple filetypes" (https://www.xspdf.com/help/50822753.html))
    files = []
    for ext in ('*.mp4', '*.mov'):
        files.extend(glob(join(clipboard_value, ext)))
    print(' Video files in TARGET_DIRECTORY:\n', files)
    if len(files) == 0:
        colored_error_message = colored('Directory does NOT contain any video file...', 'red', attrs=['reverse', 'blink'])
        print(' ❌ ERROR! ' + colored_error_message)
        # Posting macOS X notification
        notify(title='video_compressor.py',
               subtitle='Video compression failed :-(',
               message='No video file in directory...',
               sound_path='/System/Library/Sounds/Sosumi.aiff')
        # Exiting the Terminal window
        osascript.run('tell application "Terminal" to close first window')
        # Exiting the program
        exit(1)

# UNIDENTIFIED case
else:
    path_case = 'unidentified'
    print(' path_case:', path_case)
    colored_error_message = colored('Invalid video file or directory path...', 'red', attrs=['reverse', 'blink'])
    print(' ❌ ERROR! ' + colored_error_message)
    # Posting macOS X notification
    notify(title='video_compressor.py',
           subtitle='Video compression failed :-(',
           message='Invalid video file or directory path...',
           sound_path='/System/Library/Sounds/Sosumi.aiff')
    # Exiting the Terminal window
    osascript.run('tell application "Terminal" to close first window')
    # Exiting the program
    exit(1)


# 3) Creating a "compressedVideos" folder in the TARGET_DIRECTORY folder if it does not exist yet
# (Cf.: "Create a directory in Python" (https://www.geeksforgeeks.org/create-a-directory-in-python/))
print('3) Creating a "compressedVideos" folder in the TARGET_DIRECTORY folder if it does not exist yet')
if path_case == 'file':
    parent_directory = Path(clipboard_value).parent
    compressed_videos_folder_path = os.path.join(parent_directory, 'compressedVideos')
else: # meaning path_case == 'folder'
    parent_directory = clipboard_value
    compressed_videos_folder_path = os.path.join(parent_directory, 'compressedVideos')
if not os.path.isdir(compressed_videos_folder_path): # cf.: "How to find if directory exists in Python" (https://stackoverflow.com/questions/8933237/how-to-find-if-directory-exists-in-python)
   os.mkdir(compressed_videos_folder_path) # cf.: "Create a directory in Python" (https://www.geeksforgeeks.org/create-a-directory-in-python/)

# 4) Looping over the list of video files
print('4) Looping over the list of video files...')
for file in tqdm(files):

    # A) Finding the extension of the current video file (either ".mp4" or ".mov")
    print(' A) Finding the extension of the current video file (either ".mp4" or ".mov")')
    extension = file[-4:]

    # B) Storing the name of the current video file
    print(' B) Storing the name of the current video file')
    video_name = file.split('/')[-1]

    # C) Creating a temporary copy of the video file to compress inside the compressedVideo folder
    print(' C) Creating a temporary copy of the video file to compress inside the compressedVideo folder')
    temporary_video_file_path = str(parent_directory) + '/compressedVideos/currentVideoToCompress' + extension
    returned_value = copyfile(file, temporary_video_file_path)

    # D) Defining file_src and file_dst
    print(' D) Defining file_src and file_dst')
    file_src = temporary_video_file_path
    file_dst = str(parent_directory) + '/compressedVideos/currentVideoCOMPRESSED' + extension

    # E) Defining the current video compression command
    print(' E) Defining the current video compression command')
    # (Cf.: "Compressing mp4 files, listing directory contents, and copying files to a remote server in Python" (http://www.lewisu.edu/experts/wordpress/index.php/compressing-mp4-files-listing-directory-contents-and-copying-files-to-a-remote-server-in-python/))
    # (Cf.: "How To Resize a Video Clip in Python" (https://stackoverflow.com/questions/28361056/how-to-resize-a-video-clip-in-python))
    # (Cf.: "How can I make ffmpeg be quieter/less verbose?" (https://superuser.com/questions/326629/how-can-i-make-ffmpeg-be-quieter-less-verbose))
    # The CRF (Constant Rate Factor), which, in this case, is 35, can normally range from 18 to 24, where a higher number will compress the output to a smaller size
    if changeResolution:
        command = 'ffmpeg -i {0} -vf scale={1}:{2} -vcodec libx264 -crf {3} {4} -v quiet -stats'.format(
            file_src, WIDTH, HEIGHT, CRF, file_dst)
    else:
        command = 'ffmpeg -i {0} -vcodec libx264 -crf {1} {2} -v quiet -stats'.format(
            file_src, CRF, file_dst)

    # F) Running current command in Terminal
    print(' F) Running current command in Terminal')
    returned_value = os.system(command)

    # G) Renaming the compressed video file according to its original version
    print(' G) Renaming the compressed video file according to its original version')
    os.rename(file_dst, file_dst.replace(file_dst.split('/')[-1], video_name))

    # H) Removing the file_src and file_dst video files
    print(' H) Removing the file_src and file_dst video files')
    os.remove(file_src)

# Printing success message
if len(files) > 1:
    subtitle = 'Video files compressed ✅'
else:
    subtitle = 'Video file compressed ✅'
print('\n\n' + subtitle + '\n')
notify(title='video_compressor.py',
           subtitle=subtitle,
           message='The compression was successful!',
           sound_path='/System/Library/Sounds/Hero.aiff')

# Exiting the Terminal window in case the program has been triggered by Alfred
# (Cf.: How do I close the Terminal in OSX from the command line? (https://superuser.com/questions/158375/how-do-i-close-the-terminal-in-osx-from-the-command-line/1385450))
osascript.run('tell application "Terminal" to close first window')