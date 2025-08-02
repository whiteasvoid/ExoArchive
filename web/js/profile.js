document.addEventListener('DOMContentLoaded', async () => {
    const profileInfoDiv = document.getElementById('profile-info');

    async function fetchProfile() {
        try {
            // This will use the updated proxy which sends the access token
            const response = await fetch('/api/proxy?url=https://www.bungie.net/platform/User/GetMembershipsForCurrentUser/');
            
            if (response.status === 401) {
                profileInfoDiv.innerHTML = '<p>You are not logged in. Please <a href="/login">log in</a> to view your profile.</p>';
                return;
            }

            if (!response.ok) {
                throw new Error(`Bungie API request failed with status ${response.status}`);
            }

            const data = await response.json();
            
            if (data.ErrorCode !== 1) {
                throw new Error(`Bungie API Error: ${data.Message}`);
            }

            const bungieNetUser = data.Response.bungieNetUser;
            profileInfoDiv.innerHTML = `
                <p><strong>Bungie.net Name:</strong> ${bungieNetUser.uniqueName}</p>
                <p><strong>Membership ID:</strong> ${bungieNetUser.membershipId}</p>
            `;

        } catch (error) {
            console.error('Error fetching profile:', error);
            profileInfoDiv.innerHTML = `<p>Could not fetch your profile data. Error: ${error.message}</p>`;
        }
    }

    fetchProfile();
});
