import socket
import threading
import time
import os

# Configuration
SYSLOG_PORT = 1514  # Standard syslog port
MESSAGE_THRESHOLD = 100  # Number of messages before writing to disk
RATE_THRESHOLD = 10  # Messages per second before writing to disk
CACHE_DIR = "syslog_cache"  # Directory to store cache files
CACHE_FILE_NAME = "syslog_cache.log"  # File name for the cache
MAX_CACHE_SIZE = 10 * 1024 * 1024  # Maximum size of the cache file in bytes (10MB)
TIME_WINDOW = 1  # Time window in seconds for rate calculation (1 second)

# Ensure the cache directory exists
if not os.path.exists(CACHE_DIR):
    os.makedirs(CACHE_DIR)

# Global variables to manage incoming events and message rates
event_cache = []
message_count = 0
last_timestamp = time.time()

# Function to write events to disk (cache file)
def write_cache_to_disk(events):
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    cache_file_path = os.path.join(CACHE_DIR, f"{timestamp}_{CACHE_FILE_NAME}")
    
    with open(cache_file_path, 'a') as f:
        for event in events:
            f.write(event + '\n')
    print(f"Cache written to: {cache_file_path}")

# Function to get the current cache size in bytes
def get_cache_size():
    cache_size = 0
    for root, dirs, files in os.walk(CACHE_DIR):
        for file in files:
            file_path = os.path.join(root, file)
            cache_size += os.path.getsize(file_path)
    return cache_size

# Function to handle the incoming syslog message
def handle_syslog(client_socket, client_address):
    global event_cache, message_count, last_timestamp
    try:
        # Receive data from the client
        data = client_socket.recv(1024).decode('utf-8')
        
        # Append the incoming event to the cache
        event_cache.append(data.strip())
        print(f"Received event from {client_address}: {data.strip()}")
        message_count += 1

        # Calculate the time window for rate-based threshold
        current_timestamp = time.time()
        if current_timestamp - last_timestamp >= TIME_WINDOW:
            last_timestamp = current_timestamp
            if message_count >= RATE_THRESHOLD:
                print("Rate threshold exceeded, writing to disk...")
                write_cache_to_disk(event_cache)
                event_cache.clear()  # Clear the cache after writing to disk
                message_count = 0  # Reset message count after writing
        
        # If the event cache exceeds the message threshold or file size, write it to disk
        if len(event_cache) >= MESSAGE_THRESHOLD or get_cache_size() > MAX_CACHE_SIZE:
            print("Message threshold or cache size exceeded, writing to disk...")
            write_cache_to_disk(event_cache)
            event_cache.clear()  # Clear the cache after writing to disk
        
    finally:
        client_socket.close()

# Syslog server setup
def start_syslog_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind(('0.0.0.0', SYSLOG_PORT))
    print(f"Syslog server started on port {SYSLOG_PORT}...")
    
    # Handle incoming messages
    while True:
        data, addr = server_socket.recvfrom(1024)
        event = data.decode('utf-8').strip()
        print(f"Received event: {event} from {addr}")
        
        # Append to the event cache
        event_cache.append(event)
        message_count += 1
        
        # Calculate the time window for rate-based threshold
        current_timestamp = time.time()
        if current_timestamp - last_timestamp >= TIME_WINDOW:
            last_timestamp = current_timestamp
            if message_count >= RATE_THRESHOLD:
                print("Rate threshold exceeded, writing to disk...")
                write_cache_to_disk(event_cache)
                event_cache.clear()  # Clear the cache after writing to disk
                message_count = 0  # Reset message count after writing
        
        # If cache threshold exceeded, write to disk
        if len(event_cache) >= MESSAGE_THRESHOLD or get_cache_size() > MAX_CACHE_SIZE:
            print("Message threshold or cache size exceeded, writing to disk...")
            write_cache_to_disk(event_cache)
            event_cache.clear()  # Clear the cache after writing to disk

if __name__ == "__main__":
    start_syslog_server()

