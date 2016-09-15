#endcoding: utf-8

import os
import time

# Gemma Marcinkoski 1412798
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

HTTP_RESPONSES = {200: "OK", 302:"Found", 404: "Not Found", 501: "Not Implemented"}

TYPES = {"html" : "text/hmtl", "css" : "text/css", "jpg" : "image/jpg"}


class HTTPResponse:
    #for request parsing
    def __init__(self, file_path, http_request):
        #storing field for each response
        self.HTTP_method = http_request.HTTP_method
        self.HTTP_path = http_request.HTTP_path
        self.HTTP_type = http_request.HTTP_type
        #for total file path
        self.full_file_path = http_request.full_file_path
        self.response = http_request.response
        
    def ResponseCheck(self, file_path):
        #case to handle security test
        if self.response == 404:
            return 404
        
        if self.HTTP_method != "GET":
            self.response = 404
            return self.response
        
        if self.HTTP_type != "HTTP/1.1":
            self.response = 404
            return self.response
        
        if self.HTTP_path == None: 
            self.response = 404
            return self.response
        
        #for invalid paths
        if not os.path.exists(self.full_file_path):
            return 404
        
        #for deep case with redirect
        if os.path.isdir(self.full_file_path):
            return 302
        
        self.response = 200
        return self.response
        
    def MakeResponse(self):
        #initilizing http code for response maker
        response_number = self.ResponseCheck(self.full_file_path)
        
        #if its OK, send page data
        if response_number == 200:
            path_type = self.getType(self.full_file_path)
            header = self.HTTPHeaderMaker(response_number,path_type)
            site_file = open(self.full_file_path, "rb")
            site_body = site_file.read()
            return header + "\r\n" + site_body + "\r\n"
        
        #if its found
        if response_number == 302:
            deep_path = self.full_file_path
            #if no path, add it
            if not self.full_file_path.endswith("/"):
                deep_path = self.full_file_path + "/"
                
            deep_path = deep_path + "index.html"
            path_type = self.getType(deep_path)
            header = self.HTTPHeaderMaker
            
            site_file = open(deep_path, "rb")
            site_body = site_file.read()
            return header + "\r\n" + site_body + "\r\n"
        
        
        #down here if 404 or 501
        path_type = self.getType(self.full_file_path)
        header = self.HTTPHeaderMaker(response_number, path_type)
        
        if response_number == 404:
            return header + "\r\n" + "404: Not Found\r\n"
        
        return header + "\r\n" + "418: i'm a teapot, i haven't handled this case, because it shouldn't happen \r\n"
    
    def getType(self, file_path):
        #getting rightmost part of request
        self.file_type = file_path.split(".")[-1].lower()
        
        if self.file_type in TYPES:
            if self.file_type == "html":
                return TYPES[self.file_type] + "; charset=UTF-8"
            #if its css or jpeg, just link type
            return TYPES[self.file_type]
        
        else:
            #return an html type if not in types list
            print("TYPE NOT COVERED:")
            print(self.file_type)
            return "text/html" + "; charset=UTF-8"
        
    
    def HTTPHeaderMaker(self, response, path_type, redirected_url=None):
        #following traditional header guidelines
        
        if response in HTTP_RESPONSES:
            header = "%s %d %s\r\n" %("HTTP/1.1", response, HTTP_RESPONSES[response])
            
            #deep case
            if response == 302:
                header = "%s %d %s\r\n" %("HTTP/1.1", 200, HTTP_RESPONSES[200])
                
        else:
            #using 501 for cases not covered by HTTP RESPONSES
            print("HTTP_RESPONSES not covered")
            print(response)
            header = "%s %d %s\r\n" %("HTTP/1.1", 501, HTTP_RESPONSES[501])
            
        header += "Connection: close\r\n" + "Server:CMPUT404\r\n" + "Content Type: " + path_type + "\r\n"
        
        return header
        

class HTTPRequest:
    #parsing the server's request into correct http field
    def __init__(self, data, site_root):
        # initializing response number
        self.response = 0
        
        #getting the first line of the request
        try:
            self.HTTP_method, self.HTTP_path, self.HTTP_type = data.splitlines()[0].split()
            
            #get index file if site root is requested
            if self.HTTP_path == "/":
                self.HTTP_path = "/index.html"
                
            #if path is something else, error
            elif "/../" in self.HTTP_path:
                self.response = 404
                
        except IndexError as error:
            #for parsing errors causes 404 error
            self.response = 404
            print(error)
        
        #find full file path
        self.full_file_path = os.path.realpath(site_root + self.HTTP_path)
            