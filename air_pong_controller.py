"""MVC controller class for hand and keybaord inputs"""

import time
import cv2
import mediapipe as mp
from mediapipe import solutions  # pylint: disable=unused-import
from mediapipe.framework.formats import (  # pylint: disable=no-name-in-module
    landmark_pb2,  # pylint: disable=no-name-in-module
)  # pylint: disable=no-name-in-module
import numpy as np
from vpython import vector
from pynput import keyboard


class PongController:
    """
    controller class for air-pong game.

    Attributes:
        del_angle: an int for the change in angle of paddle per key press
        paddle_scaling: a list of two lists of integers for paddle zone factoring
            in meters.
            [x_init_box, x_dist, y_init_box, y_dist]
            - x_init_box: the starting x position for paddle zone
            - x_dist: the distance of travel for the paddle zone in x
            - y_init_box: the starting x position for paddle zone
            - y_dist: the distance of travel for the paddle zone in y
        vel_scaling = a float for the scaling factor of calculated velocity
            to model input velocity (0<vel_scaling<=1). Used in get_hand().
        middle_finger_mcp: an int representing the middle finger knuckle index
        del_time: a float represnting the change in timestep for calculating velocity
        empty_landmark = a mp HandLandmarkerResult object for result comparisons
    """

    del_angle = 5
    paddle_scaling = [
        [0, 2.5, 1.5, 1],
        [2.5, 2.5, 1.5, 1],
    ]  # [x_init_box, x_dist, y_init_box, y_dist]
    vel_scaling = 0.1
    middle_finger_mcp = 9
    del_time = 1 / 30
    empty_landmark = mp.tasks.vision.HandLandmarkerResult(
        handedness=[], hand_landmarks=[], hand_world_landmarks=[]
    )

    def __init__(self, model):
        """
        Start controller processes including keyboard monitoring and CV.

        Args:
            model: air pong PongModel object

        Attributes:
            self._model: a PongModel object instance
            self._previous_position: a list of vectors for each player velocity calculations.
                Populated when running.
            self._norm: a list of normal vectors for each player
            self._keyboard_listen: a pynput keybaord listener object that runs async
            self.cv_result: a HandLandmarksResult object of the latest detection result from the
                mp callback
            self.landmarker: an mp HandLandmarker object for hand detection
            self.cap: a cv2 VideoCapture object to obtain camera frames
        """
        self._model = model
        self._previous_position = [None, None]
        self._norm = [vector(1, 0, 0), vector(-1, 0, 0)]

        # pynput keyboard listener
        self._keyboard_listen = keyboard.Listener(
            on_press=self.on_press, on_release=self.on_release
        )
        self._keyboard_listen.start()

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

        Args:
            attempt: an integer representing the current attempt
        """
        cap = cv2.VideoCapture(0)  # pylint: disable=no-member
        time.sleep(0.5)
        if cap.isOpened():
            return cap
        elif attempt == 10:
            print("video capture FAILED, closing")
        else:
            print("video capture open failed, please restart")
            self.create_cap(attempt=attempt + 1)

    def on_press(self, key):
        """
        Method called when pynput detects a key has been pressed.

        Args:
            key: a pynput key object representing the key pressed
        """
        if key == keyboard.Key.up or key == keyboard.KeyCode.from_char("w"):
            # Serve ball
            self._model.serve()
        # check player one keyboard inputs
        elif key == keyboard.Key.left:
            # Get normal vector and rotate it counterclockwise
            self.rotate_paddle(0, False)
        elif key == keyboard.Key.right:
            # Get normal vector and rotate it clockwise
            self.rotate_paddle(0, True)
        # check player two keyboard inputs
        elif key == keyboard.KeyCode.from_char("a"):
            # Get normal vector and rotate it counterclockwise
            self.rotate_paddle(1, False)
        elif key == keyboard.KeyCode.from_char("d"):
            # Get normal vector and rotate it clockwise
            self.rotate_paddle(1, True)

    def rotate_paddle(self, player: int, clockwise: bool):
        """
        Rotate given players paddle normal vector and pass it to the model.

        Args:
            player: an int (0 or 1) representing which player is being targeted
            clockwise: a book flag for clockwise rotation
        """
        direction_operator = -1 if clockwise else 1
        new_norm = vector.rotate(
            self._norm[player],
            (direction_operator * self.del_angle * np.pi) / 180,
        )
        # prevent paddle overrotation
        if (new_norm.x < 0 and bool(player)) or (
            new_norm.x > 0 and not bool(player)
        ):

            self._norm[player] = new_norm
            self._model.update_paddle(
                paddle_normal=self._norm[player],
                paddle_position=self._model.paddle_position[player],
                paddle_velocity=self._model.paddle_velocity[player],
                player_paddle=player,
            )

    def on_release(self, key):
        """
        Method called when pynput detects a key has been released.

        Args:
            key: a pynput key object representing the key pressed
        """
        if key == keyboard.Key.esc:
            # Stop listener
            print("wants to end")

    def update_hand(self):
        """
        Pulls the latest hand detection result, processes it, then passes
        that to the model.

        Since the model only operates in a physical space, detected scales from
        mediapipe hand_landmarks need to be converted into position (in meters)
        and velocity (in meters per second).
        """
        # run and visualize hand detection
        self.hand_cv()

        # manipulate result
        if self.cv_result != self.empty_landmark:
            # get amount of hands
            for i, _ in enumerate(self.cv_result.handedness):
                player = (
                    0
                    if "Right" == self.cv_result.handedness[i][0].display_name
                    else 1
                )
                mid_pos = self.cv_result.hand_landmarks[i][
                    self.middle_finger_mcp
                ]

                # calculate velocity
                prev_pos = self._previous_position[i]
                vel = vector(0, 0, 0)
                if prev_pos is not None:
                    vel = self.vel_scaling * vector(
                        (prev_pos.x - mid_pos.x) / self.del_time,
                        (prev_pos.y - mid_pos.y) / self.del_time,
                        (prev_pos.z - mid_pos.z) / self.del_time,
                    )
                self._previous_position[player] = mid_pos

                # scale hand position to bounding box
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
        """
        Grabs the latest cv2 frame, passes that into a non-blocking method for detection,
        and visualizes the latest processed result.
        """
        # pull frame from cv2
        _, frame = self.cap.read()
        frame = cv2.flip(frame, 1)
        # run model on frame
        self.detect_async(frame)

        # draw the landmarks on the page for visualization
        landmarked_frame = draw_landmarks_on_image(frame, self.cv_result)
        cv2.imshow("frame", landmarked_frame)

    def detect_async(self, frame):
        """
        begin non-blocking detection of landmarks with mediapipe.

        Args:
            frame: a numpy RGB frame object
        """
        # convert np frame to mp image
        if frame is not None:
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame)
            # detect landmarks
            self.landmarker.detect_async(
                image=mp_image, timestamp_ms=int(time.time() * 1000)
            )

    def create_landmarker(self):
        """
        Initializes the mediapipe landmarker object from the hand landmarker.task
        in livestream mode.

        Parameters resource
        https://ai.google.dev/edge/mediapipe/solutions/vision/hand_landmarker/python#configuration_options
        """

        # callback function to grab latest cv result
        def update_result(
            result: mp.tasks.vision.HandLandmarkerResult,  # type: ignore
            output_image: mp.Image,  # pylint: disable=unused-argument
            timestamp_ms: int,  # pylint: disable=unused-argument
        ):
            self.cv_result = result

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


def draw_landmarks_on_image(
    rgb_image, detection_result: mp.tasks.vision.HandLandmarkerResult
):
    """
    Google's fucntion to draw detected hand landmarks onto the given rgb frame.

    Courtesy of
    https://github.com/googlesamples/mediapipe/blob/main/examples/hand_landmarker/python/hand_landmarker.ipynb

    Args:
        rgb_image a numpy RGB image object
        detection_result: a mp HandLandmarkerResult object of desired landmarks to draw
    """
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
