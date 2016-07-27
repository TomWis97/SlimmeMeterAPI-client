import configparser
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import urllib.parse
import interpreter
from mysql.connector import connection
from datetime import datetime

# Configuration reader
config = configparser.ConfigParser()
config.read('config.ini')
httpPort = int(config['client']['port'])
historyItems = config['client']['historyItems'].split(',')
# Configuration reading done.

# Initiate MySQL connection.
cnx = connection.MySQLConnection(
    user = config['client']['dbUser'],
    password = config['client']['dbPassword'],
    host = config['client']['dbHost'],
    database = config['client']['dbdatabase']
)
cursor = cnx.cursor()

def processData(input):
    timestamp = ''
    historyToSave = []
    for item in input:
        if item['name'] == 'timestamp':
            timestamp = interpreter.converttimestamp(item['value'][0])
        if item['name'] in historyItems:
            # Interpreting each item  
            historyToSave.append(interpreter.interpretValue(item['name'], item['value']))
    for historyItem in historyToSave:
        # TODO: Instead of lastreading, look at configuration file.
        if historyItem['name'][1:] == 'lastReading':
            # Checking if last information in database is the same as current information.
            query = 'SELECT MAX(timestamp) FROM history WHERE name = %s'
            cursor.execute(query, (historyItem['name'],))
            result = cursor.fetchone()
            if (result[0] == None):
                query = "INSERT INTO history ( timestamp, name, value ) VALUES ( %s, %s, %s )"
                cursor.execute(query, (historyItem['timestamp'], historyItem['name'],  historyItem['value']))
            else:
                # This doesn't preserve seconds. But that shouldn't matter because these values
                # should only refresh once per hour.
                lastInDb = result[0].strftime('%Y-%m-%d %H:%M:%S')
                if lastInDb > interpreter.converttimestamp(historyItem['timestamp']):
                    print("Writing to DB!", datetime.datetime())
                    query = "INSERT INTO history ( timestamp, name, value ) VALUES ( %s, %s, %s )"
                    cursor.execute(query, (historyItem['timestamp'], historyItem['name'],  historyItem['value']))
        else:
            query = "INSERT INTO history ( timestamp, name, value ) VALUES ( %s, %s, %s )"
            cursor.execute(query, (timestamp, historyItem['name'],  historyItem['value']))
    cnx.commit()

class webserverHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        # TODO: Fix this MASSIVE security hole. Do as I say, not as I do.
        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        self.wfile.write(bytes('jeej', 'ASCII'))
        length = self.headers['content-length']
        data = self.rfile.read(int(length))
        datastring = data.decode('UTF-8')
        #print("datastring", datastring)
        inputJson = json.loads(data.decode('UTF-8'))
        processData(inputJson)

myServer = HTTPServer(('', httpPort), webserverHandler)
myServer.serve_forever()
