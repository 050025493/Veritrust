import torch
import torch.nn.functional as F
import cv2
import numpy as np
from PIL import Image
from torchvision import transforms

class GradCAM:
    """
    Grad-CAM implementation for visualizing model attention on deepfake detection
    """
    def __init__(self, model, target_layer):
        """
        Args:
            model: The trained model
            target_layer: The layer to compute gradients for (e.g., model.features[-1])
        """
        self.model = model
        self.target_layer = target_layer
        self.gradients = None
        self.activations = None
        
        # Register hooks
        self.target_layer.register_forward_hook(self.save_activation)
        self.target_layer.register_backward_hook(self.save_gradient)
    
    def save_activation(self, module, input, output):
        """Hook to save forward pass activations"""
        self.activations = output.detach()
    
    def save_gradient(self, module, grad_input, grad_output):
        """Hook to save backward pass gradients"""
        self.gradients = grad_output[0].detach()
    
    def generate_cam(self, input_tensor, target_class=None):
        """
        Generate Class Activation Map
        
        Args:
            input_tensor: Input image tensor (1, C, H, W)
            target_class: Target class index (0 for real, 1 for fake)
                         If None, uses the predicted class
        
        Returns:
            cam: Numpy array of the CAM heatmap
            prediction: Model prediction score
        """
        self.model.eval()
        
        # Forward pass
        output = self.model(input_tensor)
        prediction = torch.sigmoid(output).item()
        
        # If no target class specified, use predicted class
        if target_class is None:
            target_class = 1 if prediction > 0.5 else 0
        
        # Zero gradients
        self.model.zero_grad()
        
        # Backward pass for target class
        if target_class == 1:
            output.backward()
        else:
            (-output).backward()
        
        # Get gradients and activations
        gradients = self.gradients  # (1, C, H, W)
        activations = self.activations  # (1, C, H, W)
        
        # Global average pooling on gradients
        weights = torch.mean(gradients, dim=(2, 3), keepdim=True)  # (1, C, 1, 1)
        
        # Weighted combination of activation maps
        cam = torch.sum(weights * activations, dim=1, keepdim=True)  # (1, 1, H, W)
        
        # Apply ReLU to keep only positive influences
        cam = F.relu(cam)
        
        # Normalize to [0, 1]
        cam = cam.squeeze().cpu().numpy()
        if cam.max() > 0:
            cam = cam / cam.max()
        
        return cam, prediction
    
    def overlay_heatmap(self, heatmap, original_image, alpha=0.5, colormap=cv2.COLORMAP_JET):
        """
        Overlay heatmap on original image
        
        Args:
            heatmap: CAM heatmap (H, W)
            original_image: Original image as numpy array (H, W, C) in RGB
            alpha: Transparency of heatmap overlay
            colormap: OpenCV colormap to use
        
        Returns:
            Blended image with heatmap overlay
        """
        # Resize heatmap to match original image
        heatmap_resized = cv2.resize(heatmap, (original_image.shape[1], original_image.shape[0]))
        
        # Convert heatmap to uint8
        heatmap_uint8 = np.uint8(255 * heatmap_resized)
        
        # Apply colormap
        heatmap_colored = cv2.applyColorMap(heatmap_uint8, colormap)
        
        # Convert from BGR to RGB
        heatmap_colored = cv2.cvtColor(heatmap_colored, cv2.COLOR_BGR2RGB)
        
        # Ensure original image is uint8
        if original_image.dtype != np.uint8:
            original_image = np.uint8(original_image)
        
        # Blend images
        overlay = cv2.addWeighted(original_image, 1 - alpha, heatmap_colored, alpha, 0)
        
        return overlay


def analyze_frame_with_gradcam(model, frame, face_cascade, transform, device="cpu"):
    """
    Analyze a single frame and generate Grad-CAM visualization
    
    Args:
        model: Trained deepfake detection model
        frame: Video frame (numpy array)
        face_cascade: OpenCV face detector
        transform: Image preprocessing transform
        device: 'cpu' or 'cuda'
    
    Returns:
        dict with:
            - 'score': Deepfake probability
            - 'face_bbox': Face bounding box [x, y, w, h]
            - 'heatmap': Grad-CAM heatmap
            - 'overlay': Heatmap overlaid on face
            - 'original_face': Original face crop
    """
    if frame is None or frame.size == 0:
        return None
    
    # Detect face
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.1, 4)
    
    if len(faces) == 0:
        return None
    
    # Get largest face
    x, y, w, h = max(faces, key=lambda b: b[2] * b[3])
    
    if w <= 0 or h <= 0:
        return None
    
    # Extract face
    face = frame[y:y+h, x:x+w]
    face_rgb = cv2.cvtColor(face, cv2.COLOR_BGR2RGB)
    
    # Prepare for model
    face_pil = Image.fromarray(face_rgb)
    tensor = transform(face_pil).unsqueeze(0).to(device)
    
    # Initialize Grad-CAM
    # For EfficientNet, use the last convolutional layer
    target_layer = model.features[-1]
    gradcam = GradCAM(model, target_layer)
    
    # Generate CAM
    try:
        cam, score = gradcam.generate_cam(tensor)
        
        # Create overlay
        overlay = gradcam.overlay_heatmap(cam, face_rgb, alpha=0.4)
        
        return {
            'score': score,
            'face_bbox': [int(x), int(y), int(w), int(h)],
            'heatmap': cam,
            'overlay': overlay,
            'original_face': face_rgb
        }
    except Exception as e:
        print(f"Error generating Grad-CAM: {e}")
        return None


def create_gradcam_visualization(original_frame, gradcam_result):
    """
    Create a comprehensive visualization with original frame and Grad-CAM overlay
    
    Args:
        original_frame: Original video frame (BGR)
        gradcam_result: Result from analyze_frame_with_gradcam
    
    Returns:
        Visualization image showing frame with bounding box and heatmap
    """
    if gradcam_result is None:
        return original_frame
    
    frame_rgb = cv2.cvtColor(original_frame, cv2.COLOR_BGR2RGB)
    x, y, w, h = gradcam_result['face_bbox']
    
    # Draw bounding box on original frame
    color = (255, 0, 0) if gradcam_result['score'] > 0.7 else \
            (255, 255, 0) if gradcam_result['score'] > 0.5 else \
            (0, 255, 0)
    
    cv2.rectangle(frame_rgb, (x, y), (x+w, y+h), color, 2)
    
    # Add score text
    text = f"Deepfake: {gradcam_result['score']:.2%}"
    cv2.putText(frame_rgb, text, (x, y-10), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
    
    # Resize overlay to fit in frame
    overlay_resized = cv2.resize(gradcam_result['overlay'], (w, h))
    
    # Place overlay on frame
    frame_rgb[y:y+h, x:x+w] = overlay_resized
    
    return frame_rgb