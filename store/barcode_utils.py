"""
Barcode generation utility for Solv-IT application.

This module provides functionality to generate barcodes
for products and save them as PNG files.
"""

import os
import sys
import barcode
from barcode.writer import ImageWriter
from django.conf import settings
from django.core.files.base import ContentFile
from io import BytesIO
import logging

logger = logging.getLogger(__name__)


def generate_barcode_file(serial_number):
    """
    Generate a barcode PNG file for a given serial number.
    
    Args:
        serial_number (str): The serial number to encode in the barcode
        
    Returns:
        tuple: (barcode_filename, barcode_path) where:
            - barcode_filename: Just the filename (e.g., 'SERIAL123.png')
            - barcode_path: Relative path for display (e.g., 'barcodes/SERIAL123.png')
            
    Raises:
        Exception: If barcode generation fails
    """
    try:
        # Validate input
        if not serial_number or not str(serial_number).strip():
            raise ValueError("Serial number cannot be empty")
        
        serial_number = str(serial_number).strip()
        logger.info(f"🔄 Starting barcode generation for serial: {serial_number}")
        
        # Check if STATIC_ROOT is configured
        if not hasattr(settings, 'STATIC_ROOT') or not settings.MEDIA_ROOT:
            logger.error("❌ STATIC_ROOT is not configured in Django settings")
            raise ValueError("Django STATIC_ROOT is not configured")
        
        # Create barcodes directory if it doesn't exist
        barcode_dir = os.path.join(settings.MEDIA_ROOT, 'barcodes')
        logger.info(f"📁 Barcode directory: {barcode_dir}")
        
        if not os.path.exists(barcode_dir):
            logger.info(f"📂 Creating directory: {barcode_dir}")
            os.makedirs(barcode_dir, exist_ok=True)
        
        # Verify directory is writable
        if not os.access(barcode_dir, os.W_OK):
            logger.error(f"❌ Directory is not writable: {barcode_dir}")
            raise PermissionError(f"Barcodes directory is not writable: {barcode_dir}")
        
        # Sanitize serial number for filename
        safe_serial = ''.join(c for c in serial_number if c.isalnum() or c in '-_.')
        if not safe_serial:
            safe_serial = "barcode"
        
        barcode_filename = f"{safe_serial}.png"
        barcode_file_path = os.path.join(barcode_dir, barcode_filename)
        
        logger.info(f"🏷️ Safe serial: {safe_serial}")
        logger.info(f"📄 Barcode file path: {barcode_file_path}")
        
        # Generate Code128 barcode
        # Code128 is a good choice as it can encode alphanumeric characters
        logger.info(f"⚙️ Generating Code128 barcode for: {serial_number}")
        barcode_instance = barcode.get_barcode_class('code128')
        ean = barcode_instance(serial_number, writer=ImageWriter())
        
        # Save without extension (barcode library adds it)
        save_path = os.path.join(barcode_dir, safe_serial)
        logger.info(f"💾 Saving to: {save_path}")
        ean.save(save_path)
        
        # Verify file was created
        if not os.path.exists(barcode_file_path):
            logger.error(f"❌ Barcode file was not created: {barcode_file_path}")
            raise IOError(f"Barcode file was not created: {barcode_file_path}")
        
        file_size = os.path.getsize(barcode_file_path)
        logger.info(f"✅ Barcode file created successfully: {barcode_file_path} ({file_size} bytes)")
        
        # Return the relative path for display in templates
        barcode_relative_path = f"barcodes/{barcode_filename}"
        logger.info(f"✅ Returning relative path: {barcode_relative_path}")
        
        return barcode_filename, barcode_relative_path
        
    except Exception as e:
        error_msg = f"❌ Error generating barcode for serial {serial_number}: {str(e)}"
        logger.error(error_msg, exc_info=True)
        raise Exception(error_msg)


def get_barcode_static_url(barcode_filename):
    """
    Get the static URL for a barcode file.
    
    Args:
        barcode_filename (str): The filename of the barcode
        
    Returns:
        str: The static URL path for the barcode
    """
    return f"{settings.STATIC_URL}barcodes/{barcode_filename}"
