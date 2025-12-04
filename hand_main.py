import subprocess
import os
import cv2
from match import match_gray
step = 0
output_file = f"in/a{step}.png"

output_dir = os.path.dirname(output_file)
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

command = ["adb", "exec-out", "screencap", "-p"]

with open(output_file, "wb") as f:
    subprocess.run(command, stdout=f, check=True)

agent_img = cv2.imread('agent.png', cv2.IMREAD_UNCHANGED)
in_img =  cv2.imread(f"in/a{step}.png")
find, atl, abr = match_gray(in_img, agent_img, "agent.png")
agent_center_x = 38
agent_center_y = 190
agent_center = [atl[0]+agent_center_x, atl[1]+agent_center_y]
print(agent_center[0], agent_center[1])
