/* main.js - PMB UNJ Interactions */

document.addEventListener('DOMContentLoaded', () => {
    // 1. Mobile Navigation Toggle
    const navToggle = document.getElementById('nav-toggle');
    const navLinks = document.getElementById('nav-links');

    if (navToggle && navLinks) {
        navToggle.addEventListener('click', () => {
            navLinks.style.display = navLinks.style.display === 'flex' ? 'none' : 'flex';
            if (navLinks.style.display === 'flex') {
                navLinks.style.flexDirection = 'column';
                navLinks.style.position = 'absolute';
                navLinks.style.top = '64px';
                navLinks.style.left = '0';
                navLinks.style.width = '100%';
                navLinks.style.backgroundColor = 'white';
                navLinks.style.padding = '24px';
                navLinks.style.borderBottom = '1px solid var(--color-fog-border)';
                navLinks.style.boxShadow = '0 4px 6px -1px rgba(0, 0, 0, 0.1)';
            }
        });
    }

    // 2. Auto-hide Messages after 5 seconds
    const messages = document.querySelectorAll('.alert');
    if (messages.length > 0) {
        setTimeout(() => {
            messages.forEach(msg => {
                msg.style.opacity = '0';
                msg.style.transform = 'translateX(100%)';
                msg.style.transition = 'all 0.3s ease';
                setTimeout(() => msg.remove(), 300);
            });
        }, 5000);
    }

    // 3. Smooth Scroll for Anchor Links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            const targetId = this.getAttribute('href');
            if (targetId === '#') return;
            
            const targetElement = document.querySelector(targetId);
            if (targetElement) {
                e.preventDefault();
                // Close mobile nav if open
                if (window.innerWidth <= 768 && navLinks) {
                    navLinks.style.display = 'none';
                }
                
                window.scrollTo({
                    top: targetElement.offsetTop - 64, // Offset for sticky nav
                    behavior: 'smooth'
                });
            }
        });
    });

    // 4. File Upload Preview/Validation (for upload.html)
    const fileInput = document.getElementById('id_file_dokumen');
    if (fileInput) {
        fileInput.addEventListener('change', function() {
            if (this.files && this.files[0]) {
                const file = this.files[0];
                const maxSize = 2 * 1024 * 1024; // 2MB
                
                // Remove existing warning
                const existingWarning = this.parentElement.querySelector('.text-error');
                if (existingWarning) existingWarning.remove();

                if (file.size > maxSize) {
                    const warning = document.createElement('p');
                    warning.className = 'text-error mt-8';
                    warning.textContent = `File terlalu besar (${(file.size / 1024 / 1024).toFixed(1)}MB). Maksimal 2MB.`;
                    this.parentElement.appendChild(warning);
                    this.value = ''; // Clear input
                }
            }
        });
    }
});

// Global Function for FAQ Accordion
function toggleFaq(button) {
    const item = button.parentElement;
    
    // Close others
    const allItems = document.querySelectorAll('.faq-item');
    allItems.forEach(el => {
        if (el !== item) el.classList.remove('active');
    });

    // Toggle current
    item.classList.toggle('active');
}
