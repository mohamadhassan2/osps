#Module to handle high-performance syslog caching with rate and size thresholds
'''
How it Works:
The server listens for incoming syslog messages over UDP on port 514.Messages are cached in the event_cache list.
If the total number of messages exceeds MESSAGES_NUM_THRESHOLD, the events are written to a file.
If the message rate exceeds RATE_MSGS_PER_SEC_THRESHOLD (messages per second), the events are also written to disk.
The server periodically checks if the message rate has exceeded the threshold within the TIME_WINDOW and writes to disk if necessary.
Cache file size is also monitored, and if it exceeds MAX_CACHE_SIZE, the events are written to disk.
Notes:
Threshold Values: You can adjust MESSAGES_NUM_THRESHOLD, RATE_MSGS_PER_SEC_THRESHOLD, and MAX_CACHE_SIZE to suit your needs.
Multithreading: If the system needs to handle multiple clients concurrently, you can use threading or asyncio to handle each connection in a separate thread.
Rate Limiting: This script uses a fixed time window (TIME_WINDOW) to calculate the message rate. You can adjust this value to match the desired rate of events.
Notes:
To handle high loads (messages per second) with a syslog server and buffer incoming messages efficiently, you can implement a file-based queueing.
This system will help you handle overload by writing incoming messages to disk (in a queue-like manner) when memory or message rate exceeds a threshold.
Steps:
In-Memory Buffering: Keep an in-memory buffer to temporarily store incoming messages.
Overflow Handling: When the buffer reaches a certain threshold, write messages to a file-based queue (a disk file).
Disk Queueing: Use a file-based queue that can handle incoming messages when the rate exceeds the in-memory buffer capacity.
Asynchronous File Writing: Implement an asynchronous or buffered file writing mechanism to handle messages in the queue.
'''

import time
import os
import glob
import math
from colorama import Fore, Back, Style,  init    # Import colorama for colored terminal output
# Initialize colorama
init(autoreset=True)  # Automatically reset color after each print

#-----------------------  Importing my modules & local configs -------------------
# Configuration
MESSAGES_NUM_THRESHOLD = 1000  # Number of messages before writing to disk
RATE_MSGS_PER_SEC_THRESHOLD = 10000 #10000000  # Messages per second before writing to disk
#CAHCHE_DIR = "hec_wsgi_que"  # Directory to store cache files
CACHE_FILE_NAME = "raw_tcp.tmp"  # File name for the cache
MAX_CACHE_SIZE = 10 * 1024 * 1024  # Maximum size of the cache file in bytes (10MB)
TIME_WINDOW = 1  # Time window in seconds for rate calculation (1 second)
#-----------------------  Importing my modules & local configs -------------------

# Global variables to manage incoming events and message rates
event_cache = []
#essage_count = 0
#last_timestamp = time.time()

#---------------------------------------------------------------------
def print_que_configs(debug_level,  message_count=0, last_timestamp=0, event_cache=[], cache_dir=''):
    print(f"D{debug_level}{Fore.YELLOW}---------------[{__name__}] Que configurations---------------")
    #print(f"Syslog Server Configuration:")
    #print(f"Port: {SYSLOG_PORT}")
    print(f"TIME WINDOW (Time window in seconds for rate calculation): {Fore.BLUE}{TIME_WINDOW} seconds")
    print(f"Last Timestamp: {Fore.BLUE}{last_timestamp}")
    print(f"MESSAGES_NUM_THRESHOLD (Number of messages before writing to disk): {Fore.BLUE+Style.BRIGHT}{MESSAGES_NUM_THRESHOLD} msgs\t\t{Fore.YELLOW}[Current Msgs Count: {message_count}]")
    print(f"RATE_MSGS_PER_SEC_THRESHOLD (Messages per second before writing to disk): {Fore.BLUE+Style.BRIGHT}{RATE_MSGS_PER_SEC_THRESHOLD} messages/sec")
    print(f"MAX CACHE SIZE (Maximum size of the cache file in bytes): {Fore.BLUE}{MAX_CACHE_SIZE / (1024 * 1024)}MB\t\t\t{Fore.YELLOW}[Event Cache Size: {len(event_cache)}]")
    print(f"Current Cache Size: {Fore.BLUE}{get_cache_size(cache_dir) / (1024 * 1024)} MB")
    
    print(f"D{debug_level}{Fore.YELLOW}---------------[{__name__}] Que configurations---------------")
    #print(f"Event Cache Size: {len(event_cache)}")
    return None
#End of function print_que_configs()
#-------------------------------------------------------------------------
# Function to write events to disk (cache file)
def write_cache_to_disk(events,cache_dir, debug_level):
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    #cache_file_path = os.path.join(cache_dir, f"{timestamp}_{CACHE_FILE_NAME}")
    cache_file_path = os.path.join(cache_dir, CACHE_FILE_NAME)
    with open(cache_file_path, 'a') as f:
        for event in events:
            #print (f"EVENTS:[{events}]  TYPE:[{type(event)}]")    #debug
            #f.write(event + '\n')
            f.write(event.decode('utf-8'))  # Decode bytes to string before writing
    if debug_level >= 2:        
        print(f"D{debug_level}{Fore.GREEN}[{__name__}]Cache written to: {cache_file_path}")
#End of function write_cache_to_disk()    
#-------------------------------------------------------------------------
#-------------------------------------------------------------------------
def setup_cache_directory(cache_dir,debug_level=0):
    #clean up old cache files we don't need
    delete_files = []
    if os.path.exists(cache_dir):
        delete_files = glob.glob(os.path.join(cache_dir, '*.tmp'))
    for file in delete_files:
        os.remove(file)
        #print(f"Deleted old cache files: {file}")
    # Ensure the cache directory exists
    if not os.path.exists(cache_dir):
        if debug_level >= 3:
            print(f"D{debug_level}[{__name__}]Cache directory [{cache_dir}] does not exist. Creating...")
    try:
        # Create the cache directory if it doesn't exist
        os.makedirs(cache_dir)
        #print(f"Cache directory created: {cache_dir}")
    except Exception as e:
        if debug_level >= 1:
            print(f"[{__name__}]Cache directory [{cache_dir}] present! ")   #{e}")
#End of function setup_cache_directory()
#--------------------------------------------------------------------
#--------------------------------------------------------------------------
# Function to get the current cache size in bytes
def get_cache_size(cache_dir):
    cache_size = 0
    for root, dirs, files in os.walk(cache_dir):
        for file in files:
            file_path = os.path.join(root, file)
            cache_size += os.path.getsize(file_path)
    return cache_size
#End of function get_cache_size()
#-------------------------------------------------------------------------
#=====================================================================
def send_to_que(data, cache_dir, message_count, last_timestamp=0, event_cache=[], debug_level=0):
    
    
    event = data.decode('utf-8').strip()
    #print(f"Received event: {event} from {addr}\n")  #debugging
    event_cache.append(data)
    #message_count += 1
        
    # Calculate the time window for rate-based threshold
    current_timestamp = time.time()
    diff = math.ceil(current_timestamp - last_timestamp)
    rate = math.ceil(message_count) / diff if diff > 0 else 0
    #count=83, rate = 8.00 msg/sec
    #print (f"Count={message_count},  Rate={rate:.2f} msg/sec [RATE_MPS_THRESHOLD:{RATE_MSGS_PER_SEC_THRESHOLD}][WINDOW:{TIME_WINDOW}]    Drift[{diff:.2f}/{TIME_WINDOW}]")  #debugging
    if diff >= TIME_WINDOW:
        last_timestamp = current_timestamp
        if rate >= RATE_MSGS_PER_SEC_THRESHOLD:
            if debug_level >= 1:
                print(f"D{debug_level}{Fore.CYAN+Style.BRIGHT}[{__name__}]> Msg/sec Rate threshold [{rate}/{RATE_MSGS_PER_SEC_THRESHOLD}] exceeded, writing cache to disk...")
            write_cache_to_disk(event_cache, cache_dir, debug_level)
            event_cache.clear()  # Clear the cache after writing to disk
            message_count = 0  # Reset message count after writing
    #print(message_count)      


    cache_dir_size_mb = get_cache_size(cache_dir) / (1024 * 1024)  # Convert to MB
    MAX_CACHE_SIZE_MB = MAX_CACHE_SIZE / (1024 * 1024)  # Convert to MB
    cache_size = get_cache_size(cache_dir)

    a=(len(event_cache) >= MESSAGES_NUM_THRESHOLD)
    b=(cache_size > MAX_CACHE_SIZE)
    #a=False; b=False
    #identify the trigger in print() output with colors
    #print(f" cache size:{cache_dir_size_mb:.2f}MB  MAX:{MAX_CACHE_SIZE_MB}MB]")
    if a or b:
        if debug_level >= 1:
            if a and b:
                print(f"D{debug_level}{Fore.BLUE+Style.NORMAL}[{__name__}> Max num msgs threshold {Fore.YELLOW}[{len(event_cache)}/{MESSAGES_NUM_THRESHOLD}] {Fore.BLUE+Style.NORMAL}or event cache size {Fore.YELLOW}[{cache_dir_size_mb:.2f}MB/{MAX_CACHE_SIZE_MB}MB] {Fore.BLUE+Style.NORMAL}exceeded, writing to cache disk...{Fore.RESET}")
            elif a and not b:
                print(f"D{debug_level}{Fore.BLUE+Style.NORMAL}[{__name__}> Max num msgs threshold {Fore.YELLOW}[{len(event_cache)}/{MESSAGES_NUM_THRESHOLD}] {Fore.BLUE+Style.NORMAL}or event cache size [{cache_dir_size_mb:.2f}MB/{MAX_CACHE_SIZE_MB}MB] {Fore.BLUE+Style.NORMAL}exceeded, writing to cache disk...{Fore.RESET}")
            elif b and not a:
                print(f"D{debug_level}{Fore.BLUE+Style.NORMAL}[{__name__}> Max num msgs threshold [{len(event_cache)}/{MESSAGES_NUM_THRESHOLD}] {Fore.BLUE+Style.NORMAL}or event cache size {Fore.YELLOW}[{cache_dir_size_mb:.2f}MB/{MAX_CACHE_SIZE_MB}MB] {Fore.BLUE+Style.NORMAL}exceeded, writing to cache disk...{Fore.RESET}")
                    
        write_cache_to_disk(event_cache, cache_dir,debug_level)
        event_cache.clear()  # Clear the cache after writing to disk

    if debug_level >= 4:      
        print_que_configs(debug_level, message_count, last_timestamp=last_timestamp, event_cache=event_cache)

#End of function send_to_que()            
#=======================================================================


#if __name__ == "__main__":
#    start()

'''
Original code:
#=====================================================================
def send_to_que(data, cache_dir, message_count=0, last_timestamp=0, event_cache=[]):
    
    setup_cache_directory(cache_dir)  # Ensure the cache directory exists. Delete on startup

    # Handle incoming messages
   # message_count = 0
   # last_timestamp = time.time()
   # event_cache = []
    
    while True:
        #data, addr = server_socket.recvfrom(1024)      #<------receive data from the socket
        event = data.decode('utf-8').strip()
        #print(f"Received event: {event} from {addr}\n")  #debugging
        # Append to the event cache
        event_cache.append(data)
        message_count += 1
        
        # Calculate the time window for rate-based threshold
        current_timestamp = time.time()
        if current_timestamp - last_timestamp >= TIME_WINDOW:
            last_timestamp = current_timestamp
            if message_count >= RATE_MSGS_PER_SEC_THRESHOLD:
                print(f"{Fore.RED+Style.BRIGHT} 4)Rate threshold exceeded, writing cache to disk.. [msg count:{message_count} ...")
                print_que_configs(message_count=message_count, last_timestamp=last_timestamp, event_cache=event_cache)
                print(f"{Fore.RED} 4)Rate threshold [count:{message_count}] exceeded, writing to disk...")
                write_cache_to_disk(event_cache, cache_dir)
                event_cache.clear()  # Clear the cache after writing to disk
                message_count = 0  # Reset message count after writing
        # If cache threshold exceeded, write to disk
        if len(event_cache) >= MESSAGES_NUM_THRESHOLD or get_cache_size(cache_dir) > MAX_CACHE_SIZE:
            print_que_configs(message_count=message_count, last_timestamp=last_timestamp, event_cache=event_cache)
            print(f"{Fore.BLUE+Style.NORMAL} 5)Message threshold or cache size exceeded, writing to cache disk...")
            write_cache_to_disk(event_cache, cache_dir)
            event_cache.clear()  # Clear the cache after writing to disk

#End of function send_to_que()            
#=======================================================================



'''