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
        self.cursor = cnx.cursor()

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
            lastInDb = result[0].strftime('%Y-%m-%d %H:%M:%S')
            if lastInDb < timestamp:
                print("Writing to DB!")
                self.storeData(timestamp, name, value)


class openTsdbDb:
    def getLast24Hour(self, name):
        pass

    def getLastMonth(self, name):
        pass

    def getLastData(self, name):
        pass

    def storeData(self, timestamp, name, value):
        pass

    def storeHourlyData(self, timestamp, name, value):
        pass
