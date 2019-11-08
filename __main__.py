from pynput import keyboard

import os
import re
import signal
import subprocess
import time

# constants
file_name = os.path.join(os.path.dirname(__file__), 'danscap.gif')
w, h = re.search(r'(\d+)x(\d+).*\*', subprocess.run('xrandr', capture_output=True).stdout.decode()).groups()

# ensure file doesn't exist
if os.path.exists(file_name): os.remove(file_name)

# give user some time to set up the scene
for i in range(3, 0, -1):
    print(i)
    time.sleep(1)

# start recording
p = subprocess.Popen([
    'ffmpeg',
    '-video_size', f'{w}x{h}',
    '-framerate', '18',
    '-f', 'x11grab',
    '-i', ':0.0',
    file_name,
])

# listen for esc
with keyboard.Listener(on_press=lambda key: key != keyboard.Key.esc) as listener:
    listener.join()

# stop recording
p.send_signal(signal.SIGINT)

# pop up window for dragging
subprocess.run(['xdg-open', os.path.dirname(file_name)])
