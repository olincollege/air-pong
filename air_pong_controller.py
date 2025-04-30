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

    def __init__(self, model, player: bool, hand: str):
        """

        Args:
            model: air pong PongModel object
            player: a boolean, False = player 1 and True = player 2
            hand: the hand assigned to the player
        """
        self._player = player
        self._previous_position = None
        # keyboard listener
        self._keyboard_listen = keyboard.Listener(
            on_press=self.on_press, on_release=self.on_release
        )
        self._keyboard_listen.start()
        self._latest_key = None

        # create landmarker
        self.cv_result = mp.tasks.vision.HandLandmarkerResult(
            handedness=[], hand_landmarks=[], hand_world_landmarks=[]
        )
        self.landmarker = mp.tasks.vision.HandLandmarker
        self.create_landmarker()
        self.cap = cv2.VideoCapture(0)

    def on_press(self, key):
        """check if key is pressed pynput"""

        self._latest_key = key
        if self._player == 1:
            # check player one keyboard inputs
            if key == keyboard.Key.up:
                print(f"up's been pressed {key}")  ## ADD MODEL CONTROL
            elif key == keyboard.Key.down:
                print(f"down's been pressed {key}")  ## ADD MODEL CONTROL
            elif key == keyboard.Key.left:
                print(f"left's been pressed {key}")  ## ADD MODEL CONTROL
            elif key == keyboard.Key.right:
                print(f"right's been pressed {key}")  ## ADD MODEL CONTROL
        elif self._player == 2:
            # check player two keyboard inputs
            if key == keyboard.KeyCode.from_char("w"):
                print(f"w's been pressed {key}")  ## ADD MODEL CONTROL
            elif key == keyboard.KeyCode.from_char("s"):
                print(f"down's been pressed {key}")  ## ADD MODEL CONTROL
            elif key == keyboard.KeyCode.from_char("a"):
                print(f"left's been pressed {key}")  ## ADD MODEL CONTROL
            elif key == keyboard.KeyCode.from_char("d"):
                print(f"right's been pressed {key}")  ## ADD MODEL CONTROL

    def on_release(self, key, injected):
        """check if key is released"""
        self._latest_key = None
        if key == keyboard.Key.esc:
            # Stop listener
            print("wants to end")

    def get_hand(self):
        """
        Returns the hand inputs from mediapipe after some processing.

        Returns:
            pos: a vpython vector representing the xyz position of hand
            vel: a vpython vector of velocity in m/s
            angle: a vpython normal vector to the center joint of palm
        """
        MIDDLE_FINGER_MCP = 9
        INDEX_FINGER_MCP = 5
        PINKY_FINGER_MCP = 17
        DEL_TIME = 1 / 30
        empty_landmark = mp.tasks.vision.HandLandmarkerResult(
            handedness=[], hand_landmarks=[], hand_world_landmarks=[]
        )

        if self.cv_result != empty_landmark:
            mid_pos = self.cv_result.hand_world_landmarks[0][MIDDLE_FINGER_MCP]
            # Used for angle of paddle
            # index_mcp = self.cv_result.hand_world_landmarks[0][INDEX_FINGER_MCP]
            # pink_mcp = self.cv_result.hand_world_landmarks[0][PINKY_FINGER_MCP]
            prev_pos = self._previous_position

            if prev_pos is not None:
                vel = (
                    np.sqrt(
                        (prev_pos.x - mid_pos.x) ** 2
                        + (prev_pos.y - mid_pos.y) ** 2
                    )
                    / DEL_TIME
                )

                self._previous_position = mid_pos

                ## ADD MODEL CONTROL

            print(f"z pos is {mid_pos.z}")
            print(self.cv_result.handedness[0][0].category_name)

    def hand_cv(self):
        """used to begin mediapipe hand detection"""

        # pull frame
        _, frame = self.cap.read()
        # non-blocking landmarker execution
        self.detect_async(frame)
        # print(f"cv result is {self.cv_result}")

    def detect_async(self, frame):
        """begin non-blocking detection of landmarks through the class landmarker"""
        # convert np frame to mp image
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame)
        # detect landmarks
        self.landmarker.detect_async(
            image=mp_image, timestamp_ms=int(time.time() * 1000)
        )

        # print(f"detected landmarks: {self.cv_result}")

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
            min_hand_detection_confidence=0.1,  # NEEDS TO BE TUNED
            min_hand_presence_confidence=0.1,  # NEEDS TO BE TUNED
            min_tracking_confidence=0.1,  # NEEDS TO BE TUNED
            result_callback=update_result,
        )

        # initialize landmarker from options
        self.landmarker = self.landmarker.create_from_options(options)

    def release(self):
        """release everything"""
        cap.release()
        cv2.destroyAllWindows()

    def close(self):
        """close all running processes for controller"""
        self.landmarker.close()

    @property
    def latest_key(self):
        """gets the latest key pressed on keyboard"""
        return self._latest_key
