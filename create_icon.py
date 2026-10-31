"""Generate a simple app icon for FileConverterPro."""
from PIL import Image, ImageDraw, ImageFont
import os

def create_icon():
    size = 256
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Background circle - gradient-like effect
    for i in range(size // 2, 0, -1):
        r = int(233 * (i / (size // 2)) + 15 * (1 - i / (size // 2)))
        g = int(69 * (i / (size // 2)) + 33 * (1 - i / (size // 2)))
        b = int(96 * (i / (size // 2)) + 94 * (1 - i / (size // 2)))
        draw.ellipse(
            [size // 2 - i, size // 2 - i, size // 2 + i, size // 2 + i],
            fill=(r, g, b, 255)
        )
    
    # Draw arrows (conversion symbol)
    # Right arrow
    arrow_color = (255, 255, 255, 255)
    # Arrow body
    draw.rectangle([70, 105, 170, 125], fill=arrow_color)
    # Arrow head
    draw.polygon([(170, 90), (200, 115), (170, 140)], fill=arrow_color)
    
    # Left arrow (below)
    draw.rectangle([86, 140, 186, 160], fill=arrow_color)
    draw.polygon([(86, 165), (56, 150), (86, 135)], fill=arrow_color)
    
    # Save as ICO
    script_dir = os.path.dirname(os.path.abspath(__file__))
    icon_path = os.path.join(script_dir, "icon.ico")
    
    # Create multiple sizes for ICO
    sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    img.save(icon_path, format="ICO", sizes=sizes)
    print(f"Icon saved to: {icon_path}")
    return icon_path

if __name__ == "__main__":
    create_icon()
