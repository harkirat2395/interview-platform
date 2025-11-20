"""
Headless mode fixes for Azure VM deployment
"""
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
os.environ['CUDA_VISIBLE_DEVICES'] = '-1'  # Disable GPU
os.environ['GLOG_minloglevel'] = '2'  # Reduce glog verbosity

# Force CPU mode for MediaPipe
import mediapipe as mp
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles

# Configure MediaPipe for CPU
def get_mediapipe_config():
    return {
        'static_image_mode': False,
        'max_num_faces': 1,
        'refine_landmarks': False,  # Disable refinement for performance
        'min_detection_confidence': 0.5,
        'min_tracking_confidence': 0.5
    }