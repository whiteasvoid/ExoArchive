document.addEventListener('DOMContentLoaded', () => {
    const urlParams = new URLSearchParams(window.location.search);
    const itemHash = urlParams.get('itemHash');
    const loadingIndicator = document.querySelector('.loading-indicator');
    const contentContainer = document.querySelector('.content-container');

    if (itemHash) {
        const apiKey = '62af834bf86c4c7bacc5f1473a0149b3';
        const apiUrl = `https://www.bungie.net/Platform/Destiny2/Manifest/DestinyInventoryItemDefinition/${itemHash}/`;

        loadingIndicator.style.display = 'block';
        contentContainer.style.display = 'none';

        fetch(apiUrl, {
            headers: {
                'X-API-Key': apiKey
            }
        })
        .then(response => response.json())
        .then(async data => {
            const item = data.Response;
            let perksContent = '';
            if (item.sockets && item.sockets.socketEntries) {
                const perkSocketIndexes = item.sockets.socketEntries.map((socket, index) => socket.randomizedPlugSetHash ? index : -1).filter(index => index !== -1);
                const perkSocketCategory = item.sockets.socketCategories.find(category => category.socketIndexes.some(index => perkSocketIndexes.includes(index)));
                if (perkSocketCategory) {
                    const perkCategoryHashes = perkSocketCategory.socketIndexes;
                    const perkPromises = perkCategoryHashes.map(async (socketIndex) => {
                    const socket = item.sockets.socketEntries[socketIndex];
                    if (socket.randomizedPlugSetHash) {
                        const plugSetApiUrl = `https://www.bungie.net/Platform/Destiny2/Manifest/DestinyPlugSetDefinition/${socket.randomizedPlugSetHash}/`;
                        const plugSetResponse = await fetch(plugSetApiUrl, { headers: { 'X-API-Key': apiKey } });
                        const plugSetData = await plugSetResponse.json();
                        const plugSet = plugSetData.Response;

                        if (plugSet.reusablePlugItems) {
                            const plugPromises = plugSet.reusablePlugItems.map(async (plug) => {
                                const plugApiUrl = `https://www.bungie.net/Platform/Destiny2/Manifest/DestinyInventoryItemDefinition/${plug.plugItemHash}/`;
                                const plugResponse = await fetch(plugApiUrl, { headers: { 'X-API-Key': apiKey } });
                                const plugData = await plugResponse.json();
                                const plugItem = plugData.Response;
                                const perkDescription = plugItem.displayProperties.description ? plugItem.displayProperties.description.replace(/\n/g, '<br>') : 'No description available.';
                                return `
                                    <div class="perk" data-perk-name="${plugItem.displayProperties.name}" data-perk-description="${perkDescription}">
                                        <img src="https://www.bungie.net${plugItem.displayProperties.icon}" alt="${plugItem.displayProperties.name}" style="width: 50px;">
                                    </div>
                                `;
                            });
                            return Promise.all(plugPromises);
                        }
                    }
                    return [];
                });

                Promise.all(perkPromises).then(perkColumns => {
                    perksContent = perkColumns.map(column => `<div class="perk-column">${column.join('')}</div>`).join('');
                    contentContainer.innerHTML = `
                        <div class="weapon-header">
                            <img src="https://www.bungie.net${item.displayProperties.icon}" alt="${item.displayProperties.name}">
                            <div class="weapon-info">
                                <h1>${item.displayProperties.name}</h1>
                                <h2>Perks</h2>
                            </div>
                        </div>
                        <div class="perks-container">${perksContent}</div>
                    `;

                    loadingIndicator.style.display = 'none';
                    contentContainer.style.display = 'block';
                }).then(() => {
                    const perks = document.querySelectorAll('.perk');
                    const tooltip = document.createElement('div');
                    tooltip.className = 'perk-tooltip';
                    document.body.appendChild(tooltip);

                    perks.forEach(perk => {
                        perk.addEventListener('mouseenter', () => {
                            const name = perk.dataset.perkName;
                            const description = perk.dataset.perkDescription;
                            tooltip.innerHTML = `<h3>${name}</h3><p>${description}</p>`;
                            tooltip.style.display = 'block';
                        });

                        perk.addEventListener('mousemove', e => {
                            tooltip.style.left = `${e.pageX + 10}px`;
                            tooltip.style.top = `${e.pageY + 10}px`;
                        });

                        perk.addEventListener('mouseleave', () => {
                            tooltip.style.display = 'none';
                        });
                    });
                });
                } else {
                    contentContainer.innerHTML = `
                        <div class="weapon-header">
                            <img src="https://www.bungie.net${item.displayProperties.icon}" alt="${item.displayProperties.name}">
                            <div class="weapon-info">
                                <h1>${item.displayProperties.name}</h1>
                                <h2>Perks</h2>
                            </div>
                        </div>
                        <p>No perks available for this item.</p>
                    `;
                    loadingIndicator.style.display = 'none';
                    contentContainer.style.display = 'block';
                }
            } else {
                contentContainer.innerHTML = `
                    <div class="weapon-header">
                        <img src="https://www.bungie.net${item.displayProperties.icon}" alt="${item.displayProperties.name}">
                        <div class="weapon-info">
                            <h1>${item.displayProperties.name}</h1>
                            <h2>Perks</h2>
                        </div>
                    </div>
                    <p>No perks available for this item.</p>
                `;
                loadingIndicator.style.display = 'none';
                contentContainer.style.display = 'block';
            }
        })
        .catch(error => {
            console.error('Error fetching item data:', error);
            contentContainer.innerHTML = '<p>Error loading item data. Please try again later.</p>';
            loadingIndicator.style.display = 'none';
            contentContainer.style.display = 'block';
        });
    }
});
