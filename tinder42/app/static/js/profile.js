let slideIndex = 0;
const slides = document.querySelectorAll('.profile-picture-gallery img');
const totalSlides = slides.length;
function showSlide(index) {
    slides.forEach((slide, i) => {
        slide.classList.remove('active');
        if (i === index) {
            slide.classList.add('active');
        }
    });
}
function changeSlide(n) {
    slideIndex = (slideIndex + n + totalSlides) % totalSlides;
    showSlide(slideIndex);
}
function autoSlide() {
    changeSlide(1);
    setTimeout(autoSlide, 5000); // 5 saniyede bir otomatik geçiş
}
document.addEventListener('DOMContentLoaded', (event) => {
    showSlide(slideIndex);
    autoSlide();
});