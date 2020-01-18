import struct
from twisted.internet.protocol import DatagramProtocol


class VitaProtocol(DatagramProtocol):
    __header_format = '!BBHIQIQ'
    __header_size = struct.calcsize(__header_format)

    def __init__(self, host, port):
        self.host = host
        self.port = port

    def startProtocol(self):
        self.transport.connect(self.host, self.port)

    def parse_vita_header(self, packet):
        (packet_type, time_stamp_type, length, stream_id, class_id, time_stamp_int, time_stamp_frac) = \
            struct.unpack(self.__header_format, packet[0:self.__header_size])

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

    def parse_meter_data(self, packet):
        meter_data = dict()

        for (meterId, meter_value) in struct.iter_unpack('!hh', packet[self.__header_size:]):
            meter_value = meter_value / (1 << 6)
            meter_data[meterId] = meter_value
            print("ID: {}, Value: {}".format(meterId, meter_value))

        return meter_data

    def received_unknown_packet(self):
        pass

    def received_meters(self, meter_data):
        for (meterId, meterValue) in meter_data.items():
            print("Id: {}, Value: {}".format(meterId, meterValue))

    def datagramReceived(self, datagram, addr):
        header = self.parse_vita_header(datagram)

        if header['classId'] >> 32 != 0x00001c2d:
            print("This is not a flex packet, ignoring")
            return

        if header['classId'] == 0x00001c2d534c8002 and header['streamId'] == 0x00000700:
            self.received_meters(self.parse_meter_data(datagram))
        else:
            self.received_unknown_packet()
