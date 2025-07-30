// Debug utility for styled console output
const debug = {
    info: (msg, ...args) => console.log(`%c[INFO] %c${msg}`, 'color: #2196f3; font-weight: bold;', 'color: inherit;', ...args),
    warn: (msg, ...args) => console.warn(`%c[WARN] %c${msg}`, 'color: #ff9800; font-weight: bold;', 'color: inherit;', ...args),
    error: (msg, ...args) => console.error(`%c[ERROR] %c${msg}`, 'color: #f44336; font-weight: bold;', 'color: inherit;', ...args),
    success: (msg, ...args) => console.log(`%c[SUCCESS] %c${msg}`, 'color: #4caf50; font-weight: bold;', 'color: inherit;', ...args),
    data: (label, data) => console.log(`%c[DATA] %c${label}:`, 'color: #9c27b0; font-weight: bold;', 'color: inherit;', data)
};

document.addEventListener('DOMContentLoaded', () => {
    const urlParams = new URLSearchParams(window.location.search);
    const itemHash = urlParams.get('itemHash');
    const loadingIndicator = document.querySelector('.loading-indicator');
    const contentContainer = document.querySelector('.content-container');

    debug.info('Page loaded.');
    debug.data('itemHash from URL', itemHash);
    const loadStart = performance.now();

    if (itemHash) {
        const apiKey = '62af834bf86c4c7bacc5f1473a0149b3';
        const apiUrl = `https://www.bungie.net/Platform/Destiny2/Manifest/DestinyInventoryItemDefinition/${itemHash}/`;
        debug.info('Fetching item data from API...');
        debug.data('API URL', apiUrl);

        loadingIndicator.style.display = 'block';
        contentContainer.style.display = 'none';

        fetch(apiUrl, {
            headers: {
                'X-API-Key': apiKey
            }
        })
        .then(response => {
            debug.success('Received response from item API.');
            return response.json();
        })
        .then(async data => {
            debug.data('Item API response', data);
            const item = data.Response;
            let perksContent = '';

            // Fetch damage type definition
            let damageTypeInfo = '';
            if (item.damageTypeHashes && item.damageTypeHashes.length > 0) {
                const damageTypeHash = item.damageTypeHashes[0];
                const damageTypeApiUrl = `https://www.bungie.net/Platform/Destiny2/Manifest/DestinyDamageTypeDefinition/${damageTypeHash}/`;
                debug.info('Fetching damage type info...');
                debug.data('Damage Type API URL', damageTypeApiUrl);
                const damageTypeResponse = await fetch(damageTypeApiUrl, { headers: { 'X-API-Key': apiKey } });
                const damageTypeData = await damageTypeResponse.json();
                debug.data('Damage Type API response', damageTypeData);
                const damageType = damageTypeData.Response;
                damageTypeInfo = `
                    <div class="weapon-detail">
                        <img src="https://www.bungie.net${damageType.displayProperties.icon}" alt="${damageType.displayProperties.name}" style="width: 30px; height: 30px;">
                        <span>${damageType.displayProperties.name}</span>
                    </div>
                `;
            } else {
                debug.warn('No damage type hashes found for item.');
            }

            // Fetch collectible definition for source information
            let sourceInfo = '';
            if (item.collectibleHash) {
                const collectibleApiUrl = `https://www.bungie.net/Platform/Destiny2/Manifest/DestinyCollectibleDefinition/${item.collectibleHash}/`;
                debug.info('Fetching collectible info...');
                debug.data('Collectible API URL', collectibleApiUrl);
                const collectibleResponse = await fetch(collectibleApiUrl, { headers: { 'X-API-Key': apiKey } });
                const collectibleData = await collectibleResponse.json();
                debug.data('Collectible API response', collectibleData);
                const collectible = collectibleData.Response;
                sourceInfo = collectible.sourceString;
            } else {
                debug.warn('No collectibleHash found for item.');
            }

            const ammoTypes = {
                1: 'Primary',
                2: 'Special',
                3: 'Heavy'
            };
            const ammoType = ammoTypes[item.equippingBlock.ammoType];
            debug.data('Ammo Type', ammoType);

            // Fetch and display stats
            let statsContent = '';
            if (item.stats && item.stats.stats) {
                const statHashes = Object.keys(item.stats.stats);
                const statDefinitions = await Promise.all(statHashes.map(statHash =>
                    fetch(`https://www.bungie.net/Platform/Destiny2/Manifest/DestinyStatDefinition/${statHash}/`, {
                        headers: { 'X-API-Key': apiKey }
                    }).then(res => res.json())
                ));

                statsContent = '<div class="stats-container">';
                for (const statDefResponse of statDefinitions) {
                    const statDef = statDefResponse.Response;
                    const statValue = item.stats.stats[statDef.hash].value;
                    statsContent += `
                        <div class="stat-bar-container">
                            <div class="stat-name">${statDef.displayProperties.name}</div>
                            <div class="stat-bar">
                                <div class="stat-bar-fill" style="width: ${statValue}%"></div>
                            </div>
                            <div class="stat-value">${statValue}</div>
                        </div>
                    `;
                }
                statsContent += '</div>';
            }


            if (item.sockets && item.sockets.socketEntries) {
                debug.info('Processing item sockets for perks...');
                const perkSocketIndexes = item.sockets.socketEntries.map((socket, index) => socket.randomizedPlugSetHash ? index : -1).filter(index => index !== -1);
                debug.data('Perk Socket Indexes', perkSocketIndexes);
                const perkSocketCategory = item.sockets.socketCategories.find(category => category.socketIndexes.some(index => perkSocketIndexes.includes(index)));
                if (perkSocketCategory) {
                    debug.success('Found perk socket category.');
                    const perkCategoryHashes = perkSocketCategory.socketIndexes;
                    const perkPromises = perkCategoryHashes.map(async (socketIndex, colIdx) => {
                        const socket = item.sockets.socketEntries[socketIndex];
                        if (socket.randomizedPlugSetHash) {
                            const plugSetApiUrl = `https://www.bungie.net/Platform/Destiny2/Manifest/DestinyPlugSetDefinition/${socket.randomizedPlugSetHash}/`;
                            debug.info('Fetching plug set info...');
                            debug.data('Plug Set API URL', plugSetApiUrl);
                            const plugSetResponse = await fetch(plugSetApiUrl, { headers: { 'X-API-Key': apiKey } });
                            const plugSetData = await plugSetResponse.json();
                            debug.data('Plug Set API response', plugSetData);
                            const plugSet = plugSetData.Response;

                            if (plugSet.reusablePlugItems) {
                                debug.success('Found reusable plug items.');
                                const plugResults = await Promise.all(plugSet.reusablePlugItems.map(async (plug) => {
                                    const plugApiUrl = `https://www.bungie.net/Platform/Destiny2/Manifest/DestinyInventoryItemDefinition/${plug.plugItemHash}/`;
                                    debug.info('Fetching plug item info...');
                                    debug.data('Plug Item API URL', plugApiUrl);
                                    try {
                                        const plugResponse = await fetch(plugApiUrl, { headers: { 'X-API-Key': apiKey } });
                                        const plugData = await plugResponse.json();
                                        const plugItem = plugData.Response;
                                        const perkDescription = plugItem.displayProperties.description ? plugItem.displayProperties.description.replace(/\n/g, '<br>') : 'No description available.';
                                        return { success: true, name: plugItem.displayProperties.name, html: `\n                                    <div class=\"perk\" data-perk-name=\"${plugItem.displayProperties.name}\" data-perk-description=\"${perkDescription}\">\n                                        <img src=\"https://www.bungie.net${plugItem.displayProperties.icon}\" alt=\"${plugItem.displayProperties.name}\" style=\"width: 50px;\">\n                                    </div>\n                                ` };
                                    } catch (err) {
                                        debug.warn(`Failed to fetch perk for plugItemHash: ${plug.plugItemHash}`);
                                        return { success: false, name: `Hash: ${plug.plugItemHash}` };
                                    }
                                }));
                                // Log summary for this column
                                const succeeded = plugResults.filter(r => r.success).map(r => r.name);
                                const failed = plugResults.filter(r => !r.success).map(r => r.name);
                                debug.data(`Perk column ${colIdx + 1} summary`, { succeeded, failed });
                                return plugResults.filter(r => r.success).map(r => r.html);
                            } else {
                                debug.warn('No reusable plug items found in plug set.');
                            }
                        }
                        return [];
                    });

                    Promise.all(perkPromises).then(perkColumns => {
                        debug.success('Perk columns loaded.');
                        perksContent = perkColumns.filter(column => column.length > 0).map(column => `<div class="perk-column">${column.join('')}</div>`).join('');
                        contentContainer.innerHTML = `
                            <div class="weapon-header">
                                <img src="https://www.bungie.net${item.displayProperties.icon}" alt="${item.displayProperties.name}">
                                <div class="weapon-info">
                                    <h1>${item.displayProperties.name}</h1>
                                    <div class="weapon-details">
                                        ${damageTypeInfo}
                                        <div class="weapon-detail">
                                            <span>${item.itemTypeDisplayName}</span>
                                        </div>
                                        <div class="weapon-detail">
                                            <span>${ammoType}</span>
                                        </div>
                                        <div class="weapon-detail">
                                            <span>${sourceInfo}</span>
                                        </div>
                                    </div>
                                    <h2>Stats</h2>
                                    ${statsContent}
                                </div>
                            </div>
                            <div class="perks-container">
                                <h2>Perks</h2>
                                <div class="perk-columns">${perksContent}</div>
                            </div>
                        `;

                        loadingIndicator.style.display = 'none';
                        contentContainer.style.display = 'block';
                    }).then(() => {
                        debug.info('Setting up perk tooltips...');
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
                        debug.success('Perk tooltips ready.');
                    });
                    } else {
                        debug.warn('No perk socket category found.');
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
                    debug.warn('No sockets or socket entries found for item.');
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
                const loadEnd = performance.now();
                debug.success(`Item loaded in ${(loadEnd - loadStart).toFixed(2)} ms.`);
            })
            .catch(error => {
                debug.error('Error fetching item data:', error);
                contentContainer.innerHTML = '<p>Error loading item data. Please try again later.</p>';
                loadingIndicator.style.display = 'none';
                contentContainer.style.display = 'block';
            });
        } else {
            debug.error('No itemHash found in URL.');
        }
    });