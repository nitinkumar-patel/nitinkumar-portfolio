#!/usr/bin/env python3
"""
Dynamic Portfolio Generator from Word Document
Reads the .docx resume file and generates index.html
"""

import zipfile
import xml.etree.ElementTree as ET
import re
from datetime import datetime

def extract_text_from_docx(docx_path):
    """Extract all text content from a Word document."""
    try:
        with zipfile.ZipFile(docx_path, 'r') as docx:
            xml_content = docx.read('word/document.xml')
            root = ET.fromstring(xml_content)
            
            ns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
            
            texts = []
            for t in root.findall('.//w:t', ns):
                if t.text:
                    texts.append(t.text)
            
            full_text = ' '.join(texts)
            full_text = re.sub(r'\s+', ' ', full_text)
            return full_text
    except Exception as e:
        print(f"Error reading document: {e}")
        return None

def parse_resume_content(text):
    """Parse the extracted text into structured sections."""
    if not text:
        return None
    
    # Clean up the text
    text = text.strip()
    
    # Find sections
    sections = {
        'name': 'Nitinkumar Patel',
        'location': 'South Elgin, IL 60177',
        'email': 'npatel121.py@gmail.com',
        'phone': '+1 (484) 447-7008',
        'linkedin': 'linkedin.com/in/nitinkumar-patel',
        'github': 'github.com/nitinkumar-patel',
        'summary': '',
        'title': 'Engineering Lead & AI Architect'
    }
    
    # Extract Professional Summary
    summary_match = re.search(r'PROFESSIONAL SUMMARY\s+(.+?)(?=TECHNICAL SKILLS|PROFESSIONAL EXPERIENCE)', text, re.IGNORECASE | re.DOTALL)
    if summary_match:
        summary_text = summary_match.group(1).strip()
        # Clean up extra spaces and fix number formatting (e.g., "1 2 +" -> "12+")
        summary_text = re.sub(r'(\d)\s+(\d)\s*\+', r'\1\2+', summary_text)
        summary_text = re.sub(r'\s+', ' ', summary_text)
        sections['summary'] = summary_text
    
    # Extract title from summary (look for the title pattern)
    title_patterns = [
        r'Engineering Lead & AI Architect',
        r'Engineering Lead[^&]*& AI Architect',
        r'Lead Full Stack Engineer[^|]*\| AI & Cloud Architect'
    ]
    
    for pattern in title_patterns:
        title_match = re.search(pattern, text, re.IGNORECASE)
        if title_match:
            sections['title'] = title_match.group(0)
            break
    
    return sections

def read_existing_html():
    """Read the existing index.html to preserve structure."""
    try:
        with open('index.html', 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return None

def update_html_content(html_content, sections):
    """Update specific sections in the existing HTML."""
    if not html_content:
        return None
    
    # Update title in <title> tag
    html_content = re.sub(
        r'<title>.*?</title>',
        f'<title>{sections["name"]} • {sections["title"]}</title>',
        html_content
    )
    
    # Update meta description
    html_content = re.sub(
        r'<meta name="description" content="[^"]*">',
        f'<meta name="description" content="{sections["title"]} - Portfolio of {sections["name"]}">',
        html_content
    )
    
    # Update hero subtitle
    html_content = re.sub(
        r'<p class="hero-subtitle">.*?</p>',
        f'<p class="hero-subtitle">{sections["title"]}</p>',
        html_content
    )
    
    # Update professional summary
    if sections.get('summary'):
        # Find the about-text paragraph and replace its content
        summary_html = f'                    {sections["summary"]}'
        html_content = re.sub(
            r'(<p class="about-text">\s*)(.*?)(\s*</p>)',
            f'\\1{summary_html}\\3',
            html_content,
            flags=re.DOTALL
        )
    
    return html_content

def generate_html_template(sections):
    """Generate HTML from parsed sections."""
    
    # Try to read existing HTML first
    existing_html = read_existing_html()
    if existing_html:
        print("Found existing index.html, updating content...")
        updated_html = update_html_content(existing_html, sections)
        if updated_html:
            return updated_html
    
    # Fallback: generate from template
    # Read the current template structure
    template = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="{title} - Portfolio of {name}">
    <title>{name} • {title}</title>
    <link rel="stylesheet" href="styles.css">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
</head>
<body>
    <!-- Navigation -->
    <nav class="navbar">
        <div class="container">
            <a href="#top" class="nav-brand">{name}</a>
            <ul class="nav-menu">
                <li><a href="#about">About</a></li>
                <li><a href="#experience">Experience</a></li>
                <li><a href="#skills">Skills</a></li>
                <li><a href="#education">Education</a></li>
                <li><a href="#contact">Contact</a></li>
            </ul>
            <div class="nav-actions">
                <button class="btn btn-nav" id="export-pdf-btn" type="button">Export PDF</button>
            </div>
            <button class="nav-toggle" aria-label="Toggle navigation">
                <span></span>
                <span></span>
                <span></span>
            </button>
        </div>
    </nav>

    <!-- Hero Section -->
    <section id="top" class="hero">
        <div class="container">
            <div class="hero-content">
                <h1 class="hero-title">{name}</h1>
                <p class="hero-subtitle">{title}</p>
                <p class="hero-location">{location}</p>
                <div class="hero-links">
                    <a href="mailto:{email}" class="btn btn-primary">Email Me</a>
                    <a href="https://www.{linkedin}" target="_blank" class="btn btn-secondary">LinkedIn</a>
                    <a href="https://{github}" target="_blank" class="btn btn-secondary">GitHub</a>
                </div>
            </div>
        </div>
    </section>

    <!-- About Section -->
    <section id="about" class="section">
        <div class="container">
            <h2 class="section-title">Professional Summary</h2>
            <div class="about-content">
                <p class="about-text">
                    {summary}
                </p>
            </div>
        </div>
    </section>

    <!-- Experience Section -->
    <section id="experience" class="section section-alt">
        <div class="container">
            <h2 class="section-title">Professional Experience</h2>
            <div class="experience-list">
                {experience_html}
            </div>
        </div>
    </section>

    <!-- Skills Section -->
    <section id="skills" class="section">
        <div class="container">
            <h2 class="section-title">Technical Skills</h2>
            <div class="skills-grid">
                {skills_html}
            </div>
        </div>
    </section>

    <!-- Education Section -->
    <section id="education" class="section section-alt">
        <div class="container">
            <h2 class="section-title">Education</h2>
            <div class="education-list">
                {education_html}
            </div>
        </div>
    </section>

    <!-- Contact Section -->
    <section id="contact" class="section">
        <div class="container">
            <h2 class="section-title">Get In Touch</h2>
            <div class="contact-content">
                <p class="contact-text">I'm always open to discussing new opportunities and interesting projects.</p>
                <div class="contact-info">
                    <a href="mailto:{email}" class="contact-link">
                        <span class="contact-icon">✉️</span>
                        <span>{email}</span>
                    </a>
                    <a href="tel:{phone}" class="contact-link">
                        <span class="contact-icon">📞</span>
                        <span>{phone}</span>
                    </a>
                    <a href="https://www.{linkedin}" target="_blank" class="contact-link">
                        <span class="contact-icon">💼</span>
                        <span>LinkedIn Profile</span>
                    </a>
                    <a href="https://{github}" target="_blank" class="contact-link">
                        <span class="contact-icon">💻</span>
                        <span>GitHub Profile</span>
                    </a>
                </div>
            </div>
        </div>
    </section>

    <!-- Footer -->
    <footer class="footer">
        <div class="container">
            <p>
                &copy; {year} {name}. All rights reserved.
                <span id="last-modified"></span>
            </p>
        </div>
    </footer>

    <!-- PDF generation library for timestamped export -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/html2pdf.js/0.10.1/html2pdf.bundle.min.js" integrity="sha512-YcsIP36iGcD1qfN3Wf9eKJeNEgnbWiwxupCSvJzpuG1HsfrN7kYM/qfNwCuWHa3gwxObn2yFcEepE4ew3hnNug==" crossorigin="anonymous" referrerpolicy="no-referrer"></script>
    <script src="script.js"></script>
</body>
</html>'''
    
    # For now, return a note that this needs manual parsing
    # The full implementation would require more sophisticated parsing
    return template.format(
        name=sections.get('name', 'Nitinkumar Patel'),
        title=sections.get('title', 'Engineering Lead & AI Architect'),
        location=sections.get('location', 'South Elgin, IL 60177'),
        email=sections.get('email', 'npatel121.py@gmail.com'),
        phone=sections.get('phone', '+1 (484) 447-7008'),
        linkedin=sections.get('linkedin', 'linkedin.com/in/nitinkumar-patel'),
        github=sections.get('github', 'github.com/nitinkumar-patel'),
        summary=sections.get('summary', 'Engineering Lead & AI Architect with 12+ years of experience...'),
        experience_html='<!-- Experience will be parsed from document -->',
        skills_html='<!-- Skills will be parsed from document -->',
        education_html='<!-- Education will be parsed from document -->',
        year=datetime.now().year
    )

def main():
    """Main function to generate portfolio from Word document."""
    docx_path = 'Nitinkumar_Patel_Engineering_Lead_251223.docx'
    output_path = 'index.html'
    
    print(f"Reading resume from: {docx_path}")
    text = extract_text_from_docx(docx_path)
    
    if not text:
        print("Error: Could not extract text from document")
        return
    
    print("Parsing resume content...")
    sections = parse_resume_content(text)
    
    if not sections:
        print("Error: Could not parse resume content")
        return
    
    print("Generating HTML...")
    html = generate_html_template(sections)
    
    if not html:
        print("Error: Could not generate HTML")
        return
    
    print(f"Writing to: {output_path}")
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print("✓ Portfolio updated successfully!")
    print(f"\nUpdated sections:")
    print(f"  - Title: {sections.get('title', 'N/A')}")
    print(f"  - Summary: {'Updated' if sections.get('summary') else 'Not found'}")
    print("\nNote: This script updates the title and summary from the Word document.")
    print("For full parsing of experience, skills, and education sections,")
    print("you may need to manually update those sections or enhance the parser.")

if __name__ == '__main__':
    main()

