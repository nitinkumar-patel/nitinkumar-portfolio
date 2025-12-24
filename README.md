# Nitinkumar Patel - Portfolio Website

A modern, responsive portfolio website showcasing my professional experience, skills, and achievements as an Engineering Lead & AI Architect.

## 🚀 Features

- **Modern Design**: Clean, professional design with smooth animations
- **Fully Responsive**: Works seamlessly on desktop, tablet, and mobile devices
- **Fast Loading**: Optimized for performance
- **SEO Friendly**: Proper meta tags and semantic HTML
- **Accessible**: Built with accessibility best practices
- **PDF Export**: One-click PDF export with automatic timestamped filename
- **Smooth Navigation**: Click on name in navbar to scroll to top
- **Last Modified Date**: Automatically displays last modified date in footer

## 📋 Sections

- **Professional Summary**: Overview of my experience and expertise
- **Professional Experience**: Detailed work history with achievements
- **Technical Skills**: Comprehensive list of technologies and tools
- **Education**: Academic background
- **Contact**: Ways to get in touch

## 🛠️ Technologies Used

- HTML5
- CSS3 (with CSS Grid and Flexbox)
- JavaScript (Vanilla JS)
- Google Fonts (Inter)
- html2pdf.js (for PDF generation)

## 📦 Setup

1. Clone the repository:
```bash
git clone https://github.com/nitinkumar-patel/nitinkumar-portfolio.git
cd nitinkumar-portfolio
```

2. Open `index.html` in your web browser, or use a local server:
```bash
# Using Python
python3 -m http.server 8000

# Using Node.js (if you have http-server installed)
npx http-server
```

3. Visit `http://localhost:8000` in your browser

## 🌐 GitHub Pages Deployment

This website is configured to work with GitHub Pages. To deploy:

1. Push this repository to GitHub
2. Go to your repository settings
3. Navigate to "Pages" section
4. Select the branch (usually `main` or `master`)
5. Select the folder (usually `/ (root)`)
6. Click Save
7. Your site will be available at `https://[your-username].github.io/nitinkumar-portfolio`

## 🔄 Dynamic Generation from Word Document

This portfolio can be automatically generated from your Word resume document:

1. Place your `.docx` resume file in the project root (e.g., `Nitinkumar_Patel_Engineering_Lead_251223.docx`)
2. Run the generation script:
```bash
python3 generate_portfolio.py
```

The script will:
- Extract text from the Word document
- Update the Professional Summary section
- Update the title and meta tags
- Preserve the existing HTML structure and styling

**Note**: Currently, the script updates the summary and title. For full parsing of experience, skills, and education sections, you may need to manually update those or enhance the parser.

## 📝 Customization

To customize this portfolio for your own use:

1. Update personal information in `index.html` (or use the generation script)
2. Modify colors and styles in `styles.css` (CSS variables at the top)
3. Add or remove sections as needed
4. Update the contact information
5. Update the PDF filename format in `script.js` (line 45) if needed

## 📄 License

This project is open source and available under the MIT License.

## 📧 Contact

- **Email**: npatel121.py@gmail.com
- **Phone**: +1 (484) 447-7008
- **LinkedIn**: [linkedin.com/in/nitinkumar-patel](https://www.linkedin.com/in/nitinkumar-patel)
- **GitHub**: [github.com/nitinkumar-patel](https://github.com/nitinkumar-patel)

---

Built with ❤️ by Nitinkumar Patel
