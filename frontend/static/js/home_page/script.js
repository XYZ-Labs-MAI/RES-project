document.getElementById("upload-image").addEventListener("change", function (event) {
    const file = event.target.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = function (e) {
            const uploadedImage = document.getElementById("uploaded-image");
            uploadedImage.src = e.target.result; // Устанавливаем изображение
            uploadedImage.style.objectFit = "cover"; // Заполняем блок
        };
        reader.readAsDataURL(file);
    }
});
