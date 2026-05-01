import cv2
import numpy as np
from datetime import datetime

# MediaPipe 0.10+ uses Tasks API - solutions API removed on Windows
try:
    import mediapipe as mp
    from mediapipe.tasks import python as mp_python
    from mediapipe.tasks.python import vision as mp_vision

    _base_options = mp_python.BaseOptions(model_asset_path=None)

    # Try legacy solutions first (Linux/Mac), fall back to tasks API
    try:
        _face_mesh_module = mp.solutions.face_mesh
        MEDIAPIPE_MODE = 'solutions'
    except AttributeError:
        MEDIAPIPE_MODE = 'tasks'

except ImportError:
    MEDIAPIPE_MODE = None

# Fallback: use OpenCV Haar cascade for basic eye detection
import os
HAAR_EYE = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')
HAAR_FACE = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')


class EyeTracker:
    def __init__(self, config):
        self.config = config
        self.gaze_direction = "center"
        self.eye_ratio = 0.3
        self.gaze_changes = 0
        self.last_gaze_change = datetime.now()
        self.alert_logger = None
        self.face_mesh = None

        self.LEFT_EYE_INDICES  = [33, 160, 158, 133, 153, 144]
        self.RIGHT_EYE_INDICES = [362, 385, 387, 263, 373, 380]

        if MEDIAPIPE_MODE == 'solutions':
            try:
                self.face_mesh = _face_mesh_module.FaceMesh(
                    max_num_faces=1,
                    refine_landmarks=True,
                    min_detection_confidence=0.5,
                    min_tracking_confidence=0.5
                )
                print("Eye tracking: using MediaPipe solutions API")
            except Exception as e:
                print(f"Eye tracking: MediaPipe solutions failed ({e}), using OpenCV fallback")
        else:
            print("Eye tracking: using OpenCV Haar cascade fallback")

    def set_alert_logger(self, alert_logger):
        self.alert_logger = alert_logger

    def _calculate_ear(self, eye_points):
        A = np.linalg.norm(eye_points[1] - eye_points[5])
        B = np.linalg.norm(eye_points[2] - eye_points[4])
        C = np.linalg.norm(eye_points[0] - eye_points[3])
        return (A + B) / (2.0 * C) if C > 0 else 0.3

    def _track_with_mediapipe(self, frame):
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(rgb)

        if not results.multi_face_landmarks:
            return self.gaze_direction, self.eye_ratio

        lm = results.multi_face_landmarks[0]
        h, w = frame.shape[:2]

        def pts(indices):
            return np.array([(lm.landmark[i].x * w, lm.landmark[i].y * h) for i in indices])

        left_pts  = pts(self.LEFT_EYE_INDICES)
        right_pts = pts(self.RIGHT_EYE_INDICES)

        self.eye_ratio = (self._calculate_ear(left_pts) + self._calculate_ear(right_pts)) / 2.0

        nose = np.array([lm.landmark[4].x * w, lm.landmark[4].y * h])
        horiz = ((np.mean(left_pts, axis=0)[0] + np.mean(right_pts, axis=0)[0]) / 2) - nose[0]

        new_gaze = "left" if horiz < -15 else "right" if horiz > 15 else "center"
        self._update_gaze(new_gaze)
        return self.gaze_direction, self.eye_ratio

    def _track_with_opencv(self, frame):
        """Fallback: detect eyes via Haar cascade and estimate gaze from position"""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        h, w = frame.shape[:2]

        faces = HAAR_FACE.detectMultiScale(gray, 1.1, 5, minSize=(80, 80))
        if len(faces) == 0:
            return self.gaze_direction, self.eye_ratio

        fx, fy, fw, fh = faces[0]
        face_gray = gray[fy:fy+fh, fx:fx+fw]
        eyes = HAAR_EYE.detectMultiScale(face_gray, 1.1, 5)

        if len(eyes) >= 2:
            self.eye_ratio = 0.35  # eyes open
            # Estimate gaze from eye center relative to face center
            eye_centers_x = [ex + ew // 2 for ex, ey, ew, eh in eyes[:2]]
            avg_eye_x = np.mean(eye_centers_x)
            face_center_x = fw / 2
            diff = avg_eye_x - face_center_x
            new_gaze = "left" if diff < -fw * 0.1 else "right" if diff > fw * 0.1 else "center"
            self._update_gaze(new_gaze)
        elif len(eyes) == 0:
            self.eye_ratio = 0.15  # possibly closed

        return self.gaze_direction, self.eye_ratio

    def _update_gaze(self, new_gaze):
        current_time = datetime.now()
        if new_gaze != self.gaze_direction:
            self.gaze_changes += 1
            self.gaze_direction = new_gaze
            self.last_gaze_change = current_time

        if (self.gaze_changes > 3 and
                (current_time - self.last_gaze_change).total_seconds() < 2 and
                self.alert_logger):
            self.alert_logger.log_alert("EYE_MOVEMENT", "Excessive eye movement detected")
            self.gaze_changes = 0

    def track_eyes(self, frame):
        try:
            if self.face_mesh is not None:
                return self._track_with_mediapipe(frame)
            else:
                return self._track_with_opencv(frame)
        except Exception as e:
            if self.alert_logger:
                self.alert_logger.log_alert("EYE_TRACKING_ERROR", str(e))
            return self.gaze_direction, self.eye_ratio
