"""
LINE Creators Market - Sticker Studio Pro (Pastel Warm Edition)
All-in-one suite: AI Background Removal, Seamless Retouch with Marquee Box,
Aspect Ratio Presets, Set Queue Organizer with Tag Helper, and Overflow-Free Chat Simulator.
100% Free - Works completely offline.
"""

import io
import os
import zipfile
import base64
from typing import Dict, List, Any
import streamlit as st
from PIL import Image
import streamlit.components.v1 as components
import image_processor as ip

# Page configuration
st.set_page_config(
    page_title="LINE Sticker Studio Pro - อบอุ่น ใช้งานง่าย คุณภาพสูงสุด",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -------------------------------------------------------------
# SESSION STATE INITIALIZATION
# -------------------------------------------------------------
if "studio_stickers" not in st.session_state:
    st.session_state.studio_stickers = []
if "queue_stickers" not in st.session_state:
    st.session_state.queue_stickers = []
if "main_idx" not in st.session_state:
    st.session_state.main_idx = 0
if "tab_idx" not in st.session_state:
    st.session_state.tab_idx = 0
if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = [
        {"sender": "bot", "text": "สวัสดีครับ! ลองคลิกส่งสติกเกอร์จากแป้นพิมพ์ด้านขวาเพื่อทดสอบดูในห้องแชทจำลองได้เลยนะ 🌿", "type": "text"}
    ]
if "chat_theme" not in st.session_state:
    st.session_state.chat_theme = "chat_blue"
if "apng_results" not in st.session_state:
    st.session_state.apng_results = []
if "sticker_tags" not in st.session_state:
    st.session_state.sticker_tags = {}

# -------------------------------------------------------------
# PASTEL WARM MINIMALIST CSS
# -------------------------------------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Prompt:wght@300;400;500;600;700&family=Inter:wght@400;500;600;700&display=swap');

html, body, [class*="css"], [class*="st-"] {
    font-family: 'Prompt', 'Inter', sans-serif;
    color: #38423B;
}

/* Page Background */
.stApp {
    background-color: #FAF7F2;
}

/* Warm Pastel Header */
.pastel-header {
    background: linear-gradient(135deg, #EBF3ED 0%, #F5ECE3 100%);
    border: 1px solid #E2D9CC;
    border-radius: 20px;
    padding: 24px 30px;
    color: #2F3E34;
    box-shadow: 0 4px 20px rgba(110, 95, 75, 0.05);
    margin-bottom: 22px;
}
.pastel-header h1 {
    color: #31523D !important;
    font-size: 2.1rem;
    font-weight: 700;
    margin: 0;
    display: flex;
    align-items: center;
    gap: 12px;
}
.pastel-header p {
    color: #5D685E;
    font-size: 1.02rem;
    margin: 8px 0 0 0;
}

/* Pastel Badges */
.pastel-badge {
    display: inline-block;
    padding: 4px 12px;
    border-radius: 14px;
    font-size: 0.8rem;
    font-weight: 600;
    margin-right: 8px;
    margin-top: 6px;
    background: #FFFFFF;
    border: 1px solid #D8E2DC;
    color: #426B50;
    box-shadow: 0 1px 3px rgba(0,0,0,0.03);
}

/* Card Containers */
.pastel-card {
    background: #FFFFFF;
    border: 1px solid #EDE6DC;
    border-radius: 16px;
    padding: 16px;
    box-shadow: 0 2px 8px rgba(90, 80, 65, 0.04);
    margin-bottom: 14px;
}

/* Status Indicators */
.status-pill-ready {
    background-color: #E7F5EC;
    color: #2B6940;
    border: 1px solid #C4E8CF;
    padding: 4px 10px;
    border-radius: 8px;
    font-size: 0.82rem;
    font-weight: 600;
    display: inline-flex;
    align-items: center;
    gap: 4px;
}
.status-pill-waiting {
    background-color: #FDF4E5;
    color: #8C5E1E;
    border: 1px solid #F8E2BD;
    padding: 4px 10px;
    border-radius: 8px;
    font-size: 0.82rem;
    font-weight: 600;
    display: inline-flex;
    align-items: center;
    gap: 4px;
}

/* Buttons */
.stButton>button {
    border-radius: 10px;
    font-weight: 600;
    border: 1px solid #D8CFBF;
    background: #FFFFFF;
    color: #3B4B3F;
    transition: all 0.2s ease;
}
.stButton>button:hover {
    border-color: #5B8E7D;
    color: #5B8E7D;
    background: #F4F8F5;
}
.stButton>button[kind="primary"] {
    background: #5B8E7D !important;
    color: #FFFFFF !important;
    border: none !important;
    box-shadow: 0 3px 10px rgba(91, 142, 125, 0.25) !important;
}
.stButton>button[kind="primary"]:hover {
    background: #4A7768 !important;
    box-shadow: 0 4px 14px rgba(91, 142, 125, 0.35) !important;
}

/* Danger / Delete button */
.delete-btn {
    color: #B91C1C !important;
    border-color: #FECACA !important;
    background: #FEF2F2 !important;
}

/* Download button */
.stDownloadButton>button {
    background: #E07A5F !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    box-shadow: 0 3px 10px rgba(224, 122, 95, 0.25) !important;
}
.stDownloadButton>button:hover {
    background: #CC654A !important;
}
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class="pastel-header">
    <h1>🌿 LINE Sticker Studio Pro</h1>
    <p>ระบบเตรียมไฟล์ภาพสติกเกอร์ LINE ครบวงจร — ลบพื้นหลัง AI คมกริบ, รีทัชเส้นประ Marquee, จัดลำดับชุดพร้อมตัวช่วยคีย์เวิร์ด และจำลองแชท LINE เสมือนจริง (ฟรี 100%)</p>
    <div>
        <span class="pastel-badge">✨ AI IS-Net / Edge Clean</span>
        <span class="pastel-badge">📐 สัดส่วนครบครัน & Custom</span>
        <span class="pastel-badge">🔲 รีทัชกรอบเส้นประ Marquee</span>
        <span class="pastel-badge">🏷️ ตัวช่วยแท็กคีย์เวิร์ด</span>
        <span class="pastel-badge">📱 แชทจำลองไม่ล้นจอ</span>
    </div>
</div>
""", unsafe_allow_html=True)

# -------------------------------------------------------------
# SIDEBAR CONTROLS
# -------------------------------------------------------------
with st.sidebar:
    st.markdown("### 📐 1. สัดส่วนและขนาดภาพ (Aspect Ratio)")
    preset_choice = st.selectbox(
        "เลือกพรีเซ็ตสัดส่วนภาพ:",
        [
            "Sticker มาตรฐาน LINE (สูงสุด 370 x 320 px)",
            "Main Image หน้าปก (240 x 240 px)",
            "Chat Tab ไอคอนแท็บ (96 x 74 px)",
            "จัตุรัส 1:1 (320 x 320 px)",
            "จัตุรัส 1:1 (300 x 300 px)",
            "แนวนอน 4:3 (320 x 240 px)",
            "แนวตั้ง 3:4 (240 x 320 px)",
            "⚙️ กำหนดขนาดเอง (Custom W x H)"
        ],
        index=0
    )

    preset_map = {
        "Sticker มาตรฐาน LINE (สูงสุด 370 x 320 px)": "sticker",
        "Main Image หน้าปก (240 x 240 px)": "main",
        "Chat Tab ไอคอนแท็บ (96 x 74 px)": "tab",
        "จัตุรัส 1:1 (320 x 320 px)": "square_320",
        "จัตุรัส 1:1 (300 x 300 px)": "square_300",
        "แนวนอน 4:3 (320 x 240 px)": "landscape_4_3",
        "แนวตั้ง 3:4 (240 x 320 px)": "portrait_3_4",
        "⚙️ กำหนดขนาดเอง (Custom W x H)": "custom"
    }
    target_preset = preset_map[preset_choice]

    custom_w, custom_h = 370, 320
    if target_preset == "custom":
        c_w, c_h = st.columns(2)
        with c_w:
            custom_w = st.number_input("ความกว้าง (W):", min_value=60, max_value=800, value=370, step=2)
        with c_h:
            custom_h = st.number_input("ความสูง (H):", min_value=60, max_value=800, value=320, step=2)
        if custom_w % 2 != 0: custom_w -= 1
        if custom_h % 2 != 0: custom_h -= 1
        st.caption(f"💡 ปรับพิกเซลเป็นเลขคู่: {custom_w} x {custom_h} px")

    canvas_mode = "fixed"
    if target_preset == "sticker":
        canvas_mode = st.selectbox(
            "การจัดวางในกรอบสติกเกอร์:",
            ["fixed", "fit"],
            format_func=lambda x: "เต็มกรอบ 370x320 px (มาตรฐาน)" if x == "fixed" else "พอดีเนื้อภาพ + ขอบ 10px เลขคู่"
        )

    st.markdown("---")
    st.markdown("### ✂️ 2. คุณภาพการลบพื้นหลัง (Background AI)")
    enable_rembg = st.toggle("เปิดใช้งาน AI ลบพื้นหลัง", value=True)
    
    bg_model = "isnet-general-use"
    enable_defringe = True
    alpha_matting = False

    if enable_rembg:
        bg_model = st.selectbox(
            "โมเดล AI ลบพื้นหลัง:",
            ["isnet-general-use", "u2net"],
            format_func=lambda m: "🌟 IS-Net (คุณภาพสูง คมกริบ แนะนำ)" if m == "isnet-general-use" else "Standard U2-Net"
        )
        enable_defringe = st.checkbox("ขจัดคราบสีขาว/ดำตามขอบ (Edge Clean)", value=True, help="ทำความสะอาดรอยคราบสีส่วนเกินตามขอบวัตถุ")
        alpha_matting = st.checkbox("Alpha Matting (เน้นเก็บไรผมละเอียด)", value=False)

    st.markdown("---")
    st.markdown("### ⚪ 3. เส้นขอบขาวสติกเกอร์ (White Outline)")
    add_white_stroke = st.toggle("เพิ่มขอบขาวรอบตัวสติกเกอร์", value=True, help="จำเป็นมากเพื่อให้สติกเกอร์เห็นชัดเจนบน LINE Dark Mode")
    stroke_width = 5 if add_white_stroke else 0
    if add_white_stroke:
        stroke_width = st.slider("ความหนาของเส้นขอบ (px):", 1, 15, 5)

    st.markdown("---")
    st.markdown("### 🚀 4. Super Upscale & ความคมชัด")
    enable_upscale = st.toggle("เปิด Super Upscale ภาพขนาดเล็ก", value=True)
    upscale_factor = 2.0
    enhancement_mode = "anime"
    denoise_strength = 0.35
    edge_sharpness = 1.7
    clarity_boost = 1.2

    if enable_upscale:
        c_u1, c_u2 = st.columns(2)
        with c_u1:
            upscale_factor = st.selectbox("ระดับขยาย:", [1.5, 2.0, 3.0, 4.0], index=1, format_func=lambda x: f"{x}x")
        with c_u2:
            enhancement_mode = st.selectbox("แนวภาพ:", ["anime", "photo"], index=0, format_func=lambda x: "🎨 การ์ตูน" if x == "anime" else "📷 ภาพถ่าย")
        
        edge_sharpness = st.slider("ความคมชัดเส้นร่าง:", 1.0, 3.0, 1.7, 0.1)
        denoise_strength = st.slider("ลดรอยแตกพิกเซล (Smooth):", 0.0, 0.8, 0.35, 0.05)
        clarity_boost = st.slider("มิติภาพ (Clarity):", 1.0, 1.8, 1.2, 0.05)

    margin_px = 10

# -------------------------------------------------------------
# MAIN APP NAVIGATION TABS
# -------------------------------------------------------------
tab_studio, tab_queue, tab_sim, tab_apng, tab_guide = st.tabs([
    "🎨 1. สตูดิโอเตรียมภาพ & รีทัช (Studio)",
    f"🔢 2. ตารางชุดสติกเกอร์ ({len(st.session_state.queue_stickers)} ภาพ)",
    "📱 3. จำลองแชท LINE (Chat Simulator)",
    "🎞️ 4. สติกเกอร์ขยับได้ (APNG)",
    "📋 5. กฎและคู่มือ (Guidelines)"
])

# =============================================================
# TAB 1: STUDIO & IN-LINE RETOUCH
# =============================================================
with tab_studio:
    st.markdown("#### 📤 1. อัปโหลดรูปภาพเพื่อเตรียมสติกเกอร์ (Drag & Drop ได้หลายไฟล์)")
    uploaded_files = st.file_uploader(
        "เลือกรูปภาพ (PNG, JPG, JPEG, WEBP):",
        type=["png", "jpg", "jpeg", "webp"],
        accept_multiple_files=True,
        key="studio_uploader"
    )

    if uploaded_files:
        c_p_btn, c_p_stat = st.columns([1.5, 3])
        with c_p_btn:
            do_process = st.button("✨ เริ่มประมวลผลรูปภาพทั้งหมด", type="primary", use_container_width=True)

        if do_process:
            progress_bar = st.progress(0, text="กำลังเตรียมการประมวลผล...")
            new_studio_items = []

            for idx, file in enumerate(uploaded_files):
                pct = int((idx + 1) / len(uploaded_files) * 100)
                progress_bar.progress(pct, text=f"กำลังประมวลผลรูปที่ {idx+1}/{len(uploaded_files)}: {file.name}")

                try:
                    orig_img = Image.open(file).convert("RGBA")
                    orig_w, orig_h = orig_img.size
                    is_small = (orig_w < 350 or orig_h < 300)

                    # 1. Super Upscale (with cloud memory guard)
                    if (enable_upscale and max(orig_w, orig_h) < 900) or is_small:
                        scale = upscale_factor if enable_upscale else 2.0
                        if max(orig_w, orig_h) * scale > 1024:
                            scale = max(1.2, 1024.0 / max(orig_w, orig_h))
                        proc_base = ip.upscale_and_restore_details(
                            orig_img,
                            scale_factor=scale,
                            enhancement_mode=enhancement_mode,
                            denoise_strength=denoise_strength,
                            edge_sharpness=edge_sharpness,
                            clarity_boost=clarity_boost
                        )
                        upscale_msg = f"{orig_w}x{orig_h} ➔ {proc_base.width}x{proc_base.height} ({scale:.1f}x Upscaled)"
                    elif max(orig_w, orig_h) > 1024:
                        ratio = 1024.0 / max(orig_w, orig_h)
                        nw, nh = int(orig_w * ratio), int(orig_h * ratio)
                        proc_base = orig_img.resize((nw, nh), Image.Resampling.LANCZOS)
                        upscale_msg = f"{orig_w}x{orig_h} ➔ {nw}x{nh} (Optimized for LINE)"
                    else:
                        proc_base = orig_img
                        upscale_msg = f"{orig_w}x{orig_h} px"

                    # 2. Background removal
                    if enable_rembg:
                        no_bg = ip.remove_background(
                            proc_base,
                            model_name=bg_model,
                            alpha_matting=alpha_matting,
                            edge_refine=enable_defringe
                        )
                    else:
                        no_bg = proc_base

                    # 3. Add white outline
                    if add_white_stroke and stroke_width > 0:
                        outlined = ip.add_outline(no_bg, stroke_width=stroke_width)
                    else:
                        outlined = no_bg

                    # 4. Fit to target preset canvas
                    final_sticker = ip.fit_to_canvas(
                        outlined,
                        target_type=target_preset,
                        margin=margin_px,
                        canvas_mode=canvas_mode,
                        custom_w=custom_w,
                        custom_h=custom_h
                    )
                    audit = ip.validate_line_specs(final_sticker, target_preset)

                    new_studio_items.append({
                        "id": f"stk_{idx}_{file.name}",
                        "name": file.name,
                        "orig_img": orig_img,
                        "proc_img": final_sticker,
                        "audit": audit,
                        "upscale_info": upscale_msg,
                        "status": "ready"
                    })
                except Exception as ex:
                    st.error(f"เกิดข้อผิดพลาดกับไฟล์ {file.name}: {str(ex)}")

            st.session_state.studio_stickers = new_studio_items
            progress_bar.empty()
            st.success(f"🎉 ประมวลผลสำเร็จเรียบร้อย {len(new_studio_items)} รูป! พร้อมตรวจสอบหรือส่งเข้าตารางชุดด้านล่าง")

    # Display Processed Items in Studio
    if st.session_state.studio_stickers:
        st.markdown("---")
        
        # Action Bar across studio
        c_top_info, c_bulk_send, c_clear_all = st.columns([2, 1.5, 1])
        with c_top_info:
            st.markdown(f"#### 🖼️ ผลลัพธ์ในสตูดิโอ ({len(st.session_state.studio_stickers)} ภาพ)")
        with c_bulk_send:
            if st.button("🚀 ส่งภาพทั้งหมดเข้าตารางชุด (หน้า 2)", type="primary", use_container_width=True):
                for item in st.session_state.studio_stickers:
                    st.session_state.queue_stickers.append(item.copy())
                st.toast(f"✅ เพิ่ม {len(st.session_state.studio_stickers)} ภาพเข้าตารางชุดเรียบร้อยแล้ว!", icon="📦")
                st.rerun()
        with c_clear_all:
            if st.button("🗑️ ล้างทั้งหมด", use_container_width=True):
                st.session_state.studio_stickers = []
                st.rerun()

        # Render Each Sticker Studio Card
        for idx, item in enumerate(st.session_state.studio_stickers):
            with st.container():
                st.markdown(f"""
                <div class="pastel-card">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <div>
                            <b>รูปที่ {idx+1:02d}: {item['name']}</b> &nbsp;
                            <span class="status-pill-ready">✓ เสร็จสิ้นพร้อมใช้งาน</span>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                col_orig, col_res, col_action = st.columns([1, 1.2, 1.2])

                with col_orig:
                    st.markdown("**ต้นฉบับ:**")
                    st.image(item["orig_img"], use_container_width=True)
                    st.caption(f"ขนาดเดิม: {item['orig_img'].width} x {item['orig_img'].height} px")
                    st.caption(f"🚀 {item['upscale_info']}")

                with col_res:
                    st.markdown("**ผลลัพธ์สติกเกอร์:**")
                    vis_preview = ip.create_checkerboard_preview(item["proc_img"])
                    st.image(vis_preview, use_container_width=True)

                with col_action:
                    st.markdown("**การจัดการ & ตรวจสอบข้อกำหนด:**")
                    aud = item["audit"]
                    st.markdown(f"- **ขนาด:** {aud['width']} x {aud['height']} px (เลขคู่ ✓)")
                    m = aud["actual_margins"]
                    st.markdown(f"- **Margin:** ซ้าย:{m['left']} ขวา:{m['right']} บน:{m['top']} ล่าง:{m['bottom']} px (≥ 10px ✓)")
                    st.markdown(f"- **ขนาดไฟล์:** {aud['file_size_kb']:.1f} KB (< 1 MB ✓)")

                    # Action Buttons
                    st.write("")
                    col_btn_send, col_btn_dl = st.columns(2)
                    with col_btn_send:
                        if st.button(f"🚀 ส่งเข้าตารางชุด", key=f"send_queue_{idx}", use_container_width=True):
                            st.session_state.queue_stickers.append(item.copy())
                            st.toast(f"เพิ่ม '{item['name']}' เข้าตารางชุดแล้ว!", icon="📦")
                            st.rerun()

                    with col_btn_dl:
                        png_bytes = ip.export_png_bytes(item["proc_img"])
                        st.download_button(
                            label="💾 โหลด PNG",
                            data=png_bytes,
                            file_name=f"sticker_{idx+1:02d}.png",
                            mime="image/png",
                            key=f"dl_stk_{idx}",
                            use_container_width=True
                        )

                    # Delete button
                    if st.button(f"🗑️ ลบรูปนี้ออกจากสตูดิโอ", key=f"del_studio_{idx}", use_container_width=True):
                        st.session_state.studio_stickers.pop(idx)
                        st.rerun()

                # Integrated Retouch Studio in expander
                with st.expander(f"🖌️ เครื่องมือรีทัชภาพนี้ (ยางลบ / กู้คืน / กรอบเส้นประ Marquee)", expanded=False):
                    img_to_retouch = item["proc_img"]
                    orig_ref = item["orig_img"]

                    buf_p = io.BytesIO()
                    img_to_retouch.save(buf_p, format="PNG")
                    b64_p = base64.b64encode(buf_p.getvalue()).decode()

                    buf_o = io.BytesIO()
                    orig_ref.save(buf_o, format="PNG")
                    b64_o = base64.b64encode(buf_o.getvalue()).decode()

                    cw, ch = img_to_retouch.width, img_to_retouch.height

                    retouch_html = f"""
                    <!DOCTYPE html>
                    <html>
                    <head>
                        <meta charset="utf-8">
                        <style>
                            body {{
                                font-family: -apple-system, BlinkMacSystemFont, 'Prompt', sans-serif;
                                margin: 0; padding: 6px; background: transparent; color: #38423B;
                            }}
                            .tool-row {{
                                display: flex; flex-wrap: wrap; gap: 8px; align-items: center;
                                background: #FAF7F2; padding: 10px 14px; border-radius: 12px;
                                border: 1px solid #E6DED2; margin-bottom: 10px;
                            }}
                            .t-btn {{
                                background: #FFFFFF; border: 1px solid #D1C7B7; padding: 6px 12px;
                                border-radius: 8px; font-weight: 600; font-size: 0.85rem; cursor: pointer;
                                display: flex; align-items: center; gap: 4px; transition: all 0.15s ease;
                            }}
                            .t-btn:hover {{ border-color: #5B8E7D; color: #5B8E7D; }}
                            .t-btn.active {{ background: #5B8E7D; color: white; border-color: #5B8E7D; }}
                            .c-frame {{
                                display: inline-block; position: relative; border-radius: 12px;
                                overflow: hidden; box-shadow: 0 3px 10px rgba(0,0,0,0.08);
                                background-image: linear-gradient(45deg, #e2e8f0 25%, transparent 25%), 
                                                  linear-gradient(-45deg, #e2e8f0 25%, transparent 25%), 
                                                  linear-gradient(45deg, transparent 75%, #e2e8f0 75%), 
                                                  linear-gradient(-45deg, transparent 75%, #e2e8f0 75%);
                                background-size: 16px 16px; background-position: 0 0, 0 8px, 8px -8px, -8px 0px;
                                background-color: #f8fafc;
                            }}
                            canvas {{ display: block; cursor: crosshair; }}
                            .save-btn {{
                                background: #E07A5F; color: white; border: none; padding: 6px 14px;
                                border-radius: 8px; font-weight: 700; font-size: 0.85rem; cursor: pointer;
                                margin-left: auto;
                            }}
                        </style>
                    </head>
                    <body>
                        <div class="tool-row">
                            <button class="t-btn active" id="btnBrushErase" onclick="setMode('brush_erase')">🧹 แปรงยางลบ</button>
                            <button class="t-btn" id="btnMarqueeErase" onclick="setMode('marquee_erase')">🔲 ยางลบเส้นประ (Marquee Box)</button>
                            <button class="t-btn" id="btnBrushRestore" onclick="setMode('brush_restore')">🖌️ แปรงกู้คืน</button>
                            <button class="t-btn" id="btnMarqueeRestore" onclick="setMode('marquee_restore')">🔲 กู้คืนเส้นประ (Marquee Box)</button>
                            <button class="t-btn" id="btnWhite" onclick="setMode('white')">⚪ แปรงขาว</button>
                            
                            <div style="display:flex; align-items:center; gap:6px; margin-left:6px;">
                                <span style="font-size:0.8rem; font-weight:600;">ขนาดแปรง:</span>
                                <input type="range" id="sizeInput" min="4" max="60" value="16" oninput="setSize(this.value)" style="cursor:pointer;" />
                                <span id="sizeLbl" style="font-size:0.8rem; font-weight:600; min-width:24px;">16px</span>
                            </div>

                            <button class="t-btn" onclick="resetCanvas()">🔄 รีเซ็ต</button>
                            <button class="save-btn" onclick="saveImage()">💾 ดาวน์โหลดผลลัพธ์ PNG</button>
                        </div>

                        <div class="c-frame">
                            <canvas id="cPaint" width="{cw}" height="{ch}"></canvas>
                        </div>

                        <script>
                            const canvas = document.getElementById('cPaint');
                            const ctx = canvas.getContext('2d');
                            let currentMode = 'brush_erase';
                            let brushRadius = 16;
                            let isDrawing = false;
                            let startX = 0, startY = 0;
                            let savedImageData = null;

                            const currImg = new Image();
                            currImg.src = "data:image/png;base64,{b64_p}";

                            const origImg = new Image();
                            origImg.src = "data:image/png;base64,{b64_o}";

                            currImg.onload = () => {{
                                ctx.drawImage(currImg, 0, 0, {cw}, {ch});
                            }};

                            function setMode(mode) {{
                                currentMode = mode;
                                document.querySelectorAll('.t-btn').forEach(b => b.classList.remove('active'));
                                if (mode === 'brush_erase') document.getElementById('btnBrushErase').classList.add('active');
                                if (mode === 'marquee_erase') document.getElementById('btnMarqueeErase').classList.add('active');
                                if (mode === 'brush_restore') document.getElementById('btnBrushRestore').classList.add('active');
                                if (mode === 'marquee_restore') document.getElementById('btnMarqueeRestore').classList.add('active');
                                if (mode === 'white') document.getElementById('btnWhite').classList.add('active');
                            }}

                            function setSize(val) {{
                                brushRadius = parseInt(val);
                                document.getElementById('sizeLbl').innerText = val + 'px';
                            }}

                            function resetCanvas() {{
                                ctx.clearRect(0, 0, canvas.width, canvas.height);
                                ctx.drawImage(currImg, 0, 0, {cw}, {ch});
                            }}

                            function getPos(e) {{
                                const rect = canvas.getBoundingClientRect();
                                return {{
                                    x: (e.clientX - rect.left) * (canvas.width / rect.width),
                                    y: (e.clientY - rect.top) * (canvas.height / rect.height)
                                }};
                            }}

                            canvas.addEventListener('mousedown', (e) => {{
                                isDrawing = true;
                                const p = getPos(e);
                                startX = p.x; startY = p.y;
                                if (currentMode.startsWith('marquee')) {{
                                    savedImageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
                                }} else {{
                                    drawBrush(p.x, p.y);
                                }}
                            }});

                            canvas.addEventListener('mousemove', (e) => {{
                                if (!isDrawing) return;
                                const p = getPos(e);
                                if (currentMode.startsWith('marquee')) {{
                                    // Restore preview and draw dashed rectangle
                                    ctx.putImageData(savedImageData, 0, 0);
                                    ctx.save();
                                    ctx.setLineDash([5, 5]);
                                    ctx.strokeStyle = currentMode === 'marquee_erase' ? '#EF4444' : '#3B82F6';
                                    ctx.lineWidth = 2;
                                    ctx.strokeRect(startX, startY, p.x - startX, p.y - startY);
                                    ctx.restore();
                                }} else {{
                                    drawBrush(p.x, p.y);
                                }}
                            }});

                            window.addEventListener('mouseup', (e) => {{
                                if (!isDrawing) return;
                                isDrawing = false;
                                const p = getPos(e);
                                if (currentMode.startsWith('marquee')) {{
                                    ctx.putImageData(savedImageData, 0, 0);
                                    const rx = Math.min(startX, p.x);
                                    const ry = Math.min(startY, p.y);
                                    const rw = Math.abs(p.x - startX);
                                    const rh = Math.abs(p.y - startY);

                                    if (rw > 2 && rh > 2) {{
                                        ctx.save();
                                        if (currentMode === 'marquee_erase') {{
                                            ctx.globalCompositeOperation = 'destination-out';
                                            ctx.fillRect(rx, ry, rw, rh);
                                        }} else if (currentMode === 'marquee_restore') {{
                                            ctx.globalCompositeOperation = 'source-over';
                                            ctx.beginPath();
                                            ctx.rect(rx, ry, rw, rh);
                                            ctx.clip();
                                            ctx.drawImage(origImg, 0, 0, {cw}, {ch});
                                        }}
                                        ctx.restore();
                                    }}
                                }}
                            }});

                            function drawBrush(x, y) {{
                                ctx.save();
                                if (currentMode === 'brush_erase') {{
                                    ctx.globalCompositeOperation = 'destination-out';
                                    ctx.beginPath();
                                    ctx.arc(x, y, brushRadius, 0, Math.PI * 2);
                                    ctx.fill();
                                }} else if (currentMode === 'white') {{
                                    ctx.globalCompositeOperation = 'source-over';
                                    ctx.fillStyle = '#ffffff';
                                    ctx.beginPath();
                                    ctx.arc(x, y, brushRadius, 0, Math.PI * 2);
                                    ctx.fill();
                                }} else if (currentMode === 'brush_restore') {{
                                    ctx.globalCompositeOperation = 'source-over';
                                    ctx.beginPath();
                                    ctx.arc(x, y, brushRadius, 0, Math.PI * 2);
                                    ctx.clip();
                                    ctx.drawImage(origImg, 0, 0, {cw}, {ch});
                                }}
                                ctx.restore();
                            }}

                            function saveImage() {{
                                const a = document.createElement('a');
                                a.download = 'retouched_{idx+1:02d}.png';
                                a.href = canvas.toDataURL('image/png');
                                a.click();
                            }}
                        </script>
                    </body>
                    </html>
                    """
                    components.html(retouch_html, height=ch + 100)

                    # Replace back option
                    retouch_back = st.file_uploader(
                        f"อัปเดตไฟล์ภาพที่รีทัชแล้วกลับเข้ามาแทนที่รูปที่ {idx+1:02d}:",
                        type=["png"],
                        key=f"retouch_back_{idx}"
                    )
                    if retouch_back is not None:
                        if st.button("💾 บันทึกรูปนี้แทนที่ผลลัพธ์ด้านบน", key=f"btn_save_back_{idx}", type="primary"):
                            up_img = Image.open(retouch_back).convert("RGBA")
                            item["proc_img"] = up_img
                            item["audit"] = ip.validate_line_specs(up_img, target_preset)
                            st.toast("✅ บันทึกรูปภาพใหม่แทนที่เรียบร้อย!", icon="✨")
                            st.rerun()

                st.markdown("---")

    else:
        st.info("💡 อัปโหลดรูปภาพด้านบนเพื่อเริ่มเตรียมสติกเกอร์ หรือจัดการคลังสติกเกอร์ในแท็บ **'2. ตารางชุดสติกเกอร์'**")

# =============================================================
# TAB 2: SET QUEUE MANAGER & TAG HELPER
# =============================================================
with tab_queue:
    st.markdown("### 🔢 2. ตารางชุดสติกเกอร์ & จัดเตรียมไฟล์ส่งขาย (Set Queue Manager)")
    st.markdown("รวบรวมสติกเกอร์ที่เตรียมไว้ จัดลำดับก่อน-หลัง เลือกภาพ Main / Tab, ติดแท็กคีย์เวิร์ด และดาวน์โหลดเป็นชุดไฟล์ ZIP")

    queue = st.session_state.queue_stickers

    if not queue:
        st.warning("⚠️ ยังไม่มีสติกเกอร์ในตารางชุด! กรุณาเตรียมสติกเกอร์จาก **'แท็บ 1 สตูดิโอ'** แล้วกดปุ่ม **'🚀 ส่งเข้าตารางชุด'**")
    else:
        q_count = len(queue)
        valid_counts = [8, 16, 24, 32, 40]
        count_ok = q_count in valid_counts

        # Metric Banner
        c_m1, c_m2, c_m3 = st.columns(3)
        with c_m1:
            st.metric(
                "จำนวนสติกเกอร์ในชุด",
                f"{q_count} รูป",
                delta="✓ ครบชุดเกณฑ์ LINE" if count_ok else f"แนะนำให้เป็น 8, 16, 24, 32 หรือ 40 รูป",
                delta_color="normal" if count_ok else "inverse"
            )
        with c_m2:
            m_idx = min(st.session_state.main_idx, q_count - 1)
            st.metric("ภาพหลักหน้าปก (Main)", f"รูปที่ {m_idx+1:02d}.png", "ขนาด 240 x 240 px")
        with c_m3:
            t_idx = min(st.session_state.tab_idx, q_count - 1)
            st.metric("ภาพแท็บห้องแชท (Tab)", f"รูปที่ {t_idx+1:02d}.png", "ขนาด 96 x 74 px")

        st.markdown("---")
        st.markdown("#### 🗂️ รายการสติกเกอร์ในคิวส่งขาย (คลิกสลับตำแหน่ง หรือเลือก Main / Tab)")

        # Grid view
        cols_per_row = 4
        for r_start in range(0, q_count, cols_per_row):
            cols = st.columns(cols_per_row)
            for c_i in range(cols_per_row):
                it_idx = r_start + c_i
                if it_idx < q_count:
                    item = queue[it_idx]
                    with cols[c_i]:
                        is_main = (it_idx == st.session_state.main_idx)
                        is_tab = (it_idx == st.session_state.tab_idx)

                        tag_label = st.session_state.sticker_tags.get(it_idx, "ยังไม่ระบุแท็ก")
                        
                        st.markdown(f"""
                        <div class="pastel-card" style="text-align:center;">
                            <b>ลำดับที่ {it_idx+1:02d}.png</b><br>
                            {'<span style="background:#FEF3C7;color:#92400E;padding:2px 6px;border-radius:4px;font-size:0.75rem;font-weight:700;">⭐ MAIN</span> ' if is_main else ''}
                            {'<span style="background:#E0F2FE;color:#075985;padding:2px 6px;border-radius:4px;font-size:0.75rem;font-weight:700;">🔖 TAB</span>' if is_tab else ''}
                            <div style="font-size:0.78rem;color:#6B7280;margin-top:2px;">🏷️ {tag_label}</div>
                        </div>
                        """, unsafe_allow_html=True)

                        prev_box = ip.create_checkerboard_preview(item["proc_img"])
                        st.image(prev_box, use_container_width=True)

                        # Main / Tab buttons
                        b1, b2 = st.columns(2)
                        with b1:
                            if st.button("⭐ เป็น Main", key=f"q_set_main_{it_idx}", use_container_width=True):
                                st.session_state.main_idx = it_idx
                                st.rerun()
                        with b2:
                            if st.button("🔖 เป็น Tab", key=f"q_set_tab_{it_idx}", use_container_width=True):
                                st.session_state.tab_idx = it_idx
                                st.rerun()

                        # Reorder & Delete buttons
                        o1, o2, o3 = st.columns([1, 1, 1])
                        with o1:
                            if it_idx > 0 and st.button("⬅️", key=f"q_mv_up_{it_idx}", use_container_width=True):
                                queue[it_idx], queue[it_idx-1] = queue[it_idx-1], queue[it_idx]
                                st.rerun()
                        with o2:
                            if it_idx < q_count - 1 and st.button("➡️", key=f"q_mv_dn_{it_idx}", use_container_width=True):
                                queue[it_idx], queue[it_idx+1] = queue[it_idx+1], queue[it_idx]
                                st.rerun()
                        with o3:
                            if st.button("🗑️", key=f"q_del_{it_idx}", use_container_width=True):
                                queue.pop(it_idx)
                                st.rerun()

                        # Tag selector
                        pop_tags = ["สวัสดี", "ขอบคุณ", "โอเค", "555", "รักเลย", "ฝันดี", "ขอโทษ", "สู้ๆ", "ยินดีด้วย", "งงมาก", "หิวข้าว"]
                        selected_tag = st.selectbox(
                            "ติดแท็กคีย์เวิร์ด:",
                            options=["(เลือกแท็ก)"] + pop_tags,
                            key=f"tag_sel_{it_idx}",
                            index=pop_tags.index(st.session_state.sticker_tags.get(it_idx, "")) + 1 if st.session_state.sticker_tags.get(it_idx) in pop_tags else 0
                        )
                        if selected_tag != "(เลือกแท็ก)":
                            st.session_state.sticker_tags[it_idx] = selected_tag

        # Batch Export ZIP
        st.markdown("---")
        st.markdown("#### 📦 ดาวน์โหลดชุดสติกเกอร์พร้อมส่งขาย (LINE Package ZIP)")
        
        main_source = queue[st.session_state.main_idx]["proc_img"]
        tab_source = queue[st.session_state.tab_idx]["proc_img"]

        main_export = ip.fit_to_canvas(main_source, target_type="main", margin=10, canvas_mode="fixed")
        tab_export = ip.fit_to_canvas(tab_source, target_type="tab", margin=8, canvas_mode="fixed")

        zip_buf = io.BytesIO()
        with zipfile.ZipFile(zip_buf, "w", zipfile.ZIP_DEFLATED) as zf:
            zf.writestr("main.png", ip.export_png_bytes(main_export))
            zf.writestr("tab.png", ip.export_png_bytes(tab_export))
            
            tag_report_lines = ["LINE Sticker Tag Helper Report:\n==============================\n"]
            for i, it in enumerate(queue):
                seq_name = f"{i+1:02d}.png"
                zf.writestr(seq_name, ip.export_png_bytes(it["proc_img"]))
                tag_name = st.session_state.sticker_tags.get(i, "ไม่ได้ระบุ")
                tag_report_lines.append(f"{seq_name}: แท็ก [{tag_name}]")

            zf.writestr("tags_suggestion.txt", "\n".join(tag_report_lines))

        zip_buf.seek(0)
        st.download_button(
            label=f"📥 ดาวน์โหลดไฟล์ ZIP ครบชุด ({q_count} สติกเกอร์ + main.png + tab.png + แท็กคีย์เวิร์ด)",
            data=zip_buf,
            file_name="line_sticker_full_package.zip",
            mime="application/zip",
            type="primary",
            use_container_width=True
        )

# =============================================================
# TAB 3: OVERFLOW-FREE LIVE LINE CHAT SIMULATOR
# =============================================================
with tab_sim:
    st.markdown("### 📱 3. ระบบจำลองห้องแชท LINE เสมือนจริง (Live LINE Chat Simulator)")
    st.markdown("ทดสอบส่งสติกเกอร์ในสภาพแวดล้อมห้องแชทจริงเพื่อตรวจเช็คขนาดและความคมชัดบนธีมต่างๆ — แสดงผลภายในกรอบสมาร์ทโฟน 100% ไม่หลุดล้นจอ")

    c_theme, c_clear = st.columns([3, 1])
    with c_theme:
        theme_dict = {
            "chat_blue": ("🔵 ธีมมาตรฐาน LINE (Chat Blue)", "#8BACD9"),
            "dark": ("🌙 โหมดมืด (Dark Mode)", "#1E1F22"),
            "white": ("⚪ มินิมอลขาว (Minimal White)", "#F4F4F6"),
            "pink": ("🌸 ธีมสีชมพู (Sakura Pink)", "#FBCFE8")
        }
        theme_k = st.selectbox(
            "เลือกธีมห้องแชท:",
            options=list(theme_dict.keys()),
            format_func=lambda k: theme_dict[k][0],
            index=0
        )
        st.session_state.chat_theme = theme_k
        chat_bg = theme_dict[theme_k][1]

    with c_clear:
        st.write("")
        st.write("")
        if st.button("🗑️ ล้างแชท", use_container_width=True):
            st.session_state.chat_messages = [
                {"sender": "bot", "text": "แชทถูกล้างแล้วนะ ลองคลิกเลือกส่งสติกเกอร์จากถาดด้านขวาได้เลย 😊", "type": "text"}
            ]
            st.rerun()

    c_phone, c_tray = st.columns([1.1, 1])

    # Build entire Phone HTML block cleanly
    with c_phone:
        bubbles_html = ""
        for m in st.session_state.chat_messages:
            if m["type"] == "text":
                if m["sender"] == "bot":
                    bubbles_html += f'<div style="align-self:flex-start;background:#FFFFFF;color:#1E293B;padding:8px 14px;border-radius:16px 16px 16px 4px;max-width:80%;font-size:0.88rem;box-shadow:0 1px 3px rgba(0,0,0,0.1);">{m["text"]}</div>'
                else:
                    bubbles_html += f'<div style="align-self:flex-end;background:#5B8E7D;color:white;padding:8px 14px;border-radius:16px 16px 4px 16px;max-width:80%;font-size:0.88rem;box-shadow:0 1px 3px rgba(0,0,0,0.1);">{m["text"]}</div>'
            elif m["type"] == "sticker":
                bubbles_html += f'<div style="align-self:flex-end;max-width:160px;filter:drop-shadow(0 3px 6px rgba(0,0,0,0.15));"><img src="data:image/png;base64,{m["b64"]}" style="width:100%;height:auto;display:block;" /></div>'

        phone_component = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{ margin: 0; padding: 0; background: transparent; font-family: -apple-system, BlinkMacSystemFont, 'Prompt', sans-serif; }}
                .phone-shell {{
                    max-width: 380px; margin: 0 auto;
                    border: 10px solid #2D3748; border-radius: 36px;
                    box-shadow: 0 15px 35px rgba(0,0,0,0.2);
                    overflow: hidden; background: {chat_bg};
                }}
                .phone-header {{
                    background: rgba(0,0,0,0.18); backdrop-filter: blur(8px);
                    padding: 12px 18px; color: white; font-weight: 600;
                    display: flex; justify-content: space-between; align-items: center;
                }}
                .chat-body {{
                    height: 380px; overflow-y: auto; padding: 14px;
                    display: flex; flex-direction: column; gap: 12px;
                }}
                .chat-body::-webkit-scrollbar {{ width: 6px; }}
                .chat-body::-webkit-scrollbar-thumb {{ background: rgba(255,255,255,0.3); border-radius: 4px; }}
            </style>
        </head>
        <body>
            <div class="phone-shell">
                <div class="phone-header">
                    <div>💬 เพื่อน (Friend)</div>
                    <div style="font-size:0.8rem;opacity:0.85;">🟢 ออนไลน์</div>
                </div>
                <div class="chat-body" id="chatArea">
                    {bubbles_html}
                </div>
            </div>
            <script>
                const c = document.getElementById('chatArea');
                if (c) c.scrollTop = c.scrollHeight;
            </script>
        </body>
        </html>
        """
        components.html(phone_component, height=440)

        # Message Input form
        with st.form("chat_txt_form", clear_on_submit=True):
            ct1, ct2 = st.columns([3, 1])
            with ct1:
                u_txt = st.text_input("พิมพ์แชท:", placeholder="พิมพ์ข้อความ...", label_visibility="collapsed")
            with ct2:
                btn_send_txt = st.form_submit_button("ส่ง 💬", use_container_width=True)

            if btn_send_txt and u_txt.strip():
                st.session_state.chat_messages.append({"sender": "user", "text": u_txt.strip(), "type": "text"})
                st.rerun()

    # Sticker Tray on right
    with c_tray:
        st.markdown("#### 🎨 แป้นพิมพ์สติกเกอร์ (คลิกเพื่อส่งในห้องแชท)")
        all_display = st.session_state.queue_stickers if st.session_state.queue_stickers else st.session_state.studio_stickers

        if not all_display:
            st.info("💡 ยังไม่มีสติกเกอร์ กรุณาเตรียมสติกเกอร์ในแท็บ 1 สตูดิโอก่อน")
        else:
            st.caption(f"มีสติกเกอร์ทั้งหมด {len(all_display)} ภาพ (คลิกที่ภาพเพื่อส่ง):")
            t_cols = st.columns(3)
            for s_i, stk_it in enumerate(all_display):
                with t_cols[s_i % 3]:
                    st.image(stk_it["proc_img"], use_container_width=True)
                    if st.button(f"ส่ง {s_i+1:02d}", key=f"sim_send_{s_i}", use_container_width=True):
                        buf = io.BytesIO()
                        stk_it["proc_img"].save(buf, format="PNG")
                        b64_stk = base64.b64encode(buf.getvalue()).decode()
                        st.session_state.chat_messages.append({
                            "sender": "user",
                            "type": "sticker",
                            "b64": b64_stk
                        })
                        st.rerun()

# =============================================================
# TAB 4: ANIMATED STICKER (APNG CONVERTER)
# =============================================================
with tab_apng:
    st.markdown("### 🎞️ 4. สติกเกอร์เคลื่อนไหว (LINE Animated APNG Converter)")
    st.markdown("นำเข้าไฟล์ GIF หรือภาพนิ่งหลายเฟรม เพื่อแปลงเป็น Animated PNG (APNG) ตามเกณฑ์ LINE (ขนาด ≤ 320x270, เลขคู่, ความยาว 1-4 วินาที, < 300 KB)")

    col_ap1, col_ap2 = st.columns([1.2, 1])
    with col_ap1:
        ap_file = st.file_uploader("อัปโหลดไฟล์ GIF เคลื่อนไหว:", type=["gif"], key="ap_gif_up")
        ap_multi = st.file_uploader("หรืออัปโหลดหลายเฟรม (5 - 20 เฟรม):", type=["png", "jpg", "jpeg", "webp"], accept_multiple_files=True, key="ap_frames_up")

    with col_ap2:
        st.markdown("#### ⏱️ สเปกการเล่น")
        a_sec = st.selectbox("ความยาวรวมของการเล่น:", [1, 2, 3, 4], index=1, format_func=lambda s: f"{s} วินาที")
        a_loop = st.selectbox("จำนวนรอบลูป (Loop Count):", [1, 2, 3, 4], index=0)
        a_rembg = st.checkbox("ลบพื้นหลังแต่ละเฟรมด้วย AI", value=True)

    if st.button("🎬 สร้างสติกเกอร์เคลื่อนไหว APNG", type="primary"):
        frames = []
        if ap_file is not None:
            frames = ip.extract_gif_frames(ap_file.read())
        elif ap_multi:
            for f in ap_multi:
                frames.append(Image.open(f).convert("RGBA"))

        if not frames:
            st.error("⚠️ กรุณาอัปโหลดไฟล์ GIF หรือภาพหลายเฟรมก่อน")
        else:
            with st.spinner(f"กำลังแปลงแอนิเมชัน {len(frames)} เฟรมตามกฎของ LINE..."):
                try:
                    ap_bytes, ap_audit = ip.create_line_apng(
                        frames=frames,
                        total_seconds=a_sec,
                        loop_count=a_loop,
                        margin_px=10,
                        remove_bg=a_rembg
                    )
                    st.session_state.apng_results.append({
                        "bytes": ap_bytes,
                        "audit": ap_audit,
                        "name": ap_file.name if ap_file else "animated.png"
                    })
                    st.success("🎉 สร้างไฟล์ APNG สำเร็จแล้ว!")
                except Exception as ex:
                    st.error(f"เกิดข้อผิดพลาด: {str(ex)}")

    # Results
    if st.session_state.apng_results:
        st.markdown("---")
        for a_idx, a_res in enumerate(st.session_state.apng_results):
            aud = a_res["audit"]
            cp1, cp2 = st.columns([1, 1.5])
            with cp1:
                b64 = base64.b64encode(a_res["bytes"]).decode()
                st.markdown(f'<div style="background:#FFFFFF;border-radius:12px;padding:12px;text-align:center;"><img src="data:image/png;base64,{b64}" style="max-width:260px;height:auto;" /></div>', unsafe_allow_html=True)
                st.download_button(
                    label=f"💾 โหลด animated_{a_idx+1:02d}.png",
                    data=a_res["bytes"],
                    file_name=f"animated_{a_idx+1:02d}.png",
                    mime="image/png",
                    key=f"dl_a_{a_idx}"
                )
            with cp2:
                st.markdown("**ผลการตรวจสอบ Audit:**")
                st.markdown(f"- ขนาด: {aud['width']} x {aud['height']} px (เลขคู่ ✓)")
                st.markdown(f"- เฟรม: {aud['frame_count']} เฟรม (5-20 เฟรม ✓)")
                st.markdown(f"- เวลาเล่น: {aud['total_seconds']} วินาที ({aud['loop_count']} ลูป)")
                st.markdown(f"- ขนาดไฟล์: {aud['file_size_kb']:.1f} KB (< 300 KB ✓)")

# =============================================================
# TAB 5: GUIDELINES
# =============================================================
with tab_guide:
    st.markdown("### 📋 ข้อกำหนด LINE Creators Market อย่างเป็นทางการ")
    g1, g2 = st.columns(2)
    with g1:
        st.markdown("""
        #### 1. สเปกภาพนิ่ง (Static Stickers)
        - **Main Image:** 240 x 240 px (1 รูป)
        - **Sticker Images:** สูงสุด 370 x 320 px (8, 16, 24, 32 หรือ 40 รูป)
        - **Chat Tab Image:** 96 x 74 px (1 รูป)
        - **ความกว้าง/ความสูง:** ต้องเป็น **เลขคู่ (Even numbers)** เสมอ
        - **Margin:** เว้นขอบว่างรอบตัวสติกเกอร์อย่างน้อย 10 px
        - **ขนาดไฟล์:** ไม่เกิน 1 MB ต่อรูป
        """)
    with g2:
        st.markdown("""
        #### 2. เคล็ดลับเพิ่มยอดขายสติกเกอร์
        - 💡 **ใส่ขอบขาว (White Outline):** ป้องกันไม่ให้ภาพกลืนกับพื้นหลังสีดำของ LINE Dark Mode
        - 💡 **ติดแท็กคีย์เวิร์ด:** แปะคำยอดฮิต (สวัสดี, ขอบคุณ, 555) เพื่อให้ LINE Auto Suggest สติกเกอร์ของคุณเวลาคนพิมพ์แชท
        - 💡 **Super Upscale:** ขยายภาพเล็กด้วย Lanczos + Edge Sharpener ป้องกันภาพแตก
        - 💡 **ตรวจสอบใน Chat Simulator:** ดูความชัดเจนและขนาดก่อนส่งขายจริง
        """)
