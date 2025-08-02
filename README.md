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

3.  **Configure API Credentials:**
    -   You will need a Bungie.net API key. You can get one by creating an application on the [Bungie.net Developer Portal](https://www.bungie.net/en/Application).
    -   When creating your application, set the **"Redirect URL"** to `https://localhost:8000/callback`.
    -   Create a file named `.env` in the root of the project directory.
    -   Add your API key, OAuth Client ID, and OAuth Client Secret to the `.env` file, following the format in `.env.example`:
        ```
        BUNGIE_API_KEY=your_api_key_here
        BUNGIE_CLIENT_ID=your_client_id_here
        BUNGIE_CLIENT_SECRET=your_client_secret_here
        ```

4.  **Set up for Personal Details (OAuth):**
    -   The Bungie.net API sadly requires that the redirect URL for authentication be `https`. With this, you need to run the server with a self-signed SSL certificate for local development.
    -   Create a directory for the certificates:
        ```bash
        mkdir certs
        ```
    -   Generate the required `key.pem` and `cert.pem` files inside the just created directory:
        ```bash
        openssl req -new -x509 -keyout certs/key.pem -out certs/cert.pem -days 365 -nodes
        ```
    -   This command will ask for some information, but you can leave them blank.

5.  **Run the server:**
    ```bash
    python server.py
    ```
    -   If the certificate files are found, the server will run on `https://`. Otherwise, it will fall back to `http` which will make anything related to the Profile or Login not work.

6.  **View the application:**
    -   Open your web browser and go to `https://localhost:8000`.
    -   It will likely show a warning about the self-signed certificate being "not secure." This is supose to happen. You can proceed past this warning.