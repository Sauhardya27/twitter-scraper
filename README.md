# Twitter Scraper

A Python-based web application for scraping Twitter data. This application allows users to extract specific information from Twitter and view the data through a web interface.

## Features

- Scrapes tweets and related data using a custom script.
- Provides a user-friendly web interface built with Flask.
- Stores and retrieves scraped data in a database.
- JavaScript-based interactivity for dynamic user experience.

## Project Structure
```
twitter-scraper
├── app/
│    ├── scraper/
|    │    ├── __init__.py
|    │    └── twitter.py
│    ├── static/
|    │    └── js/
|    │      └── main.js
│    ├── templates/
|    │    └── index.html
│    ├── __init__.py
│    ├── config.py
│    ├── database.py
│    ├── routes.py
│    └── venv/
├── .env
├── app.py
└── requirements.txt
```

## Requirements

- Python 3.8 or higher
- Flask
- Other dependencies listed in `requirements.txt`

---

## Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/Sauhardya27/twitter-scraper.git
cd twitter-scrapper
```

### 2. Create and Activate a Virtual Environment

```bash
python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Set Up Environment Variables
Create a .env file in the root directory and add your environment variables:

```bash
TWITTER_USERNAME=twitter_username
TWITTER_PASSWORD=twitter_password
PROXYMESH_USERNAME=proxymesh_username
PROXYMESH_PASSWORD=proxymesh_password
MONGODB_URI=mongodb_uri
```

### 5. Run the Application

```bash
python app.py
```
