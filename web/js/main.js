const gridContainer = document.getElementById('grid-container');
const sidebar = document.getElementById('sidebar');
const closeSidebar = document.getElementById('close-sidebar');
const sidebarContent = document.getElementById('sidebar-content');
const navSidebar = document.getElementById('nav-sidebar');
const openNavSidebar = document.getElementById('open-nav-sidebar');
const closeNavSidebar = document.getElementById('close-nav-sidebar');

// Replace with your API key
const apiKey = '4f216a8359d4433186119caf10f09148';

// This is a placeholder for the API endpoint.
const apiUrl = 'https://www.bungie.net/Platform/Destiny2/Manifest/';

// Function to fetch data from the Bungie API
async function fetchData(url) {
    const response = await fetch(url, {
        headers: {
            'X-API-Key': apiKey
        }
    });
    return response.json();
}

// Function to calculate how many items are needed to fill the viewport
function calculateItemsToDisplay() {
    const gridContainer = document.getElementById('grid-container');
    const controlsContainer = document.querySelector('.controls-container');
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
    sidebar.style.width = '350px';
    document.getElementById('item-name').textContent = item.displayProperties.name;

    // General tab: Essential item info
    let generalContent = `
        <p><strong>Name:</strong> ${item.displayProperties.name}</p>
        <p><strong>Type:</strong> ${item.itemTypeDisplayName || 'N/A'}</p>
        <p><strong>Description:</strong> ${item.displayProperties.description || 'N/A'}</p>
        <p><strong>Icon:</strong> <img src="https://www.bungie.net${item.displayProperties.icon}" alt="${item.displayProperties.name}" style="width: 50px;"></p>
    `;
    document.getElementById('general-tab').innerHTML = generalContent;

    // Stats tab: Key stats only
    let statsContent = '<p>No stats available</p>';
    if (item.stats && item.stats.stats) {
        statsContent = '';
        for (const statId in item.stats.stats) {
            const stat = item.stats.stats[statId];
            statsContent += `<p><strong>Stat ${statId}:</strong> ${stat.value}</p>`;
        }
    }
    document.getElementById('stats-tab').innerHTML = statsContent;

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
    sidebar.style.width = '0';
}

// Function to open the left navigation sidebar
function openNavSidebarFunction() {
    navSidebar.style.width = '250px';
}

// Function to close the left navigation sidebar
function closeNavSidebarFunction() {
    navSidebar.style.width = '0';
}

// Ensure event listeners are added only once
if (openNavSidebar && closeNavSidebar && closeSidebar) {
    openNavSidebar.removeEventListener('click', openNavSidebarFunction);
    closeNavSidebar.removeEventListener('click', closeNavSidebarFunction);
    closeSidebar.removeEventListener('click', closeSidebarFunction);

    openNavSidebar.addEventListener('click', openNavSidebarFunction);
    closeNavSidebar.addEventListener('click', closeNavSidebarFunction);
    closeSidebar.addEventListener('click', closeSidebarFunction);
} else {
    console.error('Sidebar buttons not found in DOM');
}

let allItems = {};
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
function passesFilter(item, searchTerm, itemType) {
    const displayName = item.displayProperties && item.displayProperties.name ? item.displayProperties.name.toLowerCase() : '';
    const displayIcon = item.displayProperties && item.displayProperties.icon ? item.displayProperties.icon : null;
    const itemTypeName = item.itemTypeDisplayName ? item.itemTypeDisplayName : '';

    // Search term filter
    if (searchTerm && !displayName.includes(searchTerm.toLowerCase())) {
        return false;
    }

    // Item type filter: exact match with itemTypeDisplayName
    if (itemType && itemTypeName !== itemType) {
        return false;
    }

    return !!displayIcon; // Ensure item has an icon
}

// Function to filter and append items
function appendItems(startFilteredIndex, itemsToAdd) {
    const itemsArray = Object.values(allItems);
    let displayedCount = 0;
    let sampleItems = []; // For debugging: track up to 5 items

    for (let i = startFilteredIndex; i < filteredItemsIndices.length && displayedCount < itemsToAdd; i++) {
        const item = itemsArray[filteredItemsIndices[i]];
        const gridItem = document.createElement('div');
        gridItem.classList.add('grid-item');
        gridItem.innerHTML = `<img src="https://www.bungie.net${item.displayProperties.icon}" alt="${item.displayProperties.name}">`;
        (function(currentItem) {
            gridItem.addEventListener('click', () => {
                openSidebar(currentItem);
            });
        })(item);
        gridContainer.appendChild(gridItem);
        displayedCount++;
        displayedItemsCount++;
        if (sampleItems.length < 5) {
            sampleItems.push(item.displayProperties.name + ' (' + item.itemTypeDisplayName + ')');
        }
    }

    // Debug: Log the number of items appended and filter settings
    const searchTerm = document.getElementById('search-bar').value.toLowerCase();
    const itemType = document.getElementById('item-type-filter').value;
    console.log(`Appended ${displayedCount} items starting from filtered index ${startFilteredIndex}. Total displayed: ${displayedItemsCount} out of ${itemsToDisplay} requested. Total filtered items: ${filteredItemsIndices.length}. Filters: search="${searchTerm}", type="${itemType}". Sample items: ${sampleItems.join(', ')}`);
}

// Function to filter and display items (used for initial load and filter changes)
function filterItems() {
    gridContainer.innerHTML = ''; // Clear the grid for initial load or filter change
    displayedItemsCount = 0; // Reset displayed count
    filteredItemsIndices = []; // Reset filtered indices
    itemsToDisplay = calculateItemsToDisplay();

    const searchTerm = document.getElementById('search-bar').value.toLowerCase();
    const itemType = document.getElementById('item-type-filter').value;

    let itemsArray = Object.values(allItems);
    itemsArray.sort((a, b) => a.displayProperties.name.localeCompare(b.displayProperties.name));

    // Build filtered indices
    for (let i = 0; i < itemsArray.length; i++) {
        if (passesFilter(itemsArray[i], searchTerm, itemType)) {
            filteredItemsIndices.push(i);
        }
    }

    appendItems(0, itemsToDisplay);
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
        appendItems(displayedItemsCount, itemsToAdd);
        itemsToDisplay += itemsToAdd;
        setTimeout(() => { isLoadingMore = false; }, 500); // Throttle to 500ms
    }
});

// Fetch the manifest and display the data
fetchData(apiUrl).then(data => {
    const itemDefinitionUrl = data.Response.jsonWorldComponentContentPaths.en.DestinyInventoryItemDefinition;
    fetch('https://www.bungie.net' + itemDefinitionUrl)
        .then(response => response.json())
        .then(itemData => {
            allItems = itemData;
            populateItemTypeFilter(allItems); // Populate dropdown after data is loaded
            filterItems(); // Initial display
        });
});