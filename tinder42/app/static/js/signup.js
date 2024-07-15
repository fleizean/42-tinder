function navigateToFormPage(stepId, text) {
    // Tüm form sayfalarını gizle
    const formPages = document.querySelectorAll('[id^="form-page-"]');
    formPages.forEach(page => {
        page.style.display = 'none';
    });

    // İlgili form sayfasını göster
    const targetFormPage = document.getElementById(`form-page-${stepId}`);
    if (targetFormPage) {
        targetFormPage.style.display = 'block';
    }

    // İlerleme çubuğunu güncelle
    updateProgressBar(stepId);
    updateProgressText(text);
}

function updateProgressBar(currentStep) {
    const steps = document.querySelectorAll('.progress-step');
    steps.forEach(step => {
        step.classList.remove('active'); // Tüm adımlardan 'active' sınıfını kaldır
        if (parseInt(step.getAttribute('data-step')) === parseInt(currentStep)) {
            step.classList.add('active'); // Tıklanan adıma 'active' sınıfı ekle
        }
    });
}

function updateProgressText(text) {
    const progressText = document.getElementById('progress-text');
    progressText.textContent = text;
}

function gpsLocate() {
    if (navigator.geolocation) {
        document.getElementById('latitudeForm').value = '';
        document.getElementById('longitudeForm').value = '';
        navigator.geolocation.getCurrentPosition(showPosition);
    } else {
        alert("Geolocation is not supported by this browser.");
    }
}

function showPosition(position) {
    document.getElementById('latitudeForm').value = position.coords.latitude;
    document.getElementById('longitudeForm').value = position.coords.longitude;
    document.getElementById('gps-location').disabled = false;
}

document.addEventListener('DOMContentLoaded', function() {
    fetch('static/json/hashtags.json')
        .then(response => response.json())
        .then(data => {
            const selectElement = document.getElementById('mySelect');
            data.forEach(item => {
                const option = document.createElement('option');
                option.value = item.text; // JSON'daki değeri kullanın
                option.textContent = item.text; // JSON'daki metni kullanın
                selectElement.appendChild(option);
            });
        })
        .catch(error => console.error('Error loading the JSON data: ', error));
});