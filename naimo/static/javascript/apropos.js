// Animation des bulles
function createBubbles() {
    const container = document.getElementById('bubbles-container');
    const bubbleCount = 20;
    
    for (let i = 0; i < bubbleCount; i++) {
        const bubble = document.createElement('div');
        bubble.className = 'bubble';

        const posX = Math.random() * 100;
        const delay = Math.random() * 5;
        const duration = 5 + Math.random() * 10;
        const size = 10 + Math.random() * 30;

        bubble.style.left = `${posX}vw`;
        bubble.style.width = `${size}px`;
        bubble.style.height = `${size}px`;
        bubble.style.animationDelay = `${delay}s`;
        bubble.style.animationDuration = `${duration}s`;

        container.appendChild(bubble);
    }
}

// Animation du poisson
function animateFish() {
    const fish = document.querySelector('.fish-animation');
    let pos = -50;
    let direction = 1;

    function moveFish() {
        pos += (0.5 * direction);
        fish.style.transform = `translateX(${pos}px) scaleX(${direction})`;

        if (pos > window.innerWidth + 50) {
            direction = -1;
            pos = window.innerWidth + 50;
        } else if (pos < -50 && direction === -1) {
            direction = 1;
            pos = -50;
        }

        requestAnimationFrame(moveFish);
    }

    moveFish();
}

// Animation au scroll
function setupScrollAnimations() {
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
            }
        });
    }, { threshold: 0.1 });

    document.querySelectorAll('.card-animated').forEach(card => {
        observer.observe(card);
    });
}

// Lancer au chargement
document.addEventListener('DOMContentLoaded', function() {
    createBubbles();
    animateFish();
    setupScrollAnimations();
});