# Exo Archive

A simple web application to browse and explore items from the Destiny 2 using the Bungie.net API.

## About the Project

I am a programming university student, and this is my first attempt at learning how to work with APIs. Exo Archive has no specific objective other than serving as a learning experience. My goal is to experiment with the Bungie.net API, understand how to manage it into a web application, and explore its possibilities. I am hoping that through this process, Exo Archive may evolve into something useful for others, such as Destiny 2 players or other developers looking to learn about APIs.

## Features

- Browse a grid of Destiny 2 items.
- Search for items by name or hash.
- Filter items by ammo type, damage type, and weapon type.
- View detailed item information, including base stats and perks.

## Project Structure

- `server.py`: The Python HTTP server to serve as a static frontend and provide the API key.
- `web/`: Contains all the frontend files.
  - `index.html`: The main item browsing page.
  - `stats.html`: The page for viewing detailed item stats.
  - `css/`: Stylesheets.
  - `js/`: JavaScript files.
  - `images/`: SVG icons for ammo types (and others soon if needed).

## Setup and Running

1. **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd <repository-directory>

2.  **Set up the environment:**
    -   Install Python 3 if you don't have it.
    -   Install the required Python packages:
        ```bash
        pip install -r requirements.txt
        ```

3.  **Configure the API Key:**
    -   You will need a Bungie.net API key. You can get one by creating an application on the [Bungie.net Developer Portal](https://www.bungie.net/en/Application).
    -   Create a file named `.env` in the root of the project directory.
    -   Add your API key to the `.env` file, following the format in `.env.example` (do not use " or ' when pasting your api key):
        ```
        BUNGIE_API_KEY=your_api_key_here
        ```

4.  **Run the server:**
    ```bash
    python server.py
    ```

5.  **View the application:**
    -   Open your web browser and go to `http://localhost:8000`.