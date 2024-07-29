# Calendar Scraping and Workorder Matching

This project combines calendar event scraping from Outlook Web App (OWA) with workorder matching functionality using OpenAI's GPT model. It automates the process of extracting calendar events, matching them with relevant workorders, and exporting the results.

## Versions

- CalendarToWO.py: Uses GPT API to scan a screenshot of a calendar to OCR the meeting names.
- OWAtoWO.py: Scrapes the calendar events straight from OWA. Much more precise, and skips the first API step.

## Features

- Scrapes calendar events from Outlook Web App using Selenium
- Matches calendar events with workorders using OpenAI's GPT model
- Exports matched data to a CSV file

## Prerequisites

Before you begin, ensure you have met the following requirements:

- Python 3.7 or higher
- Chrome browser installed
- An OpenAI API key

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/artsnoob/calendartoworkorder.git
   cd calendar-workorder-matching
   ```

2. Install the required Python packages:
   ```
   pip install selenium webdriver_manager requests
   ```

3. Create a `config.py` file in the project directory and add your OpenAI API key:
   ```python
   API_KEY = "your_openai_api_key_here"
   ```

## Usage

1. Ensure you have a `workorder.csv` file in the project directory containing your workorder data.

2. Run the script:
   ```
   python owatowo.py
   ```

3. The script will open a Chrome browser window and navigate to Outlook Web App.

4. Log in to your OWA account and navigate to the weekly calendar view.

5. Press Enter in the console to continue the script execution.

6. The script will scrape the calendar events, match them with workorders, and export the results to `meetingorder.csv`.

## Troubleshooting

If you encounter any issues:

1. Check the console output for error messages.
2. Ensure your OpenAI API key is correct and has sufficient credits.
3. Verify that your `workorder.csv` file is properly formatted and in the correct location.
4. If you're having issues with Selenium, try updating to the latest version of ChromeDriver.
