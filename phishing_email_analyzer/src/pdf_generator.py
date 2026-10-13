import os
from typing import Dict, Any, List
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, BaseDocTemplate, Frame, PageTemplate, Flowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import arabic_reshaper
from bidi.algorithm import get_display

def reshape_text(text: str) -> str:
    """Reshapes and applies bidirectional algorithm for Persian text."""
    if not text:
        return ""
    reshaped_text = arabic_reshaper.reshape(str(text))
    bidi_text = get_display(reshaped_text)
    return bidi_text

def register_fonts():
    """Registers Vazirmatn fonts for Persian text support."""
    # Assuming fonts are placed in the root directory
    font_path_regular = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'Vazirmatn-Regular.ttf')
    font_path_bold = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'Vazirmatn-Bold.ttf')

    if os.path.exists(font_path_regular):
        pdfmetrics.registerFont(TTFont('Vazirmatn', font_path_regular))
    else:
        print("Warning: Vazirmatn-Regular.ttf not found. Using default Helvetica.")
        pdfmetrics.registerFont(TTFont('Vazirmatn', 'Helvetica'))

    if os.path.exists(font_path_bold):
        pdfmetrics.registerFont(TTFont('Vazirmatn-Bold', font_path_bold))
    else:
        print("Warning: Vazirmatn-Bold.ttf not found. Using default Helvetica-Bold.")
        pdfmetrics.registerFont(TTFont('Vazirmatn-Bold', 'Helvetica-Bold'))

def get_styles():
    """Returns custom styles using Vazirmatn font."""
    styles = getSampleStyleSheet()

    # Check if font was registered successfully
    font_name = 'Vazirmatn' if 'Vazirmatn' in pdfmetrics.getRegisteredFontNames() else 'Helvetica'
    font_name_bold = 'Vazirmatn-Bold' if 'Vazirmatn-Bold' in pdfmetrics.getRegisteredFontNames() else 'Helvetica-Bold'

    styles.add(ParagraphStyle(
        name='PersianNormal',
        fontName=font_name,
        fontSize=10,
        leading=14,
        wordWrap='CJK',
        alignment=0 # Left
    ))

    styles.add(ParagraphStyle(
        name='PersianBold',
        fontName=font_name_bold,
        fontSize=12,
        leading=16,
        spaceAfter=10,
        wordWrap='CJK'
    ))

    styles.add(ParagraphStyle(
        name='PersianTitle',
        fontName=font_name_bold,
        fontSize=16,
        leading=20,
        spaceAfter=15,
        alignment=1, # Center
        wordWrap='CJK'
    ))
    return styles


def create_header_footer(canvas, doc, title):
    """Draws header and footer on each page."""
    canvas.saveState()

    # Header
    canvas.setFont('Vazirmatn-Bold' if 'Vazirmatn-Bold' in pdfmetrics.getRegisteredFontNames() else 'Helvetica-Bold', 10)
    canvas.drawString(doc.leftMargin, doc.height + doc.topMargin + 10, title)
    canvas.line(doc.leftMargin, doc.height + doc.topMargin + 5, doc.width + doc.leftMargin, doc.height + doc.topMargin + 5)

    # Footer
    canvas.setFont('Vazirmatn' if 'Vazirmatn' in pdfmetrics.getRegisteredFontNames() else 'Helvetica', 9)
    page_number_text = reshape_text(f"Page {doc.page}")
    canvas.drawRightString(doc.width + doc.leftMargin, doc.bottomMargin - 15, page_number_text)

    canvas.restoreState()


class ReportTemplate(BaseDocTemplate):
    """Custom template to allow headers and footers."""
    def __init__(self, filename, title, **kwargs):
        super().__init__(filename, **kwargs)
        self.title = title

    def build(self, flowables, **kwargs):
        frame = Frame(self.leftMargin, self.bottomMargin, self.width, self.height, id='normal')
        template = PageTemplate(id='test', frames=frame, onPage=lambda c, d: create_header_footer(c, d, self.title))
        self.addPageTemplates([template])
        super().build(flowables, **kwargs)


def _build_common_story(data: Dict[str, Any], styles) -> List[Any]:
    """Builds the common story elements for both print and fillable PDFs."""
    story = []

    # Title
    story.append(Paragraph(reshape_text("Phishing Email Analysis Report"), styles['PersianTitle']))
    story.append(Spacer(1, 15))

    # Headers Section
    story.append(Paragraph(reshape_text("Headers"), styles['PersianBold']))

    headers_data = [
        ['Date', data.get('Date', '')],
        ['Subject', data.get('Subject', '')],
        ['To', data.get('To', '')],
        ['From', data.get('From', '')],
        ['Reply-To', data.get('Reply-To', '')],
        ['Return-Path', data.get('Return-Path', '')],
        ['Sender IP', data.get('Sender IP', '')],
        ['Resolve Host', data.get('Resolve Host', '')],
        ['Message-ID', data.get('Message-ID', '')],
    ]

    # Reshape text for the table
    reshaped_headers = [[Paragraph(reshape_text(str(item)), styles['PersianNormal']) for item in row] for row in headers_data]

    t = Table(reshaped_headers, colWidths=[100, 350])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Vazirmatn' if 'Vazirmatn' in pdfmetrics.getRegisteredFontNames() else 'Helvetica'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('VALIGN', (0,0), (-1,-1), 'TOP')
    ]))
    story.append(t)
    story.append(Spacer(1, 15))

    # URLs Section
    story.append(Paragraph(reshape_text("URLs"), styles['PersianBold']))
    urls = data.get('URLs', [])
    if not urls:
        story.append(Paragraph(reshape_text("No URLs found."), styles['PersianNormal']))
    else:
        for url in urls:
            story.append(Paragraph(reshape_text(url), styles['PersianNormal']))
            story.append(Spacer(1, 2))
    story.append(Spacer(1, 15))

    # Attachments Section
    story.append(Paragraph(reshape_text("Attachments"), styles['PersianBold']))
    attachments = data.get('Attachments', [])
    if not attachments:
        story.append(Paragraph(reshape_text("No attachments found."), styles['PersianNormal']))
    else:
        for i, att in enumerate(attachments):
            att_data = [
                ['Attachment Name', att.get('Attachment Name', '')],
                ['MD5', att.get('MD5', '')],
                ['SHA1', att.get('SHA1', '')],
                ['SHA256', att.get('SHA256', '')]
            ]
            reshaped_att = [[Paragraph(reshape_text(str(item)), styles['PersianNormal']) for item in row] for row in att_data]
            t_att = Table(reshaped_att, colWidths=[100, 350])
            t_att.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('VALIGN', (0,0), (-1,-1), 'TOP')
            ]))
            story.append(t_att)
            if i < len(attachments) - 1:
                story.append(Spacer(1, 5))
    story.append(Spacer(1, 15))

    return story


def generate_print_report(data: Dict[str, Any], output_path: str):
    """Generates a print-friendly PDF with blank spaces for handwriting."""
    register_fonts()
    styles = get_styles()

    doc = ReportTemplate(output_path, "Phishing Email Print Report", pagesize=A4,
                         rightMargin=40, leftMargin=40, topMargin=50, bottomMargin=50)

    story = _build_common_story(data, styles)

    # Description
    story.append(Paragraph(reshape_text("Description"), styles['PersianBold']))

    # Construct a concise summary for description
    num_urls = len(data.get('URLs', []))
    num_atts = len(data.get('Attachments', []))
    auth_res = data.get('Authentication-Results', 'None found')
    if auth_res != 'None found':
        auth_res += " (Unverified from Headers)"

    source_filename = os.path.basename(data.get('_Source_Filename', 'unknown_source.eml'))

    summary = f"Email summary: Source file '{source_filename}' contains {num_urls} URLs and {num_atts} attachments. Authentication Results: {auth_res}."
    story.append(Paragraph(reshape_text(summary), styles['PersianNormal']))
    story.append(Spacer(1, 15))

    # Artifact Analysis
    story.append(Paragraph(reshape_text("Artifact Analysis"), styles['PersianBold']))

    # Blank fields for print
    for field in ["Sender Analysis", "URL Analysis", "Attachment Analysis"]:
        story.append(Paragraph(reshape_text(field), styles['PersianNormal']))
        # Draw a big empty box
        empty_box_data = [['\n\n\n\n\n\n']]
        t_box = Table(empty_box_data, colWidths=[450])
        t_box.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        story.append(t_box)
        story.append(Spacer(1, 10))

    story.append(PageBreak())

    # Verdict
    story.append(Paragraph(reshape_text("Verdict"), styles['PersianBold']))
    empty_box_data = [['\n\n\n']]
    t_box = Table(empty_box_data, colWidths=[450])
    t_box.setStyle(TableStyle([('GRID', (0, 0), (-1, -1), 1, colors.black)]))
    story.append(t_box)
    story.append(Spacer(1, 15))

    # Defense Actions
    story.append(Paragraph(reshape_text("Defense Actions"), styles['PersianBold']))
    empty_box_data = [['\n\n\n\n\n\n']]
    t_box = Table(empty_box_data, colWidths=[450])
    t_box.setStyle(TableStyle([('GRID', (0, 0), (-1, -1), 1, colors.black)]))
    story.append(t_box)

    doc.build(story)


class InteractiveTextField(Flowable):
    """Custom Flowable to create interactive text fields."""
    def __init__(self, name, tooltip, width, height):
        super().__init__()
        self.name = name
        self.tooltip = tooltip
        self.width = width
        self.height = height

    def draw(self):
        self.canv.saveState()
        # Form field creation.
        # ReportLab supports basic form fields but complete RTL integration in standard PDF readers might vary.
        form = self.canv.acroForm
        # ReportLab's acroForm standard implementation only supports the standard 14 fonts for text fields.
        # It throws an error if a custom TTF font like 'Vazirmatn' is used for form fields.
        # Thus, we fallback to Helvetica for the form fields themselves,
        # while keeping the Vazirmatn font for the labels (which are rendered perfectly).
        form.textfield(
            name=self.name,
            tooltip=self.tooltip,
            x=0,
            y=0,
            width=self.width,
            height=self.height,
            borderStyle='solid',
            borderWidth=1,
            fillColor=colors.white,
            borderColor=colors.black,
            textColor=colors.black,
            fontName='Helvetica',
            fontSize=10
        )
        self.canv.restoreState()


def generate_fillable_report(data: Dict[str, Any], output_path: str):
    """Generates a fillable PDF report with interactive form fields."""
    register_fonts()
    styles = get_styles()

    doc = ReportTemplate(output_path, "Phishing Email Fillable Report", pagesize=A4,
                         rightMargin=40, leftMargin=40, topMargin=50, bottomMargin=50)

    story = _build_common_story(data, styles)

    # Description
    story.append(Paragraph(reshape_text("Description"), styles['PersianBold']))

    # Construct a concise summary for description
    num_urls = len(data.get('URLs', []))
    num_atts = len(data.get('Attachments', []))
    auth_res = data.get('Authentication-Results', 'None found')
    if auth_res != 'None found':
        auth_res += " (Unverified from Headers)"

    source_filename = os.path.basename(data.get('_Source_Filename', 'unknown_source.eml'))

    summary = f"Email summary: Source file '{source_filename}' contains {num_urls} URLs and {num_atts} attachments. Authentication Results: {auth_res}."

    story.append(Paragraph(reshape_text(summary), styles['PersianNormal']))
    story.append(Spacer(1, 15))

    # Artifact Analysis
    story.append(Paragraph(reshape_text("Artifact Analysis"), styles['PersianBold']))

    for field in ["Sender Analysis", "URL Analysis", "Attachment Analysis"]:
        story.append(Paragraph(reshape_text(field), styles['PersianNormal']))
        story.append(Spacer(1, 5))
        # Add interactive text field
        tf = InteractiveTextField(name=f"Field_{field.replace(' ', '_')}", tooltip=field, width=450, height=80)
        story.append(tf)
        story.append(Spacer(1, 10))

    story.append(PageBreak())

    # Verdict
    story.append(Paragraph(reshape_text("Verdict"), styles['PersianBold']))
    story.append(Spacer(1, 5))
    tf_verdict = InteractiveTextField(name="Field_Verdict", tooltip="Verdict", width=450, height=40)
    story.append(tf_verdict)
    story.append(Spacer(1, 15))

    # Defense Actions
    story.append(Paragraph(reshape_text("Defense Actions"), styles['PersianBold']))
    story.append(Spacer(1, 5))
    tf_defense = InteractiveTextField(name="Field_Defense_Actions", tooltip="Defense Actions", width=450, height=80)
    story.append(tf_defense)

    doc.build(story)
