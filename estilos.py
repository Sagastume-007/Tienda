"""
Módulo de estilos para la aplicación de restaurante
Proporciona funciones y constantes para mantener un diseño consistente
"""

import os
from PyQt5.QtWidgets import QWidget, QGraphicsDropShadowEffect
from PyQt5.QtGui import QColor
from PyQt5.QtCore import Qt, QSize

# ============================================
# PALETA DE COLORES PRINCIPAL
# ============================================

COLORES = {
    # Colores primarios
    "primario": "#74c69d",
    "primario_hover": "#52b788",
    "primario_oscuro": "#2d6a4f",
    
    # Colores secundarios
    "secundario": "#a8dadc",
    "secundario_hover": "#90e0ef",
    "secundario_oscuro": "#457b9d",
    
    # Colores de acento
    "acento": "#fcbf49",
    "acento_hover": "#f77f00",
    
    # Colores de fondo
    "fondo": "#fdf6f0",
    "fondo_claro": "#ffffff",
    "fondo_oscuro": "#f1faee",
    "fondo_tarjeta": "#f8f9fa",
    
    # Colores de texto
    "texto": "#2c3e50",
    "texto_secundario": "#6c757d",
    "texto_claro": "#ffffff",
    
    # Colores de estado
    "exito": "#52b788",
    "advertencia": "#fcbf49",
    "peligro": "#e63946",
    "info": "#457b9d",
    
    # Colores de bordes
    "borde": "#ced4da",
    "borde_claro": "#dee2e6",
    "borde_oscuro": "#adb5bd",
    
    # Colores adicionales
    "gris_claro": "#e9ecef",
    "gris_medio": "#6c757d",
    "gris_oscuro": "#343a40",
}

# ============================================
# ESTILOS PREDEFINIDOS
# ============================================

ESTILOS = {
    "boton_primario": f"""
        QPushButton {{
            background-color: {COLORES['primario']};
            color: white;
            border: none;
            border-radius: 8px;
            padding: 8px 16px;
            font-weight: bold;
            font-size: 10pt;
        }}
        QPushButton:hover {{
            background-color: {COLORES['primario_hover']};
        }}
        QPushButton:pressed {{
            background-color: {COLORES['primario_oscuro']};
        }}
        QPushButton:disabled {{
            background-color: {COLORES['gris_claro']};
            color: {COLORES['gris_medio']};
        }}
    """,
    
    "boton_secundario": f"""
        QPushButton {{
            background-color: {COLORES['secundario']};
            color: {COLORES['texto']};
            border: none;
            border-radius: 8px;
            padding: 8px 16px;
            font-weight: bold;
            font-size: 10pt;
        }}
        QPushButton:hover {{
            background-color: {COLORES['secundario_hover']};
        }}
        QPushButton:pressed {{
            background-color: {COLORES['secundario_oscuro']};
            color: white;
        }}
        QPushButton:disabled {{
            background-color: {COLORES['gris_claro']};
            color: {COLORES['gris_medio']};
        }}
    """,
    
    "boton_peligro": f"""
        QPushButton {{
            background-color: {COLORES['peligro']};
            color: white;
            border: none;
            border-radius: 8px;
            padding: 8px 16px;
            font-weight: bold;
            font-size: 10pt;
        }}
        QPushButton:hover {{
            background-color: #d62828;
        }}
        QPushButton:pressed {{
            background-color: #9d0208;
        }}
        QPushButton:disabled {{
            background-color: {COLORES['gris_claro']};
            color: {COLORES['gris_medio']};
        }}
    """,
    
    "boton_exito": f"""
        QPushButton {{
            background-color: {COLORES['exito']};
            color: white;
            border: none;
            border-radius: 8px;
            padding: 8px 16px;
            font-weight: bold;
            font-size: 10pt;
        }}
        QPushButton:hover {{
            background-color: #40916c;
        }}
        QPushButton:pressed {{
            background-color: {COLORES['primario_oscuro']};
        }}
        QPushButton:disabled {{
            background-color: {COLORES['gris_claro']};
            color: {COLORES['gris_medio']};
        }}
    """,

    "boton_agregar": f"""
        QPushButton {{
            background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:0, y2:1,
                                              stop:0 {COLORES['primario']},
                                              stop:1 {COLORES['primario_hover']});
            color: white;
            border: 2px solid {COLORES['borde_claro']};
            border-radius: 999px;
            padding: 12px 20px;
            font-weight: 600;
            font-size: 11pt;
        }}
        QPushButton:hover {{
            background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:0, y2:1,
                                              stop:0 {COLORES['primario_hover']},
                                              stop:1 {COLORES['primario']});
            border-color: {COLORES['primario']};
        }}
        QPushButton:pressed {{
            background-color: {COLORES['primario_oscuro']};
        }}
        QPushButton:disabled {{
            background-color: {COLORES['gris_claro']};
            color: {COLORES['gris_medio']};
        }}
    """,
    
    "boton_menu": f"""
        QPushButton {{
            background-color: {COLORES['secundario']};
            color: {COLORES['texto']};
            border: 1px solid {COLORES['borde']};
            border-radius: 10px;
            padding: 10px;
            text-align: left;
            font-weight: bold;
        }}
        QPushButton:hover {{
            background-color: {COLORES['acento']};
        }}
        QPushButton:pressed {{
            background-color: {COLORES['acento_hover']};
        }}
    """,
    
    "input_texto": f"""
        QLineEdit, QTextEdit, QPlainTextEdit {{
            background-color: white;
            border: 1px solid {COLORES['borde_claro']};
            border-radius: 10px;
            padding: 10px;
            font-size: 10pt;
            color: {COLORES['texto']};
        }}
        QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {{
            border: 2px solid {COLORES['primario']};
        }}
        QLineEdit:disabled, QTextEdit:disabled, QPlainTextEdit:disabled {{
            background-color: {COLORES['gris_claro']};
            color: {COLORES['gris_medio']};
        }}
    """,
    
    "tabla": f"""
        QTableWidget {{
            background-color: white;
            border: 1px solid {COLORES['borde']};
            border-radius: 8px;
            gridline-color: {COLORES['borde_claro']};
            font-size: 10pt;
        }}
        QTableWidget::item {{
            padding: 5px;
        }}
        QTableWidget::item:selected {{
            background-color: {COLORES['primario']};
            color: white;
        }}
        QHeaderView::section {{
            background-color: {COLORES['fondo_oscuro']};
            color: {COLORES['texto']};
            padding: 8px;
            border: none;
            border-bottom: 2px solid {COLORES['primario']};
            font-weight: bold;
        }}
    """,
    
    "combobox": f"""
        QComboBox {{
            background-color: white;
            border: 2px solid {COLORES['borde']};
            border-radius: 6px;
            padding: 8px;
            font-size: 10pt;
            color: {COLORES['texto']};
        }}
        QComboBox:hover {{
            border-color: {COLORES['primario']};
        }}
        QComboBox::drop-down {{
            border: none;
            width: 30px;
        }}
        QComboBox::down-arrow {{
            image: none;
            border-left: 5px solid transparent;
            border-right: 5px solid transparent;
            border-top: 5px solid {COLORES['texto']};
            margin-right: 10px;
        }}
        QComboBox QAbstractItemView {{
            background-color: white;
            border: 1px solid {COLORES['borde']};
            selection-background-color: {COLORES['primario']};
            selection-color: white;
        }}
    """,
    
    "spinbox": f"""
        QSpinBox, QDoubleSpinBox {{
            background-color: white;
            border: 2px solid {COLORES['borde']};
            border-radius: 6px;
            padding: 8px;
            font-size: 10pt;
            color: {COLORES['texto']};
        }}
        QSpinBox:focus, QDoubleSpinBox:focus {{
            border-color: {COLORES['primario']};
        }}
        QSpinBox::up-button, QDoubleSpinBox::up-button {{
            background-color: {COLORES['fondo_claro']};
            border-left: 1px solid {COLORES['borde']};
            border-bottom: 1px solid {COLORES['borde']};
        }}
        QSpinBox::down-button, QDoubleSpinBox::down-button {{
            background-color: {COLORES['fondo_claro']};
            border-left: 1px solid {COLORES['borde']};
        }}
    """,
    
    "checkbox": f"""
        QCheckBox {{
            spacing: 8px;
            color: {COLORES['texto']};
        }}
        QCheckBox::indicator {{
            width: 20px;
            height: 20px;
            border: 2px solid {COLORES['borde']};
            border-radius: 4px;
            background-color: white;
        }}
        QCheckBox::indicator:hover {{
            border-color: {COLORES['primario']};
        }}
        QCheckBox::indicator:checked {{
            background-color: {COLORES['primario']};
            border-color: {COLORES['primario']};
        }}
    """,
    
    "radio": f"""
        QRadioButton {{
            spacing: 8px;
            color: {COLORES['texto']};
        }}
        QRadioButton::indicator {{
            width: 20px;
            height: 20px;
            border: 2px solid {COLORES['borde']};
            border-radius: 10px;
            background-color: white;
        }}
        QRadioButton::indicator:hover {{
            border-color: {COLORES['primario']};
        }}
        QRadioButton::indicator:checked {{
            background-color: {COLORES['primario']};
            border-color: {COLORES['primario']};
        }}
    """,
}

# ============================================
# FUNCIONES PRINCIPALES
# ============================================

def obtener_color(nombre_color: str) -> str:
    """
    Obtiene un color de la paleta
    
    Args:
        nombre_color: Nombre del color en la paleta
        
    Returns:
        Código hexadecimal del color
    """
    return COLORES.get(nombre_color, COLORES['texto'])


def aplicar_estilo(widget: QWidget, tipo_estilo: str):
    """
    Aplica un estilo predefinido a un widget
    
    Args:
        widget: Widget al que aplicar el estilo
        tipo_estilo: Tipo de estilo a aplicar
    """
    if tipo_estilo in ESTILOS:
        widget.setStyleSheet(ESTILOS[tipo_estilo])


def aplicar_estilo_completo(ventana: QWidget):
    """
    Aplica el estilo base completo a una ventana
    
    Args:
        ventana: Ventana principal a la que aplicar el estilo
    """
    estilo_base = f"""
        QMainWindow, QDialog, QWidget {{
            background-color: {COLORES['fondo']};
            color: {COLORES['texto']};
            font-family: 'Segoe UI', Arial, sans-serif;
            font-size: 10pt;
        }}
        
        QLabel {{
            color: {COLORES['texto']};
            background-color: transparent;
        }}
        
        QFrame {{
            border-radius: 8px;
        }}
        
        QMenuBar {{
            background-color: {COLORES['fondo_oscuro']};
            color: {COLORES['texto']};
            border-bottom: 2px solid {COLORES['primario']};
            padding: 4px;
        }}
        
        QMenuBar::item {{
            background-color: transparent;
            padding: 6px 12px;
            border-radius: 4px;
        }}
        
        QMenuBar::item:selected {{
            background-color: {COLORES['primario']};
            color: white;
        }}
        
        QMenu {{
            background-color: white;
            border: 1px solid {COLORES['borde']};
            border-radius: 4px;
            padding: 4px;
        }}
        
        QMenu::item {{
            padding: 8px 24px;
            border-radius: 4px;
        }}
        
        QMenu::item:selected {{
            background-color: {COLORES['primario']};
            color: white;
        }}
        
        QScrollBar:vertical {{
            background-color: {COLORES['fondo_claro']};
            width: 12px;
            border-radius: 6px;
        }}
        
        QScrollBar::handle:vertical {{
            background-color: {COLORES['secundario']};
            border-radius: 6px;
            min-height: 20px;
        }}
        
        QScrollBar::handle:vertical:hover {{
            background-color: {COLORES['primario']};
        }}
        
        QScrollBar:horizontal {{
            background-color: {COLORES['fondo_claro']};
            height: 12px;
            border-radius: 6px;
        }}
        
        QScrollBar::handle:horizontal {{
            background-color: {COLORES['secundario']};
            border-radius: 6px;
            min-width: 20px;
        }}
        
        QScrollBar::handle:horizontal:hover {{
            background-color: {COLORES['primario']};
        }}
        
        QToolTip {{
            background-color: {COLORES['texto']};
            color: white;
            border: 1px solid {COLORES['borde_oscuro']};
            border-radius: 4px;
            padding: 4px;
        }}
    """
    
    ventana.setStyleSheet(estilo_base)


def crear_efecto_sombra(widget: QWidget, blur_radius: int = 10, offset_x: int = 0, offset_y: int = 2, color: str = None):
    """
    Crea un efecto de sombra para un widget
    
    Args:
        widget: Widget al que aplicar la sombra
        blur_radius: Radio de desenfoque de la sombra
        offset_x: Desplazamiento horizontal
        offset_y: Desplazamiento vertical
        color: Color de la sombra (opcional)
    """
    efecto = QGraphicsDropShadowEffect()
    efecto.setBlurRadius(blur_radius)
    efecto.setOffset(offset_x, offset_y)
    
    if color:
        efecto.setColor(QColor(color))
    else:
        efecto.setColor(QColor(0, 0, 0, 50))
    
    widget.setGraphicsEffect(efecto)


def obtener_estilo_tarjeta(color_fondo: str = None, borde: bool = True) -> str:
    """
    Genera un estilo CSS para una tarjeta/frame
    
    Args:
        color_fondo: Color de fondo (opcional)
        borde: Si debe tener borde o no
        
    Returns:
        String con el estilo CSS
    """
    fondo = color_fondo if color_fondo else COLORES['fondo_tarjeta']
    borde_str = f"border: 1px solid {COLORES['borde']};" if borde else "border: none;"
    
    return f"""
        QFrame {{
            background-color: {fondo};
            {borde_str}
            border-radius: 12px;
            padding: 12px;
        }}
    """


def obtener_estilo_boton_personalizado(
    color_fondo: str,
    color_hover: str,
    color_texto: str = "white",
    border_radius: int = 8
) -> str:
    """
    Genera un estilo personalizado para un botón
    
    Args:
        color_fondo: Color de fondo del botón
        color_hover: Color al pasar el mouse
        color_texto: Color del texto
        border_radius: Radio del borde redondeado
        
    Returns:
        String con el estilo CSS
    """
    return f"""
        QPushButton {{
            background-color: {color_fondo};
            color: {color_texto};
            border: none;
            border-radius: {border_radius}px;
            padding: 8px 16px;
            font-weight: bold;
            font-size: 10pt;
        }}
        QPushButton:hover {{
            background-color: {color_hover};
        }}
        QPushButton:pressed {{
            background-color: {color_fondo};
            padding: 9px 15px 7px 17px;
        }}
        QPushButton:disabled {{
            background-color: {COLORES['gris_claro']};
            color: {COLORES['gris_medio']};
        }}
    """


# ============================================
# ESTILOS PARA COMPONENTES ESPECÍFICOS
# ============================================

def obtener_estilo_grupo(titulo: str = "") -> str:
    """Estilo para QGroupBox"""
    return f"""
        QGroupBox {{
            background-color: {COLORES['fondo_tarjeta']};
            border: 2px solid {COLORES['borde']};
            border-radius: 8px;
            margin-top: 12px;
            padding-top: 12px;
            font-weight: bold;
        }}
        QGroupBox::title {{
            subcontrol-origin: margin;
            subcontrol-position: top left;
            padding: 4px 8px;
            background-color: {COLORES['primario']};
            color: white;
            border-radius: 4px;
            left: 10px;
        }}
    """


def obtener_estilo_pestanas() -> str:
    """Estilo para QTabWidget"""
    return f"""
        QTabWidget::pane {{
            border: 1px solid {COLORES['borde']};
            border-radius: 8px;
            background-color: white;
            top: -1px;
        }}
        
        QTabBar::tab {{
            background-color: {COLORES['fondo_tarjeta']};
            border: 1px solid {COLORES['borde']};
            border-bottom: none;
            border-top-left-radius: 8px;
            border-top-right-radius: 8px;
            padding: 8px 16px;
            margin-right: 2px;
        }}
        
        QTabBar::tab:selected {{
            background-color: white;
            border-bottom: 2px solid {COLORES['primario']};
        }}
        
        QTabBar::tab:hover:!selected {{
            background-color: {COLORES['secundario']};
        }}
    """


def estilizar_boton_menu(boton, texto: str = None, icono_path: str = None, tamano_icono: int = 24, padding_left: int = None, variante: str = None):
    """
    Estiliza un botón de menú con diseño moderno y consistente
    
    Args:
        boton: El botón QPushButton a estilizar
        texto: Texto del botón (opcional)
        icono_path: Ruta opcional al archivo de icono
        tamano_icono: Tamaño del icono en píxeles
        padding_left: Padding izquierdo opcional
        variante: Variante de estilo ('danger', etc.)
    """
    from PyQt5.QtGui import QIcon, QPixmap
    from PyQt5.QtCore import Qt
    
    # Establecer el texto del botón si se proporciona
    if texto:
        boton.setText(texto)
    
    # Configurar el estilo del botón
    estilo = ESTILOS['boton_menu']
    
    # Aplicar variante de estilo si se especifica
    if variante == 'danger':
        estilo = estilo.replace(ESTILOS['boton_menu'], ESTILOS['boton_peligro'])
    
    # Aplicar padding personalizado si se especifica
    if padding_left is not None:
        estilo = estilo.replace('padding: 10px;', f'padding: 10px 10px 10px {padding_left}px;')
    
    boton.setStyleSheet(estilo)
    
    # Si se proporciona un icono, configurarlo
    if icono_path and os.path.exists(icono_path):
        try:
            icono = QIcon(icono_path)
            boton.setIcon(icono)
            boton.setIconSize(QSize(tamano_icono, tamano_icono))
        except Exception:
            pass
    
    # Configurar propiedades adicionales
    boton.setCursor(Qt.PointingHandCursor)
    boton.setMinimumHeight(40)
    boton.setMaximumHeight(60)

def aplicar_escala_ui(ventana, base_w=1280, base_h=1024, embedded=False):
    try:
        from PyQt5.QtWidgets import QApplication
        desktop = QApplication.desktop()
        avail = desktop.availableGeometry(ventana)
        margen = 8
        try:
            s = min(avail.width() / float(base_w), avail.height() / float(base_h))
            if not s or s <= 0:
                s = 1.0
        except Exception:
            s = 1.0
        try:
            ventana.ui_scale = s
        except Exception:
            pass
        if not embedded:
            target_w = int(min(avail.width() - margen, base_w))
            target_h = int(min(avail.height() - margen, base_h))
            try:
                ventana.setWindowState(Qt.WindowNoState)
            except Exception:
                pass
            try:
                ventana.move(avail.topLeft())
                ventana.resize(max(300, target_w), max(300, target_h))
            except Exception:
                pass
    except Exception:
        pass