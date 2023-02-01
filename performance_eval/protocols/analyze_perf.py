from matplotlib import pyplot
import statistics
import csv

protocol = "coap"
ms = "1000"

filename = f"data/performance_analysis_{protocol}_{ms}ms.csv"
file = open(filename)
reader = csv.reader(file)

times = []
hashtable = {}

if protocol == "http":
	for line in reader:
		try:
			if line[0] == "200":
				times.append(int(line[1]))
			else:
				print(line[0])
		except Exception as e:
			print("Exception:", line)
			print(e)
else:
	for line in reader:
		try:
			if line[0] == "S":
				hashtable[line[1]] = int(line[2])
			else:
				times.append(int(line[2]) - hashtable[line[1]] )
		except Exception as e:
			print("Eccezione per:", line)
			print(e)



print("")
print("")
print("")

print("mean:", statistics.mean(times))
print("median:", statistics.median(times))
print("max:", max(times))
print("min:", min(times))


pyplot.plot(times )
pyplot.title(f"Performance of {protocol} - sample freq {ms}ms")
pyplot.xlabel("Packet number")
pyplot.ylabel("Delay (ms)")

pyplot.savefig(f'fig/{protocol}_{ms}ms.png')
pyplot.show()

