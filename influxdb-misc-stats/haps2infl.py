#!/usr/bin/env python
# encoding: utf-8
"""
haps2infl.py

Haproxy to Influxdb stats

Created by Mihai Tianu on 2014-06-26.
Copyright (c) 2014 SellerEngine. All rights reserved.
"""

import getopt
import sys
import csv
import re
import json
import requests


help_message = '''
Usage: 
haps2infl.py -s haproxy_host:port/stats_path -i influx_host[:port] \
-u influx_user -p influx_pass -d influx_database

Sample:
haps2infl.py -s 172.0.0.1:8888/haproxy?stats -i 172.0.0.2:8086 \
-u root -p root -d haproxy
'''

class HAPStats():
    def __init__(self, url, db_host, db_port, db_user, db_passwd, db_name):
        self.url = url
        self.host = db_host
        self.port = db_port
        self.user = db_user
        self.passwd = db_passwd
        self.db = db_name

    def insert_stats(self):

        try:
            r = requests.get("http://%s;csv" % self.url)
            if r.status_code == 200:
                hastats = [ row for row in csv.reader(r.text.splitlines())]

                columns = [ re.sub('[#\ ]', '', col) for col in hastats[0:1][0] ]
                columns[-1] = 'undefined'

                points = [ [ '0' if val == "" else val for val in row ] for row in hastats[1:] ]
                points = [ [ int(v) if v.isdigit() else v for v in row ] for row in points ]

                data =[
                    {
                        "points": points,
                        "name": str(re.split(':', self.url)[0]),
                        "columns": columns
                    }
                ]
                
                inf_url = "http://{0}:{1}/db/{2}/series?u={3}&p={4}".format(
                        self.host, self.port, self.db, self.user, self.passwd)
                headers = {'content-type': 'application/json'}
                r = requests.post(inf_url, data=json.dumps(data),headers=headers)

                if r.text:
                    raise Exception, "Exception: %s" % r.text

        except Exception,e:
            print e    

class Usage(Exception):
    def __init__(self, msg):
        self.msg = msg

def main(argv):

    stats_url = ''
    db_host = ''
    db_port = 8086
    db_user = 'root'
    db_passwd = 'root'
    db_name = ''
    min_opts = 0

    try:
        try:
            opts, args = getopt.getopt(argv,"h:s:i:u:p:d:", ["stats_url=",
                                                        "influx_url=",
                                                        "user=",
                                                        "password=",
                                                        "database=",
                                                        ])
        except getopt.GetoptError:
            print help_message
            sys.exit(1)

        if not len(opts):
            raise Usage(help_message)

        for opt, arg in opts:
            if opt in ("-h", "--help"):
                raise Usage(help_message)
            if opt in ("-s", "--stats_url"):
                stats_url = arg
                min_opts+=1
            elif opt in ("-i", "--influx_url"):
                if len(re.split(':',arg)) == 2:
                    db_host,db_port = re.split(':',arg)
                else:
                    db_host = arg
                min_opts+=1
            elif opt in ("-u", "--user"):
                db_user = arg
            elif opt in ("-p", "--password"):
                db_passwd = arg
            elif opt in ("-d", "--database"):
                db_name = arg
                min_opts+=1

        if min_opts !=3:
            print "s, i, d args are mandatory"
            print "use --help detailed info"
            sys.exit(1)

        hdl = HAPStats(url=stats_url, 
                        db_host = db_host,
                        db_port = db_port,
                        db_user = db_user,
                        db_passwd = db_passwd,
                        db_name = db_name)
        hdl.insert_stats()

    except Usage, err:
        print >> sys.stderr, sys.argv[0].split("/")[-1] + ": " + str(err.msg)
        print >> sys.stderr, "for help use --help"
        sys.exit(2)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

