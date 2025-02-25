// script.js (public/script.js)

function showLoader() {
    document.getElementById('loader').style.display = 'block';
}

function hideLoader() {
    document.getElementById('loader').style.display = 'none';
}

// Sample data (now with more varied objects)
// remove when we have normal calls
const sampleData = [];
for (let i = 1; i <= 100; i++) {
    const objects = [];
    // More realistic object distribution
    if (i % 3 === 0) objects.push("car");
    if (i % 2 === 0) objects.push("person");
    if (i % 5 === 0) objects.push("tree");
    if (i % 7 === 0) objects.push("dog");
    if (i % 11 === 0) objects.push("cat");
    if (i % 4 === 0) objects.push('bicycle');
    if (i % 6 === 0) objects.push("building");

    sampleData.push({
        id: i,
        date: new Date(2023, 9, i),
        filename: `image${i}.jpg`,
        detectedObjects: objects,
    });
}

let currentPage = 1;
const itemsPerPage = 10;
let isFetching = false;

function fetchHistoryData() {
    if (isFetching) return;
    isFetching = true;
    showLoader();

    setTimeout(() => {
        const startIndex = (currentPage - 1) * itemsPerPage;
        const endIndex = startIndex + itemsPerPage;
        const newData = sampleData.slice(startIndex, endIndex);

        hideLoader();
        populateTable(newData);
        currentPage++;
        isFetching = false;
    }, 500);
}

function populateTable(data) {
    const tableBody = document.getElementById('history-table-body');

    if (data.length === 0 && currentPage === 1) {
        tableBody.innerHTML = `<tr><td colspan="5" style="text-align: center;">No history data available.</td></tr>`;
        return;
    }

    data.forEach(item => {
        const row = document.createElement('tr');

        // Count occurrences of each object
        const objectCounts = {};
        item.detectedObjects.forEach(obj => {
            objectCounts[obj] = (objectCounts[obj] || 0) + 1;
        });

        // Create the list items with counts
        const objectListItems = Object.entries(objectCounts)
            .map(([object, count]) => `<li>${object} (${count})</li>`)
            .join('');

        row.innerHTML = `
            <td data-label="ID">${item.id}</td>
            <td data-label="Date">${formatDate(item.date)}</td>
            <td data-label="Filename">${item.filename}</td>
            <td data-label="Detected Objects">
                <ul class="objects-list">
                    ${objectListItems}
                </ul>
                <p class="object-count">Total: ${item.detectedObjects.length}</p>
            </td>
            <td data-label="More"><a href="/request/${item.id}" class="more-button">More</a></td>
        `;
        tableBody.appendChild(row);
    });
}

function formatDate(dateString){
    try {
        const date = new Date(dateString);
        return date.toLocaleDateString();
    } catch(error){
        return "Invalid Date";
    }
}

// Initial load
document.addEventListener('DOMContentLoaded', fetchHistoryData);

// Lazy loading on scroll
window.addEventListener('scroll', () => {
    if ((window.innerHeight + window.scrollY) >= document.body.offsetHeight - 200) {
        if (currentPage * itemsPerPage < sampleData.length )
            fetchHistoryData();
    }
});