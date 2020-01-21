import struct
from twisted.internet.protocol import DatagramProtocol
from ssdrapiclient import SsdrApiProtocol


class VitaProtocol(DatagramProtocol):
    __header_format = '!BBHIQIQ'
    __header_size = struct.calcsize(__header_format)

    def __init__(self, host: int, port: int, api: SsdrApiProtocol) -> None:
        self.host = host
        self.port = port
        self.api = api

    def startProtocol(self):
        self.transport.connect(self.host, self.port)

    @classmethod
    def parse_vita_header(cls, packet):
        (packet_type, time_stamp_type, length, stream_id, class_id, time_stamp_int, time_stamp_frac) = \
            struct.unpack(cls.__header_format, packet[0:cls.__header_size])

        header = {
            'packetType': packet_type,
            'timestampType': time_stamp_type,
            'length': length,
            'streamId': stream_id,
            'classId': class_id,
            'timeStampInt': time_stamp_int,
            'timeStampFrac': time_stamp_frac,
        }

        return header

    @classmethod
    def parse_vita_payload(cls, packet):
        return packet[cls.__header_size:]

    def parse_meter_data(self, packet):
        meter_data = dict()

        for (meterId, meter_value) in struct.iter_unpack('!hh', packet[self.__header_size:]):
            meter_data[meterId] = meter_value
        return meter_data

    def received_unknown_packet(self):
        pass

    def received_meters(self, meter_data):
        for (meter_id, meter_value) in meter_data.items():
            self.api.update_meter(meter_id, meter_value)
        self.api.frame.Layout()

    def datagramReceived(self, datagram, addr):
        header = self.parse_vita_header(datagram)

        if header['classId'] >> 32 != 0x00001c2d:
            print("This is not a flex packet, ignoring")
            return

        if header['classId'] == 0x00001c2d534c8002 and header['streamId'] == 0x00000700:
            self.received_meters(self.parse_meter_data(datagram))
        else:
            self.received_unknown_packet()
