from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
import io

def generate_report(payload: dict) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=45,
        bottomMargin=40
    )
    
    # Styles
    styles = getSampleStyleSheet()
    
    # Custom Palette
    c_primary = colors.HexColor("#0A0A0F")
    c_accent = colors.HexColor("#3B82F6")
    c_success = colors.HexColor("#22C55E")
    c_warning = colors.HexColor("#F59E0B")
    c_danger = colors.HexColor("#EF4444")
    c_text_dark = colors.HexColor("#1E293B")
    c_text_muted = colors.HexColor("#64748B")
    c_light_bg = colors.HexColor("#F8FAFC")
    
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontSize=24,
        leading=28,
        textColor=colors.white
    )
    
    section_title_style = ParagraphStyle(
        'SectionTitle',
        parent=styles['Heading2'],
        fontSize=14,
        leading=18,
        textColor=c_accent,
        spaceAfter=6,
        spaceBefore=10
    )
    
    body_style = ParagraphStyle(
        'BodyDark',
        parent=styles['BodyText'],
        fontSize=10,
        leading=14,
        textColor=c_text_dark
    )
    
    label_style = ParagraphStyle(
        'LabelStyle',
        parent=styles['BodyText'],
        fontSize=11,
        leading=15,
        textColor=colors.white
    )
    
    list_style = ParagraphStyle(
        'ListStyle',
        parent=body_style,
        leftIndent=15,
        firstLineIndent=-10
    )
    
    elements = []
    
    # --- HEADER BLOCK ---
    # Draw a colored banner for the title
    header_data = [
        [
            Paragraph("RESUME ANALYSER REPORT", title_style),
            Paragraph("ATS MATCH DIAGNOSTIC", ParagraphStyle('SubText', parent=label_style, alignment=2, textColor=c_accent))
        ]
    ]
    header_table = Table(header_data, colWidths=[350, 180])
    header_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), c_primary),
        ('PADDING', (0,0), (-1,-1), 16),
        ('BOTTOMPADDING', (0,0), (-1,-1), 20),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    elements.append(header_table)
    elements.append(Spacer(1, 15))
    
    # --- SUMMARY & SCORE WIDGET ---
    score = payload.get("matchScore", 0)
    label = payload.get("matchLabel", "Needs Work")
    summary = payload.get("summary", "No summary available.")
    
    score_color = c_success if score >= 80 else c_warning if score >= 60 else c_danger
    
    score_html = f"<font size='44' color='{score_color.hexval()}'>{score}%</font><br/><font size='12' color='#64748B'>{label.upper()}</font>"
    score_p = Paragraph(score_html, ParagraphStyle('ScoreP', alignment=1, leading=40))
    
    summary_html = f"<b>Executive Summary:</b><br/>{summary}"
    summary_p = Paragraph(summary_html, body_style)
    
    widget_table = Table([[score_p, summary_p]], colWidths=[130, 400])
    widget_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), c_light_bg),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#E2E8F0")),
        ('PADDING', (0,0), (-1,-1), 12),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('ALIGN', (0,0), (0,0), 'CENTER'),
    ]))
    elements.append(widget_table)
    elements.append(Spacer(1, 15))
    
    # --- KEYWORDS MATCHED & MISSING ---
    elements.append(Paragraph("Keyword Analysis", section_title_style))
    matched_kws = ", ".join(payload.get("matchedKeywords", [])) or "None identified"
    missing_kws = ", ".join(payload.get("missingKeywords", [])) or "None identified"
    
    keyword_data = [
        [Paragraph("<b>Matched Keywords:</b>", body_style)],
        [Paragraph(f"<font color='green'>{matched_kws}</font>", body_style)],
        [Spacer(1, 4)],
        [Paragraph("<b>Missing Keywords:</b>", body_style)],
        [Paragraph(f"<font color='red'>{missing_kws}</font>", body_style)],
    ]
    keyword_table = Table(keyword_data, colWidths=[530])
    keyword_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), c_light_bg),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#E2E8F0")),
        ('PADDING', (0,0), (-1,-1), 10),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
    ]))
    elements.append(keyword_table)
    elements.append(Spacer(1, 15))
    
    # --- SKILLS GAP ANALYSIS ---
    skill_scores = payload.get("skillScores", {})
    if skill_scores:
        elements.append(Paragraph("Estimated Skill Scores", section_title_style))
        skill_rows = []
        for skill, val in skill_scores.items():
            skill_p = Paragraph(f"<b>{skill}</b>", body_style)
            val_p = Paragraph(f"<b>{val}%</b>", ParagraphStyle('ValP', parent=body_style, alignment=2))
            
            # Simple text representation of the progress bar
            blocks = int(val / 10)
            bar_text = "■" * blocks + "□" * (10 - blocks)
            bar_color = "green" if val >= 80 else "orange" if val >= 60 else "red"
            bar_p = Paragraph(f"<font face='Helvetica' color='{bar_color}'>{bar_text}</font>", body_style)
            
            skill_rows.append([skill_p, bar_p, val_p])
            
        skill_table = Table(skill_rows, colWidths=[180, 270, 80])
        skill_table.setStyle(TableStyle([
            ('PADDING', (0,0), (-1,-1), 6),
            ('LINEBELOW', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ]))
        elements.append(skill_table)
        elements.append(Spacer(1, 15))
        
    # --- RECOMMENDATIONS ---
    elements.append(Paragraph("Actionable Recommendations", section_title_style))
    recs = payload.get("recommendations", [])
    for idx, rec in enumerate(recs, 1):
        rec_html = f"<b>{idx}.</b> {rec}"
        elements.append(Paragraph(rec_html, list_style))
        elements.append(Spacer(1, 4))
        
    # --- FOOTER BAR ---
    def add_footer(canvas, doc):
        canvas.saveState()
        canvas.setFont('Helvetica', 8)
        canvas.setFillColor(c_text_muted)
        canvas.drawString(40, 20, "Resume Analyser API — Deployed on Azure & Render")
        canvas.drawRightString(letter[0] - 40, 20, f"Page {doc.page}")
        canvas.restoreState()
        
    doc.build(elements, onFirstPage=add_footer, onLaterPages=add_footer)
    
    pdf_data = buffer.getvalue()
    buffer.close()
    return pdf_data
