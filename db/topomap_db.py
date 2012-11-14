import logging

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, exc, joinedload

from db.models import *

class TopomapDB(object):
    def __init__(self, options):
        self.engine = create_engine(options['sql_connection'])
        self.Session = sessionmaker(bind=self.engine)
        self.active_session = None
        Base.metadata.create_all(self.engine)


    def _get_session(self):
        if not self.active_session:
            self.active_session = self.Session()
        return self.active_session


    def _destroy_session(self):
        if self.active_session:
            self.active_session.close()
            self.active_session = None

    def _add(self, obj):
        session = self._get_session()
        session.add(obj)
        session.commit()
        return obj


    def get_all_devices(self):
        return self._get_session().query(Device).all()


    def get_device(self, device_name):
        device_row = self._get_session().query(Device).\
                     filter(Device.name==device_name).first()

        return device_row


    def create_device(self, device_name, ip, 
                      type="Network Device", software="Unknown"):
        row = Device(device_name, ip, type, software)
        self._add(row)
        return row


    def get_all_device_ports(self, device_id):
        return self._get_session().query(DevicePort).\
               filter(DevicePort.device == device_id)


    def get_device_port(self, device_id, port):
        DevicePort_row = self._get_session().query(DevicePort).\
                         filter(DevicePort.device == device_id).\
                         filter(DevicePort.port == port).first()

        return DevicePort_row


    def create_device_port(self, device, port):
        row = DevicePort(device, port)
        self._add(row)
        return row


    def get_device_connection(self, end1_device, end1_port, 
                              end2_device, end2_port):
        DeviceConnection_row = \
            self._get_session().\
            query(Device, DevicePort, DeviceConnection).\
            filter(Device.id == DevicePort.device).\
            filter(DevicePort.id == DeviceConnection.end1).\
            filter(DevicePort.id == DeviceConnection.end2).\
            filter(Device.name == end1_device).\
            filter(Device.name == end2_device).\
            filter(DevicePort.port == end1_port).\
            filter(DevicePort.port == end2_port).first()

        return DeviceConnection_row


    def create_device_connection(self, end1, end2):
        row = DeviceConnection(end1, end2)
        self._add(row)


    def get_all_device_connections(self, device_name):
        connections = []
        device = self.get_device(device_name)
        if len(device) == 0:
            return []
        device_ports = self.get_all_device_ports(device.id)

        for row in device_ports:
            device_connections = self._get_session().query(DeviceConnection).\
                filter(or_(row.id == DeviceConnection.end1, 
                           row.id == DeviceConnection.end2)).all()
            for conn in device_connections:
                connections.append(conn)
        return connections


    def delete_all_device_connections(self, device_name):
        connections = self.get_all_device_connections(device_name)
        for connection in connections:
            self._get_session().delete(connection)
