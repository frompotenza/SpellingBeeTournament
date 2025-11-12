import broadcast_thread as br
import shared_resources as sr
import asyncio


# for managing the overall flow and states
class Node:

    def __init__(self):
        self.broadcast_thread = br.BroadcastThread()
        self.in_queue = sr.in_queue() # (sender, message) tuples
        self.out_queue = sr.out_queue() # message objects


    async def run(self): # NOTE while true loops always have to be async if they dont have their own thread!
        while True:
            print("Listening...")
            message = await self.in_queue.get()
            if message.type in sr.BROADCAST_MESSAGE_TYPES:
                self.broadcast_thread.parse_incoming_message(message)
            await asyncio.sleep(0.1) 


    async def start(self):
        asyncio.create_task(self.run()) # needs to run as a task because e.g. as an await it would block every other coroutine until its done
        await self.broadcast_thread.start()



    # TODO - maybe only leader - mark peers as disconnected in peerlist if last heartbeat was too long ago (also some sort of async "cronjob") 
    # TODO end discovery phase: after waiting x time and discovering minimum amount of players necessary
    # TODO alternatively: you show users how many peers are discovered and s/he can decide when to start 

##################################################################################################################################################

async def main():
    node = Node()
    await node.start()
    await asyncio.Event().wait() # keeps event loop alive


if __name__ == "__main__":
    asyncio.run(main()) # starts async event loop
    # NOTE whenever I ask for user input this might block the eventloop (and also the heartbeat)
    # check that whenever implementing user interaction and use async if necessary
    