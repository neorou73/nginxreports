class nginxlogs:
    """
    A simple class to process nginx access logs
    A query to rebuild a sqlite table currently generates approximately 25gb of data
    better to query text file and generate data from there on the fly
    based on loglist
    requires pygal python library to generate svg graphs
    """
    def __init__(self):
        self.dbName = 'nginxlogs.db'
        self.loglist = [{ "date": "Dec 29", "file": "access.log" }]

    def createCursor(self):
        import sqlite3
        self.conn = sqlite3.connect(self.dbName)
        self.c = self.conn.cursor()
        #print('connected to database')

    def createTables(self):
        self.createCursor()
        query1 = '''drop table if exists logentry'''
        query2 = '''create table logentry (entry text, timestamp text, requestip text, requesturl text, responsecode text, browser text)'''
        self.c.execute(query1)
        self.c.execute(query2)
        self.conn.commit()
        self.conn.close()
        return "created tables"
    
    def clearTables(self):
        self.createCursor()
        query = '''delete from logentry'''
        self.c.execute(query)
        self.conn.commit()
        self.conn.close()
        print("truncated the logentry table")

    def readLog(self, fileName):
        import re
        cleanedLines = []
        with open(fileName) as readf:
            content = readf.read()
            content = re.split('\n', content)
            for line in content:
                cleanedLines.append([str(line)])
            return cleanedLines

    def populateTables(self, lines, fileName):
        print("working on file %s..." % fileName)
        if len(lines) > 0:
            self.createCursor()
            query = '''insert into logentry (entry) values (?)'''
            self.c.executemany(query, lines)
            self.conn.commit()
            self.conn.close()
            print("populated tables with %d entries" % len(lines))
        else:
            print("skipping as there are 0 entries to be made.")

    def produceBarChart(self, data, chartType):
        """
        data must be a list of dicts, such as
        data = [
          { 'title': 'Fibonacci', 'data': [0,1,1,2,3,5,8,13,21,34,55]},
          { 'title': 'Padovan', 'data': [1, 1, 1, 2, 2, 3, 4, 5, 7, 9, 12]}
        ]
        """
        import pygal
        if chartType == None or chartType.lower() == 'bar':
            "default is a bar chart"
            bar_chart = pygal.Bar()
            for datum in data:
                bar_chart.add(datum['title'], datum['data'])
            bar_chart.render_to_file('bar_chart.svg')
            print("done printing bar chart to svg file")
        else:
            print("sorry that is not yet supported")
        
        


if __name__ == "__main__":
    import re, sys
    allArgs = sys.argv

    nl = nginxlogs()

    if len(allArgs) > 1 and allArgs[1] == 'rebuild-tables':
        nl.createTables()
        print("done")

    # elif len(allArgs) > 1 and allArgs[1] == 'repopulate-tables':
    #    nl.clearTables()
    #    for fname in nl.loglist:
    #        lines = nl.readLog(fname["file"])
    #        nl.populateTables(lines, fname["file"])

    else:
        print("default")
        print("command line run:", str(sys.argv))
        print("you can also run: python nginxlogs.py rebuild-tables")
