import subprocess
import os
import cv2
import math
from match import match
from bfs import bfs_color_region
from edges_rect import find_target_by_rect_edges, set_try_time as stt1
from edges_circle import find_target_by_circle_edges, set_try_time as stt2
from detect_rect import find_param_by_bfs_region, set_try_time as stt3
from detect_circle import find_ellipse_by_bfs_region, set_try_time as stt4

agent_img = cv2.imread('agent.png', cv2.IMREAD_UNCHANGED)
wpi = cv2.imread('white_point.png', cv2.IMREAD_UNCHANGED)
agent_center_x_offset = 38
agent_center_y_offset = 190
slop_value = -132.0/226.0

def find_target_by_bfs(img, a, b, c, ax, ay, slop):
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
        # cv2.imwrite(f'bfs/v_{n_step}.png', r*255)
        f, x, y = find_ellipse_by_bfs_region(img, r, a, b, c, ax, ay, n_step, wpi)
        if f:
            print("use circle")
            return f, x, y
        f, x, y = find_param_by_bfs_region(img, r, a, b, c, ax, ay, n_step, wpi)
        if f:
            print("use rect")
            return f, x, y       
        vs.append(v)
        print("visited:", len(vs))
    return False, -1, -1

def jump(slop, ax, ay, tx, ty, a, b, c):
    # agent_taget_dis = math.sqrt((agent_center[0]-tx)**2 + (agent_center[1]-ty)**2)
    # jump distance is not two point distance
    a2 = -slop
    b2 = -1
    c2 = -tx*a2 + ty

    real_y = (a*c2 - a2*c)/(a2*b-b2*a)
    real_x = (-b*real_y-c)/a
    agent_taget_dis = math.sqrt((ax-real_x)**2 + (ay-real_y)**2)

    print("agent_taget_dis:", agent_taget_dis)
    dis_time_coef = 1.39
    tap_time = int(agent_taget_dis * dis_time_coef)
    command = f"adb shell input swipe 500 500 500 500 {tap_time}"
    print(command)
    subprocess.run(command.split(" "), check=True)

def get_agent_tai_dis_jump(in_img):
    h, w = in_img.shape[:2]
    print("in_img w h:", w, h)
    find, atl, abr = match(in_img, agent_img, "agent.png", 0.18)
    print("agent atl abr:", atl, abr)
    ax = atl[0]+agent_center_x_offset
    ay = atl[1]+agent_center_y_offset
    slop = slop_value
    if ax > w/2:
        slop = -slop
    
    #line coef ax+by+c=0
    a = slop
    b = -1
    c = -ax*slop + ay

    find, tx, ty = find_target_by_rect_edges(in_img, a, b, c, ax, ay, slop)
    if find:
        print("find_target_by_rect_edges")
        # img_copy = in_img.copy()
        # cv2.circle(img_copy, [int(tx), int(ty)], 2, (255, 0, 0, 255), 2)
        # cv2.imwrite("match/target.png", img_copy)
        jump(slop, ax, ay, tx, ty, a, b, c)
        return True
    
    find, tx, ty = find_target_by_circle_edges(in_img, a, b, c, ax, ay, slop)
    if find:
        print("find_target_by_circle_edges")
        # img_copy = in_img.copy()
        # cv2.circle(img_copy, [int(tx), int(ty)], 2, (0, 255, 0, 255), 2)
        # cv2.imwrite("match/target.png", img_copy)
        jump(slop, ax, ay, tx, ty, a, b, c)
        return True

    find, tx, ty = find_target_by_bfs(in_img, a, b, c, ax, ay, slop)
    if find:
        print("find_target_by_bfs")
        # img_copy = in_img.copy()
        # cv2.circle(img_copy, [int(tx), int(ty)], 2, (0, 0, 255, 255), 2)
        # cv2.imwrite(f'match/target.png', img_copy)
        jump(slop, ax, ay, tx, ty, a, b, c)
        return True
    print("not find target")
    return False


output_file = f"in/a.png"
output_dir = os.path.dirname(output_file)
if not os.path.exists(output_dir):
    os.makedirs(output_dir)
command = ["adb", "exec-out", "screencap", "-p"]
with open(output_file, "wb") as f:
    subprocess.run(command, stdout=f, check=True)


in_img = cv2.imread(f"in/a.png", cv2.IMREAD_UNCHANGED)
try_time = 1
while not get_agent_tai_dis_jump(in_img):
    stt1(try_time)
    stt2(try_time)
    stt3(try_time)
    stt4(try_time)
    try_time += 1
    print("increase try time:", try_time)
# cv2.imwrite("in/should_not_change.png", in_img)
