*************************
HAProxy stats to InfluxDB
*************************


Usage
-----

haps2infl.py -s haproxy_host:port/stats_path -i influx_host[:port] -u influx_user -p influx_pass -d influx_database

Args:

- -h, --help - show help 
- -s, --stats_url - HAProxy's full stats without http:// prefix. No auth support for the moment
- -i, --influx_url - InfluxDB database host and optionally port
- -u, --user - InfluxDB user
- -p, --password - InfluxDB password
- -d, --database - InfluxDB database name


Sample:

.. code-block:: bash

    haps2infl.py -s haproxy_host_1:8888/haproxy?stats -i influx_db_host:8086 -u root -p root -d haproxy

The HAProxy stats url, InfluxDB server, and InfluxDB database name are mandatory!
Invoke the script fron crontab at the desired intervals.


Sample graph query
------------------

Get the backends current sessions for the specified proxy entry (backend name) for the haproxy_host_1.


Query:

.. code-block:: sql

    select scur from haproxy_host where pxname = 'proxy-name' and svname = 'BACKEND' and time > now() -  8h group by time(5m);



Results 


.. image:: https://github.com/mihait/misc-stuff/raw/master/influxdb-misc-stats/misc/stats_example.jpg


