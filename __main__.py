import argparse
import datetime
import os
import re
import signal
import subprocess
import sys
import time

parser = argparse.ArgumentParser()
parser.add_argument('--extension', '--ext', '-e', choices=['mkv', 'gif'], default='mp4')
parser.add_argument('--framerate', '-f', type=int, default=18)
parser.add_argument('--countdown', '-c', type=int, default=3)
parser.add_argument('--truncate', '-t', type=int, default=1)
args = parser.parse_args()

# constants
DIR = os.path.dirname(os.path.realpath(__file__))
TIMESTAMP = '{:%Y-%m-%d_%H-%M-%S%z}'.format(datetime.datetime.now().astimezone())
TMP_FILE_PATH = os.path.join(DIR, f'danscap.{args.extension}')
OUT_FILE_PATH = os.path.join(DIR, f'{TIMESTAMP}.{args.extension}')

# ensure file doesn't exist
if os.path.exists(TMP_FILE_PATH): os.remove(TMP_FILE_PATH)

# give user some time to set up the scene
for i in range(args.countdown, 0, -1):
    print(i)
    time.sleep(1)

# start recording
ffmpeg = subprocess.Popen(
    [
        'ffmpeg',
        '-f', 'kmsgrab',
        '-i', '-',
        '-vf', 'hwmap=derive_device=vaapi,hwdownload,format=bgr0',
        TMP_FILE_PATH,
    ],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
)
t_start = time.time()
try:
    ffmpeg.wait(timeout=0.1)
except:
    pass
if ffmpeg.returncode != None:
    print(ffmpeg.stderr.read().decode())
    sys.exit(1)
print('recording... (press enter to stop)')

# wait for enter or ctrl-c
try:
    input()
except:
    pass

# stop recording
print('stopping...')
t_end = time.time()
ffmpeg.send_signal(signal.SIGINT)
ffmpeg.wait(timeout=2)

# truncate
print('truncating...')
subprocess.run(
    f'ffmpeg -i {TMP_FILE_PATH} -t {t_end - t_start - args.truncate} -c copy {OUT_FILE_PATH}'.split(), # use -ss to truncate start? -t is duration
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    check=True,
)

# pop up window for dragging
print('popping...')
subprocess.Popen(['xdg-open', os.path.dirname(OUT_FILE_PATH)])

print('done!')
