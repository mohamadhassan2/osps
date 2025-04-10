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

import socket
import threading
import time
import os
import glob

# Configuration
SYSLOG_PORT = 2514  # Standard syslog port
MESSAGES_NUM_THRESHOLD = 200000  # Number of messages before writing to disk
RATE_MSGS_PER_SEC_THRESHOLD = 10000000  # Messages per second before writing to disk
CACHE_DIR = "high_perf_syslog_cache"  # Directory to store cache files
CACHE_FILE_NAME = "syslog_cache.tmp"  # File name for the cache
MAX_CACHE_SIZE = 10 * 1024 * 1024  # Maximum size of the cache file in bytes (10MB)
TIME_WINDOW = 1  # Time window in seconds for rate calculation (1 second)

from colorama import Fore, Back, Style, init
# Initialize colorama
init()





# Global variables to manage incoming events and message rates
event_cache = []
message_count = 0
last_timestamp = time.time()

def print_configs(message_count=0, last_timestamp=0, event_cache=[]):
    print(f"{Fore.YELLOW+Style.BRIGHT}--------------------------------{Style.RESET_ALL}")
    #print(f"Syslog Server Configuration:")
    #print(f"Port: {SYSLOG_PORT}")
    print(f"TIME WINDOW (Time window in seconds for rate calculation): {TIME_WINDOW} seconds")
    print(f"MESSAGE THRESHOLD (Number of messages before writing to disk): {MESSAGES_NUM_THRESHOLD}          Current Message Count: {message_count}")
    print(f"RATE THRESHOLD (Messages per second before writing to disk): {RATE_MSGS_PER_SEC_THRESHOLD} messages/sec")
    print(f"MAX CACHE SIZE (Maximum size of the cache file in byte): {MAX_CACHE_SIZE / (1024 * 1024)}MB          Event Cache Size: {len(event_cache)}")
    print(f"Current Cache Size: {get_cache_size() / (1024 * 1024)} MB")
    #print(f"Current Message Count: {message_count}")
    print(f"Last Timestamp: {last_timestamp}")
    #print(f"Event Cache Size: {len(event_cache)}")
    print(f"{Fore.YELLOW+Style.BRIGHT}--------------------------------{Style.RESET_ALL}")

    return None
#-------------------------------------------------------------------------
# Function to write events to disk (cache file)
def write_cache_to_disk(events):
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    cache_file_path = os.path.join(CACHE_DIR, f"{timestamp}_{CACHE_FILE_NAME}")
    #cache_file_path = os.path.join(CACHE_DIR, CACHE_FILE_NAME)
    with open(cache_file_path, 'a') as f:
        for event in events:
            f.write(event + '\n')
    print(f"{Fore.GREEN}Cache written to: {cache_file_path} {Style.RESET_ALL}")
#-------------------------------------------------------------------------
#--------------------------------------------------------------------------
# Function to get the current cache size in bytes
def get_cache_size():
    cache_size = 0
    for root, dirs, files in os.walk(CACHE_DIR):
        for file in files:
            file_path = os.path.join(root, file)
            cache_size += os.path.getsize(file_path)
    return cache_size
#-------------------------------------------------------------------------
#--------------------------------------------------------------------------
# Function to handle the incoming syslog message
def handle_syslog(client_socket, client_address):
    global event_cache, message_count, last_timestamp
    try:
        # Receive data from the client
        data = client_socket.recv(1024).decode('utf-8')
        
        # Append the incoming event to the cache
        event_cache.append(data.strip())
        print_configs(message_count, last_timestamp, event_cache)
        print(f"{Back.BLUE}[msg count:{message_count}]{Style.RESET_ALL} 1) Received event from {client_address}:{data.strip()}")
        message_count += 1

        # Calculate the time window for rate-based threshold
        current_timestamp = time.time()
        if current_timestamp - last_timestamp >= TIME_WINDOW:
            last_timestamp = current_timestamp
            if message_count >= RATE_MSGS_PER_SEC_THRESHOLD:
                print_configs(message_count=message_count, last_timestamp=last_timestamp, event_cache=event_cache)
                print(f"{Fore.RED} 2)Rate threshold [count:{message_count}] exceeded, writing to disk...{Style.RESET_ALL}")
                write_cache_to_disk(event_cache)
                event_cache.clear()  # Clear the cache after writing to disk
                message_count = 0  # Reset message count after writing
        
        # If the event cache exceeds the message threshold or file size, write it to disk
        if len(event_cache) >= MESSAGES_NUM_THRESHOLD or get_cache_size() > MAX_CACHE_SIZE:
            print_configs(message_count=message_count, last_timestamp=last_timestamp, event_cache=event_cache)
            print(f"{Fore.CYAN+Style.BRIGHT} 3)Message threshold [len_evnt_cache:{len(event_cache)} or cache size exceeded, writing to disk...{Style.RESET_ALL}")
            write_cache_to_disk(event_cache)
            event_cache.clear()  # Clear the cache after writing to disk
        
    finally:
        client_socket.close()
#-------------------------------------------------------------------------
#=====================================================================
# Syslog server setup
def start_syslog_server():

    #--------------------------------------------------------------------
    #clean up old cache files we don't need
    delete_files = []
    if os.path.exists(CACHE_DIR):
        delete_files = glob.glob(os.path.join(CACHE_DIR, '*.tmp'))
    for file in delete_files:
        os.remove(file)
        #print(f"Deleted old cache files: {file}")
    # Ensure the cache directory exists
    if not os.path.exists(CACHE_DIR):
        #print(f"{Fore.RED+Style.BRIGHT+Back.BLUE}test color{Style.RESET_ALL}")
        print(f"Cache directory does not exist. Creating: {CACHE_DIR}")
    try:
        # Create the cache directory if it doesn't exist
        os.makedirs(CACHE_DIR)
        print(f"Cache directory created: {CACHE_DIR}")
    except Exception as e:
        print(f"Cache directory not createed.Already exists! {e}")
    #--------------------------------------------------------------------

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind(('0.0.0.0', SYSLOG_PORT))
    print(f"Syslog server started on port {SYSLOG_PORT}...")
    
    # Handle incoming messages
    message_count = 0
    last_timestamp = time.time()
    event_cache = []
    while True:
        data, addr = server_socket.recvfrom(1024)
        event = data.decode('utf-8').strip()
        #print(f"Received event: {event} from {addr}\n")  #debugging
        
        # Append to the event cache
        event_cache.append(event)
        message_count += 1
        
        # Calculate the time window for rate-based threshold
        current_timestamp = time.time()
        if current_timestamp - last_timestamp >= TIME_WINDOW:
            last_timestamp = current_timestamp
            if message_count >= RATE_MSGS_PER_SEC_THRESHOLD:
                print(f"{Fore.RED+Style.BRIGHT} 4)Rate threshold exceeded, writing cache to disk.. [msg count:{message_count} ...{Style.RESET_ALL}")
                print_configs(message_count=message_count, last_timestamp=last_timestamp, event_cache=event_cache)
                print(f"{Fore.RED} 4)Rate threshold [count:{message_count}] exceeded, writing to disk...{Style.RESET_ALL}")
                write_cache_to_disk(event_cache)
                event_cache.clear()  # Clear the cache after writing to disk
                message_count = 0  # Reset message count after writing
        
        # If cache threshold exceeded, write to disk
        if len(event_cache) >= MESSAGES_NUM_THRESHOLD or get_cache_size() > MAX_CACHE_SIZE:
            print_configs(message_count=message_count, last_timestamp=last_timestamp, event_cache=event_cache)
            print(f"{Fore.BLUE+Style.NORMAL} 5)Message threshold or cache size exceeded, writing to cache disk...{Style.RESET_ALL}")
            write_cache_to_disk(event_cache)
            event_cache.clear()  # Clear the cache after writing to disk
#=======================================================================


if __name__ == "__main__":
    start_syslog_server()

