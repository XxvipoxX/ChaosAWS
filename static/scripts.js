// ===== CARRUSEL ANIMADO DE 3 FILAS =====
document.addEventListener('DOMContentLoaded', function() {
    initializeAnimatedCarousels();
    initializeGameCarousels();
    initializeModals();
    initializeUXImprovements();
    fixHeaderOverlap();
});

// ===== FIX PARA HEADER SUPERPUESTO =====
function fixHeaderOverlap() {
    const header = document.querySelector('header');
    const mainContent = document.querySelector('main');
    
    if (header && mainContent) {
        const headerHeight = header.offsetHeight;
        
        // Asegurar que el body tenga el padding correcto
        document.body.style.paddingTop = headerHeight + 'px';
        
        // Asegurar que el contenido principal esté debajo del header
        mainContent.style.marginTop = '0';
        mainContent.style.position = 'relative';
        mainContent.style.zIndex = '1';
        
        // Ajustar cualquier sección que pueda estar superpuesta
        const sections = document.querySelectorAll('.hero, .features, .library-section, .membership-section, .ventajas, .faq');
        sections.forEach(section => {
            section.style.position = 'relative';
            section.style.zIndex = '1';
        });
    }
}

// Ejecutar fix en eventos importantes
window.addEventListener('resize', fixHeaderOverlap);
window.addEventListener('load', fixHeaderOverlap);

// Carrusel animado de 3 filas (estilo slider1)
function initializeAnimatedCarousels() {
    const carousels = document.querySelectorAll('.animated-carousel');
    
    carousels.forEach(carousel => {
        const tracks = carousel.querySelectorAll('.carousel-track');
        
        tracks.forEach((track, index) => {
            // Duplicar contenido para loop infinito
            const originalContent = track.innerHTML;
            track.innerHTML = originalContent + originalContent;
            
            // Configurar velocidad según la fila
            let speed;
            switch(index) {
                case 0: speed = 40; break; // Fila 1: más rápida
                case 1: speed = 60; break; // Fila 2: media
                case 2: speed = 80; break; // Fila 3: más lenta
                default: speed = 50;
            }
            
            // Aplicar animación
            track.style.animation = `scroll-left ${speed}s linear infinite`;
            
            // Pausar animación al hacer hover
            track.addEventListener('mouseenter', () => {
                track.style.animationPlayState = 'paused';
            });
            
            track.addEventListener('mouseleave', () => {
                track.style.animationPlayState = 'running';
            });
        });
    });
}

// Carrusel de juegos destacados
function initializeGameCarousels() {
    const carousels = document.querySelectorAll('.carrusel');
    
    carousels.forEach(carousel => {
        const inner = carousel.querySelector('.carrusel-inner');
        const items = carousel.querySelectorAll('.carrusel-item');
        const prevBtn = carousel.querySelector('.carrusel-btn.prev');
        const nextBtn = carousel.querySelector('.carrusel-btn.next');
        const indicators = carousel.querySelectorAll('.indicator');
        
        let currentIndex = 0;
        let autoSlideInterval;
        
        function showSlide(index) {
            // Validar índice
            if (index >= items.length) currentIndex = 0;
            else if (index < 0) currentIndex = items.length - 1;
            else currentIndex = index;
            
            // Ocultar todas las slides
            items.forEach(item => {
                item.classList.remove('active');
                item.style.opacity = '0';
            });
            
            indicators.forEach(indicator => indicator.classList.remove('active'));
            
            // Mostrar slide actual con transición
            setTimeout(() => {
                items[currentIndex].classList.add('active');
                items[currentIndex].style.opacity = '1';
            }, 50);
            
            // Actualizar indicadores
            indicators[currentIndex].classList.add('active');
        }
        
        function nextSlide() {
            showSlide(currentIndex + 1);
        }
        
        function prevSlide() {
            showSlide(currentIndex - 1);
        }
        
        function startAutoSlide() {
            autoSlideInterval = setInterval(nextSlide, 5000);
        }
        
        function stopAutoSlide() {
            clearInterval(autoSlideInterval);
        }
        
        // Event listeners para navegación
        if (nextBtn) {
            nextBtn.addEventListener('click', () => {
                stopAutoSlide();
                nextSlide();
                startAutoSlide();
            });
        }
        
        if (prevBtn) {
            prevBtn.addEventListener('click', () => {
                stopAutoSlide();
                prevSlide();
                startAutoSlide();
            });
        }
        
        // Event listeners para indicadores
        indicators.forEach((indicator, index) => {
            indicator.addEventListener('click', () => {
                stopAutoSlide();
                showSlide(index);
                startAutoSlide();
            });
        });
        
        // Pausar auto-slide al hacer hover
        carousel.addEventListener('mouseenter', stopAutoSlide);
        carousel.addEventListener('mouseleave', startAutoSlide);
        
        // Iniciar carrusel
        showSlide(0);
        startAutoSlide();
        
        // Navegación por teclado
        document.addEventListener('keydown', (e) => {
            if (document.querySelector('.carrusel:hover')) {
                if (e.key === 'ArrowLeft') {
                    stopAutoSlide();
                    prevSlide();
                    startAutoSlide();
                } else if (e.key === 'ArrowRight') {
                    stopAutoSlide();
                    nextSlide();
                    startAutoSlide();
                }
            }
        });
    });
}

// ===== MODALES =====
function initializeModals() {
    const modal = document.getElementById('gameModal');
    if (!modal) return;
    
    const closeBtn = modal.querySelector('.close');
    const cancelBtn = modal.querySelector('.btn-cancelar');
    const confirmBtn = modal.querySelector('.btn-confirmar');
    
    function openModal(gameName) {
        const modalTitle = document.getElementById('modalGameTitle');
        if (modalTitle) {
            modalTitle.textContent = `Jugar ${gameName}`;
        }
        
        modal.style.display = 'block';
        document.body.style.overflow = 'hidden';
        
        // Verificar si el usuario está autenticado
        const isAuthenticated = document.body.classList.contains('user-authenticated') || 
                               document.querySelector('[data-user-authenticated]');
        
        if (isAuthenticated) {
            confirmBtn.style.display = 'none';
            
            // Simular carga del juego
            setTimeout(() => {
                const modalBody = modal.querySelector('.modal-body');
                if (modalBody) {
                    modalBody.innerHTML = `
                        <div class="game-loading-success">
                            <i class="fas fa-check-circle"></i>
                            <p>Juego cargado exitosamente!</p>
                        </div>
                    `;
                }
            }, 2000);
        } else {
            const modalBody = modal.querySelector('.modal-body');
            if (modalBody) {
                modalBody.innerHTML = `
                    <p>Preparando tu sesión de juego...</p>
                    <div class="loading-spinner"></div>
                `;
            }
            confirmBtn.style.display = 'inline-block';
        }
    }
    
    function closeModal() {
        modal.style.display = 'none';
        document.body.style.overflow = 'auto';
    }
    
    // Event listeners para botones de juego
    document.querySelectorAll('.btn-jugar').forEach(btn => {
        btn.addEventListener('click', function() {
            if (this.disabled) return;
            const gameName = this.getAttribute('data-game');
            openModal(gameName);
        });
    });
    
    // Event listeners para cerrar modal
    if (closeBtn) closeBtn.addEventListener('click', closeModal);
    if (cancelBtn) cancelBtn.addEventListener('click', closeModal);
    
    if (confirmBtn) {
        confirmBtn.addEventListener('click', () => {
            window.location.href = '/login/';
        });
    }
    
    // Cerrar modal al hacer click fuera
    window.addEventListener('click', (e) => {
        if (e.target === modal) {
            closeModal();
        }
    });
    
    // Cerrar modal con ESC
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && modal.style.display === 'block') {
            closeModal();
        }
    });
}

// ===== MEJORAS DE UX =====
function initializeUXImprovements() {
    // Smooth scroll para anchors
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                const headerHeight = document.querySelector('header').offsetHeight;
                const targetPosition = target.getBoundingClientRect().top + window.pageYOffset - headerHeight;
                
                window.scrollTo({
                    top: targetPosition,
                    behavior: 'smooth'
                });
            }
        });
    });
    
    // Efecto de carga para imágenes
    const images = document.querySelectorAll('img');
    images.forEach(img => {
        if (!img.complete) {
            img.style.opacity = '0';
            img.style.transition = 'opacity 0.3s ease';
        }
        img.addEventListener('load', function() {
            this.style.opacity = '1';
        });
    });
    
    // Efectos hover para tarjetas
    document.querySelectorAll('.feature, .plan, .category-card, .game-card').forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-5px)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
        });
    });
    
    // Botones "Ver Más" para categorías
    document.querySelectorAll('.btn-ver-mas').forEach(btn => {
        btn.addEventListener('click', function() {
            const categoria = this.closest('.category-card').querySelector('h5').textContent;
            showCategoryAlert(categoria);
        });
    });
    
    // Interactividad para tarjetas de juego
    document.querySelectorAll('.game-card').forEach(card => {
        card.addEventListener('click', function() {
            const gameName = this.querySelector('h3').textContent;
            showGameDetails(gameName);
        });
    });
    
    // Navegación activa
    highlightActiveNav();
    
    // Mejoras de formularios
    initializeFormEnhancements();
}

function showCategoryAlert(categoria) {
    const alertBox = document.createElement('div');
    alertBox.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: #76b900;
        color: #000;
        padding: 1rem 1.5rem;
        border-radius: 8px;
        font-weight: bold;
        z-index: 10000;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        animation: slideInRight 0.3s ease;
    `;
    alertBox.textContent = `Mostrando juegos de: ${categoria}`;
    
    document.body.appendChild(alertBox);
    
    setTimeout(() => {
        alertBox.style.animation = 'slideOutRight 0.3s ease';
        setTimeout(() => {
            if (alertBox.parentNode) {
                document.body.removeChild(alertBox);
            }
        }, 300);
    }, 3000);
}

function showGameDetails(gameName) {
    const modal = document.getElementById('gameModal');
    if (!modal) return;
    
    const modalTitle = document.getElementById('modalGameTitle');
    if (modalTitle) {
        modalTitle.textContent = `Detalles de ${gameName}`;
    }
    
    const modalBody = modal.querySelector('.modal-body');
    if (modalBody) {
        modalBody.innerHTML = `
            <div class="game-details">
                <h4>${gameName}</h4>
                <p>Información detallada del juego...</p>
                <div class="game-specs">
                    <p><strong>Género:</strong> Acción</p>
                    <p><strong>Plataforma:</strong> PC</p>
                    <p><strong>Requisitos:</strong> Streaming en la nube</p>
                </div>
            </div>
        `;
    }
    
    modal.style.display = 'block';
    document.body.style.overflow = 'hidden';
}

function highlightActiveNav() {
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('nav a');
    
    navLinks.forEach(link => {
        const href = link.getAttribute('href');
        if (href === currentPath || 
            (currentPath !== '/' && href !== '/' && currentPath.includes(href.replace('/', '')))) {
            link.classList.add('active');
        } else {
            link.classList.remove('active');
        }
    });
}

function initializeFormEnhancements() {
    // Mejoras para campos de formulario
    document.querySelectorAll('.form-input-field, input, select, textarea').forEach(field => {
        // Efecto focus mejorado
        field.addEventListener('focus', function() {
            this.parentElement.style.borderColor = '#76b900';
            this.parentElement.style.boxShadow = '0 0 0 2px rgba(118, 185, 0, 0.2)';
        });
        
        field.addEventListener('blur', function() {
            this.parentElement.style.borderColor = '#444';
            this.parentElement.style.boxShadow = 'none';
        });
        
        // Validación en tiempo real para campos requeridos
        field.addEventListener('input', function() {
            if (this.hasAttribute('required') && this.value.trim() === '') {
                this.style.borderColor = '#ff4444';
            } else {
                this.style.borderColor = '#76b900';
            }
        });
    });
    
    // Mejora para botones de formulario
    document.querySelectorAll('button[type="submit"]').forEach(button => {
        button.addEventListener('click', function(e) {
            if (this.form && !this.form.checkValidity()) {
                e.preventDefault();
                showFormError('Por favor, completa todos los campos requeridos.');
            }
        });
    });
}

function showFormError(message) {
    const errorBox = document.createElement('div');
    errorBox.style.cssText = `
        position: fixed;
        top: 20px;
        left: 50%;
        transform: translateX(-50%);
        background: #ff4444;
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 8px;
        font-weight: bold;
        z-index: 10000;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        animation: slideInDown 0.3s ease;
    `;
    errorBox.textContent = message;
    
    document.body.appendChild(errorBox);
    
    setTimeout(() => {
        errorBox.style.animation = 'slideOutUp 0.3s ease';
        setTimeout(() => {
            if (errorBox.parentNode) {
                document.body.removeChild(errorBox);
            }
        }, 300);
    }, 3000);
}

// ===== ANIMACIONES CSS ADICIONALES =====
const style = document.createElement('style');
style.textContent = `
    @keyframes scroll-left {
        0% {
            transform: translateX(0);
        }
        100% {
            transform: translateX(-50%);
        }
    }
    
    @keyframes slideInRight {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOutRight {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(100%);
            opacity: 0;
        }
    }
    
    @keyframes slideInDown {
        from {
            transform: translate(-50%, -100%);
            opacity: 0;
        }
        to {
            transform: translate(-50%, 0);
            opacity: 1;
        }
    }
    
    @keyframes slideOutUp {
        from {
            transform: translate(-50%, 0);
            opacity: 1;
        }
        to {
            transform: translate(-50%, -100%);
            opacity: 0;
        }
    }
    
    .game-loading-success {
        text-align: center;
        padding: 1rem;
    }
    
    .game-loading-success i {
        color: #76b900;
        font-size: 3rem;
        margin-bottom: 1rem;
    }
    
    .carrusel-item {
        transition: opacity 0.5s ease-in-out;
    }
    
    .loading-spinner {
        border: 4px solid rgba(255, 255, 255, 0.1);
        border-top: 4px solid #76b900;
        border-radius: 50%;
        width: 40px;
        height: 40px;
        animation: spin 1s linear infinite;
        margin: 1rem auto;
    }
    
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    .game-details {
        text-align: left;
    }
    
    .game-details h4 {
        color: #76b900;
        margin-bottom: 1rem;
    }
    
    .game-specs {
        margin-top: 1rem;
        padding: 1rem;
        background: rgba(255, 255, 255, 0.05);
        border-radius: 5px;
    }
    
    .game-specs p {
        margin: 0.5rem 0;
    }
    
    /* Mejoras para el header fix */
    body.header-fixed {
        padding-top: var(--header-height);
    }
    
    /* Estados de carga mejorados */
    .loading-state {
        opacity: 0.7;
        pointer-events: none;
    }
    
    .loading-state::after {
        content: '';
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        width: 20px;
        height: 20px;
        border: 2px solid #76b900;
        border-top: 2px solid transparent;
        border-radius: 50%;
        animation: spin 1s linear infinite;
    }
`;
document.head.appendChild(style);

// ===== RESPONSIVE HELPERS =====
function checkMobile() {
    return window.innerWidth <= 768;
}

function initializeResponsiveBehavior() {
    function handleResize() {
        if (checkMobile()) {
            document.body.classList.add('mobile');
            // Ajustes específicos para mobile
            document.querySelectorAll('.carousel-track').forEach(track => {
                track.style.animationDuration = '20s';
            });
        } else {
            document.body.classList.remove('mobile');
            // Restaurar ajustes para desktop
            document.querySelectorAll('.carousel-track').forEach((track, index) => {
                let speed;
                switch(index) {
                    case 0: speed = 40; break;
                    case 1: speed = 60; break;
                    case 2: speed = 80; break;
                    default: speed = 50;
                }
                track.style.animationDuration = `${speed}s`;
            });
        }
        
        // Re-aplicar fix para header
        fixHeaderOverlap();
    }
    
    window.addEventListener('resize', handleResize);
    
    // Inicializar estado
    handleResize();
}

// Inicializar comportamiento responsive
initializeResponsiveBehavior();

// ===== ERROR HANDLING MEJORADO =====
window.addEventListener('error', function(e) {
    console.error('Error capturado:', e.error);
    
    // Mostrar error amigable al usuario si es crítico
    if (e.error.message.includes('Cannot read') || e.error.message.includes('undefined')) {
        console.warn('Error de JavaScript no crítico:', e.error.message);
    }
});

// Manejar errores de recursos
window.addEventListener('unhandledrejection', function(e) {
    console.error('Promise rechazada:', e.reason);
});

// ===== PERFORMANCE OPTIMIZATIONS =====
function throttle(func, limit) {
    let inThrottle;
    return function() {
        const args = arguments;
        const context = this;
        if (!inThrottle) {
            func.apply(context, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    }
}

// Aplicar throttle a eventos de scroll y resize
window.addEventListener('scroll', throttle(function() {
    // Lógica de scroll optimizada
}, 100));

window.addEventListener('resize', throttle(function() {
    fixHeaderOverlap();
}, 250));

// ===== Lazy Loading para Imágenes =====
function initializeLazyLoading() {
    const images = document.querySelectorAll('img[data-src]');
    
    const imageObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                img.src = img.dataset.src;
                img.removeAttribute('data-src');
                imageObserver.unobserve(img);
            }
        });
    });
    
    images.forEach(img => imageObserver.observe(img));
}

// Inicializar lazy loading
initializeLazyLoading();

// ===== EXPORTAR FUNCIONES PARA USO GLOBAL =====
window.ChaosCompany = {
    initializeAnimatedCarousels,
    initializeGameCarousels,
    initializeModals,
    showCategoryAlert,
    fixHeaderOverlap,
    initializeUXImprovements
};

// ===== INICIALIZACIÓN FINAL =====
// Esperar a que todo esté completamente cargado
window.addEventListener('load', function() {
    // Asegurar que el header esté correctamente posicionado
    setTimeout(fixHeaderOverlap, 500);
    
    // Inicializar componentes que dependen de imágenes cargadas
    setTimeout(() => {
        initializeAnimatedCarousels();
        initializeGameCarousels();
    }, 1000);
    
    console.log('ChaosCompany - Sistema inicializado correctamente');
});