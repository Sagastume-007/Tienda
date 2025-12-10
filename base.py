import tkinter as tk
import customtkinter as ctk
import sqlite3

class EditableTableApp:
    def __init__(self, root):
        self.root = root
        self.root.geometry("600x400")
        self.root.title("Consulta por ID con SQLite")

        self.frame = ctk.CTkFrame(self.root)
        self.frame.pack(padx=20, pady=20, fill="both", expand=True)

        # Crear el campo de entrada para el ID y el botón de búsqueda
        self.id_entry = ctk.CTkEntry(self.frame, width=120)
        self.id_entry.grid(row=0, column=0, padx=5, pady=5)

        self.search_button = ctk.CTkButton(self.frame, text="Buscar", command=self.search_by_id)
        self.search_button.grid(row=0, column=1, padx=5, pady=5)

        # Etiquetas para mostrar los resultados de la consulta
        self.result_label = ctk.CTkLabel(self.frame, text="Resultado:", width=200, height=30)
        self.result_label.grid(row=1, column=0, columnspan=2, padx=5, pady=5)

        # Etiquetas donde se mostrarán los datos de la persona
        self.name_label = ctk.CTkLabel(self.frame, text="Nombre: ", width=200, height=30)
        self.name_label.grid(row=2, column=0, columnspan=2, padx=5, pady=5)

        self.age_label = ctk.CTkLabel(self.frame, text="Edad: ", width=200, height=30)
        self.age_label.grid(row=3, column=0, columnspan=2, padx=5, pady=5)

        self.city_label = ctk.CTkLabel(self.frame, text="Ciudad: ", width=200, height=30)
        self.city_label.grid(row=4, column=0, columnspan=2, padx=5, pady=5)

    def search_by_id(self):
        # Obtener el ID ingresado
        person_id = self.id_entry.get()

        # Validar que el ID sea un número
        if not person_id.isdigit():
            self.result_label.config(text="ID inválido, por favor ingrese un número.")
            return

        # Conectar a la base de datos SQLite
        conn = sqlite3.connect('mi_base_de_datos.db')
        cursor = conn.cursor()

        # Ejecutar la consulta SQL para obtener la persona por ID
        cursor.execute("SELECT nombre, edad, ciudad FROM personas WHERE id = ?", (person_id,))
        result = cursor.fetchone()

        # Verificar si se encontró un resultado
        if result:
            name, age, city = result
            self.name_label.config(text=f"Nombre: {name}")
            self.age_label.config(text=f"Edad: {age}")
            self.city_label.config(text=f"Ciudad: {city}")
            self.result_label.config(text="Resultado encontrado:")
        else:
            self.result_label.config(text="No se encontró persona con ese ID.")
            self.name_label.config(text="Nombre: ")
            self.age_label.config(text="Edad: ")
            self.city_label.config(text="Ciudad: ")

        # Cerrar la conexión a la base de datos
        conn.close()

# Crear la ventana principal
root = ctk.CTk()
app = EditableTableApp(root)

# Ejecutar la aplicación
root.mainloop()
