document.addEventListener('DOMContentLoaded', () => {
    const urlParams = new URLSearchParams(window.location.search);
    const itemHash = urlParams.get('itemHash');

    if (itemHash) {
        const apiKey = '62af834bf86c4c7bacc5f1473a0149b3';
        const apiUrl = `https://www.bungie.net/Platform/Destiny2/Manifest/DestinyInventoryItemDefinition/${itemHash}/`;

        fetch(apiUrl, {
            headers: {
                'X-API-Key': apiKey
            }
        })
        .then(response => response.json())
        .then(data => {
            const item = data.Response;
            const container = document.querySelector('.container');

            let statsContent = '';
            if (item.stats && item.stats.stats) {
                for (const statId in item.stats.stats) {
                    const stat = item.stats.stats[statId];
                    statsContent += `<p><strong>Stat ${statId}:</strong> ${stat.value}</p>`;
                }
            } else {
                statsContent = '<p>No stats available for this item.</p>';
            }

            let perksContent = '';
            if (item.sockets && item.sockets.socketCategories) {
                const perkCategoryHashes = [4241085061, 3956125808];
                const perkSocketIndexes = new Set();
                item.sockets.socketCategories.forEach(category => {
                    if (perkCategoryHashes.includes(category.socketCategoryHash)) {
                        category.socketIndexes.forEach(index => perkSocketIndexes.add(index));
                    }
                });

                const perkPromises = Array.from(perkSocketIndexes).map(socketIndex => {
                    const socket = item.sockets.socketEntries[socketIndex];
                    if (socket.reusablePlugItems) {
                        return Promise.all(socket.reusablePlugItems.map(plug => {
                            const plugApiUrl = `https://www.bungie.net/Platform/Destiny2/Manifest/DestinyInventoryItemDefinition/${plug.plugItemHash}/`;
                            return fetch(plugApiUrl, { headers: { 'X-API-Key': apiKey } })
                                .then(response => response.json())
                                .then(plugData => {
                                    const plugItem = plugData.Response;
                                    return `
                                        <div class="perk">
                                            <img src="https://www.bungie.net${plugItem.displayProperties.icon}" alt="${plugItem.displayProperties.name}" style="width: 50px;">
                                            <p>${plugItem.displayProperties.name}</p>
                                        </div>
                                    `;
                                });
                        }));
                    }
                    return Promise.resolve([]);
                });

                Promise.all(perkPromises).then(perkColumns => {
                    perksContent = perkColumns.map(column => `<div class="perk-column">${column.join('')}</div>`).join('');
                    container.innerHTML = `
                        <h1>${item.displayProperties.name}</h1>
                        <img src="https://www.bungie.net${item.displayProperties.icon}" alt="${item.displayProperties.name}" style="width: 100px;">
                        <h2>Stats</h2>
                        ${statsContent}
                        <h2>Perks</h2>
                        <div class="perks-container">${perksContent}</div>
                    `;
                });
            } else {
                container.innerHTML = `
                    <h1>${item.displayProperties.name}</h1>
                    <img src="https://www.bungie.net${item.displayProperties.icon}" alt="${item.displayProperties.name}" style="width: 100px;">
                    <h2>Stats</h2>
                    ${statsContent}
                    <h2>Perks</h2>
                    <p>No perks available for this item.</p>
                `;
            }
        })
        .catch(error => {
            console.error('Error fetching item data:', error);
            const container = document.querySelector('.container');
            container.innerHTML = '<p>Error loading item data. Please try again later.</p>';
        });
    }
});
