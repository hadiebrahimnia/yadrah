
let lastSelectedText = '';
let isTranslating = false;

document.addEventListener('mouseup', function() {
    const selectedText = window.getSelection().toString().trim();
    if (selectedText.length > 0 && selectedText !== lastSelectedText && !isTranslating) {
        lastSelectedText = selectedText;
        translateSelectedText(selectedText);
    }
});

function translateSelectedText(text) {
    isTranslating = true;
    const csrftoken = getCookie('csrftoken');
    const formData = new FormData();
    formData.append('text', text);
    formData.append('target_lang', 'fa');

    fetch('/translate/', {
        method: 'POST',
        headers: {'X-CSRFToken': csrftoken},
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.translation) {
            showAlert(data.translation.substring(0, 1000) + (data.translation.length > 1000 ? "..." : ""), {
                duration: 0,
                type: 'info'
            });
        }
        isTranslating = false;
    })
    .catch(error => {
        console.error('Error:', error);
        isTranslating = false;
    });
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.startsWith(name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}


