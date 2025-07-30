// Debug utility for styled console output
const debug = {
    info: (msg, ...args) => console.log(`%c[INFO] %c${msg}`, 'color: #2196f3; font-weight: bold;', 'color: inherit;', ...args),
    warn: (msg, ...args) => console.warn(`%c[WARN] %c${msg}`, 'color: #ff9800; font-weight: bold;', 'color: inherit;', ...args),
    error: (msg, ...args) => console.error(`%c[ERROR] %c${msg}`, 'color: #f44336; font-weight: bold;', 'color: inherit;', ...args),
    success: (msg, ...args) => console.log(`%c[SUCCESS] %c${msg}`, 'color: #4caf50; font-weight: bold;', 'color: inherit;', ...args),
    data: (label, data) => console.log(`%c[DATA] %c${label}:`, 'color: #9c27b0; font-weight: bold;', 'color: inherit;', data)
};

debug.info('Main.js loaded.');

// Replace with your API key
const apiKey = '4f216a8359d4433186119caf10f09148';

// This is a placeholder for the API endpoint.
const apiUrl = 'https://www.bungie.net/Platform/Destiny2/Manifest/';
debug.data('API URL', apiUrl);

// Function to fetch data from the Bungie API
async function fetchData(url) {
    debug.info('Fetching data from API...', url);
    const response = await fetch(url, {
        headers: {
            'X-API-Key': apiKey
        }
    });
    debug.success('Received response from API.');
    return response.json();
}

document.addEventListener('DOMContentLoaded', () => {
    const gridContainer = document.getElementById('grid-container');
    const sidebar = document.getElementById('sidebar');
    const closeSidebar = document.getElementById('close-sidebar');
    const sidebarContent = document.getElementById('sidebar-content');
    const controlsContainer = document.querySelector('.controls-container');

    // Function to calculate how many items are needed to fill the viewport
    function calculateItemsToDisplay() {
        const containerWidth = gridContainer.clientWidth;
        const controlsHeight = controlsContainer ? controlsContainer.offsetHeight : 60; // Fallback to 60px
        const containerHeight = window.innerHeight - controlsHeight; // Adjust for sticky top bar
        const itemWidth = 110; // Approximate width of a grid item (100px + 10px gap)
        const itemHeight = 110; // Approximate height of a grid item
        const columns = Math.floor(containerWidth / itemWidth);
        const rows = Math.ceil(containerHeight / itemHeight);
        return Math.max(columns * rows * 2.5, 50); // Load 2.5x viewport height, minimum 50 items
    }

    // Function to open the right sidebar and display item details in tabs
    function openSidebar(item) {
        sidebar.classList.add('open');
        document.getElementById('item-name').textContent = item.displayProperties.name;

        // General tab: Essential item info
        let generalContent = `
            <p><strong>Name:</strong> ${item.displayProperties.name}</p>
            <p><strong>Type:</strong> ${item.itemTypeDisplayName || 'N/A'}</p>
            <p><strong>Description:</strong> ${item.displayProperties.description || 'N/A'}</p>
            <p><strong>Icon:</strong> <img src="https://www.bungie.net${item.displayProperties.icon}" alt="${item.displayProperties.name}" style="width: 50px;"></p>
            <button id="copy-json-button">Copy JSON</button>
        `;
        document.getElementById('general-tab').innerHTML = generalContent;

        document.getElementById('copy-json-button').addEventListener('click', () => {
            navigator.clipboard.writeText(JSON.stringify(item, null, 2));
        });

        // Stats tab: Key stats only
        let statsContent = '<p>No stats available</p>';
        if (item.stats && item.stats.stats) {
            statsContent = '';
            for (const statId in item.stats.stats) {
                const stat = item.stats.stats[statId];
                statsContent += `<p><strong>Stat ${statId}:</strong> ${stat.value}</p>`;
            }
            statsContent += `<button id="explore-stats-button">Explore Stats</button>`;
        }
        document.getElementById('stats-tab').innerHTML = statsContent;

        if (item.stats && item.stats.stats) {
            document.getElementById('explore-stats-button').addEventListener('click', () => {
                window.open(`stats.html?itemHash=${item.hash}`, '_blank');
            });
        }

        // Handle tab switching
        const tabs = document.querySelectorAll('.tab-button');
        const tabContents = document.querySelectorAll('.tab-content');
        tabs.forEach(tab => {
            tab.removeEventListener('click', tab.clickHandler); // Remove previous listeners
            tab.clickHandler = () => {
                tabs.forEach(t => t.classList.remove('active'));
                tabContents.forEach(c => c.classList.remove('active'));
                tab.classList.add('active');
                document.getElementById(`${tab.dataset.tab}-tab`).classList.add('active');
            };
            tab.addEventListener('click', tab.clickHandler);
        });
    }

    // Function to close the right sidebar
    function closeSidebarFunction() {
        sidebar.classList.remove('open');
    }

    // Attach close event listener after DOM is loaded
    if (closeSidebar) {
        closeSidebar.removeEventListener('click', closeSidebarFunction);
        closeSidebar.addEventListener('click', closeSidebarFunction);
    }

    let allItems = {};
    let sortedItems = [];
    let itemsToDisplay = calculateItemsToDisplay();
    let displayedItemsCount = 0; // Track total displayed items across all loads
    let filteredItemsIndices = []; // Store indices of items that pass the filter

    const validWeaponTypes = [
        "Auto Rifle",
        "Pulse Rifle",
        "Scout Rifle",
        "Hand Cannon",
        "Submachine Gun",
        "Sidearm",
        "Bow",
        "Shotgun",
        "Sniper Rifle",
        "Fusion Rifle",
        "Trace Rifle",
        "Grenade Launcher",
        "Rocket Launcher",
        "Machine Gun",
        "Sword",
        "Linear Fusion Rifle",
        "Glaive"
    ];

    function populateFilterMenu(items, damageTypeDefinitions) {
        const filterContainer = document.querySelector('.dropdown-content');
        const weaponTypes = new Set();
        const damageTypes = new Set();

        Object.values(items).forEach(item => {
            if (item.itemTypeDisplayName) {
                let weaponType = item.itemTypeDisplayName.replace('Exotic ', '').replace('Legendary ', '');
                if (validWeaponTypes.includes(weaponType)) {
                    weaponTypes.add(weaponType);

                    if (item.damageTypeHashes && item.damageTypeHashes.length > 0) {
                        item.damageTypeHashes.forEach(hash => {
                            const damageType = damageTypeDefinitions[hash];
                            if (damageType) {
                                damageTypes.add(damageType.displayProperties.name);
                            }
                        });
                    } else {
                        damageTypes.add('Kinetic');
                    }
                }
            }
        });

        const filterHtml = `
            <div class="filter-category">
                <a href="#">Ammo Type</a>
                <div class="dropdown-submenu">
                    <label><input type="checkbox" name="ammoType" value="1"> Primary</label>
                    <label><input type="checkbox" name="ammoType" value="2"> Special</label>
                    <label><input type="checkbox" name="ammoType" value="3"> Heavy</label>
                </div>
            </div>
            <div class="filter-category">
                <a href="#">Damage Type</a>
                <div class="dropdown-submenu">
                    ${Array.from(damageTypes).sort().map(type => `<label><input type="checkbox" name="damageType" value="${type}"> ${type}</label>`).join('')}
                </div>
            </div>
            <div class="filter-category">
                <a href="#">Weapon Type</a>
                <div class="dropdown-submenu">
                    ${Array.from(weaponTypes).sort().map(type => `<label><input type="checkbox" name="weaponType" value="${type}"> ${type}</label>`).join('')}
                </div>
            </div>
        `;

        filterContainer.innerHTML = filterHtml;
    }

    // Function to check if an item passes the filter criteria
    function passesFilter(item, hashKey, searchTerm, filters, damageTypeDefinitions) {
        const displayName = item.displayProperties && item.displayProperties.name ? item.displayProperties.name.toLowerCase() : '';
        const displayIcon = item.displayProperties && item.displayProperties.icon ? item.displayProperties.icon : null;
        const itemTypeName = item.itemTypeDisplayName ? item.itemTypeDisplayName : '';
        const itemHash = (item.hash !== undefined && item.hash !== null) ? String(item.hash).trim() : '';
        const keyHash = hashKey ? String(hashKey).trim() : '';

        // Search term filter
        if (searchTerm) {
            const trimmedSearch = searchTerm.trim();
            const lowerSearch = trimmedSearch.toLowerCase();
            if (!displayName.includes(lowerSearch) && itemHash != trimmedSearch && keyHash != trimmedSearch) {
                return false;
            }
        }

        // Ammo type filter
        if (filters.ammoType.length > 0) {
            if (!item.equippingBlock || !filters.ammoType.includes(String(item.equippingBlock.ammoType))) {
                return false;
            }
        }

        // Damage type filter
        if (filters.damageType.length > 0) {
            let itemDamageTypes = [];
            if (item.itemTypeDisplayName && validWeaponTypes.includes(item.itemTypeDisplayName.replace('Exotic ', '').replace('Legendary ', ''))) {
                if (item.damageTypeHashes && item.damageTypeHashes.length > 0) {
                    item.damageTypeHashes.forEach(hash => {
                        const damageType = damageTypeDefinitions[hash];
                        if (damageType) {
                            itemDamageTypes.push(damageType.displayProperties.name);
                        }
                    });
                } else {
                    itemDamageTypes.push('Kinetic');
                }
            }
            
            debug.data('Item Damage Types', {name: displayName, types: itemDamageTypes});

            if (itemDamageTypes.length === 0) {
                return false;
            }
            if (!filters.damageType.some(type => itemDamageTypes.includes(type))) {
                return false;
            }
        }

        // Weapon type filter
        if (filters.weaponType.length > 0) {
            if (!item.itemTypeDisplayName) {
                return false;
            }
            let weaponType = item.itemTypeDisplayName.replace('Exotic ', '').replace('Legendary ', '');
            if (!filters.weaponType.includes(weaponType)) {
                return false;
            }
        }

        return !!displayIcon; // Ensure item has an icon
    }

    // Function to filter and append items
    function appendItems(itemsArray, startFilteredIndex, itemsToAdd) {
        let displayedCount = 0;
        debug.info(`Appending ${itemsToAdd} items starting from filtered index ${startFilteredIndex}.`);
        for (let i = startFilteredIndex; i < filteredItemsIndices.length && displayedCount < itemsToAdd; i++) {
            const itemObj = itemsArray[filteredItemsIndices[i]];
            const item = itemObj.value;
            const gridItem = document.createElement('div');
            gridItem.classList.add('grid-item');
            gridItem.innerHTML = `<img src="https://www.bungie.net${item.displayProperties.icon}" alt="${item.displayProperties.name}">`;
            gridItem.addEventListener('click', () => {
                openSidebar(item);
            });
            gridContainer.appendChild(gridItem);
            displayedCount++;
            displayedItemsCount++;
        }
        debug.success(`Appended ${displayedCount} items to grid.`);
    }


    // Debounce function for search input
    function debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }


    const dropdownButton = document.querySelector('.dropdown-button');
    const dropdownContent = document.querySelector('.dropdown-content');

    dropdownButton.addEventListener('click', () => {
        dropdownContent.style.display = dropdownContent.style.display === 'block' ? 'none' : 'block';
    });

    document.querySelectorAll('.filter-category > a').forEach(a => {
        a.addEventListener('click', (event) => {
            event.preventDefault();
            const submenu = event.target.nextElementSibling;
            submenu.style.display = submenu.style.display === 'block' ? 'none' : 'block';
        });
    });

    // Infinite scroll with throttling
    let isLoadingMore = false;
    window.addEventListener('scroll', () => {
        if (isLoadingMore) return; // Prevent multiple simultaneous loads
        if (window.innerHeight + window.scrollY >= document.body.offsetHeight - 500) {
            isLoadingMore = true;
            const itemsToAdd = calculateItemsToDisplay();
            appendItems(sortedItems, displayedItemsCount, itemsToAdd);
            itemsToDisplay += itemsToAdd;
            setTimeout(() => { isLoadingMore = false; }, 500); // Throttle to 500ms
        }
    });

    // Fetch the manifest and display the data
    fetchData(apiUrl).then(async data => {
        debug.success('Fetched manifest data.');
        const itemDefinitionUrl = data.Response.jsonWorldComponentContentPaths.en.DestinyInventoryItemDefinition;
        const damageTypeDefinitionUrl = data.Response.jsonWorldComponentContentPaths.en.DestinyDamageTypeDefinition;
        debug.data('Item Definition URL', itemDefinitionUrl);
        debug.data('Damage Type Definition URL', damageTypeDefinitionUrl);

        const [itemData, damageTypeData] = await Promise.all([
            fetch('https://www.bungie.net' + itemDefinitionUrl).then(res => res.json()),
            fetch('https://www.bungie.net' + damageTypeDefinitionUrl).then(res => res.json())
        ]);

        debug.success('Fetched DestinyInventoryItemDefinition and DestinyDamageTypeDefinition data.');
        allItems = itemData;
        const damageTypeDefinitions = damageTypeData;
        populateFilterMenu(allItems, damageTypeDefinitions); // Populate dropdown after data is loaded
        
        function filterItems() {
            gridContainer.innerHTML = ''; // Clear the grid for initial load or filter change
            displayedItemsCount = 0; // Reset displayed count
            filteredItemsIndices = []; // Reset filtered indices
            itemsToDisplay = calculateItemsToDisplay();

            const searchTerm = document.getElementById('search-bar').value;
            const filters = {
                ammoType: Array.from(document.querySelectorAll('input[name="ammoType"]:checked')).map(el => el.value),
                damageType: Array.from(document.querySelectorAll('input[name="damageType"]:checked')).map(el => el.value),
                weaponType: Array.from(document.querySelectorAll('input[name="weaponType"]:checked')).map(el => el.value)
            };

            // When building sortedItems, store both key and value
            sortedItems = Object.entries(allItems)
                .map(([key, value]) => ({ key, value }))
                .sort((a, b) => (a.value.displayProperties.name || '').localeCompare(b.value.displayProperties.name || ''));

            debug.data('Total items in allItems', Object.keys(allItems).length);

            // Build filtered indices
            filteredItemsIndices = [];
            for (let i = 0; i < sortedItems.length; i++) {
                if (passesFilter(sortedItems[i].value, sortedItems[i].key, searchTerm, filters, damageTypeDefinitions)) {
                    filteredItemsIndices.push(i);
                }
            }

            debug.data('Filtered items count', filteredItemsIndices.length);
            debug.info(`Filtering items: searchTerm='${searchTerm}', filters:`, filters);
            debug.data('Filtered item indices', filteredItemsIndices);
            appendItems(sortedItems, 0, itemsToDisplay);
        }

        filterItems(); // Initial display

        const debouncedFilterItems = debounce(filterItems, 300);
        document.getElementById('search-bar').addEventListener('input', debouncedFilterItems);
        document.querySelector('.dropdown-content').addEventListener('change', filterItems);
    }).catch(err => debug.error('Error fetching manifest:', err));
});