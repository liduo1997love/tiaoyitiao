import subprocess
import sys
import math
ax = int(sys.argv[1])
ay = int(sys.argv[2])
tx = int(sys.argv[3])
ty = int(sys.argv[4])
dis_time_coef = 1.4
agent_taget_dis = math.sqrt((ax-tx)**2 + (ay-ty)**2)
tap_time = int(agent_taget_dis * dis_time_coef)
command = f"adb shell input swipe 500 500 500 500 {tap_time}"
print(command)
subprocess.run(command.split(" "), check=True)