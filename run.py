import asyncio
from node import Node

nodes = [
    Node(1,8001,[8002,8003]),
    Node(2,8002,[8001,8004]),
    Node(3,8003,[8001,8005]),
    Node(4,8004,[8002,8006]),
    Node(5,8005,[8003,8007]),
    Node(6,8006,[8004,8008]),
    Node(7,8007,[8005,8009]),
    Node(8,8008,[8006,8010]),
    Node(9,8009,[8007]),
    Node(10,8010,[8008])
]

async def main():

    await asyncio.gather(*[node.run() for node in nodes])

    print("Servers running...")

    await asyncio.sleep(3)

    await asyncio.gather(*[node.client() for node in nodes])

asyncio.run(main())