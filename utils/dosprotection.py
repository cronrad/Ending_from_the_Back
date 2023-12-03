from utils.database import *
import bson.json_util as json_util
import json
import time

class Protection:
    def __init__(self):
        self.ip_requests = {}
        self.ip_blocked = {}
        self.request_limit = 50
        self.time_period = 10
        self.block_period = 30

    def handle_protection(self, ip_address):
        # Check if ip is blocked already
        if ip_address in self.ip_blocked:
            timer = time.time() - self.ip_blocked[ip_address] < self.block_period
            if timer:
                response_data = "BLOCKED, TOO MANY REQUESTS >:("
                response_json = json.dumps(response_data)
                return response_json, 429

        # Check if this request exceeds the limit, if it does, sent a 429
        if self.check_ip_limit(ip_address):
            self.block_ip(ip_address)
            if ip_address in self.ip_blocked and time.time() - self.ip_blocked[ip_address] >= self.block_period:
                self.unblock_ip(ip_address)
                return None
            # self.unblock_ip(ip_address)
            response_data = "BLOCKED, TOO MANY REQUESTS >:("
            response_json = json.dumps(response_data)
            return response_json, 429
        # print("THIS IS GOOD")
        # print("DICT BEFORE: " + str(self.ip_requests))
        # If else, add the address to the requests
        self.set_ip_timer(ip_address)
        # print("DICT After: " + str(self.ip_requests))
        return None

    def set_ip_timer(self, ip_address):
        if ip_address in self.ip_requests:
            curr_time = time.time()
            elapsed_time = curr_time - self.ip_requests[ip_address]["start_time"]
            if elapsed_time >= self.time_period:
                # Reset Start Time and count
                self.ip_requests[ip_address]["start_time"] = curr_time
                self.ip_requests[ip_address]["count"] = 0
            else:
                self.ip_requests[ip_address]["count"] += 1
        else:
            self.ip_requests[ip_address] = self.ip_requests.get(ip_address, {"count": 0, "start_time": time.time()})

    def check_ip_limit(self, ip_address):
        if ip_address in self.ip_requests:
            elapsed_time = time.time() - self.ip_requests[ip_address]["start_time"]
            # print("checkign elapsed time: " + str(elapsed_time))
            if elapsed_time < self.time_period:
                # print("@@ ELAPSED TIME < TIME PERIOD @@")
                # print("IP requests count: " + str(self.ip_requests[ip_address]["count"]))
                # print("request limit: " + str(self.request_limit))
                if self.ip_requests[ip_address]["count"] > self.request_limit:
                    # print("@@ BLOCKED TOO MANY REQUESTS @@")
                    return True
        return False

    def block_ip(self, ip_address):
        # respond with a ip limit 429 Too Many Requests for 30 seconds
        # adds ip to blocked dictionary with the time
        self.ip_blocked[ip_address] = time.time()
        self.ip_requests[ip_address]["count"] += 1

    def unblock_ip(self, ip_address):
        # check if timer has expired, then unblock
        if ip_address in self.ip_blocked and time.time() - self.ip_blocked[ip_address] >= self.block_period:
            del self.ip_blocked[ip_address]
            self.ip_requests[ip_address]["count"] = 0  # Reset count when IP is unblocked
