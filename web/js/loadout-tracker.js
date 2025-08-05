import { getPlugSetDefinition } from './api.js';

document.addEventListener('DOMContentLoaded', () => {
    const searchButton = document.getElementById('search-button');
    const searchInput = document.getElementById('search-input');
    const resultsContainer = document.getElementById('results-container');

    let currentMembershipType = null;
    let currentMembershipId = null;
    let refreshInterval = null;

    const classMap = {
        0: 'Titan',
        1: 'Hunter',
        2: 'Warlock'
    };

    const raceMap = {
        0: 'Human',
        1: 'Awoken',
        2: 'Exo'
    };

    const genderMap = {
        0: 'Male',
        1: 'Female'
    };

    const slotHashes = {
        kinetic: 1498876634,
        energy: 2465295065,
        power: 953998645,
        helmet: 3448274439,
        gauntlets: 3551918588,
        chest: 14239492,
        legs: 20886954,
        classItem: 1585787867,
    };

    async function fetchItemDefinition(itemHash, retries = 3, delay = 1000) {
        const url = `https://www.bungie.net/Platform/Destiny2/Manifest/DestinyInventoryItemDefinition/${itemHash}/`;
        for (let i = 0; i < retries; i++) {
            try {
                const response = await fetch(`/api/proxy?url=${encodeURIComponent(url)}`);
                if (!response.ok) {
                    throw new Error(`Bungie API request for item definition failed with status ${response.status}`);
                }
                const data = await response.json();
                if (data.ErrorCode !== 1) {
                    throw new Error(`Bungie API Error for Item Definition: ${data.Message}`);
                }
                return data.Response;
            } catch (error) {
                console.error(`Error fetching item definition for hash ${itemHash} (attempt ${i + 1}/${retries}):`, error);
                if (i < retries - 1) {
                    await new Promise(res => setTimeout(res, delay));
                } else {
                    return null;
                }
            }
        }
    }

    async function getArmorMods(item) {
        let modsHtml = '<div class="item-mods">';
        if (item.sockets) {
            const modPromises = item.sockets.map(async (socket) => {
                if (socket.plugHash) {
                    try {
                        const plugItem = await fetchItemDefinition(socket.plugHash);
                        if (plugItem.itemTypeDisplayName?.toLowerCase().includes('mod')) {
                            return `<div class="mod"><img src="https://www.bungie.net${plugItem.displayProperties.icon}" alt="${plugItem.displayProperties.name}" title="${plugItem.displayProperties.description}"><p>${plugItem.displayProperties.name}</p></div>`;
                        }
                    } catch (err) {
                        return '';
                    }
                }
                return '';
            });
            modsHtml += (await Promise.all(modPromises)).join('');
        }
        modsHtml += '</div>';
        return modsHtml;
    }

    async function getWeaponPerks(item) {
        let perksHtml = '<div class="item-perks">';
        if (item.sockets) {
            const perkPromises = item.sockets.map(async (socket) => {
                if (socket.plugHash) {
                    try {
                        const plugItem = await fetchItemDefinition(socket.plugHash);
                        if (plugItem.itemTypeDisplayName === 'Trait' || plugItem.itemTypeDisplayName === 'Enhanced Trait') {
                            perksHtml += `<div class="perk"><img src="https://www.bungie.net${plugItem.displayProperties.icon}" alt="${plugItem.displayProperties.name}" title="${plugItem.displayProperties.description}"><p>${plugItem.displayProperties.name}</p></div>`;
                        }
                    } catch (err) {
                        // Ignore errors
                    }
                }
            });
            await Promise.all(perkPromises);
        }
        perksHtml += '</div>';
        return perksHtml;
    }

    async function renderEquipment(profileResponse, characterId, characterCard) {
        const equipment = profileResponse.characterEquipment.data[characterId].items;
        const itemComponents = profileResponse.itemComponents;
        if (profileResponse.characterSockets) {
            console.log("Character Sockets: ", profileResponse.characterSockets);
        }
        const equipmentContainer = document.createElement('div');
        equipmentContainer.className = 'equipment-display';
        equipmentContainer.innerHTML = '<h3>Loading equipment...</h3>';
        characterCard.appendChild(equipmentContainer);

        const itemPromises = equipment.map(item => fetchItemDefinition(item.itemHash));
        const items = await Promise.all(itemPromises);

        const weapons = { kinetic: null, energy: null, power: null };
        const armor = { helmet: null, gauntlets: null, chest: null, legs: null, classItem: null };

        items.forEach((item, index) => {
            if (item) {
                const bucketHash = item.inventory.bucketTypeHash;
                for (const slot in slotHashes) {
                    if (slotHashes[slot] === bucketHash) {
                        const itemInstanceId = equipment[index].itemInstanceId;
                        if (itemInstanceId) {
                            const itemWithPerks = {
                                ...item,
                                itemInstanceId: itemInstanceId,
                                sockets: itemComponents.sockets?.data[itemInstanceId]?.sockets,
                                perks: itemComponents.perks?.data[itemInstanceId]?.perks
                            };
                            if (['kinetic', 'energy', 'power'].includes(slot)) {
                                weapons[slot] = itemWithPerks;
                            } else {
                                armor[slot] = itemWithPerks;
                            }
                        } else {
                            if (['kinetic', 'energy', 'power'].includes(slot)) {
                                weapons[slot] = item;
                            } else {
                                armor[slot] = item;
                            }
                        }
                    }
                }
            }
        });

        let html = '<div class="equipment-grid">';
        html += '<div><h3>Weapons</h3>';
        for (const slot of ['kinetic', 'energy', 'power']) {
            const item = weapons[slot];
            if (item) {
                html += `<div class="equipment-item"><img src="https://www.bungie.net${item.displayProperties.icon}" alt="${item.displayProperties.name}"><p class="item-name">${item.displayProperties.name}</p>${await getWeaponPerks(item)}</div>`;
            }
        }
        html += '</div>';

        html += '<div><h3>Armor</h3>';
        for (const slot of ['helmet', 'gauntlets', 'chest', 'legs', 'classItem']) {
            const item = armor[slot];
            if (item) {
                html += `<div class="equipment-item"><img src="https://www.bungie.net${item.displayProperties.icon}" alt="${item.displayProperties.name}"><p class="item-name">${item.displayProperties.name}</p>${await getArmorMods(item)}</div>`;
            }
        }
        html += '</div></div>';
        equipmentContainer.innerHTML = html;
    }

    function renderCharacters(profileResponse, container) {
        const characters = profileResponse.characters.data;
        const characterEquipment = profileResponse.characterEquipment.data;

        if (!characters) {
            container.innerHTML = '<p>Could not load character data.</p>';
            return;
        }
        
        container.innerHTML = ''; // Clear previous content

        // Find the most recently played character
        let mostRecentCharacterId = null;
        let mostRecentDate = new Date(0);

        for (const characterId in characters) {
            const character = characters[characterId];
            const lastPlayed = new Date(character.dateLastPlayed);
            if (lastPlayed > mostRecentDate) {
                mostRecentDate = lastPlayed;
                mostRecentCharacterId = characterId;
            }
        }

        if (mostRecentCharacterId) {
            const character = characters[mostRecentCharacterId];
            const emblemPath = `https://www.bungie.net${character.emblemBackgroundPath}`;
            const className = classMap[character.classType] || 'Unknown Class';
            const raceName = raceMap[character.raceType] || 'Unknown Race';
            const genderName = genderMap[character.genderType] || 'Unknown Gender';

            const card = document.createElement('div');
            card.className = 'character-card';
            card.dataset.characterId = mostRecentCharacterId;
            card.innerHTML = `
                <div class="character-emblem" style="background-image: url('${emblemPath}')"></div>
                <div class="character-details">
                    <div>
                        <h2>${className}</h2>
                        <p class="character-class">${raceName} | ${genderName}</p>
                    </div>
                    <div class="character-power">${character.light}</div>
                </div>
            `;
            container.appendChild(card);
            renderEquipment(profileResponse, mostRecentCharacterId, card);
        } else {
            container.innerHTML = '<p>No character data found.</p>';
        }
    }

    async function fetchPlayerProfile(membershipType, membershipId, isRefresh = false) {
        if (!isRefresh) {
            resultsContainer.innerHTML = '<p>Fetching profile...</p>';
        }
        try {
            const profileUrl = `https://www.bungie.net/Platform/Destiny2/${membershipType}/Profile/${membershipId}/?components=200,205,300,302,304,305`;
            const profileResponse = await fetch(`/api/proxy?url=${encodeURIComponent(profileUrl)}`);

            if (!profileResponse.ok) {
                throw new Error(`Bungie API request for profile failed with status ${profileResponse.status}`);
            }

            const profileData = await profileResponse.json();
            if (profileData.ErrorCode !== 1) {
                throw new Error(`Bungie API Error for Profile: ${profileData.Message}`);
            }

            renderCharacters(profileData.Response, resultsContainer);

            // Store current player for refresh
            currentMembershipType = membershipType;
            currentMembershipId = membershipId;

        } catch (error) {
            console.error('Error fetching player profile:', error);
            resultsContainer.innerHTML = `<p>Could not fetch player profile. Error: ${error.message}</p>`;
            clearInterval(refreshInterval); // Stop refreshing on error
        }
    }

    searchButton.addEventListener('click', async () => {
        const searchTerm = searchInput.value.trim();
        if (!searchTerm) {
            resultsContainer.innerHTML = '<p>Please enter a Bungie Name to search.</p>';
            return;
        }

        // Clear previous refresh interval
        if (refreshInterval) {
            clearInterval(refreshInterval);
        }

        const parts = searchTerm.split('#');
        if (parts.length !== 2) {
            resultsContainer.innerHTML = '<p>Invalid Bungie Name format. Please use name#1234.</p>';
            return;
        }

        const displayName = parts[0];
        const displayNameCode = parts[1];

        resultsContainer.innerHTML = '<p>Searching...</p>';

        try {
            const searchUrl = `https://www.bungie.net/Platform/Destiny2/SearchDestinyPlayerByBungieName/-1/`;
            const response = await fetch(`/api/proxy`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    url: searchUrl,
                    method: 'POST',
                    body: {
                        displayName: displayName,
                        displayNameCode: displayNameCode
                    }
                })
            });

            if (!response.ok) {
                throw new Error(`Bungie API request failed with status ${response.status}`);
            }

            const data = await response.json();
            if (data.ErrorCode !== 1) {
                throw new Error(`Bungie API Error: ${data.Message}`);
            }

            if (data.Response.length === 0) {
                resultsContainer.innerHTML = '<p>No player found with that Bungie Name.</p>';
                return;
            }

            const player = data.Response[0];
            await fetchPlayerProfile(player.membershipType, player.membershipId);

            // Set up the refresh interval
            refreshInterval = setInterval(() => {
                fetchPlayerProfile(currentMembershipType, currentMembershipId, true);
            }, 180000); // 3 minutes

        } catch (error) {
            console.error('Error searching for player:', error);
            resultsContainer.innerHTML = `<p>Could not search for player. Error: ${error.message}</p>`;
        }
    });
});
