/**
 * @file Manages all interactions with the Bungie.net API.
 * It centralizes API requests and handles the API key.
 */

/**
 * Fetches data from a given URL using the server-side proxy.
 * @param {string} url The URL to fetch data from.
 * @returns {Promise<any>} The JSON response from the API.
 */
async function fetchData(url) {
    // Builds the proxy URL, making sure the original URL is properly encoded.
    const proxyUrl = `/api/proxy?url=${encodeURIComponent(url)}`;

    const response = await fetch(proxyUrl);
    if (!response.ok) {
        // Try to parse the error message.
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
 * @returns {Promise<any>} The manifest data (specifically the 'Response' property).
 */
export async function getManifest() {
    const manifestUrl = 'https://www.bungie.net/Platform/Destiny2/Manifest/';
    const data = await fetchData(manifestUrl);
    return data.Response;
}

/**
 * Fetches a definition file (ex., for items, stats) from the Bungie API.
 * @param {string} definitionUrl - The relative URL for the definition file, obtained from the manifest.
 * @returns {Promise<any>} The requested definition data.
 */
export async function getDefinitions(definitionUrl) {
    return fetchData(`https://www.bungie.net${definitionUrl}`);
}

/**
 * Fetches the definition for a single inventory item by its hash.
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
 * A plug set is the collection of perks that can be socketed into a weapon.
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
