from PIL import Image
import os

def convert_to_ico(png_path, ico_path):
    """Convert PNG to ICO file"""
    try:
        # Open PNG image
        img = Image.open(png_path)
        
        # Convert to RGBA if not already
        if img.mode != 'RGBA':
            img = img.convert('RGBA')
        
        # Create ICO file
        img.save(ico_path, format='ICO')
        print(f"Successfully converted {png_path} to {ico_path}")
        return True
    except Exception as e:
        print(f"Error converting image: {e}")
        return False

if __name__ == "__main__":
    # Get current directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Define input and output paths
    png_file = os.path.join(current_dir, "ICON_g2c.png")
    ico_file = os.path.join(current_dir, "ICON_g2c.ico")
    
    # Convert file
    convert_to_ico(png_file, ico_file)
