import argparse
import os
import re
import signal
import subprocess
import time

parser = argparse.ArgumentParser()
parser.add_argument('--name', default='danscap')
parser.add_argument('--extension', '--ext', '-e', choices=['mkv', 'gif'], default='mp4')
parser.add_argument('--countdown', type=int, default=3)
parser.add_argument('--framerate', type=int, default=18)
parser.add_argument('--end-key', default='esc')
args = parser.parse_args()

# constants
DIR = os.path.dirname(os.path.realpath(__file__))

FILE_PATH = os.path.join(DIR, f'{args.name}.{args.extension}')
W, H = re.search(r'(\d+)x(\d+).*\*', subprocess.run('xrandr', capture_output=True).stdout.decode()).groups()

# start esc listener
listener = subprocess.Popen(['sudo', 'python3', os.path.join(DIR, 'listener.py')])

# ensure file doesn't exist
if os.path.exists(FILE_PATH): os.remove(FILE_PATH)

# give user some time to set up the scene
for i in range(args.countdown, 0, -1):
    print(i)
    time.sleep(1)

# start recording
ffmpeg = subprocess.Popen([
    'ffmpeg',
    '-video_size', f'{W}x{H}',
    '-framerate', str(args.framerate),
    '-f', 'x11grab',
    '-i', ':0.0',
    FILE_PATH,
])

# wait for esc
listener.wait()

# stop recording
ffmpeg.send_signal(signal.SIGINT)
time.sleep(1)

# pop up window for dragging
subprocess.run(['xdg-open', os.path.dirname(FILE_PATH)])
