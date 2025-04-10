#Module: Splunk HEC WSGI Module
# This module implements a WSGI application to handle Splunk HTTP Event Collector (HEC) requests.
# It can process both JSON and raw text data sent to the server.
# It is designed to be run as a standalone WSGI server or integrated into a WSGI-compatible web server.
# This module is part of a larger system for receiving and processing log data.
# It is intended to be used in conjunction with other components, such as a logging framework or data processing pipeline.
# Json test:
#curl -X POST http://localhost:8080 -d '{"event": "sample_event", "host": "localhost"}' -H "Content-Type: application/json"
#Raw text test: 
#curl -X POST http://localhost:8088 -d 'This is a test message' -H "Content-Type: text/plain"
#
#This is a basic implementation of a WSGI application that can handle Splunk HEC events sent as either JSON or raw text. 
# For a production environment, you should consider using a more robust WSGI server such as gunicorn or uWSGI and add security 
# features like token validation.

#--------------------------------------------------------------

import json
from colorama import Fore, Back, Style, init
init(autoreset=True)  # Automatically reset color after each print

#------------------  Importing my modules & Local configs -------------------
from wsgiref.simple_server import make_server
from utils.misc_utils_module import C, setup_logging, signal_handler
from configs.globals_module import HEC_RECV_HOST, HEC_RECV_PORT, HEC_RECV_PATH, OSPS_DEFAULT_LOG_FILE
#------------------  Importing my modules & Local configs -------------------

logger = setup_logging(OSPS_DEFAULT_LOG_FILE)  # Set up logging configuration

#--------------------------------------------------------------
# WSGI application to handle Splunk HEC requests
def splunk_hec_app(environ, start_response):
    # Set default response status and headers
    status = '200 OK'
    headers = [('Content-type', 'application/json')]
    start_response(status, headers)

    # Check if the request path matches the HEC endpoint
    if environ.get('PATH_INFO') != HEC_RECV_PATH:
        # If not, return a 404 Not Found response
        status = '404 Not Found'
        start_response(status, headers)
        return [b'Not Found']
    
    # Check if the request method is POST
    if environ.get('REQUEST_METHOD') != 'POST':
        # If not, return a 405 Method Not Allowed response
        status = '405 Method Not Allowed'
        start_response(status, headers)
        return [b'Method Not Allowed']
    
    # Check for the presence of the Splunk HEC token in the request headers
    # In a real-world scenario, you would validate the token against your Splunk configuration
    # For this example, we will just check if it matches a hardcoded value
    token = environ.get('HTTP_X_SPLUNK_HEC_TOKEN')
    if token != "your_splunk_token":
        status = '403 Forbidden'
        response = {"status": "error", "message": "Forbidden"}
        return [json.dumps(response).encode('utf-8')]

    try:
        # Read the request body from the WSGI environment
        content_length = int(environ.get('CONTENT_LENGTH', 0))
        raw_data = environ['wsgi.input'].read(content_length) if content_length else b""   
        # Determine the content type and parse accordingly
        if environ.get('CONTENT_TYPE') == 'application/json':
            # Parse JSON if it's JSON data
            try:
                data = json.loads(raw_data)
                print("Received JSON:", data)
                # Process the JSON as needed
                response = {"status": "success", "message": "JSON data received"}
            except json.JSONDecodeError:
                response = {"status": "error", "message": "Invalid JSON format"}
        else:
            # Treat raw data as text
            raw_text = raw_data.decode('utf-8')
            print("Received Raw Text:", raw_text)
            # Process the raw text as needed
            response = {"status": "success", "message": "Raw text data received"}
    
        # Return the response as a JSON string
        return [json.dumps(response).encode('utf-8')]

    except Exception as e:
        # If there was an error, return an error message
        response = {"status": "error", "message": str(e)}
        return [json.dumps(response).encode('utf-8')]
#End of splunk_hec_app()    
#--------------------------------------------------------------
#==============================================================
# Create and run the WSGI server on port 
def start_hec2_server():
    # Define the server and the application
    httpd = make_server(HEC_RECV_HOST, HEC_RECV_PORT, splunk_hec_app)
    print(f"{Fore.BLUE}Splunk HEC (WSGI) server running on {HEC_RECV_HOST}:{HEC_RECV_PORT}")
    logger.info(f"Splunk HEC (WSGI) server running on {HEC_RECV_HOST}:{HEC_RECV_PORT}")
    httpd.serve_forever()   # 
#End of start_hec2_server()    
#==============================================================

#if __name__ == '__main__':
#    start_hec2_server()
