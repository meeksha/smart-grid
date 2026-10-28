import requests
import matplotlib.pyplot as plt


url = "http://127.0.0.1:5000/all"


data = requests.get(url).json()


names = list(data.keys())

power = list(data.values())


plt.bar(names, power)

plt.title("Digital Twin Smart Grid")

plt.show()