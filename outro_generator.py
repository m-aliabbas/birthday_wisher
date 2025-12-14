import subprocess
from pathlib import Path
import shlex
import json
import os
from PIL import Image, ImageDraw
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
        return 1080, 1920
    
    width = int(streams[0]["width"])
    height = int(streams[0]["height"])
    return width, height


def create_outro_frame(width: int, height: int, progress: float, logo_path: str = None):
    """
    Create a single frame of the outro animation.
    
    Args:
        width: Frame width
        height: Frame height
        progress: Animation progress (0.0 to 1.0)
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
    
    # Animation phases
    if progress < 0.3:
        # Fade in phase
        logo_alpha = int(255 * (progress / 0.3))
    elif progress > 0.7:
        # Fade out phase
        logo_alpha = int(255 * ((1.0 - progress) / 0.3))
    else:
        # Hold phase
        logo_alpha = 255
    
    # Create overlay
    overlay = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    
    # Add centered logo if available
    if logo_path and Path(logo_path).exists() and logo_alpha > 0:
        try:
            logo = Image.open(logo_path).convert('RGBA')
            
            # Calculate logo size - max 40% of screen width or height, maintaining aspect ratio
            base_size = min(width, height)
            max_logo_size = int(base_size * 0.4)
            
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
            
            # Position logo at center
            logo_x = (width - logo_width) // 2
            logo_y = (height - logo_height) // 2
            
            # Create a subtle glow behind the logo
            glow_size = 15
            glow = Image.new('RGBA', (logo_width + glow_size * 2, logo_height + glow_size * 2), (0, 0, 0, 0))
            glow_draw = ImageDraw.Draw(glow)
            glow_alpha_val = int(logo_alpha * 0.3)
            glow_draw.ellipse([0, 0, logo_width + glow_size * 2, logo_height + glow_size * 2], 
                            fill=(255, 215, 0, glow_alpha_val))
            overlay.paste(glow, (logo_x - glow_size, logo_y - glow_size), glow)
            
            # Paste logo
            overlay.paste(logo, (logo_x, logo_y), logo)
            
        except Exception as e:
            print(f"Warning: Could not load logo for outro: {e}")
    
    # Composite overlay onto background
    img = Image.alpha_composite(img.convert('RGBA'), overlay).convert('RGB')
    
    return img


def create_outro_video(output_path: str, duration: int = 3, template_video: str = None, logo_path: str = None):
    """
    Create a 3-second outro video with centered logo fade in/out.
    
    Args:
        output_path: Path where the outro video will be saved
        duration: Duration in seconds (default 3)
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
    
    print(f"Creating outro with dimensions: {width}x{height}")
    
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
                print(f"Found logo for outro: {logo_path}")
                break
    
    # Generate frames
    fps = 30
    total_frames = fps * duration
    frames = []
    
    print(f"Generating {total_frames} frames for outro animation...")
    
    for frame_num in range(total_frames):
        progress = frame_num / total_frames
        frame = create_outro_frame(width, height, progress, logo_path)
        frames.append(np.array(frame))
    
    # Create video from frames using moviepy
    print("Creating outro video from frames...")
    clip = ImageSequenceClip(frames, fps=fps)
    
    # Write video with audio (silent audio track)
    temp_video = str(out.parent / f"temp_outro_{os.getpid()}.mp4")
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
    
    print(f"✅ Outro created: {out}")
    return out


def concatenate_videos_with_outro(intro_path: str, main_video_path: str, outro_path: str, output_path: str):
    """
    Concatenate intro, main video, and outro.
    
    Args:
        intro_path: Path to intro video
        main_video_path: Path to main rendered video
        outro_path: Path to outro video
        output_path: Path for final output
    """
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    
    # Create concat file
    concat_file = out.parent / "concat_list.txt"
    with open(concat_file, 'w') as f:
        f.write(f"file '{Path(intro_path).absolute()}'\n")
        f.write(f"file '{Path(main_video_path).absolute()}'\n")
        f.write(f"file '{Path(outro_path).absolute()}'\n")
    
    cmd = (
        f'ffmpeg -y '
        f'-f concat -safe 0 -i {shlex.quote(str(concat_file))} '
        f'-c copy '
        f'{shlex.quote(str(out))}'
    )
    
    print(">> Concatenating intro + main + outro videos:", cmd)
    p = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    # Clean up concat file
    concat_file.unlink(missing_ok=True)
    
    if p.returncode != 0:
        raise RuntimeError(f"Failed to concatenate videos: {p.stderr}")
    
    print(f"✅ Final video created: {out}")
    return out
