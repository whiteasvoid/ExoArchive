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
            let perksContent = '';
            if (item.sockets && item.sockets.socketEntries) {
                const perkPromises = item.sockets.socketEntries.map(socket => {
                    if (socket.randomizedPlugSetHash) {
                        const plugSetApiUrl = `https://www.bungie.net/Platform/Destiny2/Manifest/DestinyPlugSetDefinition/${socket.randomizedPlugSetHash}/`;
                        return fetch(plugSetApiUrl, { headers: { 'X-API-Key': apiKey } })
                            .then(response => response.json())
                            .then(plugSetData => {
                                const plugSet = plugSetData.Response;
                                if (plugSet.reusablePlugItems) {
                                    return Promise.all(plugSet.reusablePlugItems.map(plug => {
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
                                return [];
                            });
                    }
                    return Promise.resolve([]);
                });

                Promise.all(perkPromises).then(perkColumns => {
                    perksContent = perkColumns.map(column => `<div class="perk-column">${column.join('')}</div>`).join('');
                    container.innerHTML = `
                        <h1>${item.displayProperties.name}</h1>
                        <img src="https://www.bungie.net${item.displayProperties.icon}" alt="${item.displayProperties.name}" style="width: 100px;">
                        <h2>Perks</h2>
                        <div class="perks-container">${perksContent}</div>
                    `;
                });
            } else {
                container.innerHTML = `
                    <h1>${item.displayProperties.name}</h1>
                    <img src="https://www.bungie.net${item.displayProperties.icon}" alt="${item.displayProperties.name}" style="width: 100px;">
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
