"""MVC controller class for hand and keybaord inputs"""

import threading
import time
import cv2
import mediapipe as mp
from mediapipe import solutions
from mediapipe.framework.formats import landmark_pb2
import numpy as np


class PongController:
    """controller class for air-pong game"""

    def __init__(
        self, is_debug=True
    ):  # THIS LINE TO BE CHANGED ONCE FINISHED _degug = False
        print("initializing controller")
        self._debug = is_debug
        self._running = True

        # define cv handlandmarker callback
        self.cv_result = mp.tasks.vision.HandLandmarkerResult
        # define class landmarker
        self.landmarker = mp.tasks.vision.HandLandmarker
        # create and assign self.landmarker as landmarker
        self.create_landmarker()

        print("past landmarker")
        # threading
        self.cv_thread = threading.Thread(target=self.hand_cv)
        print("define thread")
        self.cv_thread.start()
        print("started thread and finishing init")

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

        while self._running:
            # pull frame
            _, frame = cap.read()
            # mirror frame
            frame = cv2.flip(frame, 1)
            # non-blocking landmarker execution
            self.detect_async(frame)
            print(f"cv result is {self.cv_result}")
            # draw the landmarks on the page
            if self._debug:
                landmarked_frame = draw_landmarks_on_image(
                    frame, self.cv_result
                )
                cv2.imshow("frame", landmarked_frame)
                if cv2.waitKey(1) == ord("q"):
                    break

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

    def close(self):
        """close all running processes for controller"""
        self._running = False
        self.landmarker.close()


def draw_landmarks_on_image(
    rgb_image, detection_result: mp.tasks.vision.HandLandmarkerResult
):
    """
    Courtesy of https://github.com/googlesamples/mediapipe/blob/main/examples/hand_landmarker/python/hand_landmarker.ipynb

    Draws detected landmarks from model on a given image

    Args:
        rgb_image: a mediapipe image object
        detection_result: a handlandmarker object containing detected hands

    Return:
        annotated_image: a numpy rgb image array
    """
    try:
        if detection_result.landmarks() == []:
            return rgb_image
        else:
            hand_landmarks_list = detection_result.landmarks()
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
