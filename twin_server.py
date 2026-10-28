import json
import copy
import numpy as np

class AIDigitalTwin:

    def __init__(self, blueprint, node_id):

        with open(blueprint) as f:
            self.blueprint = json.load(f)

        self.node_id = node_id
        self.state = copy.deepcopy(self.blueprint)

        self.capacity = sum(t["capacity"] for t in self.state["transformers"])

        self.fault_active = False
        self.fault_timer = 0

    def simulate(self):

        total = 0

        for t in self.state["transformers"]:

            # 🔥 FAULT MODE → allow variation (DO NOT FREEZE)
            if self.fault_active:
                t["load"] += np.random.randint(-3, 3)
                if t["load"] < self.capacity:
                    t["load"] = self.capacity + 10

            else:
                change = np.random.randint(-10, 10)
                t["load"] += change

                if t["load"] < 20:
                    t["load"] = 20

                if t["load"] > t["capacity"]:
                    t["load"] = t["capacity"] - 5

            total += t["load"]

        # fault decay
        if self.fault_active:
            self.fault_timer -= 1
            if self.fault_timer <= 0:
                self.fault_active = False
                print(f"✅ Node {self.node_id} recovered")

        return total

    def apply_fault(self):

        print(f"⚡ FAULT injected at Node {self.node_id}")

        self.fault_active = True
        self.fault_timer = 5

        for t in self.state["transformers"]:
            t["load"] = t["capacity"] + 50