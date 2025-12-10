# estilo.py

# 🎨 Colores con más contraste y estilo profesional
COLOR_FONDO_GENERAL = "#F5F7FA"
COLOR_FONDO_FRAME = "#FFFFFF"
COLOR_PRIMARIO = "#007BFF"          # Azul principal
COLOR_SECUNDARIO = "#5BC0DE"        # Azul celeste
COLOR_TEXTO = "#212529"             # Gris oscuro casi negro
COLOR_HOVER = "#0056b3"             # Hover para azul
COLOR_BOTON = "#ffff52"             # Verde positivo
COLOR_BOTON_HOVER = "#218838"       # Hover verde
COLOR_PELIGRO = "#DC3545"           # Rojo de advertencia
COLOR_PELIGRO_HOVER = "#C82333"     # Hover rojo
COLOR_EXITO = "#28A745"             # Mismo verde para éxito
COLOR_EXITO_HOVER = "#218838"       # Hover verde oscuro

# 🅰️ Fuentes (definidas como tuplas, no CTkFont)
FUENTE_GENERAL = ("Quicksand", 12, "bold")
FUENTE_TITULO = ("Poppins", 30, "bold")
FUENTE_SUBTITULO = ("Quicksand", 18, "bold")
FUENTE_BOTON = ("Quicksand", 14, "bold")
FUENTE_LABEL_TOTAL = ("Quicksand", 16, "bold")
FUENTE_VALOR_TOTAL = ("Quicksand", 18, "bold")

# ✅ Estilo de botones estándar
ESTILO_BOTON = {
    "fg_color": COLOR_BOTON,
    "text_color": "black",
    "hover_color": COLOR_BOTON_HOVER,
    "corner_radius": 10,
    "width": 140,
    "height": 50,
    "font": FUENTE_BOTON
}

# ⚠️ Estilo de botones de eliminar
ESTILO_BOTON_PELIGRO = {
    "fg_color": COLOR_PELIGRO,
    "text_color": "white",
    "hover_color": COLOR_PELIGRO_HOVER,
    "corner_radius": 10,
    "width": 140,
    "height": 50,
    "font": FUENTE_BOTON
}

# ✅ Estilo de botones de acción verde (éxito)
ESTILO_BOTON_EXITO = {
    "fg_color": COLOR_EXITO,
    "text_color": "white",
    "hover_color": COLOR_EXITO_HOVER,
    "corner_radius": 10,
    "width": 140,
    "height": 50,
    "font": FUENTE_BOTON
}
