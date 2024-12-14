function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

const csrftoken = getCookie('csrftoken');
console.log("CSRF-токен:", csrftoken); // Проверьте, что токен получен

document.getElementById("upload-image").addEventListener("change", async function (event) {
    const file = event.target.files[0];
    if (file) {
        console.log("Файл выбран: ", file.name);
        console.log("Размер файла: ", file.size, " байт");
        const reader = new FileReader();
        reader.onload = async function (e) {
            const uploadedImage = document.getElementById("uploaded-image");
            uploadedImage.src = e.target.result; // Отображаем загруженное изображение
            uploadedImage.style.objectFit = "cover"; // Заполняем блок

            // Отправляем изображение на сервер
            const formData = new FormData();
            formData.append("image", file);
            console.log("Формируем FormData с изображением");

            try {
                console.log("Отправляем POST-запрос на /ml-api/process-image/");
                const response = await fetch("/ml-api/process-image/", {
                    method: "POST",
                    headers: {
                        'X-CSRFToken': csrftoken, // Передаём CSRF-токен
                    },
                    body: formData,
                });

                if (response.ok) {
                    console.log("Запрос успешно выполнен");
                    const data = await response.json();
                    console.log("Получен ответ от сервера:", data);
                    updateUI(data); // Обновляем интерфейс с результатами
                } else {
                    console.error("Ошибка при выполнении запроса. Статус:", response.status);
                    const errorData = await response.json();
                    console.error("Ошибка:", errorData.error);
                }
            } catch (error) {
                console.error("Ошибка сети:", error);
            }
        };
        reader.readAsDataURL(file);
    } else {
        console.warn("Файл не выбран");
    }
});