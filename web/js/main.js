import { getManifest, getDefinitions } from './api.js';

/**
 * @file Main application logic.
 * Handles UI initialization, item grid rendering, filtering, and sidebar interactions.
 * Fetches Destiny 2 manifest and item definitions via Bungie.net API (using api.js).
 */

// Debug utility for styled console output
const debug = {
    info: (msg, ...args) => console.log(`%c[INFO] %c${msg}`, 'color: #2196f3; font-weight: bold;', 'color: inherit;', ...args),
    warn: (msg, ...args) => console.warn(`%c[WARN] %c${msg}`, 'color: #ff9800; font-weight: bold;', 'color: inherit;', ...args),
    error: (msg, ...args) => console.error(`%c[ERROR] %c${msg}`, 'color: #f44336; font-weight: bold;', 'color: inherit;', ...args),
    success: (msg, ...args) => console.log(`%c[SUCCESS] %c${msg}`, 'color: #4caf50; font-weight: bold;', 'color: inherit;', ...args),
    data: (label, data) => console.log(`%c[DATA] %c${label}:`, 'color: #9c27b0; font-weight: bold;', 'color: inherit;', data)
};

debug.info('Main.js loaded.');

// API key is now handled by the api.js module.

document.addEventListener('DOMContentLoaded', () => {
    const gridContainer = document.getElementById('grid-container');
    const sidebar = document.getElementById('sidebar');
    const closeSidebar = document.getElementById('close-sidebar');
    const sidebarContent = document.getElementById('sidebar-content');
    const controlsContainer = document.querySelector('.controls-container');

    // Function to calculate how many items are needed to fill the viewport
    function calculateItemsToDisplay() {
        const containerWidth = gridContainer.clientWidth;
        const controlsHeight = controlsContainer ? controlsContainer.offsetHeight : 60; // If it doesnt exist, defaults to 60px
        const containerHeight = window.innerHeight - controlsHeight; // Adjust for sticky top bar
        const itemWidth = 110; // Approximate width of a grid item (100px + 10px gap)
        const itemHeight = 110; // Approximate height of a grid item
        const columns = Math.floor(containerWidth / itemWidth);
        const rows = Math.ceil(containerHeight / itemHeight);
        return Math.max(columns * rows * 2.5, 50); // Load 2.5x viewport height, minimum 50 items
    }

    /**
     * Opens the sidebar and fills it with details for a specific item.
     * Uses HTML templates to create the content. - Removed innerHTML for better performance and security.
     * @param {object} item - The full data object for the item.
     */
    function openSidebar(item) {
        sidebar.classList.add('open');
        document.getElementById('item-name').textContent = item.displayProperties.name;

        // --- General Tab ---
        const generalTab = document.getElementById('general-tab');
        generalTab.innerHTML = ''; // Clear previous content before appending new.
        const generalContent = document.getElementById('sidebar-general-template').content.cloneNode(true);
        generalContent.querySelector('[data-template="item-name"]').textContent = item.displayProperties.name;
        generalContent.querySelector('[data-template="item-type"]').textContent = item.itemTypeDisplayName || 'N/A';
        generalContent.querySelector('[data-template="item-description"]').innerHTML = item.displayProperties.description || 'N/A';
        const icon = generalContent.querySelector('[data-template="item-icon"]');
        icon.src = `https://www.bungie.net${item.displayProperties.icon}`;
        icon.alt = item.displayProperties.name;
        generalTab.appendChild(generalContent);

        generalTab.querySelector('.copy-json-button').addEventListener('click', () => {
            navigator.clipboard.writeText(JSON.stringify(item, null, 2));
            debug.success('Item JSON copied to clipboard.');
        });

        // --- Stats Tab ---
        const statsTab = document.getElementById('stats-tab');
        statsTab.innerHTML = ''; // Clear previous content.
        if (item.stats && item.stats.stats) {
            const statsContent = document.getElementById('sidebar-stats-template').content.cloneNode(true);
            const statsList = statsContent.querySelector('.stats-list');
            for (const statId in item.stats.stats) {
                const stat = item.stats.stats[statId];
                const statItem = document.createElement('p');
                statItem.innerHTML = `<strong>Stat ${statId}:</strong> ${stat.value}`;
                statsList.appendChild(statItem);
            }
            statsTab.appendChild(statsContent);

            statsTab.querySelector('.explore-stats-button').addEventListener('click', () => {
                window.open(`stats.html?itemHash=${item.hash}`, '_blank');
            });
        } else {
            statsTab.innerHTML = '<p>There are no stats available for this item.</p>';
        }

        // --- Tab Switching Logic ---
        const tabs = sidebar.querySelectorAll('.tab-button');
        const tabContents = sidebar.querySelectorAll('.tab-content');
        tabs.forEach(tab => {
            tab.addEventListener('click', (e) => {
                tabs.forEach(t => t.classList.remove('active'));
                tabContents.forEach(c => c.classList.remove('active'));
                e.currentTarget.classList.add('active');
                document.getElementById(`${e.currentTarget.dataset.tab}-tab`).classList.add('active');
            });
        });
        // Activate the first tab by default.
        tabs[0].classList.add('active');
        tabContents[0].classList.add('active');
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
    let damageTypeDefinitions = {};
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

    /**
     * Populates the filter dropdown menu based on available item properties.
     * Creates filter options dynamically from the loaded item data using templates.
     */
    function populateFilterMenu(items, damageTypeDefinitions) {
        const filterContainer = document.querySelector('.dropdown-content');
        filterContainer.innerHTML = ''; // Clear existing filters to prevent duplication.

        const weaponTypes = new Set();
        const damageTypes = new Set();

        Object.values(items).forEach(item => {
            const weaponType = (item.itemTypeDisplayName || '').replace(/Exotic |Legendary /g, '');
            if (validWeaponTypes.includes(weaponType)) {
                weaponTypes.add(weaponType);
                if (item.damageTypeHashes?.length > 0) {
                    item.damageTypeHashes.forEach(hash => {
                        const damageType = damageTypeDefinitions[hash];
                        if (damageType) damageTypes.add(damageType.displayProperties.name);
                    });
                } else {
                    damageTypes.add('Kinetic'); // Default to Kinetic if no damage type is assigned.
                }
            }
        });

        const createFilterCategory = (title, name, values) => {
            const category = document.getElementById('filter-category-template').content.cloneNode(true);
            category.querySelector('a').textContent = title;
            const submenu = category.querySelector('.dropdown-submenu');
            values.forEach(value => {
                const checkboxItem = document.getElementById('filter-checkbox-template').content.cloneNode(true);
                const label = checkboxItem.querySelector('label');
                const input = checkboxItem.querySelector('input');
                input.name = name;
                input.value = value.value ?? value;
                label.append(` ${value.label ?? value}`);
                submenu.appendChild(checkboxItem);
            });
            filterContainer.appendChild(category);
        };
        
        createFilterCategory('Ammo Type', 'ammoType', [
            { label: 'Primary', value: 1 },
            { label: 'Special', value: 2 },
            { label: 'Heavy', value: 3 }
        ]);
        createFilterCategory('Damage Type', 'damageType', Array.from(damageTypes).sort());
        createFilterCategory('Weapon Type', 'weaponType', Array.from(weaponTypes).sort());
    }

    // Function to check if an item passes the filter checks.
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

    /**
     * Appends a specified number of items to the grid from the filtered list.
     * @param {Array} itemsArray - The sorted array of all items.
     * @param {number} startFilteredIndex - The starting index in the `filteredItemsIndices` array.
     * @param {number} itemsToAppend - The number of items to add to the grid.
     */
    function appendItems(itemsArray, startFilteredIndex, itemsToAppend) {
        let appendedCount = 0;
        const fragment = document.createDocumentFragment();

        for (let i = startFilteredIndex; i < filteredItemsIndices.length && appendedCount < itemsToAppend; i++) {
            const itemObj = itemsArray[filteredItemsIndices[i]];
            const item = itemObj.value;
            const gridItemContent = document.getElementById('item-template').content.cloneNode(true);
            const gridItem = gridItemContent.querySelector('.grid-item');
            const img = gridItem.querySelector('img');
            img.src = `https://www.bungie.net${item.displayProperties.icon}`;
            img.alt = item.displayProperties.name;
            gridItem.addEventListener('click', () => openSidebar(item));
            fragment.appendChild(gridItemContent);
            appendedCount++;
        }
        gridContainer.appendChild(fragment);
        displayedItemsCount += appendedCount;
        debug.success(`Appended ${appendedCount} new items to the grid.`);
    }


    // Debounce function for search input
    // This function limits how often the filter function is called when typing in the search bar.
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
    // This will load more items when the user scrolls near the bottom of the page.
    let isLoadingMore = false;
    window.addEventListener('scroll', () => {
        if (isLoadingMore) return; // Prevent multiple simultaneous loads
        if (window.innerHeight + window.scrollY >= document.body.offsetHeight - 500) {
            isLoadingMore = true;
            const itemsToAdd = calculateItemsToDisplay();
            appendItems(sortedItems, displayedItemsCount, itemsToAdd);
            itemsToDisplay += itemsToAdd;
            setTimeout(() => { isLoadingMore = false; }, 500); // Throttle to 500ms
            //Improve performance by throttling the scroll event
        }
    });

    /**
     * The main initialization function for the application.
     * Fetches all the necessary data from the API and sets up event listeners.
     */
    async function initialize() {
        try {
            debug.info('Initializing application...');
            const manifest = await getManifest();
            debug.success('Manifest loaded.');

            // Fetch item and damage type definitions at the same time.
            const [itemData, dmgTypeData] = await Promise.all([
                getDefinitions(manifest.jsonWorldComponentContentPaths.en.DestinyInventoryItemDefinition),
                getDefinitions(manifest.jsonWorldComponentContentPaths.en.DestinyDamageTypeDefinition)
            ]);
            
            allItems = itemData;
            damageTypeDefinitions = dmgTypeData;
            debug.success('Item and Damage Type definitions loaded.');

            // Sort items alphabetically for consistent ordering.
            sortedItems = Object.entries(allItems)
                .map(([key, value]) => ({ key, value }))
                .sort((a, b) => (a.value.displayProperties.name || '').localeCompare(b.value.displayProperties.name || ''));
            
            // WIth the data loaded, populate the filter UI and display the initial item grid.
            populateFilterMenu(allItems, damageTypeDefinitions);
            filterAndDisplayItems();
            
            // --- Event Listeners ---
            const searchBar = document.getElementById('search-bar');
            const dropdownContent = document.querySelector('.dropdown-content');

            closeSidebar.addEventListener('click', closeSidebarFunction);
            searchBar.addEventListener('input', debounce(filterAndDisplayItems, 300));
            dropdownContent.addEventListener('change', filterAndDisplayItems);
            
            debug.success('Application initialized successfully.');
        } catch (err) {
            debug.error('Application initialization failed:', err);
            // The api.js module will display an error on the page if config fails.
        }
    }

    /**
     * Filters all items based on current criteria and updates the grid.
     */
    function filterAndDisplayItems() {
        gridContainer.innerHTML = ''; // Clear the grid for new results.
        displayedItemsCount = 0;

        const searchTerm = document.getElementById('search-bar').value.trim().toLowerCase();
        const filters = {
            ammoType: Array.from(document.querySelectorAll('input[name="ammoType"]:checked')).map(el => el.value),
            damageType: Array.from(document.querySelectorAll('input[name="damageType"]:checked')).map(el => el.value),
            weaponType: Array.from(document.querySelectorAll('input[name="weaponType"]:checked')).map(el => el.value)
        };

        // Re-build the list of filtered item indices.
        filteredItemsIndices = [];
        for (let i = 0; i < sortedItems.length; i++) {
            if (passesFilter(sortedItems[i].value, sortedItems[i].key, searchTerm, filters, damageTypeDefinitions)) {
                filteredItemsIndices.push(i);
            }
        }

        debug.info(`Found ${filteredItemsIndices.length} items matching filters.`);
        appendItems(sortedItems, 0, calculateItemsToDisplay());
    }

    // Start the application
    initialize();
});