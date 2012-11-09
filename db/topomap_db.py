from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, exc, joinedload

from db.models import *

class TopomapDB(object):
    def __init__(self, options):
        self.engine = create_engine(options['sql_connection'])
        self.Session = sessionmaker(bind=self.engine)
        Base.metadata.create_all(self.engine)

    def _get_session(self):
        _session = self.Session()
        return _session


    def _destroy_session(self, session):
        pass

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
            filter(DevicePort.port == end2_port)

        return DeviceConnection_row

    def create_device_connection(self, end1, end2):
        row = DeviceConnection(end1, end2)
        self._add(row)


    def get_all_device_connections(self, device_name):
        device_connections = self._get_session().\
            query(Device, DevicePort, DeviceConnection).\
            filter(Device.id == DevicePort.device).\
            filter(DevicePort.id == DeviceConnection.end1).\
            filter(DevicePort.id == DeviceConnection.end2).\
            filter(Device.name == device_name)

        return device_connections

    def delete_all_device_connections(self, device_name):
        connections = self.get_all_device_connections(device_name)
        for connection in connections:
            self._get_session().delete(connection)
