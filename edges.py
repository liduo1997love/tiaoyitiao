import cv2
import numpy as np
import math

def is_same_point(x1, y1, x2, y2, inter_max = 5):
    print("edge is_same_point:", abs(x1 - x2), abs(y1 - y2))
    return abs(x1 - x2) < inter_max and abs(y1 - y2) < inter_max

def check_two_line(i1x, i1y, i2x, i2y, p1x, p1y, p2x, p2y, ax, ay, a, b, c, inter_max, oppo_diff_max, p_l_dis_max):
    same_p = is_same_point(i1x, i1y, i2x, i2y, inter_max)
    same_x = abs(p1x-p2x) < oppo_diff_max
    same_y = abs(p1y-p2y) < oppo_diff_max
    print("edge check_two_line:", same_p, abs(p1x-p2x), same_x, abs(p1y-p2y), same_y)
    if same_p and (same_x or same_y):
        tx = (p1x+p2x)/2
        ty = (p1y+p2y)/2
        point_line_dis = abs(a*tx + b*ty + c)/math.sqrt(a**2 + b**2)
        point_agent_dis = math.sqrt((tx-ax)**2 + (ty-ay)**2)
        print("edge p_l_dis p_a_dis:", point_line_dis, point_agent_dis)
        if point_line_dis < p_l_dis_max and ty < ay and point_agent_dis > 50:
            return True, tx, ty
    return False, -1, -1

def find_target_by_edges(img, a, b, c, ax, ay, slop, inter_max, slop_diff_max, oppo_diff_max, p_l_dis_max):
    # Apply Canny edge detection
    img_copy = img.copy()
    edges = cv2.Canny(img, 100, 200, apertureSize=5) # img, minVal, maxVal

    # Display the original and edge-detected images
    cv2.imwrite("edge/edge.png", edges)

    lines = cv2.HoughLinesP(edges, 1, np.pi / 180, 100, minLineLength=100, maxLineGap=10)
    slop_lines = []
    neg_slop_lines = []
    for line in lines:
        x1, y1, x2, y2 = line[0]
        if abs(x1 - x2) < 0.01:
            continue
        if min(y1, y2) > ay:
            continue
        k = (y1 - y2)/(x1 - x2)
        if abs(k - slop) < slop_diff_max:
            cv2.line(img_copy, (x1, y1), (x2, y2), (0, 255, 0, 255), 2)
            slop_lines.append(line[0])
            continue
        if abs(k + slop) < slop_diff_max:
            cv2.line(img_copy, (x1, y1), (x2, y2), (0, 255, 0, 255), 2)
            neg_slop_lines.append(line[0])
    cv2.imwrite("edge/lines.png", img_copy)

    if len(slop_lines) == 0 or len(neg_slop_lines) == 0:
        return False, -1, -1

    for sl in slop_lines:
        sx1, sy1, sx2, sy2 = sl
        for nl in neg_slop_lines:
            nx1, ny1, nx2, ny2 = nl
            find, tx, ty = check_two_line(sx1, sy1, nx1, ny1, sx2, sy2, nx2, ny2, ax, ay, a, b, c, inter_max, oppo_diff_max, p_l_dis_max)
            if find: return find, tx, ty

            find, tx, ty = check_two_line(sx1, sy1, nx2, ny2, sx2, sy2, nx1, ny1, ax, ay, a, b, c, inter_max, oppo_diff_max, p_l_dis_max)
            if find: return find, tx, ty

            find, tx, ty = check_two_line(sx2, sy2, nx1, ny1, sx1, sy1, nx2, ny2, ax, ay, a, b, c, inter_max, oppo_diff_max, p_l_dis_max)
            if find: return find, tx, ty

            find, tx, ty = check_two_line(sx2, sy2, nx2, ny2, sx1, sy1, nx1, ny1, ax, ay, a, b, c, inter_max, oppo_diff_max, p_l_dis_max)
            if find: return find, tx, ty         
    return False, -1, -1


# img = cv2.imread("in/a.png", cv2.IMREAD_UNCHANGED)
# slop = -132.0/226.0
# find_target_by_edges(img, slop)
