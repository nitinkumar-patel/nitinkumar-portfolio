// Mobile Navigation Toggle
const navToggle = document.querySelector('.nav-toggle');
const navMenu = document.querySelector('.nav-menu');

navToggle.addEventListener('click', () => {
    navMenu.classList.toggle('active');
    navToggle.classList.toggle('active');
});

// Close mobile menu when clicking on a link
document.querySelectorAll('.nav-menu a').forEach(link => {
    link.addEventListener('click', () => {
        navMenu.classList.remove('active');
        navToggle.classList.remove('active');
    });
});

// Smooth scroll for navigation links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        const hash = this.getAttribute('href');
        if (!hash || hash === '#') {
            return;
        }
        e.preventDefault();
        const target = document.querySelector(hash);
        if (target) {
            const offsetTop = target.offsetTop - 80;
            window.scrollTo({
                top: offsetTop,
                behavior: 'smooth'
            });

            // Keep URL hash in sync with active section navigation.
            if (window.location.hash !== hash) {
                history.pushState(null, '', hash);
            }
        }
    });
});

// Export to PDF (best fidelity via browser print engine)
const exportPdfBtn = document.querySelector('#export-pdf-btn');
if (exportPdfBtn) {
    exportPdfBtn.addEventListener('click', (e) => {
        e.preventDefault();
        // Ensure mobile menu doesn't overlap print layout.
        navMenu.classList.remove('active');
        navToggle.classList.remove('active');

        // Let the browser print engine generate PDF (best layout fidelity).
        // In the dialog choose: Destination = Save as PDF.
        window.scrollTo({ top: 0, behavior: 'auto' });
        window.print();
    });
}

// Footer "Last modified" text using document.lastModified
const lastModifiedEl = document.querySelector('#last-modified');
if (lastModifiedEl) {
    const modified = new Date(document.lastModified);
    if (!isNaN(modified.getTime())) {
        const opts = { year: 'numeric', month: 'short', day: 'numeric' };
        const formatted = modified.toLocaleDateString(undefined, opts);
        lastModifiedEl.textContent = ` • Last modified: ${formatted}`;
    }
}

// Navbar background on scroll
const navbar = document.querySelector('.navbar');
let lastScroll = 0;

window.addEventListener('scroll', () => {
    const currentScroll = window.pageYOffset;
    
    if (currentScroll > 100) {
        navbar.style.boxShadow = '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)';
    } else {
        navbar.style.boxShadow = 'none';
    }
    
    lastScroll = currentScroll;
});

// Intersection Observer for fade-in animations
const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px'
};

const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.style.opacity = '1';
            entry.target.style.transform = 'translateY(0)';
        }
    });
}, observerOptions);

// Observe all sections
document.querySelectorAll('.section').forEach(section => {
    section.style.opacity = '0';
    section.style.transform = 'translateY(30px)';
    section.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
    observer.observe(section);
});

// Add active state to navigation links based on scroll position
const sections = document.querySelectorAll('.section');
const navLinks = document.querySelectorAll('.nav-menu a');

window.addEventListener('scroll', () => {
    let current = '';
    
    sections.forEach(section => {
        const sectionTop = section.offsetTop;
        const sectionHeight = section.clientHeight;
        if (window.pageYOffset >= sectionTop - 100) {
            current = section.getAttribute('id');
        }
    });

    navLinks.forEach(link => {
        link.classList.remove('active');
        if (link.getAttribute('href') === `#${current}`) {
            link.classList.add('active');
        }
    });
});

