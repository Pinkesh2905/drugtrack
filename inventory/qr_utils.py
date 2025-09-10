import qrcode
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers import RoundedModuleDrawer
from qrcode.image.styles.colormasks import SquareGradiantColorMask
import os
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import io


def generate_qr_code(data, filename_prefix):
    """
    Generate QR code for given data and save it to media/qr_codes/
    
    Args:
        data (str): Data to encode in QR code
        filename_prefix (str): Prefix for the QR code filename
    
    Returns:
        str: Relative path to the saved QR code image
    """
    try:
        # Create QR code instance
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        
        # Add data
        qr.add_data(data)
        qr.make(fit=True)
        
        # Create QR code image with styling
        img = qr.make_image(
            image_factory=StyledPilImage,
            module_drawer=RoundedModuleDrawer(),
            color_mask=SquareGradiantColorMask(
                back_color=(255, 255, 255),
                center_color=(0, 100, 200),
                edge_color=(0, 50, 150)
            )
        )
        
        # Convert to bytes
        img_io = io.BytesIO()
        img.save(img_io, format='PNG')
        img_content = ContentFile(img_io.getvalue())
        
        # Generate filename
        filename = f"qr_codes/{filename_prefix}_qr.png"
        
        # Save using Django's storage system
        saved_path = default_storage.save(filename, img_content)
        
        return saved_path
        
    except Exception as e:
        print(f"Error generating QR code: {e}")
        return None


def verify_qr_data(qr_data):
    """
    Verify and parse QR code data
    
    Args:
        qr_data (str): QR code data in format "batch_number|drug_name|expiry_date"
    
    Returns:
        dict: Parsed QR data or None if invalid
    """
    try:
        parts = qr_data.split('|')
        if len(parts) >= 3:
            return {
                'batch_number': parts[0],
                'drug_name': parts[1],
                'expiry_date': parts[2],
                'is_valid': True
            }
        else:
            return {
                'is_valid': False,
                'error': 'Invalid QR code format'
            }
    except Exception as e:
        return {
            'is_valid': False,
            'error': str(e)
        }


def create_qr_codes_directory():
    """
    Ensure qr_codes directory exists in media folder
    """
    qr_dir = os.path.join(settings.MEDIA_ROOT, 'qr_codes')
    if not os.path.exists(qr_dir):
        os.makedirs(qr_dir)
    return qr_dir


# Utility function to get QR code URL
def get_qr_code_url(filename):
    """
    Get the full URL for a QR code file
    
    Args:
        filename (str): QR code filename
    
    Returns:
        str: Full URL to the QR code
    """
    if filename and default_storage.exists(filename):
        return default_storage.url(filename)
    return None