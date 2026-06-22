// API Key Management
const apiKeyModal = document.getElementById("apiKeyModal");
const apiKeyInput = document.getElementById("apiKeyInput");
const submitApiKeyBtn = document.getElementById("submitApiKey");
const changeApiKeyBtn = document.getElementById("changeApiKeyBtn");
const closeModalBtn = document.getElementById("closeModalBtn");
const input = document.getElementById("images");
const previewContainer = document.getElementById("preview-container");
const form = document.querySelector("form");
const submitBtn = document.getElementById("submit-btn");

const SESSION_KEY = "gemini_api_key";

// Initialize API Key on page load
function initializeApiKey() {
    const storedKey = sessionStorage.getItem(SESSION_KEY);
    if (!storedKey) {
        apiKeyModal.style.display = "flex";
    }
}

// Submit API Key from modal
submitApiKeyBtn.addEventListener("click", function () {
    const key = apiKeyInput.value.trim();
    if (!key) {
        alert("Please enter your API key");
        return;
    }
    sessionStorage.setItem(SESSION_KEY, key);
    apiKeyModal.style.display = "none";
    apiKeyInput.value = "";
});

// Close modal without entering key
closeModalBtn.addEventListener("click", function () {
    apiKeyModal.style.display = "none";
});

// Allow Enter key to submit
apiKeyInput.addEventListener("keypress", function (e) {
    if (e.key === "Enter") {
        submitApiKeyBtn.click();
    }
});

// Change API Key button
changeApiKeyBtn.addEventListener("click", function () {
    apiKeyModal.style.display = "flex";
    apiKeyInput.focus();
});

// Image preview functionality
if (input && previewContainer) {
    input.addEventListener("change", function () {
        previewContainer.innerHTML = "";
        const files = this.files;

        for (let i = 0; i < files.length; i++) {
            const reader = new FileReader();

            reader.onload = function (e) {
                const img = document.createElement("img");
                img.src = e.target.result;
                previewContainer.appendChild(img);
            };

            reader.readAsDataURL(files[i]);
        }
    });
}

// Form submission with API key header
if (form && submitBtn) {
    form.addEventListener("submit", function (e) {
        const apiKey = sessionStorage.getItem(SESSION_KEY);
        if (!apiKey) {
            e.preventDefault();
            alert("Please enter your API key first");
            apiKeyModal.style.display = "flex";
            return;
        }

        // Add API key to form as a hidden field
        let apiKeyField = document.querySelector("input[name='api_key']");
        if (!apiKeyField) {
            apiKeyField = document.createElement("input");
            apiKeyField.type = "hidden";
            apiKeyField.name = "api_key";
            form.appendChild(apiKeyField);
        }
        apiKeyField.value = apiKey;

        submitBtn.textContent = "Loading...";
        submitBtn.disabled = true;
    });
}

// Initialize on page load
window.addEventListener("DOMContentLoaded", initializeApiKey);
