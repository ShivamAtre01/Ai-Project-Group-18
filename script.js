// Fetch available languages and populate the select dropdown
fetch('http://localhost:8000/languages')
    .then(response => response.json())
    .then(languages => {
        const languageSelect = document.getElementById('language');
        const currentOptions = Array.from(languageSelect.options).map(opt => opt.value);
        
        Object.entries(languages)
            .sort((a, b) => a[1].localeCompare(b[1]))
            .forEach(([code, name]) => {
                if (!currentOptions.includes(code)) {
                    const option = new Option(name, code);
                    languageSelect.add(option);
                }
            });
    })
    .catch(error => console.error('Error loading languages:', error));

document.getElementById('verseLookupForm').addEventListener('submit', function(event) {
    event.preventDefault();

    const chapter = document.getElementById('chapter').value;
    const verse = document.getElementById('verse').value;
    const language = document.getElementById('language').value;
    const languageName = document.getElementById('language').options[document.getElementById('language').selectedIndex].text;

    // Clear previous results
    document.getElementById('hindiText').textContent = '';
    document.getElementById('englishText').textContent = '';
    document.getElementById('translatedText').textContent = '';
    
    // Show loading state
    document.getElementById('result').style.opacity = '0.5';

    fetch(`http://localhost:8000/lookup?chapter=${chapter}&verse=${verse}&language=${language}`)
        .then(response => response.json())
        .then(data => {
            document.getElementById('result').style.opacity = '1';
            
            if (data.error) {
                throw new Error(data.error);
            }

            document.getElementById('hindiText').textContent = data.hindi;
            document.getElementById('englishText').textContent = data.english;
            document.getElementById('translatedText').textContent = data.translated;
            document.getElementById('translatedTitle').textContent = `${languageName} Translation`;
            
            // Show all translation boxes
            document.querySelectorAll('.translation-box').forEach(box => {
                box.style.display = 'block';
            });
        })
        .catch(error => {
            document.getElementById('result').style.opacity = '1';
            alert('Error: ' + error.message);
        });
});