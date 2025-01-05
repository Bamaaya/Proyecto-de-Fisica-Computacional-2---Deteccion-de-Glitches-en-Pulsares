import tkinter as tk
import numpy as np
import matplotlib.pyplot as plt
import math
import sympy as sym

from scipy.signal import find_peaks
from tkinter import filedialog, messagebox, ttk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# FUNCIONES DE ANÁISIS
#Función para limpiar los datos
def limpiarDatos(lista):
  """
  Función datosLimpios()
  -Input: lista
  -Output: lista

  Cumple la función de limpiar listas de datos de datos no numéricos mediante math.isfinite()
  Retorna la misma lista ingresada sin datos "Nan"
  """
  datosLimpios = []
  for datos in lista:
    if math.isfinite(datos):
      datosLimpios.append(datos)

  return datosLimpios

def eliminarDuplicados(tiempo): #se usa después de procesar los datos y limpiar lista tiempo de nans

    listaClean = []
    indicesClean = []

    for i in range(len(tiempo)):
        elem = str(tiempo[i]).split(".")[0] #el tiempo se formatea 1323.0000002
        #son duplicados los que empiezan igual antes de el punto.

        if elem not in listaClean:
            listaClean.append(elem)
            indicesClean.append(i) # de vuelve los indices

    return indicesClean


def procesar_linea(elementos, tiempo, frecuencia, incertezas):
  """
  Procesa una línea del archivo.
  """
  datosLinea = elementos.split()

  # Verificar si la línea no está vacía
  if not datosLinea:
      print(f"Advertencia: línea vacía ignorada.")
      return tiempo, frecuencia, incertezas

  if len(datosLinea) == 3:
      try:
          tiempo.append(float(datosLinea[0]))
          frecuencia.append(float(datosLinea[1]))
          incertezas.append(float(datosLinea[2]))
      except ValueError:
          print(f"Advertencia: no se pudo convertir los valores a float en la línea: {elementos}")

  elif len(datosLinea) == 2:
      try:
          tiempo.append(float(datosLinea[0]))
          frecuencia.append(float(datosLinea[1]))
      except ValueError:
          print(f"Advertencia: no se pudo convertir los valores a float en la línea: {elementos}")

  else:
      print(f"Advertencia: número de columnas inesperadas en la línea: {elementos}")

  return tiempo, frecuencia, incertezas


def leerArchivo(archivo):
    """
    Función leerArchivo()
    -Input: archivo
    -Output: 3 listas

    Lee el archivo y procesa sus datos en 3 listas: tiempos, frecuencias, e incertezas.
    """
    with open(archivo, "r") as lectura:
        listaDatos = lectura.readlines()

    tiempo = []
    frecuencia = []
    incertezas = []

    # Procesar cada línea del archivo
    for elementos in listaDatos:
        tiempo, frecuencia, incertezas = procesar_linea(elementos, tiempo, frecuencia, incertezas)

    # Limpiar los datos de posibles Nans
    tiempoTrue = limpiarDatos(tiempo)
    frecuenciaTrue = limpiarDatos(frecuencia)

    #eliminar los duplicados:
    indices = eliminarDuplicados(tiempoTrue)

    tiempoClean = [tiempoTrue[i] for i in indices]
    frecuenciaClean = [frecuenciaTrue[i] for i in indices]


    # Si hay incertezas, limpiarlas también
    if incertezas:

        incertezasTrue = limpiarDatos(incertezas)
        incertezasClean = [incertezasTrue[i] for i in indices]


        return tiempoClean, frecuenciaClean, incertezasTrue

    else:

        return tiempoClean, frecuenciaClean, []

def ajuste_polinomial(xi,yi,grado=2):

  m = grado

  # PROCEDIMIENTO
  xi = np.array(xi)
  yi = np.array(yi)
  n  = len(xi)

  # llenar matriz a y vector B
  k = m + 1
  A = np.zeros(shape=(k,k),dtype=float)
  B = np.zeros(k,dtype=float)
  for i in range(0,k,1):
      for j in range(0,i+1,1):
          coeficiente = np.sum(xi**(i+j))
          A[i,j] = coeficiente
          A[j,i] = coeficiente
      B[i] = np.sum(yi*(xi**i))

  # coeficientes, resuelve sistema de ecuaciones
  C = np.linalg.solve(A,B)

  # polinomio
  x = sym.Symbol('x')
  f = 0
  fetiq = 0
  for i in range(0,k,1):
      f = f + C[i]*(x**i)
      fetiq = fetiq + np.around(C[i],4)*(x**i)

  fx = sym.lambdify(x,f)
  fi = fx(xi)

  residuo = np.array(yi)-np.array(fi)

  return list(residuo)

def calcular_glitches_y_tiempos(tiempo, frecuencias, paso=1):
    """
    Calcula los tiempos y magnitudes de los glitches basados en los picos positivos y negativos de las frecuencias.
    
    Args:
        tiempo (list): Lista de valores de tiempo.
        frecuencias (list): Lista de valores de frecuencia.
        paso (int): Distancia mínima entre picos.

    Returns:
        tuple: Listas con tiempos de los glitches y magnitudes de los glitches.
    """
    # Encontrar picos positivos
    peaksDatos = find_peaks(frecuencias, distance=paso)
    tiemposInd = [tiempo[i] for i in peaksDatos[0]]
    peaksInd = [frecuencias[i] for i in peaksDatos[0]]

    # Encontrar picos negativos
    datosNega = [(-1) * i for i in frecuencias]
    peaksNega = find_peaks(datosNega, distance=paso)
    tiemposNegaInd = [tiempo[j] for j in peaksNega[0]]
    peaksNegaInd = [frecuencias[j] for j in peaksNega[0]]

    # Cálculo de tiempos y magnitudes de glitches
    tiemposTrue = []
    magGlitch = []
    for i in range(len(peaksDatos[0])):
        tiemposTrue.append((tiemposInd[i] + tiemposNegaInd[i]) / 2)
        magGlitch.append(peaksInd[i] - peaksNegaInd[i])

    return tiemposTrue, magGlitch, tiemposInd, peaksInd, tiemposNegaInd, peaksNegaInd

def graficar_glitches(tiempo, frecuencias, tiemposInd, peaksInd, tiemposNegaInd, peaksNegaInd, nombre):
    """
    Genera un gráfico de los datos de frecuencia con los picos detectados.

    Args:
        tiempo (list): Lista de valores de tiempo.
        frecuencias (list): Lista de valores de frecuencia.
        tiemposInd (list): Tiempos de los picos positivos.
        peaksInd (list): Valores de frecuencia en los picos positivos.
        tiemposNegaInd (list): Tiempos de los picos negativos.
        peaksNegaInd (list): Valores de frecuencia en los picos negativos.
        nombre (str): Nombre para el título del gráfico.
    """
    fig = plt.figure(figsize=(6, 6))
    ax = fig.add_subplot(111)
    ax.plot(tiempo, frecuencias, linewidth=1, linestyle="--", color="black", alpha=0.5)
    ax.set_title(f"Glitches detectados en {nombre}")
    ax.scatter(tiemposInd, peaksInd, marker="x", color="red", s=10, label="Post-Glitch")
    ax.scatter(tiemposNegaInd, peaksNegaInd, marker="x", color="blue", s=10, label="Pre-Glitch")
    ax.set_xlabel("Tiempo [MJD]")
    ax.set_ylabel("Glitches")
    ax.legend()
    plt.show()


# FUNCIONES DE GUI
def open_file():
    """Función para abrir el explorador de archivos y seleccionar un archivo."""
    selected_file = filedialog.askopenfilename(title="Seleccionar archivo")
    if selected_file:
        show_next_window(selected_file)

def show_next_window(selected_file):
    """Ventana secundaria para ingresar detalles del archivo."""
    def check_fields():
        """Verifica que todos los campos obligatorios estén completos y maneja el análisis."""
        if not nombre_entry.get().strip():
            messagebox.showerror("Error", "El campo 'Nombre del pulsar' es obligatorio.")
            return
        if not frecuencia_combobox.get().strip():
            messagebox.showerror("Error", "El campo 'Unidad de frecuencia' es obligatorio.")
            return
        if not tiempo_combobox.get().strip():
            messagebox.showerror("Error", "El campo 'Unidad de Tiempo' es obligatorio.")
            return
        if not tipo_ajuste_combobox.get().strip():
            messagebox.showerror("Error", "Debe seleccionar un tipo de ajuste.")
            return
        if not paso_entry.get().strip():
            messagebox.showerror("Error", "Debe ingresar un valor para el paso entre picos.")
            return

        # Realizar el análisis según la selección
        try:
            tiempoArchivo, frecuenciaArchivo, _ = leerArchivo(selected_file)

            # Obtener parámetros seleccionados
            tipo_ajuste = tipo_ajuste_combobox.get()
            paso = int(paso_entry.get())

            if tipo_ajuste == "Lineal":
                residuos = ajuste_polinomial(tiempoArchivo, frecuenciaArchivo, grado=1)

            elif tipo_ajuste == "Polinomial":
                grado = int(grado_entry.get())
                residuos = ajuste_polinomial(tiempoArchivo, frecuenciaArchivo, grado)
            else:
                raise ValueError("Tipo de ajuste no válido.")

            tiemposGlitches, magGlitches, tiemposPos, peaksPos, tiemposNeg, peaksNeg = calcular_glitches_y_tiempos(
                tiempoArchivo, residuos, paso
            )

            graficar_glitches(tiempoArchivo, residuos, tiemposPos, peaksPos, tiemposNeg, peaksNeg, nombre_entry.get())

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo realizar el análisis: {e}")

    # Crear ventana secundaria
    new_window = tk.Toplevel()
    new_window.title("Detalles del Archivo")
    new_window.geometry("950x500")
    new_window.configure(bg="#eaeaea")

    # Header
    header = tk.Label(new_window, text="Glitch Finder", bg="#3366cc", fg="white", font=("Helvetica", 20, "bold"), pady=10)
    header.pack(fill="x")

    # Crear campos de entrada
    frame = tk.Frame(new_window, bg="#eaeaea", pady=20)
    frame.pack(expand=True)

    # Campos existentes
    tk.Label(frame, text="Ingresa Nombre del pulsar", bg="#eaeaea", font=("Helvetica", 12)).grid(row=0, column=0, padx=20, pady=10, sticky="w")
    nombre_entry = tk.Entry(frame, width=30, bg="#dcdcdc")
    nombre_entry.grid(row=0, column=1, padx=20, pady=10)

    tk.Label(frame, text="Unidad de Frecuencia", bg="#eaeaea", font=("Helvetica", 12)).grid(row=0, column=2, padx=20, pady=10, sticky="w")
    frecuencia_combobox = ttk.Combobox(frame, values=["Hz", "kHz", "cps", "SNU"], state="readonly", width=28)
    frecuencia_combobox.grid(row=0, column=3, padx=20, pady=10)

    tk.Label(frame, text="Archivo elegido", bg="#eaeaea", font=("Helvetica", 12)).grid(row=1, column=0, padx=20, pady=10, sticky="w")
    selected_file_entry = tk.Entry(frame, width=30, bg="#f8d7da")
    selected_file_entry.grid(row=1, column=1, padx=20, pady=10)
    selected_file_entry.insert(0, selected_file)
    selected_file_entry.config(state="readonly")

    tk.Label(frame, text="Unidad de Tiempo", bg="#eaeaea", font=("Helvetica", 12)).grid(row=1, column=2, padx=20, pady=10, sticky="w")
    tiempo_combobox = ttk.Combobox(frame, values=["MJD", "BJD", "TGC", "TT"], state="readonly", width=28)
    tiempo_combobox.grid(row=1, column=3, padx=20, pady=10)

    # Nuevos campos
    tk.Label(frame, text="Tipo de Ajuste", bg="#eaeaea", font=("Helvetica", 12)).grid(row=2, column=0, padx=20, pady=10, sticky="w")
    tipo_ajuste_combobox = ttk.Combobox(frame, values=["Lineal", "Polinomial"], state="readonly", width=28)
    tipo_ajuste_combobox.grid(row=2, column=1, padx=20, pady=10)

    tk.Label(frame, text="Paso entre picos", bg="#eaeaea", font=("Helvetica", 12)).grid(row=3, column=0, padx=20, pady=10, sticky="w")
    paso_entry = tk.Entry(frame, width=30, bg="#dcdcdc")
    paso_entry.grid(row=3, column=1, padx=20, pady=10)

    tk.Label(frame, text="Grado del Polinomio (si aplica)", bg="#eaeaea", font=("Helvetica", 12)).grid(row=3, column=2, padx=20, pady=10, sticky="w")
    grado_entry = tk.Entry(frame, width=30, bg="#dcdcdc")
    grado_entry.grid(row=3, column=3, padx=20, pady=10)

    # Botones
    submit_button = tk.Button(new_window, text="Confirmar", command=check_fields, bg="#4CAF50", fg="white", font=("Helvetica", 12))
    submit_button.pack(pady=10)

    close_button = tk.Button(new_window, text="Cancelar", command=new_window.destroy, bg="#ff4d4d", fg="white", font=("Helvetica", 12))
    close_button.pack(pady=10)



# Crear ventana principal
root = tk.Tk()
root.title("Glitch Finder")
root.geometry("700x500")
root.configure(bg="#1a1a1a")

canvas = tk.Canvas(root, width=700, height=500, bg="#1a1a1a", highlightthickness=0)
canvas.pack(fill="both", expand=True)

canvas.create_text(350, 100, text="Glitch Finder", fill="white", font=("Helvetica", 32, "bold"))
canvas.create_text(350, 150, text="Selecciona un archivo para analizar", fill="white", font=("Helvetica", 14))

upload_button = tk.Button(
    root, text="Subir Archivo", font=("Helvetica", 14), bg="#4CA6FF", fg="white", 
    relief="flat", command=open_file
)
upload_button_window = canvas.create_window(350, 300, anchor="center", window=upload_button)

root.mainloop()

# COMO hacer para seguir esta linea de código usando tkinter?
