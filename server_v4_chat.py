from http.server import BaseHTTPRequestHandler, HTTPServer
import urllib #Only for parse.unquote and parse.unquote_plus.
import json
import base64
import re
# If you need to add anything above here you should check with course staff first.

chats=[]
id = 0


"""
Server documentation
4 valid requests, all others 404. All requests ignore query parameters (for simplicity, we could actually be more efficient if we didn't ignore...)
* POST /api/chats (post a new message, body must be json object with "message" and "color" properties
* DELETE /api/chats (delete an existing message, body must be json object with "id" property)
* GET /api/chats (get all chat messages, return value is json list of objects.)
* GET / returns an html file.
"""

def server(method, url, body, headers):    
    global id
    # Parse URL -- this is probably the best way to do it. Delete if you want.
    parameters = None
    if "?" in url:
        url, parameters = url.split("?", 1)

    if method == "POST" and url == "/api/chats":
        if not headers.get("Content-Type") == "application/json":
            return 'body not json', 400, {"Content-Type":"text/plain"}
        else:
            try:
                body = json.loads(body)
                if "message" not in body and "color" not in body:
                    return 'message and color properties are required', 400, {"Content-Type":"text/plain"}
                else:
                    chats.append({"id": id, "message":body["message"], "color":body["color"]})
                    id = id + 1
                    return "ok", 200, {"Content-Type":"text/plain"}
            except:
                return 'body not json', 400, {"Content-Type":"text/plain"}
    elif method == "DELETE" and url == "/api/chats":
        if not headers.get("Content-Type") == "application/json":
            return 'body not json', 400, {"Content-Type":"text/plain"}
        else:
            try:
                body = json.loads(body)
                if "id" not in body:
                    return 'id property is required', 400, {"Content-Type":"text/plain"}
                else:
                    for chat in chats:
                        if chat["id"] == body["id"]:
                            chats.remove(chat)
                            break
                return 'ok', 200, {"Content-Type":"text/plain"}
            except:
                return 'body not json', 400, {"Content-Type":"text/plain"}
    elif method == "GET" and url == "/api/chats":
        
        return json.dumps(chats), 200, {"Content-Type":"application/json"}
    elif method == "GET" and url=="/":
        return open("chatroom.html").read(), 200, {"Content-Type":"text/html"}
    else:
        return "404 not found", 404, {"Content-Type": "text/plain"}





# You shouldn't need to change content below this. It would be best if you just left it alone.


class RequestHandler(BaseHTTPRequestHandler):
    def c_read_body(self):
        # Read the content-length header sent by the BROWSER
        content_length = int(self.headers.get("Content-Length", 0))
        # read the data being uploaded by the BROWSER
        body = self.rfile.read(content_length)
        # we're making some assumptions here -- but decode to a string.
        body = str(body, encoding="utf-8")
        return body

    def c_send_response(self, message, response_code, headers):
        # Convert the return value into a byte string for network transmission
        if type(message) == str:
            message = bytes(message, "utf8")
        
        # Send the first line of response.
        self.protocol_version = "HTTP/1.1"
        self.send_response(response_code)
        
        # Send headers (plus a few we'll handle for you)
        for key, value in headers.items():
            self.send_header(key, value)
        self.send_header("Content-Length", len(message))
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()

        # Send the file.
        self.wfile.write(message)
        

    def do_POST(self):
        # Step 1: read the last bit of the request
        try:
            body = self.c_read_body()
        except Exception as error:
            # Can't read it -- that's the client's fault 400
            self.c_send_response("Couldn't read body as text", 400, {'Content-Type':"text/plain"})
            raise
                
        try:
            # Step 2: handle it.
            message, response_code, headers = server("POST", self.path, body, self.headers)
            # Step 3: send the response
            self.c_send_response(message, response_code, headers)
        except Exception as error:
            # If your code crashes -- that's our fault 500
            self.c_send_response("The server function crashed.", 500, {'Content-Type':"text/plain"})
            raise
        

    def do_GET(self):
        try:
            # Step 1: handle it.
            message, response_code, headers = server("GET", self.path, None, self.headers)
            # Step 3: send the response
            self.c_send_response(message, response_code, headers)
        except Exception as error:
            # If your code crashes -- that's our fault 500
            self.c_send_response("The server function crashed.", 500, {'Content-Type':"text/plain"})
            raise


    def do_DELETE(self):
        # Step 1: read the last bit of the request
        try:
            body = self.c_read_body()
        except Exception as error:
            # Can't read it -- that's the client's fault 400
            self.c_send_response("Couldn't read body as text", 400, {'Content-Type':"text/plain"})
            raise
        
        try:
            # Step 2: handle it.
            message, response_code, headers = server("DELETE", self.path, body, self.headers)
            # Step 3: send the response
            self.c_send_response(message, response_code, headers)
        except Exception as error:
            # If your code crashes -- that's our fault 500
            self.c_send_response("The server function crashed.", 500, {'Content-Type':"text/plain"})
            raise



def run():
    PORT = 80
    print(f"Starting server http://localhost:{PORT}/")
    server = ("", PORT)
    httpd = HTTPServer(server, RequestHandler)
    httpd.serve_forever()


run()
