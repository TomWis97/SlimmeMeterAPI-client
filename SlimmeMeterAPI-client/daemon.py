import configparser
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import urllib.parse
import interpreter
from mysql.connector import connection
from datetime import datetime
import timeit

# Configuration reader
config = configparser.ConfigParser()
config.read('config.ini')
httpPort = int(config['client']['port'])
historyItems = [i.strip() for i in config['client']['historyItems'].split(',')]
hourlyHistoryItems = [
    i.strip() for i in config['client']['hourlyHistoryItems'].split(',')]
# Configuration reading done.

# Initiate MySQL connection.
cnx = connection.MySQLConnection(
    user=config['client']['dbUser'],
    password=config['client']['dbPassword'],
    host=config['client']['dbHost'],
    database=config['client']['dbdatabase']
)
cursor = cnx.cursor()


def dbGetLast24Hour(name):
    """Gets data from the last 24 hours from a given name."""
    query = ('SELECT * FROM history WHERE timestamp > DATE_SUB(CURDATE(), '
             'INTERVAL 1 DAY) AND name = %s')
    cursor.execute(query, (name,))


def dbGetLastMonth(name):
    """Gets data from the last 30 days from a given name."""
    query = ('SELECT * FROM history WHERE name = %s AND timestamp > DATE_SUB('
             'CURDATE(), INTERVAL 30 DAY) GROUP BY DATE(timestamp)')
    cursor.execute(query, (name,))
    result = cursor.fetchall()
    return result


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
        if historyItem['name'] in hourlyHistoryItems:
            # Checking if last information in database is the same as
            # current information.
            query = 'SELECT MAX(timestamp) FROM history WHERE name = %s'
            cursor.execute(query, (historyItem['name'],))
            result = cursor.fetchone()
            if (result[0] == None):
                query = ("INSERT INTO history ( timestamp, name, value )"
                         "VALUES ( %s, %s, %s )")
                cursor.execute(query, (historyItem['timestamp'],
                               historyItem['name'],  historyItem['value']))
            else:
                # This doesn't preserve seconds. But that shouldn't matter
                # because these values should only refresh once per hour.
                lastInDb = result[0].strftime('%Y-%m-%d %H:%M:%S')
                if lastInDb < historyItem['timestamp']:
                    print("Writing to DB!")
                    query = ("INSERT INTO history ( timestamp, name, value )"
                             "VALUES ( %s, %s, %s )")
                    cursor.execute(query, (historyItem['timestamp'],
                                   historyItem['name'],  historyItem['value']))
        else:
            query = ("INSERT INTO history ( timestamp, name, value )"
                     "VALUES ( %s, %s, %s )")
            cursor.execute(query, (timestamp, historyItem['name'],
                           historyItem['value']))
    cnx.commit()


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
