"""
Compatibility module for imghdr in Python 3.13+
This module provides basic image format detection functionality
that was removed from Python 3.13's standard library.
"""

import struct

def what(file, h=None):
    """Detect the image format of a file or file-like object."""
    if h is None:
        if hasattr(file, 'read'):
            h = file.read(32)
            file.seek(0)  # Reset file position
        else:
            try:
                with open(file, 'rb') as f:
                    h = f.read(32)
            except (OSError, IOError):
                return None
    
    if not h:
        return None
    
    # JPEG detection
    if h.startswith(b'\xff\xd8\xff'):
        return 'jpeg'
    
    # PNG detection  
    if h.startswith(b'\x89PNG\r\n\x1a\n'):
        return 'png'
    
    # GIF detection
    if h.startswith(b'GIF87a') or h.startswith(b'GIF89a'):
        return 'gif'
    
    # BMP detection
    if h.startswith(b'BM'):
        return 'bmp'
    
    # WEBP detection
    if h[8:12] == b'WEBP':
        return 'webp'
    
    # TIFF detection
    if h.startswith(b'II*\x00') or h.startswith(b'MM\x00*'):
        return 'tiff'
    
    return None

# Compatibility functions for older code
def test_jpeg(h, f):
    """Test for JPEG format."""
    return h.startswith(b'\xff\xd8\xff')

def test_png(h, f):
    """Test for PNG format."""
    return h.startswith(b'\x89PNG\r\n\x1a\n')

def test_gif(h, f):
    """Test for GIF format."""
    return h.startswith(b'GIF87a') or h.startswith(b'GIF89a')