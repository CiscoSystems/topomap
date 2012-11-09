# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2011 Cisco Systems Inc. LLC.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
#
#    Author: Arvind Somya (asomya@cisco.com)
#
import logging

import copy
import time
import netifaces
import os
import re
import subprocess
import socket
import sys

from socket import gethostname

from db.topomap_db import TopomapDB as db


def _import_module(mod_str):
    (path, sep, name) = mod_str.rpartition('.')
    try:
        __import__(path)
        plugin_class = getattr(sys.modules[path], name)
        return plugin_class
    except Exception, e:
        raise Exception("Plugin %s could not be loaded: %s" % \
                        (mod_str, e))


class Topodict(object):
    def __init__(self, *args, **kwargs):
        self.topodict = {}

    def compare(self, topodict):
        logging.debug("Comparing topology")
        # Compare old and new topologies
        if sorted(topodict) == sorted(self.topodict):
            logging.debug("Topology unchanged")
            return False
        else:
            # Update local topology
            self.topodict = copy.deepcopy(topodict)
            logging.debug("New Topology %s" % self.topodict)
            return True

class Topomap(object):
    def __init__(self, conf, **kwargs):
        self.conf = conf
        self.topodict = Topodict()
        self.providers = self.conf['AGENT']['providers']
        self.interfaces = self.conf['AGENT']['int_prefixes']
        self.db = db(self.conf['DATABASE'])

        loglevel = logging.WARNING
        if self.conf['LOG']['level']:
            if self.conf['LOG']['level'] == 'debug':
                loglevel = logging.DEBUG
            elif self.conf['LOG']['level'] == 'info':
                loglevel = logging.INFO

        logging.basicConfig(
            filename=self.conf['LOG']['file'],
            format='%(asctime)s %(process)d %(levelname)s %(message)s',
            level=loglevel)

        self.int_checks = []
        # Precompile all regexes for interface checks
        for interface in self.interfaces:
            pattern = re.compile(interface)
            self.int_checks.append(pattern)
        
        logging.info("Loaded interface checks")
        self.plugins = []
        # Import all provider plugins
        for provider in self.providers:
            plugin = _import_module(provider)
            self.plugins.append(plugin)
            logging.info("Loaded plugin %s" % provider)

    def reload_conf(self):
        pass

    def cleanup(self):
        pass

    def get_all_interfaces(self):
        return netifaces.interfaces()
    
    def check_interface(self, interface):
        # Run regex again interface name
        for check in self.int_checks:
            if check.match(interface, 0):
                return True
        return False

    def get_provider_neighbors(self):
        # Gather topology from all providers
        # TODO(asomya): Combine return from multiple
        # providers. Need a conflict resolution 
        # algorithm
        all_interfaces = self.get_all_interfaces()
        topodict = {}
        for interface in all_interfaces:
            if self.check_interface(interface):
                for plugin in self.plugins:
                    logging.debug("Getting interface %s neighbors" % interface)
                    cl = plugin(interface)
                    op = cl.get_neighbors()
                    if op:
                        topodict[interface] = op

        # Check topodict for changes
        if self.topodict.compare(topodict):
            logging.debug("Topology Changed")
            self.update_db()

    def scan(self):
        # Main process loop
        while True:
            logging.info("Scanning")
            self.get_provider_neighbors()
            time.sleep(int(self.conf['AGENT']['polling_interval']))

    def update_db(self):
        # Create a single session for all transactions
        self.db._get_session()

        topodict = self.topodict.topodict
        # Get local hostname 
        hostname = gethostname()
        # Delete all existing connections for this host
        self.db.delete_all_device_connections(hostname)

        # Check if this host exists in the DB
        dev = self.db.get_device(hostname)
        if not dev:
            logging.debug("Creating device")
            # Get server details
            ip = socket.gethostbyname(hostname)
            uname = os.uname()
            type = uname[0]
            software = ' '.join(uname[2:])
            # Create a new device in the DB
            dev = self.db.create_device(hostname, ip, type, software)

        # Loop over interfaces
        for interface in topodict.keys():
            # Check if this device/port combination exists
            dport = self.db.get_device_port(dev.id, interface)
            if not dport:
                # Create a row in the Db for this host/port combo
                logging.debug("Creating device port")
                dport = self.db.create_device_port(dev.id, interface)
             
            # Check the device for the other end of this connection
            dev_id = topodict[interface]['device_id']
            edev = self.db.get_device(dev_id)

            if not edev:
                logging.debug("Creating end device")
                # Create this device
                dev_ip = topodict[interface]['device_ip']
                type = None
                software = topodict[interface]['device_desc']
                edev = self.db.create_device(dev_id, dev_ip, type, software)

            # Check the end device port row
            pid =  topodict[interface]['port_id']
            eport = self.db.get_device_port(edev.id, pid)
            
            if not eport:
                # Create this port
                eport = self.db.create_device_port(edev.id, pid)

            # Create connection row
            logging.debug("Creating connection")
            self.db.create_device_connection(dport.id, eport.id)

        # Delete the active session
        self.db._destroy_session()
