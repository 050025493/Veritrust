from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import tempfile
import os
import logging
import time
import sys
from pathlib import Path

# Add parent directory to path for imports
parent_dir = str(Path(__file__).parent.parent)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from model_loader import load_model
from inference import analyze_video_with_gradcam
from database.database import get_db, VideoAnalysis, BlockchainLog, init_db
from video_hash import compute_video_hash, get_file_size
from blockchain.blockchain_service import get_blockchain_service

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="VeriTrust AI Engine", version="2.0.0")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    init_db()
    logger.info("✅ Database initialized")

# Load model
model = load_model()
blockchain_service = get_blockchain_service()

ALLOWED_VIDEO_TYPES = {
    "video/mp4", "video/mpeg", "video/quicktime", 
    "video/x-msvideo", "video/webm"
}
MAX_FILE_SIZE = 500 * 1024 * 1024  # 500MB


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "ok",
        "model": "loaded",
        "blockchain_connected": blockchain_service.is_connected(),
        "database": "connected"
    }


@app.get("/stats")
async def get_stats(db: Session = Depends(get_db)):
    """Get analysis statistics"""
    total_analyses = db.query(VideoAnalysis).count()
    fake_count = db.query(VideoAnalysis).filter(
        VideoAnalysis.prediction == "FAKE"
    ).count()
    real_count = db.query(VideoAnalysis).filter(
        VideoAnalysis.prediction == "REAL"
    ).count()
    blockchain_verified = db.query(VideoAnalysis).filter(
        VideoAnalysis.blockchain_verified == True
    ).count()
    
    return {
        "total_analyses": total_analyses,
        "fake_detected": fake_count,
        "real_verified": real_count,
        "suspicious": total_analyses - fake_count - real_count,
        "blockchain_verified": blockchain_verified
    }


@app.post("/predict-video")
async def predict_video(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Analyze video for deepfake detection with hash-based caching
    
    Flow:
    1. Compute video hash
    2. Check if already analyzed (instant result, no GPU cost)
    3. If new: analyze, store in DB, log to blockchain
    4. Return results with blockchain verification
    """
    
    # Validate file type
    if file.content_type not in ALLOWED_VIDEO_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed: {', '.join(ALLOWED_VIDEO_TYPES)}"
        )
    
    temp_path = None
    start_time = time.time()
    
    try:
        # Read file content
        content = await file.read()
        
        # Check file size
        if len(content) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=413,
                detail=f"File too large. Max: {MAX_FILE_SIZE/(1024*1024):.0f}MB"
            )
        
        # ========================================
        # STEP 1: Compute video hash
        # ========================================
        from video_hash import compute_video_hash_from_bytes
        video_hash = compute_video_hash_from_bytes(content)
        file_size = len(content)
        
        logger.info(f"Video hash: {video_hash[:16]}... ({file_size:,} bytes)")
        
        # ========================================
        # STEP 2: Check if already analyzed
        # ========================================
        existing = db.query(VideoAnalysis).filter(
            VideoAnalysis.video_hash == video_hash
        ).first()
        
        if existing:
            logger.info(f" Cache hit! Video already analyzed (ID: {existing.id})")
            
            return {
                "filename": file.filename,
                "prediction": existing.prediction,
                "confidence": existing.confidence,
                "status": "success",
                "cached": True,
                "original_filename": existing.filename,
                "analysis_timestamp": existing.analysis_timestamp.isoformat(),
                "video_hash": video_hash,
                "blockchain_tx_hash": existing.blockchain_tx_hash,
                "blockchain_url": existing.blockchain_url,
                "blockchain_verified": existing.blockchain_verified,
                "gradcam_frames": []  # Not stored in DB to save space
            }
        
        # ========================================
        # STEP 3: New video - Perform analysis
        # ========================================
        logger.info(f" New video - performing AI analysis...")
        
        # Save to temp file for analysis
        with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as temp:
            temp.write(content)
            temp_path = temp.name
        
        # Run AI analysis
        prediction, score, gradcam_frames = analyze_video_with_gradcam(
            model, temp_path, generate_visualization=True
        )
        
        analysis_duration = time.time() - start_time
        
        logger.info(
            f"Analysis complete: {prediction} ({score:.4f}) "
            f"in {analysis_duration:.2f}s"
        )
        
        # ========================================
        # STEP 4: Log to blockchain
        # ========================================
        blockchain_result = None
        blockchain_tx_hash = None
        blockchain_url = None
        
        try:
            logger.info(" Logging to blockchain...")
            
            is_fake = prediction == "FAKE"
            confidence_int = int(score * 100)
            
            blockchain_result = blockchain_service.log_evidence(
                video_hash=video_hash,
                is_fake=is_fake,
                confidence=confidence_int
            )
            
            if blockchain_result['success']:
                blockchain_tx_hash = blockchain_result['tx_hash']
                blockchain_url = blockchain_result['etherscan_url']
                logger.info(f" Blockchain TX: {blockchain_tx_hash}")
                
                # Save blockchain log
                blockchain_log = BlockchainLog(
                    tx_hash=blockchain_tx_hash,
                    video_hash=video_hash,
                    is_fake=is_fake,
                    confidence=confidence_int,
                    status="pending"
                )
                db.add(blockchain_log)
            else:
                logger.error(f"❌ Blockchain error: {blockchain_result.get('error')}")
                
        except Exception as e:
            logger.error(f"Blockchain logging failed: {e}")
        
        # ========================================
        # STEP 5: Save to database
        # ========================================
        analysis_record = VideoAnalysis(
            video_hash=video_hash,
            filename=file.filename,
            file_size=file_size,
            prediction=prediction,
            confidence=score,
            blockchain_tx_hash=blockchain_tx_hash,
            blockchain_verified=False,  # Will be updated by background task
            blockchain_url=blockchain_url,
            analysis_duration=analysis_duration,
            gradcam_generated=len(gradcam_frames) > 0
        )
        
        db.add(analysis_record)
        db.commit()
        db.refresh(analysis_record)
        
        logger.info(f" Saved to database (ID: {analysis_record.id})")
        
        # ========================================
        # STEP 6: Return results
        # ========================================
        return {
            "filename": file.filename,
            "prediction": prediction,
            "confidence": round(score, 4),
            "status": "success",
            "cached": False,
            "video_hash": video_hash,
            "analysis_id": analysis_record.id,
            "blockchain_tx_hash": blockchain_tx_hash,
            "blockchain_url": blockchain_url,
            "blockchain_verified": False,
            "gradcam_frames": gradcam_frames,
            "analysis_duration": round(analysis_duration, 2)
        }
    
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
            except Exception as e:
                logger.warning(f"Failed to cleanup temp file: {e}")


@app.get("/analysis/{video_hash}")
async def get_analysis(video_hash: str, db: Session = Depends(get_db)):
    """
    Get analysis by video hash
    """
    analysis = db.query(VideoAnalysis).filter(
        VideoAnalysis.video_hash == video_hash
    ).first()
    
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    return analysis.to_dict()


@app.get("/blockchain/{tx_hash}")
async def get_blockchain_status(tx_hash: str, db: Session = Depends(get_db)):
    """
    Check blockchain transaction status
    """
    log = db.query(BlockchainLog).filter(
        BlockchainLog.tx_hash == tx_hash
    ).first()
    
    if not log:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    # Check current status on blockchain
    receipt = blockchain_service.get_transaction_receipt(tx_hash)
    
    if receipt['confirmed'] and log.status == "pending":
        # Update status
        log.status = "confirmed" if receipt['status'] == 1 else "failed"
        log.block_number = receipt['block_number']
        log.gas_used = receipt['gas_used']
        db.commit()
    
    return {
        **log.to_dict(),
        'blockchain_receipt': receipt
    }


@app.get("/history")
async def get_history(
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """
    Get analysis history
    """
    analyses = db.query(VideoAnalysis).order_by(
        VideoAnalysis.analysis_timestamp.desc()
    ).offset(offset).limit(limit).all()
    
    return {
        "total": db.query(VideoAnalysis).count(),
        "limit": limit,
        "offset": offset,
        "analyses": [a.to_dict() for a in analyses]
    }