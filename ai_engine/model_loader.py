import torch
import torch.nn as nn
from torchvision import models
import os
import logging

logger = logging.getLogger(__name__)

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
MODEL_PATH = os.path.join(os.path.dirname(__file__), "deepfake_model.pth")

def load_model():
    """Load and initialize the EfficientNet B0 deepfake detection model"""
    
    logger.info(f"Loading model from: {MODEL_PATH}")
    logger.info(f"Using device: {DEVICE}")
    
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(f"Model file not found: {MODEL_PATH}")
    
    try:
        model = models.efficientnet_b0(weights=None)

        # Custom classifier for binary classification
        model.classifier = nn.Sequential(
            nn.Dropout(0.2),
            nn.Linear(1280, 512),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(512, 1)
        )

        checkpoint = torch.load(MODEL_PATH, map_location=DEVICE)

        # Handle both checkpoint formats
        if isinstance(checkpoint, dict) and 'model_state_dict' in checkpoint:
            model.load_state_dict(checkpoint['model_state_dict'])
        else:
            model.load_state_dict(checkpoint)

        model.to(DEVICE)
        model.eval()
        
        logger.info("Model loaded successfully")
        return model
    
    except Exception as e:
        logger.error(f"Failed to load model: {str(e)}")
        raise
