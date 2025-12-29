"""
Create a placeholder icon for the Thumbdrive Launcher
Generates a simple USB/thumbdrive icon
"""

from PIL import Image, ImageDraw, ImageFont
import os
from pathlib import Path

def create_thumbdrive_icon(size=256):
    """Create a simple thumbdrive icon"""

    # Create image with transparent background
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Calculate dimensions
    margin = size // 8
    usb_width = size - (2 * margin)
    usb_height = int(usb_width * 1.3)

    # Center the icon
    x_start = margin
    y_start = (size - usb_height) // 2

    # Draw USB connector (top part)
    connector_height = usb_height // 4
    connector_width = usb_width // 2
    connector_x = x_start + (usb_width - connector_width) // 2

    # USB connector
    draw.rectangle(
        [connector_x, y_start, connector_x + connector_width, y_start + connector_height],
        fill='#606060',
        outline='#303030',
        width=2
    )

    # Draw USB body (main part)
    body_y = y_start + connector_height
    body_height = usb_height - connector_height

    # Main body with gradient effect (using rectangles)
    draw.rectangle(
        [x_start, body_y, x_start + usb_width, body_y + body_height],
        fill='#4A90E2',
        outline='#2E5C8A',
        width=3
    )

    # Add highlight for 3D effect
    highlight_margin = size // 16
    draw.rectangle(
        [x_start + highlight_margin, body_y + highlight_margin,
         x_start + usb_width - highlight_margin, body_y + highlight_margin * 2],
        fill='#6BA4E8',
        outline=None
    )

    # Draw USB symbol or "D:"
    try:
        # Try to use a font for the drive letter
        font_size = size // 4
        try:
            font = ImageFont.truetype("arial.ttf", font_size)
        except:
            font = ImageFont.load_default()

        # Draw "D:" in the center
        text = "D:"
        # Get text bounding box
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        text_x = x_start + (usb_width - text_width) // 2
        text_y = body_y + (body_height - text_height) // 2

        draw.text((text_x, text_y), text, fill='white', font=font)
    except Exception as e:
        print(f"Could not add text: {e}")

    # Add small connector pins
    pin_width = connector_width // 6
    pin_height = connector_height // 3
    pin_y = y_start + connector_height // 3

    # Left pin
    pin1_x = connector_x + connector_width // 4
    draw.rectangle(
        [pin1_x, pin_y, pin1_x + pin_width, pin_y + pin_height],
        fill='#FFD700'
    )

    # Right pin
    pin2_x = connector_x + 3 * connector_width // 4 - pin_width
    draw.rectangle(
        [pin2_x, pin_y, pin2_x + pin_width, pin_y + pin_height],
        fill='#FFD700'
    )

    return img


def save_as_ico(img, output_path):
    """Save image as .ico file with multiple sizes"""
    # Create multiple sizes for better display at different resolutions
    sizes = [(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)]

    # Resize to all sizes
    icons = []
    for size in sizes:
        resized = img.resize(size, Image.Resampling.LANCZOS)
        icons.append(resized)

    # Save as .ico
    icons[0].save(
        output_path,
        format='ICO',
        sizes=[(img.width, img.height) for img in icons],
        append_images=icons[1:]
    )


def main():
    """Main function to create the icon"""
    script_dir = Path(__file__).parent
    icon_path = script_dir / "thumbdrive_icon.ico"

    print("Creating thumbdrive icon...")

    try:
        # Create the icon
        icon_img = create_thumbdrive_icon(size=256)

        # Save as .ico
        save_as_ico(icon_img, icon_path)

        print(f"[OK] Icon created successfully: {icon_path}")
        return icon_path

    except Exception as e:
        print(f"[ERROR] Error creating icon: {e}")
        print("\nTrying to install Pillow...")
        import subprocess
        try:
            subprocess.run(["pip", "install", "Pillow"], check=True)
            print("[OK] Pillow installed. Please run this script again.")
        except:
            print("[ERROR] Could not install Pillow. Please run: pip install Pillow")
        return None


if __name__ == "__main__":
    main()
