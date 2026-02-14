import cv2
import torch
from torchvision import transforms
from PIL import Image
import numpy as np
import base64
from io import BytesIO

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

# =======================
# PREPROCESSING
# =======================

transform = transforms.Compose([
    transforms.Resize((224,224)),
    transforms.ToTensor(),
    transforms.Normalize([0.485,0.456,0.406],   # Standard ImageNet mean
                         [0.229,0.224,0.225])   # Standard ImageNet std
])

face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
)

# =======================
# GRAD-CAM INTEGRATION
# =======================

from gradcam import analyze_frame_with_gradcam, create_gradcam_visualization

# =======================
# FRAME PREDICTION
# =======================

def predict_frame(model, frame):
    """Predict deepfake probability for a single frame"""
    try:
        if frame is None or frame.size == 0:
            return None
            
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.1, 4)

        if len(faces) == 0:
            return None

        # Get largest face
        x, y, w, h = max(faces, key=lambda b: b[2]*b[3])
        
        # Validate face coordinates
        if w <= 0 or h <= 0:
            return None
            
        face = frame[y:y+h, x:x+w]

        face = Image.fromarray(cv2.cvtColor(face, cv2.COLOR_BGR2RGB))
        tensor = transform(face).unsqueeze(0).to(DEVICE)

        with torch.no_grad():
            output = model(tensor)
            score = torch.sigmoid(output).item()

        return score
    except Exception as e:
        print(f"Error predicting frame: {e}")
        return None

# =======================
# VIDEO ANALYSIS WITH GRAD-CAM
# =======================

def analyze_video_with_gradcam(model, path, generate_visualization=True):
    """
    Analyze entire video for deepfake detection with Grad-CAM visualization
    
    Args:
        model: Trained model
        path: Path to video file
        generate_visualization: Whether to generate Grad-CAM heatmaps
    
    Returns:
        tuple: (prediction, score, gradcam_frames)
            - prediction: 'REAL', 'FAKE', or 'SUSPICIOUS'
            - score: Confidence score
            - gradcam_frames: List of base64 encoded visualization frames (if enabled)
    """
    
    EMA_ALPHA = 0.15
    CONSECUTIVE_FRAMES = 5
    FAKE_THRESHOLD = 0.70

    cap = cv2.VideoCapture(path)
    
    if not cap.isOpened():
        raise ValueError(f"Failed to open video: {path}")

    ema_score = 0
    hits = 0
    is_fake = False
    first = True
    frame_count = 0
    processed_count = 0
    gradcam_frames = []
    
    # Sample frames for Grad-CAM visualization (every Nth frame)
    visualization_interval = 10 if generate_visualization else float('inf')

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            frame_count += 1
            score = predict_frame(model, frame)

            if score is None:
                continue

            processed_count += 1
            
            if first:
                ema_score = score
                first = False
            else:
                ema_score = EMA_ALPHA * score + (1-EMA_ALPHA) * ema_score

            # Generate Grad-CAM visualization for sampled frames
            if generate_visualization and frame_count % visualization_interval == 0 and len(gradcam_frames) < 5:
                gradcam_result = analyze_frame_with_gradcam(
                    model, frame, face_cascade, transform, DEVICE
                )
                
                if gradcam_result is not None:
                    # Create visualization
                    vis_frame = create_gradcam_visualization(frame, gradcam_result)
                    
                    # Convert to base64 for sending to frontend
                    pil_img = Image.fromarray(vis_frame)
                    buffer = BytesIO()
                    pil_img.save(buffer, format='JPEG', quality=85)
                    img_str = base64.b64encode(buffer.getvalue()).decode()
                    
                    gradcam_frames.append({
                        'frame_number': frame_count,
                        'score': float(gradcam_result['score']),
                        'image': f"data:image/jpeg;base64,{img_str}"
                    })

            if ema_score > FAKE_THRESHOLD:
                hits += 1
            else:
                hits = 0

            if hits >= CONSECUTIVE_FRAMES:
                is_fake = True
                # Generate one final Grad-CAM for the detection frame
                if generate_visualization and len(gradcam_frames) < 5:
                    gradcam_result = analyze_frame_with_gradcam(
                        model, frame, face_cascade, transform, DEVICE
                    )
                    if gradcam_result is not None:
                        vis_frame = create_gradcam_visualization(frame, gradcam_result)
                        pil_img = Image.fromarray(vis_frame)
                        buffer = BytesIO()
                        pil_img.save(buffer, format='JPEG', quality=85)
                        img_str = base64.b64encode(buffer.getvalue()).decode()
                        gradcam_frames.append({
                            'frame_number': frame_count,
                            'score': float(gradcam_result['score']),
                            'image': f"data:image/jpeg;base64,{img_str}",
                            'detection_frame': True
                        })
                break
    finally:
        cap.release()
    
    # Return result based on analysis
    if processed_count == 0:
        raise ValueError("No faces detected in video")
    
    if is_fake:
        return "FAKE", float(ema_score), gradcam_frames
    elif ema_score > 0.55:
        return "SUSPICIOUS", float(ema_score), gradcam_frames
    else:
        return "REAL", float(ema_score), gradcam_frames


# =======================
# ORIGINAL ANALYZE VIDEO (backward compatibility)
# =======================

def analyze_video(model, path):
    """Analyze entire video for deepfake detection (original function)"""
    prediction, score, _ = analyze_video_with_gradcam(model, path, generate_visualization=False)
    return prediction, score