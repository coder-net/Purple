import socket
import enum


class Action(enum.Enum):
    LOGIN = 1
    LOGOUT = 2
    MOVE = 3
    UPGRADE = 4
    TURN = 5
    PLAYER = 6
    GAMES = 7
    MAP = 10

    def __int__(self):
        return self.value

class Result(enum.Enum):
    OKEY = 0
    BAD_COMMAND = 1
    RESOURCE_NOT_FOUND = 2
    ACCESS_DENIED = 3
    INAPPROPRIATE_GAME_STATE = 4
    TIMEOUT = 5
    INTERNAL_SERVER_ERROR = 500

    # def __int__(self):
    #     return self.value

class Connector:
    def __init__(self, SERVER_ADDR="wgforge-srv.wargaming.net", SERVER_PORT=443):
        self.SERVER_ADDR = SERVER_ADDR
        self.SERVER_PORT = SERVER_PORT
        self.socket = socket.socket()
        self.int_size = 4
        self.encoding = "utf-8"

    def connect(self):
        self.socket.connect((self.SERVER_ADDR, self.SERVER_PORT))

    def close(self):
        self.socket.close()

    def receive(self):
        result = Result(__class__.to_int(self.receive_part(self.int_size)))
        data_len = __class__.to_int(self.receive_part(self.int_size))
        data = self.receive_part(data_len).decode(self.encoding)
        return (result, data)

    @staticmethod
    def to_int(sbytem, byteorder="little", signed=False):
        return int.from_bytes(sbytem, byteorder=byteorder, signed=signed)

    @staticmethod
    def from_int(num, length=4, byteorder="little", signed=False):
        return int(num).to_bytes(length, byteorder=byteorder, signed=signed)

    def receive_part(self, msg_length):
        data = []
        while msg_length > 0:
            data.append(self.socket.recv(msg_length))
            msg_length -= len(data[-1])
        return b"".join(data)

    def send(self, action, data=""):
        action_code = __class__.from_int(int(action))
        data_bytes = data.encode(self.encoding)
        length_code = __class__.from_int(len(data_bytes))
        msg = action_code + length_code + data_bytes
        self.socket.send(msg)


def main():
    try:
        import json

        def to_json(obj):
            return json.dumps(obj, separators=(",", ":"))

        cn = Connector()
        cn.connect()

        cn.send(Action.LOGIN, to_json({"name": "Phoebus"}))
        msg = cn.receive()
        print(f"{msg[0]}: ")
        print(msg[1])
        
        cn.send(Action.MAP, to_json({"layer": 0}))
        msg = cn.receive()
        print(f"{msg[0]}: ")
        print(msg[1])

        cn.send(Action.MAP, to_json({"layer": 1}))
        msg = cn.receive()
        print(f"{msg[0]}: ")
        print(msg[1])

        cn.send(Action.MAP, to_json({"layer": 10}))
        msg = cn.receive()
        print(f"{msg[0]}: ")
        print(msg[1])

        cn.send(Action.LOGOUT)
        msg = cn.receive()
        print(f"LOGOUT: {msg}")
    finally:
        cn.close()


if __name__ == "__main__":
    main()
