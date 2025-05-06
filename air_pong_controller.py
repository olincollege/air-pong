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
    """
    controller class for air-pong game.

    Attributes:
        del_angle: an int for the change in angle of paddle per press
        paddle_scaling: a list of two lists of integers for paddle zone factoring
            in meters.
            [x_init_box, x_dist, y_init_box, y_dist]
            - x_init_box: the starting x position for paddle zone
            - x_dist: the distance of travel for the paddle zone in x
            - y_init_box: the starting x position for paddle zone
            - y_dist: the distance of travel for the paddle zone in y
        vel_scaling = a float for the scaling factor of calculated velocity
            to model input velocity (0<vel_scaling<=1)
    """

    del_angle = 5
    paddle_scaling = [
        [0, 2.5, 1.5, 1],
        [2.5, 2.5, 1.5, 1],
    ]  # [x_init_box, x_dist, y_init_box, y_dist]
    vel_scaling = 0.1

    def __init__(self, model):
        """
        Start controller processes including keyboard monitoring and CV.

        Args:
            model: air pong PongModel object
        """
        self._model = model
        self._previous_position = [None, None]
        self._norm = [vector(1, 0, 0), vector(-1, 0, 0)]

        # pynput keyboard listener
        self._keyboard_listen = keyboard.Listener(
            on_press=self.on_press, on_release=self.on_release
        )
        self._keyboard_listen.start()
        self._latest_key = None

        # mediapipe landmarker
        self.cv_result = mp.tasks.vision.HandLandmarkerResult(
            handedness=[], hand_landmarks=[], hand_world_landmarks=[]
        )
        self.landmarker = mp.tasks.vision.HandLandmarker
        self.create_landmarker()
        self.cap = self.create_cap(attempt=0)

    def create_cap(self, attempt):
        """
        creates the videocapture element and checks for failed video opening.
        """
        cap = cv2.VideoCapture(0)
        time.sleep(0.5)
        if cap.isOpened():
            return cap
        elif attempt == 10:
            print("video capture FAILED, closing")
            self.close()
        else:
            print("video capture open failed, please restart")
            self.create_cap(attempt=attempt + 1)

    def on_press(self, key):  # REFACTOR AT SOME POINT
        """
        control rotation and serve when key is pressed by the player.

        Args:
            key: a pynput key object representing the key pressed
        """

        self._latest_key = key

        if key == keyboard.Key.up or key == keyboard.KeyCode.from_char("w"):
            # Serve ball
            self._model.serve()
        # check player one keyboard inputs
        elif key == keyboard.Key.left:
            # Get normal vector and rotate it counterclockwise
            new_norm = vector.rotate(
                self._norm[0],
                (self.del_angle * np.pi) / 180,
            )
            if new_norm.x > 0:
                self._norm[0] = new_norm
                self._model.update_paddle(
                    paddle_normal=self._norm[0],
                    paddle_position=self._model.paddle_position[0],
                    paddle_velocity=self._model.paddle_velocity[0],
                    player_paddle=0,
                )
        elif key == keyboard.Key.right:
            # Get normal vector and rotate it clockwise
            new_norm = vector.rotate(
                self._norm[0],
                (-self.del_angle * np.pi) / 180,
            )
            if new_norm.x > 0:
                self._norm[0] = new_norm
                self._model.update_paddle(
                    paddle_normal=self._norm[0],
                    paddle_position=self._model.paddle_position[0],
                    paddle_velocity=self._model.paddle_velocity[0],
                    player_paddle=0,
                )
        # check player two keyboard inputs
        elif key == keyboard.KeyCode.from_char("a"):
            # Get normal vector and rotate it counterclockwise
            new_norm = vector.rotate(
                self._norm[1],
                (self.del_angle * np.pi) / 180,
            )
            if new_norm.x < 0:
                self._norm[1] = new_norm
                self._model.update_paddle(
                    paddle_normal=self._norm[1],
                    paddle_position=self._model.paddle_position[1],
                    paddle_velocity=self._model.paddle_velocity[1],
                    player_paddle=1,
                )
        elif key == keyboard.KeyCode.from_char("d"):
            # Get normal vector and rotate it clockwise
            new_norm = vector.rotate(
                self._norm[1],
                (-self.del_angle * np.pi) / 180,
            )
            if new_norm.x < 0:
                self._norm[1] = new_norm
                self._model.update_paddle(
                    paddle_normal=self._norm[1],
                    paddle_position=self._model.paddle_position[1],
                    paddle_velocity=self._model.paddle_velocity[1],
                    player_paddle=1,
                )

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
        # pull frame
        _, frame = self.cap.read()
        frame = cv2.flip(frame, 1)
        # non-blocking landmarker execution
        self.detect_async(frame)

        # draw the landmarks on the page
        landmarked_frame = draw_landmarks_on_image(frame, self.cv_result)
        cv2.imshow("frame", landmarked_frame)

        # variables for easy tuning
        MIDDLE_FINGER_MCP = 9
        DEL_TIME = 1 / 30
        empty_landmark = mp.tasks.vision.HandLandmarkerResult(
            handedness=[], hand_landmarks=[], hand_world_landmarks=[]
        )

        # manipulate result
        if self.cv_result != empty_landmark:
            # get amount of hands
            for i, _ in enumerate(self.cv_result.handedness):
                player = (
                    0
                    if "Right" == self.cv_result.handedness[i][0].display_name
                    else 1
                )
                mid_pos = self.cv_result.hand_landmarks[i][MIDDLE_FINGER_MCP]
                prev_pos = self._previous_position[i]
                vel = vector(0, 0, 0)
                if prev_pos is not None:
                    vel = self.vel_scaling * vector(
                        (prev_pos.x - mid_pos.x) / DEL_TIME,
                        (prev_pos.y - mid_pos.y) / DEL_TIME,
                        (prev_pos.z - mid_pos.z) / DEL_TIME,
                    )

                self._previous_position[player] = mid_pos

                vect_mid_pos = vector(
                    self.paddle_scaling[player][0]
                    + self.paddle_scaling[player][1] * mid_pos.x,
                    self.paddle_scaling[player][2]
                    - self.paddle_scaling[player][3] * mid_pos.y,
                    mid_pos.z,
                )

                # update hand position in model
                norm = self._model.paddle_normal[player]
                self._model.update_paddle(
                    paddle_normal=norm,
                    paddle_position=vect_mid_pos,
                    paddle_velocity=vel,
                    player_paddle=player,
                )

    def hand_cv(self):
        """used to begin mediapipe hand detection"""

        # pull frame
        _, frame = self.cap.read()

        frame = cv2.flip(frame, 1)
        # non-blocking landmarker execution
        self.detect_async(frame)

    def detect_async(self, frame):
        """begin non-blocking detection of landmarks through the class landmarker"""
        # convert np frame to mp image
        if frame is not None:
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame)
            # detect landmarks
            self.landmarker.detect_async(
                image=mp_image, timestamp_ms=int(time.time() * 1000)
            )

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
            num_hands=2,  # track single hand for paddle
            min_hand_detection_confidence=0.1,
            min_hand_presence_confidence=0.1,
            min_tracking_confidence=0.1,
            result_callback=update_result,
        )

        # initialize landmarker from options
        self.landmarker = self.landmarker.create_from_options(options)

    @property
    def latest_key(self):
        """gets the latest key pressed on keyboard"""
        return self._latest_key


def draw_landmarks_on_image(
    rgb_image, detection_result: mp.tasks.vision.HandLandmarkerResult
):
    """
    Courtesy of https://github.com/googlesamples/mediapipe/blob/main/examples/hand_landmarker/python/hand_landmarker.ipynb

    Visualize the landmarks on the page for the game"""
    try:
        if detection_result.hand_landmarks == []:
            return rgb_image
        else:
            hand_landmarks_list = detection_result.hand_landmarks
            annotated_image = np.copy(rgb_image)

            # Loop through the detected hands to visualize.
            for idx, _ in enumerate(hand_landmarks_list):
                hand_landmarks = hand_landmarks_list[idx]

                # Draw the hand landmarks.
                hand_landmarks_proto = landmark_pb2.NormalizedLandmarkList()
                hand_landmarks_proto.landmark.extend(
                    [
                        landmark_pb2.NormalizedLandmark(
                            x=landmark.x, y=landmark.y, z=landmark.z
                        )
                        for landmark in hand_landmarks
                    ]
                )
                mp.solutions.drawing_utils.draw_landmarks(
                    annotated_image,
                    hand_landmarks_proto,
                    mp.solutions.hands.HAND_CONNECTIONS,
                    mp.solutions.drawing_styles.get_default_hand_landmarks_style(),
                    mp.solutions.drawing_styles.get_default_hand_connections_style(),
                )
            return annotated_image
    except Exception as e:
        print(f"running exception: {e}")
        return rgb_image
