#Module: caching_engine_module
''''
Utilize a cache that stores data along with the timestamp of when it was last fetched. When you need to retrieve the data, you can 
check if the data is stale based on the timestamp (older than 5 minutes, for example). If it's stale, it will call the module again to 
fetch fresh data; otherwise, it will return the cached data. Required Libraries:  pip install cachetools

How It Works:
CacheEngine Class:
    self.cache(): A dictionary that stores the cached data along with a timestamp.
    self.cache_lifetime(): The time in seconds for which the cache is considered valid (5 minutes by default).
    _is_cache_stale(): Checks if the cached data is older than the defined cache lifetime.
    _update_cache: Updates the cache with new data and the current timestamp.
    get_cached_data(): This function either retrieves the cached data (if valid) or calls the fetch_stream_data_function to fetch fresh data and updates the cache.

Fetching Data:
    fetch_data_from_api(): This function simulates fetching data from an external API. Replace this with your actual API call or data fetching function.

Example Execution:
    On the first call, the cache is empty, so it fetches fresh data and stores it in the cache.
    On subsequent calls within 5 minutes, it returns cached data.
    If 5 minutes have passed, it fetches fresh data again and updates the cache.

Customization:
    Custom Cache Lifetime: You can change the cache_lifetime parameter in CacheEngine to any value you need (in seconds).
    API Call Function: Replace fetch_data_from_api with your actual function for collecting data from syslog, Splunk HEC, or any other source.
'''

import os
import time
import json
from datetime import datetime

from configs.globals_module import CACHEDIR, HIGH_REQ_THRESHOLD, CACHE_LIFETIME

#*********************************************************************************
# CacheEngine Class
# This class implements a caching mechanism that can switch between in-memory and file-based caching
# based on the request rate.
# It uses a dictionary to store cached data and a timestamp to determine if the cache is stale.
class CacheEngine:
    #--------------------------------------------------------------
    def __init__(self, cache_lifetime=5*60, high_request_threshold=10, cache_dir="cache"):
        """
        Initializes the caching engine with a specific cache lifetime, request rate threshold,
        and cache directory for file-based caching.
        """
        self.cache = {}                         # In-memory cache,  type of dictionary
        self.cache_lifetime = cache_lifetime  # Cache lifetime in seconds
        self.cache_dir = cache_dir
        self.high_request_threshold = high_request_threshold  # Number of requests per second to trigger file-based cache
        self.last_request_time = time.time()
        self.request_count = 0
        
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)
    #End of __init__()        
    #--------------------------------------------------------------
    #--------------------------------------------------------------
    def _is_cache_stale(self, cache_key):
        """
        Helper method to check if the cached data is stale.
        Returns True if the cache data is stale.
        """
        if cache_key not in self.cache:
            return True
        cache_timestamp = self.cache[cache_key]['timestamp']
        current_time = time.time()
        return current_time - cache_timestamp > self.cache_lifetime
    #End of _is_cache_stale()
    #--------------------------------------------------------------
    #--------------------------------------------------------------
    def _update_cache(self, cache_key, data):
        """
        Updates the cache with new data and the current timestamp.
        """
        self.cache[cache_key] = {
            'data': data,
            'timestamp': time.time()  # Store current timestamp
        }
    #End of _update_cache()    
    #--------------------------------------------------------------
    #--------------------------------------------------------------
    def _is_fast_stream(self,mps):
        """
        Determines if the data stream is too fast based on the request rate.
        """
        current_time = time.time()
        #if (current_time - self.last_request_time) < 0.000001:  # Within 1 second
        #    self.request_count += 1                 #increment if time drift < threashold
        #else: #false
        #    self.last_request_time = current_time   #reset
        #    self.request_count = 1
        #print("MSPS:",mps, "REQ COUNT:",self.request_count, " REQ THREASHOLD:", self.high_request_threshold, \
        #      " CurTime:", current_time, " Self Req Last Time:", self.last_request_time, " Drift:", current_time-self.last_request_time)
        #return self.request_count > self.high_request_threshold     #true if req counter > threashold

        return (mps > self.high_request_threshold)

    #End of _is_fast_stream()
    #--------------------------------------------------------------
    #--------------------------------------------------------------
    def _save_to_file(self, cache_key, data):
        """
        Saves cache data to the file system.
        """
        file_path = os.path.join(self.cache_dir, f"{cache_key}.json")
        with open(file_path, "w") as file:
            json.dump(data, file)
    #End of _save_to_file()       
    #--------------------------------------------------------------
    #--------------------------------------------------------------
    def _load_from_file(self, cache_key):
        """
        Loads cache data from the file system.
        """
        file_path = os.path.join(self.cache_dir, f"{cache_key}.json")
        if os.path.exists(file_path):
            with open(file_path, "r") as file:
                return json.load(file)
        return None
    #end of _load_from_file()
    #--------------------------------------------------------------
    #--------------------------------------------------------------
    def get_cached_data(self, cache_key, fetch_stream_data_function, mps):
        """
        Retrieves data from the cache (in-memory or file-based).
        If stale, calls the provided `fetch_stream_data_function` to fetch fresh data.
        """
    
        # Check if data stream is fast, decide caching strategy
        if self._is_fast_stream(mps):
            print(f"[{mps:.2f}/{self.high_request_threshold}]\033[31mData stream is FAST, switching to file-based cache for:\033[0m [{cache_key}]")
            cached_data = self._load_from_file(cache_key)
            if cached_data and not self._is_cache_stale(cache_key):
                print(f"\033[32mReturning cached data from file for:\033[0m [{cache_key}].")
                from_file_cache = True
                return cached_data, from_file_cache
        else:
            print(f"[{mps:.2f}/{self.high_request_threshold}]\033[32mData stream is SLOW, using in-memory cache for:\033[0m [{cache_key}].")
            if self._is_cache_stale(cache_key):
                print(f"\033[33mCache for {cache_key} is stale. Fetching fresh data directly from the stream...\033[0m")
                fresh_data = fetch_stream_data_function()  # Call the function to fetch new data
                self._update_cache(cache_key, fresh_data)  # Update the cache
                from_file_cache=False
                return fresh_data, from_file_cache
            else:
                print(f"Returning cached data for {cache_key}.")
                from_file_cache=True
                return self.cache[cache_key]['data'], from_file_cache

        # If the cache is stale or not found, fetch new data
        fresh_data = fetch_stream_data_function()
        
        # Save to the appropriate cache depending on stream speed
        if self._is_fast_stream(mps):
            self._save_to_file(cache_key, fresh_data)
        else:
            self._update_cache(cache_key, fresh_data)

        return fresh_data, from_file_cache
    #end of get_cached_data()
    #--------------------------------------------------------------
#End of CacheEngine class()
#**********************************************************************************

#--------------------------------------------------------------
# Example usage with an API fetching function
def fetch_data_from_api2():
    # Simulate fetching data from an API (e.g., syslog, Splunk HEC, etc.)
   #This is where you would implement your actual API call -MyH

    return {"data": "Fresh data from source/API", "timestamp": datetime.now().isoformat()}
#--------------------------------------------------------------

#==========================================================
def use_caching():
    # Create an instance of CacheEngine
    cache_engine = CacheEngine(cache_lifetime=CACHE_LIFETIME, high_request_threshold=HIGH_REQ_THRESHOLD, cache_dir=CACHEDIR)

    cache_key = "api_data"  # Unique key to identify the cached data. Could be syslog, Splunk HEC, etc.

    # Simulate getting cached data or fresh data from the API
    data = cache_engine.get_cached_data(cache_key, fetch_data_from_api2)
    print(f"Fetched Data: {data}")

    # Simulate a second call to see caching behavior
    time.sleep(1)  # Sleep for 1 second
    data = cache_engine.get_cached_data(cache_key, fetch_data_from_api2)
    print(f"Fetched Data: {data}")

    # Simulate a second call after more than 5 minutes to force cache expiry
    time.sleep(300)  # Sleep for 5 minutes
    data = cache_engine.get_cached_data(cache_key, fetch_data_from_api2)
    print(f"Fetched Data: {data}")
#==========================================================    

#if __name__ == "__main__":
#    use_caching()

