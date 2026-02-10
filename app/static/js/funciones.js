// Carousel functionality for index page
document.addEventListener('DOMContentLoaded', function() {
    initializeCarousel();
});

function initializeCarousel() {
    const slides = document.querySelectorAll('.carousel-slide');
    const dots = document.querySelectorAll('.dot');
    let currentSlide = 0;

    if (slides.length === 0) return;

    function showSlide(n) {
        slides.forEach(slide => slide.classList.remove('active'));
        dots.forEach(dot => dot.classList.remove('active'));
        
        currentSlide = (n + slides.length) % slides.length;
        
        slides[currentSlide].classList.add('active');
        dots[currentSlide].classList.add('active');
    }

    // Dot click events
    dots.forEach((dot, index) => {
        dot.addEventListener('click', () => {
            showSlide(index);
        });
    });

    // Auto-advance slides every 5 seconds
    setInterval(() => {
        showSlide(currentSlide + 1);
    }, 5000);

    // Carousel comprar buttons
    document.querySelectorAll('.btn-comprar').forEach(btn => {
        btn.addEventListener('click', function() {
            const slide = this.closest('.carousel-slide');
            const title = slide.querySelector('h2').textContent;
            alert(`Redirigiendo a compra de: ${title}`);
            // Aquí puedes redirigir a la página correspondiente
        });
    });
}