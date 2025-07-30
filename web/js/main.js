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

    // Function to populate the item type dropdown with grouped options
    function populateItemTypeFilter(items) {
        const itemTypeFilter = document.getElementById('item-type-filter');
        const itemTypes = new Set();
        const categories = {
            Weapons: [],
            Armor: [],
            Abilities: [],
            Other: []
        };

        // Collect unique itemTypeDisplayName values
        Object.values(items).forEach(item => {
            if (item.itemTypeDisplayName) {
                itemTypes.add(item.itemTypeDisplayName);
            }
        });

        // Sort and categorize item types
        Array.from(itemTypes).sort().forEach(type => {
            if (type.toLowerCase().includes('weapon') || type.toLowerCase().includes('ornament')) {
                categories.Weapons.push(type);
            } else if (type.toLowerCase().includes('armor')) {
                categories.Armor.push(type);
            } else if (type.toLowerCase().includes('ability') || type.toLowerCase().includes('aspect') || type.toLowerCase().includes('grenade') || type.toLowerCase().includes('melee') || type.toLowerCase().includes('super') || type.toLowerCase().includes('class')) {
                categories.Abilities.push(type);
            } else {
                categories.Other.push(type);
            }
        });

        // Log categories for debugging
        console.log('Populated item type dropdown with categories:', {
            Weapons: categories.Weapons,
            Armor: categories.Armor,
            Abilities: categories.Abilities,
            Other: categories.Other
        });

        // Populate dropdown with optgroups
        itemTypeFilter.innerHTML = '<option value="">All</option>';
        for (const [category, types] of Object.entries(categories)) {
            if (types.length > 0) {
                const optgroup = document.createElement('optgroup');
                optgroup.label = category;
                types.forEach(type => {
                    const option = document.createElement('option');
                    option.value = type;
                    option.textContent = type;
                    optgroup.appendChild(option);
                });
                itemTypeFilter.appendChild(optgroup);
            }
        }
    }

    // Function to check if an item passes the filter criteria
    function passesFilter(item, hashKey, searchTerm, itemType) {
        const displayName = item.displayProperties && item.displayProperties.name ? item.displayProperties.name.toLowerCase() : '';
        const displayIcon = item.displayProperties && item.displayProperties.icon ? item.displayProperties.icon : null;
        const itemTypeName = item.itemTypeDisplayName ? item.itemTypeDisplayName : '';
        const itemHash = (item.hash !== undefined && item.hash !== null) ? String(item.hash).trim() : '';
        const keyHash = hashKey ? String(hashKey).trim() : '';

        // Debug: log hash comparison if searching by hash
        if (searchTerm && !isNaN(searchTerm.trim())) {
            debug.data('Comparing search', {search: searchTerm.trim(), itemHash, keyHash, displayName});
        }

        // Search term filter (match name or hash)
        if (searchTerm) {
            const trimmedSearch = searchTerm.trim();
            const lowerSearch = trimmedSearch.toLowerCase();
            // Match name (case-insensitive) or hash (loose comparison to key or property)
            if (!displayName.includes(lowerSearch) && itemHash != trimmedSearch && keyHash != trimmedSearch) {
                return false;
            }
        }

        // Item type filter: exact match with itemTypeDisplayName
        if (itemType && itemTypeName !== itemType) {
            return false;
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

    // Function to filter and display items (used for initial load and filter changes)
    function filterItems() {
        gridContainer.innerHTML = ''; // Clear the grid for initial load or filter change
        displayedItemsCount = 0; // Reset displayed count
        filteredItemsIndices = []; // Reset filtered indices
        itemsToDisplay = calculateItemsToDisplay();

        const searchTerm = document.getElementById('search-bar').value;
        const itemType = document.getElementById('item-type-filter').value;

        // When building sortedItems, store both key and value
        sortedItems = Object.entries(allItems)
            .map(([key, value]) => ({ key, value }))
            .sort((a, b) => (a.value.displayProperties.name || '').localeCompare(b.value.displayProperties.name || ''));

        debug.data('Total items in allItems', Object.keys(allItems).length);

        // Build filtered indices
        filteredItemsIndices = [];
        for (let i = 0; i < sortedItems.length; i++) {
            if (passesFilter(sortedItems[i].value, sortedItems[i].key, searchTerm, itemType)) {
                filteredItemsIndices.push(i);
            }
        }

        debug.data('Filtered items count', filteredItemsIndices.length);
        debug.info(`Filtering items: searchTerm='${searchTerm}', itemType='${itemType}'`);
        debug.data('Filtered item indices', filteredItemsIndices);
        appendItems(sortedItems, 0, itemsToDisplay);
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

    const debouncedFilterItems = debounce(filterItems, 300);

    // Add event listeners
    document.getElementById('search-bar').addEventListener('input', debouncedFilterItems);
    document.getElementById('item-type-filter').addEventListener('change', filterItems);

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
    fetchData(apiUrl).then(data => {
        debug.success('Fetched manifest data.');
        const itemDefinitionUrl = data.Response.jsonWorldComponentContentPaths.en.DestinyInventoryItemDefinition;
        debug.data('Item Definition URL', itemDefinitionUrl);
        fetch('https://www.bungie.net' + itemDefinitionUrl)
            .then(response => response.json())
            .then(itemData => {
                debug.success('Fetched DestinyInventoryItemDefinition data.');
                allItems = itemData;
                populateItemTypeFilter(allItems); // Populate dropdown after data is loaded
                filterItems(); // Initial display
            })
            .catch(err => debug.error('Error fetching DestinyInventoryItemDefinition:', err));
    }).catch(err => debug.error('Error fetching manifest:', err));
});