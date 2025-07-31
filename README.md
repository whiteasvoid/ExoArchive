# Destiny 2 Item Explorer

This is a simple web application to browse and explore items from the Destiny 2 game, using the Bungie.net API.

## Features

-   Browse a grid of Destiny 2 items.
-   Search for items by name or hash.
-   Filter items by ammo type, damage type, and weapon type.
-   View detailed item information, including stats and perks.
-   Responsive design for desktop and mobile.

## Project Structure

-   `server.py`: A simple Python HTTP server to serve the static frontend and provide the API key.
-   `web/`: Contains all the frontend files.
    -   `index.html`: The main item browsing page.
    -   `stats.html`: The page for viewing detailed item stats.
    -   `css/`: Stylesheets.
    -   `js/`: JavaScript files.
    -   `images/`: SVG icons for ammo types.

## Setup and Running

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd <repository-directory>
    ```

2.  **Set up the environment:**
    -   Install Python 3 if you don't have it.
    -   Create a virtual environment (recommended):
        ```bash
        python -m venv venv
        source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
        ```
    -   Install the required Python packages:
        ```bash
        pip install -r requirements.txt
        ```

3.  **Configure the API Key:**
    -   You will need a Bungie.net API key. You can get one by creating an application on the [Bungie.net Developer Portal](https://www.bungie.net/en/Application).
    -   Create a file named `.env` in the root of the project directory.
    -   Add your API key to the `.env` file, following the format in `.env.example`:
        ```
        BUNGIE_API_KEY=your_api_key_here
        ```

4.  **Run the server:**
    ```bash
    python server.py
    ```

5.  **View the application:**
    -   Open your web browser and go to `http://localhost:8000`.
