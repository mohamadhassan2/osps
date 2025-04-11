# Mohamad Hassan
# 2023-10-01

from datetime import datetime   # Date and time handling
import signal  # Signal handling for graceful shutdown
#import sys     # System library for system-specific parameters and functions
import os      # OS library for operating system dependent functionality
import argparse
from flask import app
from flask import Flask, request, jsonify
from colorama import Back, Style, init, Fore
init(autoreset=True)  # Automatically reset color after each print

#------------------  Importing my modules & Local configs -------------------
DEFAULT_DEBUG_LEVEL = 0
RAW_TCP_RECV_PORT=1614  # Port for raw TCP socket receiver
RAW_TCP_RECV_HOST='0.0.0.0'

from configs.globals_module import OSPS_DEFAULT_LOG_FILE, DEFAULT_DEBUG_LEVEL
from utils.misc_utils_module import setup_logging, signal_handler

from sources.raw_tcp_receiver_server_module import start_raw_tcp_server
from sources.syslog_receiver_server_module import  start_syslog_server
from sources.hec1_module import start_hec1_server
from sources.hec2_wsgi_module  import start_hec2_server
from sources.hec3_splunk_Flask_receiver_module import start_hec3_server as start_hec1_server_flask, start_hec3_server
from sources.rest1_api_collector_module import run_rest1_api_collector
from sources.rest2_hateoas_api_collector_module import run_rest2_hateoas_api_collector
#------------------  Importing my modules & Local configs -------------------



# Configure logging to write to file    
#log_file = "syslog_server.log"
#logging.basicConfig(level=logging.DEBUG_LEVEL,format="%(asctime)s - %(message)s",filename=OSPS_DEFAULT_LOG_FILE,filemode='a')
logger = setup_logging(OSPS_DEFAULT_LOG_FILE)  # Set up logging configuration



#=====================================================================================
if __name__ == "__main__":

    signal.signal(signal.SIGINT, signal_handler)  # Setup signal handling

        #----------------get args from user------------------------
    this_script_name = os.path.basename(__file__)
    parser = argparse.ArgumentParser(prog=this_script_name, \
                                    description='For details on this script see: https://github.com/mohamadhassan2/download-github-security-vulnerabilities-/blob/main/README.md ')
    parser.add_argument("-f", "--log_file", type=str, default=OSPS_DEFAULT_LOG_FILE, \
                        help="The output file name to save the results. [default: csv]", required=False )  
    parser.add_argument('-t', '--type', type=str, \
                        help="Set the type (ie ext) of the output file. If json selected additinal file will be generated.", required=False )      #option that takes a value
    parser.add_argument('-d', '--debug', type=int, default=DEFAULT_DEBUG_LEVEL, \
                        help="Levels [0:none(default) 1:Show connections only 2:Show failed parsing 3:Show raw lines 4:Show json]]", required=False ), \
    parser.add_argument('-R', '--syslog', action='store_true', default=False, \
                        help="Enable syslog reciever mode.", required=False)
    parser.add_argument('-S', '--socket', action='store_true', default=False, \
                        help="Enable raw (TCP) socket reciever mode.", required=False)
    parser.add_argument('-H1', '--hec1', action='store_true', default=False, \
                        help="Enable Splunk HEC server mode.", required=False )
    parser.add_argument('-H2', '--hec2', action='store_true', default=False, \
                        help="Enable Splunk HEC server mode (WSGI).", required=False )
    parser.add_argument('-H3', '--hec3', action='store_true', default=False, \
                        help="Enable Splunk HEC server mode (Flask).", required=False )
    parser.add_argument('-A1', '--rest1', action='store_true', default=False, \
                        help="Enable REST API collector mode.", required=False )
    parser.add_argument('-A2', '--rest2', action='store_true', default=False, \
                        help="Enable REST API2 collector mode (HATEOAS).", required=False )
    
    
    args = parser.parse_args()
    DEBUG_LEVEL= args.debug
    #print(f"  [Type:{args.type}]   [Debug Level:{DEBUG_LEVEL}]  [Enable Syslog:{args.syslog}]")   # type: ignore #debug 

    if args.socket:
        print("\n")
        print (f"🟢{Back.YELLOW+Fore.BLACK}Raw TCP socket server enabled")
        logger.info(f"🟢 Raw TCP socket server enabled")
        start_raw_tcp_server(RAW_TCP_RECV_HOST, RAW_TCP_RECV_PORT, DEBUG_LEVEL)   # From sources/raw_tcp_receiver_server_module.py
    elif args.syslog:
        print("\n")
        print (f"🟢 {Back.YELLOW+Fore.BLACK}Syslog server enabled...")
        logger.info(f"🟢 {Back.YELLOW+Fore.BLACK}Syslog server enabled...")   
        start_syslog_server(DEBUG_LEVEL=args.debug)    # From sources/syslog_receiver_server_module.py
    elif args.hec1:
        print("\n")
        print (f"🟢 {Back.YELLOW+Fore.BLACK}Splunk HEC1 server enabled.")
        logger.info(f"🟢 {Back.YELLOW+Fore.BLACK}Splunk HEC1 server enabled.")
        start_hec1_server(DEBUG_LEVEL=args.debug)     #From sources/hec1_module.py
    elif args.hec2:
        print("\n")
        print (f"🟢 {Back.YELLOW+Fore.BLACK}Splunk HEC2 server enabled (WSGI implementation)")
        logger.info(f"🟢 {Back.YELLOW+Fore.BLACK}Splunk HEC2 server enabled (WSGI implementaion)")
        start_hec2_server(DEBUG_LEVEL=args.debug)     # From sources/hec2_wsgi_module.py
    elif args.hec3:
        print("\n")
        print (f"🟢 {Back.YELLOW+Fore.BLACK}Splunk HEC3 server enabled (Flask)")
        logger.info(f"🟢 {Back.YELLOW+Fore.BLACK}Splunk HEC3 server enabled (Flask)")
        start_hec3_server(DEBUG_LEVEL=args.debug)   # From sources/hec3_splunk_Flask_receiver_module.py
    elif args.rest1:
        print("\n")
        print (f"🟢 {Back.YELLOW+Fore.BLACK}REST API collector enabled")
        logger.info(f"🟢 {Back.YELLOW+Fore.BLACK}REST API collector enabled")
        run_rest1_api_collector(DEBUG_LEVEL=args.debug)      # From sources/rest1_api_collector_module.py
    elif args.rest2:
        print("\n")
        print (f"🟢 {Back.YELLOW+Fore.BLACK}REST2 API collector enabled (HATEOAS)")
        logger.info(f"🟢 {Back.YELLOW+Fore.BLACK}REST2 API collector enabled (HATEOAS)")
        run_rest2_hateoas_api_collector(DEBUG_LEVEL=args.debug)    # From sources/rest2_hateoas_api_collector_module.py
        

    #print("Press Ctrl+C to stop the server")
   
    #logger.info("Syslog server started......"
    
    

    # Note: This script requires root privileges to bind to port 514.
#=======================================================================================