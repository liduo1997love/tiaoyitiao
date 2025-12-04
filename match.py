import cv2
import numpy as np
import sys

def match_gray(main_image, template, name):
    # Convert images to grayscale (optional, but often improves performance)
    main_image_gray = cv2.cvtColor(main_image, cv2.COLOR_BGR2GRAY)
    _, _, _, alpha_channel = cv2.split(template)
    template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)

    cv2.imwrite(f'match/gray_main_{name}', main_image_gray)
    cv2.imwrite(f'match/gray_temp_{name}', template_gray)
    cv2.imwrite(f'match/gray_mask_{name}', alpha_channel)

    # Get the dimensions of the template
    w, h = template_gray.shape[::-1]
    # print("temp h w:", h, w)

    # Perform template matching
    # TM_CCOEFF_NORMED is a common method for normalized cross-correlation

    result = cv2.matchTemplate(main_image_gray, template_gray, cv2.TM_CCOEFF_NORMED, mask=alpha_channel)

    # Sum the results to get a combined score

    # Find the location of the best match
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
    print(min_val, max_val, min_loc, max_loc)

    # Define a threshold for a "good enough" match (adjust as needed)
    threshold = 0.8

    # If the maximum correlation value is above the threshold, a match is found
    if max_val >= threshold :
        top_left = max_loc
        bottom_right = (top_left[0] + w, top_left[1] + h)

        # Draw a rectangle around the matched region (optional)
        cv2.rectangle(main_image, top_left, bottom_right, (0, 255, 0), 2)

        # Display the result (optional)
        # cv2.imshow('Matched Image', main_image)
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()
        print(f"Subimage found {name}")
        success = cv2.imwrite(f'match/{name}', main_image)
        return True, top_left, bottom_right
    else:
        # print("Subimage not found.")
        return False, None, None

def match(main_image, template, name, threshold):
    # Convert images to grayscale (optional, but often improves performance)
    # main_image_gray = cv2.cvtColor(main_image, cv2.COLOR_BGR2GRAY)
    # template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)

    # Get the dimensions of the template
    # w, h = template_gray.shape[::-1]
    h, w = template.shape[:2]
    # print("temp h w:", h, w)

    # Perform template matching
    # TM_CCOEFF_NORMED is a common method for normalized cross-correlation

    image_main_b, image_main_g, image_main_r, _ = cv2.split(main_image)
    image_needle_b, image_needle_g, image_needle_r, alpha_channel = cv2.split(template)
    # cv2.imwrite('match/agent_mask.png', alpha_channel)
    method = cv2.TM_SQDIFF_NORMED
    result_b = cv2.matchTemplate(image_main_b, image_needle_b, method, mask=alpha_channel)
    result_g = cv2.matchTemplate(image_main_g, image_needle_g, method, mask=alpha_channel)
    result_r = cv2.matchTemplate(image_main_r, image_needle_r, method, mask=alpha_channel)

    # Sum the results to get a combined score
    result = result_b + result_g + result_r
    # print(result,result_b , result_g , result_r)

    # Find the location of the best match
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
    print(min_val, max_val, min_loc, max_loc)

    # If the maximum correlation value is above the threshold, a match is found
    top_left = min_loc
    bottom_right = (top_left[0] + w, top_left[1] + h)
    cv2.rectangle(main_image, top_left, bottom_right, (0, 255, 0), 2)
    cv2.imwrite(f'match/{name}', main_image)
    if min_val <= threshold :
        print(f"Subimage found {name}.")
        return True, top_left, bottom_right
    else:
        # print("Subimage not found.")
        return False, 0, 0

# magic cube case
def contains_white_point(img, cx, cy, wpi):
    wp_h, wp_w = wpi.shape[:2]
    output_img = img.copy()
    img_center = output_img[cy-wp_h//2:cy+wp_h//2+1, cx-wp_w//2:cx+wp_w//2+1]
    print(img_center.shape, wpi.shape)
    f, _, _ = match(img_center, wpi, "img_center_match_wp.png", 0.07)
    return f

