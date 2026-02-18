from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
import tempfile
import os


class PDFGenerator:
    def __init__(self, analysis_results, original_filename):
        self.results = analysis_results
        self.original_filename = original_filename
        self.styles = getSampleStyleSheet()
        self.setup_custom_styles()

    def setup_custom_styles(self):
        """Setup custom paragraph styles safely"""

        # Custom Title Style
        if 'CustomTitle' not in self.styles:
            self.styles.add(ParagraphStyle(
                name='CustomTitle',
                parent=self.styles['Heading1'],
                fontSize=24,
                textColor=colors.HexColor('#1a1a1a'),
                spaceAfter=30,
                alignment=TA_CENTER
            ))

        # Section Header Style
        if 'SectionHeader' not in self.styles:
            self.styles.add(ParagraphStyle(
                name='SectionHeader',
                parent=self.styles['Heading2'],
                fontSize=16,
                textColor=colors.HexColor('#2c3e50'),
                spaceAfter=12,
                spaceBefore=20
            ))

        # Custom Body Style (FIXED - renamed)
        if 'CustomBodyText' not in self.styles:
            self.styles.add(ParagraphStyle(
                name='CustomBodyText',
                parent=self.styles['Normal'],
                fontSize=10,
                spaceAfter=6
            ))

    def generate(self):
        """Generate PDF report"""

        # Create temp file
        temp_dir = tempfile.gettempdir()
        pdf_filename = f"log_analysis_{os.path.basename(self.original_filename)}_{os.getpid()}.pdf"
        pdf_path = os.path.join(temp_dir, pdf_filename)

        # Create document
        doc = SimpleDocTemplate(pdf_path, pagesize=letter)
        story = []

        # Title
        story.append(Paragraph("Log Analysis Report", self.styles['CustomTitle']))
        story.append(Spacer(1, 0.2 * inch))

        # File Information
        story.append(Paragraph("File Information", self.styles['SectionHeader']))
        file_info_data = [
            ['Filename:', self.results.get('filename', 'N/A')],
            ['File Type:', self.results.get('file_type', 'Unknown')],
            ['File Size:', self.results.get('total_size', 'N/A')],
            ['Analysis Date:', self.results.get('timestamp', 'N/A')],
        ]

        file_info_table = Table(file_info_data, colWidths=[2 * inch, 4 * inch])
        file_info_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#ecf0f1')),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
        ]))

        story.append(file_info_table)
        story.append(Spacer(1, 0.3 * inch))

        # Summary Section
        story.append(Paragraph("Summary Statistics", self.styles['SectionHeader']))

        summary_data = [
            ['Metric', 'Value'],
            ['Total Lines', str(self.results.get('total_lines', 0))],
            ['Error Count', str(self.results.get('error_count', 0))],
            ['Warning Count', str(self.results.get('warning_count', 0))],
            ['Info Count', str(self.results.get('info_count', 0))],
            ['Error Rate', f"{self.results.get('error_rate', 0):.2f}%"],
            ['Warning Rate', f"{self.results.get('warning_rate', 0):.2f}%"],
            ['Unique IP Addresses', str(self.results.get('unique_ip_count', 0))],
        ]

        summary_table = Table(summary_data, colWidths=[3 * inch, 3 * inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
        ]))

        story.append(summary_table)
        story.append(Spacer(1, 0.3 * inch))

        # Top URLs (Using Corrected Style)
        if self.results.get('unique_urls'):
            story.append(Paragraph("Top URLs", self.styles['SectionHeader']))
            for url in self.results['unique_urls'][:10]:
                story.append(Paragraph(f"• {url}", self.styles['CustomBodyText']))
            story.append(Spacer(1, 0.2 * inch))

        # Build PDF
        doc.build(story)

        return pdf_path
