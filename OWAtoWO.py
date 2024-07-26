import base64
import requests
import csv
import os
import json
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
import time

# OpenAI API Key
api_key = "xx"

def setup_chrome_driver():
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--disable-notifications")
    
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=chrome_options)

def wait_for_user_signal():
    input("Please log in to OWA, navigate to the weekly calendar view, then press Enter to continue...")

def wait_for_calendar_to_load(driver, timeout=30):
    try:
        WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "[role='grid']"))
        )
        print("Calendar grid detected.")
    except TimeoutException:
        print("Timeout waiting for calendar grid to load.")

def interact_with_calendar(driver):
    try:
        calendar_body = driver.find_element(By.CSS_SELECTOR, "[role='grid']")
        driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", calendar_body)
        time.sleep(2)
        print("Scrolled calendar to load all events.")
    except Exception as e:
        print(f"Error interacting with calendar: {str(e)}")

def scrape_events(driver):
    events = []
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "[role='button'][aria-label]"))
        )
        
        event_elements = driver.find_elements(By.CSS_SELECTOR, "[role='button'][aria-label]")
        
        for event in event_elements:
            aria_label = event.get_attribute("aria-label")
            if aria_label:
                print(f"Found event with aria-label: {aria_label}")
                parts = aria_label.split(", ")
                if len(parts) >= 2:
                    events.append({
                        "title": parts[0],
                        "details": ", ".join(parts[1:])
                    })
        
        print(f"Found {len(events)} events.")
    except Exception as e:
        print(f"Error scraping events: {str(e)}")
    
    return events

def parse_workorders(file_path):
    workorders = []
    with open(file_path, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            workorders.append(row)
    return workorders

def calculate_meeting_duration(start_time, end_time):
    start = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
    end = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
    duration = end - start
    return round(duration.total_seconds() / 3600, 2)

def format_meetings(events):
    formatted_meetings = []
    for event in events:
        formatted_meetings.append(f"{event['details']}: {event['title']}")
    return '\n'.join(formatted_meetings)

def match_meetings_to_workorders(meetings, workorders):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
   
    payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {
                "role": "system",
                "content": "You are a helpful assistant that matches meetings with work orders. Please provide your response as a list of dictionaries, where each dictionary contains 'meeting', 'workorder', 'start_time', and 'end_time' keys. The 'meeting' value should be a string containing the date and title of the meeting. The 'start_time' and 'end_time' should be in ISO format (YYYY-MM-DDTHH:MM:SS)."
            },
            {
                "role": "user",
                "content": f"Given these meetings:\n{meetings}\n\nAnd these workorders:\n{workorders}\n\nPlease match each meeting with the most logical workorder. If there's no matching workorder, use null for the workorder value. Include the exact start and end times for each meeting in ISO format."
            }
        ],
        "max_tokens": 6000
    }
   
    try:
        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
        response.raise_for_status()
        response_json = response.json()
        
        print("Raw API response:")
        print(json.dumps(response_json, indent=2))
        
        content = response_json['choices'][0]['message']['content']
        print("Parsed content:")
        print(content)
        
        json_start = content.find('[')
        json_end = content.rfind(']') + 1
        if json_start != -1 and json_end != -1:
            json_content = content[json_start:json_end]
            
            if not json_content.endswith(']'):
                json_content = json_content.rsplit('},', 1)[0] + '}]'
            
            matched_data = json.loads(json_content)
            
            matched_data = [
                {**item, 'duration': calculate_meeting_duration(item['start_time'], item['end_time'])}
                for item in matched_data
            ]
            
            return matched_data
        else:
            print("Error: Could not find valid JSON in the API response.")
            print("Full content received:")
            print(content)
            return []
    except Exception as e:
        print(f"Error processing API response: {str(e)}")
    
    return []

def display_results(matched_data):
    if not matched_data:
        print("\nNo meetings found.")
        return
    
    print("\nMatched Meetings and Work Orders:")
    print("----------------------------------")
    for item in matched_data:
        print(f"Meeting: {item['meeting']}")
        print(f"Work Order: {item['workorder'] if item['workorder'] is not None else 'No matching work order'}")
        print(f"Duration: {item['duration']} hours")
        print("----------------------------------")

def export_to_csv(matched_data, output_file):
    with open(output_file, 'w', newline='') as csvfile:
        fieldnames = ['meeting', 'workorder', 'duration']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
       
        writer.writeheader()
        for item in matched_data:
            writer.writerow({
                'meeting': item['meeting'],
                'workorder': item['workorder'] if item['workorder'] is not None else '',
                'duration': item['duration']
            })

def main():
    driver = setup_chrome_driver()
    
    try:
        print("Opening OWA...")
        driver.get("https://outlook.office.com/calendar/")
        
        wait_for_user_signal()
        
        print("Starting to scrape calendar data for the current week...")
        wait_for_calendar_to_load(driver)
        
        interact_with_calendar(driver)
        
        calendar_events = scrape_events(driver)
        
        if not calendar_events:
            print("No events were found. Please check your calendar and ensure events are visible.")
            return

        print("\nCalendar Events for the current week:")
        for event in calendar_events:
            print(f"Title: {event['title']}")
            print(f"Details: {event['details']}")
            print("---")
        
        # Format meetings
        formatted_meetings = format_meetings(calendar_events)
        
        # Parse workorders
        print("\nParsing work orders...")
        workorders = parse_workorders('workorder.csv')
        print("Work orders parsed successfully.")
        
        # Match meetings to workorders
        print("\nMatching meetings to work orders...")
        matched_data = match_meetings_to_workorders(formatted_meetings, workorders)
        
        # Display results
        display_results(matched_data)

        # Export to CSV
        if matched_data:
            output_file = 'meetingorder.csv'
            export_to_csv(matched_data, output_file)
            print(f"\nProcess completed. Results exported to {output_file}")
        else:
            print("\nNo data to export. Please check the API response and ensure meetings and work orders are being correctly processed.")
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")
    finally:
        input("Press Enter to close the browser...")
        driver.quit()

if __name__ == "__main__":
    main()
