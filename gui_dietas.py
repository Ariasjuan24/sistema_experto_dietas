import pymysql
from tkinter import Tk, Label, Entry, Button, Text, messagebox, StringVar, ttk, Toplevel
from pyswip import Prolog
from tkinter import *
from tkinter import ttk
from PIL import Image, ImageTk
from tkinter import Toplevel, Label, Frame, Button, LEFT, BOTH

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

# Función para mostrar la ventana principal
def abrir_ventana_principal():
    ventana_bienvenida.destroy()
    ventana_principal()

# Función para mostrar información del sistema
def mostrar_informacion():
    messagebox.showinfo(
        "Información del Sistema",
        "Este sistema experto te ayudará a encontrar una dieta recomendada "
        "según tu condición de salud, edad, peso, altura y nivel de actividad física."
    )

# Función para calcular calorías objetivo
def calcular_calorias(edad, peso, altura, genero, nivel_actividad):
    altura_cm = altura * 100
    if genero == "Hombre":
        tmb = 10 * peso + 6.25 * altura_cm - 5 * edad + 5
    else:
        tmb = 10 * peso + 6.25 * altura_cm - 5 * edad - 161

    factores_actividad = {
        "Sedentario": 1.2,
        "Ligera actividad": 1.375,
        "Actividad moderada": 1.55,
        "Alta actividad": 1.725,
        "Muy intensa": 1.9
    }
    calorias_objetivo = tmb * factores_actividad.get(nivel_actividad, 1.2)
    return round(calorias_objetivo, 2)

# Función para guardar datos en MySQL
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

# Función para obtener dieta recomendada
def obtener_dieta():
    resultado_texto.delete(1.0, "end")
    nombre = nombre_entrada.get()
    edad = edad_entrada.get()
    altura = altura_entrada.get()
    peso = peso_entrada.get()
    condicion = condicion_var.get()
    genero = genero_var.get()
    nivel_actividad = nivel_actividad_var.get()

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

    calorias_objetivo = calcular_calorias(edad, peso, altura, genero, nivel_actividad)
    calorias_objetivo_var.set(f"{calorias_objetivo} kcal")

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

    guardar_usuario(nombre, edad, altura, peso, condicion, dieta, calorias_objetivo)

# Función para la ventana principal
def ventana_principal():
    global nombre_entrada, edad_entrada, altura_entrada, peso_entrada, condicion_var, genero_var
    global nivel_actividad_var, calorias_objetivo_var, resultado_texto

    ventana = Tk()
    ventana.title("Sistema Experto de Dietas")
    ventana.config(bg="#e0f7fa")

    niveles_actividad = ["Sedentario", "Ligera actividad", "Actividad moderada", "Alta actividad", "Muy intensa"]
    condiciones_salud = ["Hipertensión", "Diabetes", "Obesidad", "Colesterol alto", "Aumento muscular", "Vegano", "Normal"]

    bienvenida = Label(ventana, text="Bienvenido al Sistema Experto de Dietas", font=("Arial", 16, "bold"), fg="#00796b", bg="#e0f7fa")
    bienvenida.grid(row=0, column=0, columnspan=2, pady=20)

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

    Button(ventana, text="Obtener Dieta", command=obtener_dieta, bg="#00796b", fg="white", font=("Arial", 12, "bold")).grid(row=9, column=0, columnspan=2, pady=20)

    resultado_texto = Text(ventana, height=10, width=50, font=("Arial", 12))
    resultado_texto.grid(row=10, column=0, columnspan=2, pady=10)

    ventana.mainloop()

def mostrar_info_sistema():
    # Crear ventana de información
    ventana_info = Toplevel()
    ventana_info.title("Información del Sistema")
    ventana_info.geometry("600x500")  # Ajusta el tamaño si es necesario
    ventana_info.configure(bg="#f0f8ff")

    # Título principal
    Label(ventana_info, text="Información del Sistema Experto", font=("Arial", 14, "bold"), bg="#f0f8ff").pack(pady=10)

    # Subtítulo de "Información del sistema"
    Label(ventana_info, text="Información del sistema", font=("Arial", 12, "bold"), bg="#f0f8ff").pack(pady=5)

    # Información del sistema
    info_sistema = """
    Este es un sistema experto diseñado para ayudar a los usuarios 
    a obtener recomendaciones personalizadas de dietas en base a sus necesidades. 
    Utiliza una base de conocimientos y un conjunto de reglas para ofrecer 
    soluciones adecuadas dependiendo de los datos del usuario.
    """
    Label(ventana_info, text=info_sistema, font=("Arial", 10), bg="#f0f8ff", justify=LEFT).pack(pady=10)

    # Subtítulo de "Expertos"
    Label(ventana_info, text="Expertos", font=("Arial", 12, "bold"), bg="#f0f8ff").pack(pady=5)

    # Frame para los expertos
    frame_expertos = Frame(ventana_info, bg="#f0f8ff")
    frame_expertos.pack(fill=BOTH, expand=True, padx=10, pady=10)

    # Función para cargar y redimensionar imagen
    def cargar_imagen(ruta, tamaño=(100, 100)):
        try:
            img = Image.open(ruta)  # Abrir imagen
            img = img.resize(tamaño, Image.Resampling.LANCZOS)  # Redimensionar usando LANCZOS
            return ImageTk.PhotoImage(img)
        except Exception as e:
            print(f"Error al cargar la imagen '{ruta}': {e}")
            return None

    # Información del Experto 1
    frame_experto1 = Frame(frame_expertos, bg="#f0f8ff")
    frame_experto1.grid(row=0, column=0, padx=10, pady=10, sticky="w")

    ruta_img1 = "images/navarro.png"  # Ruta de la imagen del experto 1
    img_experto1 = cargar_imagen(ruta_img1)

    if img_experto1:
        Label(frame_experto1, image=img_experto1, bg="#f0f8ff").pack(side=LEFT)
    else:
        Label(frame_experto1, text="Foto no disponible", bg="#f0f8ff", fg="red").pack(side=LEFT)

    Label(frame_experto1, text="Nombre: José Navarro\nEspecialidad: Asesor nutricional\nInstagram: @leads_sport_nutrition", 
          font=("Arial", 10), bg="#f0f8ff", justify=LEFT).pack(side=LEFT, padx=10)

    # Información del Experto 2
    frame_experto2 = Frame(frame_expertos, bg="#f0f8ff")
    frame_experto2.grid(row=1, column=0, padx=10, pady=10, sticky="w")

    ruta_img2 = "images/mateo.png"  # Ruta de la imagen del experto 2
    img_experto2 = cargar_imagen(ruta_img2)

    if img_experto2:
        Label(frame_experto2, image=img_experto2, bg="#f0f8ff").pack(side=LEFT)
    else:
        Label(frame_experto2, text="Foto no disponible", bg="#f0f8ff", fg="red").pack(side=LEFT)

    Label(frame_experto2, text="Nombre: Mateo López\nEspecialidad: Lic. en nutrición deportiva\nInstagram: @mateolopeznutrition", 
          font=("Arial", 10), bg="#f0f8ff", justify=LEFT).pack(side=LEFT, padx=10)

    # Botón para cerrar, con estilo mejorado
    def on_enter_cerrar(boton):
        boton.config(bg="#4169e1", font=("Arial", 12, "bold"))

    def on_leave_cerrar(boton):
        boton.config(bg="#4682b4", font=("Arial", 10))

    btn_cerrar = Button(ventana_info, text="Cerrar", command=ventana_info.destroy, bg="#4682b4", fg="white", 
                        relief="flat", width=20, height=2)
    btn_cerrar.pack(pady=20)
    btn_cerrar.bind("<Enter>", lambda e: on_enter_cerrar(btn_cerrar))
    btn_cerrar.bind("<Leave>", lambda e: on_leave_cerrar(btn_cerrar))

    # Necesario para mantener referencias de las imágenes
    ventana_info.mainloop()

# Crear la ventana de bienvenida
ventana_bienvenida = Tk()
ventana_bienvenida.title("Bienvenida")
ventana_bienvenida.geometry("600x400")  # Ventana más amplia para dar mejor sensación
ventana_bienvenida.configure(bg="#e0f7fa")  # Fondo de color suave

# Etiqueta de bienvenida con estilo
Label(ventana_bienvenida, text="¡Bienvenido a NutriAsistPro!", font=("Verdana", 20, "bold"), bg="#e0f7fa", fg="#00796b").pack(pady=30)

# Sección para agregar una imagen de bienvenida (opcional)
try:
    # Usando PIL para abrir la imagen
    imagen_bienvenida = Image.open("images/nutri.png")  # Cambia esta ruta por la correcta
    imagen_bienvenida = imagen_bienvenida.resize((250, 250))  # Redimensiona la imagen a 250x250
    imagen_bienvenida = ImageTk.PhotoImage(imagen_bienvenida)  # Convertir a formato adecuado para Tkinter
    
    # Mostrar la imagen redimensionada
    Label(ventana_bienvenida, image=imagen_bienvenida, bg="#e0f7fa").pack(pady=10)
except Exception as e:
    print(f"No se pudo cargar la imagen: {e}")

# Botones con mejor estilo y efectos de hover
def on_enter_boton(boton):
    boton.config(bg="#004d40")

def on_leave_boton(boton):
    boton.config(bg="#00796b")

frame_botones = Frame(ventana_bienvenida, bg="#e0f7fa")
frame_botones.pack()

# Botón para mostrar información del sistema
btn_info = Button(frame_botones, text="Información del Sistema", command=mostrar_info_sistema, 
                  bg="#00796b", fg="white", font=("Arial", 12, "bold"), relief="flat", width=20, height=2)
btn_info.grid(row=0, column=0, pady=10)
btn_info.bind("<Enter>", lambda e: on_enter_boton(btn_info))
btn_info.bind("<Leave>", lambda e: on_leave_boton(btn_info))

# Botón para comenzar
btn_comenzar = Button(frame_botones, text="Comenzar", command=ventana_principal, 
                     bg="#00796b", fg="white", font=("Arial", 12, "bold"), relief="flat", width=20, height=2)
btn_comenzar.grid(row=1, column=0, pady=10)
btn_comenzar.bind("<Enter>", lambda e: on_enter_boton(btn_comenzar))
btn_comenzar.bind("<Leave>", lambda e: on_leave_boton(btn_comenzar))

# Mostrar la ventana
ventana_bienvenida.mainloop()