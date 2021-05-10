# Python 3 server example
import sqlite3
import os
from http.server import BaseHTTPRequestHandler, HTTPServer
import time
import json

# create a default path to connect to and create (if necessary) a database
# called 'database.sqlite3' in the same directory as this script
DEFAULT_PATH = os.path.join(os.path.dirname(__file__), 'database.sqlite3')

def db_connect(db_path=DEFAULT_PATH):
    con = sqlite3.connect(db_path)
    return con

con  = db_connect()
cur = con.cursor()

cur.execute("SELECT id, name, calories FROM food")
results = cur.fetchall()
for row in results:
    print(row)

hostName = "localhost"
serverPort = 8080

class MyServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(bytes(json.dumps({'hämtat':results}), "utf-8"))
if __name__ == "__main__":        
    webServer = HTTPServer((hostName, serverPort), MyServer)
    print("Server started http://%s:%s" % (hostName, serverPort))

    try:
        webServer.serve_forever()

    except KeyboardInterrupt:
        pass

    webServer.server_close()
    print("Server stopped.")
