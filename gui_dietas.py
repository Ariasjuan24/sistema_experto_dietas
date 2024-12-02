import pymysql
from tkinter import Tk, Label, Entry, Button, Text, messagebox, StringVar, ttk
from pyswip import Prolog

# Conexión a MySQL
def conectar_mysql():
    return pymysql.connect(
        host="localhost",
        user="nutriologo",
        password="123",
        database="sistema_dietas"
    )

# Inicializar Prolog
prolog = Prolog()
prolog.consult("sistema_dietas.pl")

# Función para calcular las calorías objetivo
def calcular_calorias(edad, peso, altura, genero, nivel_actividad):
    # Convertir altura de metros a centímetros
    altura_cm = altura * 100

    # Calcular TMB (Tasa Metabólica Basal)
    if genero == "Hombre":
        tmb = 10 * peso + 6.25 * altura_cm - 5 * edad + 5
    else:  # Mujer
        tmb = 10 * peso + 6.25 * altura_cm - 5 * edad - 161

    # Multiplicar por el factor de actividad
    factores_actividad = {
        "Sedentario": 1.2,
        "Ligera actividad": 1.375,
        "Actividad moderada": 1.55,
        "Alta actividad": 1.725,
        "Muy intensa": 1.9
    }
    calorias_objetivo = tmb * factores_actividad.get(nivel_actividad, 1.2)
    return round(calorias_objetivo, 2)

# Función para guardar datos del usuario en la base de datos
def guardar_usuario(nombre, edad, altura, peso, condicion, dieta, calorias_objetivo):
    try:
        conexion = conectar_mysql()
        cursor = conexion.cursor()
        consulta = """ 
        INSERT INTO usuarios (nombre, edad, altura, peso, condiciones, dieta_recomendada, calorias_objetivo)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(consulta, (nombre, edad, altura, peso, condicion, dieta, calorias_objetivo))
        conexion.commit()
        cursor.close()
        conexion.close()
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo guardar en la base de datos: {e}")

# Función para obtener la dieta recomendada
def obtener_dieta():
    resultado_texto.delete(1.0, "end")
    # Capturar datos
    nombre = nombre_entrada.get()
    edad = edad_entrada.get()
    altura = altura_entrada.get()
    peso = peso_entrada.get()
    condicion = condicion_var.get()
    genero = genero_var.get()
    nivel_actividad = nivel_actividad_var.get()

    # Validar entradas
    try:
        edad = int(edad)
        altura = float(altura)
        peso = float(peso)
    except ValueError:
        messagebox.showerror("Error", "Por favor, ingrese datos válidos.")
        return

    if not nombre or not condicion or not genero or not nivel_actividad:
        messagebox.showerror("Error", "Por favor, complete todos los campos.")
        return

    # Calcular calorías objetivo
    calorias_objetivo = calcular_calorias(edad, peso, altura, genero, nivel_actividad)
    calorias_objetivo_var.set(f"{calorias_objetivo} kcal")

    # Consultar Prolog para dieta recomendada
    query = f"recomendar_dieta('{condicion}', {calorias_objetivo}, Dieta, DietaAjustada)"
    resultados = list(prolog.query(query))

    if resultados:
        dieta = resultados[0]["Dieta"]
        alimentos_ajustados = resultados[0]["DietaAjustada"]

        resultado_texto.insert("end", f"Dieta recomendada: {dieta}\n")
        resultado_texto.insert("end", "Alimentos ajustados:\n")
        for alimento in alimentos_ajustados:
            resultado_texto.insert("end", f"- {alimento}\n")
    else:
        resultado_texto.insert("end", "No se encontraron recomendaciones para esta condición.\n")

    # Guardar en base de datos
    guardar_usuario(nombre, edad, altura, peso, condicion, dieta, calorias_objetivo)

# Crear ventana principal
ventana = Tk()
ventana.title("Sistema Experto de Dietas")
ventana.config(bg="#e0f7fa")

# Variables globales
niveles_actividad = ["Sedentario", "Ligera actividad", "Actividad moderada", "Alta actividad", "Muy intensa"]
condiciones_salud = ["Hipertensión", "Diabetes", "Obesidad", "Colesterol alto", "Aumento muscular", "Vegano", "Normal"]

# Encabezado de bienvenida
bienvenida = Label(ventana, text="Bienvenido al Sistema Experto de Dietas", font=("Arial", 16, "bold"), fg="#00796b", bg="#e0f7fa")
bienvenida.grid(row=0, column=0, columnspan=2, pady=20)

# Campos de entrada
Label(ventana, text="Nombre:", bg="#e0f7fa", font=("Arial", 12)).grid(row=1, column=0, padx=10, pady=10)
nombre_entrada = Entry(ventana, font=("Arial", 12))
nombre_entrada.grid(row=1, column=1, padx=10, pady=10)

Label(ventana, text="Edad:", bg="#e0f7fa", font=("Arial", 12)).grid(row=2, column=0, padx=10, pady=10)
edad_entrada = Entry(ventana, font=("Arial", 12))
edad_entrada.grid(row=2, column=1, padx=10, pady=10)

Label(ventana, text="Altura (m):", bg="#e0f7fa", font=("Arial", 12)).grid(row=3, column=0, padx=10, pady=10)
altura_entrada = Entry(ventana, font=("Arial", 12))
altura_entrada.grid(row=3, column=1, padx=10, pady=10)

Label(ventana, text="Peso (kg):", bg="#e0f7fa", font=("Arial", 12)).grid(row=4, column=0, padx=10, pady=10)
peso_entrada = Entry(ventana, font=("Arial", 12))
peso_entrada.grid(row=4, column=1, padx=10, pady=10)

Label(ventana, text="Condición de Salud:", bg="#e0f7fa", font=("Arial", 12)).grid(row=5, column=0, padx=10, pady=10)
condicion_var = StringVar(value="Hipertensión")
condicion_menu = ttk.Combobox(ventana, textvariable=condicion_var, values=condiciones_salud, state="readonly", font=("Arial", 12))
condicion_menu.grid(row=5, column=1, padx=10, pady=10)

Label(ventana, text="Género:", bg="#e0f7fa", font=("Arial", 12)).grid(row=6, column=0, padx=10, pady=10)
genero_var = StringVar(value="Hombre")
genero_menu = ttk.Combobox(ventana, textvariable=genero_var, values=["Hombre", "Mujer"], state="readonly", font=("Arial", 12))
genero_menu.grid(row=6, column=1, padx=10, pady=10)

Label(ventana, text="Nivel de Actividad:", bg="#e0f7fa", font=("Arial", 12)).grid(row=7, column=0, padx=10, pady=10)
nivel_actividad_var = StringVar(value="Sedentario")
nivel_actividad_menu = ttk.Combobox(ventana, textvariable=nivel_actividad_var, values=niveles_actividad, state="readonly", font=("Arial", 12))
nivel_actividad_menu.grid(row=7, column=1, padx=10, pady=10)

Label(ventana, text="Calorías Objetivo:", bg="#e0f7fa", font=("Arial", 12)).grid(row=8, column=0, padx=10, pady=10)
calorias_objetivo_var = StringVar()
calorias_objetivo_label = Label(ventana, textvariable=calorias_objetivo_var, font=("Arial", 12))
calorias_objetivo_label.grid(row=8, column=1, padx=10, pady=10)

# Botón para obtener dieta
Button(ventana, text="Obtener Dieta", command=obtener_dieta, bg="#00796b", fg="white", font=("Arial", 12, "bold")).grid(row=9, column=0, columnspan=2, pady=20)

# Área de texto para mostrar resultados
resultado_texto = Text(ventana, width=50, height=10, font=("Arial", 12), wrap="word")
resultado_texto.grid(row=10, column=0, columnspan=2, padx=10, pady=10)

# Instrucciones adicionales
instrucciones = Label(ventana, text="Complete los datos para recibir su recomendación personalizada.", bg="#e0f7fa", font=("Arial", 12))
instrucciones.grid(row=11, column=0, columnspan=2, pady=10)

# Ejecutar la aplicación
ventana.mainloop()
