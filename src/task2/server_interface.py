from connection import Action, Connector
import json


def to_json(obj):
    return json.dumps(obj, separators=(",", ":"))


class serverInterface:
    def __init__(self, name):
        self.opened_connection = Connector()
        self.opened_connection.connect()
        self.opened_connection.send(
            Action.LOGIN, to_json({"name": name}))
        msg = self.opened_connection.receive()

    def closeConnection(self):
        if self.opened_connection:
            self.opened_connection.send(Action.LOGOUT)
            msg = self.opened_connection.receive()
            self.opened_connection.close()
            self.opened_connection = None
            return msg

    def getMapLevel(self, level):
        if self.opened_connection:
            if level in [0, 1, 10]:
                self.opened_connection.send(
                    Action.MAP, to_json({"layer": level}))
                msg = self.opened_connection.receive()
                # msg[0] result check need
                status_result = msg[0]
                return ''.join(msg[1:])

    # def map(self, smap):
        # if not self.cn:
           # raise RequestError(Action.PLAYER, "Please Login first.")
        # if not self.map_idx:
            #smap = self.cn.request(Action.MAP, dict(layer=0))
            #xy = self.cn.request(Action.MAP, dict(layer=10))
            # TODO, update static map by coordinates
            # assert smap["idx"] == xy["idx"]
            # smap["size"] = xy["size"]
            # for idx, x, y in (point.values() for point in xy["coordinates"]):
            #     pass # way to indexing in list by points idx
        #dmap = self.cn.request(Action.MAP, dict(layer=1))
        # update smap by dmap: points[idx].post_idx <- posts[post_idx], where
        # idx equal

    def __del__(self):
        self.closeConnection()
