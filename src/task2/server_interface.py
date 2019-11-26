import connection
import json

def to_json(obj):
    return json.dumps(obj, separators=(",", ":"))

class serverInterface:
    def __init__(self, name):
        self.opened_connection = connection.Connector()
        self.opened_connection.connect()
        self.opened_connection.send(connection.Action.LOGIN, to_json({"name": name}))
        msg = self.opened_connection.receive()
            
    def closeConnection(self):
        if self.opened_connection :
            self.opened_connection.send(connection.Action.LOGOUT)
            msg = self.opened_connection.receive()        
            self.opened_connection.close()
            self.opened_connection=None
            return msg
    
    def getMapLevel(self,level):
        if level == 0 or level == 1 or level == 10:
            if self.opened_connection :
                self.opened_connection.send(connection.Action.MAP, to_json({"layer": level}))
                msg = self.opened_connection.receive()   
                #msg[0] result check need
                status_result=msg[0]
                return ''.join(msg[1:])     
            
    def __del__(self):
        self.closeConnection()   
