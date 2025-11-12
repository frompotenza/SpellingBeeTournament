from enum import Enum
import asyncio
import queue
import json

 # TODO IMPORTANT ask if we are allowed to use python queues 
 # (probably not because they want us to implement the blocking stuff ourselves)
__in_queue = asyncio.Queue() # NOTE threads can only write via event loop
__out_queue = queue.Queue() # NOTE async can only read via executor I think (not tested)

__peerlist = []


def in_queue() -> asyncio.Queue:
    return __in_queue

def out_queue() -> asyncio.Queue:
    return __out_queue   


class SingletonMeta(type): 
    _instances = {} 
    
    def __call__(cls, *args, **kwargs): 
        if cls not in cls._instances: 
            instance = super().__call__(*args, **kwargs) 
            cls._instances[cls] = instance 
            return cls._instances[cls] 


class PeerList(metaclass=SingletonMeta):

    def peer_list(self) -> list:
        return __peerlist

    def append(self, peer):
        __peerlist.append(peer)

    def remove(peer):
        __peerlist.remove(peer)

    def pop(peer_index):
        __peerlist.pop(peer_index)

    def mark_as_disconnected(peer_index):
        pass # TODO I need to define a peer structure first

    def mark_as_connected(peer_index):
        pass # TODO I need to define a peer structure first
    

class States(Enum):
    IDLE = 1 # only listens if something happens
    DISCOVERY = 2 # peer discovery and joining game (if there is a running game)
    LEADER_ELECTION = 3

BROADCAST_STATES = [States.IDLE, States.DISCOVERY, States.LEADER_ELECTION]


class MessageTypes(Enum):
    HEARTBEAT = 1
    LEADER_ELECTION = 2
    SHUTDOWN = 3
    # NOTE we could add a discovery message (faster connection), but I just let them wait for heatbeat for discovery (simpler, needs 5-10s)

BROADCAST_MESSAGE_TYPES = [MessageTypes.HEARTBEAT, MessageTypes.LEADER_ELECTION, MessageTypes.SHUTDOWN]


def send_message(socket, message, target_ip, target_port):
    message_bytes = json.dumps(message, cls=EnumEncoder).encode("utf-8")
    return socket.sendto(
        message_bytes, 
        (target_ip, target_port)
    )

class EnumEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Enum):
            return obj.name  # or obj.value
        return super().default(obj)
    

def decode_message(data):
    message = json.loads(data.decode("utf-8"))
    message.type = MessageTypes[message["type"]]