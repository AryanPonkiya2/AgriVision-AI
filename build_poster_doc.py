"""
Build details1.docx replicating the AgriVision poster layout from the reference image.
Uses python-docx with table-based multi-column layout (landscape A3/A4 wide page).
"""

import os, io
from docx import Document
from docx.shared import Pt, RGBColor, Inches, Cm, Emu
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls, qn
from docx.oxml import OxmlElement
import copy

# ── colours (matching poster) ──────────────────────────────────────────────────
DK_GREEN   = "1B5E20"   # header dark green
MID_GREEN  = "2E7D32"   # section headers
LT_GREEN   = "E8F5E9"   # objective box bg
TEAL_GREEN = "004D40"   # footer / accent
GOLD       = "F9A825"
WHITE      = "FFFFFF"
ALMOST_WHT = "F5F5F5"

# ── image paths ────────────────────────────────────────────────────────────────
IMG_DIR = r"C:\Users\Isha\.gemini\antigravity-ide\brain\885ebdde-ce51-40f3-9622-c587cc4d9c8b"
I_HEALTHY_TOM  = os.path.join(IMG_DIR, "leaf_healthy_tomato_1789880496584.jpg")
I_BLIGHT_TOM   = os.path.join(IMG_DIR, "leaf_early_blight_tomato_1789880509055.jpg")
I_BLIGHT_POT   = os.path.join(IMG_DIR, "leaf_late_blight_potato_1789880522905.jpg")
I_HEALTHY_POT  = os.path.join(IMG_DIR, "leaf_healthy_potato_1789880593595.jpg")
I_SPOT_POT     = os.path.join(IMG_DIR, "leaf_spot_potato_1789880606260.jpg")
I_HEALTHY_PEP  = os.path.join(IMG_DIR, "leaf_healthy_pepper_1789880617679.jpg")

OUT = r"d:\AGUNI\AI-ML course\plant project\AgriVision playground\Professional UI\poster\details1.docx"

# ── helpers ────────────────────────────────────────────────────────────────────
def set_cell_bg(cell, hex_color):
    shd = parse_xml(
        f'<w:shd {nsdecls("w")} w:fill="{hex_color}" '
        f'w:color="auto" w:val="clear"/>'
    )
    cell._tc.get_or_add_tcPr().append(shd)

def set_cell_border(cell, top="1", bottom="1", left="1", right="1", color="CCCCCC"):
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()
    tcBorders = OxmlElement('w:tcBorders')
    for side, val in [("top", top), ("bottom", bottom), ("left", left), ("right", right)]:
        el = OxmlElement(f'w:{side}')
        el.set(qn('w:val'), 'single')
        el.set(qn('w:sz'), val)
        el.set(qn('w:space'), '0')
        el.set(qn('w:color'), color)
        tcBorders.append(el)
    tcPr.append(tcBorders)

def cell_para(cell, align=WD_ALIGN_PARAGRAPH.LEFT):
    p = cell.paragraphs[0]
    p.alignment = align
    return p

def add_run(para, text, bold=False, italic=False, size=9, color=None, font="Calibri"):
    r = para.add_run(text)
    r.bold = bold; r.italic = italic
    r.font.size = Pt(size); r.font.name = font
    if color:
        r.font.color.rgb = RGBColor.from_string(color)
    return r

def section_heading(para, text, size=10, color=DK_GREEN):
    r = para.add_run(text)
    r.bold = True; r.font.size = Pt(size)
    r.font.name = "Calibri"; r.font.color.rgb = RGBColor.from_string(color)
    return r

def add_bullet(para, text, bold_pre=None, size=8, indent=False):
    """Add a bullet-like line using • character (no list style needed)."""
    cell_para = para
    if bold_pre:
        rb = cell_para.add_run(f"• {bold_pre}")
        rb.bold = True; rb.font.size = Pt(size); rb.font.name = "Calibri"
    else:
        rb = cell_para.add_run(f"• {text}")
        rb.font.size = Pt(size); rb.font.name = "Calibri"

def new_para(cell):
    p = OxmlElement('w:p')
    cell._tc.append(p)
    from docx.text.paragraph import Paragraph
    return Paragraph(p, cell)

def img_para(cell, img_path, width_in=1.2, align=WD_ALIGN_PARAGRAPH.CENTER):
    p = cell.paragraphs[0]
    p.alignment = align
    r = p.add_run()
    r.add_picture(img_path, width=Inches(width_in))
    return p

def make_simple_table(doc_or_cell, headers, rows, col_widths, header_bg=MID_GREEN,
                       font_size=7.5):
    """Return a formatted mini table."""
    n_cols = len(headers)
    if hasattr(doc_or_cell, 'add_table'):
        tbl = doc_or_cell.add_table(rows=1 + len(rows), cols=n_cols)
    else:
        # nested table inside a cell
        tbl = doc_or_cell.add_table(rows=1 + len(rows), cols=n_cols)
    tbl.style = 'Table Grid'

    # header
    hdr = tbl.rows[0].cells
    for i, h in enumerate(headers):
        set_cell_bg(hdr[i], header_bg)
        p = hdr[i].paragraphs[0]
        r = p.add_run(h)
        r.bold = True; r.font.size = Pt(font_size)
        r.font.color.rgb = RGBColor.from_string(WHITE)
        r.font.name = "Calibri"
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER

    # data rows
    for ri, row_data in enumerate(rows):
        row = tbl.rows[ri + 1].cells
        bg = ALMOST_WHT if ri % 2 == 1 else WHITE
        for ci, val in enumerate(row_data):
            set_cell_bg(row[ci], bg)
            p = row[ci].paragraphs[0]
            is_highlighted = (ri == len(rows) - 1 and ci > 0)  # last row highlight
            r = p.add_run(str(val))
            r.font.size = Pt(font_size)
            r.font.name = "Calibri"
            if ci == 0:
                r.bold = True
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER if ci > 0 else WD_ALIGN_PARAGRAPH.LEFT

    # column widths
    for row in tbl.rows:
        for ci, cell in enumerate(row.cells):
            cell.width = Inches(col_widths[ci])
    return tbl

# ══════════════════════════════════════════════════════════════════════════════
#  DOCUMENT SETUP  (Landscape, narrow margins for wide poster look)
# ══════════════════════════════════════════════════════════════════════════════
doc = Document()
section = doc.sections[0]
section.page_width  = Inches(15)      # super-wide landscape
section.page_height = Inches(10.5)
section.top_margin    = Inches(0.25)
section.bottom_margin = Inches(0.25)
section.left_margin   = Inches(0.25)
section.right_margin  = Inches(0.25)

# ══════════════════════════════════════════════════════════════════════════════
#  HEADER ROW  (dark green bar: logo | tagline | farm image text)
# ══════════════════════════════════════════════════════════════════════════════
hdr_tbl = doc.add_table(rows=1, cols=3)
hdr_tbl.style = 'Table Grid'

# col widths
TOTAL_W = 14.5
C1, C2, C3 = 3.5, 7.0, 4.0
for i, w in enumerate([C1, C2, C3]):
    for cell in [hdr_tbl.rows[0].cells[i]]:
        cell.width = Inches(w)

# ── Header cell 1: Logo ──────────────────────────────────────────────────────
h1 = hdr_tbl.rows[0].cells[0]
set_cell_bg(h1, DK_GREEN)
h1.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
p = h1.paragraphs[0]
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p.add_run("🌿  AgriVision")
r.bold = True; r.font.size = Pt(26); r.font.name = "Calibri"
r.font.color.rgb = RGBColor.from_string(WHITE)

p2 = new_para(h1)
p2.alignment = WD_ALIGN_PARAGRAPH.CENTER
r2 = p2.add_run("Your Farmer Assistant")
r2.font.size = Pt(13); r2.font.name = "Calibri"; r2.italic = True
r2.font.color.rgb = RGBColor.from_string("A5D6A7")

# ── Header cell 2: Title ─────────────────────────────────────────────────────
h2 = hdr_tbl.rows[0].cells[1]
set_cell_bg(h2, "1B5E20")
h2.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
p = h2.paragraphs[0]
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p.add_run("AI-Powered Solutions for Crop Identification, Disease Detection,")
r.bold = True; r.font.size = Pt(16); r.font.name = "Calibri"
r.font.color.rgb = RGBColor.from_string(WHITE)
p2 = new_para(h2)
p2.alignment = WD_ALIGN_PARAGRAPH.CENTER
r2 = p2.add_run("and Real-Time Agricultural Insights")
r2.bold = True; r2.font.size = Pt(16); r2.font.name = "Calibri"
r2.font.color.rgb = RGBColor.from_string(WHITE)

# ── Header cell 3: Tagline ───────────────────────────────────────────────────
h3 = hdr_tbl.rows[0].cells[2]
set_cell_bg(h3, "2E7D32")
h3.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
for line in ["Healthier Crops", "Better Harvests", "A Greener Tomorrow"]:
    p = h3.paragraphs[0] if line == "Healthier Crops" else new_para(h3)
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run(line)
    r.bold = True; r.font.size = Pt(14); r.font.name = "Calibri"
    r.font.color.rgb = RGBColor.from_string("F1F8E9")

doc.add_paragraph().paragraph_format.space_after = Pt(4)

# ══════════════════════════════════════════════════════════════════════════════
#  MAIN 5-COLUMN BODY
# ══════════════════════════════════════════════════════════════════════════════
body = doc.add_table(rows=1, cols=5)
body.style = 'Table Grid'

# column widths
CW = [2.7, 2.8, 3.2, 3.2, 2.6]   # total ~14.5"
for i, w in enumerate(CW):
    body.rows[0].cells[i].width = Inches(w)

C = body.rows[0].cells   # shorthand

# helper: pad & colour every section cell
for ci in range(5):
    set_cell_bg(C[ci], WHITE)
    C[ci].vertical_alignment = WD_ALIGN_VERTICAL.TOP

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  COL 0  —  1. ABSTRACT
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
col0 = C[0]
set_cell_bg(col0, WHITE)

# Section label
p = col0.paragraphs[0]
set_cell_bg(col0, LT_GREEN)
p.alignment = WD_ALIGN_PARAGRAPH.LEFT
r = p.add_run("1.  ABSTRACT")
r.bold = True; r.font.size = Pt(11); r.font.name = "Calibri"
r.font.color.rgb = RGBColor.from_string(DK_GREEN)

# body
p1 = new_para(col0)
r = p1.add_run(
    "AgriVision is an AI-powered platform designed to assist Indian farmers in identifying "
    "crop diseases, providing crop information, and delivering real-time agricultural insights. "
    "The system uses image recognition and machine learning to detect plant diseases at an early "
    "stage, along with prevention and management suggestions. It also offers weather updates, "
    "market trends, and export intelligence to support better decision-making and increase farm "
    "productivity while reducing crop loss."
)
r.font.size = Pt(8); r.font.name = "Calibri"

# Objectives box
set_cell_bg(col0, LT_GREEN)
p_obj_h = new_para(col0)
r = p_obj_h.add_run("  OBJECTIVES")
r.bold = True; r.font.size = Pt(9.5); r.font.name = "Calibri"
r.font.color.rgb = RGBColor.from_string(DK_GREEN)

for obj in [
    "Accurate crop and disease identification",
    "Real-time weather updates",
    "Crop information & best practices",
    "Agricultural market & export insights",
    "Empower farmers with data-driven decisions",
]:
    p_b = new_para(col0)
    r = p_b.add_run(f"  ✓  {obj}")
    r.font.size = Pt(8); r.font.name = "Calibri"
    r.font.color.rgb = RGBColor.from_string("1B5E20")

# Leaf image as app screenshot stand-in
p_img = new_para(col0)
p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
try:
    run_img = p_img.add_run()
    run_img.add_picture(I_HEALTHY_TOM, width=Inches(2.3))
except Exception as e:
    p_img.add_run(f"[Image: {e}]")

p_cap = new_para(col0)
p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p_cap.add_run("Tomato Leaf Blight — View Solution")
r.font.size = Pt(7); r.italic = True; r.font.name = "Calibri"
r.font.color.rgb = RGBColor.from_string("555555")

# Why it matters
p_why = new_para(col0)
r = p_why.add_run("WHY IT MATTERS")
r.bold = True; r.font.size = Pt(9.5); r.font.name = "Calibri"
r.font.color.rgb = RGBColor.from_string(DK_GREEN)

p_why2 = new_para(col0)
r = p_why2.add_run(
    "Indian farmers face major challenges like early disease detection, lack of reliable "
    "information, and dependency on traditional methods. AgriVision bridges this gap with "
    "technology, making farming smarter, more productive and sustainable."
)
r.font.size = Pt(8); r.font.name = "Calibri"

# Footer tag
p_ft = new_para(col0)
set_cell_bg(col0, MID_GREEN)
r = p_ft.add_run("  Empowering Farmers with Technology  ")
r.bold = True; r.font.size = Pt(8.5); r.font.name = "Calibri"
r.font.color.rgb = RGBColor.from_string(WHITE)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  COL 1  —  2. MATERIALS & METHODS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
col1 = C[1]

p = col1.paragraphs[0]
set_cell_bg(col1, "E8F5E9")
r = p.add_run("2.  MATERIALS & METHODS")
r.bold = True; r.font.size = Pt(11); r.font.name = "Calibri"
r.font.color.rgb = RGBColor.from_string(DK_GREEN)

# 2.1 Dataset
p21 = new_para(col1)
r = p21.add_run("2.1  Dataset")
r.bold = True; r.font.size = Pt(9.5); r.font.name = "Calibri"
r.font.color.rgb = RGBColor.from_string(MID_GREEN)

p21b = new_para(col1)
r = p21b.add_run(
    "PlantVillage (open-source dataset) containing healthy and diseased leaf images of "
    "multiple crops (tomato, potato, etc.)."
)
r.font.size = Pt(8); r.font.name = "Calibri"

# Dataset table — nested
ds_headers = ["Crop", "Healthy", "Diseased", "Total"]
ds_rows = [
    ("Tomato", "1,000", "1,000", "2,000"),
    ("Potato", "800",   "800",   "1,600"),
    ("Others", "600",   "600",   "1,200"),
    ("Total",  "2,400", "2,400", "4,800"),
]
ds_tbl = col1.add_table(rows=1 + len(ds_rows), cols=4)
ds_tbl.style = 'Table Grid'
hdr_cells = ds_tbl.rows[0].cells
for i, h in enumerate(ds_headers):
    set_cell_bg(hdr_cells[i], MID_GREEN)
    p = hdr_cells[i].paragraphs[0]
    r = p.add_run(h); r.bold = True; r.font.size = Pt(7.5)
    r.font.color.rgb = RGBColor.from_string(WHITE); r.font.name = "Calibri"
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
for ri, rd in enumerate(ds_rows):
    rc = ds_tbl.rows[ri+1].cells
    bg = "F1F8E9" if ri % 2 == 0 else WHITE
    if ri == len(ds_rows) - 1:
        bg = "C8E6C9"
    for ci, v in enumerate(rd):
        set_cell_bg(rc[ci], bg)
        p = rc[ci].paragraphs[0]; r = p.add_run(v)
        r.font.size = Pt(7.5); r.font.name = "Calibri"
        if ri == len(ds_rows)-1: r.bold = True
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER if ci > 0 else WD_ALIGN_PARAGRAPH.LEFT

# 2.2 Preprocessing
p22 = new_para(col1)
r = p22.add_run("2.2  Preprocessing")
r.bold = True; r.font.size = Pt(9.5); r.font.name = "Calibri"
r.font.color.rgb = RGBColor.from_string(MID_GREEN)
for item in [
    "Image resizing (224 x 224)",
    "Normalization",
    "Data augmentation (rotation, flip, zoom)",
    "Train / Validation / Test split (70:15:15)",
]:
    p = new_para(col1); r = p.add_run(f"• {item}")
    r.font.size = Pt(8); r.font.name = "Calibri"

# 2.3 Model & Techniques
p23 = new_para(col1)
r = p23.add_run("2.3  Model & Techniques")
r.bold = True; r.font.size = Pt(9.5); r.font.name = "Calibri"
r.font.color.rgb = RGBColor.from_string(MID_GREEN)
for item in [
    "Convolutional Neural Network (CNN)",
    "Transfer Learning (ResNet / EfficientNet)",
    "Adam optimizer",
    "Categorical Cross-Entropy loss",
]:
    p = new_para(col1); r = p.add_run(f"• {item}")
    r.font.size = Pt(8); r.font.name = "Calibri"

# 2.4 System Architecture (text diagram)
p24 = new_para(col1)
r = p24.add_run("2.4  System Architecture")
r.bold = True; r.font.size = Pt(9.5); r.font.name = "Calibri"
r.font.color.rgb = RGBColor.from_string(MID_GREEN)

arch_tbl = col1.add_table(rows=3, cols=4)
arch_tbl.style = 'Table Grid'
arch_labels = [
    ("Input\nImage", "Preprocessing", "CNN\nModel", "Prediction\n(Disease/\nHealthy)"),
    ("▼", "▼", "▼", "▼"),
    ("Crop Info", "Weather", "Market\n& Export", ""),
]
arch_bgs = [
    [MID_GREEN, "558B2F", DK_GREEN, "1B5E20"],
    [WHITE, WHITE, WHITE, WHITE],
    ["81C784", "66BB6A", "4CAF50", WHITE],
]
for ri, row_labels in enumerate(arch_labels):
    for ci, label in enumerate(row_labels):
        cell = arch_tbl.rows[ri].cells[ci]
        set_cell_bg(cell, arch_bgs[ri][ci])
        p = cell.paragraphs[0]; p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(label)
        r.font.size = Pt(7); r.font.name = "Calibri"; r.bold = (ri == 0)
        if ri == 0:
            r.font.color.rgb = RGBColor.from_string(WHITE)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  COL 2  —  3. RESULTS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
col2 = C[2]

p = col2.paragraphs[0]
set_cell_bg(col2, "E8F5E9")
r = p.add_run("3.  RESULTS")
r.bold = True; r.font.size = Pt(11); r.font.name = "Calibri"
r.font.color.rgb = RGBColor.from_string(DK_GREEN)

# 3.1 Performance Table
p31 = new_para(col2)
r = p31.add_run("3.1  Disease Detection Performance")
r.bold = True; r.font.size = Pt(9.5); r.font.name = "Calibri"
r.font.color.rgb = RGBColor.from_string(MID_GREEN)

perf_h = ["Model", "Accuracy", "Precision", "Recall", "F1-Score"]
perf_rows = [
    ("VGG16",        "92.4%", "91.8%", "90.7%", "91.2%"),
    ("ResNet50",     "95.7%", "95.1%", "94.8%", "94.9%"),
    ("EfficientNet", "96.8%", "96.5%", "96.1%", "96.3%"),
]
pt = col2.add_table(rows=1 + len(perf_rows), cols=5)
pt.style = 'Table Grid'
for i, h in enumerate(perf_h):
    set_cell_bg(pt.rows[0].cells[i], MID_GREEN)
    p = pt.rows[0].cells[i].paragraphs[0]
    r = p.add_run(h); r.bold = True; r.font.size = Pt(7.5)
    r.font.color.rgb = RGBColor.from_string(WHITE); r.font.name = "Calibri"
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
for ri, rd in enumerate(perf_rows):
    rc = pt.rows[ri+1].cells
    bg = "E8F5E9" if ri == 2 else (WHITE if ri % 2 == 0 else "F5F5F5")
    for ci, v in enumerate(rd):
        set_cell_bg(rc[ci], bg)
        p = rc[ci].paragraphs[0]; r = p.add_run(v)
        r.font.size = Pt(7.5); r.font.name = "Calibri"
        if ri == 2: r.bold = True
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER if ci > 0 else WD_ALIGN_PARAGRAPH.LEFT

# 3.2 Sample Predictions — 6 leaf images in 2 rows x 3 cols
p32 = new_para(col2)
r = p32.add_run("3.2  Sample Predictions")
r.bold = True; r.font.size = Pt(9.5); r.font.name = "Calibri"
r.font.color.rgb = RGBColor.from_string(MID_GREEN)

leaf_imgs = [
    (I_HEALTHY_TOM, "Healthy (Tomato)"),
    (I_BLIGHT_TOM,  "Early Blight (Tomato)"),
    (I_BLIGHT_POT,  "Late Blight (Potato)"),
    (I_HEALTHY_POT, "Healthy (Potato)"),
    (I_SPOT_POT,    "Leaf Spot (Potato)"),
    (I_HEALTHY_PEP, "Healthy (Pepper)"),
]

leaf_tbl = col2.add_table(rows=4, cols=3)  # row 0+1: images row1, row 2+3: images row2
leaf_tbl.style = 'Table Grid'
img_w = 0.9
for col_i in range(3):
    for row_batch in range(2):
        idx = row_batch * 3 + col_i
        img_row  = row_batch * 2
        cap_row  = row_batch * 2 + 1
        img_path, caption = leaf_imgs[idx]

        img_cell = leaf_tbl.rows[img_row].cells[col_i]
        p = img_cell.paragraphs[0]; p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        try:
            run = p.add_run(); run.add_picture(img_path, width=Inches(img_w))
        except:
            p.add_run("[img]")

        cap_cell = leaf_tbl.rows[cap_row].cells[col_i]
        set_cell_bg(cap_cell, "F1F8E9")
        pc = cap_cell.paragraphs[0]; pc.alignment = WD_ALIGN_PARAGRAPH.CENTER
        rc = pc.add_run(caption)
        rc.font.size = Pt(7); rc.font.name = "Calibri"; rc.italic = True

# 3.3 Weather & Market Insights
p33 = new_para(col2)
r = p33.add_run("3.3  Weather & Market Insights (Example)")
r.bold = True; r.font.size = Pt(9.5); r.font.name = "Calibri"
r.font.color.rgb = RGBColor.from_string(MID_GREEN)

wm_tbl = col2.add_table(rows=1, cols=2)
wm_tbl.style = 'Table Grid'

# Left: weather
wl = wm_tbl.rows[0].cells[0]
set_cell_bg(wl, "E3F2FD")
pw = wl.paragraphs[0]
r = pw.add_run("Weather Forecast (Maharashtra)\n")
r.bold = True; r.font.size = Pt(7.5); r.font.name = "Calibri"
r.font.color.rgb = RGBColor.from_string("0D47A1")
for line in ["28°C  Partly Cloudy", "Humidity: 72%   Wind: 12 km/h",
             "Mon  Tue  Wed  Thu  Fri", "27°   28°   29°   28°   27°"]:
    r2 = pw.add_run(f"\n{line}")
    r2.font.size = Pt(7); r2.font.name = "Calibri"

# Right: market price
wr = wm_tbl.rows[0].cells[1]
set_cell_bg(wr, "FFF8E1")
pm = wr.paragraphs[0]
r = pm.add_run("Market Price (Today)\n")
r.bold = True; r.font.size = Pt(7.5); r.font.name = "Calibri"
r.font.color.rgb = RGBColor.from_string("E65100")
for item, arrow, pct in [("Tomato  Rs18/kg", "▲", "5%"),
                          ("Potato   Rs16/kg", "▲", "3%"),
                          ("Onion    Rs22/kg", "▼", "2%")]:
    r2 = pm.add_run(f"\n{item}  {arrow} {pct}")
    r2.font.size = Pt(7.5); r2.font.name = "Calibri"
    r2.font.color.rgb = RGBColor.from_string("2E7D32" if arrow == "▲" else "C62828")

# Export insights
p_exp = new_para(col2)
set_cell_bg(col2, "F1F8E9")
r = p_exp.add_run("Export Insights — Top Destinations: UAE, Bangladesh, Nepal")
r.font.size = Pt(7.5); r.font.name = "Calibri"; r.bold = True
r.font.color.rgb = RGBColor.from_string(DK_GREEN)
p_exp2 = new_para(col2)
r = p_exp2.add_run("Major Export Crops: Basmati Rice, Mango, Spices")
r.font.size = Pt(7.5); r.font.name = "Calibri"

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  COL 3  —  4. RESULTS (CONT.)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
col3 = C[3]

p = col3.paragraphs[0]
set_cell_bg(col3, "E8F5E9")
r = p.add_run("4.  RESULTS (CONT.)")
r.bold = True; r.font.size = Pt(11); r.font.name = "Calibri"
r.font.color.rgb = RGBColor.from_string(DK_GREEN)

# 4.1 Agricultural Analytics
p41 = new_para(col3)
r = p41.add_run("4.1  Agricultural Analytics")
r.bold = True; r.font.size = Pt(9.5); r.font.name = "Calibri"
r.font.color.rgb = RGBColor.from_string(MID_GREEN)

p41s = new_para(col3)
r = p41s.add_run("Top Crop Producing Regions (India)")
r.bold = True; r.font.size = Pt(8.5); r.font.name = "Calibri"

# Simple bar chart text representation
bar_data = [("Rice", 80), ("Wheat", 65), ("Maize", 38), ("Sugarcane", 34), ("Cotton", 28)]
bar_tbl = col3.add_table(rows=len(bar_data) + 1, cols=2)
bar_tbl.style = 'Table Grid'
for i, (crop, val) in enumerate(bar_data):
    rc = bar_tbl.rows[i+1].cells
    set_cell_bg(rc[0], WHITE)
    p = rc[0].paragraphs[0]; r = p.add_run(crop)
    r.font.size = Pt(7.5); r.font.name = "Calibri"; r.bold = True

    # Draw a simple bar using background colour
    set_cell_bg(rc[1], "43A047")
    rc[1].width = Inches(val / 80 * 1.5)
    p2 = rc[1].paragraphs[0]; r2 = p2.add_run(f" {val}M T")
    r2.font.size = Pt(7); r2.font.name = "Calibri"
    r2.font.color.rgb = RGBColor.from_string(WHITE)

# Header for bar table
h_bar = bar_tbl.rows[0].cells
set_cell_bg(h_bar[0], MID_GREEN); set_cell_bg(h_bar[1], MID_GREEN)
p = h_bar[0].paragraphs[0]; r = p.add_run("Crop")
r.bold = True; r.font.size = Pt(7.5); r.font.color.rgb = RGBColor.from_string(WHITE); r.font.name = "Calibri"
p2 = h_bar[1].paragraphs[0]; r2 = p2.add_run("Production (Million Tonnes)")
r2.bold = True; r2.font.size = Pt(7.5); r2.font.color.rgb = RGBColor.from_string(WHITE); r2.font.name = "Calibri"

# State-wise Export table
p41e = new_para(col3)
r = p41e.add_run("State-wise Export Contribution")
r.bold = True; r.font.size = Pt(8.5); r.font.name = "Calibri"

exp_rows = [
    ("Maharashtra", "22.5%"),
    ("Tamil Nadu",  "15.4%"),
    ("Karnataka",   "12.8%"),
    ("Gujarat",     "10.6%"),
    ("Others",      "38.7%"),
]
exp_tbl = col3.add_table(rows=1 + len(exp_rows), cols=2)
exp_tbl.style = 'Table Grid'
for i, h in enumerate(["State", "Contribution (%)"]):
    set_cell_bg(exp_tbl.rows[0].cells[i], MID_GREEN)
    p = exp_tbl.rows[0].cells[i].paragraphs[0]
    r = p.add_run(h); r.bold = True; r.font.size = Pt(7.5)
    r.font.color.rgb = RGBColor.from_string(WHITE); r.font.name = "Calibri"
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
for ri, (state, pct) in enumerate(exp_rows):
    rc = exp_tbl.rows[ri+1].cells
    bg = "F1F8E9" if ri % 2 == 0 else WHITE
    set_cell_bg(rc[0], bg); set_cell_bg(rc[1], bg)
    p0 = rc[0].paragraphs[0]; r0 = p0.add_run(state)
    r0.font.size = Pt(7.5); r0.font.name = "Calibri"
    p1 = rc[1].paragraphs[0]; r1 = p1.add_run(pct)
    r1.font.size = Pt(7.5); r1.font.name = "Calibri"
    p1.alignment = WD_ALIGN_PARAGRAPH.CENTER

# 4.2 Model Performance (Loss Curve) — text representation
p42 = new_para(col3)
r = p42.add_run("4.2  Model Performance (Loss Curve)")
r.bold = True; r.font.size = Pt(9.5); r.font.name = "Calibri"
r.font.color.rgb = RGBColor.from_string(MID_GREEN)

loss_tbl = col3.add_table(rows=6, cols=4)
loss_tbl.style = 'Table Grid'
for i, h in enumerate(["Epoch", "0", "10", "50"]):
    set_cell_bg(loss_tbl.rows[0].cells[i], MID_GREEN)
    p = loss_tbl.rows[0].cells[i].paragraphs[0]
    r = p.add_run(h); r.bold = True; r.font.size = Pt(7)
    r.font.color.rgb = RGBColor.from_string(WHITE); r.font.name = "Calibri"
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER

rows_loss = [
    ("Train Loss",  "2.0", "0.8", "0.2"),
    ("Val Loss",    "2.1", "1.0", "0.3"),
    ("Train Acc",   "0.3", "0.78","0.97"),
    ("Val Acc",     "0.28","0.74","0.96"),
    ("F1 (macro)",  "--",  "0.72","0.965"),
]
for ri, rd in enumerate(rows_loss):
    rc = loss_tbl.rows[ri+1].cells
    bg = "F1F8E9" if ri % 2 == 0 else WHITE
    for ci, v in enumerate(rd):
        set_cell_bg(rc[ci], bg)
        p = rc[ci].paragraphs[0]; r = p.add_run(v)
        r.font.size = Pt(7); r.font.name = "Calibri"
        if ci == 0: r.bold = True
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER if ci > 0 else WD_ALIGN_PARAGRAPH.LEFT

# 4.3 Key Findings
p43 = new_para(col3)
r = p43.add_run("4.3  Key Findings")
r.bold = True; r.font.size = Pt(9.5); r.font.name = "Calibri"
r.font.color.rgb = RGBColor.from_string(MID_GREEN)
for finding in [
    "ResNet50 gave the best balance of accuracy and generalization.",
    "Early disease detection reduces crop loss by up to 40%.",
    "Weather and market insights improve farmer decision-making.",
    "The system is scalable for multiple crops and regions.",
]:
    pf = new_para(col3)
    r = pf.add_run(f"✓  {finding}")
    r.font.size = Pt(8); r.font.name = "Calibri"
    r.font.color.rgb = RGBColor.from_string("1B5E20")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  COL 4  —  5. CONCLUSION
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
col4 = C[4]

p = col4.paragraphs[0]
set_cell_bg(col4, "E8F5E9")
r = p.add_run("5.  CONCLUSION")
r.bold = True; r.font.size = Pt(11); r.font.name = "Calibri"
r.font.color.rgb = RGBColor.from_string(DK_GREEN)

p_conc = new_para(col4)
r = p_conc.add_run(
    "AgriVision successfully demonstrates the potential of AI and data-driven insights in "
    "transforming Indian agriculture. By combining crop and disease detection, real-time "
    "weather updates, and market intelligence, the platform helps farmers make informed "
    "decisions, reduce crop loss, and increase productivity."
)
r.font.size = Pt(8); r.font.name = "Calibri"

# Tech tagline box
p_tag = new_para(col4)
set_cell_bg(col4, "C8E6C9")
r = p_tag.add_run("\n  Technology + Agriculture\n  = A Sustainable Future\n")
r.bold = True; r.italic = True; r.font.size = Pt(10); r.font.name = "Calibri"
r.font.color.rgb = RGBColor.from_string(DK_GREEN)

# Future Work
p_fw = new_para(col4)
r = p_fw.add_run("Future Work")
r.bold = True; r.font.size = Pt(9.5); r.font.name = "Calibri"
r.font.color.rgb = RGBColor.from_string(MID_GREEN)
for fw in [
    "Expand dataset for more crops and regions.",
    "Integrate real-time satellite data.",
    "Improve mobile app performance.",
    "Add voice support for farmers.",
]:
    pf = new_para(col4)
    r = pf.add_run(f"• {fw}")
    r.font.size = Pt(8); r.font.name = "Calibri"

# References
p_ref = new_para(col4)
set_cell_bg(col4, MID_GREEN)
r = p_ref.add_run("  REFERENCES")
r.bold = True; r.font.size = Pt(9.5); r.font.name = "Calibri"
r.font.color.rgb = RGBColor.from_string(WHITE)

refs = [
    "1. PlantVillage Dataset - Kaggle (https://www.kaggle.com/datasets/).",
    "2. He et al. (2016). Deep Residual Learning for Image Recognition. CVPR.",
    "3. Tan & Le (2019). EfficientNet: Rethinking Model Scaling. ICML.",
    "4. FAO. The State of Food and Agriculture 2023.",
    "5. IMD. India Meteorological Department.",
    "6. APEDA. Agricultural & Processed Food Products Export Development Authority.",
]
for ref in refs:
    pr = new_para(col4)
    r = pr.add_run(ref)
    r.font.size = Pt(7); r.font.name = "Calibri"
    r.font.color.rgb = RGBColor.from_string("333333")

# Contact
p_ct = new_para(col4)
set_cell_bg(col4, MID_GREEN)
r = p_ct.add_run("  CONTACT")
r.bold = True; r.font.size = Pt(9.5); r.font.name = "Calibri"
r.font.color.rgb = RGBColor.from_string(WHITE)

for line in [
    "  yourname@example.com",
    "  [Your College / University Name], India",
    "  https://github.com/AgriVision",
]:
    pc = new_para(col4)
    r = pc.add_run(line)
    r.font.size = Pt(8); r.font.name = "Calibri"

# ══════════════════════════════════════════════════════════════════════════════
#  FOOTER ROW
# ══════════════════════════════════════════════════════════════════════════════
doc.add_paragraph().paragraph_format.space_after = Pt(2)

ftr_tbl = doc.add_table(rows=1, cols=3)
ftr_tbl.style = 'Table Grid'
for cell in ftr_tbl.rows[0].cells:
    set_cell_bg(cell, DK_GREEN)
    cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER

fl = ftr_tbl.rows[0].cells[0]
p = fl.paragraphs[0]; p.alignment = WD_ALIGN_PARAGRAPH.LEFT
r = p.add_run("  🌿  AgriVision   |   Your Farmer Assistant")
r.bold = True; r.font.size = Pt(10); r.font.name = "Calibri"
r.font.color.rgb = RGBColor.from_string(WHITE)

fm = ftr_tbl.rows[0].cells[1]
p = fm.paragraphs[0]; p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p.add_run("Research Conclave — Poster Presentation  |  AI & Agricultural Track")
r.font.size = Pt(8.5); r.font.name = "Calibri"
r.font.color.rgb = RGBColor.from_string("A5D6A7")

fr_cell = ftr_tbl.rows[0].cells[2]
p = fr_cell.paragraphs[0]; p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
r = p.add_run("Smart Farming  |  Better Yields  |  Greener Tomorrow  ")
r.bold = True; r.font.size = Pt(9.5); r.font.name = "Calibri"
r.font.color.rgb = RGBColor.from_string(GOLD)

# ══════════════════════════════════════════════════════════════════════════════
#  SAVE
# ══════════════════════════════════════════════════════════════════════════════
doc.save(OUT)
print("Saved:", OUT)
