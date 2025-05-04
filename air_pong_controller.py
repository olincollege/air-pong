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
        self._model = model
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
        """
        check if key is pressed with pynput

        Args:
            key: a pynput key object representing the key pressed
        """

        self._latest_key = key
        if self._player == 1:
            # check player one keyboard inputs
            if key == keyboard.Key.up:
                print(f"key {key} pressed")
                # self._model.serve()
                # Serve ball
                no = None
            elif key == keyboard.Key.left:
                print(f"key {key} pressed")
                # Get normal vector and rotate it left
                norm = self._model.paddle_normal
                new_norm = 5
                # self._model.update_paddle(paddle_normal=new_norm)
            elif key == keyboard.Key.right:
                print(f"key {key} pressed")
                norm = self._model.paddle_normal
                new_norm = 5
                # self._model.update_paddle(paddle_normal=new_norm)
        elif self._player == 2:
            # check player two keyboard inputs
            if key == keyboard.KeyCode.from_char("w"):
                print(f"key {key} pressed")
                # Serve ball
                # self._model.serve()
                no = None
            elif key == keyboard.KeyCode.from_char("a"):
                print(f"key {key} pressed")
                # Get normal vector and rotate it left
                norm = self._model.paddle_normal
                new_norm = 5
                # self._model.update_paddle(paddle_normal=new_norm)
            elif key == keyboard.KeyCode.from_char("d"):
                print(f"key {key} pressed")
                # Get normal vector and rotate it right
                norm = self._model.paddle_normal
                new_norm = 5
                # self._model.update_paddle(paddle_normal=new_norm)

    def on_release(self, key):
        """check if key is released"""
        self._latest_key = None
        if key == keyboard.Key.esc:
            # Stop listener
            print("wants to end")

    def update_hand(self):
        """
        Create the hand for the

        Returns:
            pos: a vpython vector representing the xyz position of hand
            vel: a vpython vector of velocity in m/s
            angle: a vpython normal vector to the center joint of palm
        """
        self.hand_cv()

        MIDDLE_FINGER_MCP = 9
        DEL_TIME = 1 / 30
        empty_landmark = mp.tasks.vision.HandLandmarkerResult(
            handedness=[], hand_landmarks=[], hand_world_landmarks=[]
        )

        if self.cv_result != empty_landmark:
            print("in if")
            mid_pos = self.cv_result.hand_landmarks[0][MIDDLE_FINGER_MCP]
            prev_pos = self._previous_position
            vel = 0
            if prev_pos is not None:
                vel = (
                    np.sqrt(
                        (prev_pos.x - mid_pos.x) ** 2
                        + (prev_pos.y - mid_pos.y) ** 2
                    )
                    / DEL_TIME
                )

            self._previous_position = mid_pos

            # update hand position in model
            vect_mid_pos = vector(mid_pos.x, mid_pos.y, mid_pos.z)
            print(f"pos is {vect_mid_pos}")
            print(f"vel is {vel}")
            norm = self._model.paddle_normal
            self._model.update_paddle(
                paddle_normal=norm,
                paddle_position=vect_mid_pos,
                paddle_velocity=vel,
            )

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
        print(f"frame is {frame}")
        if frame is not None:
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
            #

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
