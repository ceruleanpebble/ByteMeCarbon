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

// ===== Authentication Modal =====
const authModal = document.getElementById('authModal');
const getStartedBtn = document.getElementById('getStartedBtn');
const closeModal = document.querySelector('.auth-close');
const loginForm = document.getElementById('loginForm');
const signupForm = document.getElementById('signupForm');
const showSignupLink = document.getElementById('showSignup');
const showLoginLink = document.getElementById('showLogin');
const loginFormElement = document.getElementById('loginFormElement');
const signupFormElement = document.getElementById('signupFormElement');

// Open modal
getStartedBtn.addEventListener('click', (e) => {
    e.preventDefault();
    authModal.classList.add('active');
});

// Close modal
closeModal.addEventListener('click', () => {
    authModal.classList.remove('active');
});

// Close modal on outside click
authModal.addEventListener('click', (e) => {
    if (e.target === authModal) {
        authModal.classList.remove('active');
    }
});

// Switch to signup
showSignupLink.addEventListener('click', (e) => {
    e.preventDefault();
    loginForm.classList.remove('active');
    signupForm.classList.add('active');
    clearErrors();
});

// Switch to login
showLoginLink.addEventListener('click', (e) => {
    e.preventDefault();
    signupForm.classList.remove('active');
    loginForm.classList.add('active');
    clearErrors();
});

// Clear error messages
function clearErrors() {
    document.getElementById('loginError').classList.remove('active');
    document.getElementById('signupError').classList.remove('active');
}

function showError(elementId, message) {
    const errorEl = document.getElementById(elementId);
    errorEl.textContent = message;
    errorEl.classList.add('active');
}

// Handle login
loginFormElement.addEventListener('submit', async (e) => {
    e.preventDefault();
    clearErrors();
    
    const email = document.getElementById('loginEmail').value;
    const password = document.getElementById('loginPassword').value;
    
    try {
        const response = await fetch('/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ email, password }),
        });
        
        const data = await response.json();
        
        if (response.ok) {
            // Redirect to dashboard
            window.location.href = '/dashboard';
        } else {
            showError('loginError', data.error || 'Login failed');
        }
    } catch (error) {
        showError('loginError', 'Network error. Please try again.');
    }
});

// Handle signup
signupFormElement.addEventListener('submit', async (e) => {
    e.preventDefault();
    clearErrors();
    
    const email = document.getElementById('signupEmail').value;
    const password = document.getElementById('signupPassword').value;
    const passwordConfirm = document.getElementById('signupPasswordConfirm').value;
    
    // Validate passwords match
    if (password !== passwordConfirm) {
        showError('signupError', 'Passwords do not match');
        return;
    }
    
    // Validate password length
    if (password.length < 6) {
        showError('signupError', 'Password must be at least 6 characters');
        return;
    }
    
    try {
        const response = await fetch('/signup', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ email, password }),
        });
        
        const data = await response.json();
        
        if (response.ok) {
            // Redirect to dashboard
            window.location.href = '/dashboard';
        } else {
            showError('signupError', data.error || 'Signup failed');
        }
    } catch (error) {
        showError('signupError', 'Network error. Please try again.');
    }
});

