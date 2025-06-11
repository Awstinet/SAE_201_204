// Fonctions JavaScript
function scrollToSection(sectionId) {
    document.getElementById(sectionId).scrollIntoView({ behavior: 'smooth' });
}


// Initialisation des bulles flottantes
function generateBubbles() {
    const bubbleContainer = document.createElement('div');
    bubbleContainer.className = 'bubble-container';
    document.body.appendChild(bubbleContainer);
    
    for (let i = 0; i < 10; i++) {
        const bubble = document.createElement('div');
        bubble.className = 'bubble';
        
        const size = Math.random() * 30 + 10;
        const left = Math.random() * 100;
        const top = Math.random() * 100;
        const delay = Math.random() * 15;
        const duration = Math.random() * 10 + 10;
        
        bubble.style.width = `${size}px`;
        bubble.style.height = `${size}px`;
        bubble.style.left = `${left}%`;
        bubble.style.top = `${top}%`;
        bubble.style.animationDelay = `${delay}s`;
        bubble.style.animationDuration = `${duration}s`;
        
        bubbleContainer.appendChild(bubble);
    }
}

// Au chargement de la page
document.addEventListener('DOMContentLoaded', function() {
    generateBubbles();
});