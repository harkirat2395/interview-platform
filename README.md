# Interview Assessment Platform

AI-powered interview assessment platform with real-time video analysis, speech recognition, and comprehensive scoring.

## Features

- 🎥 **WebRTC Camera Integration** - Browser-based camera access
- 🎯 **Real-time Analysis** - Confidence, engagement, and fluency tracking
- 🗣️ **Speech Recognition** - Automatic transcription and analysis
- 📊 **Comprehensive Scoring** - Proportional scoring based on performance
- 🚨 **Compliance Monitoring** - Violation detection and evidence capture

## Deployment on Azure

### Prerequisites
- Python 3.10.11
- Azure App Service account

### Quick Deployment

1. **Clone this repository**
2. **Create Azure App Service:**
   ```bash
   az webapp up --name your-interview-app --resource-group your-resource-group --runtime "PYTHON:3.10"