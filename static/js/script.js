// =================================
// ARCOP - JavaScript principal
// =================================

document.addEventListener('DOMContentLoaded', function() {
    
    // Animation au scroll
    window.addEventListener('scroll', function() {
        const cards = document.querySelectorAll('.news-card, .video-card, .agenda-card');
        cards.forEach(card => {
            const cardTop = card.getBoundingClientRect().top;
            const windowHeight = window.innerHeight;
            if (cardTop < windowHeight - 50) {
                card.style.opacity = '1';
                card.style.transform = 'translateY(0)';
            }
        });
    });

    // Initialisation des cartes avec animation
    document.querySelectorAll('.news-card, .video-card, .agenda-card').forEach(card => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        card.style.transition = 'all 0.5s ease';
    });

    // Gestion du formulaire de newsletter
    const newsletterForm = document.querySelector('.newsletter-form');
    if (newsletterForm) {
        newsletterForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const email = this.querySelector('input[type="email"]').value;
            alert('Merci de vous être inscrit à notre newsletter avec l\'email: ' + email);
            this.reset();
        });
    }

    // Navigation smooth scroll
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            const href = this.getAttribute('href');
            if (href !== '#' && href !== '#accueil') {
                e.preventDefault();
                const target = document.querySelector(href);
                if (target) {
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            }
        });
    });

    // Menu mobile toggle (si nécessaire)
    const navToggle = document.querySelector('.nav-toggle');
    const navMenu = document.querySelector('nav');
    
    if (navToggle) {
        navToggle.addEventListener('click', function() {
            navMenu.classList.toggle('active');
        });
    }
});

// Fonction pour charger plus d'actualités (si pagination AJAX)
function loadMoreNews() {
    // À implémenter si besoin
    console.log('Chargement de plus d\'actualités...');
}

// Fonction pour le formulaire de contact
function handleContactForm(event) {
    event.preventDefault();
    const form = event.target;
    const formData = new FormData(form);
    
    // À implémenter avec votre backend
    console.log('Formulaire de contact soumis');
    alert('Votre message a été envoyé avec succès!');
    form.reset();
}
