# Birthday Wisher - Video Renderer

A Streamlit web application for rendering personalized birthday videos with custom images.

## Features

- 🎨 **Template Selection**: Choose from available video templates
- ⚙️ **Configuration Editor**: Edit template settings with an intuitive UI
- 📤 **Image Upload**: Upload customer photos directly in the browser
- 🎬 **Video Rendering**: Render personalized videos with one click
- 📄 **Raw JSON Editor**: Advanced editing for template configurations
- 📥 **Download**: Download rendered videos directly from the browser

## Prerequisites

- Python 3.7+
- FFmpeg (must be installed and available in PATH)

### Installing FFmpeg

**macOS (using Homebrew):**
```bash
brew install ffmpeg
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install ffmpeg
```

**Windows:**
Download from [ffmpeg.org](https://ffmpeg.org/download.html) and add to PATH.

## Installation

1. Clone or navigate to the project directory:
```bash
cd /path/to/birthday_wisher
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Running the Streamlit App

Start the web interface:
```bash
streamlit run app.py
```

The application will open in your default browser at `http://localhost:8501`

### Using the Web Interface

1. **Select a Template**: Choose from available templates in the sidebar
2. **Upload an Image**: Upload the customer's photo (JPG or PNG)
3. **Configure Settings** (optional): Adjust placeholder position, chroma key, and output settings
4. **Render Video**: Click "Render Video" and wait for processing
5. **Download**: Download the rendered video from the browser

### Command Line Usage

You can still use the command-line interface:
```bash
python render.py --template templates/bday1 --image /path/to/image.jpg --out output/result.mp4
```

## Template Structure

Each template folder should contain:
```
templates/
  bday1/
    ├── template.json     # Configuration file
    ├── template.mp4      # Video template
    └── border.png        # Optional border overlay
```

### Template Configuration (`template.json`)

```json
{
  "template_video": "template.mp4",
  "border_png": "border.png",
  "placeholder": { "x": 50, "y": 90, "w": 960, "h": 890 },
  "chroma": { "hex": "3ec954", "similarity": 0.23, "blend": 0.03 },
  "fit": "cover",
  "output": { "fps": 30, "crf": 18, "preset": "medium" }
}
```

**Configuration Options:**

- `placeholder`: Position and size of the image overlay
  - `x`, `y`: Top-left corner position
  - `w`, `h`: Width and height

- `chroma`: Chroma key (green screen) settings
  - `hex`: Color to key out (without #)
  - `similarity`: Color matching threshold (0.0-1.0)
  - `blend`: Edge blending amount (0.0-1.0)

- `fit`: How to fit the image
  - `cover`: Fill placeholder (may crop image)
  - `contain`: Fit inside placeholder (may add padding)

- `output`: Video encoding settings
  - `fps`: Frames per second
  - `crf`: Quality (0-51, lower = better quality)
  - `preset`: Encoding speed (ultrafast to veryslow)

## Output

Rendered videos are saved in the `output/` folder with timestamps:
```
output/
  birthday_video_20231214_143022.mp4
```

## Troubleshooting

**"FFmpeg not found" error:**
- Ensure FFmpeg is installed and available in your system PATH
- Test by running `ffmpeg -version` in terminal

**Rendering takes too long:**
- Try a faster preset (e.g., "fast" or "veryfast")
- Reduce video quality by increasing CRF value
- Check template video resolution

**Image doesn't fit properly:**
- Adjust placeholder dimensions in configuration
- Try different fit modes (cover vs contain)
- Check chroma key settings if background shows

## License

This project is for internal use.
