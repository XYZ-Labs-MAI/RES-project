// Функция для создания карточки из шаблона
function createHistoryCard(data) {
    const template = document.getElementById("history-card-template").content.cloneNode(true);
    const card = template.querySelector(".history-card");

    const image = card.querySelector(".history-card__image");
    image.src = data.imageSrc;
    image.alt = data.title;

    card.querySelector(".history-card__title").textContent = data.title;
    card.querySelector(".history-card__date").textContent = data.date;

    // Обработчик клика для открытия попапа
    card.addEventListener("click", function (event) {
        if (!event.target.classList.contains("history-card__delete")) {
            openPopup(data);
        }
    });

    // Обработчик для удаления карточки
    const deleteButton = card.querySelector(".history-card__delete");
    deleteButton.addEventListener("click", function (event) {
        event.stopPropagation();
        localStorage.removeItem(data.id);
        card.remove();
    });

    return card;
}

// Функция для открытия попапа (без innerHTML)
function openPopup(data) {
    const popup = document.createElement("div");
    popup.className = "popup";

    const popupContent = document.createElement("div");
    popupContent.className = "popup__content";

    const closeButton = document.createElement("span");
    closeButton.className = "popup__close";
    closeButton.textContent = "×";
    closeButton.addEventListener("click", () => popup.remove());

    const title = document.createElement("h2");
    title.className = "popup__title";
    title.textContent = data.title;

    const image = document.createElement("img");
    image.className = "popup__image";
    image.src = data.imageSrc;
    image.alt = data.title;
    image.style.width = "100%";

    const details = document.createElement("div");
    details.className = "popup__details";
    details.innerHTML = `<p>Самолет: 98%</p><p>Машина: 95%</p><p>Катер: 90%</p>`;

    popupContent.appendChild(closeButton);
    popupContent.appendChild(title);
    popupContent.appendChild(image);
    popupContent.appendChild(details);
    popup.appendChild(popupContent);

    document.body.appendChild(popup);
    popup.style.display = "flex";
}

// Загрузка данных из localStorage и отображение карточек
document.addEventListener("DOMContentLoaded", function () {
    const historyCardsContainer = document.getElementById("history-cards");
    historyCardsContainer.innerHTML = "";

    for (let i = 0; i < localStorage.length; i++) {
        const key = localStorage.key(i);
        const data = JSON.parse(localStorage.getItem(key));
        const card = createHistoryCard(data);
        historyCardsContainer.appendChild(card);
    }
});

document.addEventListener("DOMContentLoaded", function () {
    const historyCardsContainer = document.getElementById("history-cards");
    historyCardsContainer.innerHTML = "";

    // Собираем все данные из localStorage в массив
    const cardsData = [];
    for (let i = 0; i < localStorage.length; i++) {
        const key = localStorage.key(i);
        const data = JSON.parse(localStorage.getItem(key));
        cardsData.push({ id: key, ...data });
    }

    // Сортируем массив по дате (предполагаем, что data.date - это строка в формате ISO)
    cardsData.sort((a, b) => new Date(b.date) - new Date(a.date));

    // Создаем и добавляем карточки в контейнер
    cardsData.forEach(data => {
        const card = createHistoryCard(data);
        historyCardsContainer.appendChild(card);
    });
});