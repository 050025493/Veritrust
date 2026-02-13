import cv2
import torch
from torchvision import transforms
from PIL import Image
import numpy as np

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
# VIDEO ANALYSIS
# =======================

def analyze_video(model, path):
    """Analyze entire video for deepfake detection"""
    
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

            if ema_score > FAKE_THRESHOLD:
                hits += 1
            else:
                hits = 0

            if hits >= CONSECUTIVE_FRAMES:
                is_fake = True
                break
    finally:
        cap.release()
    
    # Return result based on analysis
    if processed_count == 0:
        raise ValueError("No faces detected in video")
    
    if is_fake:
        return "FAKE", float(ema_score)
    elif ema_score > 0.55:
        return "SUSPICIOUS", float(ema_score)
    else:
        return "REAL", float(ema_score)
