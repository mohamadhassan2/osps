#Module: raw_tcp_receiver_module.py
# # This module implements a simple TCP server that listens for incoming connections and prints the received messages to the console.
# # It is designed to be run as a standalone script or integrated into a larger system for receiving and processing log data.
# # It is intended to be used in conjunction with other components, such as a logging framework or data processing pipeline.
# #--------------------------------------------------------------
import time
import traceback
import sys
import socket
import logging
from colorama import Fore, Back, Style, init
# Initialize colorama
init(autoreset=True)  # Automatically reset color after each print

#-----------------------  Importing my modules & local configs -------------------
from utils.misc_utils_module import print_error_details, DLevel
from utils.queues_module import send_to_que, setup_cache_directory
#RAW_TCP_RECV_PORT=1614  # Port for raw TCP socket receiver
#RAW_TCP_RECV_HOST = '0.0.0.0'  # Listen on all interfaces
CACHE_DIR = 'raw_tcp_que'
#-----------------------  Importing my modules & local configs -------------------

#------------------------------- raw tcp listener  -------------
#This code is a simple TCP server that listens for incoming connections and prints the received messages to the console.
 # Create a socket to listen for messages https://realpython.com/python-sockets/
def start_raw_tcp_server(raw_tcp_recv_host, raw_tcp_recv_port, debug_level=0):

    if debug_level != 0:
        print(f"{Fore.YELLOW+Back.LIGHTRED_EX+Style.BRIGHT} **** LEVEL:{debug_level} DEBUG MODE ENABLED **** {Fore.RESET}")

    print(f"{Fore.GREEN}>>Starting raw (TCP) socket server..." )
    logging.info(f"{Fore.GREEN}>>Starting raw (TCP) socket server..." )

    ################Initialize for sending to queue() ###
    cache_dir = CACHE_DIR
    setup_cache_directory(cache_dir,debug_level)  # Ensure the cache directory exists. Delete on startup
    message_count = 0
    last_timestamp = time.time()
    event_cache = []
    #################################

    try:
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)   #Create a TCP socket
        server_address = (raw_tcp_recv_host, raw_tcp_recv_port)  #Bind the socket to the host and port
        server_socket.bind(server_address)  #Bind the socket to the host and port
        server_socket.listen(15)  # Listen to incoming connections. Maximum 5 queued connections
        print(f"Listening on {raw_tcp_recv_host}:{raw_tcp_recv_port}...")

        #------------>Start accept incoming connections loop
        while True: 
            client_socket, client_address = server_socket.accept()   #Accept a connection
            try:
                print(f"Connection from {client_address}")
                setup_cache_directory(cache_dir,debug_level)  # Ensure the cache directory exists. Delete on startup
                message_count = 0
                last_timestamp = time.time()
                event_cache = []
                #----------------------
                while True: #Receive data from the client
                    data = client_socket.recv(1024)   #bufsize argument of 1024 used above is the maximum amount of data to be received at once   
                    if not data:        
                        break
                    if debug_level >= 2:
                        #print(f"D{debug_level}{Back.GREEN+Fore.YELLOW}[{__name__}] {Fore.RESET}1)Received:{Style.RESET_ALL} ->{Fore.LIGHTMAGENTA_EX}{data}<- {Style.RESET_ALL}[len:{len(data)}]")
                        print(f"{DLevel(2)} [Bytes received:{len(data)}] RAW TCP message from {client_address} ")
                    if debug_level >= 3:
                         #if len(data)==0: print ("\n") # Print newline if data is empty
                        print(f"{DLevel(3)}{Fore.LIGHTMAGENTA_EX} DATA:{Fore.YELLOW+Style.BRIGHT}[{Fore.LIGHTBLACK_EX}{data}{Fore.YELLOW+Style.BRIGHT}]{Fore.BLUE}[lenght:{len(data)}]{Fore.RESET} ")
                       #logger.info(f"{DLevel(3)}{Fore.LIGHTMAGENTA_EX} DATA:{Fore.YELLOW+Style.BRIGHT}[{Fore.LIGHTBLACK_EX}{data}{Fore.YELLOW+Style.BRIGHT}]{Fore.BLUE}[lenght:{len(data)}]{Fore.RESET} ")

                    message_count += 1
                    last_timestamp = time.time()
                    send_to_que(data, cache_dir, message_count, last_timestamp, event_cache, debug_level)  
                    
            finally:
                client_socket.close()
    except Exception as e:
        print_error_details(e)
        logging.error(f"Error occurred: {e}")
    finally:
        if 'server_socket' in locals():
            server_socket.close()
            print(f"[{__name__}]:Server closed.")
            #print(f"Server closed.")
        #-------------------> End accept connections while loop
            
    return None        
#End of start_raw_tcp_server
#------------------------------- raw tcp listener  -------------
