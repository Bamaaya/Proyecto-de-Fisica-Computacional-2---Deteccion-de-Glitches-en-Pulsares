import numpy as np
import matplotlib.pyplot as plt

def readFile(path):
    """
    Reads a given file and split it's content into three new lists: frequencies, time of arrival and errors

    Parameters:
    - File's path (path): path of the file to be read

    Return:
    - freq (list): list that contains the given pulsar's frequecies
    - toa (list): list that contains the time of arrival of each frequency
    - err (list): list that contains something that I suspect is the error of one of the two things above
    """
    file = open(path,"r")
    file.readline()
    contentInFile = file.readlines()
    freq = [] # Frequency
    toa = [] # Time of arrival
    err = [] # Error? I'm not sure
    for line in contentInFile:
        line = line.split()
        freq.append(float(line[1]))
        toa.append(float(line[2]))
        err.append(float(line[3]))
    file.close()
    return freq, toa, err

path = input("Ingrese el paso de su archivo (con formato): ") # /Users/benja_n/Downloads/psr04.tim
freq, toa, err = readFile(path)

# Intervals are calculated
intervalNumber = int(input("Ingrese la cantidad de intervalos deseados para realizar sub-intervalos de\nfrecuencias (ingrese un número entero positivo): "))
toaRange = toa[-1] - toa[0]
intervalLenght = toaRange/intervalNumber
# Limits of each interval are determinated
intervals = []
for i in range(1,intervalNumber):
    intervals.append(toa[0]+intervalLenght*i)
intervals.append(toa[-1])
# Lists to add each time/frequency based on it's corresponding time interval is created
t = {}
f0 = {}
for i in range(intervalNumber):
    t[f't_{i}'] = []
    f0[f'f0_{i}'] = []
# Each time/frequency is added to it's corresponding list
for elem in toa:
    if elem < intervals[0]:
        t[f't_0'].append(elem)
        f0[f'f0_0'].append(freq[toa.index(elem)])
    for i in range(1,len(intervals)):
        if intervals[i-1] < elem <= intervals[i]:
            t[f't_{i}'].append(elem)
            f0[f'f0_{i}'].append(freq[toa.index(elem)])
print(t,"\n",f0)
# Derivatives are calculated for each sub-section
f1 = {}
for key, value in f0.items():
    f1[f'f1_{key[3:]}'] = np.gradient(value)
print(f1)
# Code if numpy's method isn't apropiated
"""import sympy as sp
f1 = {}
for key, value in f0.items():
    value_symbols = [sp.symbols(f'x{i}') for i in range(len(value))]
    value_diff = [sp.diff(val) for val in value_symbols]
    f1[f'f1_{key[3:]}'] = value_diff"""

# This needs to be fixed since you can't make a plot with a dictionary
"""fig = plt.figure(figsize=(6,6))
ax = fig.add_subplot(111)
ax.plot(toa, f1, linewidth=1, linestyle="--", color="black", alpha=0.5)
ax.set_title("Glitches detectados para psr04")
ax.set_xlabel("Tiempo [IDK]")
ax.set_ylabel("Derivada de la frecuencia")
ax.legend()
plt.show()"""
print("Este es un programa en desarrollo, no considerar sus resultados como válidos.")