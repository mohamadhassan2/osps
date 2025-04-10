#Module: splunk_hec3_sender_module.py
# This module is designed to send events to Splunk using the HTTP Event Collector (HEC) API.
# It uses the requests library to send JSON payloads to the Splunk server.

import requests
import json

# Splunk HEC configuration
splunk_url = 'https://<splunk-server>:8088'  # Replace with your Splunk HEC endpoint
splunk_token = 'Splunk <your-token>'  # Replace with your HEC token

headers = {
    'Authorization': splunk_token,
    'Content-Type': 'application/json'
}
#--------------------------------------------------------------
def send_event_to_splunk(event_data):
    """
    Send event data to Splunk HEC
    """
    payload = {
        "event": event_data,
        "sourcetype": "_json",  # You can change this to the appropriate sourcetype
        "index": "main"  # Optional, change to your desired index
    }
    response = requests.post(f'{splunk_url}/services/collector', headers=headers, data=json.dumps(payload))
    if response.status_code == 200:
        print(f"Event successfully sent to Splunk: {event_data}")
    else:
        print(f"Failed to send event to Splunk. Status code: {response.status_code}, Response: {response.text}")

#=========================================================        
#if __name__ == "__main__":
#    # Example event data to send to Splunk
#    example_event = {
#        "timestamp": "2025-04-08T12:00:00",
#        "hostname": "test-host",
#        "message": "This is a test event from Python"
#    }
#    send_event_to_splunk(example_event)
#End of main()
#=========================================================