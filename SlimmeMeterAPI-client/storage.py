import datetime
import requests

class mySqlDb:
    def __init__(self, host, database, user, password):
        # Import MySQL here, so it doesn't fuck shit up when this module is
        # imported and MySQL isn't available.
        from mysql.connector import connection
        self.cnx = connection.MySQLConnection(
            user=user,
            password=password,
            host=host,
            database=database)
        self.cursor = self.cnx.cursor()

    def getLast24Hour(self, name):
        """Gets data from the last 24 hours from a given name."""
        query = ('SELECT * FROM history WHERE timestamp > DATE_SUB(CURDATE(), '
                 'INTERVAL 1 DAY) AND name = %s')
        self.cursor.execute(query, (name,))
        result = self.cursor.fetchall()
        return result

    def getLastMonth(self, name):
        """Gets data from the last 30 days from a given name."""
        query = ('SELECT * FROM history WHERE name = %s AND timestamp > '
                 'DATE_SUB(CURDATE(), INTERVAL 30 DAY) GROUP BY DATE('
                 'timestamp)')
        self.cursor.execute(query, (name,))
        result = self.cursor.fetchall()
        return result

    def getLastData(self, name):
        query = 'SELECT MAX(timestamp) FROM history WHERE name = %s'
        self.cursor.execute(query, (name,))
        result = self.cursor.fetchone()
        return result

    def storeData(self, timestamp, name, value):
        query = ("INSERT INTO history ( timestamp, name, value )"
                 "VALUES ( %s, %s, %s )")
        self.cursor.execute(query, (timestamp, name, value))
        self.cnx.commit()

    def storeHourlyData(self, timestamp, name, value):
        r = self.getLastData(name)
        if r[0] == None:
            # There isn't an item already in the database.
            self.storeData(timestamp, name, value)
        else:
            lastInDb = r[0].strftime('%Y-%m-%d %H:%M:%S')
            if lastInDb < timestamp:
                print("Writing to DB!")
                self.storeData(timestamp, name, value)

    def flushData(self):
        # TODO: Move the self.cnx.commit() to here and check if it doen't break
        pass


class openTsdbDb:
    queue = []
    def __init__(self, host, port, location):
        import json
        import datetime
        self.host = str(host)
        self.port = int(port)
        self.location = str(location)

    def getLast24Hour(self, name):
        pass

    def getLastMonth(self, name):
        pass

    def getLastData(self, name):
        pass

    def storeData(self, timestamp, name, value):
        unixtimestamp = self.convertUnixTimestamp(timestamp)
        dataDict = {
            'metric': name,
            'timestamp': unixtimestamp,
            'value': value,
            'tags': {
                'location': self.location
            }
        }
        self.queue.append(dataDict)

    def flushData(self):
        #print(self.queue)
        url = 'http://' + self.host + ':' + str(self.port) + '/api/put'
        r = requests.post(url, json = self.queue)
        self.queue = []

    def storeHourlyData(self, timestamp, name, value):
        pass

    def convertUnixTimestamp(self, timestamp):
        """Convert an MySQL timestamp (YYYY-MM-DD HH:MM:SS) to epoch."""
        date, time = timestamp.split(' ')
        year, month, day = date.split('-')
        hour, minute, second = time.split(':')
        # Note to self: How to handle timezones?
        year = int(year)
        month = int(month)
        day = int(day)
        hour = int(hour)
        minute = int(minute)
        second = int(second)
        dtobj = datetime.datetime(year, month, day, hour, minute, second)
        return int(dtobj.timestamp())
