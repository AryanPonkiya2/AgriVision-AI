import os
import time
import docx
from docx import Document
from docx.shared import Pt, RGBColor, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls

def set_cell_shading(cell, color):
    shading_elm = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{color}"/>')
    cell._tc.get_or_add_tcPr().append(shading_elm)

def create_report():
    doc = Document()
    
    # Page setup - 1 inch margins
    sections = doc.sections
    for section in sections:
        section.top_margin = Inches(1)
        section.bottom_margin = Inches(1)
        section.left_margin = Inches(1)
        section.right_margin = Inches(1)

    # Styles Setup
    style_normal = doc.styles['Normal']
    font = style_normal.font
    font.name = 'Calibri'
    font.size = Pt(11)
    font.color.rgb = RGBColor(0x33, 0x33, 0x33)

    # Color constants
    COLOR_PRIMARY = RGBColor(0x1B, 0x4D, 0x22)    # Dark Green
    COLOR_SECONDARY = RGBColor(0x10, 0xB9, 0x81)  # Mint Green
    COLOR_ACCENT = RGBColor(0xF5, 0x9E, 0x0B)     # Amber/Gold
    COLOR_MUTED = RGBColor(0x77, 0x77, 0x77)      # Gray

    # --- Title Page Header ---
    title_p = doc.add_paragraph()
    title_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    title_p.paragraph_format.space_before = Pt(40)
    title_p.paragraph_format.space_after = Pt(10)
    title_run = title_p.add_run("AGRIVISION AI")
    title_run.font.size = Pt(28)
    title_run.font.bold = True
    title_run.font.color.rgb = COLOR_PRIMARY

    sub_p = doc.add_paragraph()
    sub_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    sub_p.paragraph_format.space_after = Pt(30)
    sub_run = sub_p.add_run("Advanced Plant Disease Detection & Agricultural Market Intelligence Portal")
    sub_run.font.size = Pt(14)
    sub_run.font.italic = True
    sub_run.font.color.rgb = COLOR_SECONDARY

    meta_p = doc.add_paragraph()
    meta_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    meta_p.paragraph_format.space_after = Pt(50)
    meta_run = meta_p.add_run("Project Implementation & Architecture Report\nDate: July 20, 2026\nSystem Version: v2.0.0")
    meta_run.font.size = Pt(11)
    meta_run.font.color.rgb = COLOR_MUTED

    # Horizontal Divider Line
    divider_p = doc.add_paragraph()
    divider_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    divider_p.paragraph_format.space_after = Pt(20)
    divider_run = divider_p.add_run("—" * 40)
    divider_run.font.color.rgb = COLOR_SECONDARY

    # Add Heading Helper
    def add_section_heading(text, level=1):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(18)
        p.paragraph_format.space_after = Pt(6)
        p.paragraph_format.keep_with_next = True
        
        run = p.add_run(text)
        run.font.bold = True
        if level == 1:
            run.font.size = Pt(18)
            run.font.color.rgb = COLOR_PRIMARY
            p.paragraph_format.space_after = Pt(8)
        elif level == 2:
            run.font.size = Pt(14)
            run.font.color.rgb = COLOR_SECONDARY
        else:
            run.font.size = Pt(12)
            run.font.bold = True
        return p

    # --- Section 1: Objective ---
    add_section_heading("1. Project Objective", level=1)
    
    p = doc.add_paragraph(
        "AgriVision AI is an end-to-end full-stack web application designed to empower modern farmers, "
        "agricultural experts, and home gardeners with high-fidelity, real-time decision-support tools. "
        "The project integrates deep learning plant pathology diagnostics, localized market pricing analysis, "
        "weather-based cultivation insights, and international crop trade metrics into a single cohesive interface."
    )
    p.paragraph_format.space_after = Pt(10)
    
    p = doc.add_paragraph("The primary objectives of the AgriVision AI project include:")
    p.paragraph_format.space_after = Pt(6)
    
    bullet1 = doc.add_paragraph(style='List Bullet')
    r = bullet1.add_run("Deploy Advanced Cloud AI for Disease Classification: ")
    r.font.bold = True
    bullet1.add_run("Integrate the robust Plant.id API v3 to identify 38+ plant and fruit diseases with up to 95%+ accuracy in under 5 seconds, offloading on-device computational loads and ensuring state-of-the-art diagnostic capabilities.")
    
    bullet2 = doc.add_paragraph(style='List Bullet')
    r = bullet2.add_run("Analyze Localized Market Trends: ")
    r.font.bold = True
    bullet2.add_run("Provide real-time market data directly from government endpoints (data.gov.in API) to eliminate middleman exploitation, ensuring farmers have access to fair regional commodity prices and daily volume trends.")
    
    bullet3 = doc.add_paragraph(style='List Bullet')
    r = bullet3.add_run("Enable Geospatial Agricultural Intelligence: ")
    r.font.bold = True
    bullet3.add_run("Implement interactive SVG-based maps of India mapping crop profiles, sowing/harvesting calendars, and irrigation guidelines across individual states.")
    
    bullet4 = doc.add_paragraph(style='List Bullet')
    r = bullet4.add_run("Integrate Export-Driven Cultivation Support: ")
    r.font.bold = True
    bullet4.add_run("Guide high-value farming operations by highlighting export-oriented crops, target importing nations, and regional export volume shares.")

    # --- Section 2: How It Works ---
    add_section_heading("2. How It Works", level=1)
    
    p = doc.add_paragraph(
        "AgriVision AI leverages a modular client-server architecture built on top of the Flask micro-framework, "
        "utilizing deep learning APIs for cloud-based diagnostic processing, and asynchronous client-side scripting "
        "for rich, interactive visualizations. Below is a detailed breakdown of the internal mechanism:"
    )
    p.paragraph_format.space_after = Pt(10)

    add_section_heading("2.1 Frontend User Interface & Layout", level=2)
    p = doc.add_paragraph(
        "The interface relies on clean, premium glassmorphism layouts styled with custom vanilla CSS and custom "
        "web typography (Outfit for headers, Space Grotesk for interactive values). Interactive SVG maps of India "
        "are loaded directly into the DOM (on map, weather, and export dashboards). The maps are programmed with "
        "CSS custom transitions and JavaScript event handlers that detect mouse clicks on individual state paths, "
        "highlighting the selected state with glowing box shadows and triggering immediate side-panel updates."
    )
    p.paragraph_format.space_after = Pt(10)

    add_section_heading("2.2 Flask Backend Routing & Data Orchestration", level=2)
    p = doc.add_paragraph(
        "The file app.py handles core routing, request processing, and data rendering. When a user uploads a leaf or "
        "fruit image via the '/upload' form, the server generates a unique UUID filename to prevent namespace collisions, "
        "saves the file locally in static/uploads, and triggers the prediction pipeline. The application also hosts "
        "an endpoint '/api/crop-prices' that acts as an API gateway for real-time market rates."
    )
    p.paragraph_format.space_after = Pt(10)

    add_section_heading("2.3 Deep Learning Diagnostic Pipeline & Key Discrepancy", level=2)
    p = doc.add_paragraph(
        "Architectural Note: During the project's research phase, a local transfer learning model using MobileNetV2 was trained "
        "on the Kaggle 'New Plant Diseases Dataset' (which contains 87,000+ annotated leaf images) and saved as mobilenetv2_best.keras. "
        "However, to ensure high generalization across diverse environmental conditions, broad coverage of fruit and plant species, "
        "and low server-side resource footprint in production, the active Flask web application runs queries by calling the external Plant.id API v3."
    )
    p.paragraph_format.space_after = Pt(10)

    p = doc.add_paragraph(
        "1. Image Processing & Encoding: The uploaded image is saved, and its binary content is encoded into a Base64 ASCII string inside api_client.py.\n"
        "2. Plant.id API Gateway: The Base64 representation is wrapped in a secure payload and transmitted via a POST request to the Plant.id API endpoint (https://api.plant.id/v3/identification) using a secret API key. The API returns details on plant species, disease diagnosis, confidence scoring, causes, preventions, and treatments.\n"
        "3. Confidence Thresholding: To filter out false alarms on healthy vegetation, the backend applies a 10% (0.10) threshold to the top disease prediction probability. If the probability is below this threshold or the engine signals the plant is healthy, the system returns a 'Healthy' status.\n"
        "4. local Fallback Rules: If the external API is unreachable or returns empty strings for treatment guidance, the backend executes a local keyword-matching algorithm (get_disease_info()). It scans the disease label for keywords (such as 'rot', 'blight', 'spot', 'mildew', or 'virus') and pulls matching causes, preventions, and treatments from a pre-defined dictionary database in app.py."
    )
    p.paragraph_format.space_after = Pt(10)

    add_section_heading("2.4 Real-time APMC Price API & Deterministic Hashing", level=2)
    p = doc.add_paragraph(
        "To fetch actual APMC commodity prices, the Flask server queries data.gov.in APIs, filtering records by state. "
        "If the live API fails, the application switches to a local deterministic fallback engine: get_seeded_market_data(). "
        "The system hashes a seed composed of the state name, crop name, and current date (e.g., 'Gujarat_Cotton_2026-07-20') using MD5. "
        "The resulting hash integer is used mathematically to generate stable daily pricing (within a natural +/- 5% variance of baseline prices), "
        "trend percentages (+/- 2.5%), trend directions (represented by neon green triangle ▲ or neon red ▼), and daily trade volumes. "
        "This ensures that even when offline, the application displays stable, consistent, and logical market indicators to the user."
    )
    p.paragraph_format.space_after = Pt(10)

    # --- Section 3: What It Does ---
    add_section_heading("3. What It Does", level=1)
    
    p = doc.add_paragraph(
        "AgriVision AI is structured as a comprehensive portal that provides farmers with a full suite "
        "of diagnostic and decision-making capabilities:"
    )
    p.paragraph_format.space_after = Pt(10)

    bullet_features = [
        ("AI Plant Pathology Diagnostics: ", "Identifies 38 separate disease categories (such as Cedar Apple Rust, Early Blight, Late Blight, Common Rust, Leaf Mold, Spider Mites, Mosaic Virus, and Leaf Curl) across 14 major crop and fruit species (Apple, Blueberry, Cherry, Corn, Grape, Orange, Peach, Pepper, Potato, Raspberry, Soybean, Squash, Strawberry, Tomato)."),
        ("Structured Treatment Plans: ", "Splits diagnosis output into three clear, action-oriented categories: Causes (how the pathogen spreads), Prevention (horticultural sanitation, spacing, base-watering), and Treatments (organic remedies, biological controls, and chemical fungicides)."),
        ("Live APMC Price Indicators: ", "Displays regional mandi pricing, daily volumes, and trend metrics for core commodities in individual Indian states."),
        ("Interactive Crop Profiles: ", "Maps major local crop varieties, their sowing/harvest calendars, and district-level distribution grids directly onto an interactive map visual of India."),
        ("National Export Dashboard: ", "Maintains an active directory ranking the top 10 agricultural exports of India, their primary importing trade partners, and category export volume shares (e.g., Rice to Saudi Arabia at 18%, Cotton to Bangladesh at 35%, Mangoes to UAE at 55%)."),
        ("Weather Map Dashboard: ", "Correlates weather conditions with regional crop profiles, giving warning indicators for conditions that might trigger fungal or bacterial disease outbreaks (e.g., high humidity combined with moderate heat).")
    ]
    
    for title, desc in bullet_features:
        bp = doc.add_paragraph(style='List Bullet')
        r = bp.add_run(title)
        r.font.bold = True
        bp.add_run(desc)

    # --- Section 4: How to Use ---
    add_section_heading("4. How to Use", level=1)
    
    p = doc.add_paragraph("AgriVision AI features an intuitive user flow designed for ease of use:")
    p.paragraph_format.space_after = Pt(10)

    steps = [
        ("1. Navigate to the Homepage: ", "Access the base URL (/). Explore the stats counter and review the general overview of supported plant species."),
        ("2. Open the Diagnose Portal: ", "Click 'Diagnose' in the navigation bar. Choose between scanning a 'Plant Leaf' or 'Fruit' to optimize backend parameters. Click the upload field, choose an image (e.g., one from test/test/), and click 'Diagnose'."),
        ("3. Review the Diagnosis Dashboard: ", "Read the classification results, confidence score gauge, disease cause description, preventive actions, and treatment guidelines. Click 'Analyze New Subject' to clear the form and repeat."),
        ("4. Explore the Crop Map: ", "Select 'Crop Map' from the navigation links. Click on states (such as Gujarat, Maharashtra, Punjab, or Uttar Pradesh) to dynamically load regional crop recommendations, APMC pricing, sowing cycles, and irrigation requirements."),
        ("5. Check Export Statistics: ", "Open 'Export Map' to browse the top 10 national export crops. Click on individual states to review their primary international trade crops and exporting shares."),
        ("6. Analyze Weather Maps: ", "Open 'Weather Map' to view local atmospheric parameters mapped against regional crop sensitivities.")
    ]

    for title, desc in steps:
        sp = doc.add_paragraph()
        sp.paragraph_format.left_indent = Inches(0.25)
        sp.paragraph_format.space_after = Pt(4)
        r = sp.add_run(title)
        r.font.bold = True
        sp.add_run(desc)

    # --- Section 5: Does It Really Solve Problems? ---
    add_section_heading("5. Does It Really Solve Problems?", level=1)
    
    p = doc.add_paragraph(
        "Many agricultural software tools suffer from lack of practical applicability or complex configurations. "
        "AgriVision AI is built specifically to address tangible, high-impact issues faced by farmers:"
    )
    p.paragraph_format.space_after = Pt(10)

    problems = [
        ("Eliminating Diagnosis Delays: ", "Fungal diseases like Late Blight can destroy an entire potato crop in under a week. Traditional agricultural extension cycles take days to weeks for field inspectors to visit. AgriVision AI provides a high-confidence diagnosis in 2-5 seconds, allowing immediate isolation and treatment before wide-scale damage occurs."),
        ("Preventing Pesticide Overuse: ", "Without precise identification, farmers often apply generic broad-spectrum chemical pesticides, which degrade soil quality, harm beneficial insects, and lead to pathogen resistance. By classifying the exact disease (e.g., distinguishing Cedar Apple Rust from Apple Scab) and giving specific organic, biological, and chemical options, the application promotes target-specific, eco-friendly crop care."),
        ("Empowering Price Negotiation: ", "Due to lack of transparent price data, small farmers frequently sell their produce to local middlemen at heavily discounted rates. AgriVision AI's APMC pricing engine pulls live/simulated mandi pricing directly to the farmer's mobile screen, providing them with local benchmark pricing to negotiate on equal terms."),
        ("Export Optimization: ", "The export dashboard guides progressive farmers and agricultural cooperatives toward high-value international trade crops (like Mango, Sesame, and Spices) by detailing target countries and volume shares. This changes farming from a local subsistence activity into an internationally competitive business.")
    ]

    for title, desc in problems:
        pp = doc.add_paragraph(style='List Bullet')
        r = pp.add_run(title)
        r.font.bold = True
        pp.add_run(desc)

    # --- Section 6: Why It Needs to be Made ---
    add_section_heading("6. Why It Needs to be Made", level=1)
    
    p = doc.add_paragraph(
        "Agriculture is the primary source of livelihood for over 58% of India's population. However, crop diseases "
        "cost the national economy billions of rupees annually, directly impacting food security, farm incomes, and rural stability. "
        "AgriVision AI represents a critical digital intervention because:"
    )
    p.paragraph_format.space_after = Pt(10)

    reasons = [
        ("Deficit of Pathologists: ", "There is an extreme shortage of trained agricultural pathologists and extension officers in rural regions. AI-powered diagnostics serve as a highly scalable alternative that is available 24/7."),
        ("Data Convergence: ", "Currently, farmers have to use multiple sources for weather, mandi prices, and crop care. AgriVision AI unifies these systems, correlating regional weather maps and crop profiles so farmers can anticipate risks and market opportunities in one workflow."),
        ("Modernizing Rural Livelihoods: ", "Adopting deep learning and data-driven intelligence is necessary to build a climate-resilient agricultural economy. Empowering young, tech-savvy farmers with these tools drives modern agricultural practices and improves local farm profitability.")
    ]

    for title, desc in reasons:
        rp = doc.add_paragraph(style='List Bullet')
        r = rp.add_run(title)
        r.font.bold = True
        rp.add_run(desc)

    # --- Section 7: Future Improvements ---
    add_section_heading("7. Future Improvements", level=1)
    
    p = doc.add_paragraph(
        "To scale the platform and expand its reach, the following future roadmap is planned for AgriVision AI:"
    )
    p.paragraph_format.space_after = Pt(10)

    roadmaps = [
        ("Offline Edge Compilation (TensorFlow Lite): ", "Compile the research MobileNetV2 transfer learning model into a lightweight TFLite format to run on-device inside a mobile application. This enables diagnostics in areas with zero cellular connectivity, bringing the 87,000+ image training set knowledge directly to the field."),
        ("IoT Drone/CCTV Field Integration: ", "Integrate remote camera feeds or drone imagery to auto-scan entire fields, identifying early-stage disease outbreaks and generating farm-wide crop health heatmaps."),
        ("Local Language Translation (Multilingual UI): ", "Localize the user interface, causes, and treatments into regional Indian languages (Hindi, Gujarati, Punjabi, Bengali, Marathi, and Tamil) to ensure accessibility for all farmers."),
        ("Pest and Weed Classifier: ", "Expand the classification engine to recognize crop pests, weeds, and beneficial predatory insects, giving chemical-free weed management advice.")
    ]

    for title, desc in roadmaps:
        rm = doc.add_paragraph(style='List Bullet')
        r = rm.add_run(title)
        r.font.bold = True
        rm.add_run(desc)

    # --- Section 8: Technical File-by-File Analysis ---
    add_section_heading("8. Technical File-by-File Analysis", level=1)
    
    p = doc.add_paragraph(
        "A comprehensive directory scan was completed. The AgriVision AI codebase consists of the following key components, "
        "listed with their size, structure, and functional details:"
    )
    p.paragraph_format.space_after = Pt(12)

    # Create Table
    table = doc.add_table(rows=1, cols=4)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    
    # Headers
    hdr_cells = table.rows[0].cells
    hdr_cells[0].text = 'File / Component'
    hdr_cells[1].text = 'Type'
    hdr_cells[2].text = 'Size / Length'
    hdr_cells[3].text = 'Functional Details'
    
    # Format Headers
    for cell in hdr_cells:
        set_cell_shading(cell, "1E4620")
        for p_cell in cell.paragraphs:
            p_cell.alignment = WD_ALIGN_PARAGRAPH.LEFT
            for run_cell in p_cell.runs:
                run_cell.font.bold = True
                run_cell.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
                run_cell.font.size = Pt(10)

    file_data = [
        ("app.py", "Flask Backend", "664 lines\n(35,169 bytes)", 
         "Main application server. Contains Flask routes for homepage, upload, crop-map, export-map, and weather. Includes local fallback databases for disease causes, disease prevention, base crop profiles, and state APMC price maps. Combines live data.gov.in API fetching with deterministic MD5 fallback simulator."),
        
        ("api_client.py", "API Helper", "162 lines\n(6,120 bytes)", 
         "Handles communication with the external Plant.id API v3 endpoint. Encodes images to Base64, dispatches POST requests with detailed symptom queries, handles HTTP error codes (e.g. 401, 403), processes JSON output, and implements a 10% disease probability threshold."),
        
        ("extract_pdf.py", "Utility Script", "18 lines\n(642 bytes)", 
         "Utility script that uses PyPDF2 to read the project's transfer learning documentation PDF and dump its raw text structure to a txt file."),
        
        ("requirements.txt", "Config File", "7 lines\n(104 bytes)", 
         "Lists python package dependencies: Flask (v3.1.1), gunicorn (v26.0.0), tensorflow (v2.18.0), numpy, Pillow, opencv-python-headless, and python-dotenv."),
        
        ("templates/home.html", "HTML Template", "156 lines\n(9,779 bytes)", 
         "Landing page template. Configured with dynamic navbar, statistics counter, and supported plant listings. Corrected to describe the Base64 API transmission path rather than local image resizing and MobileNetV2 hosting."),
        
        ("templates/upload.html", "HTML Template", "15.3 KB", 
         "Diagnosis file upload page. Renders image input fields, forms, and crop/fruit selection toggle. Handles flashing warning/error messages."),
        
        ("templates/result.html", "HTML Template", "118 lines\n(5,514 bytes)", 
         "Diagnosis result dashboard. Renders uploaded leaf image alongside plant type, disease label, confidence score gauge, cause description, and step-by-step organic/chemical treatment recommendation blocks."),
        
        ("templates/map.html", "HTML Template", "2,046 lines\n(345,393 bytes)", 
         "Interactive Crop Map page. Features a highly detailed inline SVG map of India with green outlines and glowing hover animations. Dynamic side panel displays regional crops, sowing guides, and simulated APMC details upon state selection."),
        
        ("templates/export.html", "HTML Template", "1,155 lines\n(227,719 bytes)", 
         "National Export Map dashboard. Displays the SVG map with gold outlines. Clicking a state queries export_data.js and renders list cards detail ranking regional export commodities, importing trade countries, and export volume shares."),
        
        ("templates/weather.html", "HTML Template", "1,823 lines\n(250,248 bytes)", 
         "Weather Map interface. Configures cloudy animated background layers and glows mapping climatic variables across states."),
        
        ("templates/team.html", "HTML Template", "12.4 KB", 
         "Team bio page. Contains bio cards for project team Aryan Ponkiya, Kausar Rami, and Vraj Akbari across specialized agronomic AI roles. Corrected to attribute accuracy directly to the Plant.id engine integration."),
        
        ("static/style.css", "CSS Stylesheet", "14.4 KB", 
         "Global style sheet. Declares CSS variables, animations (animate-up, floatGlow), responsive flex/grid layouts, scrollbar behavior, and custom glassmorphic styling (backdrop-filters)."),
        
        ("static/export_data.js", "JS Database", "40.7 KB", 
         "Static JSON database mapping Indian states to lists of export crops, rank indices, target countries, and export shares."),
        
        ("static/leaves.js", "JS Animation", "5.5 KB", 
         "Adds floating, interactive leaf particle animations to the web background, creating an organic theme across pages."),
        
        ("test/test/", "Test Dataset", "33 JPG files", 
         "Contains test images representing Apple Cedar Rust, Apple Scab, Corn Common Rust, Potato Early Blight, Potato Healthy, Tomato Early Blight, Tomato Healthy, and Tomato Yellow Curl Virus classes.")
    ]

    for filename, ftype, fsize, fdetails in file_data:
        row_cells = table.add_row().cells
        row_cells[0].text = filename
        row_cells[1].text = ftype
        row_cells[2].text = fsize
        row_cells[3].text = fdetails
        
        # Style row text
        for cell in row_cells:
            for paragraph in cell.paragraphs:
                paragraph.alignment = WD_ALIGN_PARAGRAPH.LEFT
                for run in paragraph.runs:
                    run.font.size = Pt(9.5)

    # Table formatting tweaks: set column widths
    widths = [Inches(1.2), Inches(1.0), Inches(1.0), Inches(3.3)]
    for row in table.rows:
        for idx, width in enumerate(widths):
            row.cells[idx].width = width

    # Save Document
    output_filename = "AgriVision_AI_Project_Report.docx"
    doc.save(output_filename)
    print(f"Report successfully saved as: {output_filename}")

if __name__ == "__main__":
    create_report()
