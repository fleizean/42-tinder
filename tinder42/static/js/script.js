document.addEventListener('DOMContentLoaded', function() {

document.querySelector('.navbar-item[href="#home-section"]').addEventListener('click', function(e) {
    e.preventDefault(); // Sayfa yenilenmesini önlemek için
    const bannerSection = document.getElementById('home-section');
    bannerSection.scrollIntoView({ behavior: 'smooth' }); // Kaydırma işlemi
});
    

document.querySelector('.navbar-item[href="#features-section"]').addEventListener('click', function(e) {
    e.preventDefault(); // Sayfa yenilenmesini önlemek için
    const featuresSection = document.getElementById('features-section');
    featuresSection.scrollIntoView({ behavior: 'smooth' }); // Kaydırma işlemi
});

document.querySelector('.navbar-item[href="#howitworks-section"]').addEventListener('click', function(e) {
    e.preventDefault(); // Sayfa yenilenmesini önlemek için
    const howitWorksSection = document.getElementById('howitworks-section');
    howitWorksSection.scrollIntoView({ behavior: 'smooth' }); // Kaydırma işlemi
});

document.querySelector('.navbar-item[href="#aboutus-section"]').addEventListener('click', function(e) {
    e.preventDefault(); // Sayfa yenilenmesini önlemek için
    const aboutUsSection = document.getElementById('aboutus-section');
    aboutUsSection.scrollIntoView({ behavior: 'smooth' }); // Kaydırma işlemi
});

window.addEventListener('scroll', function() {
    var navbar = document.querySelector('.navbar');
    var logo = document.querySelector('.logo-img'); // Changed to querySelector
    if (window.scrollY > 0) {
        navbar.classList.add('scrolled');
        logo.style.display = 'flex';
    } else {
        navbar.classList.remove('scrolled');
        logo.style.display = 'none';
    }
});
});