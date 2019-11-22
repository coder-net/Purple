import socket
import enum
import json
from os import strerror


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

class Connector:
    int_size = 4
    encoding = "utf-8"

    def __init__(self, SERVER_ADDR="wgforge-srv.wargaming.net", SERVER_PORT=443):
        self.SERVER_ADDR = SERVER_ADDR
        self.SERVER_PORT = SERVER_PORT
        self.socket = socket.socket()

    # TODO, EISCONN handling
    def connect(self):
        code = self.socket.connect_ex((self.SERVER_ADDR, self.SERVER_PORT))
        if code not in (0, socket.errno.EISCONN):
            raise socket.error(code, strerror(code))

    def close(self):
        self.socket.close()

    # TODO, recv ints
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
        data = bytearray(msg_length)
        mem = memoryview(data)
        while msg_length > 0:
            msg_length -= self.socket.recv_into(mem, msg_length)
            mem = mem[-msg_length:]
        return data

    def send(self, action, data=""):
        action_code = __class__.from_int(int(action))
        data_bytes = data.encode(self.encoding)
        length_code = __class__.from_int(len(data_bytes))
        msg = b"".join((action_code, length_code, data_bytes))
        self.socket.sendall(msg)

class RequestHandler:
    dumps_compact = json.JSONEncoder(separators=(",", ":")).encode

    def __init__(self, connector=Connector()):
        self.connector = connector

    def login(self, name, **options):
        self.connector.connect()
        options.update(name=name)
        self.connector.send(Action.LOGIN, self.dumps_compact(options))
        msg = self.connector.receive()
        if msg[0] is not Result.OKEY:
            return msg
        

    def logout(self):
        self.connector.send(Action.LOGOUT)
        msg = self.connector.receive()
        self.connector.close()
        return msg

    def get_point_info(self, idx):
        pass


def connector_demonstration():
    try:
        def to_json(obj):
            return json.dumps(obj, separators=(",", ":"))

        def print_result(action, msg, sep=" "):
            print(f"{action.name} {msg[0].name}:{sep}{msg[1]}")

        cn = Connector()
        cn.connect()

        cn.send(Action.LOGIN, to_json({"name": "Phoebus"}))
        msg = cn.receive()
        print_result(Action.LOGIN, msg, "\n")
        
        cn.send(Action.MAP, to_json({"layer": 0}))
        msg = cn.receive()
        print_result(Action.MAP, msg, "\n")

        cn.send(Action.MAP, to_json({"layer": 1}))
        msg = cn.receive()
        print_result(Action.MAP, msg, "\n")

        cn.send(Action.MAP, to_json({"layer": 10}))
        msg = cn.receive()
        print_result(Action.MAP, msg, "\n")

        cn.send(Action.LOGOUT)
        msg = cn.receive()
        print_result(Action.LOGOUT, msg)
    finally:
        cn.close()


if __name__ == "__main__":
    connector_demonstration()
