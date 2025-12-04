import subprocess
import os
from match import match, match_gray
from detectRect import find_param_by_bfs_region
from detectCircle import find_ellipse_by_bfs_region
import cv2
import math
from bfs import bfs_color_region

agent_img = cv2.imread('agent.png', cv2.IMREAD_UNCHANGED)
wpi = cv2.imread('white_point.png', cv2.IMREAD_UNCHANGED)

def find_param_by_bfs(img, a, b, c, ax, ay, slop):
    x_step = 10
    vs = []
    h, w = img.shape[:2]
    step_add = 1 if slop < 0 else -1
    n_step = step_add
    while True:
        start_x = int(ax + x_step*n_step)
        start_y = int(ay+x_step*slop*n_step)
        if start_x >= w or start_x < 0:
            break
        visited = False
        for v in vs:
            if v[start_y, start_x]:
                visited = True
                break
        if visited:
            n_step += step_add
            continue
        r, v = bfs_color_region(img, [start_x, start_y])
        cv2.imwrite(f'bfs/v_{n_step}.png', r*255)
        f, x, y = find_param_by_bfs_region(img, r, a, b, c, ax, ay, n_step, wpi)
        if f:
            print("use rect")
            return f, x, y
        else:
            f, x, y = find_ellipse_by_bfs_region(img, r, a, b, c, ax, ay, n_step, wpi)
            if f:
                print("use circle")
                return f, x, y
        vs.append(v)
        print("visited:", len(vs))
    return False, -1, -1

def cal_agent_tai_dis(in_img):
    h, w = in_img.shape[:2]
    print("in_img w h:", w, h)
    find, atl, abr = match(in_img, agent_img, "agent.png", 0.18)
    agent_center_x_offset = 38
    agent_center_y_offset = 190
    print("agent atl abr:", atl, abr)
    agent_center = [atl[0]+agent_center_x_offset, atl[1]+agent_center_y_offset]
    slop = -132.0/226.0
    if agent_center[0] > w/2:
        slop = -slop
    line_x_len = 500
    end_point = [agent_center[0]+line_x_len, agent_center[1] + int(line_x_len*slop)]
    in_img_copy = in_img.copy()
    cv2.circle(in_img_copy, agent_center, 2, (0, 255, 0), 2)
    cv2.line(in_img_copy, agent_center, end_point, (0, 255, 0), 2)
    

    #line coef ax+by+c=0
    a = slop
    b = -1
    c = -agent_center[0]*slop + agent_center[1]

    # find, tx, ty = find_parallelogram_contours(in_img, a, b, c, agent_center[0], agent_center[1])
    find, tx, ty = find_param_by_bfs(in_img, a, b, c, agent_center[0], agent_center[1], slop)
    print(find, tx, ty)
    if not find:
        print("not find target")
        return
    cv2.circle(in_img_copy, [int(tx), int(ty)], 2, (0, 0, 255), 2)
    cv2.imwrite(f'match/center.png', in_img_copy)

    agent_taget_dis = math.sqrt((agent_center[0]-tx)**2 + (agent_center[1]-ty)**2)
    print("agent_taget_dis:", agent_taget_dis)
    dis_time_coef = 1.4
    tap_time = int(agent_taget_dis * dis_time_coef)
    command = f"adb shell input swipe 500 500 500 500 {tap_time}"
    print(command)

    subprocess.run(command.split(" "), check=True)


# subprocess.run(["rm", "-rf", "bfs/*"], check=True)
# subprocess.run(["rm", "-rf", "dr/*"], check=True)
# subprocess.run(["rm", "-rf", "dc/*"], check=True)

output_file = f"in/a.png"
output_dir = os.path.dirname(output_file)
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

command = ["adb", "exec-out", "screencap", "-p"]

with open(output_file, "wb") as f:
    subprocess.run(command, stdout=f, check=True)

in_img = cv2.imread(f"in/a.png", cv2.IMREAD_UNCHANGED)
cal_agent_tai_dis(in_img)
