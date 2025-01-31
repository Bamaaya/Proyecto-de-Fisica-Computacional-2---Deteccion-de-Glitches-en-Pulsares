import sympy as sp

def readFile(path):
    """
    Reads a given file and split it's content into three new lists: frequencies, time of arrival and errors

    Parameters:
    - File's path (path): path of the file to be read

    Return:
    - freq (list): list that contains the given pulsar's frequecies
    toa (list): list that contains the time of arrival of each frequency
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

path = input("Ingrese el paso de su archivo (con formato): ")
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

# Lists to add each time to it's corresponding interval is created
toaSubIntervals = {}
for i in range(intervalNumber):
    toaSubIntervals[f'f0_{i}'] = []
# Each time is added to it's corresponding list
for i in range(intervals):
    for elem in toa:
        if elem < intervals[i]:
            toaSubIntervals[f'f0_{i}'].append(elem)
