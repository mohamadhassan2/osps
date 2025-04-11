from flask import Flask, request, jsonify
import json

import requests
from colorama import Back, Style, init, Fore
init(autoreset=True)  # Automatically reset color after each print  
#------------------  Importing my modules & Local configs -------------------

#from configs.globals_module import OSPS_DEFAULT_LOG_FILE, HEC_RECV_HOST, HEC_RECV_PORT, HEC_RECV_PATH
# from utils.misc_utils_module import setup_logging, signal_handler

# Create Flask app
app = Flask(__name__)

# Splunk HEC endpoint setup
splunk_url = 'https://<splunk-server>:8088'  # Replace with your Splunk HEC endpoint
splunk_token = 'Splunk <your-token>'  # Replace with your HEC token

# Headers to authenticate with Splunk
headers = {
    'Authorization': splunk_token,
    'Content-Type': 'application/json'
}
#--------------------------------------------------------------------
def send_event_to_splunk(event_data):
    #Function to send event data to Splunk HEC
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
#--------------------------------------------------------------------

@app.route('/start_hec1_server', methods=['POST'])

#--------------------------------------------------------------------
def start_hec1_server(DEBUG_LEVEL=0):

    print(f"{Fore.GREEN}>>Starting Splunk HEC server..." )
    if DEBUG_LEVEL != 0:
        print(f"{Fore.YELLOW+Back.LIGHTRED_EX+Style.BRIGHT} **** LEVEL:{DEBUG_LEVEL} DEBUG MODE ENABLED **** {Fore.RESET}")
    


    #Function: Endpoint to receive events from Splunk HEC
    try:
        event_data = request.get_json()  # Get JSON payload from the incoming request
        if not event_data:
            return jsonify({"error": "No event data found"}), 400

        # Send the event data to Splunk HEC
        send_event_to_splunk(event_data)

        return jsonify({"status": "Event received and sent to Splunk successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
#--------------------------------------------------------------------    

#====================================================================
#if __name__ == "__main__":
#    # Run the Flask app
    app.run(host='0.0.0.0', port=8080, debug=True)
#====================================================================