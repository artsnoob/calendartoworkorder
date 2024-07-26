import base64
import requests
import csv
import os
import json
from datetime import datetime, timedelta

# OpenAI API Key
api_key = "xx"

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def get_meetings_from_image(image_path):
    base64_image = encode_image(image_path)
   
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
   
    payload = {
        "model": "gpt-4o",
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Please list all the meetings in this calendar screenshot. For each meeting, provide the date, exact start time, exact end time, and title in the format: 'YYYY-MM-DD, HH:MM - HH:MM, Title'"
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    }
                ]
            }
        ],
        "max_tokens": 3000
    }
   
    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
    return response.json()['choices'][0]['message']['content']

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
    return round(duration.total_seconds() / 3600, 2)  # Convert to hours and round to 2 decimal places

def format_meetings(meetings):
    formatted_meetings = []
    for meeting in meetings.split('\n'):
        parts = meeting.split(', ')
        if len(parts) >= 3:
            date = parts[0]
            time = parts[1]
            title = ', '.join(parts[2:])
            formatted_meetings.append(f"{date}: {time} - {title}")
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
        "max_tokens": 3000
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
        
        # Extract the JSON part from the content
        json_start = content.find('[')
        json_end = content.rfind(']') + 1
        if json_start != -1 and json_end != -1:
            json_content = content[json_start:json_end]
            
            # Handle potential incomplete JSON
            if not json_content.endswith(']'):
                json_content = json_content.rsplit('},', 1)[0] + '}]'
            
            # Parse the JSON content
            matched_data = json.loads(json_content)
            
            # Calculate meeting duration for all entries, including those with null workorder values
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
    except requests.exceptions.RequestException as e:
        print(f"Error making request to OpenAI API: {str(e)}")
    except KeyError as e:
        print(f"Error accessing API response: {str(e)}")
        print("Full response received:")
        print(json.dumps(response_json, indent=2))
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON from API response: {str(e)}")
        print("Content causing the error:")
        print(content)
    except Exception as e:
        print(f"Unexpected error processing API response: {str(e)}")
        print(f"Error details: {str(e)}")
    
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
    # Get screenshot from user
    screenshot_path = input("Please provide the path to your calendar screenshot: ")
   
    # Ensure the screenshot file exists
    if not os.path.exists(screenshot_path):
        print("Error: The specified screenshot file does not exist.")
        return

    # Get meetings from the image
    print("Analyzing the calendar screenshot...")
    meetings = get_meetings_from_image(screenshot_path)
    print("Meetings extracted successfully.")
    print("Extracted meetings:")
    print(meetings)
   
    # Format meetings
    formatted_meetings = format_meetings(meetings)
   
    # Parse workorders
    print("\nParsing work orders...")
    workorders = parse_workorders('workorder.csv')
    print("Work orders parsed successfully.")
    print("Parsed work orders:")
    print(workorders)
   
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

if __name__ == "__main__":
    main()
