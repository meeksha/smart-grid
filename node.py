import asyncio
import websockets
import json
import os
import time

from twin_server import AIDigitalTwin

DATA_DIR = os.path.abspath("data")
FAULT_FILE = os.path.join(DATA_DIR, "fault.json")

os.makedirs(DATA_DIR, exist_ok=True)


class Node:

    def __init__(self, id, port, peers):

        self.id = id
        self.port = port
        self.peers = peers

        self.twin = AIDigitalTwin("grid_blueprints/station.json", id)

    # --------------------------
    # SAVE STATE (IMPORTANT)
    # --------------------------

    def save_state(self, load):

        file = os.path.join(DATA_DIR, f"node_{self.id}.json")

        with open(file, "w") as f:
            json.dump({
                "node": self.id,
                "load": load,
                "capacity": self.twin.capacity,
                "time": time.time()
            }, f)

    # --------------------------
    # SERVER
    # --------------------------

    async def server(self):

        async def handler(ws):
            try:
                async for msg in ws:

                    data = json.loads(msg)

                    if data.get("action") == "redistribute":

                        amount = data["amount"]

                        for t in self.twin.state["transformers"]:
                            t["load"] += amount / len(self.twin.state["transformers"])

                        print(f"Node {self.id} received +{amount}")

                        self.save_state(sum(t["load"] for t in self.twin.state["transformers"]))

                    await ws.send(json.dumps({"ack": True}))

            except:
                pass

        return await websockets.serve(handler, "localhost", self.port)

    # --------------------------
    # CLIENT LOOP
    # --------------------------

    async def client(self):

        while True:

            # --------------------------
            # FAULT CHECK
            # --------------------------

            if os.path.exists(FAULT_FILE):
                try:
                    with open(FAULT_FILE) as f:
                        fault = json.load(f)

                    if fault.get("node") == self.id:
                        os.remove(FAULT_FILE)
                        self.twin.apply_fault()

                except:
                    pass

            # --------------------------
            # SIMULATION
            # --------------------------

            load = self.twin.simulate()

            print(f"Node {self.id} Load:{load}")

            # 🔥 ALWAYS SAVE
            self.save_state(load)

            # --------------------------
            # OVERLOAD
            # --------------------------

            if load > self.twin.capacity:

                excess = load - self.twin.capacity
                share = excess / len(self.peers)

                print(f"Node {self.id} redistributing {excess}")

                msg = json.dumps({
                    "node": self.id,
                    "action": "redistribute",
                    "amount": share
                })

                for peer in self.peers:
                    try:
                        async with websockets.connect(f"ws://localhost:{peer}") as ws:
                            await ws.send(msg)
                            await ws.recv()
                    except:
                        continue

            # --------------------------
            # SYNC
            # --------------------------

            for peer in self.peers:
                try:
                    async with websockets.connect(f"ws://localhost:{peer}") as ws:
                        await ws.send(json.dumps({"node": self.id}))
                        await ws.recv()
                except:
                    continue

            await asyncio.sleep(2)

    # --------------------------
    # RUN
    # --------------------------

    async def run(self):
        await self.server()