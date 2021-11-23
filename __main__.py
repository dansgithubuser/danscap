from pynput import keyboard

import argparse
import os
import re
import signal
import subprocess
import threading
import time

parser = argparse.ArgumentParser()
parser.add_argument('--name', default='danscap')
parser.add_argument('--extension', '--ext', '-e', choices=['mkv', 'gif'], default='mp4')
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
end_key_pressed = False

def listen_for_end_key():
    def on_press(key):
        global end_key_pressed
        if key == end_key:
            end_key_pressed = True
    with keyboard.Listener(on_press=on_press) as listener:
        listener.join()

thread = threading.Thread(target=listen_for_end_key)
thread.daemon = True
thread.start()
while not end_key_pressed: time.sleep(0.01)

# stop recording
p.send_signal(signal.SIGINT)
time.sleep(1)

# pop up window for dragging
subprocess.run(['xdg-open', os.path.dirname(file_name)])
