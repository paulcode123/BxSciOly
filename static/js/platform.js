// Wait for the DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize the intersection observer for scroll animations
    initScrollAnimations();
    
    // Initialize the concept map visualization
    initConceptMap();
    
    // Create background particles
    createParticles();
    
    // Initialize new interactive elements
    initTiltEffect();
    initComparisonSlider();
    initMouseTracker();
    initScrollProgressBar();
    initTypewriterEffect();
    initTimeline();
    init3DButtons();
});

// Function to initialize scroll animations
function initScrollAnimations() {
    // Create an Intersection Observer
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            // If the element is in the viewport
            if (entry.isIntersecting) {
                // Add the 'visible' class to trigger animations
                entry.target.classList.add('visible');
                
                // If this is a section title, animate child elements with staggered delay
                if (entry.target.classList.contains('section-title')) {
                    const parent = entry.target.closest('.section-content');
                    const animatedElements = parent.querySelectorAll('.platform-point, .fade-in, .slide-in-left, .slide-in-right, .timeline-item');
                    
                    animatedElements.forEach((el, index) => {
                        setTimeout(() => {
                            el.classList.add('visible');
                        }, 300 + (index * 150)); // Staggered delay
                    });
                }
            }
        });
    }, {
        threshold: 0.2 // Trigger when 20% of the element is visible
    });
    
    // Observe all section content and titles
    document.querySelectorAll('.section-content, .section-title').forEach(el => {
        observer.observe(el);
    });
}

// Function to initialize and animate the concept map
function initConceptMap() {
    const conceptMap = document.querySelector('.concept-map');
    if (!conceptMap) return;
    
    // Define concept nodes
    const concepts = [
        { id: 'learning', label: 'Learning', x: 50, y: 30 },
        { id: 'home', label: 'At Home', x: 25, y: 60 },
        { id: 'meeting', label: 'Interactive Meetings', x: 75, y: 60 },
        { id: 'conceptual', label: 'Conceptual Understanding', x: 20, y: 40 },
        { id: 'memory', label: 'Beyond Memory Games', x: 80, y: 40 },
        { id: 'logistics', label: 'Automated Logistics', x: 50, y: 75 },
        { id: 'talent', label: 'Talent Utilization', x: 35, y: 85 },
        { id: 'top10', label: 'Top 10 in States', x: 65, y: 85 }
    ];
    
    // Define edges between concepts
    const edges = [
        { from: 'learning', to: 'home' },
        { from: 'learning', to: 'meeting' },
        { from: 'home', to: 'conceptual' },
        { from: 'meeting', to: 'memory' },
        { from: 'conceptual', to: 'memory' },
        { from: 'learning', to: 'logistics' },
        { from: 'logistics', to: 'talent' },
        { from: 'talent', to: 'top10' },
        { from: 'memory', to: 'top10' }
    ];
    
    // Create nodes
    concepts.forEach(concept => {
        const node = document.createElement('div');
        node.className = 'concept-node';
        node.id = `node-${concept.id}`;
        node.textContent = concept.label;
        node.style.left = `${concept.x}%`;
        node.style.top = `${concept.y}%`;
        
        // Add click event to highlight connected nodes
        node.addEventListener('click', () => highlightConnections(concept.id));
        
        conceptMap.appendChild(node);
    });
    
    // Create edges
    edges.forEach(edge => {
        createEdge(edge.from, edge.to);
    });
    
    // Animate nodes and edges with delay
    setTimeout(() => {
        document.querySelectorAll('.concept-node').forEach((node, index) => {
            setTimeout(() => {
                node.classList.add('visible');
            }, index * 100);
        });
        
        setTimeout(() => {
            document.querySelectorAll('.concept-edge').forEach((edge, index) => {
                setTimeout(() => {
                    edge.classList.add('visible');
                }, index * 100);
            });
        }, 800); // Start edges after nodes
    }, 1000); // Delay start
}

// Function to create an edge between two nodes
function createEdge(fromId, toId) {
    const fromNode = document.getElementById(`node-${fromId}`);
    const toNode = document.getElementById(`node-${toId}`);
    
    if (!fromNode || !toNode) return;
    
    // Get center positions
    const fromRect = fromNode.getBoundingClientRect();
    const toRect = toNode.getBoundingClientRect();
    const mapRect = document.querySelector('.concept-map').getBoundingClientRect();
    
    const fromX = fromRect.left + fromRect.width/2 - mapRect.left;
    const fromY = fromRect.top + fromRect.height/2 - mapRect.top;
    const toX = toRect.left + toRect.width/2 - mapRect.left;
    const toY = toRect.top + toRect.height/2 - mapRect.top;
    
    // Calculate length and angle
    const length = Math.sqrt(Math.pow(toX - fromX, 2) + Math.pow(toY - fromY, 2));
    const angle = Math.atan2(toY - fromY, toX - fromX) * 180 / Math.PI;
    
    // Create edge element
    const edge = document.createElement('div');
    edge.className = 'concept-edge';
    edge.dataset.from = fromId;
    edge.dataset.to = toId;
    
    // Position and rotate
    edge.style.width = `${length}px`;
    edge.style.left = `${fromX}px`;
    edge.style.top = `${fromY}px`;
    edge.style.transform = `rotate(${angle}deg)`;
    
    document.querySelector('.concept-map').appendChild(edge);
}

// Function to highlight connections when a node is clicked
function highlightConnections(nodeId) {
    // Reset all nodes and edges
    document.querySelectorAll('.concept-node').forEach(node => {
        node.style.transform = 'scale(1)';
        node.style.background = 'rgba(52, 152, 219, 0.8)';
    });
    
    document.querySelectorAll('.concept-edge').forEach(edge => {
        edge.style.background = 'rgba(255, 255, 255, 0.2)';
        edge.style.height = '2px';
    });
    
    // Highlight the selected node
    const selectedNode = document.getElementById(`node-${nodeId}`);
    if (selectedNode) {
        selectedNode.style.transform = 'scale(1.2)';
        selectedNode.style.background = 'rgba(231, 76, 60, 0.9)';
    }
    
    // Highlight connected edges and nodes
    document.querySelectorAll(`.concept-edge[data-from="${nodeId}"], .concept-edge[data-to="${nodeId}"]`).forEach(edge => {
        edge.style.background = 'rgba(231, 76, 60, 0.7)';
        edge.style.height = '3px';
        
        // Get the connected node id
        const connectedNodeId = edge.dataset.from === nodeId ? edge.dataset.to : edge.dataset.from;
        const connectedNode = document.getElementById(`node-${connectedNodeId}`);
        
        if (connectedNode) {
            connectedNode.style.transform = 'scale(1.1)';
            connectedNode.style.background = 'rgba(155, 89, 182, 0.9)';
        }
    });
}

// Function to create background particles for visual effect
function createParticles() {
    const containers = document.querySelectorAll('.bg-animation');
    
    containers.forEach(container => {
        // Create particles
        for (let i = 0; i < 50; i++) {
            const particle = document.createElement('div');
            particle.className = 'particle';
            
            // Random position, size, and opacity
            const size = Math.random() * 5 + 2;
            particle.style.width = `${size}px`;
            particle.style.height = `${size}px`;
            particle.style.left = `${Math.random() * 100}%`;
            particle.style.top = `${Math.random() * 100}%`;
            particle.style.opacity = Math.random() * 0.5 + 0.2;
            
            // Animation
            const duration = Math.random() * 40 + 10;
            const xMovement = Math.random() * 100 - 50;
            const yMovement = Math.random() * 100 - 50;
            
            particle.style.animation = `
                moveParticle ${duration}s linear infinite,
                fadeInOut ${duration / 2}s ease-in-out infinite alternate
            `;
            
            particle.style.setProperty('--x-movement', `${xMovement}px`);
            particle.style.setProperty('--y-movement', `${yMovement}px`);
            
            container.appendChild(particle);
        }
    });
    
    // Add keyframes to the document
    const style = document.createElement('style');
    style.innerHTML = `
        @keyframes moveParticle {
            0% { transform: translate(0, 0); }
            50% { transform: translate(var(--x-movement, 50px), var(--y-movement, 50px)); }
            100% { transform: translate(0, 0); }
        }
        
        @keyframes fadeInOut {
            0% { opacity: 0.1; }
            100% { opacity: 0.5; }
        }
    `;
    document.head.appendChild(style);
}

// Function to initialize 3D tilt effect
function initTiltEffect() {
    const tiltElements = document.querySelectorAll('.tilt-element');
    
    tiltElements.forEach(element => {
        element.addEventListener('mousemove', (e) => {
            const rect = element.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            
            const xPercent = x / rect.width;
            const yPercent = y / rect.height;
            
            const rotateX = (yPercent - 0.5) * -20;
            const rotateY = (xPercent - 0.5) * 20;
            
            element.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg)`;
            
            // Move inner content
            const content = element.querySelector('.tilt-content');
            if (content) {
                content.style.transform = `translateZ(30px)`;
            }
        });
        
        element.addEventListener('mouseleave', () => {
            element.style.transform = 'perspective(1000px) rotateX(0) rotateY(0)';
            
            const content = element.querySelector('.tilt-content');
            if (content) {
                content.style.transform = 'translateZ(0)';
            }
        });
    });
}

// Function to initialize comparison slider
function initComparisonSlider() {
    const sliders = document.querySelectorAll('.comparison-slider');
    
    sliders.forEach(slider => {
        const container = slider.closest('.comparison-container');
        const before = container.querySelector('.comparison-before');
        
        // Set initial position
        slider.style.left = '50%';
        before.style.width = '50%';
        
        // Handle mouse and touch events
        let isDragging = false;
        
        const startDrag = (e) => {
            isDragging = true;
            e.preventDefault();
        };
        
        const stopDrag = () => {
            isDragging = false;
        };
        
        const drag = (e) => {
            if (!isDragging) return;
            
            let x = e.type.includes('touch') 
                ? e.touches[0].clientX 
                : e.clientX;
            
            const rect = container.getBoundingClientRect();
            let position = (x - rect.left) / rect.width * 100;
            
            if (position < 0) position = 0;
            if (position > 100) position = 100;
            
            slider.style.left = `${position}%`;
            before.style.width = `${position}%`;
        };
        
        // Mouse events
        slider.addEventListener('mousedown', startDrag);
        document.addEventListener('mouseup', stopDrag);
        document.addEventListener('mousemove', drag);
        
        // Touch events
        slider.addEventListener('touchstart', startDrag);
        document.addEventListener('touchend', stopDrag);
        document.addEventListener('touchmove', drag);
    });
}

// Function to initialize mouse tracker
function initMouseTracker() {
    const tracker = document.createElement('div');
    tracker.className = 'mouse-tracker';
    document.body.appendChild(tracker);
    
    document.addEventListener('mousemove', (e) => {
        const { clientX, clientY } = e;
        
        // Add a slight delay for smooth effect
        setTimeout(() => {
            tracker.style.left = `${clientX}px`;
            tracker.style.top = `${clientY}px`;
        }, 30);
        
        // Check if hovering over interactive elements
        const isHoveringInteractive = e.target.closest('a, button, .concept-node, .interactive-card');
        
        if (isHoveringInteractive) {
            tracker.style.width = '60px';
            tracker.style.height = '60px';
            tracker.style.background = 'rgba(231, 76, 60, 0.2)';
        } else {
            tracker.style.width = '30px';
            tracker.style.height = '30px';
            tracker.style.background = 'rgba(52, 152, 219, 0.3)';
        }
    });
}

// Function to initialize scroll progress bar
function initScrollProgressBar() {
    // Create the container and progress bar
    const container = document.createElement('div');
    container.className = 'scroll-progress-container';
    
    const progressBar = document.createElement('div');
    progressBar.className = 'scroll-progress-bar';
    
    container.appendChild(progressBar);
    document.body.appendChild(container);
    
    // Update progress on scroll
    window.addEventListener('scroll', () => {
        const scrollTop = document.documentElement.scrollTop || document.body.scrollTop;
        const scrollHeight = document.documentElement.scrollHeight - document.documentElement.clientHeight;
        const progress = (scrollTop / scrollHeight) * 100;
        
        progressBar.style.width = `${progress}%`;
    });
}

// Function to initialize typewriter effect
function initTypewriterEffect() {
    const typewriters = document.querySelectorAll('.typewriter');
    
    typewriters.forEach(typewriter => {
        const text = typewriter.textContent;
        typewriter.textContent = '';
        typewriter.style.width = '0';
        
        // Create an Intersection Observer to start typing when visible
        const observer = new IntersectionObserver((entries) => {
            if (entries[0].isIntersecting) {
                // Start typewriter animation when element is visible
                setTimeout(() => {
                    typewrite(typewriter, text);
                }, 500);
                observer.disconnect();
            }
        }, { threshold: 0.5 });
        
        observer.observe(typewriter);
    });
    
    function typewrite(element, text) {
        // Start with a small width and gradually increase to 100%
        element.style.width = '0%';
        
        // Animation to gradually increase width
        const widthAnimation = setInterval(() => {
            const currentWidth = parseFloat(element.style.width);
            if (currentWidth < 100) {
                element.style.width = (currentWidth + 1) + '%';
            } else {
                clearInterval(widthAnimation);
            }
        }, 30);
        
        let i = 0;
        const speed = 50; // typing speed in ms
        
        function type() {
            if (i < text.length) {
                element.textContent += text.charAt(i);
                i++;
                setTimeout(type, speed);
            } else {
                // Once typing is complete, remove the right border
                setTimeout(() => {
                    element.style.borderRight = 'none';
                }, 1000);
            }
        }
        
        type();
    }
}

// Function to initialize timeline
function initTimeline() {
    const timeline = document.querySelector('.timeline');
    if (!timeline) return;
    
    const timelineItems = timeline.querySelectorAll('.timeline-item');
    
    // Create an Intersection Observer to animate timeline items
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
            }
        });
    }, { threshold: 0.2 });
    
    timelineItems.forEach(item => {
        observer.observe(item);
    });
}

// Function to initialize 3D buttons
function init3DButtons() {
    const buttons = document.querySelectorAll('.button-3d');
    
    buttons.forEach(button => {
        button.addEventListener('mousedown', () => {
            button.style.transform = 'translateY(10px)';
            button.style.boxShadow = '0 0 0 #2980b9, 0 0 0 rgba(0, 0, 0, 0.2)';
        });
        
        button.addEventListener('mouseup', () => {
            button.style.transform = 'translateY(2px)';
            button.style.boxShadow = '0 8px 0 #2980b9, 0 15px 20px rgba(0, 0, 0, 0.2)';
        });
        
        button.addEventListener('mouseleave', () => {
            button.style.transform = 'translateY(0)';
            button.style.boxShadow = '0 10px 0 #2980b9, 0 15px 20px rgba(0, 0, 0, 0.2)';
        });
    });
} 