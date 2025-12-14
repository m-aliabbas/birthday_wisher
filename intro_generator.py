import subprocess
from pathlib import Path
import shlex
import platform
import os
import json
from PIL import Image, ImageDraw, ImageFont
import numpy as np
from moviepy.editor import ImageSequenceClip
import tempfile


def get_video_dimensions(video_path: str) -> tuple[int, int]:
    """Get video dimensions using ffprobe."""
    cmd = [
        "ffprobe", "-v", "error",
        "-select_streams", "v:0",
        "-show_entries", "stream=width,height",
        "-of", "json",
        str(video_path)
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    data = json.loads(result.stdout)
    streams = data.get("streams", [])
    if not streams:
        # Default to common video size
        return 1080, 1920
    
    width = int(streams[0]["width"])
    height = int(streams[0]["height"])
    return width, height


def get_font_path():
    """Get appropriate font path based on operating system - prefer bold/fancy fonts."""
    system = platform.system()
    
    font_paths = []
    
    if system == "Darwin":  # macOS
        font_paths = [
            "/System/Library/Fonts/Supplemental/Arial Black.ttf",
            "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
            "/System/Library/Fonts/Supplemental/Futura.ttc",
            "/System/Library/Fonts/Supplemental/Impact.ttf",
            "/Library/Fonts/Arial.ttf",
        ]
    elif system == "Linux":
        font_paths = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
            "/usr/share/fonts/TTF/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        ]
    elif system == "Windows":
        font_paths = [
            "C:/Windows/Fonts/impact.ttf",
            "C:/Windows/Fonts/arialbd.ttf",
            "C:/Windows/Fonts/ariblk.ttf",
            "C:/Windows/Fonts/arial.ttf",
        ]
    
    for font in font_paths:
        if Path(font).exists():
            return font
    
    return None


def create_intro_frame(width: int, height: int, customer_name: str, progress: float, font_path: str = None, logo_path: str = None):
    """
    Create a single frame of the intro animation.
    
    Args:
        width: Frame width
        height: Frame height
        customer_name: Customer's name
        progress: Animation progress (0.0 to 1.0)
        font_path: Path to font file
        logo_path: Path to logo image
    
    Returns:
        PIL Image
    """
    # Create image with elegant gradient background
    img = Image.new('RGB', (width, height), color='#1a1a2e')
    
    # Add subtle gradient effect
    gradient = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    gradient_draw = ImageDraw.Draw(gradient)
    for y in range(height):
        alpha = int(30 * (1 - y / height))
        gradient_draw.line([(0, y), (width, y)], fill=(138, 43, 226, alpha))
    img = Image.alpha_composite(img.convert('RGBA'), gradient).convert('RGB')
    
    draw = ImageDraw.Draw(img)
    
    # Calculate font sizes based on video dimensions
    base_size = min(width, height)
    font_size_1 = int(base_size * 0.10)  # "Happy Birthday" - BIGGER and BOLD
    font_size_2 = int(base_size * 0.12)  # Customer name (larger, more prominent)
    font_size_3 = int(base_size * 0.06)  # "from"
    
    # Load fonts
    try:
        if font_path and Path(font_path).exists():
            font1 = ImageFont.truetype(font_path, font_size_1)
            font2 = ImageFont.truetype(font_path, font_size_2)
            font3 = ImageFont.truetype(font_path, font_size_3)
        else:
            font1 = ImageFont.load_default()
            font2 = ImageFont.load_default()
            font3 = ImageFont.load_default()
    except:
        font1 = ImageFont.load_default()
        font2 = ImageFont.load_default()
        font3 = ImageFont.load_default()
    
    # Animation phases with smooth easing
    if progress < 0.25:
        # Text fade in phase
        text_alpha = int(255 * (progress / 0.25))
        logo_alpha = 0
        y_shift = int(20 * (1 - progress / 0.25))  # Slight upward movement
    elif progress < 0.35:
        # Logo fade in
        text_alpha = 255
        logo_alpha = int(255 * ((progress - 0.25) / 0.1))
        y_shift = 0
    elif progress > 0.85:
        # Fade out phase
        fade_progress = (1.0 - progress) / 0.15
        text_alpha = int(255 * fade_progress)
        logo_alpha = int(255 * fade_progress)
        y_shift = int(20 * (1 - fade_progress))  # Slight downward movement
    else:
        # Hold phase
        text_alpha = 255
        logo_alpha = 255
        y_shift = 0
    
    # Text content
    text1 = "Happy Birthday"
    text2 = customer_name
    text3 = "from"
    
    # Calculate text positions (centered)
    bbox1 = draw.textbbox((0, 0), text1, font=font1)
    bbox2 = draw.textbbox((0, 0), text2, font=font2)
    bbox3 = draw.textbbox((0, 0), text3, font=font3)
    
    text1_w = bbox1[2] - bbox1[0]
    text2_w = bbox2[2] - bbox2[0]
    text3_w = bbox3[2] - bbox3[0]
    
    # Vertical positioning - more centered and balanced
    total_text_height = font_size_1 + font_size_2 + font_size_3 + 40
    y_start = (height - total_text_height) // 2 - int(base_size * 0.08) + y_shift
    
    x1 = (width - text1_w) // 2
    y1 = y_start
    
    x2 = (width - text2_w) // 2
    y2 = y1 + int(font_size_1 * 1.3)
    
    x3 = (width - text3_w) // 2
    y3 = y2 + int(font_size_2 * 1.4)
    
    # Create overlay for text with glow effect
    overlay = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    overlay_draw = ImageDraw.Draw(overlay)
    
    # Draw glow/shadow effect (multiple layers for softer shadow)
    shadow_offset = max(4, int(base_size * 0.004))
    glow_layers = 3
    for i in range(glow_layers, 0, -1):
        glow_alpha = int((text_alpha // glow_layers) * 0.6)
        offset = shadow_offset * i // glow_layers
        overlay_draw.text((x1 + offset, y1 + offset), text1, font=font1, fill=(0, 0, 0, glow_alpha))
        overlay_draw.text((x2 + offset, y2 + offset), text2, font=font2, fill=(0, 0, 0, glow_alpha))
        overlay_draw.text((x3 + offset, y3 + offset), text3, font=font3, fill=(0, 0, 0, glow_alpha))
    
    # Draw "Happy Birthday" with colorful gradient effect - letter by letter
    happy_word = "Happy"
    birthday_word = "Birthday"
    colors = [
        (255, 0, 128, text_alpha),    # Hot Pink
        (255, 128, 0, text_alpha),    # Orange
        (255, 215, 0, text_alpha),    # Gold
        (0, 255, 128, text_alpha),    # Spring Green
        (0, 191, 255, text_alpha),    # Deep Sky Blue
        (138, 43, 226, text_alpha),   # Blue Violet
    ]
    
    # Draw "Happy" with rainbow colors
    x_offset = x1
    for i, char in enumerate(happy_word):
        color = colors[i % len(colors)]
        overlay_draw.text((x_offset, y1), char, font=font1, fill=color)
        char_bbox = overlay_draw.textbbox((x_offset, y1), char, font=font1)
        x_offset = char_bbox[2]
    
    # Add space
    space_bbox = overlay_draw.textbbox((x_offset, y1), " ", font=font1)
    x_offset = space_bbox[2]
    
    # Draw "Birthday" with rainbow colors
    for i, char in enumerate(birthday_word):
        color = colors[(i + len(happy_word)) % len(colors)]
        overlay_draw.text((x_offset, y1), char, font=font1, fill=color)
        char_bbox = overlay_draw.textbbox((x_offset, y1), char, font=font1)
        x_offset = char_bbox[2]
    
    # Draw customer name and "from" text
    overlay_draw.text((x2, y2), text2, font=font2, fill=(255, 255, 255, text_alpha))  # Pure White
    overlay_draw.text((x3, y3), text3, font=font3, fill=(255, 182, 193, text_alpha))  # Light Pink
    
    # Add logo at the bottom if available
    if logo_path and Path(logo_path).exists() and logo_alpha > 0:
        try:
            logo = Image.open(logo_path).convert('RGBA')
            
            # Calculate logo size (max 250x250, maintaining aspect ratio)
            max_logo_size = 250
            aspect_ratio = logo.width / logo.height
            
            if logo.width > logo.height:
                logo_width = min(max_logo_size, logo.width)
                logo_height = int(logo_width / aspect_ratio)
            else:
                logo_height = min(max_logo_size, logo.height)
                logo_width = int(logo_height * aspect_ratio)
            
            # Resize logo maintaining aspect ratio
            logo = logo.resize((logo_width, logo_height), Image.Resampling.LANCZOS)
            
            # Apply alpha to logo
            if logo_alpha < 255:
                logo_with_alpha = Image.new('RGBA', logo.size, (0, 0, 0, 0))
                for x in range(logo.width):
                    for y in range(logo.height):
                        r, g, b, a = logo.getpixel((x, y))
                        new_alpha = int(a * logo_alpha / 255)
                        logo_with_alpha.putpixel((x, y), (r, g, b, new_alpha))
                logo = logo_with_alpha
            
            # Position logo at bottom center (lifted up more)
            logo_x = (width - logo_width) // 2
            logo_y = height - logo_height - int(base_size * 0.15)  # 15% margin from bottom (lifted up)
            
            # Create a subtle glow behind the logo
            glow_size = 10
            glow = Image.new('RGBA', (logo_width + glow_size * 2, logo_height + glow_size * 2), (0, 0, 0, 0))
            glow_draw = ImageDraw.Draw(glow)
            glow_alpha_val = int(logo_alpha * 0.3)
            glow_draw.ellipse([0, 0, logo_width + glow_size * 2, logo_height + glow_size * 2], 
                            fill=(255, 215, 0, glow_alpha_val))
            overlay.paste(glow, (logo_x - glow_size, logo_y - glow_size), glow)
            
            # Paste logo
            overlay.paste(logo, (logo_x, logo_y), logo)
            
        except Exception as e:
            print(f"Warning: Could not load logo: {e}")
    
    # Composite overlay onto background
    img = Image.alpha_composite(img.convert('RGBA'), overlay).convert('RGB')
    
    return img


def create_intro_video(customer_name: str, output_path: str, duration: int = 4, template_video: str = None, logo_path: str = None):
    """
    Create a 4-second intro video with customer name and "Happy Birthday from City Bakers".
    Uses animated frames for smooth transitions with logo.
    
    Args:
        customer_name: Name of the customer
        output_path: Path where the intro video will be saved
        duration: Duration in seconds (default 4)
        template_video: Path to template video to match dimensions
        logo_path: Path to City Bakers logo image
    """
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    
    # Get video dimensions from template
    if template_video and Path(template_video).exists():
        width, height = get_video_dimensions(template_video)
    else:
        width, height = 1080, 1920  # Default
    
    print(f"Creating intro with dimensions: {width}x{height}")
    
    # Get font and logo paths
    font_path = get_font_path()
    
    # Look for logo in common locations
    if not logo_path:
        possible_logo_paths = [
            Path("assets/logo.png"),
            Path("assets/city_bakers_logo.png"),
            Path("logo.png"),
            Path("templates/logo.png")
        ]
        for p in possible_logo_paths:
            if p.exists():
                logo_path = str(p)
                print(f"Found logo: {logo_path}")
                break
    
    # Generate frames
    fps = 30
    total_frames = fps * duration
    frames = []
    
    print(f"Generating {total_frames} frames for intro animation...")
    
    for frame_num in range(total_frames):
        progress = frame_num / total_frames
        frame = create_intro_frame(width, height, customer_name, progress, font_path, logo_path)
        frames.append(np.array(frame))
    
    # Create video from frames using moviepy
    print("Creating video from frames...")
    clip = ImageSequenceClip(frames, fps=fps)
    
    # Write video with audio (silent audio track)
    temp_video = str(out.parent / f"temp_intro_{os.getpid()}.mp4")
    clip.write_videofile(
        temp_video,
        codec='libx264',
        audio=False,
        fps=fps,
        preset='fast',
        verbose=False,
        logger=None
    )
    
    # Add silent audio track using ffmpeg
    cmd = (
        f'ffmpeg -y -i {shlex.quote(temp_video)} '
        f'-f lavfi -i anullsrc=channel_layout=stereo:sample_rate=44100 '
        f'-t {duration} -c:v copy -c:a aac -shortest '
        f'{shlex.quote(str(out))}'
    )
    
    subprocess.run(cmd, shell=True, capture_output=True, check=True)
    
    # Clean up temp file
    Path(temp_video).unlink(missing_ok=True)
    
    print(f"✅ Intro created: {out}")
    return out


def concatenate_videos(intro_path: str, main_video_path: str, output_path: str):
    """
    Concatenate intro video with main video.
    
    Args:
        intro_path: Path to intro video
        main_video_path: Path to main rendered video
        output_path: Path for final output
    """
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    
    # Create concat file
    concat_file = out.parent / "concat_list.txt"
    with open(concat_file, 'w') as f:
        f.write(f"file '{Path(intro_path).absolute()}'\n")
        f.write(f"file '{Path(main_video_path).absolute()}'\n")
    
    cmd = (
        f'ffmpeg -y '
        f'-f concat -safe 0 -i {shlex.quote(str(concat_file))} '
        f'-c copy '
        f'{shlex.quote(str(out))}'
    )
    
    print(">> Concatenating videos:", cmd)
    p = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    # Clean up concat file
    concat_file.unlink(missing_ok=True)
    
    if p.returncode != 0:
        raise RuntimeError(f"Failed to concatenate videos: {p.stderr}")
    
    print(f"✅ Final video created: {out}")
    return out
