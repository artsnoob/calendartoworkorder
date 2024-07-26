# Meeting-Workorder Matcher

This Python script automates the process of matching calendar meetings with work orders. It uses OpenAI's GPT-4 model to extract meeting information from calendar screenshots and match them with relevant work orders.

calendartowo.py: Uses GPT API to scan a screenshot of a calendar to OCR the meeting names.
OWAtoWO.py: Scrapes the calendar events straight from OWA. Much more precise, and skips the first API step.

## Features

- Extract meeting information from calendar screenshots using OpenAI's GPT-4 vision model
- Parse work orders from a CSV file
- Match meetings with relevant work orders using GPT-4
- Calculate meeting durations
- Export matched data to a CSV file

## Prerequisites

- Python 3.6+
- OpenAI API key

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/meeting-workorder-matcher.git
   cd meeting-workorder-matcher
   ```

2. Install required dependencies:
   ```
   pip install requests
   ```

3. Set up your OpenAI API key:
   - Open the script and replace `"xx"` with your actual OpenAI API key.

## Usage

1. Prepare your input files:
   - Save your calendar screenshot as an image file (e.g., JPEG, PNG)
   - Ensure your work orders are in a CSV file named `workorder.csv` in the same directory as the script

2. Run the script:
   ```
   python meeting_workorder_matcher.py
   ```

3. When prompted, enter the path to your calendar screenshot.

4. The script will process the data and display the matched meetings and work orders in the console.

5. The results will be exported to a CSV file named `meetingorder.csv` in the same directory.

## Output

The script generates two types of output:

1. Console output: Displays the extracted meetings, parsed work orders, and matched data.
2. CSV file (`meetingorder.csv`): Contains the matched meetings, work orders, and meeting durations.

## Limitations

- The accuracy of meeting extraction depends on the quality and clarity of the calendar screenshot.
- The matching process relies on the GPT-4 model's understanding of the context and may not always provide perfect matches.

## Contributing

Contributions, issues, and feature requests are welcome. Feel free to check [issues page](https://github.com/yourusername/meeting-workorder-matcher/issues) if you want to contribute.

## License

[MIT](https://choosealicense.com/licenses/mit/)
