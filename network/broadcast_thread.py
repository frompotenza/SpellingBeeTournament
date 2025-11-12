import socket
import threading
import shared_resources as sr
import time
import asyncio


class BroadcastThread:

    BROADCAST_PORT : int = 50000
    BROADCAST_IP : str = '255.255.255.255'
    BUFSIZE : int = 1024


    def __init__(self):
        self.active = True # TODO delete this and replace with TRUE everywhere if we never need this (probably we wont)
        self.in_queue = sr.in_queue()
        self.out_queue = sr.out_queue()

        # init socket
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind(('', self.BROADCAST_PORT))
        
        # init threads
        self.peerlist = sr.PeerList()
        self.listener_thread = threading.Thread(target=self.__listener_thread, args=())
        self.sender_thread = threading.Thread(target=self.__sender_thread, args=())
        self.listener_thread.start()
        self.sender_thread.start()
 

    async def start(self) :
        self.active = True
        asyncio.create_task(self.heartbeat())


    def __listener_thread(self):
        while self.active:
            data, sender = self.socket.recvfrom(self.BUFSIZE) # blocks thread until data received
            message = data.decode()
            print(f'Received broadcast message: {message} by {sender}')
            try:
                loop = asyncio.get_running_loop()
                loop.call_soon_threadsafe(self.in_queue.put_nowait, (sender, message))
            except RuntimeError as e:
                print(e.__traceback__)
                print("Waiting for event loop...")


    def __sender_thread(self):
        while self.active:
            if not self.out_queue.empty():
                message = self.out_queue.get()
                # NOTE: in general, one have to check whether all bytes are sent
                # source: https://docs.python.org/3/library/socket.html
                # however, I think this is not true for UDP (correct me if I'm wrong)
                sr.send_message(self.socket, message, self.BROADCAST_IP, self.BROADCAST_PORT)


    def parse_incoming_message(self, message):
        if message.type == sr.States.HEARTBEAT:
            print(f"Received heartbeat message: {message}")
            # TODO check whether message contains expected fields
            # TODO if unknown peer: add peer to peerlist
            # TODO if known peer: update in peerlist when I last received broadcast from peer
        else:
            print(f"Ignoring received broadcast message of unknown type: {message}")
        # TODO leader election message type
        # TODO shutdown message type


    async def heartbeat(self):
        while True:
            print(f"{time.time()} - HEARTBEAT")
            heartbeat_message = {
                "type": sr.MessageTypes.HEARTBEAT.name, # "HEARTBEAT"
                "sending_time": time.time()
            }

            self.out_queue.put(heartbeat_message)
            await asyncio.sleep(5)


    def __exit__(self):
        self.socket.close()
