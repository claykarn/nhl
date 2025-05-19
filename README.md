# NHL YouTube Data

This project collects and analyzes YouTube video data from official NHL team channels using the YouTube Data API v3.

## What's Included

- **`nhldata.csv`** — A dataset of 183 videos published between **May 5 and May 12, 2025**, across 8 NHL playoff teams.
  - Each row represents one video, with columns for:
    - `team`
    - `title`
    - `published` timestamp
    - `views`, `likes`, `comments`
    - `duration_minutes`
    - `subscriber count` at time of scraping

- **`ytdata.py`** — A Python script that queries the YouTube Data API and outputs a structured CSV.

- **`.env.example`** — A template for setting up your API key securely.

## Scraper Setup & Customization

To setup the scraper:
1. Copy `.env.example` → `.env`
2. Add your YouTube API key:
  YT_API_KEY= 'your_actual_key_here'

To scrape data for other YouTube channels or date ranges:

1. Download `ytdata.py`
2. Replace the team names and YouTube **channel handles or IDs** in the `teams` dictionary inside `ytdata.py`
3. Adjust the `START_DATE` and `END_DATE` values to define your desired time range. Optionally, change the csv file name output at the bottom.
4. Run the script to generate a new CSV

> Note: You’ll need your own YouTube Data API key, saved in a local `.env` file.

