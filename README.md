=======
Topomap (Topology Discovery Agent)
=======

Cisco topology discovery agent

Overview
========
This is a topology discovery agent that will atempt to record physical connections between servers and network hardware. At present it is limited to a single hop layer 2 adjacency to the servers it runs on.

Architecture
============
The topology discovery agent runs on Linux servers, for package and library requirements please refer to the dependencies section. The agent periodically scans connections to the local machine using the providers specified in the config file (currently only a single lldp provider). 

The information returned from the providers is collated into a local topology map. The agent maintains a memory based local topolgy map all times, on subsequent iterations the agent will compare the new topology map against the in memory map and only commit changes if it finds changes between the two, this helps minimize database interactions.

Configuration
=============
The configuration file is located in etc/topomap.ini. The following options are supported:

    [AGENT]
    # Polling interval in seconds
    polling_interval = 10
    # Specify interface prefixes to search on
    int_prefixes = eth,en
    # Specify providers
    providers = topomap.providers.lldp.LLDP,
    # Specify location of the pid file
    pidfile = /var/run/topomap.pid
    # Specify run directory
    rundir = /opt/stack/topomap

    [DATABASE]
    # Specify DB connection string
    sql_connection = mysql://root:nova@localhost/topomap?charset=utf8

    [LOG]
    # Log level Default: WARNING
    level = debug
    # Log file
    file = /var/log/topomap.log

Running the agent
=================
To run the agent run bin/topomap. Use bin/topomap -h to find out the various options supported by the agent. The agent can run in blocking agent mode or a background daemon mode. To use the daemon mode specify the -d options when starting the agent.
