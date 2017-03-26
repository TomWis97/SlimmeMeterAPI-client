import configparser
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import urllib.parse
import interpreter
from datetime import datetime
import timeit
import storage

# Configuration reader
config = configparser.ConfigParser()
config.read('config.ini')
httpPort = int(config['client']['port'])
historyItems = [i.strip() for i in config['client']['historyItems'].split(',')]
hourlyHistoryItems = [
    i.strip() for i in config['client']['hourlyHistoryItems'].split(',')]
dbType = config['client']['dbType']
# Configuration reading done.

if dbType == 'mysql':
    db = storage.mySqlDb(
        config['client']['dbHost'],
        config['client']['dbDatabase'],
        config['client']['dbUser'],
        config['client']['dbPassword'])
elif dbType == 'opentsdb':
    raise ValueError("OpenTSDB isn't implemented yet.")
else:
    raise ValueError("Not a valid option for database type.")


def processData(input):
    timestamp = ''
    historyToSave = []
    for item in input:
        if item['name'] == 'timestamp':
            timestamp = interpreter.converttimestamp(item['value'][0])
        if item['name'] in historyItems or item['name'] in hourlyHistoryItems:
            # Interpreting each item
            historyToSave.append(interpreter.interpretValue(item['name'],
                                 item['value']))
    for historyItem in historyToSave:
        # TODO: Instead of lastreading, look at configuration file.
        if historyItem['name'] in hourlyHistoryItems:
            db.storeHourlyData(timestamp, historyItem['name'],
                               historyItem['value'])
        else:
            db.storeData(timestamp, historyItem['name'], historyItem['value'])


class webserverHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        # TODO: Fix this MASSIVE security hole. Do as I say, not as I do.
        # To future me: I'm talking about the ability for everyone who has
        # access to the server to send data.
        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        self.wfile.write(bytes('jeej', 'ASCII'))
        length = self.headers['content-length']
        data = self.rfile.read(int(length))
        datastring = data.decode('UTF-8')
        inputJson = json.loads(data.decode('UTF-8'))
        processData(inputJson)

    def do_GET(self):
        if self.path == '/debug':
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write('<h1>Jeej!</h1>'.encode('UTF-8'))


myServer = HTTPServer(('', httpPort), webserverHandler)
myServer.serve_forever()
