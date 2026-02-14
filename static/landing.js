// Smooth scroll animation observer
const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -100px 0px'
};

const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.classList.add('visible');
        }
    });
}, observerOptions);

// Observe all sections for scroll animations
document.addEventListener('DOMContentLoaded', () => {
    const animateElements = document.querySelectorAll('.info-card, .stat-card, .feature-card, .team-card');
    animateElements.forEach(el => {
        el.setAttribute('data-animate', '');
        observer.observe(el);
    });

    // Add parallax effect to hero section
    window.addEventListener('scroll', () => {
        const scrolled = window.pageYOffset;
        const hero = document.querySelector('.hero-content');
        if (hero) {
            hero.style.transform = `translateY(${scrolled * 0.3}px)`;
            hero.style.opacity = 1 - (scrolled * 0.002);
        }
    });

    // Add hover effect to CTA button
    const ctaButton = document.querySelector('.cta-button');
    if (ctaButton) {
        ctaButton.addEventListener('mouseenter', () => {
            ctaButton.style.transform = 'translateY(-3px) scale(1.02)';
        });
        ctaButton.addEventListener('mouseleave', () => {
            ctaButton.style.transform = 'translateY(0) scale(1)';
        });
    }

    // Stagger animation for cards
    const cards = document.querySelectorAll('.info-card, .feature-card, .team-card');
    cards.forEach((card, index) => {
        card.style.animationDelay = `${index * 0.1}s`;
    });
});

// Add smooth scrolling for anchor links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

// Animate stats on scroll
const animateStats = () => {
    const stats = document.querySelectorAll('.stat-number');
    stats.forEach(stat => {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const text = stat.textContent;
                    const number = parseInt(text);
                    if (!isNaN(number)) {
                        let current = 0;
                        const increment = number / 50;
                        const timer = setInterval(() => {
                            current += increment;
                            if (current >= number) {
                                stat.textContent = text;
                                clearInterval(timer);
                            } else {
                                stat.textContent = Math.floor(current) + '%';
                            }
                        }, 30);
                    }
                    observer.unobserve(entry.target);
                }
            });
        }, { threshold: 0.5 });
        observer.observe(stat);
    });
};

animateStats();
