import pymysql
from tkinter import Tk, Label, Entry, Button, Text, messagebox, StringVar, ttk, Toplevel
from pyswip import Prolog
from tkinter import *
from tkinter import ttk, filedialog
from PIL import Image, ImageTk
from tkinter import Toplevel, Label, Frame, Button, LEFT, BOTH
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import subprocess
import os

# Función para conectar a MySQL con manejo de errores mejorado
def conectar_mysql():
    try:
        conexion = pymysql.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            user=os.getenv('DB_USER', 'nutriologo'),
            password=os.getenv('DB_PASSWORD', '123'),
            database=os.getenv('DB_NAME', 'sistema_dietas')
        )
        return conexion
    except pymysql.MySQLError as err:
        messagebox.showerror("Error de Conexión", f"No se pudo conectar a la base de datos: {err}")
        return None

# Inicializar Prolog
prolog = Prolog()
prolog.consult("sistema_dietas.pl")

# Función para calcular calorías objetivo mejorada
def calcular_calorias(edad, peso, altura, genero, nivel_actividad):
    altura_cm = altura * 100
    
    # Fórmula Mifflin-St Jeor más precisa
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

def validar_datos(nombre, edad, altura, peso, condicion, genero, nivel_actividad):
    # Verificación de campos obligatorios
    campos = {
        "Nombre": nombre,
        "Edad": edad,
        "Altura": altura,
        "Peso": peso,
        "Género": genero,
        "Nivel de Actividad": nivel_actividad
    }

    # Validar campos obligatorios
    for campo, valor in campos.items():
        if not valor or str(valor).strip() == "":
            messagebox.showerror("Error de Validación", f"El campo {campo} no puede estar vacío")
            return False

    try:
        # Conversión y validación de tipos
        edad_int = int(edad)
        altura_float = float(altura)
        peso_float = float(peso)

        # Validaciones de rango
        if edad_int < 1 or edad_int > 120:
            messagebox.showerror("Error", "Edad debe estar entre 1 y 120 años")
            return False

        if altura_float < 0.5 or altura_float > 2.5:
            messagebox.showerror("Error", "Altura debe estar entre 0.5 y 2.5 metros")
            return False

        if peso_float < 10 or peso_float > 500:
            messagebox.showerror("Error", "Peso debe estar entre 10 y 500 kg")
            return False

    except ValueError:
        messagebox.showerror("Error", "Por favor ingrese valores numéricos válidos")
        return False

    return True

def obtener_dieta():
    # Limpiar resultado anterior
    resultado_texto.delete(1.0, "end")
    
    # Obtener valores de entrada
    nombre = nombre_entrada.get().strip()
    edad = edad_entrada.get().strip()
    altura = altura_entrada.get().strip()
    peso = peso_entrada.get().strip()
    
    # Obtener selecciones de los ComboBox
    condicion = condicion_var.get() if condicion_var.get() else "Normal"
    genero = genero_var.get()
    nivel_actividad = nivel_actividad_var.get()

    # Validación completa de todos los campos
    if not validar_datos(nombre, edad, altura, peso, condicion, genero, nivel_actividad):
        return

    try:
        edad = int(edad)
        altura = float(altura)
        peso = float(peso)
    except ValueError:
        messagebox.showerror("Error", "Por favor, ingrese datos numéricos válidos.")
        return

    # Calcular calorías
    calorias_objetivo = calcular_calorias(edad, peso, altura, genero, nivel_actividad)
    calorias_objetivo_var.set(f"{calorias_objetivo} kcal")

    # Consulta a Prolog
    calorias_objetivo_num = int(round(calorias_objetivo))
    query = f"recomendar_dieta('{condicion}', {calorias_objetivo_num}, Dieta, DietaAjustada)"
    
    resultados = list(prolog.query(query))

    if resultados:
        dieta = resultados[0].get("Dieta", "No disponible")
        alimentos_ajustados = resultados[0].get("DietaAjustada", [])
        
        resultado_texto.insert("end", f"Dieta recomendada: {dieta}\n")
        resultado_texto.insert("end", "Alimentos ajustados:\n")
        for alimento in alimentos_ajustados:
            resultado_texto.insert("end", f"- {alimento}\n")
    else:
        resultado_texto.insert("end", "No se encontraron recomendaciones para esta condición.\n")
        dieta = "No disponible"

    # Guardar usuario
    guardar_usuario(nombre, edad, altura, peso, condicion, dieta, calorias_objetivo)

    
# Función para guardar usuario con manejo de errores mejorado
def guardar_usuario(nombre, edad, altura, peso, condicion, dieta, calorias_objetivo):
    try:
        with conectar_mysql() as conexion:
            with conexion.cursor() as cursor:
                consulta = """ 
                INSERT INTO usuarios 
                (nombre, edad, altura, peso, condiciones, dieta_recomendada, calorias_objetivo)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """
                
                cursor.execute(consulta, (
                    nombre, edad, altura, peso, 
                    condicion, dieta, calorias_objetivo
                ))
                conexion.commit()
                messagebox.showinfo("Éxito", "Usuario guardado correctamente.")
    except Exception as e:
        messagebox.showerror("Error de Base de Datos", f"No se pudo guardar: {e}")

# Función para imprimir dieta
def imprimir_dieta():
    dieta_contenido = resultado_texto.get("1.0", "end").strip()
    if not dieta_contenido:
        messagebox.showerror("Error", "No hay información de dieta para imprimir.")
        return
    
    archivo = filedialog.asksaveasfilename(
        defaultextension=".pdf",
        filetypes=[("Archivo PDF", "*.pdf")],
        title="Guardar dieta como PDF"
    )
    
    if not archivo: 
        return

    try:
        pdf = canvas.Canvas(archivo, pagesize=letter)
        pdf.setFont("Helvetica", 12)
        pdf.drawString(30, 750, "Sistema Experto de Dietas - Recomendación Personalizada")
        pdf.line(30, 745, 580, 745)
        
        y = 720
        for linea in dieta_contenido.splitlines():
            pdf.drawString(30, y, linea)
            y -= 20
            if y < 50:
                pdf.showPage()
                pdf.setFont("Helvetica", 12)
                y = 750
        
        pdf.save()
        messagebox.showinfo("Éxito", f"Dieta guardada como PDF: {archivo}")
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo guardar el archivo PDF: {e}")

# Función para la ventana principal
def ventana_principal():
    global calorias_objetivo_var, nombre_entrada, edad_entrada, altura_entrada, peso_entrada
    global condicion_var, genero_var, nivel_actividad_var, resultado_texto

    ventana = Tk()
    ventana.title("Sistema Experto de Dietas")
    ventana.config(bg="#e0f7fa")

    niveles_actividad = ["Sedentario", "Ligera actividad", "Actividad moderada", "Alta actividad", "Muy intensa"]
    condiciones_salud = ["Hipertensión", "Diabetes", "Obesidad", "Colesterol alto", "Aumento muscular", "Vegano", "Normal"]

    bienvenida = Label(ventana, text="Bienvenido al Sistema Experto de Dietas", 
                       font=("Arial", 16, "bold"), fg="#00796b", bg="#e0f7fa")
    bienvenida.grid(row=0, column=0, columnspan=2, pady=20)

    campos = [
        ("Nombre:", nombre_entrada := Entry(ventana, font=("Arial", 12))),
        ("Edad:", edad_entrada := Entry(ventana, font=("Arial", 12))),
        ("Altura (m):", altura_entrada := Entry(ventana, font=("Arial", 12))),
        ("Peso (kg):", peso_entrada := Entry(ventana, font=("Arial", 12)))
    ]

    # Validaciones en tiempo real
    vcmd_nombre = (ventana.register(lambda P: len(P) <= 50), '%P')
    vcmd_numerico = (ventana.register(lambda P: P.replace('.','',1).isdigit() or P == ""), '%P')
    
    nombre_entrada.config(validate="key", validatecommand=vcmd_nombre)
    edad_entrada.config(validate="key", validatecommand=(ventana.register(lambda P: P.isdigit() or P == ""), '%P'))
    altura_entrada.config(validate="key", validatecommand=vcmd_numerico)
    peso_entrada.config(validate="key", validatecommand=vcmd_numerico)

    # Configurar campos
    for i, (texto, entrada) in enumerate(campos, 1):
        Label(ventana, text=texto, bg="#e0f7fa", font=("Arial", 12)).grid(row=i, column=0, sticky="w", padx=10)
        entrada.grid(row=i, column=1, padx=10)

    # Género
    Label(ventana, text="Género:", bg="#e0f7fa", font=("Arial", 12)).grid(row=5, column=0, sticky="w", padx=10)
    genero_var = StringVar(value="Hombre")  # Valor por defecto vacío
    genero_menu = ttk.Combobox(ventana, textvariable=genero_var, 
                                values=["Hombre", "Mujer"], 
                                state="readonly", 
                                font=("Arial", 12))
    genero_menu.grid(row=5, column=1, padx=10)

    # Nivel de actividad
    Label(ventana, text="Nivel de actividad:", bg="#e0f7fa", font=("Arial", 12)).grid(row=6, column=0, sticky="w", padx=10)
    nivel_actividad_var = StringVar(value="Sedentario")  # Valor por defecto vacío
    nivel_actividad_menu = ttk.Combobox(ventana, 
                                        textvariable=nivel_actividad_var, 
                                        values=niveles_actividad, 
                                        state="readonly", 
                                        font=("Arial", 12))
    nivel_actividad_menu.grid(row=6, column=1, padx=10)

    # Condición de salud
    Label(ventana, text="Condición de salud:", bg="#e0f7fa", font=("Arial", 12)).grid(row=7, column=0, sticky="w", padx=10)
    condicion_var = StringVar(value="Normal")  # Valor por defecto "Normal"
    condicion_menu = ttk.Combobox(ventana, 
                                  textvariable=condicion_var, 
                                  values=condiciones_salud, 
                                  state="readonly", 
                                  font=("Arial", 12))
    condicion_menu.grid(row=7, column=1, padx=10)

    # Botón Obtener Dieta
    Button(ventana, text="Obtener Dieta", 
           command=obtener_dieta, 
           font=("Arial", 12), 
           bg="#00796b", 
           fg="white").grid(row=8, column=0, columnspan=2, pady=10)

    # Calorías objetivo
    Label(ventana, text="Calorías objetivo:", bg="#e0f7fa", font=("Arial", 12)).grid(row=9, column=0, sticky="w", padx=10)
    calorias_objetivo_var = StringVar()
    Label(ventana, textvariable=calorias_objetivo_var, bg="#e0f7fa", font=("Arial", 12)).grid(row=9, column=1)

    # Resultado de la dieta
    Label(ventana, text="Resultado de la dieta:", bg="#e0f7fa", font=("Arial", 12)).grid(row=10, column=0, columnspan=2, pady=10)

    resultado_texto = Text(ventana, height=10, width=50, font=("Arial", 12))
    resultado_texto.grid(row=11, column=0, columnspan=2, padx=10)

    # Botón Imprimir PDF
    Button(ventana, text="Imprimir PDF", 
           command=imprimir_dieta, 
           font=("Arial", 12), 
           bg="#00796b", 
           fg="white").grid(row=12, column=0, columnspan=2, pady=10)

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