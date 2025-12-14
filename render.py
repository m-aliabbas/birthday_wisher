import argparse
import json
import subprocess
from pathlib import Path
import shlex


def ensure_ffmpeg():
    try:
        subprocess.run(["ffmpeg", "-version"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run(["ffprobe", "-version"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception:
        raise SystemExit("❌ ffmpeg/ffprobe not found. Install ffmpeg and ensure it's on PATH.")


def ffprobe_size(path: Path) -> tuple[int, int]:
    # Returns (width, height) for first video stream
    cmd = [
        "ffprobe", "-v", "error",
        "-select_streams", "v:0",
        "-show_entries", "stream=width,height",
        "-of", "json",
        str(path)
    ]
    out = subprocess.check_output(cmd, text=True)
    data = json.loads(out)
    streams = data.get("streams", [])
    if not streams:
        raise SystemExit(f"❌ Could not read video size from: {path}")
    w = int(streams[0]["width"])
    h = int(streams[0]["height"])
    return w, h


def run(cmd: str):
    print(">>", cmd)
    p = subprocess.run(cmd, shell=True)
    if p.returncode != 0:
        raise SystemExit(p.returncode)


def main(template_folder: str, image_path: str, out_path: str):
    ensure_ffmpeg()

    tdir = Path(template_folder)
    cfg_path = tdir / "template.json"
    if not cfg_path.exists():
        raise SystemExit(f"❌ template.json not found in: {tdir}")

    cfg = json.loads(cfg_path.read_text(encoding="utf-8"))

    template_video = tdir / cfg.get("template_video", "template.mp4")
    if not template_video.exists():
        raise SystemExit(f"❌ template video not found: {template_video}")

    border_png = cfg.get("border_png")
    border_path = (tdir / border_png) if border_png else None
    if border_path and not border_path.exists():
        print(f"⚠️ border_png configured but missing, ignoring: {border_path}")
        border_path = None

    ph = cfg["placeholder"]
    x, y, w, h = int(ph["x"]), int(ph["y"]), int(ph["w"]), int(ph["h"])

    chroma = cfg.get("chroma", {})
    chroma_hex = chroma.get("hex", "3ec954").lower().replace("#", "")
    similarity = float(chroma.get("similarity", 0.23))
    blend = float(chroma.get("blend", 0.03))

    fit = cfg.get("fit", "cover").lower()
    out_cfg = cfg.get("output", {})
    fps = int(out_cfg.get("fps", 30))
    crf = int(out_cfg.get("crf", 18))
    preset = str(out_cfg.get("preset", "medium"))

    img = Path(image_path)
    if not img.exists():
        raise SystemExit(f"❌ customer image not found: {img}")

    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)

    canvas_w, canvas_h = ffprobe_size(template_video)

    # Fit modes:
    # cover = fill placeholder completely (may crop)
    # contain = fit inside placeholder (may add padding)
    if fit == "contain":
        img_chain = f"scale={w}:{h}:force_original_aspect_ratio=decrease,pad={w}:{h}:(ow-iw)/2:(oh-ih)/2"
    else:
        # default cover
        img_chain = f"scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h}"

    # Inputs:
    # 0: template video
    # 1: customer image (loop)
    # 2: optional border PNG
    if border_path:
        filter_complex = (
            f"[1:v]{img_chain}[photo];"
            f"color=c=black:s={canvas_w}x{canvas_h}[base];"
            f"[base][photo]overlay={x}:{y}[bg];"
            f"[0:v]format=rgba,colorkey=0x{chroma_hex}:{similarity}:{blend}[fg];"
            f"[bg][fg]overlay=0:0[v1];"
            f"[v1][2:v]overlay=0:0,format=yuv420p[vout]"
        )
        cmd = (
            f'ffmpeg -y '
            f'-i {shlex.quote(str(template_video))} '
            f'-loop 1 -i {shlex.quote(str(img))} '
            f'-i {shlex.quote(str(border_path))} '
            f'-filter_complex "{filter_complex}" '
            f'-map "[vout]" -map 0:a? -shortest '
            f'-r {fps} -c:v libx264 -crf {crf} -preset {preset} -c:a aac '
            f'{shlex.quote(str(out))}'
        )
    else:
        filter_complex = (
            f"[1:v]{img_chain}[photo];"
            f"color=c=black:s={canvas_w}x{canvas_h}[base];"
            f"[base][photo]overlay={x}:{y}[bg];"
            f"[0:v]format=rgba,colorkey=0x{chroma_hex}:{similarity}:{blend}[fg];"
            f"[bg][fg]overlay=0:0,format=yuv420p[vout]"
        )
        cmd = (
            f'ffmpeg -y '
            f'-i {shlex.quote(str(template_video))} '
            f'-loop 1 -i {shlex.quote(str(img))} '
            f'-filter_complex "{filter_complex}" '
            f'-map "[vout]" -map 0:a? -shortest '
            f'-r {fps} -c:v libx264 -crf {crf} -preset {preset} -c:a aac '
            f'{shlex.quote(str(out))}'
        )

    run(cmd)
    print(f"✅ Rendered: {out}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--template", required=True, help="Template folder path (contains template.json)")
    ap.add_argument("--image", required=True, help="Customer image (.jpg/.png)")
    ap.add_argument("--out", required=True, help="Output mp4 path")
    args = ap.parse_args()

    main(args.template, args.image, args.out)
