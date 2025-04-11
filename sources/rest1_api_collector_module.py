#Module: generic_rest_api_module.py
# # # # This module implements a generic REST API client that can fetch data from a specified API endpoint.
# # # # It is designed to be run as a standalone script or integrated into a larger system for receiving and processing data.
# # # # It is intended to be used in conjunction with other components, such as a logging framework or data processing pipeline.
# # # #--------------------------------------------------------------

from colorama import Fore, Back, Style, init
# Initialize colorama
init(autoreset=True)  # Automatically reset color after each print
import requests

#--------------------------------------------------------------
from configs.globals_module import GITHUB_ADVISORY_URL, GITHUB_TOKEN, CISA_KEV_URL

#--------------------------------------------------------------
def get_user_configuration():
    # Get API URL and authentication details from the user
    api_url = input("Enter the API URL (e.g., https://api.example.com/data): ")
    if not api_url:
        api_url = GITHUB_ADVISORY_URL
        #api_url = CISA_KEV_URL
        print(f"No API URL provided. Using default URL. [{api_url}]")

    api_key = input("Enter your API Key (if needed): ")
    if not api_key:
        api_key = GITHUB_TOKEN
        print(f"No API Key provided. Using default GitHub Advisory URL. [{api_key}]")

    auth_type = input("Enter authentication type (e.g., 'Bearer' or 'Basic'): ").lower()

    # Set the appropriate headers based on authentication type
    if auth_type == 'bearer':
        auth_token = api_key
        headers = {'Authorization': f'Bearer {auth_token}'}
    elif auth_type == 'basic':
        username = input("Enter your username: ")
        password = input("Enter your password: ")
        headers = None  # We'll use the auth tuple for Basic Auth
        auth = (username, password)
    else:
        print("Unsupported authentication type. Using no authentication.")
        headers = None
        auth = None

    return api_url, headers, auth
#--------------------------------------------------------------
#--------------------------------------------------------------
# Function to fetch data from the API with pagination
def fetch_data_from_api(api_url, headers, auth):
    page = 1
    all_data = []

    while True:
        params = {'page': page}
        print(f"Fetching data from page {page}...")
        # Send GET request with pagination and authentication if provided
        if auth:
            response = requests.get(api_url, params=params, auth=auth, headers=headers)
        else:
            response = requests.get(api_url, params=params, headers=headers)
            #response = requests.get(api_url)
            
        # Check if the response is successful
        if response.status_code == 200:
            data = response.json()
            # Check if the response is a dictionary
            if not isinstance(data, dict):
                print("Response is not a dictionary.")
                all_data = data
            else: #--------
                keys = data.keys()
                print(f"Respoinse is dictonary. Keys in the response:") # {keys}")
                # Dynamically find the key that contains the results
                results_key = None
                for key in data.keys():
                    if isinstance(data[key], list):  # Assumption: results will be a list
                        results_key = key
                        break # Exit the loop once we find the first list key

                if results_key:
                    all_data.extend(data[results_key])  # Use the dynamically found results key
                    # Check if there's a 'next' page
                    if 'next' in data and data['next']:
                        page += 1
                    else:
                        break
                else: # No results key found
                    print("No results key found in the response.")
                break
                #--------
       
        else: #response.status_code != 200
            print(f"Error fetching data: {response.status_code} - {response.text}")
            break  #We exit the loop on error

    return all_data
#--------------------------------------------------------------
#==============================================================
# Function to run the REST API collector
def run_rest1_api_collector(DEBUG_LEVEL=0):

    if DEBUG_LEVEL != 0:
        print(f"{Fore.YELLOW+Back.LIGHTRED_EX+Style.BRIGHT} **** LEVEL:{DEBUG_LEVEL} DEBUG MODE ENABLED **** {Fore.RESET}")
    api_url, headers, auth = get_user_configuration()

    print("Fetching data from the API...")
    data = fetch_data_from_api(api_url, headers, auth)

    # Optionally, save to file or process the data
    #print(data)
    print(f"Fetched {len(data)} items.")
#===============================================================

#if __name__ == "__main__":
    #start_rest_api_call()
