from pynput import keyboard

import argparse
import os
import re
import signal
import subprocess
import time

parser = argparse.ArgumentParser()
parser.add_argument('--name', default='danscap')
parser.add_argument('--extension', '--ext', '-e', choices=['mkv', 'gif'], default='mkv')
parser.add_argument('--countdown', type=int, default=3)
parser.add_argument('--framerate', type=int, default=18)
parser.add_argument('--end-key', default='esc')
args = parser.parse_args()

# constants
file_name = os.path.join(os.path.dirname(__file__), f'{args.name}.{args.extension}')
w, h = re.search(r'(\d+)x(\d+).*\*', subprocess.run('xrandr', capture_output=True).stdout.decode()).groups()

# ensure file doesn't exist
if os.path.exists(file_name): os.remove(file_name)

# give user some time to set up the scene
for i in range(args.countdown, 0, -1):
    print(i)
    time.sleep(1)

# start recording
p = subprocess.Popen([
    'ffmpeg',
    '-video_size', f'{w}x{h}',
    '-framerate', str(args.framerate),
    '-f', 'x11grab',
    '-i', ':0.0',
    file_name,
])

# listen for esc
end_key = getattr(keyboard.Key, args.end_key)
with keyboard.Listener(on_press=lambda key: key != end_key) as listener:
    listener.join()

# stop recording
p.send_signal(signal.SIGINT)

# pop up window for dragging
subprocess.run(['xdg-open', os.path.dirname(file_name)])
