import socket
import enum
import json
import os

encode_compact = json.JSONEncoder(separators=(",", ":")).encode


class Action(enum.Enum):
    LOGIN = 1
    LOGOUT = 2
    MOVE = 3
    UPGRADE = 4
    TURN = 5
    PLAYER = 6
    GAMES = 7
    MAP = 10


class Result(enum.Enum):
    OKEY = 0
    BAD_COMMAND = 1
    RESOURCE_NOT_FOUND = 2
    ACCESS_DENIED = 3
    INAPPROPRIATE_GAME_STATE = 4
    TIMEOUT = 5
    INTERNAL_SERVER_ERROR = 500


class GameConnectionError(Exception):
    def __init__(self, code, error):
        self.code = code
        self.error = error
        super().__init__(": ".join((code.name, error)))


class ResponseError(GameConnectionError):
    pass


class Connector:
    int_size = 4
    encoding = "utf-8"

    def __init__(self, address: "(SERVER_ADDRESS, SERVER_PORT)" = None):
        directory = os.path.dirname(os.path.abspath(__file__))
        if address is None:
            with open(os.path.join(directory, "server_config.json")) as json_data:
                server_config = json.load(json_data)
                address = server_config["SERVER_ADDRESS"], server_config["SERVER_PORT"]
        self.SERVER_ADDR = address[0]
        self.SERVER_PORT = address[1]
        self.socket = None

    def __bool__(self):
        return self.socket is not None

    def connect(self):
        if not self:
            self.socket = socket.socket()
            self.socket.connect((self.SERVER_ADDR, self.SERVER_PORT))

    def close(self):
        if self:
            self.socket.close()
            self.socket = None

    def request(self, action, data=None):
        """
        Sends request to the server and gets and return response.

        Parameters:
            action: Action instance
            data: request data object
        Returns:
            response data object
        Raises:
            ResponseError: if request not valid
        """
        if data is not None:
            self.send(action, data)
        else:
            self.send(action)

        msg = self.receive()
        if msg[0] is not Result.OKEY:
            raise ResponseError(msg[0], json.loads(msg[1])["error"])
        response = json.loads(msg[1] or "null")
        return response

    # TODO, recv ints
    def receive(self):
        result = Result(__class__.to_int(self.receive_by_parts(self.int_size)))
        data_len = __class__.to_int(self.receive_by_parts(self.int_size))
        data = self.receive_by_parts(data_len).decode(self.encoding)
        return (result, data)

    @staticmethod
    def to_int(sbytem, byteorder="little", signed=False):
        return int.from_bytes(sbytem, byteorder=byteorder, signed=signed)

    @staticmethod
    def from_int(num, length=4, byteorder="little", signed=False):
        return int(num).to_bytes(length, byteorder=byteorder, signed=signed)

    def receive_by_parts(self, msg_length):
        data = bytearray(msg_length)
        mem = memoryview(data)
        while msg_length > 0:
            msg_length -= self.socket.recv_into(mem, msg_length)
            mem = mem[-msg_length:]
        return data

    def send(self, action, data=""):
        assert isinstance(action, Action), "action is not valid."
        action_code = __class__.from_int(action.value)
        data_bytes = data.encode(self.encoding)
        length_code = __class__.from_int(len(data_bytes))
        msg = b"".join((action_code, length_code, data_bytes))
        self.socket.sendall(msg)


class RequestError(GameConnectionError):
    pass


if __name__ == "__main__":
    connector_demonstration()
    send_some_requests()
