document.addEventListener('DOMContentLoaded', function() {

document.querySelector('.navbar-item[href="#features-section"]').addEventListener('click', function(e) {
    e.preventDefault(); // Sayfa yenilenmesini önlemek için
    const featuresSection = document.getElementById('features-section');
    featuresSection.scrollIntoView({ behavior: 'smooth' }); // Kaydırma işlemi
});

window.addEventListener('scroll', function() {
    var navbar = document.querySelector('.navbar');
    if (window.scrollY > 0) {
        navbar.classList.add('scrolled');
    } else {
        navbar.classList.remove('scrolled');
    }
});
});