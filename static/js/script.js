// =================================
// ARCOP - JavaScript RESPONSIVE
// Version améliorée avec menu mobile
// =================================

document.addEventListener('DOMContentLoaded', function() {
    
    // ============================
    // MENU HAMBURGER (MOBILE)
    // ============================
    
    const menuToggle = document.querySelector('.mobile-menu-toggle');
    const nav = document.querySelector('nav');
    const navItems = document.querySelectorAll('.nav-item');
    
    if (menuToggle) {
        menuToggle.addEventListener('click', function() {
            this.classList.toggle('active');
            nav.classList.toggle('active');
            
            // Fermer tous les dropdowns quand on ferme le menu
            if (!nav.classList.contains('active')) {
                navItems.forEach(item => {
                    item.classList.remove('active');
                });
            }
        });
    }
    
    // Gestion des dropdowns sur mobile
    navItems.forEach(item => {
        const link = item.querySelector('a');
        const dropdown = item.querySelector('.dropdown');
        
        if (dropdown && window.innerWidth <= 768) {
            link.addEventListener('click', function(e) {
                // Sur mobile, empêcher la navigation si c'est un menu avec dropdown
                if (window.innerWidth <= 768) {
                    e.preventDefault();
                    
                    // Fermer les autres dropdowns
                    navItems.forEach(otherItem => {
                        if (otherItem !== item) {
                            otherItem.classList.remove('active');
                        }
                    });
                    
                    // Toggle le dropdown actuel
                    item.classList.toggle('active');
                }
            });
        }
    });
    
    // Fermer le menu mobile quand on clique sur un lien
    const allNavLinks = document.querySelectorAll('nav a');
    allNavLinks.forEach(link => {
        link.addEventListener('click', function() {
            // Ne fermer que si c'est un lien final (pas un dropdown parent)
            if (!this.nextElementSibling || !this.nextElementSibling.classList.contains('dropdown')) {
                if (window.innerWidth <= 768) {
                    nav.classList.remove('active');
                    if (menuToggle) {
                        menuToggle.classList.remove('active');
                    }
                    navItems.forEach(item => {
                        item.classList.remove('active');
                    });
                }
            }
        });
    });
    
    // Fermer le menu si on redimensionne vers desktop
    window.addEventListener('resize', function() {
        if (window.innerWidth > 768) {
            nav.classList.remove('active');
            if (menuToggle) {
                menuToggle.classList.remove('active');
            }
            navItems.forEach(item => {
                item.classList.remove('active');
            });
        }
    });
    
    // ============================
    // ANIMATION AU SCROLL
    // ============================
    
    const animateOnScroll = () => {
        const cards = document.querySelectorAll('.news-card, .video-card, .agenda-card, .stat-card');
        cards.forEach(card => {
            const cardTop = card.getBoundingClientRect().top;
            const windowHeight = window.innerHeight;
            if (cardTop < windowHeight - 50) {
                card.style.opacity = '1';
                card.style.transform = 'translateY(0)';
            }
        });
    };
    
    // Initialisation des cartes avec animation
    document.querySelectorAll('.news-card, .video-card, .agenda-card, .stat-card').forEach(card => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        card.style.transition = 'all 0.5s ease';
    });
    
    // Throttle pour optimiser les performances
    let scrollTimeout;
    window.addEventListener('scroll', function() {
        if (scrollTimeout) {
            window.cancelAnimationFrame(scrollTimeout);
        }
        scrollTimeout = window.requestAnimationFrame(animateOnScroll);
    });
    
    // Animation initiale
    animateOnScroll();
    
    // ============================
    // FORMULAIRE NEWSLETTER
    // ============================
    
    const newsletterForm = document.querySelector('.newsletter-form');
    if (newsletterForm) {
        newsletterForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const email = this.querySelector('input[type="email"]').value;
            
            // Validation basique
            if (validateEmail(email)) {
                alert('✅ Merci de vous être inscrit à notre newsletter avec l\'email: ' + email);
                this.reset();
            } else {
                alert('❌ Veuillez entrer une adresse email valide.');
            }
        });
    }
    
    // Fonction de validation email
    function validateEmail(email) {
        const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return re.test(email);
    }
    
    // ============================
    // NAVIGATION SMOOTH SCROLL
    // ============================
    
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            const href = this.getAttribute('href');
            if (href !== '#' && href !== '#accueil') {
                const target = document.querySelector(href);
                if (target) {
                    e.preventDefault();
                    
                    // Fermer le menu mobile si ouvert
                    if (window.innerWidth <= 768 && nav) {
                        nav.classList.remove('active');
                        if (menuToggle) {
                            menuToggle.classList.remove('active');
                        }
                    }
                    
                    // Scroll smooth
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            }
        });
    });
    
    // ============================
    // LAZY LOADING IMAGES
    // ============================
    
    if ('IntersectionObserver' in window) {
        const imageObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    if (img.dataset.src) {
                        img.src = img.dataset.src;
                        img.removeAttribute('data-src');
                        observer.unobserve(img);
                    }
                }
            });
        });
        
        document.querySelectorAll('img[data-src]').forEach(img => {
            imageObserver.observe(img);
        });
    }
    
    // ============================
    // GESTION ORIENTATION MOBILE
    // ============================
    
    let lastOrientation = window.orientation;
    window.addEventListener('orientationchange', function() {
        if (window.orientation !== lastOrientation) {
            lastOrientation = window.orientation;
            
            // Fermer le menu mobile lors du changement d'orientation
            if (nav) {
                nav.classList.remove('active');
            }
            if (menuToggle) {
                menuToggle.classList.remove('active');
            }
            
            // Forcer un reflow
            setTimeout(() => {
                window.scrollBy(0, 1);
                window.scrollBy(0, -1);
            }, 100);
        }
    });
    
    // ============================
    // DÉTECTION TACTILE
    // ============================
    
    if ('ontouchstart' in window) {
        document.body.classList.add('touch-device');
    }
    
    // ============================
    // BOUTON "RETOUR EN HAUT"
    // ============================
    
    const createScrollToTopButton = () => {
        const button = document.createElement('button');
        button.innerHTML = '↑';
        button.className = 'scroll-to-top';
        button.setAttribute('aria-label', 'Retour en haut');
        
        button.style.cssText = `
            position: fixed;
            bottom: 30px;
            right: 30px;
            width: 50px;
            height: 50px;
            background: #2d862d;
            color: white;
            border: none;
            border-radius: 50%;
            font-size: 24px;
            cursor: pointer;
            opacity: 0;
            visibility: hidden;
            transition: all 0.3s ease;
            z-index: 999;
            box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        `;
        
        document.body.appendChild(button);
        
        // Afficher/cacher le bouton selon le scroll
        window.addEventListener('scroll', () => {
            if (window.pageYOffset > 300) {
                button.style.opacity = '1';
                button.style.visibility = 'visible';
            } else {
                button.style.opacity = '0';
                button.style.visibility = 'hidden';
            }
        });
        
        // Action du bouton
        button.addEventListener('click', () => {
            window.scrollTo({
                top: 0,
                behavior: 'smooth'
            });
        });
    };
    
    createScrollToTopButton();
    
    // ============================
    // OPTIMISATION PERFORMANCE
    // ============================
    
    // Désactiver les hover effects sur mobile pour meilleure performance
    if (window.innerWidth <= 768) {
        document.body.classList.add('no-hover');
    }
    
    // Performance monitoring (facultatif, à commenter en production)
    /*
    if ('performance' in window) {
        window.addEventListener('load', () => {
            const perfData = performance.timing;
            const pageLoadTime = perfData.loadEventEnd - perfData.navigationStart;
            console.log('⏱️ Temps de chargement de la page:', pageLoadTime + 'ms');
        });
    }
    */
    
    // ============================
    // ACCESSIBILITÉ
    // ============================
    
    // Trap focus dans le menu mobile quand ouvert
    const trapFocus = (element) => {
        const focusableElements = element.querySelectorAll(
            'a[href], button, textarea, input, select, [tabindex]:not([tabindex="-1"])'
        );
        const firstElement = focusableElements[0];
        const lastElement = focusableElements[focusableElements.length - 1];
        
        element.addEventListener('keydown', function(e) {
            if (e.key === 'Tab') {
                if (e.shiftKey) {
                    if (document.activeElement === firstElement) {
                        lastElement.focus();
                        e.preventDefault();
                    }
                } else {
                    if (document.activeElement === lastElement) {
                        firstElement.focus();
                        e.preventDefault();
                    }
                }
            }
            
            // Fermer avec Escape
            if (e.key === 'Escape') {
                if (nav) {
                    nav.classList.remove('active');
                }
                if (menuToggle) {
                    menuToggle.classList.remove('active');
                    menuToggle.focus();
                }
            }
        });
    };
    
    if (nav) {
        trapFocus(nav);
    }
    
});

// ============================
// FONCTIONS UTILITAIRES
// ============================

// Fonction pour charger plus d'actualités (si pagination AJAX)
function loadMoreNews() {
    console.log('Chargement de plus d\'actualités...');
    // À implémenter selon vos besoins
}

// Fonction pour le formulaire de contact
function handleContactForm(event) {
    event.preventDefault();
    const form = event.target;
    const formData = new FormData(form);
    
    console.log('Formulaire de contact soumis');
    alert('✅ Votre message a été envoyé avec succès!');
    form.reset();
}

// Détection du type de dispositif
function getDeviceType() {
    const width = window.innerWidth;
    if (width < 768) return 'mobile';
    if (width < 1024) return 'tablet';
    return 'desktop';
}

// Optimisation des images selon la taille d'écran
function loadOptimizedImages() {
    const images = document.querySelectorAll('img[data-src-mobile][data-src-desktop]');
    const deviceType = getDeviceType();
    
    images.forEach(img => {
        const src = deviceType === 'mobile' ? 
            img.dataset.srcMobile : 
            img.dataset.srcDesktop;
        
        if (src && img.src !== src) {
            img.src = src;
        }
    });
}

// ============================
// EXPORT POUR UTILISATION GLOBALE
// ============================

window.arcop = {
    loadMoreNews,
    handleContactForm,
    getDeviceType,
    loadOptimizedImages
};