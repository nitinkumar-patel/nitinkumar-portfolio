#!/usr/bin/env python3
"""
Dynamic Portfolio Generator from Word Document.
Reads the .docx resume file and updates index.html.
"""

import html
import re
import zipfile
import xml.etree.ElementTree as ET
from datetime import datetime

SECTION_ALIASES = {
    "PROFESSIONAL SUMMARY": "summary",
    "SUMMARY": "summary",
    "TECHNICAL SKILLS": "skills",
    "SKILLS": "skills",
    "PROFESSIONAL EXPERIENCE": "experience",
    "EXPERIENCE": "experience",
    "CERTIFICATIONS & LEARNING": "certifications",
    "CERTIFICATIONS AND LEARNING": "certifications",
    "EDUCATION": "education",
}


def normalize_text(value):
    """Normalize spaces and punctuation artifacts from docx extraction."""
    value = value.replace("\xa0", " ").replace("–", "–")
    value = re.sub(r"\s+", " ", value).strip()
    value = re.sub(r"\s+([,.;:])", r"\1", value)
    value = re.sub(r"\(\s+", "(", value)
    value = re.sub(r"\s+\)", ")", value)
    return value.strip()


def extract_docx_paragraphs(docx_path):
    """Extract paragraph-level content from a Word document."""
    try:
        with zipfile.ZipFile(docx_path, "r") as docx:
            xml_content = docx.read("word/document.xml")
            root = ET.fromstring(xml_content)

        ns = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
        paragraphs = []
        for paragraph in root.findall(".//w:p", ns):
            texts = [t.text for t in paragraph.findall(".//w:t", ns) if t.text]
            if texts:
                cleaned = normalize_text("".join(texts))
                if cleaned:
                    paragraphs.append(cleaned)
        return paragraphs
    except Exception as exc:
        print(f"Error reading document: {exc}")
        return []


def extract_docx_paragraphs_with_links(docx_path):
    """Extract paragraph text and hyperlink metadata from a Word document."""
    try:
        with zipfile.ZipFile(docx_path, "r") as docx:
            xml_content = docx.read("word/document.xml")
            rels_content = docx.read("word/_rels/document.xml.rels")
            root = ET.fromstring(xml_content)
            rels_root = ET.fromstring(rels_content)

        ns = {
            "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
            "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
            "rel": "http://schemas.openxmlformats.org/package/2006/relationships",
        }
        rel_map = {
            rel.attrib.get("Id"): rel.attrib.get("Target", "")
            for rel in rels_root.findall(".//rel:Relationship", ns)
            if rel.attrib.get("Id")
        }

        paragraph_entries = []
        for paragraph in root.findall(".//w:p", ns):
            texts = [t.text for t in paragraph.findall(".//w:t", ns) if t.text]
            if not texts:
                continue
            cleaned = normalize_text("".join(texts))
            if not cleaned:
                continue

            links = []
            for hyperlink in paragraph.findall(".//w:hyperlink", ns):
                rel_id = hyperlink.attrib.get("{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id")
                link_text_parts = [t.text for t in hyperlink.findall(".//w:t", ns) if t.text]
                link_text = normalize_text("".join(link_text_parts))
                link_url = rel_map.get(rel_id, "").strip()
                if link_text and link_url:
                    links.append({"text": link_text, "url": link_url})

            paragraph_entries.append({"text": cleaned, "links": links})
        return paragraph_entries
    except Exception:
        return [{"text": paragraph, "links": []} for paragraph in extract_docx_paragraphs(docx_path)]


def extract_text_from_docx(docx_path):
    """Backward-compatible full text extraction."""
    paragraphs = extract_docx_paragraphs_with_links(docx_path)
    if not paragraphs:
        return None
    return normalize_text(" ".join(paragraphs))


def detect_header_info(paragraphs):
    """Extract name/contact details from the header area."""
    info = {
        "name": "Nitinkumar Patel",
        "location": "South Elgin, IL",
        "email": "npatel121.py@gmail.com",
        "phone": "+1 (484) 447-7008",
        "linkedin": "linkedin.com/in/nitinkumar-patel",
        "github": "github.com/nitinkumar-patel",
        "title": "Staff AI Engineer",
    }
    if paragraphs:
        info["name"] = paragraphs[0]

    for line in paragraphs[:8]:
        if "@" in line:
            email = re.search(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", line)
            phone = re.search(r"(\+?1[\s-]?)?\(?\d{3}\)?[\s-]\d{3}[\s-]\d{4}", line)
            if email:
                info["email"] = email.group(0)
            if phone:
                digits = re.sub(r"\D", "", phone.group(0))
                if len(digits) == 10:
                    digits = "1" + digits
                info["phone"] = f"+{digits[0]} ({digits[1:4]}) {digits[4:7]}-{digits[7:]}"
            location = line.split("|")[0].strip()
            if location:
                info["location"] = location
        if "linkedin.com/in/" in line.lower():
            info["linkedin"] = line.split("|")[0].strip()
        if "github.com/" in line.lower():
            github = re.search(r"github\.com/[A-Za-z0-9_.-]+", line, re.IGNORECASE)
            if github:
                info["github"] = github.group(0)
    return info


def line_text(entry):
    if isinstance(entry, dict):
        return entry.get("text", "")
    return entry


def line_links(entry):
    if isinstance(entry, dict):
        return entry.get("links", [])
    return []


def split_section_blocks(paragraphs):
    """Split resume paragraphs into section blocks by heading."""
    blocks = {}
    current = None
    for entry in paragraphs:
        line = line_text(entry)
        key = SECTION_ALIASES.get(line.upper())
        if key:
            current = key
            blocks[current] = []
            continue
        if current:
            blocks[current].append(entry)
    return blocks


def parse_summary(lines):
    plain_lines = [line_text(line) for line in lines]
    return normalize_text(" ".join(plain_lines)) if plain_lines else ""


def parse_skills(lines):
    def split_top_level_commas(text):
        items = []
        token = []
        depth = 0
        for ch in text:
            if ch == "(":
                depth += 1
            elif ch == ")" and depth > 0:
                depth -= 1
            if ch == "," and depth == 0:
                value = normalize_text("".join(token))
                if value:
                    items.append(value)
                token = []
                continue
            token.append(ch)
        value = normalize_text("".join(token))
        if value:
            items.append(value)
        return items

    categories = []
    for line in [line_text(line) for line in lines]:
        if ":" not in line:
            continue
        label, values = line.split(":", 1)
        skills = split_top_level_commas(values)
        if skills:
            categories.append({"category": normalize_text(label), "skills": skills})
    return categories


def is_experience_header(line):
    return bool(re.search(r"(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{4}\s*[–-]\s*(Present|\w+\s+\d{4})", line))


def parse_experience_header(line):
    """Parse a merged company/date/title line into structured fields."""
    date_match = re.search(
        r"(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{4}\s*[–-]\s*(Present|(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{4})",
        line,
    )
    if not date_match:
        return None

    left = normalize_text(line[: date_match.start()])
    date = normalize_text(date_match.group(0))
    right = normalize_text(line[date_match.end() :])

    role = right
    company = left
    if not role and "|" in left:
        left_parts = [p.strip() for p in left.split("|") if p.strip()]
        if len(left_parts) >= 2:
            company = " | ".join(left_parts[:-1])
            role = left_parts[-1]
    if not role:
        role = "Professional Experience"

    return {"company": company, "role": role, "date": date, "achievements": []}


def parse_experience(lines):
    experience = []
    current = None
    for line in [line_text(line) for line in lines]:
        if is_experience_header(line):
            parsed = parse_experience_header(line)
            if parsed:
                if current:
                    experience.append(current)
                current = parsed
                continue
        if current and line:
            current["achievements"].append(normalize_text(line))
    if current:
        experience.append(current)
    return experience


def find_best_url(item_text, links):
    normalized_item = normalize_text(item_text).lower()
    compact_item = re.sub(r"[^a-z0-9]+", "", normalized_item)
    for link in links:
        link_text = normalize_text(link.get("text", "")).lower()
        compact_link = re.sub(r"[^a-z0-9]+", "", link_text)
        if link_text and (
            link_text in normalized_item
            or normalized_item in link_text
            or (compact_link and compact_link in compact_item)
            or (compact_item and compact_item in compact_link)
        ):
            return link.get("url")
    github_match = re.search(r"github\.com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", normalized_item, re.IGNORECASE)
    if github_match:
        return f"https://{github_match.group(0)}"
    return None


def parse_certifications(lines):
    parsed = {"completed": [], "in_progress": [], "projects": []}
    current = None

    def parse_project_items(payload, links):
        payload = normalize_text(payload)
        if not payload:
            return []
        if "github.com/" in payload.lower():
            return [{"text": payload, "url": find_best_url(payload, links)}]
        return [
            {"text": normalize_text(item), "url": find_best_url(item, links)}
            for item in payload.split(",")
            if item.strip()
        ]

    for entry in lines:
        line = line_text(entry)
        links = line_links(entry)
        lowered = line.lower()
        if lowered.startswith("completed:"):
            current = "completed"
            payload = line.split(":", 1)[1]
        elif lowered.startswith("in progress:"):
            current = "in_progress"
            payload = line.split(":", 1)[1]
        elif lowered.startswith("projects:"):
            current = "projects"
            payload = line.split(":", 1)[1]
        else:
            payload = line
        if current:
            if current == "projects":
                items = parse_project_items(payload, links)
            else:
                items = [
                    {"text": normalize_text(item), "url": find_best_url(item, links)}
                    for item in re.split(r",\s*", payload)
                    if item.strip()
                ]
            parsed[current].extend(items)
    return parsed


def parse_education(lines):
    entries = []
    for line in [line_text(line) for line in lines]:
        parts = [normalize_text(part) for part in line.split("|") if part.strip()]
        if not parts:
            continue
        degree = parts[0]
        school = parts[1] if len(parts) > 1 else ""
        year = parts[2] if len(parts) > 2 else ""
        entries.append({"degree": degree, "school": school, "year": year})
    return entries


def parse_resume_content(paragraph_entries):
    """Parse paragraph-level data into structured resume sections."""
    if not paragraph_entries:
        return None

    paragraphs = [line_text(entry) for entry in paragraph_entries]
    sections = detect_header_info(paragraphs)
    blocks = split_section_blocks(paragraph_entries)
    sections["summary"] = parse_summary(blocks.get("summary", []))
    sections["skills"] = parse_skills(blocks.get("skills", []))
    sections["experience"] = parse_experience(blocks.get("experience", []))
    sections["certifications"] = parse_certifications(blocks.get("certifications", []))
    sections["education"] = parse_education(blocks.get("education", []))

    if sections.get("summary"):
        title_match = re.search(r"(Staff AI Engineer|AI Solutions Architect|Engineering Lead)", sections["summary"], re.IGNORECASE)
        if title_match:
            sections["title"] = title_match.group(0)
    return sections

def read_existing_html():
    """Read the existing index.html to preserve structure."""
    try:
        with open('index.html', 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return None


def safe(value):
    return html.escape(value or "", quote=True)


def render_experience_html(experience):
    items = []
    for job in experience:
        achievements = "\n".join(f'                        <li>{safe(item)}</li>' for item in job.get("achievements", []))
        item = (
            "                <div class=\"experience-item\">\n"
            "                    <div class=\"experience-header\">\n"
            f"                        <h3 class=\"experience-title\">{safe(job.get('role'))}</h3>\n"
            f"                        <span class=\"experience-company\">{safe(job.get('company'))}</span>\n"
            f"                        <span class=\"experience-date\">{safe(job.get('date'))}</span>\n"
            "                    </div>\n"
            "                    <ul class=\"experience-achievements\">\n"
            f"{achievements}\n"
            "                    </ul>\n"
            "                </div>"
        )
        items.append(item)
    return "\n\n".join(items)


def render_skills_html(skill_categories):
    categories = []
    for category in skill_categories:
        tags = "\n".join(f'                        <span class="skill-tag">{safe(tag)}</span>' for tag in category.get("skills", []))
        block = (
            "                <div class=\"skill-category\">\n"
            f"                    <h3 class=\"skill-category-title\">{safe(category.get('category'))}</h3>\n"
            "                    <div class=\"skill-tags\">\n"
            f"{tags}\n"
            "                    </div>\n"
            "                </div>"
        )
        categories.append(block)
    return "\n".join(categories)


def render_education_html(education):
    entries = []
    for item in education:
        school_line = safe(item.get("school"))
        if item.get("year"):
            school_line = f"{school_line} | {safe(item.get('year'))}" if school_line else safe(item.get("year"))
        entries.append(
            "                <div class=\"education-item\">\n"
            f"                    <h3 class=\"education-degree\">{safe(item.get('degree'))}</h3>\n"
            f"                    <p class=\"education-school\">{school_line}</p>\n"
            "                </div>"
        )
    return "\n".join(entries)


def render_certifications_html(certifications):
    def pills_html(items):
        rendered = []
        for item in items:
            if isinstance(item, dict):
                text = item.get("text", "")
                url = item.get("url")
            else:
                text = str(item)
                url = None

            if url:
                rendered.append(
                    f'                        <li class="cert-pill"><a class="cert-link" href="{safe(url)}" target="_blank" rel="noopener noreferrer">{safe(text)}</a></li>'
                )
            else:
                rendered.append(f'                        <li class="cert-pill">{safe(text)}</li>')
        return "\n".join(rendered)

    completed = pills_html(certifications.get("completed", []))
    in_progress = pills_html(certifications.get("in_progress", []))
    projects = pills_html(certifications.get("projects", []))

    return (
        "    <section id=\"certifications\" class=\"section\">\n"
        "        <div class=\"container\">\n"
        "            <h2 class=\"section-title\">Certifications &amp; Learning</h2>\n"
        "            <div class=\"certifications-grid\">\n"
        "                <article class=\"cert-card\">\n"
        "                    <h3 class=\"cert-card-title\">Completed</h3>\n"
        "                    <ul class=\"cert-pill-list\">\n"
        f"{completed}\n"
        "                    </ul>\n"
        "                </article>\n"
        "                <article class=\"cert-card\">\n"
        "                    <h3 class=\"cert-card-title\">In Progress</h3>\n"
        "                    <ul class=\"cert-pill-list\">\n"
        f"{in_progress}\n"
        "                    </ul>\n"
        "                </article>\n"
        "                <article class=\"cert-card cert-card-projects\">\n"
        "                    <h3 class=\"cert-card-title\">Projects</h3>\n"
        "                    <ul class=\"cert-pill-list cert-pill-list-projects\">\n"
        f"{projects}\n"
        "                    </ul>\n"
        "                </article>\n"
        "            </div>\n"
        "        </div>\n"
        "    </section>\n"
    )

def update_html_content(html_content, sections):
    """Update specific sections in the existing HTML."""
    if not html_content:
        return None
    
    # Update title in <title> tag
    html_content = re.sub(
        r'<title>.*?</title>',
        f'<title>{safe(sections["name"])} • {safe(sections["title"])}</title>',
        html_content
    )
    
    # Update meta description
    html_content = re.sub(
        r'<meta name="description" content="[^"]*">',
        f'<meta name="description" content="{safe(sections["title"])} - Portfolio of {safe(sections["name"])}">',
        html_content
    )
    
    # Update hero subtitle
    html_content = re.sub(
        r'<p class="hero-subtitle">.*?</p>',
        f'<p class="hero-subtitle">{safe(sections["title"])}</p>',
        html_content
    )
    
    # Update professional summary
    if sections.get('summary'):
        html_content = re.sub(
            r'(<p class="about-text">\s*)(.*?)(\s*</p>)',
            f'\\1{safe(sections["summary"])}\\3',
            html_content,
            flags=re.DOTALL
        )

    # Ensure certifications tab exists in header navigation.
    if 'href="#certifications"' not in html_content:
        html_content = re.sub(
            r'(<li><a href="#skills">Skills</a></li>)',
            r'\1\n                <li><a href="#certifications">Certifications</a></li>',
            html_content,
            count=1,
        )

    # Keep copyright year in sync.
    current_year = datetime.now().year
    html_content = re.sub(
        r'&copy;\s*\d{4}\s+Nitinkumar Patel',
        f'&copy; {current_year} Nitinkumar Patel',
        html_content,
        count=1,
    )

    if sections.get("experience"):
        html_content = re.sub(
            r'<section id="experience" class="section section-alt">.*?</section>',
            (
                "    <section id=\"experience\" class=\"section section-alt\">\n"
                "        <div class=\"container\">\n"
                "            <h2 class=\"section-title\">Professional Experience</h2>\n"
                "            <div class=\"experience-list\">\n"
                f"{render_experience_html(sections['experience'])}\n"
                "            </div>\n"
                "        </div>\n"
                "    </section>"
            ),
            html_content,
            flags=re.DOTALL,
            count=1,
        )

    if sections.get("skills"):
        html_content = re.sub(
            r'<section id="skills" class="section">.*?</section>',
            (
                "    <section id=\"skills\" class=\"section\">\n"
                "        <div class=\"container\">\n"
                "            <h2 class=\"section-title\">Technical Skills</h2>\n"
                "            <div class=\"skills-grid\">\n"
                f"{render_skills_html(sections['skills'])}\n"
                "            </div>\n"
                "        </div>\n"
                "    </section>"
            ),
            html_content,
            flags=re.DOTALL,
            count=1,
        )

    if sections.get("education"):
        html_content = re.sub(
            r'<section id="education" class="section section-alt">.*?</section>',
            (
                "    <section id=\"education\" class=\"section section-alt\">\n"
                "        <div class=\"container\">\n"
                "            <h2 class=\"section-title\">Education</h2>\n"
                "            <div class=\"education-list\">\n"
                f"{render_education_html(sections['education'])}\n"
                "            </div>\n"
                "        </div>\n"
                "    </section>"
            ),
            html_content,
            flags=re.DOTALL,
            count=1,
        )

    if sections.get("certifications"):
        cert_block = render_certifications_html(sections["certifications"])
        cert_section_pattern = r'<section id="certifications" class="section">.*?</section>'
        if re.search(cert_section_pattern, html_content, re.DOTALL):
            html_content = re.sub(cert_section_pattern, cert_block.strip(), html_content, flags=re.DOTALL, count=1)
        else:
            html_content = re.sub(
                r'(\s*<!-- Education Section -->)',
                f"\n{cert_block}\n\\1",
                html_content,
                count=1,
            )

    # Keep repeated runs idempotent by removing accidental duplicate section comments.
    html_content = re.sub(
        r'(\s*<!-- (Experience|Skills|Certifications|Education) Section -->)\s*\1+',
        r"\1",
        html_content,
        flags=re.DOTALL,
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
                <li><a href="#certifications">Certifications</a></li>
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
    docx_path = 'Resume.docx'
    output_path = 'index.html'
    
    print(f"Reading resume from: {docx_path}")
    paragraphs = extract_docx_paragraphs_with_links(docx_path)

    if not paragraphs:
        print("Error: Could not extract text from document")
        return
    
    print("Parsing resume content...")
    sections = parse_resume_content(paragraphs)
    
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
    print("\nUpdated sections:")
    print(f"  - Title: {sections.get('title', 'N/A')}")
    print(f"  - Summary: {'Updated' if sections.get('summary') else 'Not found'}")
    print(f"  - Experience entries: {len(sections.get('experience', []))}")
    print(f"  - Skills categories: {len(sections.get('skills', []))}")
    certs = sections.get("certifications", {})
    print(
        f"  - Certifications/Learning: completed={len(certs.get('completed', []))}, "
        f"in_progress={len(certs.get('in_progress', []))}, projects={len(certs.get('projects', []))}"
    )
    print(f"  - Education entries: {len(sections.get('education', []))}")

if __name__ == '__main__':
    main()

