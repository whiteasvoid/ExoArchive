let characterEquipmentData = null;
let primaryMembership = null;

async function pollForEquipmentChanges() {
    if (!primaryMembership) return;

    const { membershipType, membershipId } = primaryMembership;
    const profileUrl = `https://www.bungie.net/Platform/Destiny2/${membershipType}/Profile/${membershipId}/?components=200,205`;
    const profileResponse = await fetch(`/api/proxy?url=${encodeURIComponent(profileUrl)}`);

    if (!profileResponse.ok) {
        console.error(`Bungie API request for profile failed with status ${profileResponse.status}`);
        return;
    }

    const profileData = await profileResponse.json();
    if (profileData.ErrorCode !== 1) {
        console.error(`Bungie API Error for Profile: ${profileData.Message}`);
        return;
    }

    const newEquipmentData = profileData.Response.characterEquipment.data;

    for (const characterId in newEquipmentData) {
        const oldItems = characterEquipmentData[characterId].items.map(item => item.itemInstanceId).sort();
        const newItems = newEquipmentData[characterId].items.map(item => item.itemInstanceId).sort();

        if (JSON.stringify(oldItems) !== JSON.stringify(newItems)) {
            console.log(`Equipment changed for character ${characterId}`);
            handleEquipmentChange(characterId, newEquipmentData[characterId].items);
        }
    }

    characterEquipmentData = newEquipmentData;
}

function handleEquipmentChange(characterId, newEquipment) {
    const characterCard = document.querySelector(`.character-card[data-character-id='${characterId}']`);
    if (characterCard) {
        const equipmentDisplay = characterCard.querySelector('.equipment-display');
        if (equipmentDisplay) {
            renderEquipment(newEquipment, characterCard, true);
        }
    }
}

document.addEventListener('DOMContentLoaded', async () => {
    const profileInfoDiv = document.getElementById('profile-info');
    const charactersContainer = document.getElementById('characters-container');

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

    // Function to render character cards
    function renderCharacters(profileResponse) {
        const characters = profileResponse.characters.data;
        characterEquipmentData = profileResponse.characterEquipment.data;
        const characterEquipment = characterEquipmentData;

        if (!characters) {
            charactersContainer.innerHTML = '<p>Could not load character data.</p>';
            return;
        }
        
        charactersContainer.innerHTML = ''; // Clear previous content

        for (const characterId in characters) {
            const character = characters[characterId];
            const emblemPath = `https://www.bungie.net${character.emblemBackgroundPath}`;
            const className = classMap[character.classType] || 'Unknown Class';
            const raceName = raceMap[character.raceType] || 'Unknown Race';
            const genderName = genderMap[character.genderType] || 'Unknown Gender';

            const card = document.createElement('div');
            card.className = 'character-card';
            card.dataset.characterId = characterId;
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
            charactersContainer.appendChild(card);
        }

        const toggleEquipmentButton = document.getElementById('toggle-equipment-button');
        let allEquipmentVisible = false;

        toggleEquipmentButton.addEventListener('click', () => {
            allEquipmentVisible = !allEquipmentVisible;
            toggleEquipmentButton.textContent = allEquipmentVisible ? 'Hide All Equipment' : 'Show All Equipment';

            const characterCards = document.querySelectorAll('.character-card');
            characterCards.forEach(card => {
                const characterId = card.dataset.characterId;
                const equipment = characterEquipment[characterId].items;
                renderEquipment(equipment, card, allEquipmentVisible);
            });
        });
    }

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

    // Function to render equipment
    async function renderEquipment(equipment, characterCard, show) {
        const existingEquipment = characterCard.querySelector('.equipment-display');

        if (!show) {
            if (existingEquipment) {
                existingEquipment.remove();
            }
            return;
        }

        if (existingEquipment) {
            return; // Already visible
        }

        const equipmentContainer = document.createElement('div');
        equipmentContainer.className = 'equipment-display';
        equipmentContainer.innerHTML = '<h3>Loading equipment...</h3>';
        characterCard.appendChild(equipmentContainer);

        const itemPromises = equipment.map(item => fetchItemDefinition(item.itemHash));
        const items = await Promise.all(itemPromises);

        const weapons = {
            kinetic: null,
            energy: null,
            power: null,
        };
        const armor = {
            helmet: null,
            gauntlets: null,
            chest: null,
            legs: null,
            classItem: null,
        };

        items.forEach(item => {
            if (item) {
                const bucketHash = item.inventory.bucketTypeHash;
                switch (bucketHash) {
                    case slotHashes.kinetic:
                        weapons.kinetic = item;
                        break;
                    case slotHashes.energy:
                        weapons.energy = item;
                        break;
                    case slotHashes.power:
                        weapons.power = item;
                        break;
                    case slotHashes.helmet:
                        armor.helmet = item;
                        break;
                    case slotHashes.gauntlets:
                        armor.gauntlets = item;
                        break;
                    case slotHashes.chest:
                        armor.chest = item;
                        break;
                    case slotHashes.legs:
                        armor.legs = item;
                        break;
                    case slotHashes.classItem:
                        armor.classItem = item;
                        break;
                }
            }
        });

        let html = '<div class="equipment-grid">';
        
        // Render Weapons
        html += '<div>';
        html += '<h3>Weapons</h3>';
        ['kinetic', 'energy', 'power'].forEach(slot => {
            const item = weapons[slot];
            if (item) {
                html += `
                    <div class="equipment-item">
                        <img src="https://www.bungie.net${item.displayProperties.icon}" alt="${item.displayProperties.name}">
                        <p>${item.displayProperties.name}</p>
                    </div>
                `;
            }
        });
        html += '</div>';

        // Render Armor
        html += '<div>';
        html += '<h3>Armor</h3>';
        ['helmet', 'gauntlets', 'chest', 'legs', 'classItem'].forEach(slot => {
            const item = armor[slot];
            if (item) {
                html += `
                    <div class="equipment-item">
                        <img src="https://www.bungie.net${item.displayProperties.icon}" alt="${item.displayProperties.name}">
                        <p>${item.displayProperties.name}</p>
                    </div>
                `;
            }
        });
        html += '</div>';

        html += '</div>';

        equipmentContainer.innerHTML = html;
    }

    async function fetchProfile() {
        try {
            // Get user's memberships
            const membershipsResponse = await fetch('/api/proxy?url=https://www.bungie.net/platform/User/GetMembershipsForCurrentUser/');
            
            if (membershipsResponse.status === 401) {
                profileInfoDiv.innerHTML = '<p>You are not logged in. Please <a href="/login">log in</a> to view your profile.</p>';
                return;
            }
            if (!membershipsResponse.ok) {
                throw new Error(`Bungie API request failed with status ${membershipsResponse.status}`);
            }

            const membershipsData = await membershipsResponse.json();
            if (membershipsData.ErrorCode !== 1) {
                throw new Error(`Bungie API Error: ${membershipsData.Message}`);
            }

            const bungieNetUser = membershipsData.Response.bungieNetUser;
            profileInfoDiv.innerHTML = `
                <p><strong>Bungie.net Name:</strong> ${bungieNetUser.uniqueName}</p>
                <p><strong>Membership ID:</strong> ${bungieNetUser.membershipId}</p>
            `;

            const destinyMemberships = membershipsData.Response.destinyMemberships;
            if (!destinyMemberships || destinyMemberships.length === 0) {
                charactersContainer.innerHTML = '<p>No Destiny accounts found for this user.</p>';
                return;
            }

            // Get profile (character) data for the first
            primaryMembership = destinyMemberships[0];
            const { membershipType, membershipId } = primaryMembership;
            
            const profileUrl = `https://www.bungie.net/Platform/Destiny2/${membershipType}/Profile/${membershipId}/?components=200,205`;
            const profileResponse = await fetch(`/api/proxy?url=${encodeURIComponent(profileUrl)}`);

            if (!profileResponse.ok) {
                throw new Error(`Bungie API request for profile failed with status ${profileResponse.status}`);
            }

            const profileData = await profileResponse.json();
            if (profileData.ErrorCode !== 1) {
                throw new Error(`Bungie API Error for Profile: ${profileData.Message}`);
            }

            renderCharacters(profileData.Response);

        } catch (error) {
            console.error('Error fetching profile:', error);
            profileInfoDiv.innerHTML = `<p>Could not fetch your profile data. Error: ${error.message}</p>`;
            charactersContainer.innerHTML = '';
        }
    }

    fetchProfile();

    setInterval(pollForEquipmentChanges, 300000); // 5 minutes
});
