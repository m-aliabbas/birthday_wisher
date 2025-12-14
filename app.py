import streamlit as st
import json
from pathlib import Path
import subprocess
import shutil
from datetime import datetime
import tempfile
import os
from render import main as render_main
from intro_generator import create_intro_video, concatenate_videos
from outro_generator import create_outro_video, concatenate_videos_with_outro

import subprocess, shutil, sys

def install_ffmpeg_ubuntu():
    if shutil.which("ffmpeg"):
        print("ffmpeg already installed")
        return
    subprocess.check_call(["sudo", "apt-get", "update"])
    subprocess.check_call(["sudo", "apt-get", "install", "-y", "ffmpeg"])
    print("ffmpeg installed ✅")
install_ffmpeg_ubuntu()

# Set page config
st.set_page_config(
    page_title="Birthday Wisher - Video Renderer",
    page_icon="🎂",
    layout="wide"
)

# Initialize session state
if 'selected_template' not in st.session_state:
    st.session_state.selected_template = None
if 'template_config' not in st.session_state:
    st.session_state.template_config = None
if 'uploaded_image_path' not in st.session_state:
    st.session_state.uploaded_image_path = None


def get_available_templates():
    """Get list of available template folders."""
    templates_dir = Path("templates")
    if not templates_dir.exists():
        return []
    
    templates = []
    for item in templates_dir.iterdir():
        if item.is_dir() and (item / "template.json").exists():
            templates.append(item.name)
    return sorted(templates)


def load_template_config(template_name):
    """Load template configuration from JSON."""
    config_path = Path("templates") / template_name / "template.json"
    if config_path.exists():
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None


def save_template_config(template_name, config):
    """Save template configuration to JSON."""
    config_path = Path("templates") / template_name / "template.json"
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2)
    st.success(f"✅ Template configuration saved!")


def check_ffmpeg():
    """Check if ffmpeg is installed."""
    try:
        subprocess.run(["ffmpeg", "-version"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except:
        return False


def render_video(template_folder, image_path, output_name, customer_name):
    """Render video using the render module with intro."""
    try:
        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)
        temp_dir = Path(tempfile.gettempdir()) / "birthday_wisher"
        temp_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Get template video path for dimensions
        template_video_path = Path("templates") / template_folder / "template.mp4"
        
        # Create intro video matching template dimensions
        intro_path = temp_dir / f"intro_{timestamp}.mp4"
        create_intro_video(
            customer_name, 
            str(intro_path), 
            duration=4,
            template_video=str(template_video_path) if template_video_path.exists() else None
        )
        # Render main video
        main_video_path = temp_dir / f"main_{timestamp}.mp4"
        render_main(
            template_folder=str(Path("templates") / template_folder),
            image_path=image_path,
            out_path=str(main_video_path)
        )
        
        # Create outro video matching template dimensions
        outro_path = temp_dir / f"outro_{timestamp}.mp4"
        create_outro_video(
            str(outro_path),
            duration=3,
            template_video=str(template_video_path) if template_video_path.exists() else None
        )
        
        # Concatenate intro, main video, and outro
        final_output_path = output_dir / f"{output_name}_{timestamp}.mp4"
        concatenate_videos_with_outro(str(intro_path), str(main_video_path), str(outro_path), str(final_output_path))
        
        # Clean up temporary files
        intro_path.unlink(missing_ok=True)
        main_video_path.unlink(missing_ok=True)
        outro_path.unlink(missing_ok=True)
        main_video_path.unlink(missing_ok=True)
        
        return final_output_path
    except Exception as e:
        raise Exception(f"Rendering failed: {str(e)}")


# Main UI
st.title("🎂 Birthday Wisher - Video Renderer")
st.markdown("---")

# Check ffmpeg installation
if not check_ffmpeg():
    st.error("❌ FFmpeg is not installed or not found in PATH. Please install ffmpeg to use this application.")
    st.stop()

# Sidebar for template selection
with st.sidebar:
    st.header("📁 Template Selection")
    
    templates = get_available_templates()
    
    if not templates:
        st.warning("No templates found in the templates folder.")
        st.stop()
    
    selected_template = st.selectbox(
        "Choose a template:",
        templates,
        index=templates.index(st.session_state.selected_template) if st.session_state.selected_template in templates else 0
    )
    
    if selected_template != st.session_state.selected_template:
        st.session_state.selected_template = selected_template
        st.session_state.template_config = load_template_config(selected_template)
        st.rerun()
    
    st.markdown("---")
    st.markdown("### Template Info")
    template_path = Path("templates") / selected_template
    video_file = template_path / "template.mp4"
    if video_file.exists():
        st.success("✅ Video file found")
    else:
        st.error("❌ Video file missing")

# Create tabs
tab1, tab2, tab3 = st.tabs(["🎨 Render Video", "⚙️ Edit Configuration", "📄 Raw JSON"])

# Tab 1: Render Video
with tab1:
    st.header("Upload Image and Render")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("1. Customer Information")
        customer_name = st.text_input(
            "Customer Name *",
            placeholder="Enter customer's name",
            help="This name will appear in the intro: 'Happy Birthday [Name] from City Bakers'"
        )
        
        st.subheader("2. Upload Image")
        uploaded_file = st.file_uploader(
            "Choose an image file",
            type=['jpg', 'jpeg', 'png'],
            help="Upload the customer's photo to be inserted into the template"
        )
        
        if uploaded_file:
            # Save uploaded file temporarily
            temp_dir = Path(tempfile.gettempdir()) / "birthday_wisher"
            temp_dir.mkdir(exist_ok=True)
            
            image_path = temp_dir / uploaded_file.name
            with open(image_path, 'wb') as f:
                f.write(uploaded_file.getvalue())
            
            st.session_state.uploaded_image_path = str(image_path)
            
            # Display preview
            st.image(uploaded_file, caption="Uploaded Image", use_container_width=True)
        
        st.subheader("3. Output Settings")
        output_name = st.text_input(
            "Output filename (without extension)",
            value="birthday_video",
            help="The output video will be saved in the 'output' folder"
        )
        
        render_button = st.button("🎬 Render Video", type="primary", use_container_width=True)
    
    with col2:
        st.subheader("Template Preview")
        
        # Show current template configuration
        if st.session_state.template_config:
            config = st.session_state.template_config
            
            st.markdown("**Current Settings:**")
            st.json({
                "Placeholder": config.get("placeholder", {}),
                "Fit Mode": config.get("fit", "cover"),
                "Chroma Key": config.get("chroma", {}),
                "Output": config.get("output", {})
            })
        
        # Template video preview
        template_video_path = Path("templates") / selected_template / "template.mp4"
        if template_video_path.exists():
            st.video(str(template_video_path))
    
    # Render process
    if render_button:
        if not customer_name or not customer_name.strip():
            st.error("Please enter customer's name first!")
        elif not uploaded_file:
            st.error("Please upload an image first!")
        elif not output_name:
            st.error("Please provide an output filename!")
        else:
            with st.spinner("🎬 Creating intro and rendering video... This may take a few moments."):
                try:
                    output_path = render_video(
                        selected_template,
                        st.session_state.uploaded_image_path,
                        output_name,
                        customer_name.strip()
                    )
                    
                    st.success(f"✅ Video rendered successfully!")
                    st.balloons()
                    
                    # Show video player
                    st.subheader("Rendered Video:")
                    st.video(str(output_path))
                    
                    # Download button
                    with open(output_path, 'rb') as f:
                        st.download_button(
                            label="⬇️ Download Video",
                            data=f,
                            file_name=output_path.name,
                            mime="video/mp4"
                        )
                    
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")

# Tab 2: Edit Configuration
with tab2:
    st.header("Edit Template Configuration")
    
    if st.session_state.template_config:
        config = st.session_state.template_config.copy()
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📐 Placeholder Settings")
            placeholder = config.get("placeholder", {})
            
            new_x = st.number_input("X Position", value=placeholder.get("x", 0), min_value=0)
            new_y = st.number_input("Y Position", value=placeholder.get("y", 0), min_value=0)
            new_w = st.number_input("Width", value=placeholder.get("w", 100), min_value=1)
            new_h = st.number_input("Height", value=placeholder.get("h", 100), min_value=1)
            
            config["placeholder"] = {"x": new_x, "y": new_y, "w": new_w, "h": new_h}
            
            st.markdown("---")
            st.subheader("🎨 Chroma Key Settings")
            chroma = config.get("chroma", {})
            
            chroma_hex = st.text_input("Hex Color", value=chroma.get("hex", "3ec954"))
            chroma_similarity = st.slider("Similarity", 0.0, 1.0, float(chroma.get("similarity", 0.23)), 0.01)
            chroma_blend = st.slider("Blend", 0.0, 1.0, float(chroma.get("blend", 0.03)), 0.01)
            
            config["chroma"] = {
                "hex": chroma_hex,
                "similarity": chroma_similarity,
                "blend": chroma_blend
            }
        
        with col2:
            st.subheader("🖼️ Fit Mode")
            fit_mode = st.radio(
                "Image Fit",
                ["cover", "contain"],
                index=0 if config.get("fit", "cover") == "cover" else 1,
                help="cover: Fill placeholder (may crop) | contain: Fit inside (may add padding)"
            )
            config["fit"] = fit_mode
            
            st.markdown("---")
            st.subheader("📹 Output Settings")
            output = config.get("output", {})
            
            fps = st.number_input("FPS", value=output.get("fps", 30), min_value=1, max_value=60)
            crf = st.number_input("CRF (Quality)", value=output.get("crf", 18), min_value=0, max_value=51, 
                                 help="Lower = better quality, larger file size")
            preset = st.selectbox(
                "Encoding Preset",
                ["ultrafast", "superfast", "veryfast", "faster", "fast", "medium", "slow", "slower", "veryslow"],
                index=["ultrafast", "superfast", "veryfast", "faster", "fast", "medium", "slow", "slower", "veryslow"].index(
                    output.get("preset", "medium")
                )
            )
            
            config["output"] = {
                "fps": fps,
                "crf": crf,
                "preset": preset
            }
            
            st.markdown("---")
            st.subheader("🖼️ Border Settings")
            border_png = st.text_input("Border PNG filename", value=config.get("border_png", ""))
            if border_png:
                config["border_png"] = border_png
            elif "border_png" in config:
                del config["border_png"]
        
        st.markdown("---")
        
        if st.button("💾 Save Configuration", type="primary"):
            save_template_config(selected_template, config)
            st.session_state.template_config = config

# Tab 3: Raw JSON
with tab3:
    st.header("Raw JSON Editor")
    
    if st.session_state.template_config:
        st.info("⚠️ Direct JSON editing - Be careful with syntax!")
        
        json_str = json.dumps(st.session_state.template_config, indent=2)
        edited_json = st.text_area(
            "Edit JSON directly:",
            value=json_str,
            height=400,
            help="Edit the template configuration in raw JSON format"
        )
        
        col1, col2 = st.columns([1, 4])
        
        with col1:
            if st.button("💾 Save JSON", type="primary"):
                try:
                    new_config = json.loads(edited_json)
                    save_template_config(selected_template, new_config)
                    st.session_state.template_config = new_config
                except json.JSONDecodeError as e:
                    st.error(f"❌ Invalid JSON: {str(e)}")
        
        with col2:
            if st.button("🔄 Reset to Current"):
                st.rerun()

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: gray;'>
        Birthday Wisher Video Renderer | Built with Streamlit
    </div>
    """,
    unsafe_allow_html=True
)
