# import the necessary packages
from collections import deque
from imutils.video import VideoStream
from math import floor
import numpy as np
import argparse
import cv2
import imutils
import time
from classify import classify
import socketio

WIZARD = 'Radagast' # or 'Gandalf' or 'Saruman'

NUMBER_TO_SPELL = {
    0: 'dragonstrike',
    1: 'dragonstrike',
    2: 'teleport',
    3: 'thunderhead',
    4: 'dragonstrike',
    5: 'guardian',
    6: 'ice_tornado',
    7: 'dragonstrike',
    8: 'dragonstrike',
    9: 'furious_fowl'
}

# Color ranges for detection, in opencv's own 'special' interpretation of HSL
yellowLower = (12, 124, 150)
yellowUpper = (32, 255, 255)

blueLower = (110, 50, 50)
blueUpper = (120, 255, 255)

def send_move(coords):
    sio.emit('message', {
        WIZARD: {
            "move": coords,
            "spells":{}
        }
    })

def send_spell(spell):
    sio.emit('message', {
        WIZARD :{
            "move": (0,0),
            "spells":{spell: True}
        }
    })

sio = socketio.Client()
@sio.on('connect')
def on_connect():
    print("I'm connected! Much Tze Wow")
    send_spell('join')

@sio.on('message')
def on_message(data):
    pass

@sio.on('my message')
def on_message(data):
    pass

@sio.on('disconnect')
def on_disconnect():
    print("I'm disconnected!")

sio.connect('http://172.17.129.220:8080')

MIN_MOVEMENT_SENDING_DELAY = 0.1

# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video",
                help="path to the (optional) video file")
ap.add_argument("-b", "--buffer", type=int, default=500,
                help="max buffer size")
args = vars(ap.parse_args())

# define the lower and upper boundaries of the "yellow"
# ball in the HSV color space, then initialize the
# list of tracked points

pts = deque(maxlen=args["buffer"])

# if a video path was not supplied, grab the reference
# to the webcam
if not args.get("video", False):
    vs = VideoStream(src=0).start()

# otherwise, grab a reference to the video file
else:
    vs = cv2.VideoCapture(args["video"])

# cam_width = vs.get(cv2.cv.CV_CAP_PROP_FRAME_WIDTH)
_, cam_width, _ = vs.read().shape
# allow the camera or video file to warm up
time.sleep(2.0)

def process_xs(arr):
    span = arr.max() - arr.min()
    if span < cam_width * 0.08: # for drawing 1s
        norm = np.full(arr.size, 0.5)
    else:
        norm = (arr - arr.min()) / (arr.max() - arr.min())

    return (20 * norm).astype(int).flatten()

def process_ys(arr):
    norm = (arr - arr.min()) / (arr.max() - arr.min())

    return (20 * norm).astype(int).flatten()

last_blue_sent = time.time()
def record_blue(center, point):
    if time.time() - last_blue_sent < MIN_MOVEMENT_SENDING_DELAY:
        return
    x, y = center[0] - point[0], center[1] - point[1] # note inversion of image
    largest = max(abs(x), abs(y))

    if largest == 0:
        return

    x /= largest
    y /= largest
    y = -y

    if time.time() - last_blue_sent > MIN_MOVEMENT_SENDING_DELAY * 10:
        print(f'Moving {x} {y}')

    send_move((x,y))

def draw_spell_img(pts):
    if len(pts) < 25:
        return

    pts_arr = np.array(pts)
    xs, ys = pts_arr[:, 0], pts_arr[:, 1]

    xs = process_xs(xs)
    ys = process_ys(ys)
    print(xs)

    bg = np.zeros((20, 20, 3), np.uint8)
    # Fill image with white color
    bg[:] = (255, 255, 255)


    for i in range(1, len(pts)):
        # if either of the tracked points are None, ignore
        # them
        if pts[i - 1] is None or pts[i] is None:
            continue

        start = (xs[i - 1], ys[i - 1])
        end = (xs[i], ys[i])

        cv2.line(bg, start, end, (0, 0, 0), 2)

    # Add border
    bg = cv2.copyMakeBorder(bg, 4, 4, 4, 4, cv2.BORDER_CONSTANT, value=(255, 255, 255))
    # Flip
    bg = cv2.flip(bg, 1)

    cv2.imwrite(f'bg-{time.time()}.png', bg)
    print('spell image written!')

    number = classify(bg)
    spell = NUMBER_TO_SPELL[number]
    print(f'\n\nClassified {number}, spell {spell} \n\n')

    send_spell(NUMBER_TO_SPELL[number])

prev, prev_num_pts = time.time(), 0

blue_last_seen = None
blue_center = None
blue_point = None
# keep looping
while True:
    # grab the current frame
    frame = vs.read()
    now = time.time()

    if now - prev > 0.4:
        if prev_num_pts == len(pts) and len(pts) != 0:
            draw_spell_img(pts)
            pts = deque(maxlen=args["buffer"])
        print(len(pts), blue_center)
        prev_num_pts = len(pts)

    # handle the frame from VideoCapture or VideoStream
    frame = frame[1] if args.get("video", False) else frame

    # if we are viewing a video and we did not grab a frame,
    # then we have reached the end of the video
    if frame is None:
        break

    # resize the frame, blur it, and convert it to the HSV
    # color space
    frame = imutils.resize(frame, width=600)
    blurblue = cv2.GaussianBlur(frame, (11, 11), 0)
    hsv = cv2.cvtColor(blurblue, cv2.COLOR_BGR2HSV)

    # construct a mask for the color "blue", then perform
    # a series of dilations and erosions to remove any small
    # blobs left in the mask
    mask = cv2.inRange(hsv, blueLower, blueUpper)
    mask = cv2.erode(mask, None, iterations=2)
    mask = cv2.dilate(mask, None, iterations=2)

    # find contours in the mask and initialize the current
    # (x, y) center of the ball
    cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
                            cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    center = None

    # only proceed if at least one contour was found
    if len(cnts) > 0:
        # find the largest contour in the mask, then use
        # it to compute the minimum enclosing circle and
        # centroid
        c = max(cnts, key=cv2.contourArea)
        ((x, y), radius) = cv2.minEnclosingCircle(c)
        M = cv2.moments(c)
        center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))

        # only proceed if the radius meets a minimum size
        if radius > 10:
            # draw the circle and centroid on the frame,
            # then update the list of tracked points
            cv2.circle(frame, (int(x), int(y)), int(radius),
                       (0, 255, 255), 2)
            cv2.circle(frame, center, 5, (0, 255, 0), -1)

        # update the points queue
        if not blue_center:
            blue_center = center
        else:
            blue_point = center

        if blue_point:
            cv2.line(frame, blue_center, blue_point, (0, 255, 0), 5)
            record_blue(blue_center, blue_point)

        blue_last_seen = now

    else:
        if blue_last_seen and now - blue_last_seen > 0.4:
            print('hmmmm')
            blue_last_seen = None
            blue_center = None
            blue_point = None
            send_move((0,0))


    # construct a mask for the color "yellow", then perform
    # a series of dilations and erosions to remove any small
    # blobs left in the mask
    mask = cv2.inRange(hsv, yellowLower, yellowUpper)
    mask = cv2.erode(mask, None, iterations=2)
    mask = cv2.dilate(mask, None, iterations=2)

    # find contours in the mask and initialize the current
    # (x, y) center of the ball
    cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
                            cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    center = None

    # only proceed if at least one contour was found
    if len(cnts) > 0:
        # find the largest contour in the mask, then use
        # it to compute the minimum enclosing circle and
        # centroid
        c = max(cnts, key=cv2.contourArea)
        ((x, y), radius) = cv2.minEnclosingCircle(c)
        M = cv2.moments(c)
        center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))

        # only proceed if the radius meets a minimum size
        if radius > 10:
            # draw the circle and centroid on the frame,
            # then update the list of tracked points
            cv2.circle(frame, (int(x), int(y)), int(radius),
                       (0, 255, 255), 2)
            cv2.circle(frame, center, 5, (0, 255, 0), -1)

        # update the points queue
        pts.appendleft(center)


        # loop over the set of tracked points
        for i in range(1, len(pts)):
            # if either of the tracked points are None, ignore
            # them
            if pts[i - 1] is None or pts[i] is None:
                continue

            # otherwise, compute the thickness of the line and
            # draw the connecting lines
            thickness = int(np.sqrt(args["buffer"] / float(i + 1)) * 2.5)
            cv2.line(frame, pts[i - 1], pts[i], (0, 255, 0), thickness)

    # show the frame to our screen
    cv2.imshow("Frame", cv2.flip(frame, 1))
    key = cv2.waitKey(1) & 0xFF

    # if the 'q' key is pressed, stop the loop
    if key == ord("q"):
        break

    if now - prev > 0.4:
       prev = now

# if we are not using a video file, stop the camera video stream
if not args.get("video", False):
    vs.stop()

# otherwise, release the camera
else:
    vs.release()

# close all windows
cv2.destroyAllWindows()
