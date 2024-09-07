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
        navigator.geolocation.getCurrentPosition(showPosition, handleGeolocationError);
    } else {
        fetchIPLocation();
    }
}

function handleGeolocationError(error) {
    if (error.code === error.PERMISSION_DENIED) {
        fetchIPLocation();
    } else {
        console.error('Geolocation error:', error);
    }
}

function fetchIPLocation() {
    fetch('https://ipinfo.io/json?token=6c244836685637')
        .then(response => response.json())
        .then(data => {
            const loc = data.loc.split(',');
            const latitude = loc[0];
            const longitude = loc[1];
            console.log(`IP Info: ${JSON.stringify(data)}`);
            showPosition({coords: {latitude: parseFloat(latitude), longitude: parseFloat(longitude)}});
            console.log(`City: ${data.city}, Region: ${data.region}, Country: ${data.country}`);
        })
        .catch(error => {
            console.error('Error fetching IP info:', error);
        });
}

function showPosition(position) {
    document.getElementById('latitudeForm').value = position.coords.latitude;
    document.getElementById('longitudeForm').value = position.coords.longitude;
    document.getElementById('gps-location').disabled = false;
}

document.addEventListener('DOMContentLoaded', function() {
    gpsLocate();

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

document.getElementById('file').addEventListener('change', function() {
    const file = this.files[0];
    const maxSize = 2 * 1024 * 1024; // 2 MB boyut sınırı

    if (file.size > maxSize) {
        Swal.fire({
            icon: 'error',
            title: 'Oops...',
            text: 'The file size exceeds the 2 MB limit. Please choose a smaller file.',
        });
        this.value = '';
    } else {
        Swal.fire({
            icon: 'success',
            title: 'Great!',
            text: 'Profile picture uploaded successfully.',
        });
        document.getElementById('imageName').textContent = file.name;
        return;
    }
});