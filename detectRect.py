import cv2
import numpy as np
import math
from match import contains_white_point

def find_contours_center(img, contours, a, b, c, ax, ay, n, wpi):
    for contour in contours:
        arclen = cv2.arcLength(contour, True)
        if arclen < 80:
            # print(f"rect {n} arclen:", arclen, " < 10")
            continue
        for delta in range(0, 4):
            d_v = delta / 200.0
            epsilon = d_v * arclen # Adjust epsilon for approximation

            approx = cv2.approxPolyDP(contour, epsilon, True)
            if len(approx) != 4:
                print(f"rect {n} len(approx) != 4:", len(approx))
                continue
            # parallelograms.append(approx)
            xy_diff_max = 5
            ay_diff = abs(approx[0][0][1] - approx[2][0][1])
            bx_diff = abs(approx[1][0][0] - approx[3][0][0])
            same_1 = ay_diff < xy_diff_max and bx_diff < xy_diff_max
            ax_diff = abs(approx[0][0][0] - approx[2][0][0])
            by_diff = abs(approx[1][0][1] - approx[3][0][1])
            same_2 = ax_diff < xy_diff_max and by_diff < xy_diff_max
            valid = same_1 or same_2
            if not valid:
                print(f"rect {n} not valid:", ay_diff, bx_diff, ax_diff, by_diff)
                continue

            center_x = (approx[0][0][0] + approx[1][0][0] + approx[2][0][0] + approx[3][0][0])/4
            center_y = (approx[0][0][1] + approx[1][0][1] + approx[2][0][1] + approx[3][0][1])/4

            point_line_dis = abs(a*center_x + b*center_y + c)/math.sqrt(a**2 + b**2)
            point_agent_dis = math.sqrt((center_x-ax)**2 + (center_y-ay)**2)
            print("rect:", n, point_line_dis, point_agent_dis, center_x, center_y, arclen)
            if point_line_dis > 20 or point_agent_dis < 50:
                continue
            # if not contains_white_point(img, int(center_x), int(center_y-3), wpi):
            #     continue
            output_img = img.copy()
            cv2.drawContours(output_img, [approx], -1, (0, 255, 0, 255), 2)
            cv2.imwrite(f"dr/contour_{n}.png", output_img)
            return True, center_x, center_y
    return False, -1, -1

def find_param_by_bfs_region(img, region, a, b, c, ax, ay, n, wpi):
    contours, _ = cv2.findContours(region, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    find, x, y = find_contours_center(img, contours, a, b, c, ax, ay, n, wpi)
    if find:
        return find, x, y
    return False, 0, 0