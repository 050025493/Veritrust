from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import tempfile
import os
import logging

from model_loader import load_model
from inference import analyze_video_with_gradcam

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="VeriTrust AI Engine", version="1.0.0")

# CORS configuration (allow frontend to connect)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change to specific origin in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load model on startup
model = load_model()

ALLOWED_VIDEO_TYPES = {"video/mp4", "video/mpeg", "video/quicktime", "video/x-msvideo", "video/webm"}
MAX_FILE_SIZE = 500 * 1024 * 1024  # 500MB

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok", "model": "loaded"}

@app.post("/predict-video")
async def predict_video(file: UploadFile = File(...)):
    """Analyze video for deepfake detection"""
    
    # Validate file type
    if file.content_type not in ALLOWED_VIDEO_TYPES:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid file type. Allowed: {', '.join(ALLOWED_VIDEO_TYPES)}"
        )
    
    temp_path = None
    try:
        # Save uploaded video temporarily
        with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as temp:
            content = await file.read()
            
            # Check file size
            if len(content) > MAX_FILE_SIZE:
                raise HTTPException(
                    status_code=413,
                    detail=f"File too large. Max size: {MAX_FILE_SIZE / (1024*1024):.0f}MB"
                )
            
            temp.write(content)
            temp_path = temp.name
        
        logger.info(f"Analyzing video: {file.filename}")
        prediction, score, gradcam_frames = analyze_video_with_gradcam(
            model, temp_path, generate_visualization=True
        )
        
        logger.info(f"Result - Prediction: {prediction}, Confidence: {score:.4f}, Grad-CAM frames: {len(gradcam_frames)}")
        
        response = {
            "filename": file.filename,
            "prediction": prediction,
            "confidence": round(score, 4),
            "status": "success",
            "gradcam_frames": gradcam_frames
        }
        
        return response
    
    except Exception as e:
        logger.error(f"Error analyzing video: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error analyzing video: {str(e)}"
        )
    
    finally:
        # Cleanup temp file
        if temp_path and os.path.exists(temp_path):
            try:
                os.remove(temp_path)
                logger.info(f"Cleaned up temporary file: {temp_path}")
            except Exception as e:
                logger.warning(f"Failed to cleanup temp file: {e}")