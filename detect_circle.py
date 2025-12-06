import cv2
import numpy as np
import math
from match import contains_white_point

point_line_dis_max = 16
point_agent_dis_max = 78
ellipse_angle_max = 91
ellipse_angle_min = 87.8
# ellipse has no precise len formula
ellipse_len_diff_max = 70
ellipse_area_diff_min_ratio = 0.4
try_time = 0
incr = 5

def set_try_time(t):
    global try_time
    try_time = t

def find_contours_center(img, contours, a, b, c, ax, ay, n, wpi, region_area):
    # Iterate through contours and fit ellipses
    nn = 0
    for contour in contours:
        nn+=1
        # Filter out small contours that cannot form an ellipse
        if len(contour) < 5:
            continue
        arclen = cv2.arcLength(contour, True)
        if arclen < 50:
            continue
        ellipse = cv2.fitEllipse(contour)
        img_with_ellipses = img.copy()
        cv2.ellipse(img_with_ellipses, ellipse, (0, 255, 0, 255), 2) # Green color, thickness 2
        cv2.imwrite(f"dc/contour_{n}_{nn}.png", img_with_ellipses)
        [e_a, e_b] = ellipse[1]
        ellipse_len = math.pi * (3/2*(e_a+e_b) - math.sqrt(e_a*e_b))/2
        print("circle len diff:", n, abs(arclen - ellipse_len), arclen, ellipse_len)
        if abs(arclen - ellipse_len) > ellipse_len_diff_max:
            continue

        # arc_area = cv2.contourArea(contour)
        ellipse_area = math.pi * e_a * e_b / 4
        print("circle area ratio:", n, region_area/ellipse_area, region_area, ellipse_area)
        if region_area/ellipse_area < ellipse_area_diff_min_ratio:
            continue

        center_x = ellipse[0][0]
        center_y = ellipse[0][1]
        point_line_dis = abs(a*center_x + b*center_y + c)/math.sqrt(a**2 + b**2)
        point_agent_dis = math.sqrt((center_x-ax)**2 + (center_y-ay)**2)
        print("circle:", n, point_line_dis, point_agent_dis, ellipse, arclen)
        if point_line_dis > point_line_dis_max + try_time*incr \
            or point_agent_dis < point_agent_dis_max \
            or ellipse_angle_max < ellipse[2] or ellipse[2] < ellipse_angle_min:
            continue
        # if not contains_white_point(img, int(center_x), int(center_y), wpi):
        #     continue
        return True, center_x, center_y
    return False, -1, -1

def find_ellipse_by_bfs_region(img, region, a, b, c, ax, ay, n, wpi):
    contours, _ = cv2.findContours(region, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    region_area = cv2.countNonZero(region)
    find, x, y = find_contours_center(img, contours, a, b, c, ax, ay, n, wpi, region_area)
    if find:
        return find, x, y
    return False, 0, 0

# Load the image
# img = cv2.imread('your_image.jpg')