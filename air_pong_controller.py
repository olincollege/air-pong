"""MVC controller class for hand and keybaord inputs"""

import threading
import time
import cv2
import mediapipe as mp
from mediapipe import solutions
from mediapipe.framework.formats import landmark_pb2
import numpy as np
from vpython import vector
from pynput import keyboard


class PongController:
    """controller class for air-pong game"""

    def __init__(self, model, player):
        self._player = player
        print("initializing controller")
        self._running = True

        # keyboard listener
        self._keyboard_listen = keyboard.Listener(
            on_press=self.on_press, on_release=self.on_release
        )
        self._keyboard_listen.start()
        self._latest_key = None

        # create landmarker
        self.cv_result = mp.tasks.vision.HandLandmarkerResult
        self.landmarker = mp.tasks.vision.HandLandmarker
        self.create_landmarker()

        # threading
        self.cv_thread = threading.Thread(target=self.hand_cv)
        self.cv_thread.start()

    def on_press(self, key):
        """check if key is pressed pynput"""

        self._latest_key = key
        if self._player == 1:
            # check player one keyboard inputs
            if key == keyboard.Key.up:
                print(f"up's been pressed {key}")
            elif key == keyboard.Key.down:
                print(f"down's been pressed {key}")
            elif key == keyboard.Key.left:
                print(f"left's been pressed {key}")
            elif key == keyboard.Key.right:
                print(f"right's been pressed {key}")
        elif self._player == 2:
            # check player two keyboard inputs
            if key == keyboard.KeyCode.from_char("w"):
                print(f"w's been pressed {key}")
            elif key == keyboard.KeyCode.from_char("s"):
                print(f"down's been pressed {key}")
            elif key == keyboard.KeyCode.from_char("a"):
                print(f"left's been pressed {key}")
            elif key == keyboard.KeyCode.from_char("d"):
                print(f"right's been pressed {key}")

    def on_release(self, key, injected):
        """check if key is released"""
        self._latest_key = None
        if key == keyboard.Key.esc:
            # Stop listener
            print("wants to end")

    def create_landmarker(self):
        """creates the landmarker object from the hand landmarker.task"""

        # callback function to grab latest cv result
        def update_result(
            result: mp.tasks.vision.HandLandmarkerResult,
            output_image: mp.Image,
            timestamp_ms: int,
        ):  #
            self.cv_result = result

        options = mp.tasks.vision.HandLandmarkerOptions(
            base_options=mp.tasks.BaseOptions(
                model_asset_path="hand_landmarker.task"
            ),  # path to model
            running_mode=mp.tasks.vision.RunningMode.LIVE_STREAM,  # running live stream
            num_hands=1,  # track single hand for paddle
            min_hand_detection_confidence=0.3,  # NEEDS TO BE TUNED
            min_hand_presence_confidence=0.3,  # NEEDS TO BE TUNED
            min_tracking_confidence=0.3,  # NEEDS TO BE TUNED
            result_callback=update_result,
        )

        # initialize landmarker from options
        self.landmarker = self.landmarker.create_from_options(options)

    def hand_cv(self):
        """used to begin mediapipe hand detection"""
        # access webcam
        cap = cv2.VideoCapture(0)

        self._cap_width = cv2.CAP_PROP_FRAME_WIDTH
        self._cap_height = cv2.CAP_PROP_FRAME_HEIGHT
        self._cap_timestamp = cv2.CAP_PROP_POS_MSEC

        while self._running:
            # pull frame
            _, frame = cap.read()
            # mirror frame
            frame = cv2.flip(frame, 1)
            # non-blocking landmarker execution
            self.detect_async(frame)
            # print(f"cv result is {self.cv_result}")

        # release everything
        cap.release()
        cv2.destroyAllWindows()
        # close local landmarker

    def detect_async(self, frame):
        """begin non-blocking detection of landmarks through the class landmarker"""
        # convert np frame to mp image
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame)
        # detect landmarks
        self.landmarker.detect_async(
            image=mp_image, timestamp_ms=int(time.time() * 1000)
        )

    def get_hand(self):
        """
        Returns the hand inputs from mediapipe after some processing.

        Returns:
            pos: a vpython vector representing the xyz position of hand
            vel: a vpython vector of velocity in m/s
            angle: a vpython normal vector to the center joint of palm
        """
        middle_knuckle = 9
        try:
            if self.cv_result != mp.tasks.vision.HandLandmarkerResult:
                print(self.cv_result.hand_landmarks[0][middle_knuckle])
        except:
            w = 1

    def close(self):
        """close all running processes for controller"""
        self._running = False
        self.landmarker.close()

    @property
    def latest_key(self):
        """gets the latest key pressed on keyboard"""
        return self._latest_key
