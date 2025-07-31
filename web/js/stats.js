/**
 * @file This script handles the detailed item statistics page (stats.html).
 * It fetches data for a single item and populates the UI with its stats and perks.
 */

import {
    getInventoryItemDefinition,
    getStatDefinition,
    getDamageTypeDefinition,
    getCollectibleDefinition,
    getPlugSetDefinition
} from './api.js';

// Simple debug utility for styled console output.
const debug = {
    info: (msg, ...args) => console.log(`%c[INFO] %c${msg}`, 'color: #2196f3; font-weight: bold;', 'color: inherit;', ...args),
    warn: (msg, ...args) => console.warn(`%c[WARN] %c${msg}`, 'color: #ff9800; font-weight: bold;', 'color: inherit;', ...args),
    error: (msg, ...args) => console.error(`%c[ERROR] %c${msg}`, 'color: #f44336; font-weight: bold;', 'color: inherit;', ...args),
    success: (msg, ...args) => console.log(`%c[SUCCESS] %c${msg}`, 'color: #4caf50; font-weight: bold;', 'color: inherit;', ...args),
    data: (label, data) => console.log(`%c[DATA] %c${label}:`, 'color: #9c27b0; font-weight: bold;', 'color: inherit;', data)
};

/**
 * Populates the header section of the page with the item's primary details.
 * @param {object} item - The item's definition data.
 * @param {string} sourceInfo - The source string for the item.
 */
async function populateWeaponHeader(item, sourceInfo) {
    document.querySelector('[data-template="weapon-name"]').textContent = item.displayProperties.name;
    document.querySelector('[data-template="weapon-icon"]').src = `https://www.bungie.net${item.displayProperties.icon}`;
    document.querySelector('[data-template="weapon-type"]').textContent = item.itemTypeDisplayName;
    document.querySelector('[data-template="weapon-source"]').textContent = sourceInfo || 'Source not available.';

    // Ammo Type
    const ammoTypes = {
        1: { name: 'Primary', icon: 'images/ammo-primary.svg' },
        2: { name: 'Special', icon: 'images/ammo-special.svg' },
        3: { name: 'Heavy', icon: 'images/ammo-heavy.svg' }
    };
    const ammoTypeDetails = ammoTypes[item.equippingBlock.ammoType];
    if (ammoTypeDetails) {
        document.querySelector('[data-template="ammo-icon"]').src = ammoTypeDetails.icon;
        document.querySelector('[data-template="ammo-type"]').textContent = ammoTypeDetails.name;
    }

    // Damage Type
    const damageTypeContainer = document.querySelector('.damage-type-container');
    if (item.damageTypeHashes && item.damageTypeHashes.length > 0) {
        const damageType = await getDamageTypeDefinition(item.damageTypeHashes[0]);
        if (damageType && damageType.displayProperties.hasIcon) {
            damageTypeContainer.querySelector('img').src = `https://www.bungie.net${damageType.displayProperties.icon}`;
            damageTypeContainer.querySelector('span').textContent = damageType.displayProperties.name;
        } else {
            damageTypeContainer.style.display = 'none';
        }
    } else {
        damageTypeContainer.style.display = 'none';
    }
}

/**
 * Populates the stats section of the page.
 * @param {object} item - The item's definition data.
 */
async function populateStats(item) {
    const statsContainer = document.querySelector('.stats-container');
    statsContainer.innerHTML = ''; // Clear any placeholder content.

    if (!item.stats || !item.stats.stats) {
        statsContainer.innerHTML = '<p>No stats available for this item.</p>';
        return;
    }

    const statHashes = Object.keys(item.stats.stats);
    const statTemplate = document.getElementById('stat-bar-template');

    for (const statHash of statHashes) {
        const statDef = await getStatDefinition(statHash);
        const statValue = item.stats.stats[statHash].value;

        const statElement = statTemplate.content.cloneNode(true);
        statElement.querySelector('.stat-name').textContent = statDef.displayProperties.name;
        statElement.querySelector('.stat-value').textContent = statValue;
        const statBarFill = statElement.querySelector('.stat-bar-fill');
        statBarFill.style.setProperty('--stat-bar-width', `${statValue}%`);

        statsContainer.appendChild(statElement);
    }
}

/**
 * Fetches and populates the perks for the item.
 * @param {object} item - The item's definition data.
 */
async function populatePerks(item) {
    const perksContainer = document.querySelector('.perk-columns');
    perksContainer.innerHTML = '';

    if (!item.sockets || !item.sockets.socketCategories) {
        perksContainer.innerHTML = '<p>No perk information available.</p>';
        return;
    }
    
    const perkSocketCategory = item.sockets.socketCategories.find(cat => cat.socketCategoryHash === 4241085061);
    if (!perkSocketCategory) {
        perksContainer.innerHTML = '<p>No primary perk sockets found.</p>';
        return;
    }

    const perkTemplate = document.getElementById('perk-template');
    const perkColumnTemplate = document.getElementById('perk-column-template');

    for (const socketIndex of perkSocketCategory.socketIndexes) {
        const socket = item.sockets.socketEntries[socketIndex];
        const plugSetHash = socket.randomizedPlugSetHash || socket.reusablePlugSetHash;
        
        if (plugSetHash) {
            const plugSet = await getPlugSetDefinition(plugSetHash);
            if (plugSet.reusablePlugItems) {
                const column = perkColumnTemplate.content.cloneNode(true);
                const perkColumn = column.querySelector('.perk-column');
                
                for (const plug of plugSet.reusablePlugItems) {
                    const plugItem = await getInventoryItemDefinition(plug.plugItemHash);
                    if (!plugItem.displayProperties.name || !plugItem.displayProperties.hasIcon) continue;

                    const perkElement = perkTemplate.content.cloneNode(true);
                    const perkDiv = perkElement.querySelector('.perk');
                    perkDiv.dataset.perkName = plugItem.displayProperties.name;
                    perkDiv.dataset.perkDescription = plugItem.displayProperties.description || 'No description available.';
                    perkElement.querySelector('img').src = `https://www.bungie.net${plugItem.displayProperties.icon}`;
                    perkElement.querySelector('img').alt = plugItem.displayProperties.name;
                    perkColumn.appendChild(perkElement);
                }
                if(perkColumn.childElementCount > 0) perksContainer.appendChild(column);
            }
        }
    }
    if(perksContainer.childElementCount > 0) setupPerkTooltips();
}

/**
 * Sets up the hover tooltips for all perk icons.
 */
function setupPerkTooltips() {
    const perks = document.querySelectorAll('.perk');
    const tooltip = document.querySelector('.perk-tooltip');

    perks.forEach(perk => {
        perk.addEventListener('mouseenter', (e) => {
            const name = e.currentTarget.dataset.perkName;
            const description = e.currentTarget.dataset.perkDescription;
            tooltip.innerHTML = `<h3>${name}</h3><p>${description.replace(/\n/g, '<br>')}</p>`;
            tooltip.style.display = 'block';
        });

        perk.addEventListener('mousemove', e => {
            tooltip.style.left = `${e.pageX + 15}px`;
            tooltip.style.top = `${e.pageY + 15}px`;
        });

        perk.addEventListener('mouseleave', () => {
            tooltip.style.display = 'none';
        });
    });
}

/**
 * Main initialization function for the stats page.
 */
document.addEventListener('DOMContentLoaded', async () => {
    const urlParams = new URLSearchParams(window.location.search);
    const itemHash = urlParams.get('itemHash');
    const loadingIndicator = document.querySelector('.loading-indicator');
    const contentContainer = document.querySelector('.content-container');

    if (!itemHash) {
        contentContainer.innerHTML = '<h1>No Item Specified</h1><p>Please provide an item hash in the URL.</p>';
        loadingIndicator.style.display = 'none';
        contentContainer.style.display = 'block';
        return;
    }

    try {
        debug.info(`Fetching data for item hash: ${itemHash}`);
        const item = await getInventoryItemDefinition(itemHash);
        debug.data('Item Definition', item);

        let sourceInfo = 'Source not available.';
        if (item.collectibleHash) {
            const collectible = await getCollectibleDefinition(item.collectibleHash);
            sourceInfo = collectible.sourceString;
        }

        await Promise.all([
            populateWeaponHeader(item, sourceInfo),
            populateStats(item),
            populatePerks(item)
        ]);

        loadingIndicator.style.display = 'none';
        contentContainer.style.display = 'block';
        debug.success('Successfully displayed item stats.');

    } catch (err) {
        debug.error('Failed to load item stats:', err);
        loadingIndicator.style.display = 'none';
        contentContainer.innerHTML = '<h1>Error</h1><p>Could not load item data. Please check the console for details.</p>';
        contentContainer.style.display = 'block';
    }
});