import io
import os
from typing import Optional
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    HRFlowable,
    Table,
    TableStyle,
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from backend.app.models.schemas import ResumeSchema


class PDFGenerator:
    """
    Generates ATS-optimized, machine-readable PDF resumes using ReportLab.
    Supports 3 professional styles:
    - classic_ats: standard monochrome, universally compatible with all ATS parsers
    - modern_tech: tech-forward styling with subtle indigo/slate accents
    - executive: refined typography with deep navy hierarchy for senior roles
    """

    TEMPLATE_CONFIGS = {
        "classic_ats": {
            "primary": colors.HexColor("#0f172a"),
            "heading": colors.HexColor("#1e293b"),
            "subheading": colors.HexColor("#1e293b"),
            "text": colors.HexColor("#334155"),
            "muted": colors.HexColor("#475569"),
            "divider": colors.HexColor("#cbd5e1"),
            "link": "#2563eb",
            "divider_thickness": 1,
        },
        "modern_tech": {
            "primary": colors.HexColor("#312e81"),
            "heading": colors.HexColor("#4338ca"),
            "subheading": colors.HexColor("#1e1b4b"),
            "text": colors.HexColor("#1f2937"),
            "muted": colors.HexColor("#4b5563"),
            "divider": colors.HexColor("#6366f1"),
            "link": "#4f46e5",
            "divider_thickness": 1.5,
        },
        "executive": {
            "primary": colors.HexColor("#1e3a8a"),
            "heading": colors.HexColor("#172554"),
            "subheading": colors.HexColor("#1e293b"),
            "text": colors.HexColor("#1e293b"),
            "muted": colors.HexColor("#334155"),
            "divider": colors.HexColor("#93c5fd"),
            "link": "#1d4ed8",
            "divider_thickness": 1.2,
        },
    }

    @classmethod
    def generate(cls, resume: ResumeSchema, output_path: Optional[str] = None, template: str = "classic_ats") -> bytes:
        config = cls.TEMPLATE_CONFIGS.get(template, cls.TEMPLATE_CONFIGS["classic_ats"])
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            output_path if output_path else buffer,
            pagesize=letter,
            leftMargin=36,
            rightMargin=36,
            topMargin=36,
            bottomMargin=36,
        )

        styles = getSampleStyleSheet()

        name_style = ParagraphStyle(
            "NameStyle",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=21,
            leading=25,
            alignment=TA_CENTER,
            textColor=config["primary"],
        )

        contact_style = ParagraphStyle(
            "ContactStyle",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=9.5,
            leading=13,
            alignment=TA_CENTER,
            textColor=config["muted"],
        )

        section_heading = ParagraphStyle(
            "SectionHeading",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=11.5,
            leading=15,
            alignment=TA_LEFT,
            textColor=config["heading"],
            spaceBefore=8,
            spaceAfter=3,
        )

        subheading_left = ParagraphStyle(
            "SubheadingLeft",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=10,
            leading=13,
            textColor=config["subheading"],
        )

        subheading_right = ParagraphStyle(
            "SubheadingRight",
            parent=styles["Normal"],
            fontName="Helvetica-Oblique",
            fontSize=9,
            leading=13,
            alignment=TA_RIGHT,
            textColor=config["muted"],
        )

        body_style = ParagraphStyle(
            "Body",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=9.5,
            leading=13.5,
            textColor=config["text"],
        )

        bullet_style = ParagraphStyle(
            "Bullet",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=9.2,
            leading=13,
            leftIndent=14,
            firstLineIndent=-10,
            textColor=config["text"],
            spaceAfter=2,
        )

        elements = []

        # 1. Candidate Name
        elements.append(Paragraph(resume.name.upper() if resume.name else "CANDIDATE NAME", name_style))
        elements.append(Spacer(1, 4))

        # 2. Contact Information
        contact_parts = []
        if resume.email:
            contact_parts.append(f'<a href="mailto:{resume.email}" color="{config["link"]}">{resume.email}</a>')
        if resume.phone:
            contact_parts.append(resume.phone)
        if resume.location:
            contact_parts.append(resume.location)
        for link in resume.links:
            display_link = link.replace("https://", "").replace("http://", "").rstrip("/")
            contact_parts.append(f'<a href="{link}" color="{config["link"]}">{display_link}</a>')

        contact_line = " | ".join(contact_parts)
        if contact_line:
            elements.append(Paragraph(contact_line, contact_style))
            elements.append(Spacer(1, 8))

        def add_divider():
            return HRFlowable(
                width="100%",
                thickness=config["divider_thickness"],
                color=config["divider"],
                spaceBefore=2,
                spaceAfter=6,
            )

        # 3. Professional Summary
        if resume.summary:
            elements.append(Paragraph("PROFESSIONAL SUMMARY", section_heading))
            elements.append(add_divider())
            elements.append(Paragraph(resume.summary, body_style))
            elements.append(Spacer(1, 6))

        # 4. Technical Skills
        if resume.skills:
            elements.append(Paragraph("TECHNICAL SKILLS", section_heading))
            elements.append(add_divider())
            skills_text = f"<b>Core Competencies:</b> {', '.join(resume.skills)}"
            elements.append(Paragraph(skills_text, body_style))
            elements.append(Spacer(1, 6))

        # 5. Professional Experience
        if resume.experience:
            elements.append(Paragraph("PROFESSIONAL EXPERIENCE", section_heading))
            elements.append(add_divider())
            for exp in resume.experience:
                role_company = f"<b>{exp.title}</b> | {exp.company}"
                dates_loc = f"{exp.start_date} - {exp.end_date or 'Present'}"
                if exp.location:
                    dates_loc += f" ({exp.location})"

                table_data = [
                    [
                        Paragraph(role_company, subheading_left),
                        Paragraph(dates_loc, subheading_right),
                    ]
                ]
                t = Table(table_data, colWidths=[380, 160])
                t.setStyle(
                    TableStyle([
                        ("VALIGN", (0, 0), (-1, -1), "TOP"),
                        ("LEFTPADDING", (0, 0), (-1, -1), 0),
                        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
                    ])
                )
                elements.append(t)

                for h in exp.highlights:
                    bullet_text = f"&bull; {h}"
                    elements.append(Paragraph(bullet_text, bullet_style))
                elements.append(Spacer(1, 4))
            elements.append(Spacer(1, 2))

        # 6. Projects
        if resume.projects:
            elements.append(Paragraph("KEY PROJECTS", section_heading))
            elements.append(add_divider())
            for proj in resume.projects:
                tech_str = f" [<i>{', '.join(proj.technologies)}</i>]" if proj.technologies else ""
                proj_title = f"<b>{proj.name}</b>{tech_str}"
                proj_link = f'<a href="{proj.link}" color="{config["link"]}">Link</a>' if proj.link else ""

                table_data = [
                    [
                        Paragraph(proj_title, subheading_left),
                        Paragraph(proj_link, subheading_right),
                    ]
                ]
                t = Table(table_data, colWidths=[440, 100])
                t.setStyle(
                    TableStyle([
                        ("VALIGN", (0, 0), (-1, -1), "TOP"),
                        ("LEFTPADDING", (0, 0), (-1, -1), 0),
                        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
                    ])
                )
                elements.append(t)

                if proj.description:
                    elements.append(Paragraph(proj.description, body_style))

                for h in proj.highlights:
                    bullet_text = f"&bull; {h}"
                    elements.append(Paragraph(bullet_text, bullet_style))
                elements.append(Spacer(1, 4))
            elements.append(Spacer(1, 2))

        # 7. Education
        if resume.education:
            elements.append(Paragraph("EDUCATION", section_heading))
            elements.append(add_divider())
            for edu in resume.education:
                deg_inst = f"<b>{edu.degree}</b> - {edu.institution}"
                yr_gpa = edu.graduation_year or ""
                if edu.gpa:
                    yr_gpa += f" | GPA: {edu.gpa}"

                table_data = [
                    [
                        Paragraph(deg_inst, subheading_left),
                        Paragraph(yr_gpa, subheading_right),
                    ]
                ]
                t = Table(table_data, colWidths=[400, 140])
                t.setStyle(
                    TableStyle([
                        ("VALIGN", (0, 0), (-1, -1), "TOP"),
                        ("LEFTPADDING", (0, 0), (-1, -1), 0),
                        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
                    ])
                )
                elements.append(t)
            elements.append(Spacer(1, 6))

        # 8. Certifications & Achievements
        if resume.certifications or resume.achievements:
            elements.append(Paragraph("CERTIFICATIONS & ACHIEVEMENTS", section_heading))
            elements.append(add_divider())
            for cert in resume.certifications:
                elements.append(Paragraph(f"&bull; {cert}", bullet_style))
            for ach in resume.achievements:
                elements.append(Paragraph(f"&bull; {ach}", bullet_style))
            elements.append(Spacer(1, 6))

        doc.build(elements)
        if output_path:
            with open(output_path, "rb") as f:
                return f.read()
        return buffer.getvalue()
