#Module to collect data from a REST API using HATEOAS principles
# This module allows users to navigate through a REST API using HATEOAS links.
# It is designed to be run as a standalone script or integrated into a larger system for receiving and processing data.
# It is intended to be used in conjunction with other components, such as a logging framework or data processing pipeline.
#HATEOAS (Hypermedia as the Engine of Application State) is a constraint of the REST application architecture that distinguishes it from most other network application architectures.
# It allows a client to interact with a network application entirely through hypermedia links provided dynamically by the server.
# HATEOAS enables clients to discover and navigate the API's capabilities without prior knowledge of its structure.
#
#HATEOAS (Hypermedia As The Engine of Application State) is a REST architectural style where the client interacts with the server entirely
#through hypermedia provided by the server. In a HATEOAS-compliant API, each response includes relevant links (usually under a _links key)
#that tell the client where to go next.




import requests
from colorama import Fore, Back, Style, init
# Initialize colorama
init(autoreset=True)  # Automatically reset color after each print
#-----------------------  Importing my modules & local configs -------------------
from configs.globals_module import GITHUB_ADVISORY_URL, GITHUB_TOKEN, CISA_KEV_URL
#------------------------  Importing my modules & local configs -------------------

#--------------------------------------------------------------
# This module implements a generic REST API client that can fetch data from a specified API endpoint.
def get_user_configuration():
    # Get API URL and authentication details from the user
    api_url = input("Enter the base API URL (e.g., https://api.example.com): ")
    api_key = input("Enter your API Key (if needed): ")
    auth_type = input("Enter authentication type (e.g., 'Bearer' or 'Basic'): ").lower()

    #--------
    if not api_url:
        #api_url = GITHUB_ADVISORY_URL
        api_url = CISA_KEV_URL
        print(f"No API URL provided. Using default URL. [{api_url}]")

    api_key = input("Enter your API Key (if needed): ")
    if not api_key:
        api_key = GITHUB_TOKEN
        print(f"No API Key provided. Using default GitHub Advisory URL. [{api_key}]")
    #--------

    # Set the appropriate headers based on authentication type
    if auth_type == 'bearer':
        auth_token = api_key
        headers = {'Authorization': f'Bearer {auth_token}'}
        auth = None
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
#End of get_user_configuration function()
#--------------------------------------------------------------

#---------------------------------------------------------------
# Function to make a HATEOAS request to the API
# This function performs a GET request to the API, either with authentication or not.
# It handles pagination and follows HATEOAS links to navigate through the API.
# It returns the JSON response from the API.
# If the request fails, it prints an error message and returns None.
def make_hateoas_request(api_url, headers, auth, endpoint=""):
    # Perform a GET request to the API, either with authentication or not
    url = f"{api_url}/{endpoint}" if endpoint else api_url
    print(f"Making request to: {url}")
    
    if auth:
        response = requests.get(url, headers=headers, auth=auth)
    else:
        response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching data: {response.status_code} - {response.text}")
        return None
#WEND of make_hateoas_request function()
#--------------------------------------------------------------
#--------------------------------------------------------------
# Function to navigate through the API using HATEOAS
# This function starts from the base API URL and follows the links provided in the response.
# It continues to fetch data until there are no more links to follow.
# It prints the data fetched from each endpoint and follows the 'next' link if available.
# It handles pagination by checking for the presence of '_links' in the response.
# It also checks if the response is a dictionary and handles it accordingly.
# It returns the data fetched from the API.
# The function is designed to be flexible and can be adapted for different APIs.
# It can be used to collect data from various REST APIs that follow HATEOAS principles.
# This function is the main entry point for navigating through the API.
# It uses the make_hateoas_request function to fetch data from the API.
# It handles the pagination and navigation through the API using HATEOAS links.
def navigate_hateoas(api_url, headers, auth):
    current_endpoint = ""
    while True:
        # Make a request to the current endpoint
        data = make_hateoas_request(api_url, headers, auth, current_endpoint)
        
        if not data:
            break

        # Process the data as needed (for example, print or store it)
        print(f"Data fetched from {current_endpoint}:")
        print(data)

        # Look for '_links' to find next steps
        if '_links' in data:
            links = data['_links']
            next_link = links.get('next', {}).get('href')
            
            if next_link:
                # If there's a 'next' link, use it for the next API call
                current_endpoint = next_link
                print(f"Following next link: {current_endpoint}")
            else:
                print("No more links to follow.")
                break
        else:
            print("No '_links' found in response. Stopping navigation.")
            break
#END of navigate_hateoas function()
#--------------------------------------------------------------
###============================================================
def run_rest2_hateoas_api_collector(DEBUG_LEVEL=0):
    
    if DEBUG_LEVEL != 0:
        print(f"{Fore.YELLOW+Back.LIGHTRED_EX+Style.BRIGHT} **** LEVEL:{DEBUG_LEVEL} DEBUG MODE ENABLED **** {Fore.RESET}")

    api_url, headers, auth = get_user_configuration()

    print("Navigating through the API using HATEOAS...")
    navigate_hateoas(api_url, headers, auth)
#===========================================================

#if __name__ == "__main__":
#    main()

