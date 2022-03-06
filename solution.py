import time
import cv2
import numpy as np

def drawImg(img, cvtColor=cv2.COLOR_RGB2BGR):
    nDims = img.ndim
    if not (nDims == 3 or nDims == 2):
        raise ValueError("ndims must be 2 or 3")
    img = np.asarray(img)
    if nDims == 3:
        img = img.transpose(1, 0, 2)
        cv2.cvtColor(img, cvtColor)
    else:
        img = img.transpose()
    cv2.imshow("DEBUG", img)
    cv2.waitKey(1)
    return

"""
Replace following with your own algorithm logic

Two random coordinate generator has been provided for testing purposes.
Manual mode where you can use your mouse as also been added for testing purposes.
"""
previous_frame = None
previous_target = [0, 0]

def GetLocation(move_type, env, current_frame):
    global previous_frame
    global previous_target
    
    #Use relative coordinates to the current position of the "gun", defined as an integer below
    if move_type == "relative":
        """
        North = 0
        North-East = 1
        East = 2
        South-East = 3
        South = 4
        South-West = 5
        West = 6
        North-West = 7
        NOOP = 8
        """
        # default to noop
        coordinate = 8
    #Use absolute coordinates for the position of the "gun", coordinate space are defined below
    else:
        """
        (x,y) coordinates
        Upper left = (0,0)
        Bottom right = (W, H) 
        """
        # list of duck coords
        duck_locations = []

        # empty list for checking duck locations
        empty = []

        # store copy of current_frame for overlaying contours
        overlay_frame = current_frame

        # convert to greyscale and blur
        processed_frame = cv2.cvtColor(current_frame, cv2.COLOR_RGB2GRAY)
        processed_frame = cv2.medianBlur(src=processed_frame, ksize=9)
        processed_frame = cv2.GaussianBlur(src=processed_frame, ksize=(5,5), sigmaX=0)
        
        # instantiate previous frame at first run
        if previous_frame is None:
            previous_frame = processed_frame

        # find the absolute difference between previous frame and the current one to see movement
        diff_frame = cv2.absdiff(previous_frame, processed_frame)
        previous_frame = processed_frame

        # kernel for erosion
        kernel = np.ones((7,7))

        # apply a thresholding to diff_frame to remove small differences (movements)
        threshholded_frame = cv2.threshold(src=diff_frame, thresh=150, maxval=255, type=cv2.THRESH_BINARY)[1]
        
        # erode result to make the resultant 'blobs' of movement smaller
        threshholded_frame = cv2.erode(src=diff_frame, kernel=kernel)

        # create contours from the values found from abs_diff
        contours, _ = cv2.findContours(image=threshholded_frame, mode=cv2.RETR_EXTERNAL, method=cv2.CHAIN_APPROX_TC89_L1)
        for contour in contours:
            # if contour is large enough (but not too large), accept as duck
            if (cv2.contourArea(contour) > 600) and (cv2.contourArea(contour) < 1000):
                (x,y), _ = cv2.minEnclosingCircle(contour)
                center = (int(x), int(y))
                cv2.circle(overlay_frame, center, radius=15, color=(255, 0, 0), thickness=2)
                duck_locations.append(center)
        

        # draw contours on debug window
        cv2.drawContours(image=overlay_frame, contours=contours, contourIdx=-1, color=(0, 255, 0), thickness=2, lineType=cv2.LINE_AA)

        # parse x and y coords and send to game
        if duck_locations == empty:
            coordinatex = 0
            coordinatey = 0
            coordinate = [coordinatex, coordinatey]
        else:
            # try to find a duck that is less likely to be the same duck
            while len(duck_locations) > 0: 
                coordinatey, coordinatex = duck_locations.pop(0)
                # coordinatey, coordinatex = max(duck_locations, key=lambda item:item[0])
                coordinate = [coordinatex, coordinatey]
                if coordinatex not in range(previous_target[0] - 100, previous_target[0] + 100) and len(duck_locations) > 0:
                    break
            
        # Store previous target to make sure the same target isnt hit twice
        previous_target = coordinate

        # draw debug window
        cv2.imshow("DEBUG0", cv2.cvtColor(overlay_frame.transpose(1,0,2), cv2.COLOR_RGB2BGR))
        cv2.imshow("DEBUG1", cv2.cvtColor(processed_frame, cv2.COLOR_RGB2BGR))
        cv2.waitKey(1)
    return [{'coordinate' : coordinate, 'move_type' : move_type}]
