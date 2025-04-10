#Module: syslog_receiver_server_module.py
# # # This module implements a syslog server that listens for incoming syslog messages over UDP and TCP.
# # # It is designed to be run as a standalone script or integrated into a larger system for receiving and processing syslog data.
# # # It is intended to be used in conjunction with other components, such as a logging framework or data processing pipeline.
# # #--------------------------------------------------------------

from datetime import datetime
import json
import logging
import re
import socket
import threading
import time
from colorama import Fore, Back, Style, init
# Initialize colorama
init(autoreset=True)  # Automatically reset color after each print

#-----------------------  Importing my modules & local configs -------------------
OSPS_DEFAULT_LOG_FILE = "osps.log"
DEFAULT_DEBUG_LEVEL = 0
DEFAULT_SYSLOG_FILE = "syslog_server.log"
SYSLOG_RECV_HOST = '0.0.0.0'
SYSLOG_RECV_UDP_PORT = 1514  # Default syslog UDP port
SYSLOG_RECV_TCP_PORT = 1514  # Default syslog TCP port
SYSLOG_TCP_RECV_BUFF_SIZE = 1024  # Buffer size for TCP. Increase if needed
CACHE_DIR = 'syslog_que'

from utils.misc_utils_module import print_error_details, setup_logging, signal_handler
from utils.caching_engine_module import CacheEngine, fetch_data_from_api2
#-----------------------  Importing my modules & local configs -------------------

logger = setup_logging(DEFAULT_SYSLOG_FILE)  # Set up logging configuration

#--------------------------------------------------------------
def parse_syslog_message(data, DEBUG_LEVEL=0):
    """Parse syslog message based on RFC 3164 or RFC 5424"""
    #-----
    #RFC3164_REGEX = re.compile(
    #   r"^(?P<pri><\d{1,3}>)(?P<timestamp>\w{3} \d{1,2} \d{2}:\d{2}:\d{2}) (?P<hostname>[\w.-]+) (?P<appname>\w+) (?P<msgid>\S+) (?P<message>.*)$")
    #RFC3164_REGEX = re.compile(r"^line", re.MULTILINE)
    RFC3164_REGEX = re.compile(
        r"^^(?P<pri><\d{1,3}>)|(?P<timestamp>\w{3}  {1,2}\d{1,2} \d{2}:\d{2}:\d{2}) (?P<hostname>\S+) (?P<appname>\S+)(?:\[(?P<pid>\d+)\])?: (?P<message>.+)$", re.M)
    RFC5424_REGEX = re.compile(
    r"^(?P<pri><\d{1,3}>)(?P<version>\d{1}) (?P<timestamp>[\d-]+T[\d:.]+[\w+]+) (?P<hostname>[\w.-]+) (?P<appname>\w+) (?P<procid>\S+) (?P<msgid>\S+) (?P<structureddata>\S*) (?P<message>.*)$", re.M)
    #-------    
    # Check if it's RFC 5424
    match_5424 = RFC5424_REGEX.match(data)
    if match_5424:
        logtype = "RFC5424"
        if DEBUG_LEVEL >= 2:
            print(f"{Fore.LIGHTBLUE_EX}Stream matched --RFC 5424--")
            logger.info(f"{Fore.LIGHTBLUE_EX}Stream matched --RFC 5424--")
        if DEBUG_LEVEL >=4:
            pairs = data.split("\n")    # Split the data into lines
            for pair in pairs:
                value = (pair.split(","))   # Split each line into key-value pairs
                #print (f"Pair: ->[{pair}]<-")
                matches = RFC5424_REGEX.match(pair)
                print( f"{Fore.LIGHTYELLOW_EX}{json.dumps(matches.groupdict(), indent=4)}")  #show syslog lines as json

        return logtype, match_5424.groupdict()
    else:
        logtype = "UNKNOWN"
    
    match_3164 = RFC3164_REGEX.match(data)
    if match_3164:
        logtype = "RFC3164"
        if DEBUG_LEVEL >= 2:
            print(f"{Fore.LIGHTBLUE_EX}Stream matched --RFC 3164--")
            logger.info(f"{Fore.LIGHTBLUE_EX}Stream matched --RFC 3164--")
        if DEBUG_LEVEL >= 4:    
            pairs = data.split("\n")    # Split the data into lines
            for pair in pairs:
                value = (pair.split(","))   # Split each line into key-value pairs
                matches = RFC3164_REGEX.match(pair)
                print(f"{Fore.LIGHTBLUE_EX}{json.dumps(matches.groupdict(), indent=4)}")    #show syslog lines as json
        return logtype, match_3164.groupdict()
    else:
        logtype = "UNKNOWN"
    
    return logtype, None
#End of parse_syslog_message()
#--------------------------------------------------------------
#--------------------------------------------------------------
def handle_syslog_message(data, address, protocol, DEBUG_LEVEL=0, mps=0):
    """Process and log the syslog message"""
    rfc_type = "RCF"
    if DEBUG_LEVEL >= 2:
        print(f"[{len(data)}] Bytes received {Fore.MAGENTA}{protocol}{Fore.RESET} syslog message from {address}")
        logger.info(f"[{len(data)}] Bytes received {Fore.MAGENTA}{protocol}{Fore.RESET} syslog message from {address}")   # Log to file
    if DEBUG_LEVEL >= 3:
        print(f"{Fore.LIGHTMAGENTA_EX}DATA:[{data}]{Fore.LIGHTBLACK_EX}  [lenght:{len(data)}]{Fore.RESET} ")  # Print without newline
        logger.warning(f"{Fore.LIGHTMAGENTA_EX}DATA:[{data}]{Fore.LIGHTGREEN_EX}  [length:{len(data)}]{Fore.RESET}) # Log to file")         
    
    #print(f"\033[91mReceived syslog message from {address}: {data}{Fore.RESET}")
    rfc_type, log_data = parse_syslog_message(data, DEBUG_LEVEL)   #; print(f"\n{Fore.MAGENTA}Parsed syslog message:{Fore.RESET} >[{log_data}]<") ; exit()
    #print (f"{rfc_type}:  {type(rfc_type)}")
    
    if log_data:
        message = log_data.get('message', '')
        timestamp = log_data.get('timestamp', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        log_msg = f"{timestamp} - {message}"
        logger.info(f"Logged: {log_msg}")   # Log to file    
        
        #......... caching code .....................................
        #print (f"MPS in handle_syslog_message(): {mps:.2f}")
        # Create an instance of CacheEngine
        #cache_engine = CacheEngine(cache_lifetime=CACHE_LIFETIME, high_request_threshold=HIGH_REQ_THRESHOLD, cache_dir=CACHEDIR)
        #cache_key = "in_syslog"   #also used a filename in cache dir
        # Simulate getting cached data or fresh data from the API
        #data = cache_engine.get_cached_data(cache_key, fetch_data_from_api2, mps)
        #from_file_cache=False
        #data, from_file_cache = cache_engine.get_cached_data(cache_key, log_data, mps )
        #print(f"\033[31mFetched Data to cache>>>:{Fore.RESET} {data}")
        #print(f"\033\[31mFetched Data to cache>>>: {log_msg}{Fore.RESET}")
        #if from_file_cache:
        #    print(f"{Fore.MAGENTA}Logged:{Fore.RESET} {log_msg}") # Display on console. Dimmed text
        #else:    
        #    print(f"{Fore.MAGENTA};47mLogged:{Fore.RESET} {log_msg}") # Display on console
        #......... caching code .....................................

    else:
        if DEBUG_LEVEL >= 3:
                print(f" Stream matched --RFC {rfc_type}-- {Fore.LIGHTRED_EX}Failed to parse. At least one event is not confirming to RFC!")
                logger.warning(f" Stream matched --RFC {rfc_type}-- {Fore.LIGHTRED_EX}Failed to parse. At least one event is not confirming to RFC!")
        #print("\033[94mFailed to parse syslog message!{Fore.RESET}")
    
#End of handle_syslog_message()        
#--------------------------------------------------------------        
#--------------------------------------------------------------
def syslog_server_udp(host, port, DEBUG_LEVEL=0):
    """Run a syslog server for UDP"""
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind((host, port))
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # Allow address reuse when restarting the server quickly
  #  server_socket.setblocking(False)  # Set non-blocking mode
    print(f"Syslog server {Fore.MAGENTA}(UDP){Fore.RESET} listening on {host}:{port}\n")
    logger.info(f"Syslog server {Fore.MAGENTA}(UDP){Fore.RESET} listening on {host}:{port}")   # Log to file   
    #print(f"\033[96mSyslog server (UDP) listening on {host}:{port}{Fore.RESET}")
    counter = 0
    data = {}
    while True:
        counter += 1
        data, address = server_socket.recvfrom(1024)  # buffer size
        data = data.decode('utf-8').strip()
        handle_syslog_message(data, address, "UDP", DEBUG_LEVEL,0)  # Process the message
#End of syslog_server_udp()        
#--------------------------------------------------------------
#--------------------------------------------------------------
def calc_msg_per_sec(message_count, previous_time):
  
    current_time = time.time()
    elapsed_time = current_time - previous_time
    mps=0
    if elapsed_time >= 1:
        mps = message_count / elapsed_time
        message_count = 0
        previous_time = current_time
        
    return mps        
#End of calc_msg_per_sec()
#--------------------------------------------------------------
#--------------------------------------------------------------
def syslog_server_tcp(host, port, DEBUG_LEVEL=0):
    """Run a syslog server for TCP"""
    server_socket = None
    RECVBUF = SYSLOG_TCP_RECV_BUFF_SIZE  # Buffer size for TCP. Increase if needed
    try:
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # TCP socket
        server_socket.bind((host, port))  # Bind to host and port
        server_socket.listen(5)  # Listen for incoming connections (max 5)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # Allow address reuse when restarting the server quickly

        print(f"Syslog server {Fore.LIGHTBLUE_EX}(TCP){Fore.RESET} listening on {host}:{port}")
        logger.info(f"Syslog server {Fore.LIGHTBLUE_EX}(TCP){Fore.RESET} listening on {host}:{port}")
        counter = 0
        while True:
            counter += 1
            client_socket, client_address = server_socket.accept()  # Accept incoming connection
            try:
                if DEBUG_LEVEL >= 2:
                    print(f"TCP Connection received from {client_address}: {counter}")
                    logger.info(f"TCP Connection received from {client_address}")

                #Added msg per sec calcuation to be used with caching engine -MyH 4/7/25
                message_count = 0
                start_time = time.time()
                previous_time = start_time
                while True:
                    data = client_socket.recv(RECVBUF).decode('utf-8').strip()
                    if data:
                        message_count += 1
                        mps = calc_msg_per_sec(message_count, previous_time)
                        #print (f"Message per second: {mps:.2f}")
                        #previous_time = time.time( )
                        handle_syslog_message(data, client_address, "TCP", DEBUG_LEVEL, mps)
                    else:
                        break
            except Exception as e:
                print_error_details(e)
                logger.error(f"Error handling client: {e}")
            finally:
                if client_socket:
                    client_socket.close()
                    print(f"TCP Connection closed from {client_address}")
    except Exception as e:
        print_error_details(e)
        logger.info(f"syslog_server_tcp(): An error occurred. Exit:{e}")
    finally:
        if server_socket:
            server_socket.close()
            print("🔴 Server closed.")     
            
#End of syslog_server_tcp()        
#--------------------------------------------------------------
#==============================================================
def start_syslog_server(host=SYSLOG_RECV_HOST, udp_port=SYSLOG_RECV_UDP_PORT, tcp_port=SYSLOG_RECV_TCP_PORT, DEBUG_LEVEL=0):
    """Run both UDP and TCP syslog servers"""
    
    udp_thread = threading.Thread(target=syslog_server_udp, args=(host, udp_port, DEBUG_LEVEL))  
    tcp_thread = threading.Thread(target=syslog_server_tcp, args=(host, tcp_port, DEBUG_LEVEL))

    udp_thread.daemon = True    # Set as daemon thread
    tcp_thread.daemon = True    # Set as daemon thread

    udp_thread.start()          # Start UDP server
    tcp_thread.start()          # Start TCP server

    udp_thread.join()          # Wait for UDP server to finish
    tcp_thread.join()          # Wait for TCP server to finish
#End of start_syslog_server()    
#==========================================================