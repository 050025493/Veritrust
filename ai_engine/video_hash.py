"""
Video Hashing Utility
Generates unique SHA-256 hash for video files for deduplication
"""

import hashlib
import os


def compute_video_hash(file_path):
    """
    Compute SHA-256 hash of video file
    
    Args:
        file_path: Path to video file
        
    Returns:
        str: 64-character hexadecimal hash
    """
    sha256_hash = hashlib.sha256()
    
    # Read file in chunks to handle large videos
    with open(file_path, "rb") as f:
        # Read in 64kb chunks
        for byte_block in iter(lambda: f.read(65536), b""):
            sha256_hash.update(byte_block)
    
    return sha256_hash.hexdigest()


def compute_video_hash_from_bytes(file_bytes):
    """
    Compute SHA-256 hash from file bytes (for uploaded files)
    
    Args:
        file_bytes: Bytes of the file
        
    Returns:
        str: 64-character hexadecimal hash
    """
    sha256_hash = hashlib.sha256()
    sha256_hash.update(file_bytes)
    return sha256_hash.hexdigest()


def get_file_size(file_path):
    """Get file size in bytes"""
    return os.path.getsize(file_path)


if __name__ == "__main__":
    # Test the hashing
    import sys
    
    if len(sys.argv) > 1:
        test_file = sys.argv[1]
        if os.path.exists(test_file):
            video_hash = compute_video_hash(test_file)
            file_size = get_file_size(test_file)
            
            print(f"File: {test_file}")
            print(f"Size: {file_size:,} bytes ({file_size / (1024*1024):.2f} MB)")
            print(f"Hash: {video_hash}")
        else:
            print(f"File not found: {test_file}")
    else:
        print("Usage: python video_hash.py <video_file>")