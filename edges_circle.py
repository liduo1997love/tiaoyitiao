import cv2
import math

ellipse_len_min = 40
point_line_dis_max=15
point_agent_dis_max = 78
ellipse_angle_max = 91
ellipse_angle_min = 87.8
try_time = 0
incr = 5

def set_try_time(t):
    global try_time
    try_time = t

def find_target_by_circle_edges(img, a, b, c, ax, ay, slop):
    edges = cv2.Canny(img, 100, 200)
    # cv2.imwrite("edges_circle/Canny.png", edges)
    contours, _ = cv2.findContours(edges.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    n = -1
    for contour in contours:
        n += 1
        if len(contour) < 5:
            continue
        ellipse = cv2.fitEllipse(contour)

        [e_a, e_b] = ellipse[1]
        ellipse_len = math.pi * (3/2*(e_a+e_b) - math.sqrt(e_a*e_b))/2

        if ellipse_len < ellipse_len_min:
            continue
        
        center_x = ellipse[0][0]
        center_y = ellipse[0][1]
        if center_y > ay:
            continue

        # img_copy = img.copy()
        # cv2.ellipse(img_copy, ellipse, (0, 255, 0, 255), 2) # Draw ellipse in green
        # cv2.drawContours(img_copy, contours, n, (0, 0, 255, 255), 2)
        # cv2.imwrite(f"edges_circle/contour_{n}.png", img_copy)
        point_line_dis = abs(a*center_x + b*center_y + c)/math.sqrt(a**2 + b**2)
        point_agent_dis = math.sqrt((center_x-ax)**2 + (center_y-ay)**2)
        print("edges_circle:", n, point_line_dis, point_agent_dis, ellipse, ellipse_len)
        if point_line_dis > point_line_dis_max + try_time*incr \
            or point_agent_dis < point_agent_dis_max \
            or ellipse_angle_max < ellipse[2] or ellipse[2] < ellipse_angle_min:
            continue
        return True, center_x, center_y
    return False, -1, -1

# img = cv2.imread("in/a.png")
# find_target_by_circle_edges(img, 1,1,0,0,2000,0)