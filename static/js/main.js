document.addEventListener('DOMContentLoaded', function() {
    // Function to switch tabs
    function openTab(evt, tabName) {
        // Hide all tab content
        const tabContents = document.getElementsByClassName('tab-content');
        for (let i = 0; i < tabContents.length; i++) {
            tabContents[i].style.display = 'none';
        }

        // Remove active class from all tab links
        const tabLinks = document.getElementsByClassName('tab-link');
        for (let i = 0; i < tabLinks.length; i++) {
            tabLinks[i].className = tabLinks[i].className.replace(' active', '');
        }

        // Show the current tab and add active class to the button
        document.getElementById(tabName).style.display = 'block';
        evt.currentTarget.className += ' active';
    }

    // Set default tab to open
    const academicTab = document.getElementById('academic-tab');
    if (academicTab) {
        academicTab.click();
    }

    // Expose the function globally
    window.openTab = openTab;

    // Create particles background
    createParticles();

    // Add floating elements
    addFloatingElements();

    // Initialize scroll to top button
    initScrollToTop();

    // Add entrance animations for cards
    animateOnScroll();

    // Add typing effect to hero title
    if (document.querySelector('.hero h1')) {
        const text = document.querySelector('.hero h1').textContent;
        document.querySelector('.hero h1').innerHTML = '';
        typeText(document.querySelector('.hero h1'), text, 0, 100);
    }
});

// Function to create particles
function createParticles() {
    const bgAnimation = document.createElement('div');
    bgAnimation.className = 'bg-animation';
    document.body.appendChild(bgAnimation);

    for (let i = 0; i < 50; i++) {
        createParticle(bgAnimation);
    }
}

// Function to create a single particle
function createParticle(container) {
    const particle = document.createElement('div');
    particle.className = 'particle';
    
    // Random size between 5 and 20px
    const size = Math.random() * 15 + 5;
    particle.style.width = `${size}px`;
    particle.style.height = `${size}px`;
    
    // Random position
    particle.style.left = `${Math.random() * 100}%`;
    particle.style.top = `${Math.random() * 100}%`;
    
    // Random background (science themed)
    const shapes = ['circle', 'triangle', 'square', 'diamond'];
    const shape = shapes[Math.floor(Math.random() * shapes.length)];
    particle.classList.add(shape);
    
    // Random animation duration between 10 and 30 seconds
    const duration = Math.random() * 20 + 10;
    particle.style.animation = `float ${duration}s infinite ease-in-out`;
    
    // Random delay
    particle.style.animationDelay = `${Math.random() * 5}s`;
    
    // Add to container
    container.appendChild(particle);
    
    // Set a random CSS variable for the direction
    particle.style.setProperty('--direction', Math.random() > 0.5 ? '1' : '-1');
}

// Function to add floating elements to sections
function addFloatingElements() {
    const sections = document.querySelectorAll('.section');
    
    sections.forEach(section => {
        // Add 3-6 floating elements per section
        const count = Math.floor(Math.random() * 4) + 3;
        
        for (let i = 0; i < count; i++) {
            const element = document.createElement('div');
            element.className = 'floating-element';
            
            // Random size between 30 and 150px
            const size = Math.random() * 120 + 30;
            element.style.width = `${size}px`;
            element.style.height = `${size}px`;
            
            // Random position
            element.style.left = `${Math.random() * 90 + 5}%`;
            element.style.top = `${Math.random() * 80 + 10}%`;
            
            // Random animation
            const duration = Math.random() * 10 + 15;
            element.style.animation = `float ${duration}s infinite ease-in-out`;
            
            // Random delay
            element.style.animationDelay = `${Math.random() * 5}s`;
            
            section.appendChild(element);
        }
    });
}

// Function to initialize scroll to top button
function initScrollToTop() {
    // Create scroll to top button
    const scrollTopBtn = document.createElement('div');
    scrollTopBtn.className = 'scroll-top';
    scrollTopBtn.innerHTML = '↑';
    document.body.appendChild(scrollTopBtn);
    
    // Show button when scrolling down
    window.addEventListener('scroll', function() {
        if (window.pageYOffset > 300) {
            scrollTopBtn.classList.add('show');
        } else {
            scrollTopBtn.classList.remove('show');
        }
    });
    
    // Scroll to top when clicking the button
    scrollTopBtn.addEventListener('click', function() {
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    });
}

// Function to animate elements when scrolled into view
function animateOnScroll() {
    const cards = document.querySelectorAll('.card');
    const sections = document.querySelectorAll('.section-title');
    
    // Set initial state
    cards.forEach(card => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(50px)';
        card.style.transition = 'opacity 0.8s ease, transform 0.8s ease';
    });
    
    sections.forEach(section => {
        section.style.opacity = '0';
        section.style.transform = 'translateY(30px)';
        section.style.transition = 'opacity 0.8s ease, transform 0.8s ease';
    });
    
    // Function to check if element is in viewport
    function isInViewport(element) {
        const rect = element.getBoundingClientRect();
        return (
            rect.top <= (window.innerHeight || document.documentElement.clientHeight) * 0.85 &&
            rect.bottom >= 0
        );
    }
    
    // Function to handle scroll animation
    function handleScrollAnimation() {
        cards.forEach(card => {
            if (isInViewport(card)) {
                card.style.opacity = '1';
                card.style.transform = 'translateY(0)';
            }
        });
        
        sections.forEach(section => {
            if (isInViewport(section)) {
                section.style.opacity = '1';
                section.style.transform = 'translateY(0)';
            }
        });
    }
    
    // Listen for scroll events
    window.addEventListener('scroll', handleScrollAnimation);
    
    // Trigger once on load
    handleScrollAnimation();
}

// Function for typing effect
function typeText(element, text, index, speed) {
    if (index < text.length) {
        element.innerHTML += text.charAt(index);
        index++;
        setTimeout(() => typeText(element, text, index, speed), speed);
    }
} 