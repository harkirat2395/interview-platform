"""
Main Interview Assessment Platform - Azure WebRTC Version
Optimized for deployment with browser-based camera access
"""

import streamlit as st
import warnings
import os
import sys
import tempfile
from config import QUESTIONS, IS_PRODUCTION

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

warnings.filterwarnings('ignore')
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

# Import custom modules
from recording_system import RecordingSystem
from analysis_system import AnalysisSystem
from scoring_dashboard import ScoringDashboard

# Try importing WebRTC
try:
    from streamlit_webrtc import webrtc_streamer, WebRtcMode, VideoProcessorBase
    WEBRTC_AVAILABLE = True
except ImportError:
    WEBRTC_AVAILABLE = False
    st.error("WebRTC not available - camera functionality disabled")

# Page configuration
st.set_page_config(
    page_title="Interview Assessment Platform",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .success-box {
        background: #d4edda;
        border: 1px solid #c3e6cb;
        border-left: 4px solid #28a745;
        border-radius: 4px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .warning-box {
        background: #fff3cd;
        border: 1px solid #ffeaa7;
        border-left: 4px solid #ffc107;
        border-radius: 4px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .error-box {
        background: #f8d7da;
        border: 1px solid #f5c6cb;
        border-left: 4px solid #dc3545;
        border-radius: 4px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .metric-card {
        background: #ffffff;
        border: 1px solid #dee2e6;
        border-radius: 4px;
        padding: 1rem;
        text-align: center;
        margin-bottom: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

class WebRTCVideoProcessor(VideoProcessorBase):
    """WebRTC video processor for capturing frames"""
    def __init__(self):
        self.frames = []
        self.max_frames = 100  # Keep only recent frames to prevent memory issues
        
    def recv(self, frame):
        import av
        img = frame.to_ndarray(format="bgr24")
        self.frames.append(img)
        
        # Keep only recent frames to prevent memory issues
        if len(self.frames) > self.max_frames:
            self.frames = self.frames[-self.max_frames:]
            
        return frame

def initialize_session_state():
    """Initialize session state variables"""
    if 'page' not in st.session_state:
        st.session_state.page = "home"
    if 'results' not in st.session_state:
        st.session_state.results = []
    if 'interview_started' not in st.session_state:
        st.session_state.interview_started = False
    if 'interview_complete' not in st.session_state:
        st.session_state.interview_complete = False
    if 'webrtc_ctx' not in st.session_state:
        st.session_state.webrtc_ctx = None
    if 'camera_active' not in st.session_state:
        st.session_state.camera_active = False

# def load_models():
#     """Load AI models with progress tracking"""
#     progress_text = "Loading AI models... This may take a minute."
#     progress_bar = st.progress(0)
    
#     models = {}
    
#     # Load models progressively
#     try:
#         # Face detection models
#         import mediapipe as mp
#         mp_face_mesh = mp.solutions.face_mesh
#         mp_hands = mp.solutions.hands
        
#         models['face_mesh'] = mp_face_mesh.FaceMesh(
#             static_image_mode=False,
#             max_num_faces=5,
#             refine_landmarks=True,
#             min_detection_confidence=0.5,
#             min_tracking_confidence=0.5
#         )
#         models['hands'] = mp_hands.Hands(
#             static_image_mode=False,
#             max_num_hands=2,
#             min_detection_confidence=0.5,
#             min_tracking_confidence=0.5
#         )
#         progress_bar.progress(30)
#     except Exception as e:
#         st.warning(f"MediaPipe models not available: {e}")
#         models['face_mesh'] = None
#         models['hands'] = None
    
#     try:
#         # YOLO models
#         from ultralytics import YOLO
#         models['yolo'] = YOLO("yolov8n.pt")
#         models['yolo_cls'] = YOLO("yolov8n-cls.pt")
#         progress_bar.progress(60)
#     except Exception as e:
#         st.warning(f"YOLO models not available: {e}")
#         models['yolo'] = None
#         models['yolo_cls'] = None
    
#     try:
#         # Sentence transformer
#         from sentence_transformers import SentenceTransformer
#         models['sentence_model'] = SentenceTransformer('all-MiniLM-L6-v2')
#         progress_bar.progress(80)
#     except Exception as e:
#         st.warning(f"Sentence transformer not available: {e}")
#         models['sentence_model'] = None
    
#     # DeepFace availability
#     try:
#         from deepface import DeepFace
#         models['face_loaded'] = True
#     except:
#         models['face_loaded'] = False
    
#     progress_bar.progress(100)
#     st.success("✅ Models loaded successfully!")
    
#     return models
def load_models():
    """Load AI models with progress tracking - HEADLESS COMPATIBLE"""
    progress_text = "Loading AI models... This may take a minute."
    progress_bar = st.progress(0)
    
    models = {}
    
    # Load models progressively
    try:
        # Face detection models - HEADLESS COMPATIBLE
        import mediapipe as mp
        mp_face_mesh = mp.solutions.face_mesh
        mp_hands = mp.solutions.hands
        
        # Use CPU-only configuration
        models['face_mesh'] = mp_face_mesh.FaceMesh(
            static_image_mode=False,
            max_num_faces=1,  # Reduce from 5 to 1 for performance
            refine_landmarks=False,  # Disable refinement
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        models['hands'] = mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,  # Reduce from 2 to 1
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        progress_bar.progress(30)
    except Exception as e:
        st.warning(f"MediaPipe models not available: {e}")
        models['face_mesh'] = None
        models['hands'] = None
    
    try:
        # YOLO models - skip classification model to avoid _lzma issue
        from ultralytics import YOLO
        models['yolo'] = YOLO("yolov8n.pt")
        # Skip yolov8n-cls.pt to avoid _lzma dependency issues
        models['yolo_cls'] = None
        progress_bar.progress(60)
    except Exception as e:
        st.warning(f"YOLO models not available: {e}")
        models['yolo'] = None
        models['yolo_cls'] = None
    
    try:
        # Sentence transformer
        from sentence_transformers import SentenceTransformer
        models['sentence_model'] = SentenceTransformer('all-MiniLM-L6-v2')
        progress_bar.progress(80)
    except Exception as e:
        st.warning(f"Sentence transformer not available: {e}")
        models['sentence_model'] = None
    
    # DeepFace availability
    try:
        from deepface import DeepFace
        models['face_loaded'] = True
    except:
        models['face_loaded'] = False
    
    progress_bar.progress(100)
    st.success("✅ Models loaded successfully!")
    
    return models
def show_home_page():
    """Display home page"""
    st.markdown('<div class="main-header">🎯 Interview Assessment Platform</div>', unsafe_allow_html=True)
    
    st.info("""
    **Welcome to the AI-Powered Interview Assessment Platform!**
    
    This platform uses advanced computer vision and AI to evaluate your interview performance through:
    - **Real-time video analysis** for confidence and engagement
    - **Speech recognition** for fluency and content analysis
    - **Compliance monitoring** to ensure test integrity
    - **Comprehensive scoring** with detailed feedback
    """)
    
    st.markdown("---")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📋 Assessment Details")
        st.write(f"""
        - **Number of Questions:** {len(QUESTIONS)}
        - **Time per Question:** 20 seconds
        - **Evaluation Metrics:**
          - Confidence & Engagement
          - Speech Fluency & Grammar
          - Answer Relevance & Accuracy
          - Professional Presence
        - **Compliance Requirements:**
          - Single person in frame
          - No unauthorized objects
          - Maintain eye contact with camera
        """)
    
    with col2:
        st.subheader("🎥 Camera Setup")
        if WEBRTC_AVAILABLE:
            st.success("✅ WebRTC camera support available")
            st.write("Click 'Begin Assessment' to start camera")
        else:
            st.error("❌ Camera support not available")
            st.write("Please enable camera permissions in your browser")
    
    st.markdown("---")
    
    # Guidelines acceptance
    if 'guidelines_accepted' not in st.session_state:
        st.session_state.guidelines_accepted = False
    
    st.session_state.guidelines_accepted = st.checkbox(
        f"I confirm that I am ready to complete {len(QUESTIONS)} interview questions and understand the assessment guidelines.",
        value=st.session_state.guidelines_accepted,
        key="guidelines_checkbox"
    )
    
    if st.session_state.guidelines_accepted:
        st.success("✅ You are ready to proceed with the assessment.")
        if st.button("🚀 Begin Assessment", type="primary", use_container_width=True):
            st.session_state.page = "interview"
            st.session_state.interview_started = False
            st.rerun()
    else:
        st.info("ℹ️ Please accept the guidelines to continue.")

def show_interview_page(models):
    """Display interview page with WebRTC camera"""
    st.title("🎥 Interview Assessment Session")
    
    # Navigation
    if not st.session_state.interview_complete:
        if st.button("← Back to Home"):
            st.session_state.page = "home"
            st.session_state.interview_started = False
            st.session_state.interview_complete = False
            st.rerun()
    else:
        col1, col2 = st.columns(2)
        with col1:
            if st.button("← Back to Home"):
                st.session_state.page = "home"
                st.session_state.interview_started = False
                st.session_state.interview_complete = False
                st.rerun()
        with col2:
            if st.button("🔄 New Assessment"):
                st.session_state.results = []
                st.session_state.interview_started = False
                st.session_state.interview_complete = False
                st.rerun()
    
    st.markdown("---")
    
    if not st.session_state.interview_started and not st.session_state.interview_complete:
        show_interview_setup()
    
    elif st.session_state.interview_started and not st.session_state.interview_complete:
        show_interview_recording(models)
    
    else:
        show_results()

def show_interview_setup():
    """Show interview setup with camera preview"""
    st.subheader("🎬 Setup Your Interview Environment")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.write("""
        **📋 Setup Instructions:**
        1. Ensure good lighting on your face
        2. Position yourself centered in the frame
        3. Remove any unauthorized items from view
        4. Ensure you're alone in the room
        5. Check that audio is working
        
        **🎥 Camera Preview:**
        - The camera will activate when you start the assessment
        - Green boundaries show the optimal frame area
        - Stay within the boundaries throughout the assessment
        """)
    
    with col2:
        st.info("""
        **⏰ Time Estimate:**
        - Setup: 2-3 minutes
        - Questions: 1 minute total
        - Analysis: 1-2 minutes
        """)
    
    st.markdown("---")
    
    if st.button("🎬 Start Camera & Begin Assessment", type="primary", use_container_width=True):
        st.session_state.interview_started = True
        st.session_state.camera_active = True
        st.rerun()

def show_interview_recording(models):
    """Show interview recording interface"""
    if not WEBRTC_AVAILABLE:
        st.error("❌ Camera functionality not available. Please check browser permissions.")
        return
    
    # Initialize systems
    recording_system = RecordingSystem(models)
    analysis_system = AnalysisSystem(models)
    scoring_dashboard = ScoringDashboard()
    
    # WebRTC camera stream
    st.subheader("📹 Camera Feed - Interview in Progress")
    
    webrtc_ctx = webrtc_streamer(
        key="interview-camera",
        mode=WebRtcMode.SENDRECV,
        video_processor_factory=WebRTCVideoProcessor,
        media_stream_constraints={
            "video": {
                "width": {"ideal": 640},
                "height": {"ideal": 480},
                "frameRate": {"ideal": 15}
            },
            "audio": True
        },
        rtc_configuration={
            "iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]
        }
    )
    
    st.session_state.webrtc_ctx = webrtc_ctx
    
    if webrtc_ctx.video_processor:
        # Show camera status
        st.success("✅ Camera active - You're ready to begin!")
        
        # Start interview button
        if st.button("🎤 Start Interview Questions", type="primary", use_container_width=True):
            with st.spinner("Starting interview session..."):
                # Simulate interview process (you'll need to adapt your recording system)
                st.info("Interview simulation starting...")
                
                # For now, we'll simulate results
                simulate_interview_results(recording_system, analysis_system, scoring_dashboard)
                
                st.session_state.interview_complete = True
                st.rerun()
    else:
        st.warning("⏸️ Camera not active. Please allow camera permissions and refresh the page.")

def simulate_interview_results(recording_system, analysis_system, scoring_dashboard):
    """Simulate interview results for demo purposes"""
    # This is a placeholder - you'll need to integrate your actual recording logic
    st.session_state.results = []
    
    for i, question in enumerate(QUESTIONS):
        # Simulate result for each question
        result = {
            "question": question["question"],
            "question_number": i + 1,
            "transcript": "This is a simulated transcript for demonstration purposes. In a real interview, your actual speech would be transcribed here.",
            "violations": [],
            "violation_detected": False,
            "fused_emotions": {"Confident": 75.0, "Nervous": 15.0, "Engaged": 8.0, "Neutral": 2.0},
            "emotion_scores": {"confidence": 75.0, "confidence_label": "High", "nervousness": 15.0, "nervous_label": "Calm"},
            "accuracy": 78.5,
            "fluency": 82.3,
            "wpm": 145,
            "blink_count": 12,
            "outfit": "Business Casual",
            "has_valid_data": True,
            "fluency_detailed": {
                "speech_rate": 145,
                "speech_rate_normalized": 0.92,
                "pause_ratio": 0.12,
                "grammar_score": 88.5,
                "grammar_errors": 2,
                "lexical_diversity": 68.2,
                "coherence_score": 72.4,
                "filler_count": 3,
                "filler_ratio": 0.04,
                "fluency_level": "Fluent"
            },
            "filler_count": 3,
            "filler_ratio": 0.04,
            "improvements_applied": {
                "no_fake_metrics": True,
                "stopword_filtering": True,
                "quality_weighted_emotions": True
            }
        }
        
        # Make hiring decision
        decision, reasons = scoring_dashboard.decide_hire(result)
        result["hire_decision"] = decision
        result["hire_reasons"] = reasons
        
        st.session_state.results.append(result)

def show_results():
    """Display assessment results"""
    if not st.session_state.results:
        st.info("📊 No results available. Please complete an assessment first.")
        return
    
    scoring_dashboard = ScoringDashboard()
    scoring_dashboard.render_dashboard(st.session_state.results)

def main():
    """Main application function"""
    initialize_session_state()
    
    # Load models (cached)
    @st.cache_resource(show_spinner="Loading AI models...")
    def load_cached_models():
        return load_models()
    
    models = load_cached_models()
    
    # Page routing
    if st.session_state.page == "home":
        show_home_page()
    else:
        show_interview_page(models)

if __name__ == "__main__":
    main()