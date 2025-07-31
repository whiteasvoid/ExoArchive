/**
 * @file Manages all interactions with the Bungie.net API.
 * This module centralizes API requests and handles the API key.
 */

// A private variable to store the API key. It's not truly private but acts as a module-level variable.
let _apiKey = null;

/**
 * Fetches the application configuration from our local server, which includes the Bungie API key.
 * This must be called before any other function in this module.
 * @returns {Promise<void>} A promise that resolves when the key is fetched and set.
 */
async function fetchAndSetApiKey() {
    // If the key is already fetched, no need to do it again.
    if (_apiKey) return;

    try {
        const response = await fetch('/api/config');
        if (!response.ok) {
            throw new Error(`Failed to fetch server configuration: ${response.statusText}`);
        }
        const config = await response.json();
        if (!config.apiKey) {
            throw new Error('API key not found in server configuration.');
        }
        _apiKey = config.apiKey;
    } catch (error) {
        console.error('Error fetching API key:', error);
        // Display a user-friendly error message on the page, as this is a critical failure.
        document.body.innerHTML = `
            <div style="padding: 20px; text-align: center;">
                <h1>Configuration Error</h1>
                <p>Could not load application configuration. Please ensure the server is running correctly and that you have a valid .env file.</p>
                <p>See the README.md for setup instructions.</p>
            </div>
        `;
        // Stop further execution by re-throwing the error.
        throw error;
    }
}

/**
 * A generic function to fetch data from a given URL, automatically including the API key.
 * It ensures the API key is available before making the request.
 * @param {string} url - The URL to fetch data from.
 * @returns {Promise<any>} The JSON response from the API.
 */
async function fetchData(url) {
    // The API key is now handled by the server-side proxy.
    // We just need to ensure the config is loaded to confirm server health.
    if (!_apiKey) {
        await fetchAndSetApiKey();
    }

    // Construct the proxy URL, ensuring the original URL is properly encoded.
    const proxyUrl = `/api/proxy?url=${encodeURIComponent(url)}`;

    const response = await fetch(proxyUrl);
    if (!response.ok) {
        // Try to parse the error message from the proxy.
        let errorData;
        try {
            errorData = await response.json();
        } catch (e) {
            // If the response is not JSON, use the status text.
            errorData = { error: response.statusText };
        }
        throw new Error(`API request via proxy failed: ${errorData.error || 'Unknown error'} for URL: ${url}`);
    }
    return response.json();
}

/**
 * Fetches the Destiny 2 manifest from the Bungie API.
 * The manifest contains the latest URLs for all other definition files.
 * @returns {Promise<any>} The manifest data (specifically the `Response` property).
 */
export async function getManifest() {
    const manifestUrl = 'https://www.bungie.net/Platform/Destiny2/Manifest/';
    const data = await fetchData(manifestUrl);
    return data.Response;
}

/**
 * Fetches a definition file (e.g., for items, stats) from the Bungie API.
 * @param {string} definitionUrl - The relative URL for the definition file, obtained from the manifest.
 * @returns {Promise<any>} The requested definition data.
 */
export async function getDefinitions(definitionUrl) {
    return fetchData(`https://www.bungie.net${definitionUrl}`);
}

/**
 * Fetches the full definition for a single inventory item by its hash.
 * @param {string} itemHash - The unique hash of the item to fetch.
 * @returns {Promise<any>} The item definition data.
 */
export async function getInventoryItemDefinition(itemHash) {
    const url = `https://www.bungie.net/Platform/Destiny2/Manifest/DestinyInventoryItemDefinition/${itemHash}/`;
    const data = await fetchData(url);
    return data.Response;
}

/**
 * Fetches the full definition for a single stat by its hash.
 * @param {string} statHash - The unique hash of the stat to fetch.
 * @returns {Promise<any>} The stat definition data.
 */
export async function getStatDefinition(statHash) {
    const url = `https://www.bungie.net/Platform/Destiny2/Manifest/DestinyStatDefinition/${statHash}/`;
    const data = await fetchData(url);
    return data.Response;
}

/**
 * Fetches the full definition for a single collectible by its hash.
 * @param {string} collectibleHash - The unique hash of the collectible to fetch.
 * @returns {Promise<any>} The collectible definition data.
 */
export async function getCollectibleDefinition(collectibleHash) {
    const url = `https://www.bungie.net/Platform/Destiny2/Manifest/DestinyCollectibleDefinition/${collectibleHash}/`;
    const data = await fetchData(url);
    return data.Response;
}

/**
 * Fetches the full definition for a plug set by its hash.
 * A plug set is a collection of perks that can be socketed into a weapon.
 * @param {string} plugSetHash - The unique hash of the plug set to fetch.
 * @returns {Promise<any>} The plug set definition data.
 */
export async function getPlugSetDefinition(plugSetHash) {
    const url = `https://www.bungie.net/Platform/Destiny2/Manifest/DestinyPlugSetDefinition/${plugSetHash}/`;
    const data = await fetchData(url);
    return data.Response;
}

/**
 * Fetches the full definition for a damage type by its hash.
 * @param {string} damageTypeHash - The unique hash of the damage type to fetch.
 * @returns {Promise<any>} The damage type definition data.
 */
export async function getDamageTypeDefinition(damageTypeHash) {
    const url = `https://www.bungie.net/Platform/Destiny2/Manifest/DestinyDamageTypeDefinition/${damageTypeHash}/`;
    const data = await fetchData(url);
    return data.Response;
}
