import time
import cv2
import numpy as np

"""
Replace following with your own algorithm logic

Two random coordinate generator has been provided for testing purposes.
Manual mode where you can use your mouse as also been added for testing purposes.
"""
previous_frame = None

def GetLocation(move_type, env, current_frame):
    global previous_frame
    
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
        coordinate = 8
    #Use absolute coordinates for the position of the "gun", coordinate space are defined below
    else:
        """
        (x,y) coordinates
        Upper left = (0,0)
        Bottom right = (W, H) 
        """
        
        
        processed_frame = cv2.cvtColor(current_frame, cv2.COLOR_RGB2GRAY)
        processed_frame = cv2.GaussianBlur(src=processed_frame, ksize=(5,5), sigmaX=0)

        if previous_frame is None:
            previous_frame = processed_frame
        
        diff_frame = cv2.absdiff(previous_frame, processed_frame)
        previous_frame = processed_frame

        kernel = np.ones((6,6))
        #diff_frame = cv2.dilate(diff_frame, kernel, 1)

        threshholded_frame = cv2.threshold(src=diff_frame, thresh=100, maxval=255, type=cv2.THRESH_BINARY)[1]
        threshholded_frame = cv2.erode(src=threshholded_frame, kernel=kernel)
        coordinatex = np.where(threshholded_frame == np.amax(threshholded_frame))[0][0]
        coordinatey = np.where(threshholded_frame == np.amax(threshholded_frame))[1][0]
        coordinate = [coordinatex, coordinatey]
        #coordinate = env.action_space_abs.sample()
        print(coordinate)
    return [{'coordinate' : coordinate, 'move_type' : move_type}]
