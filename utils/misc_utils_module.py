#Module: misc_utils_module.py

import logging
import sys
import socket
import os
import time
import csv
import traceback
import requests
from datetime import datetime
import json
import sys

#------------------  Importing my modules & Local configs -------------------
from configs.globals_module import  OSPS_DEFAULT_LOG_FILE
#------------------  Importing my modules & Local configs -------------------

logger = logging.getLogger(__name__)

#--------------------------------------------------------------
# Function to print error details
def print_error_details(e):
    exc_type, exc_value, exc_traceback = sys.exc_info()
    traceback_details = traceback.extract_tb(exc_traceback)
    filename, line_number, function_name, text = traceback_details[-1]
    print(f"{Fore.RED}Error: {e}")
    print(f"{Fore.RED}Error occurred in file: {filename}")
    print(f"{Fore.RED}Line number: {line_number}")
    print(f"{Fore.RED}Function name: {function_name}\n")
    logging.error(f"Error occurred in file: {filename}")
#End of print_error_details()
# -------------------------------------------------------------
#--------------------------------------------------------------
# Set up logging configuration
def setup_logging(log_file=OSPS_DEFAULT_LOG_FILE):
    logger = logging.getLogger()    # Create a logger instance
    logger.setLevel(logging.INFO) #Set the logging level to INFO
    
    console_handler = logging.StreamHandler()   # Create a console handler and set its level to INFO
    console_handler.setLevel(logging.INFO)
    
    file_handler = logging.FileHandler(log_file) # Create a file handler to log messages to a file and set its level to INFO
    file_handler.setLevel(logging.INFO)
    
    # Create a formatter and set it for both handlers
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - \033[94m%(message)s\033[0m')
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)
    
    # Add both handlers to the logger
    #logger.addHandler(console_handler)  #Rem to stop**! console handler to the logger
    logger.addHandler(file_handler) # Add the file handler to the logger
    
    return logger
#End of setup_logging()
#--------------------------------------------------------------
#--------------------------------------------------------------
#Function to setup signal traps. We need to know when user hit CTRL-C
def signal_handler(sig, frame):
        print('You pressed Ctrl+C!')
        print("\nSIGINT received. Shutting down gracefully...")
        logger.info("SIGINT received. Shutting down gracefully...")
        sockets = []  # List to store all socket connections
        for s in sockets:
            try:
                s.shutdown(socket.SHUT_RDWR)  # Disable further sends and receives
                s.close()
            except OSError as e:
             print(f"Error closing socket: {e}")
        
        sys.exit(0)

    #singal.pause()
    #return
#end of setup_signal_handling():
#------------------------------------------------------------------------------
#------------------------------------------------------------------------------
from colorama import Back, Style, init, Fore
# Initialize colorama
init(autoreset=True)  # Automatically reset color after each print

#print(Fore.RED + "This is red text")
#print(Fore.GREEN + "This is green text")
#print(Back.YELLOW + "This text has a yellow background")
#print(Style.BRIGHT + "This is bright text")
#print(Fore.CYAN + Back.MAGENTA + "This is cyan text with a magenta background")
#print(Style.RESET_ALL + "This is back to normal text")
#--------------------------------------------------------------
#--------------------------------------------------------------
class C:
    # ANSI escape codes for different colors
    COLORS = {
        "reset": "\033[0m",
        "bold": "\033[1m",
        "underline": "\033[4m",
        "black": "\033[30m",
        "red": "\033[31m",
        "green": "\033[32m",
        "yellow": "\033[33m",
        "blue": "\033[34m",
        "magenta": "\033[35m",
        "cyan": "\033[36m",
        "white": "\033[37m",
        "grey": "\033[90m",
        "light_red": "\033[91m",
        "light_green": "\033[92m",
        "light_yellow": "\033[93m",
        "light_blue": "\033[94m",
        "light_magenta": "\033[95m",
        "light_cyan": "\033[96m",
        "light_white": "\033[97m",
    }
    @staticmethod
    def printline(text, color="reset", bold=False, underline=False):
        """
        Print text in a specified color.
        :param text: The text to be printed
        :param color: The color name (default is 'reset')
        :param bold: If True, text will be bold
        :param underline: If True, text will be underlined
        """
        color_code = C.COLORS.get(color, C.COLORS["reset"])
        # Apply bold and underline if requested
        if bold:
            color_code = "\033[1m" + color_code
        if underline:
            color_code = "\033[4m" + color_code    
        print(f"{color_code}{text}{C.COLORS['reset']}")
# Example usage:
    ''''
    C.printline("This is a normal message.", "reset")    # Default color
    C.printline("This is an error message.", "red")  # Print in red color
    C.printline("This is a success message.", "green", bold=True)    # Print in green color with bold
    C.printline("This is an informational message.", "blue", underline=True) # Print in blue color with underline
    C.printline("This is a warning message.", "yellow", bold=True, underline=True)'  # Print in yellow with both bold and underline
    '''
#End of class C    
#--------------------------------------------------------------
#------------------------------------------------------------------------------
def progressBar(iterable, page, status , prefix = '', suffix = '', decimals = 1, length = 100, fill = '#', printEnd = "\r"):
    #print (iterable, "  ", len(iterable))
    """
    https://stackoverflow.com/questions/3173320/text-progress-bar-in-terminal-with-block-characters
    Call in a loop to create terminal progress bar
    @params:
        iterable    - Required  : iterable object (Iterable)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
    """
    total = len(iterable)
    # Progress Bar Printing Function
    def printProgressBar (iteration):
        percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
        filledLength = int(length * iteration // total)
        bar = fill * filledLength + '-' * (length - filledLength)
        print(f'\r{prefix}[page:{page}] |{bar}| {percent}% {suffix}    [status:{status}]', end = printEnd)
    # Initial Call
    printProgressBar(0)
    # Update Progress Bar
    for i, item in enumerate(iterable):
        yield item
        printProgressBar(i + 1)
    # Print New Line on Complete
    print()
#End of progressBar(iterable, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█', printEnd = "\r"):    
#------------------------------------------------------------------------------
#------------------------------------------------------------------------------
#Function to count the lines in CSV file to see if has been populated
def count_lines(output_file_name):
    with open(output_file_name, 'r') as fp:
        lines = len (fp.readlines()) - 1
    return lines        
#end of count_lines()
#------------------------------------------------------------------------------
#------------------------------------------------------------------------------
#Function to check if the event is a valid JSON string
def is_json(event):
    try:
        json.loads(event)
        return True
    except ValueError:
        return False
#end of is_json(event):
#------------------------------------------------------------------------------
#------------------------------------------------------------------------------
def csv_to_json_file(csv_filepath, json_filepath):
    data = []
    with open(csv_filepath, 'r') as csvfile:
        csv_reader = csv.DictReader(csvfile)
        for row in csv_reader:
            data.append(row)

    with open(json_filepath, 'w') as jsonfile:
        json.dump(data, jsonfile, indent=4)

    return data.count("GHSA ID")    
#-------------------------------------------------------------------------
#------------------------------------------------------------------------------
#This code snippet utilizes the sys.stdout.write and sys.stdout.flush methods to overwrite the previous
#timer value on the same line, creating the effect of a live countdown. The \r character moves the cursor
#to the beginning of the line before writing the new timer value.
def countdown(t):
    while t:
        mins, secs = divmod(t, 60)
        timer = '\033[36m{:02d}:{:02d}'.format(mins, secs)
        sys.stdout.write('\r' + timer)
        sys.stdout.flush()
        time.sleep(1)
        t -= 1
    print("  Done!\033[0m\n")
# End of def countdown(t):    
#------------------------------------------------------------------------------
#------------------------------------------------------------------------------
#Function to determine how long to pause between git api call (if you need to).
def ask_to_run_timer(timer_in_sec):        
   
    user_input = input(f"Want to pause (calcuated) for \033[36m{timer_in_sec/60:.2f} mins \033[0m[{timer_in_sec} sec] before trying again (y/N)?")
    if user_input == "y" :
        print(f"Yes") 
        print (f"Sleeping [{timer_in_sec/60:.2f}] mins...")
        logging.info (f"Sleeping [{timer_in_sec/60:.2f}] mins...")
        #time.sleep (timer_in_sec)
        countdown(int(timer_in_sec))
    else:
        print(f"No")    #don't run timer
    print("\n")    
    
    return user_input
#end of ask_to_run_timer(timer_in_sec):
#------------------------------------------------------------------------------
#------------------------------------------------------------------------------
#Function to Checks the rate limit status for the GitHub API.
#Check API rate limits data  and calculate wait timer base on time difference------------
# Args:
#        github_token (str, optional): Your GitHub personal access token. 
#        If not provided, it will attempt to read from the GITHUB_TOKEN environment variable.
#Returns:
#        dict: A dictionary containing rate limit information, or None if an error occurs.
# 
def check_rate_limit(github_token=None):
    print(f"➡️ \033[94m>>Getting GitHub API Rate Limit Information...\033[0m")
    logging.info (f"➡️ \033[94m>>Getting GitHub API Rate Limit Information...\033[0m")
   
    if github_token is None:
        github_token = os.environ.get("GITHUB_TOKEN")
        if github_token is None:
            print("⛔️ Error: GitHub token not found. Set GITHUB_TOKEN environment variable or pass it as an argument.")
            logging.error ("⛔️ Error: GitHub token not found. Set GITHUB_TOKEN environment variable or pass it as an argument.")
            return None

    headers = {'Authorization': f'token {github_token}'}
    response = requests.get('https://api.github.com/rate_limit', headers=headers)

    if response.status_code == 200:
        return response.json()['resources']['core']
    else:
        print(f"⛔️ \033[41;37mError: Failed to retrieve rate limit information. Status code: [\033[33;4m{response.status_code}]\033[0m")
        logging.error (f"⛔️ \033[41;37mError: Failed to retrieve rate limit information. Status code: [\033[33;4m{response.status_code}]\033[0m")
        return None
#end of check_rate_limit(github_token=None):    
#------------------------------------------------------------------------------
#------------------------------------------------------------------------------
def calculate_pause_timer(rate_limit):
     
    rate_limit_timestamp_epoc = (rate_limit['reset'])
    datetime_object_utc = datetime.fromtimestamp(rate_limit_timestamp_epoc)
    
    print (f"API Rate Limting Data: [Limit:{rate_limit['limit']}]\t[Remaining in window:{rate_limit['remaining']}]\t[Used:{rate_limit['used']}]\t[Window will reset at:{datetime_object_utc}]")
    logging.info (f"API Rate Limting Data: [Limit:{rate_limit['limit']}][Remaining in window:{rate_limit['remaining']}][Used:{rate_limit['used']}][Window will reset at:{datetime_object_utc}]")
    
    curr_timestamp_epoc = int (time.time() )
    current_datetime = datetime.now()
    current_datetime = current_datetime.strftime("%Y-%m-%d %H:%M:%S")
    print("Current Timestamp:\t", curr_timestamp_epoc, "\t\t", current_datetime )
    print("Rate Limit Timestamp:\t", rate_limit_timestamp_epoc, "\t\t", datetime.fromtimestamp(rate_limit_timestamp_epoc))
    #timer = int(( rate_limit_timestamp_epoc - curr_timestamp_epoc)/60 )
    timer_in_sec = (rate_limit_timestamp_epoc - curr_timestamp_epoc)
    print ("Calculated ideal pause (in seconds):\t\t", timer_in_sec,"[", round(timer_in_sec/60,2), "mins].")

    #pause_in_sec = 10   #debug
    answer = "n"        #default not to pause
    remaining = int (rate_limit['remaining'])   #convert set to int
    if (remaining < 1 ) or (curr_timestamp_epoc > rate_limit_timestamp_epoc) :
        answer = ask_to_run_timer(timer_in_sec)
        print ("You answerd: [", answer,"]") 

    return timer_in_sec, answer

#end calculate_pause_timer():    
#------------------------------------------------------------------------------



r""""  Test routines below has escape code. Need to use r trick for mutli-line comments
#--------------------------------------------------------------
def parse_5424(syslog_line):
    # Regex to parse the RFC 5424 syslog format
    #regex = r"^(<(?P<pri>\d{1,3})>)\d (?P<timestamp>[0-9\-T:.Z]+) (?P<hostname>[\w.-]+) (?P<appname>\w+) (?P<procid>\S+) (?P<msgid>\S+) (?P<structured_data>(?:\[[^\]]*\])*) (?P<message>.+)$"
    # Match the syslog message with the regex
    match = re.match(regex, syslog_line)
    if not match:
        #raise ValueError("Invalid syslog format")
        print(f"\033[91mInvalid syslog 5424 format\033[0m")
    # Extract matched groups
    parsed_data = match.groupdict()
    # Parse the PRI value (facility and severity)
    parsed_data['pri'] = parsed_data['pri']  # just extract PRI as a string
    timestamp_str = parsed_data['timestamp']    # Extract the timestamp string into datatime object
    try:
        parsed_data['timestamp'] = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
    except ValueError:
        #raise ValueError(f"Invalid timestamp format: {timestamp_str}")
        print(f"\033[91mInvalid 5424 timestamp format: {timestamp_str}\033[0m")
    
    # Return the parsed log data
    return parsed_data
#End of parse_5424()    
#--------------------------------------------------------------

#--------------------------------------------------------------
def parse_rfc3164(syslog_lines):
    # Regex to parse the RFC 3164 syslog format
   # regex = r"^(<(?P<pri>\d{1,3})>)\w{3} +(?P<day>\d{1,2}) (?P<time>\d{2}:\d{2}:\d{2}) (?P<hostname>[\w.-]+) (?P<appname>\w+): (?P<message>.+)$, re.MULTILINE"
    # Match the syslog message with the regex
    match = re.match(regex, syslog_lines)
    if not match:
        #print (syslog_lines)
        #raise ValueError("🔴 Invalid syslog 3164 format", {syslog_lines})
        print(f"\033[91mInvalid syslog 3164 format\033[0m", {syslog_lines})
        #return None
    # Extract matched groups
    parsed_data = match.groupdict()
    if match:
        print (match.groupsdict())
    else:
        print ("Match not found")

    exit()
    # Parse the PRI value (facility and severity)
    parsed_data['pri'] = parsed_data['pri']  # just extract PRI as a string

    # Combine the month, day, and time to form the timestamp
    month = syslog_lines.split()[1]  # Extract the month (e.g., Apr)
    timestamp_str = f"{month} {parsed_data['day']} {parsed_data['time']}"
    
    # Convert to a full timestamp (add current year for consistency)
    try:
        parsed_data['timestamp'] = datetime.strptime(timestamp_str, "%b %d %H:%M:%S")
    except ValueError:
        #raise ValueError(f"Invalid timestamp format: {timestamp_str}")
        print(f"\033[91mInvalid 3164 timestamp format: {timestamp_str}\033[0m")
    # Return the parsed log data
    return parsed_data
#End of parse_rfc3164()    
#--------------------------------------------------------------
"""
