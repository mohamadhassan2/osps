#Module: globals_module.py

OSPS_DEFAULT_LOG_FILE = "osps.log"  # Default log file name


CACHEDIR = "cache"  # Directory to store cached files
HIGH_REQ_THRESHOLD = 22 # Number of requests per second to trigger file-based cache (stream is too fast)
CACHE_LIFETIME = 5 * 60  # Cache lifetime in seconds (5 minutes)

SYSLOG_RECV_HOST='0.0.0.0'  # Listen on all interfaces
SYSLOG_RECV_TCP_PORT=1514    # TCP port
SYSLOG_RECV_UDP_PORT=1514   # UDP port
SYSLOG_TCP_RECV_BUFF_SIZE=1024



DEFAULT_SYSLOG_FILE = "syslog_server.log"  # Default log file name
DEFAULT_DEBUG_LEVEL = 0   # Default debug level

HEC_RECV_HOST = '0.0.0.0'  # Splunk HEC server host
HEC_RECV_PORT = 8080  # Splunk HEC server port
HEC_RECV_PATH = '/services/collector/event'  # Splunk HEC endpoint path

#GitHub Advisory Database API URL
GITHUB_ADVISORY_URL = "https://api.github.com/advisories"
GITHUB_TOKEN = "ghp_7r2Yv3q4e5b8m2r1z3e6f0X1y6Z1q3x2"  # GitHub token for authentication
# CISA Known Exploited Vulnerabilities (KEV) URL
CISA_KEV_URL = "https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json"
