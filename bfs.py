import cv2
import numpy as np
from collections import deque

def bfs_color_region(img, start, thresh=2):
    h, w = img.shape[:2]
    visited = np.zeros((h, w), np.uint8)

    sx, sy = start

    q = deque([(sx, sy)])
    visited[sy, sx] = 1

    region = np.zeros((h, w), np.uint8)  # store results

    # 4-direction or 8-direction neighbors
    dirs = [(1,0), (-1,0), (0,1), (0,-1)]

    #bg color
    max_pixel = 600*600
    region_num = 0

    while q:
        x, y = q.popleft()

        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if 0 <= nx < w and 0 <= ny < h and not visited[ny, nx]:
                visited[ny, nx] = 1

                # Color difference
                diff = np.linalg.norm(img[ny, nx].astype(np.int32) - img[y, x].astype(np.int32))
                if diff <= thresh:
                    region[ny, nx] = 1
                    region_num += 1
                    if region_num > max_pixel:
                        return region, visited
                    q.append((nx, ny))

    return region, visited

# img = cv2.imread("in/a0.png")
# r, v = bfs_color_region(img, (500, 500))
# cv2.imwrite('bfs/v.png', r*255)
