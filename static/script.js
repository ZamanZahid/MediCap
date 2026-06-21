const input = document.getElementById("images");
const previewContainer = document.getElementById("preview-container");
const form = document.querySelector("form");
const submitBtn = document.getElementById("submit-btn");

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

if (form && submitBtn) {
    form.addEventListener("submit", function () {
        submitBtn.textContent = "Loading...";
        submitBtn.disabled = true;
    });
}
