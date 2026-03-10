// 🌿 Basic Website Functionality
document.addEventListener('DOMContentLoaded', () => {
    // Hide loading screen
    const loadingScreen = document.getElementById('loading-screen');
    if (loadingScreen) {
        loadingScreen.style.display = 'none';
    }

    // Initialize basic functionality
    initBasicFunctionality();
});

// 🌿 Initialize basic functionality
function initBasicFunctionality() {
    // Hamburger menu
    const hamburger = document.getElementById('hamburger');
    const nav = document.getElementById('nav');

    if (hamburger && nav) {
        hamburger.addEventListener('click', function () {
            hamburger.classList.toggle('active');
            nav.classList.toggle('active');
        });

        // Close nav on link click (mobile)
        document.querySelectorAll('.nav-link').forEach(link => {
            link.addEventListener('click', () => {
                if (window.innerWidth <= 768) {
                    hamburger.classList.remove('active');
                    nav.classList.remove('active');
                }
            });
        });
    }

    // Smooth scrolling
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({ behavior: 'smooth' });
            }
        });
    });

    // Scroll to top button
    const scrollBtn = document.createElement('button');
    scrollBtn.innerHTML = '<i class="fa-solid fa-arrow-up"></i>';
    scrollBtn.className = "scroll-to-top";
    document.body.appendChild(scrollBtn);

    scrollBtn.addEventListener('click', () => {
        window.scrollTo({ top: 0, behavior: 'smooth' });
    });

    // Show/hide scroll button
    window.addEventListener('scroll', () => {
        if (window.scrollY > 300) {
            scrollBtn.style.display = 'block';
        } else {
            scrollBtn.style.display = 'none';
        }
    });

    // Navbar scroll effect
    const header = document.getElementById('header');
    if (header) {
        window.addEventListener('scroll', () => {
            if (window.scrollY > 60) {
                header.classList.add('scrolled');
            } else {
                header.classList.remove('scrolled');
            }
        });
    }
}

// 🌿 Loading Screen Animation
window.addEventListener('load', () => {
    const loadingScreen = document.getElementById('loading-screen');

    if (typeof gsap !== 'undefined') {
        gsap.to(loadingScreen, {
            opacity: 0,
            duration: 1,
            ease: "power2.out",
            onComplete: () => {
                loadingScreen.style.display = 'none';
                initAnimations();
            }
        });
    } else {
        // Fallback
        if (loadingScreen) {
            loadingScreen.style.display = 'none';
        }
        initAnimations();
    }
});

// 🌿 Initialize all animations
function initAnimations() {
    if (typeof gsap === 'undefined') {
        console.warn('GSAP not available, skipping animations');
        return;
    }

    // Header animations
    animateHeader();

    // Hero section animations
    animateHero();

    // Floating leaves animation
    animateFloatingLeaves();

    // Product cards animations
    animateProductCards();

    // About section animations
    animateAboutSection();

    // Contact section animations
    animateContactSection();

    // Footer animation
    animateFooter();

    // Scroll to top button
    initScrollToTop();

    // Smooth scrolling
    initSmoothScrolling();

    // Navbar scroll effect
    initNavbarScroll();
}

// 🌿 Header Animation - Fixed to prevent tilting
function animateHeader() {
    const header = document.getElementById('header');
    const logo = document.getElementById('logo');
    const navLinks = document.querySelectorAll('.nav-link');

    // Header entrance animation - only animate opacity and y position
    gsap.fromTo(header,
        { y: -100, opacity: 0 },
        { y: 0, opacity: 1, duration: 1, ease: "power2.out" }
    );

    // Logo animation - use transformOrigin to prevent tilting
    gsap.fromTo(logo,
        { scale: 0.8, opacity: 0, transformOrigin: "left center" },
        { scale: 1, opacity: 1, duration: 0.8, delay: 0.2, ease: "back.out(1.7)" }
    );

    // Navigation links stagger animation - only animate y and opacity
    gsap.fromTo(navLinks,
        { y: -20, opacity: 0 },
        {
            y: 0,
            opacity: 1,
            duration: 0.6,
            stagger: 0.1,
            delay: 0.4,
            ease: "power2.out"
        }
    );
}

// 🌿 Hero Section Animation
function animateHero() {
    const heroTitle = document.getElementById('hero-title');
    const heroSubtitle = document.getElementById('hero-subtitle');
    const heroBtn = document.getElementById('hero-btn');

    // Hero title animation
    gsap.fromTo(heroTitle,
        { y: 50, opacity: 0 },
        { y: 0, opacity: 1, duration: 1, ease: "power2.out" }
    );

    // Hero subtitle animation
    gsap.fromTo(heroSubtitle,
        { y: 30, opacity: 0 },
        { y: 0, opacity: 1, duration: 1, delay: 0.3, ease: "power2.out" }
    );

    // Hero button animation
    gsap.fromTo(heroBtn,
        { y: 20, opacity: 0, scale: 0.8 },
        { y: 0, opacity: 1, scale: 1, duration: 0.8, delay: 0.6, ease: "back.out(1.7)" }
    );

    // Button hover effect
    heroBtn.addEventListener('mouseenter', () => {
        gsap.to(heroBtn, { scale: 1.05, duration: 0.3, ease: "power2.out" });
    });

    heroBtn.addEventListener('mouseleave', () => {
        gsap.to(heroBtn, { scale: 1, duration: 0.3, ease: "power2.out" });
    });
}

// 🌿 Floating Leaves Animation
function animateFloatingLeaves() {
    const leaves = document.querySelectorAll('.floating-leaves i');

    leaves.forEach((leaf, index) => {
        gsap.to(leaf, {
            y: -20,
            rotation: 360,
            duration: 3 + index,
            repeat: -1,
            yoyo: true,
            ease: "power1.inOut",
            delay: index * 0.5
        });
    });
}

// 🌿 Product Cards Animation
function animateProductCards() {
    const productCards = document.querySelectorAll('.product-card');

    productCards.forEach((card, index) => {
        // Initial state
        gsap.set(card, { y: 50, opacity: 0 });

        // Scroll trigger animation
        ScrollTrigger.create({
            trigger: card,
            start: "top 85%",
            end: "bottom 15%",
            onEnter: () => {
                gsap.to(card, {
                    y: 0,
                    opacity: 1,
                    duration: 0.8,
                    delay: index * 0.1,
                    ease: "power2.out"
                });
            }
        });

        // Hover animations
        card.addEventListener('mouseenter', () => {
            gsap.to(card, {
                y: -10,
                duration: 0.3,
                ease: "power2.out"
            });
        });

        card.addEventListener('mouseleave', () => {
            gsap.to(card, {
                y: 0,
                duration: 0.3,
                ease: "power2.out"
            });
        });
    });
}

// 🌿 About Section Animation
function animateAboutSection() {
    const aboutTitle = document.getElementById('about-title');
    const aboutDescription = document.getElementById('about-description');
    const features = document.querySelectorAll('.feature');

    // Title animation
    ScrollTrigger.create({
        trigger: aboutTitle,
        start: "top 80%",
        onEnter: () => {
            gsap.fromTo(aboutTitle,
                { y: 30, opacity: 0 },
                { y: 0, opacity: 1, duration: 0.8, ease: "power2.out" }
            );
        }
    });

    // Description animation
    ScrollTrigger.create({
        trigger: aboutDescription,
        start: "top 80%",
        onEnter: () => {
            gsap.fromTo(aboutDescription,
                { y: 20, opacity: 0 },
                { y: 0, opacity: 1, duration: 0.8, delay: 0.2, ease: "power2.out" }
            );
        }
    });

    // Features stagger animation
    ScrollTrigger.create({
        trigger: features[0],
        start: "top 80%",
        onEnter: () => {
            gsap.fromTo(features,
                { y: 30, opacity: 0 },
                {
                    y: 0,
                    opacity: 1,
                    duration: 0.8,
                    stagger: 0.2,
                    ease: "power2.out"
                }
            );
        }
    });
}

// 🌿 Contact Section Animation
function animateContactSection() {
    const contactTitle = document.getElementById('contact-title');
    const contactText = document.getElementById('contact-text');
    const contactBtn = document.getElementById('contact-btn');

    // Title animation
    ScrollTrigger.create({
        trigger: contactTitle,
        start: "top 80%",
        onEnter: () => {
            gsap.fromTo(contactTitle,
                { y: 30, opacity: 0 },
                { y: 0, opacity: 1, duration: 0.8, ease: "power2.out" }
            );
        }
    });

    // Text animation
    ScrollTrigger.create({
        trigger: contactText,
        start: "top 80%",
        onEnter: () => {
            gsap.fromTo(contactText,
                { y: 20, opacity: 0 },
                { y: 0, opacity: 1, duration: 0.8, delay: 0.2, ease: "power2.out" }
            );
        }
    });

    // Button animation
    ScrollTrigger.create({
        trigger: contactBtn,
        start: "top 80%",
        onEnter: () => {
            gsap.fromTo(contactBtn,
                { y: 20, opacity: 0, scale: 0.8 },
                { y: 0, opacity: 1, scale: 1, duration: 0.8, delay: 0.4, ease: "back.out(1.7)" }
            );
        }
    });

    // Button hover effect
    contactBtn.addEventListener('mouseenter', () => {
        gsap.to(contactBtn, { scale: 1.05, duration: 0.3, ease: "power2.out" });
    });

    contactBtn.addEventListener('mouseleave', () => {
        gsap.to(contactBtn, { scale: 1, duration: 0.3, ease: "power2.out" });
    });
}

// 🌿 Footer Animation
function animateFooter() {
    const footer = document.getElementById('footer');

    ScrollTrigger.create({
        trigger: footer,
        start: "top 90%",
        onEnter: () => {
            gsap.fromTo(footer,
                { y: 30, opacity: 0 },
                { y: 0, opacity: 1, duration: 0.8, ease: "power2.out" }
            );
        }
    });
}

// 🌿 Scroll to Top Button
function initScrollToTop() {
    const scrollBtn = document.createElement('button');
    scrollBtn.innerHTML = '<i class="fa-solid fa-arrow-up"></i>';
    scrollBtn.className = "scroll-to-top";
    document.body.appendChild(scrollBtn);

    // Show/hide button based on scroll
    ScrollTrigger.create({
        start: "top top",
        end: 99999,
        onUpdate: (self) => {
            if (self.progress > 0.1) {
                gsap.to(scrollBtn, { opacity: 1, duration: 0.3 });
            } else {
                gsap.to(scrollBtn, { opacity: 0, duration: 0.3 });
            }
        }
    });

    // Scroll to top functionality
    scrollBtn.addEventListener('click', () => {
        gsap.to(window, {
            scrollTo: { y: 0 },
            duration: 1.5,
            ease: "power2.inOut"
        });
    });

    // Button hover effect
    scrollBtn.addEventListener('mouseenter', () => {
        gsap.to(scrollBtn, { scale: 1.1, duration: 0.3 });
    });

    scrollBtn.addEventListener('mouseleave', () => {
        gsap.to(scrollBtn, { scale: 1, duration: 0.3 });
    });
}

// 🌿 Smooth Scrolling
function initSmoothScrolling() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                gsap.to(window, {
                    scrollTo: { y: target, offsetY: 80 },
                    duration: 1.5,
                    ease: "power2.inOut"
                });
            }
        });
    });
}

// 🌿 Navbar Scroll Effect
function initNavbarScroll() {
    const header = document.getElementById('header');

    ScrollTrigger.create({
        start: "top top",
        end: 99999,
        onUpdate: (self) => {
            if (self.progress > 0.05) {
                header.classList.add('scrolled');
            } else {
                header.classList.remove('scrolled');
            }
        }
    });
}

// 🌿 Hamburger Menu Animation
document.addEventListener('DOMContentLoaded', () => {
    const hamburger = document.getElementById('hamburger');
    const nav = document.getElementById('nav');

    hamburger.addEventListener('click', function () {
        hamburger.classList.toggle('active');
        nav.classList.toggle('active');

        if (nav.classList.contains('active')) {
            gsap.fromTo(nav.querySelectorAll('.nav-link'),
                { y: -20, opacity: 0 },
                { y: 0, opacity: 1, duration: 0.5, stagger: 0.1, ease: "power2.out" }
            );
        }
    });

    // Close nav on link click (mobile)
    document.querySelectorAll('.nav-link').forEach(link => {
        link.addEventListener('click', () => {
            if (window.innerWidth <= 768) {
                hamburger.classList.remove('active');
                nav.classList.remove('active');
            }
        });
    });
});

// 🌿 Mouse Movement Effect for Hero
document.addEventListener('mousemove', (e) => {
    if (typeof gsap === 'undefined') return;
    const mouseX = e.clientX / window.innerWidth;
    const mouseY = e.clientY / window.innerHeight;

    gsap.to('.hero-visual img', {
        x: mouseX * 10,
        y: mouseY * 10,
        duration: 1,
        ease: "power2.out"
    });
});

// 🌿 Stagger Animation for Product Images
function animateProductImages() {
    const productImages = document.querySelectorAll('.product-image');

    productImages.forEach((img, index) => {
        gsap.fromTo(img,
            { scale: 1.2, opacity: 0 },
            {
                scale: 1,
                opacity: 1,
                duration: 0.8,
                delay: index * 0.2,
                ease: "power2.out"
            }
        );
    });
}

// 🌿 Call product image animation when products load
window.addEventListener('load', () => {
    setTimeout(animateProductImages, 2000);
});

// 🌿 Text Reveal Animation
const textReveal = (element) => {
    const text = element.textContent;
    element.textContent = '';

    for (let i = 0; i < text.length; i++) {
        const span = document.createElement('span');
        span.textContent = text[i];
        span.style.opacity = '0';
        element.appendChild(span);

        gsap.to(span, {
            opacity: 1,
            duration: 0.05,
            delay: i * 0.05,
            ease: "power2.out"
        });
    }
};

// 🌿 Text animations removed for simplicity
document.addEventListener('DOMContentLoaded', () => {
    // No text reveal needed
});

// 🌿 Performance optimization
window.addEventListener('scroll', () => {
    // Throttle scroll events for better performance
    if (!window.scrollTimeout) {
        window.scrollTimeout = setTimeout(() => {
            window.scrollTimeout = null;
        }, 16);
    }
});

// 🌿 Cleanup function for ScrollTrigger
window.addEventListener('beforeunload', () => {
    if (typeof ScrollTrigger !== 'undefined') {
        ScrollTrigger.getAll().forEach(trigger => trigger.kill());
    }
});

// 🌿 Basic functionality for when GSAP is not available
if (typeof gsap === 'undefined') {
    // Simple scroll to top functionality
    const scrollBtn = document.createElement('button');
    scrollBtn.innerHTML = '<i class="fa-solid fa-arrow-up"></i>';
    scrollBtn.className = "scroll-to-top";
    document.body.appendChild(scrollBtn);

    scrollBtn.addEventListener('click', () => {
        window.scrollTo({ top: 0, behavior: 'smooth' });
    });

    // Show/hide scroll button
    window.addEventListener('scroll', () => {
        if (window.scrollY > 300) {
            scrollBtn.style.display = 'block';
        } else {
            scrollBtn.style.display = 'none';
        }
    });

    // Simple smooth scrolling
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({ behavior: 'smooth' });
            }
        });
    });
}
