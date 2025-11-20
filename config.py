"""
Configuration file for Azure deployment
"""

import os

# Deployment environment
IS_PRODUCTION = os.getenv('IS_PRODUCTION', 'False').lower() == 'true'

# Model settings
MODEL_LOADING = "lazy" if IS_PRODUCTION else "eager"
ENABLE_GPU = False  # Azure App Service typically doesn't have GPU

# Camera source
CAMERA_SOURCE = "webrtc"  # Use WebRTC for browser camera access

# Performance optimization for production
if IS_PRODUCTION:
    SAMPLE_EVERY_N_FRAMES = 15
    MAX_FRAME_WIDTH = 640
    MAX_FRAME_HEIGHT = 480
    MODEL_CONFIDENCE = 0.5
else:
    SAMPLE_EVERY_N_FRAMES = 8
    MAX_FRAME_WIDTH = 1280
    MAX_FRAME_HEIGHT = 720
    MODEL_CONFIDENCE = 0.7

# Interview questions
QUESTIONS = [
    {
        "question": "Tell me about yourself.",
        "type": "personal",
        "ideal_answer": "I'm a computer science postgraduate with a strong interest in AI and software development. I've worked on several projects involving Python, machine learning, and data analysis, which helped me improve both my technical and problem-solving skills. I enjoy learning new technologies and applying them to create practical solutions. Outside of academics, I like collaborating on team projects and continuously developing my professional skills.",
        "tip": "Focus on your background, skills, and personality"
    },
    {
        "question": "What are your strengths and weaknesses?",
        "type": "personal",
        "ideal_answer": "One of my key strengths is that I'm very detail-oriented and persistent – I make sure my work is accurate and well-tested. I also enjoy solving complex problems and learning new tools quickly. As for weaknesses, I used to spend too much time perfecting small details, which sometimes slowed me down. But I've been improving by prioritizing tasks better and focusing on overall impact.",
        "tip": "Be honest and show self-awareness"
    },
    {
        "question": "Where do you see yourself in the next 5 years?",
        "type": "personal",
        "ideal_answer": "In the next five years, I see myself growing into a more responsible and skilled professional, ideally in a role where I can contribute to meaningful projects involving AI and software development. I'd also like to take on leadership responsibilities and guide new team members as I gain experience.",
        "tip": "Show ambition aligned with career growth"
    }
]