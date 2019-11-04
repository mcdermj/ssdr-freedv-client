import struct

from twisted.internet.protocol import DatagramProtocol

class VitaProtocol(DatagramProtocol):
    __headerFormat = '!BBHIQIQ'
    __headerSize = struct.calcsize(__headerFormat)

    def __init__(self, host, port):
        self.host = host
        self.port = port

    def startProtocol(self):
        self.transport.connect(self.host, self.port)

    def parseVitaHeader(self, packet):
        (packetType, timeStampType, length, streamId, classId, timeStampInt, timeStampFrac) = struct.unpack(self.__headerFormat, packet[0:self.__headerSize])

        header = {
            'packetType': packetType,
            'timestampType': timeStampType,
            'length': length,
            'streamId': streamId,
            'classId': classId,
            'timeStampInt': timeStampInt,
            'timeStampFrac': timeStampFrac,
        }

        return header

    def parseMeterData(self, packet):
        meterData = dict()

        for (meterId, meterValue) in struct.iter_unpack('!hh', packet[self.__headerSize:]):
            meterValue = meterValue / (1 << 6)
            meterData[meterId] = meterValue
            print("ID: {}, Value: {}".format(meterId, meterValue))

        return meterData

    def receivedUnknownPacket(self):
        pass

    def receivedMeters(self, meterData):
        for (meterId, meterValue) in meterData.items():
            print("Id: {}, Value: {}".format(meterId, meterValue))

    def datagramReceived(self, datagram, addr):
        header = self.parseVitaHeader(datagram)

        if header['classId'] >> 32 != 0x00001c2d:
            print("This is not a flex packet, ignoring")
            return

        if header['classId'] == 0x00001c2d534c8002 and header['streamId'] == 0x00000700:
            self.receivedMeters(self.parseMeterData(datagram))
        else:
            self.receivedUnknownPacket()