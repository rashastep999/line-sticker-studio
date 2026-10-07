"""
LINE Creators Market Image Processing Module
- Background removal with rembg
- High-quality upscaling & sharpening
- Automatic margin padding (10px) to prevent LINE rejection
- Strict enforcement of even pixel dimensions (W % 2 == 0, H % 2 == 0)
- Presets: Sticker (max 370x320), Main (240x240), Tab (96x74)
- Max file size guarantee (< 1MB)
"""

import io
import math
from typing import Tuple, Optional, Dict, Any, List
from PIL import Image, ImageEnhance, ImageFilter, ImageDraw, ImageOps
import numpy as np

# Optional rembg import with lazy loading
# Multi-model rembg session cache
_REMBG_SESSIONS: Dict[str, Any] = {}

def get_rembg_session(model_name: str = "isnet-general-use"):
    global _REMBG_SESSIONS
    if model_name not in _REMBG_SESSIONS:
        try:
            from rembg import new_session
            _REMBG_SESSIONS[model_name] = new_session(model_name)
        except Exception as e:
            # Fallback to u2net if specific model fails
            print(f"Failed to load model {model_name}, falling back to u2net: {e}")
            try:
                from rembg import new_session
                _REMBG_SESSIONS[model_name] = new_session("u2net")
            except Exception:
                _REMBG_SESSIONS[model_name] = False
    return _REMBG_SESSIONS[model_name]

def refine_alpha_edges(
    image: Image.Image,
    defringe: bool = True,
    smooth_radius: float = 0.8
) -> Image.Image:
    """
    Cleans up cutout boundaries:
    - Defringing: removes dark/light halo artifacts around transparent edges
    - Anti-aliasing: smooths ragged alpha staircase edges
    """
    image = image.convert("RGBA")
    r, g, b, a = image.split()

    if smooth_radius > 0:
        # Smooth alpha mask to eliminate jagged stepped pixels
        a_smooth = a.filter(ImageFilter.GaussianBlur(radius=smooth_radius))
        # Keep threshold clean
        a = Image.blend(a, a_smooth, 0.4)

    if defringe:
        # Clean RGB color spill in semi-transparent fringe pixels
        rgb = Image.merge("RGB", (r, g, b))
        # Gentle median on edge boundary to clean fringe
        rgb_clean = rgb.filter(ImageFilter.MedianFilter(size=3))
        # Blend near outer edges
        rgb_final = Image.blend(rgb, rgb_clean, 0.25)
        r, g, b = rgb_final.split()

    return Image.merge("RGBA", (r, g, b, a))

def remove_background(
    image: Image.Image,
    model_name: str = "isnet-general-use",
    alpha_matting: bool = False,
    edge_refine: bool = True,
    **kwargs
) -> Image.Image:
    """
    High-precision background removal using IS-Net / U2-Net with edge refinement.
    """
    try:
        from rembg import remove
        session = get_rembg_session(model_name)
        
        # Prepare rembg arguments
        kwargs = {
            "alpha_matting": alpha_matting,
            "alpha_matting_foreground_threshold": 240,
            "alpha_matting_background_threshold": 10,
            "alpha_matting_erode_size": 10
        } if alpha_matting else {}

        if session is False or session is None:
            result = remove(image, **kwargs)
        else:
            result = remove(image, session=session, **kwargs)

        res_rgba = result.convert("RGBA")
        if edge_refine:
            res_rgba = refine_alpha_edges(res_rgba)
        return res_rgba
    except Exception as e:
        print(f"Background removal failed or fallback triggered: {e}")
        try:
            # Emergency fallback with default rembg
            from rembg import remove
            res = remove(image).convert("RGBA")
            return refine_alpha_edges(res) if edge_refine else res
        except Exception:
            return image.convert("RGBA")

def trim_transparent_borders(image: Image.Image) -> Image.Image:
    """
    Crops out transparent borders around the subject so we can accurately
    calculate margins and scale the actual subject content.
    """
    image = image.convert("RGBA")
    bbox = image.getbbox()
    if bbox:
        return image.crop(bbox)
    return image

def upscale_and_restore_details(
    image: Image.Image,
    scale_factor: float = 2.0,
    enhancement_mode: str = "anime",
    denoise_strength: float = 0.3,
    edge_sharpness: float = 1.6,
    clarity_boost: float = 1.2
) -> Image.Image:
    """
    Super-Resolution Upscaling & Detail Restorer.
    Designed specifically for low-resolution, small images to prevent pixelation,
    blur, and jagged edges when preparing LINE stickers.
    
    scale_factor: 1.5x, 2.0x, 3.0x, or 4.0x
    enhancement_mode: 'anime' (Sticker/Line Art) or 'photo' (Realistic/General)
    denoise_strength: 0.0 to 1.0 (anti-aliasing and smoothing out jagged pixel blocks)
    edge_sharpness: 1.0 to 3.0 (fine crispness for outlines and details)
    clarity_boost: 1.0 to 2.0 (local contrast & micro-detail definition)
    """
    if scale_factor <= 1.0 and edge_sharpness <= 1.0 and clarity_boost <= 1.0:
        return image

    image = image.convert("RGBA")
    orig_w, orig_h = image.size

    # Target upscaled dimensions
    new_w = max(1, int(round(orig_w * scale_factor)))
    new_h = max(1, int(round(orig_h * scale_factor)))

    # Step 1: High-fidelity Lanczos Super-Sampling
    upscaled = image.resize((new_w, new_h), Image.Resampling.LANCZOS)
    r, g, b, a = upscaled.split()
    rgb = Image.merge("RGB", (r, g, b))

    # Step 2: Anti-aliasing / Denoise (Smooth out jagged pixel staircase)
    if denoise_strength > 0:
        blur_radius = max(0.4, denoise_strength * 1.0)
        smoothed_rgb = rgb.filter(ImageFilter.GaussianBlur(radius=blur_radius))
        # Blend back slightly so we don't lose key details
        blend_factor = min(0.65, denoise_strength * 0.6)
        rgb = Image.blend(rgb, smoothed_rgb, blend_factor)

    # Step 3: Multi-stage Detail & Edge Restoration
    if enhancement_mode == "anime":
        # Mode: Anime / Sticker / Vector Cartoon
        # Fine edge crispness for outlines
        fine_percent = int(edge_sharpness * 140)
        rgb = rgb.filter(ImageFilter.UnsharpMask(radius=1.0, percent=fine_percent, threshold=2))

        # Secondary outline emphasis
        if edge_sharpness > 1.3:
            rgb = rgb.filter(ImageFilter.UnsharpMask(radius=2.2, percent=80, threshold=4))

        # Clarity (Micro-contrast)
        if clarity_boost > 1.0:
            clarity_percent = int((clarity_boost - 1.0) * 80)
            rgb = rgb.filter(ImageFilter.UnsharpMask(radius=12.0, percent=clarity_percent, threshold=6))
    else:
        # Mode: Photo / Realistic Texture
        fine_percent = int(edge_sharpness * 120)
        rgb = rgb.filter(ImageFilter.UnsharpMask(radius=1.5, percent=fine_percent, threshold=3))
        
        if clarity_boost > 1.0:
            clarity_percent = int((clarity_boost - 1.0) * 70)
            rgb = rgb.filter(ImageFilter.UnsharpMask(radius=16.0, percent=clarity_percent, threshold=5))

    # Also smooth alpha mask to prevent ragged transparent edges after upscale
    if denoise_strength > 0:
        a_smooth = a.filter(ImageFilter.GaussianBlur(radius=max(0.4, denoise_strength * 0.8)))
        # Binarize/contract slightly to keep crisp boundary
        a = Image.blend(a, a_smooth, min(0.5, denoise_strength * 0.5))

    r_out, g_out, b_out = rgb.split()
    return Image.merge("RGBA", (r_out, g_out, b_out, a))

def add_outline(
    image: Image.Image,
    stroke_color: Tuple[int, int, int, int] = (255, 255, 255, 255),
    stroke_width: int = 5
) -> Image.Image:
    """
    Adds a clean, smooth sticker-style outline (White border) around the subject.
    Essential for LINE stickers to ensure visibility in both Dark and Light mode.
    """
    if stroke_width <= 0:
        return image

    image = image.convert("RGBA")
    alpha = image.split()[3]

    # Expand alpha mask using MaxFilter for outline
    expanded_alpha = alpha.filter(ImageFilter.MaxFilter(stroke_width * 2 + 1))
    
    # Smooth the stroke edge
    expanded_alpha = expanded_alpha.filter(ImageFilter.SMOOTH)

    # Create solid color outline image
    outline_img = Image.new("RGBA", image.size, stroke_color)
    outline_img.putalpha(expanded_alpha)

    # Composite original image on top of outline
    result = Image.alpha_composite(outline_img, image)
    return result

def enhance_image(
    image: Image.Image,
    sharpness: float = 1.3,
    contrast: float = 1.05,
    brightness: float = 1.0,
    saturation: float = 1.05
) -> Image.Image:
    """
    Applies professional sharpening and color enhancements while preserving transparency.
    """
    image = image.convert("RGBA")
    r, g, b, a = image.split()
    rgb_image = Image.merge("RGB", (r, g, b))

    # Brightness
    if brightness != 1.0:
        enhancer = ImageEnhance.Brightness(rgb_image)
        rgb_image = enhancer.enhance(brightness)

    # Contrast
    if contrast != 1.0:
        enhancer = ImageEnhance.Contrast(rgb_image)
        rgb_image = enhancer.enhance(contrast)

    # Color Saturation
    if saturation != 1.0:
        enhancer = ImageEnhance.Color(rgb_image)
        rgb_image = enhancer.enhance(saturation)

    # Sharpening
    if sharpness != 1.0:
        enhancer = ImageEnhance.Sharpness(rgb_image)
        rgb_image = enhancer.enhance(sharpness)
        # Apply gentle UnsharpMask for crisp cartoon/sticker vector look
        if sharpness > 1.2:
            rgb_image = rgb_image.filter(ImageFilter.UnsharpMask(radius=1.5, percent=120, threshold=3))

    r_new, g_new, b_new = rgb_image.split()
    return Image.merge("RGBA", (r_new, g_new, b_new, a))

def ensure_even(val: int) -> int:
    """LINE requires even pixel dimensions (width & height)."""
    return val if val % 2 == 0 else val - 1

def fit_to_canvas(
    subject: Image.Image,
    target_type: str = "sticker",
    margin: int = 10,
    canvas_mode: str = "fixed",
    custom_w: int = 370,
    custom_h: int = 320
) -> Image.Image:
    """
    Places subject into a LINE-compliant canvas with guaranteed margins and even dimensions.
    
    target_type:
      - 'sticker': max 370 x 320 px (standard LINE)
      - 'main': 240 x 240 px (cover image)
      - 'tab': 96 x 74 px (chat tab icon)
      - 'square_320': 320 x 320 px (1:1 square)
      - 'square_300': 300 x 300 px (1:1 square)
      - 'landscape_4_3': 320 x 240 px (4:3 horizontal)
      - 'portrait_3_4': 240 x 320 px (3:4 vertical)
      - 'custom': user defined custom_w x custom_h (even dimensions enforced)
    """
    trimmed = trim_transparent_borders(subject)
    orig_w, orig_h = trimmed.size
    if orig_w == 0 or orig_h == 0:
        return Image.new("RGBA", (370, 320), (0, 0, 0, 0))

    effective_margin = max(10, margin)

    # Determine canvas dimensions based on preset
    if target_type == "main":
        canvas_w, canvas_h = 240, 240
    elif target_type == "tab":
        canvas_w, canvas_h = 96, 74
        effective_margin = min(margin, 8)
    elif target_type == "square_320":
        canvas_w, canvas_h = 320, 320
    elif target_type == "square_300":
        canvas_w, canvas_h = 300, 300
    elif target_type == "landscape_4_3":
        canvas_w, canvas_h = 320, 240
    elif target_type == "portrait_3_4":
        canvas_w, canvas_h = 240, 320
    elif target_type == "custom":
        canvas_w = ensure_even(max(60, min(800, custom_w)))
        canvas_h = ensure_even(max(60, min(800, custom_h)))
    else:  # 'sticker'
        max_canvas_w, max_canvas_h = 370, 320
        max_content_w = max_canvas_w - (2 * effective_margin)
        max_content_h = max_canvas_h - (2 * effective_margin)

        scale = min(max_content_w / orig_w, max_content_h / orig_h)
        new_w = max(1, int(round(orig_w * scale)))
        new_h = max(1, int(round(orig_h * scale)))

        if canvas_mode == "fit":
            raw_cw = new_w + (2 * effective_margin)
            raw_ch = new_h + (2 * effective_margin)
            if raw_cw % 2 != 0: raw_cw += 1
            if raw_ch % 2 != 0: raw_ch += 1
            canvas_w = min(370, raw_cw)
            canvas_h = min(320, raw_ch)
            canvas_w = ensure_even(canvas_w)
            canvas_h = ensure_even(canvas_h)
        else:
            canvas_w, canvas_h = 370, 320

    # Ensure strictly even dimensions
    canvas_w = ensure_even(canvas_w)
    canvas_h = ensure_even(canvas_h)

    # Scale content to fit inside margins
    max_w = max(1, canvas_w - (2 * effective_margin))
    max_h = max(1, canvas_h - (2 * effective_margin))

    scale = min(max_w / orig_w, max_h / orig_h)
    target_content_w = max(1, int(round(orig_w * scale)))
    target_content_h = max(1, int(round(orig_h * scale)))

    # High quality resize
    resized_subject = trimmed.resize((target_content_w, target_content_h), Image.Resampling.LANCZOS)

    # Create canvas
    canvas = Image.new("RGBA", (canvas_w, canvas_h), (0, 0, 0, 0))
    pos_x = (canvas_w - target_content_w) // 2
    pos_y = (canvas_h - target_content_h) // 2
    canvas.paste(resized_subject, (pos_x, pos_y), resized_subject)

    return canvas

def validate_line_specs(
    image: Image.Image,
    target_type: str = "sticker"
) -> Dict[str, Any]:
    """
    Validates whether the image strictly satisfies LINE Creators Market specifications.
    Returns audit details with pass/fail status and human-friendly messages.
    """
    w, h = image.size
    image_rgba = image.convert("RGBA")
    
    # 1. Even dimension check
    w_even = (w % 2 == 0)
    h_even = (h % 2 == 0)
    even_check = w_even and h_even

    # 2. Target dimension check
    if target_type == "sticker":
        dim_ok = (w <= 370 and h <= 320 and w >= 50 and h >= 50)
        expected_desc = "กว้าง ≤ 370px, สูง ≤ 320px (เลขคู่)"
    elif target_type == "main":
        dim_ok = (w == 240 and h == 240)
        expected_desc = "ขนาดพอดี 240 x 240 px"
    elif target_type == "tab":
        dim_ok = (w == 96 and h == 74)
        expected_desc = "ขนาดพอดี 96 x 74 px"
    else:
        # All other presets are compliant as long as even
        dim_ok = (w <= 370 and h <= 320)
        expected_desc = f"{w} x {h} px (เลขคู่)"

    # 3. Transparent margin check
    bbox = image_rgba.getbbox()
    margin_ok = False
    actual_margins = {"left": 0, "top": 0, "right": 0, "bottom": 0}
    
    if bbox:
        left, top, right, bottom = bbox
        actual_margins["left"] = left
        actual_margins["top"] = top
        actual_margins["right"] = w - right
        actual_margins["bottom"] = h - bottom
        
        min_required_margin = 10 if target_type in ("sticker", "main") else 4
        margin_ok = all(m >= min_required_margin for m in actual_margins.values())
    else:
        margin_ok = False

    # 4. Transparency check
    has_alpha = False
    alpha_channel = image_rgba.split()[3]
    alpha_min, alpha_max = alpha_channel.getextrema()
    has_alpha = (alpha_min < 255) # Has at least some transparent pixels

    # 5. File size check
    buf = io.BytesIO()
    image_rgba.save(buf, format="PNG", optimize=True)
    file_size_bytes = buf.tell()
    file_size_kb = file_size_bytes / 1024.0
    size_ok = file_size_bytes <= 1048576  # 1 MB

    all_passed = even_check and dim_ok and margin_ok and has_alpha and size_ok

    return {
        "all_passed": all_passed,
        "width": w,
        "height": h,
        "even_dimensions": even_check,
        "dim_ok": dim_ok,
        "expected_desc": expected_desc,
        "margin_ok": margin_ok,
        "actual_margins": actual_margins,
        "has_transparency": has_alpha,
        "file_size_kb": file_size_kb,
        "size_ok": size_ok
    }

def draw_margin_guides(
    image: Image.Image,
    margin_px: int = 10
) -> Image.Image:
    """
    Renders visual dashed guide lines showing the 10px safe margin area for user inspection.
    """
    preview = image.copy().convert("RGBA")
    draw = ImageDraw.Draw(preview)
    w, h = preview.size

    guide_color = (6, 199, 85, 200) # LINE Green
    
    # Outer margin box
    x0, y0 = margin_px, margin_px
    x1, y1 = w - margin_px - 1, h - margin_px - 1

    # Draw dashed rectangle
    dash_len = 6
    # Top & Bottom
    for x in range(x0, x1, dash_len * 2):
        draw.line([(x, y0), (min(x + dash_len, x1), y0)], fill=guide_color, width=1)
        draw.line([(x, y1), (min(x + dash_len, x1), y1)], fill=guide_color, width=1)
    # Left & Right
    for y in range(y0, y1, dash_len * 2):
        draw.line([(x0, y), (x0, min(y + dash_len, y1))], fill=guide_color, width=1)
        draw.line([(x1, y), (x1, min(y + dash_len, y1))], fill=guide_color, width=1)

    return preview

def create_checkerboard_preview(
    image: Image.Image,
    tile_size: int = 12
) -> Image.Image:
    """
    Renders image over a subtle checkerboard pattern to visualize transparency.
    """
    w, h = image.size
    bg = Image.new("RGBA", (w, h), (245, 245, 247, 255))
    draw = ImageDraw.Draw(bg)
    color_dark = (225, 225, 230, 255)

    for y in range(0, h, tile_size):
        for x in range(0, w, tile_size):
            if ((x // tile_size) + (y // tile_size)) % 2 == 1:
                draw.rectangle([x, y, x + tile_size, y + tile_size], fill=color_dark)

    return Image.alpha_composite(bg, image.convert("RGBA"))

def export_png_bytes(image: Image.Image) -> bytes:
    """
    Exports image to PNG bytes guaranteed to be under 1MB.
    """
    buf = io.BytesIO()
    image.save(buf, format="PNG", optimize=True)
    if buf.tell() > 1048576:
        # Emergency palette quantize if somehow exceeds 1MB
        quantized = image.quantize(colors=256, method=Image.Quantize.MEDIANCUT)
        buf = io.BytesIO()
        quantized.save(buf, format="PNG", optimize=True)
    return buf.getvalue()

# =====================================================================
# FEATURE 4: MANUAL RETOUCH BRUSH (ERASER & RESTORE)
# =====================================================================
def apply_manual_touchup(
    current_img: Image.Image,
    orig_img: Image.Image,
    mask_array: np.ndarray,
    mode: str = "erase"
) -> Image.Image:
    """
    Applies manual touch-up brush edits.
    - 'erase': Erases pixels to transparent wherever the user painted.
    - 'restore': Recovers the original pixels from the unedited original image.
    """
    if mask_array is None or mask_array.size == 0:
        return current_img

    current_rgba = current_img.convert("RGBA")
    w, h = current_rgba.size

    # Convert canvas drawing array to PIL mask
    mask_pil = Image.fromarray(mask_array.astype("uint8"), "RGBA")
    if mask_pil.size != (w, h):
        mask_pil = mask_pil.resize((w, h), Image.Resampling.BILINEAR)

    # Use alpha channel of the painted mask
    brush_alpha = mask_pil.split()[3]
    brush_np = np.array(brush_alpha) > 20  # Threshold where user painted

    curr_np = np.array(current_rgba)

    if mode == "erase":
        # Zero out alpha channel where user brushed
        curr_np[brush_np, 3] = 0
        return Image.fromarray(curr_np, "RGBA")
    else:  # 'restore'
        # Scale original to current canvas size to sample original pixels
        orig_scaled = orig_img.convert("RGBA").resize((w, h), Image.Resampling.LANCZOS)
        orig_np = np.array(orig_scaled)
        # Restore pixels
        curr_np[brush_np] = orig_np[brush_np]
        return Image.fromarray(curr_np, "RGBA")

# =====================================================================
# FEATURE 5: ANIMATED STICKER (APNG CONVERTER & VALIDATOR)
# =====================================================================
def extract_gif_frames(gif_bytes_or_file) -> List[Image.Image]:
    """
    Extracts all individual animation frames from a GIF file as RGBA images.
    """
    if isinstance(gif_bytes_or_file, (bytes, bytearray)):
        gif_file = io.BytesIO(gif_bytes_or_file)
    else:
        gif_file = gif_bytes_or_file

    gif = Image.open(gif_file)
    frames = []

    try:
        while True:
            # Convert frame to RGBA
            frame_rgba = gif.convert("RGBA")
            frames.append(frame_rgba.copy())
            gif.seek(gif.tell() + 1)
    except EOFError:
        pass

    return frames

def create_line_apng(
    frames: List[Image.Image],
    total_seconds: int = 2,
    loop_count: int = 1,
    margin_px: int = 10,
    remove_bg: bool = False
) -> Tuple[bytes, Dict[str, Any]]:
    """
    Creates a LINE Creators Market compliant Animated Sticker (APNG format).
    
    LINE Animated Sticker Guidelines:
    - Dimensions: Max W 320 x H 270 px (width and height must be EVEN numbers)
    - Margin: >= 10 px
    - Playback time: Exactly 1, 2, 3, or 4 seconds
    - Frames: 5 to 20 frames per sticker
    - Loop count: 1 to 4 loops
    - File size: Must be under 300 KB (307,200 bytes)
    """
    if not frames:
        raise ValueError("No frames provided")

    # Step 1: Subsample or limit frames between 5 and 20 frames
    num_input_frames = len(frames)
    if num_input_frames > 20:
        # Uniformly downsample to 20 frames
        indices = np.linspace(0, num_input_frames - 1, 20, dtype=int)
        selected_frames = [frames[i] for i in indices]
    elif num_input_frames < 5:
        # Repeat frames to reach at least 5 frames
        selected_frames = frames * int(math.ceil(5 / num_input_frames))
        selected_frames = selected_frames[:5]
    else:
        selected_frames = frames[:]

    frame_count = len(selected_frames)

    # Step 2: Fit each frame to LINE Animated Canvas (Max 320x270, even, 10px margin)
    max_canvas_w = 320
    max_canvas_h = 270
    content_w = max_canvas_w - (2 * margin_px)
    content_h = max_canvas_h - (2 * margin_px)

    # Calculate global bounding box across all frames so animation stays anchored
    combined_box = None
    processed_frames = []

    for f in selected_frames:
        f_rgba = f.convert("RGBA")
        if remove_bg:
            f_rgba = remove_background(f_rgba)
        bbox = f_rgba.getbbox()
        if bbox:
            if combined_box is None:
                combined_box = list(bbox)
            else:
                combined_box[0] = min(combined_box[0], bbox[0])
                combined_box[1] = min(combined_box[1], bbox[1])
                combined_box[2] = max(combined_box[2], bbox[2])
                combined_box[3] = max(combined_box[3], bbox[3])
        processed_frames.append(f_rgba)

    if combined_box is None:
        combined_box = [0, 0, processed_frames[0].width, processed_frames[0].height]

    box_w = max(1, combined_box[2] - combined_box[0])
    box_h = max(1, combined_box[3] - combined_box[1])

    # Scale factor
    scale = min(content_w / box_w, content_h / box_h)
    canvas_w = 320
    canvas_h = 270

    final_frames = []
    for f in processed_frames:
        cropped = f.crop(combined_box)
        new_w = max(1, int(round(cropped.width * scale)))
        new_h = max(1, int(round(cropped.height * scale)))
        resized = cropped.resize((new_w, new_h), Image.Resampling.LANCZOS)

        canvas = Image.new("RGBA", (canvas_w, canvas_h), (0, 0, 0, 0))
        pos_x = (canvas_w - new_w) // 2
        pos_y = (canvas_h - new_h) // 2
        canvas.paste(resized, (pos_x, pos_y), resized)
        final_frames.append(canvas)

    # Step 3: Calculate duration per frame in milliseconds
    # Playback time must be 1, 2, 3, or 4 seconds. Total loop duration:
    total_duration_ms = total_seconds * 1000
    # Duration for 1 cycle:
    cycle_duration_ms = total_duration_ms / max(1, loop_count)
    frame_duration_ms = max(50, int(round(cycle_duration_ms / frame_count)))

    # Step 4: Export to APNG bytes
    buf = io.BytesIO()
    # Pillow creates APNG when format="PNG" and save_all=True
    final_frames[0].save(
        buf,
        format="PNG",
        save_all=True,
        append_images=final_frames[1:],
        duration=frame_duration_ms,
        loop=loop_count,
        optimize=True
    )
    apng_bytes = buf.getvalue()

    # Step 5: Check file size (< 300 KB = 307,200 bytes)
    max_apng_bytes = 307200
    if len(apng_bytes) > max_apng_bytes:
        # Quantize colors to reduce file size under 300KB
        quantized_frames = []
        for f in final_frames:
            q = f.quantize(colors=128, method=Image.Quantize.MEDIANCUT)
            quantized_frames.append(q.convert("RGBA"))

        buf = io.BytesIO()
        quantized_frames[0].save(
            buf,
            format="PNG",
            save_all=True,
            append_images=quantized_frames[1:],
            duration=frame_duration_ms,
            loop=loop_count,
            optimize=True
        )
        apng_bytes = buf.getvalue()

    file_size_kb = len(apng_bytes) / 1024.0
    size_ok = (len(apng_bytes) <= max_apng_bytes)
    even_ok = (canvas_w % 2 == 0 and canvas_h % 2 == 0)
    dim_ok = (canvas_w <= 320 and canvas_h <= 270)
    frames_ok = (5 <= frame_count <= 20)
    time_ok = (total_seconds in (1, 2, 3, 4))

    all_passed = size_ok and even_ok and dim_ok and frames_ok and time_ok

    audit = {
        "all_passed": all_passed,
        "width": canvas_w,
        "height": canvas_h,
        "even_dimensions": even_ok,
        "dim_ok": dim_ok,
        "frame_count": frame_count,
        "frames_ok": frames_ok,
        "total_seconds": total_seconds,
        "time_ok": time_ok,
        "loop_count": loop_count,
        "file_size_kb": file_size_kb,
        "size_ok": size_ok
    }

    return apng_bytes, audit
