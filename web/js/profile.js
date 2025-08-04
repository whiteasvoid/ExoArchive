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
    function renderCharacters(characters) {
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
            const primaryMembership = destinyMemberships[0];
            const { membershipType, membershipId } = primaryMembership;
            
            const profileUrl = `https://www.bungie.net/Platform/Destiny2/${membershipType}/Profile/${membershipId}/?components=200`;
            const profileResponse = await fetch(`/api/proxy?url=${encodeURIComponent(profileUrl)}`);

            if (!profileResponse.ok) {
                throw new Error(`Bungie API request for profile failed with status ${profileResponse.status}`);
            }

            const profileData = await profileResponse.json();
            if (profileData.ErrorCode !== 1) {
                throw new Error(`Bungie API Error for Profile: ${profileData.Message}`);
            }

            const characters = profileData.Response.characters.data;
            renderCharacters(characters);

        } catch (error) {
            console.error('Error fetching profile:', error);
            profileInfoDiv.innerHTML = `<p>Could not fetch your profile data. Error: ${error.message}</p>`;
            charactersContainer.innerHTML = '';
        }
    }

    fetchProfile();
});
