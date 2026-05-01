import cv2
import numpy as np

# MediaPipe 0.10+ dropped solutions API on Windows - use OpenCV fallback
try:
    import mediapipe as mp
    try:
        _face_mesh_module = mp.solutions.face_mesh
        MEDIAPIPE_MODE = 'solutions'
    except AttributeError:
        MEDIAPIPE_MODE = None
except ImportError:
    MEDIAPIPE_MODE = None

HAAR_FACE  = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
HAAR_MOUTH = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_smile.xml')


class MouthMonitor:
    def __init__(self, config):
        self.mouth_threshold = config['detection']['mouth']['movement_threshold']
        self.mouth_movement_count = 0
        self.alert_logger = None
        self.face_mesh = None

        if MEDIAPIPE_MODE == 'solutions':
            try:
                self.face_mesh = _face_mesh_module.FaceMesh(
                    max_num_faces=1,
                    refine_landmarks=True,
                    min_detection_confidence=0.5,
                    min_tracking_confidence=0.5
                )
                print("Mouth detection: using MediaPipe solutions API")
            except Exception as e:
                print(f"Mouth detection: MediaPipe failed ({e}), using OpenCV fallback")
        else:
            print("Mouth detection: using OpenCV Haar cascade fallback")

    def set_alert_logger(self, alert_logger):
        self.alert_logger = alert_logger

    def _monitor_with_mediapipe(self, frame):
        results = self.face_mesh.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        if not results.multi_face_landmarks:
            return False

        lm = results.multi_face_landmarks[0]
        upper_lip = lm.landmark[13].y
        lower_lip = lm.landmark[14].y
        right_corner = lm.landmark[78].x
        left_corner  = lm.landmark[306].x

        mouth_open  = lower_lip - upper_lip
        mouth_width = abs(right_corner - left_corner)
        return mouth_open > 0.03 or mouth_width > 0.2

    def _monitor_with_opencv(self, frame):
        """Fallback: detect open mouth via smile/mouth Haar cascade"""
        gray  = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = HAAR_FACE.detectMultiScale(gray, 1.1, 5, minSize=(80, 80))
        if len(faces) == 0:
            return False

        fx, fy, fw, fh = faces[0]
        # Only look in lower half of face for mouth
        mouth_roi = gray[fy + fh//2 : fy + fh, fx : fx + fw]
        mouths = HAAR_MOUTH.detectMultiScale(mouth_roi, 1.7, 11)
        return len(mouths) > 0

    def monitor_mouth(self, frame):
        try:
            if self.face_mesh is not None:
                moving = self._monitor_with_mediapipe(frame)
            else:
                moving = self._monitor_with_opencv(frame)

            if moving:
                self.mouth_movement_count += 1
                if self.mouth_movement_count > self.mouth_threshold and self.alert_logger:
                    self.alert_logger.log_alert(
                        "MOUTH_MOVEMENT",
                        "Excessive mouth movement detected (possible talking)"
                    )
                    self.mouth_movement_count = 0
                return True
            else:
                self.mouth_movement_count = max(0, self.mouth_movement_count - 1)
                return False
        except Exception as e:
            if self.alert_logger:
                self.alert_logger.log_alert("MOUTH_DETECTION_ERROR", str(e))
            return False
