import qrcode
from PIL import Image
import os

def generate_qr_code(url, filename="engepower_qr.png", size=10, border=2):
    """
    Generate a QR code for the given URL
    
    Args:
        url (str): The URL to encode in the QR code
        filename (str): Output filename for the QR code image
        size (int): Box size in pixels (default: 10)
        border (int): Border width in boxes (default: 2)
    """
    try:
        # Create QR code instance
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=size,
            border=border
        )
        
        # Add data to QR code
        qr.add_data(url)
        qr.make(fit=True)
        
        # Create image from QR code
        qr_image = qr.make_image(fill_color="black", back_color="white")
        
        # Save the image
        qr_image.save(filename)
        
        print(f"✅ QR code generated successfully!")
        print(f"📁 Saved as: {filename}")
        print(f"🔗 URL encoded: {url}")
        print(f"📏 Image size: {qr_image.size[0]}x{qr_image.size[1]} pixels")
        
        return filename
        
    except Exception as e:
        print(f"❌ Error generating QR code: {e}")
        return None

def generate_qr_code_with_logo(url, logo_path=None, filename="engepower_qr_with_logo.png"):
    """
    Generate a QR code with a logo in the center (if logo provided)
    
    Args:
        url (str): The URL to encode
        logo_path (str): Path to logo image (optional)
        filename (str): Output filename
    """
    try:
        # Generate basic QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,  # Higher error correction for logo
            box_size=10,
            border=2
        )
        
        qr.add_data(url)
        qr.make(fit=True)
        
        qr_image = qr.make_image(fill_color="black", back_color="white")
        
        # Add logo if provided
        if logo_path and os.path.exists(logo_path):
            logo = Image.open(logo_path)
            
            # Resize logo to fit in QR code center
            logo_size = qr_image.size[0] // 4
            logo = logo.resize((logo_size, logo_size))
            
            # Calculate position to center logo
            pos = ((qr_image.size[0] - logo_size) // 2, (qr_image.size[1] - logo_size) // 2)
            
            # Paste logo onto QR code
            qr_image.paste(logo, pos)
            
            print(f"✅ QR code with logo generated successfully!")
        else:
            print(f"✅ QR code generated successfully!")
            
        # Save the image
        qr_image.save(filename)
        print(f"📁 Saved as: {filename}")
        print(f"🔗 URL encoded: {url}")
        
        return filename
        
    except Exception as e:
        print(f"❌ Error generating QR code with logo: {e}")
        return None

if __name__ == "__main__":
    # URL to encode
    url = "https://engepower.co.mz/"
    
    print("🚀 Generating QR Code for EngePower")
    print("=" * 50)
    
    # Generate basic QR code
    basic_qr = generate_qr_code(url, "engepower_basic_qr.png")
    
    # Generate QR code with higher quality (larger size)
    large_qr = generate_qr_code(url, "engepower_large_qr.png", size=15, border=3)
    
    # Try to generate QR code with logo if logo exists
    logo_path = "logo.png"  # Adjust path as needed
    if os.path.exists(logo_path):
        logo_qr = generate_qr_code_with_logo(url, logo_path, "engepower_logo_qr.png")
    else:
        print(f"ℹ️  Logo not found at {logo_path}. Skipping logo QR code generation.")
        print(f"💡 Place a logo.png file in the same directory to generate QR code with logo.")
    
    print("\n" + "=" * 50)
    print("🎯 QR Code generation complete!")
    print("💡 You can now use these QR codes for:")
    print("   - Business cards")
    print("   - Marketing materials")
    print("   - Website sharing")
    print("   - Mobile scanning")
