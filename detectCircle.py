import cv2
import numpy as np
import math
from match import contains_white_point

def find_contours_center(img, contours, a, b, c, ax, ay, n, wpi):
    # Iterate through contours and fit ellipses
    for contour in contours:
        # Filter out small contours that cannot form an ellipse
        if len(contour) < 5:
            continue
        arclen = cv2.arcLength(contour, True)
        if arclen < 50:
            continue
        ellipse = cv2.fitEllipse(contour)
        center_x = ellipse[0][0]
        center_y = ellipse[0][1]
        point_line_dis = abs(a*center_x + b*center_y + c)/math.sqrt(a**2 + b**2)
        point_agent_dis = math.sqrt((center_x-ax)**2 + (center_y-ay)**2)
        img_with_ellipses = img.copy()
        cv2.ellipse(img_with_ellipses, ellipse, (0, 255, 0), 2) # Green color, thickness 2
        cv2.imwrite(f"dc/contour_{n}.png", img_with_ellipses)
        print("circle:", n, point_line_dis, point_agent_dis, ellipse, arclen)
        if point_line_dis > 17 or point_agent_dis < 78 or 91 < ellipse[2] or ellipse[2] < 88:
            continue
        # if not contains_white_point(img, int(center_x), int(center_y), wpi):
        #     continue
        return True, center_x, center_y
    return False, -1, -1

def find_ellipse_by_bfs_region(img, region, a, b, c, ax, ay, n, wpi):
    contours, _ = cv2.findContours(region, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    find, x, y = find_contours_center(img, contours, a, b, c, ax, ay, n, wpi)
    if find:
        return find, x, y
    return False, 0, 0

# Load the image
# img = cv2.imread('your_image.jpg')