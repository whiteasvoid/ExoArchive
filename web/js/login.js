document.addEventListener('DOMContentLoaded', async () => {
    const authStatusDiv = document.getElementById('auth-status');

    try {
        const response = await fetch('/api/user');
        const data = await response.json();

        if (data.authenticated) {
            // If the user is already authenticated, redirect to the profile page.
            window.location.href = '/profile';
        } else {
            // Otherwise, set up the authentication button.
            authStatusDiv.innerHTML = `
                <p>Connect your Bungie.net account to access your personal Destiny 2 information.</p>
                <button id="auth-button">Authenticate with Bungie.net</button>
            `;
            document.getElementById('auth-button').addEventListener('click', authenticate);
        }
    } catch (error) {
        console.error('Error checking authentication status:', error);
        authStatusDiv.innerHTML = '<p>Could not check authentication status. Please try again later.</p>';
    }
});

async function authenticate() {
    try {
        const response = await fetch('/api/oauth-client-id');
        if (!response.ok) {
            throw new Error('Could not retrieve client ID from server.');
        }
        const { clientId } = await response.json();

        if (!clientId || clientId === 'your_client_id_here') {
            alert('The Bungie.net Client ID is not configured on the server. Please ask the site administrator to configure it.');
            return;
        }

        const authUrl = `https://www.bungie.net/en/OAuth/Authorize?client_id=${clientId}&response_type=code`;
        window.location.href = authUrl;
    } catch (error) {
        console.error('Authentication error:', error);
        alert('An error occurred during authentication. Please try again later.');
    }
}
