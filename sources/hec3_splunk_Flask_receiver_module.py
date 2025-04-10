#Module: splunk_hec_Flask_receiver.py
#Description: This script sets up a Flask web server https://flask.palletsprojects.com/en/stable/ that listens for incoming HTTP POST requests
#             containing event data and forwards it to a Splunk HTTP Event Collector (HEC) endpoint.    
#curl -X POST http://localhost:8080/receive_event \
#-H "Content-Type: application/json" \
#-d '{"timestamp": "2025-04-08T12:00:00", "hostname": "test-host", "message": "This is a test event from Flask server"}'
#
#curl -X POST http://localhost:8088 -d 'This is a *** RAW ** test message' -H "Content-Type: text/plain"



from flask import Flask, request, jsonify
import json
from colorama import Back, Style, init, Fore
init(autoreset=True)  # Automatically reset color after each print

#------------------  Importing my modules & Local configs -------------------
from utils.misc_utils_module import is_json
from utils.queues_module import send_to_que
from colorama import Fore, Back, Style, init
#------------------  Importing my modules & Local configs -------------------



# Create Flask app
app = Flask(__name__)
#app.run(host='0.0.0.0', port=8080, debug=True)

# Splunk HEC endpoint setup
splunk_url = 'https://<splunk-server>:8088'  # Replace with your Splunk HEC endpoint
splunk_token = 'Splunk <your-token>'  # Replace with your HEC token

# Headers to authenticate with Splunk
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

    response = request.post(f'{splunk_url}/services/collector', headers=headers, data=json.dumps(payload))

    if response.status_code == 200:
        print(f"Event successfully sent to Splunk: {event_data}")
    else:
        print(f"Failed to send event to Splunk. Status code: {response.status_code}, Response: {response.text}")
#--------------------------------------------------------------
#--------------------------------------------------------------
def send_event_to_que(event_data):
    """
    Send event data to Splunk HEC
    """
    payload = {
        "event": event_data,
        "sourcetype": "_json",  # You can change this to the appropriate sourcetype
        "index": "main"  # Optional, change to your desired index
    }

    #response = request.post(f'{splunk_url}/services/collector', headers=headers, data=json.dumps(payload))

#--------------------------------------------------------------
#@app.route('/')
#def index():
#    return 'Index Page'
#
#@app.route('/hello')
#def hello():
    return 'Hello, World'
#--------------------------------------------------------------
# Endpoint to receive events from Splunk HEC
@app.route('/receive_event', methods=['POST'])
def receive_event():
    #print(f"{Fore.YELLOW+Style.BRIGHT}--------------------------------{Style.RESET_ALL}"); exit(0)
    """
    Endpoint to receive events from Splunk HEC
    """
    #sent_to_que(event_data)  # Send raw data to the queue
    try:
        event_data = request.get_json()  # Get JSON payload from the incoming request
        str_event_data = str(event_data)
        print(f"{Back.GREEN}Received event data: [{str_event_data}]")
        if is_json (str_event_data):
            # Process JSON data as needed
            print(f"{Fore.LIGHTWHITE_EX}1)Received JSON event data: {str_event_data}") 
            sent_to_que(event_data)  # Send raw data to the queue
        else:
             # Process raw data as needed
            print(f"{Fore.LIGHTMAGENTA_EX}2)Received raw event data: {event_data}")
            #event_data = request.data.decode('utf-8')  # Fallback to raw data if JSON parsing fails
            sent_to_que(event_data)  # Send raw data to the queue
  
        if not event_data:
            return jsonify({"error": "No event data found"}), 400

        # Send the event data to Splunk HEC
        #send_event_to_splunk(event_data)

        return jsonify({"status": "Event received and sent to Splunk successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
#--------------------------------------------------------------
##============================================================
#if __name__ == "__main__":
#    # Run the Flask app
#    
#============================================================
def start_hec3_server():
    
    app.run(host='0.0.0.0', port=8080, debug=True)