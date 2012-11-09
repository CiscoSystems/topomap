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
from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Device(Base):
    __tablename__ = 'device'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    ip = Column(String(255))
    type = Column(String(255))
    software = Column(String(255))

    def __init__(self, name, ip, type, software):
        self.name = name
        self.ip = ip
        self.type = type
        self.software = software

    def __repr__(self):
        return "<Device('%d', '%s', '%s', '%s', '%s')>" % \
                (self.id, self.name, self.ip, self.type, self.software)


class DevicePort(Base):
    __tablename__ = 'device_port'

    id = Column(Integer, primary_key=True)
    device = Column(Integer, ForeignKey('device.id'))
    port = Column(String(255))

    def __init__(self, device, port):
        self.device = device
        self.port = port

    def __repr__(self):
        return "<DevicePort('%d', '%d', '%s')>" % \
               (self.id, self.device, self.port)

class DeviceConnection(Base):
    __tablename__ = 'device_connection'

    id = Column(Integer, primary_key=True)
    end1 = Column(Integer, ForeignKey('device_port.id'))
    end2 = Column(Integer, ForeignKey('device_port.id'))

    def __init__(self, end1, end2):
        self.end1 = end1
        self.end2 = end2

    def __repr__(self):
        return "<DeviceConnection('%d', '%d')>" % (self.end1, self.end2)
