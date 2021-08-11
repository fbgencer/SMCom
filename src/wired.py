import SMCom
import serial
import threading
import time

BAUD_RATE = 115200
# from_two_bytes = lambda byte1, byte2 : (byte1 | (byte2 << 8))
# to_two_bytes = lambda int1 : ((int1 & 0xFF), ((int1 >> 8) & 0xFF))

class Wired(SMCom.SMCOM_PUBLIC):
    def __init__(self, rx_buffer_size, tx_buffer_size, device_id):
        super().__init__(rx_buffer_size, tx_buffer_size, device_id)
        self.ser = serial.Serial('/dev/ttyUSB0', BAUD_RATE)
        self.compacket = SMCom.pySMCOM_PUBLIC() 

    def __write__(self, buffer, length):
        if buffer == None or buffer == [] or buffer == "" or buffer == b'':
            return SMCom.SMCOM_STATUS_FAIL
        elif type(buffer) == str:
            buffer = bytes(buffer, "utf-8")
        elif type(buffer) == int:
            buffer = bytes([buffer])
        elif type(buffer) == list or type(buffer) == tuple:
            if type(buffer[0]) == int:
                buffer = bytes(buffer)
            elif type(buffer[0]) == str:
                buffer = bytes("".join(buffer), "utf-8")
        self.ser.write(buffer)
        return SMCom.SMCOM_STATUS_SUCCESS

    def __rx_callback__(self, event, status, packet):
        print("rx callback here")
        self.compacket.data = packet.data
        self.compacket.data_len = packet.data_len

    def __tx_callback__(self, event, status, packet):
        pass
    
    def __available__(self):
        if self.ser.inWaiting() > 0:
            print(self.ser.inWaiting())
        return self.ser.inWaiting()

    def __read__(self, length):
        buffer = []
        pair = SMCom.SMCom_Pair()
        temp = self.ser.read(length)
        for i in temp:
            buffer.append(i)
        print("buffer: ", buffer)
        pair.vec = buffer
        print("pair.vec: ", pair.vec)##    
        pair.status = SMCom.SMCOM_STATUS_SUCCESS
        return pair

    def get_version(self, id):
        # self.write(id, 10, [], 0)
        SMCom_version = self.compacket.data
        # SMCom_version = f"{SMCom_version[6]}.{SMCom_version[5]}.{SMCom_version[4]}"
        return SMCom_version
    
    def get_mac_adress(self, id):
        self.write(id, 11, [0,0,0,0,0], 5)
        data = []
        mac_adress = [0 for i in range(6)]
        self.__read__(data, 9)
        for i in range(4, len(data)-6):
            mac_adress[i-4] = hex(data[i])
            temp = mac_adress[i-4][2:]
            mac_adress[i-4] = temp.upper() if len(temp) != 1 else "0"+temp
        mac_adress = ":".join(mac_adress)
        return mac_adress
    
    def thread_func(self):
        while True:
            #print("sjjsjsjs")
            if(self.ser.inWaiting()):
                print(self.ser.inWaiting())
            self.listener()
            #time.sleep(0.1)

    MESSAGES_SENSEWAY_WIRED = \
    [
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
        ("GET_VERSION",                     get_version),
        ("AUTO_ADDRESSING_INIT",            0),
        ("AUTO_ADDRESSING_SET_NEW_ID",      0),
        ("START_BATCH_MEASUREMENT",         0),
        ("GET_BATCH_MEASUREMENT",           0),
        ("GET_CLEARANCE",                   0),
        ("GET_CREST",                       0),
        ("GET_GRMS",                        0),
        ("GET_KURTOSIS",                    0),
        ("GET_SKEWNESS",                    0),
        ("GET_BATCH_MEASUREMENT_CHUNK",     0),
        ("AUTO_ADDRESSING_INTEGRITY_CHECK", 0),
        ("GET_ALL_TELEMETRY",               0),
        ("GET_VRMS",                        0),
        ("GET_PEAK",                        0),
        ("GET_SUM",                         0)
    ]

    def __del__(self):
        self.ser.close()

nodeA = Wired(1024, 1024, 13)
t = threading.Thread(target=nodeA.thread_func, daemon=True)
t.start()

time.sleep(2)
nodeA.write(255, 10, [], 0)
time.sleep(2)
#temp = nodeA.get_version(255)
#print("x: ", temp)
t.join()
print("...")