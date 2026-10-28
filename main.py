from node import PhysicalNode
import time


twin_url = "http://127.0.0.1:5000"


A = PhysicalNode("A", 50, twin_url)

B = PhysicalNode("B", 30, twin_url)

C = PhysicalNode("C", 20, twin_url)


A.add_neighbor(B)

B.add_neighbor(C)

C.add_neighbor(A)


A.sync_to_twin()

B.sync_to_twin()

C.sync_to_twin()


print("Simulating fault")


A.update_power(-100)


A.check_blackout()