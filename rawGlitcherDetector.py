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
