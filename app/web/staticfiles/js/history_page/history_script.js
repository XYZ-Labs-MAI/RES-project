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