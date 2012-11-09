# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2010 United States Government as represented by the
# Administrator of the National Aeronautics and Space Administration.
# Copyright 2011 OpenStack LLC.
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
from xml.dom.minidom import parseString
from subprocess import Popen, PIPE, STDOUT

class LLDP(object):
    def __init__(self, interface, **kwargs):
        self.interface = interface

    def get_neighbors(self):
        cmd = 'lldpctl ' + self.interface + ' -f xml'
        p = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
        output = p.stdout.read()
        parsed = parseString(output)
        port = parsed.getElementsByTagName("port")
        chassis = parsed.getElementsByTagName("chassis")

        if len(port) > 0:
            pid = port[0].getElementsByTagName("id")[0].childNodes[0].data
            pdesc = port[0].getElementsByTagName("descr")[0].childNodes[0].data
            sid = chassis[0].getElementsByTagName("name")[0].childNodes[0].data
            sip = chassis[0].getElementsByTagName("mgmt-ip")[0].childNodes[0].data
            sdesc = chassis[0].getElementsByTagName("descr")[0].childNodes[0].data

            return {
                "port_id": pid,
                "port_desc": pdesc,
                "device_id": sid,
                "device_ip": sip,
                "device_desc": sdesc
            }

        return False
