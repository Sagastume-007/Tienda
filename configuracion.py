
import sqlite3
from db import DB_PATH
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QMessageBox, QListWidget, QPushButton
from config_empresa import ConfiguracionEmpresaDialog
from seguridad import buscar_unidad_por_etiqueta

def abrir_configuracion_empresa(parent):
    if buscar_unidad_por_etiqueta(etiqueta="INSTALADOR"):
        dialog = ConfiguracionEmpresaDialog(parent)
        dialog.exec_()
    else:
        QMessageBox.information(parent, "Configuración", "Llave INSTALADOR no detectada.")

def abrir_gestion_productos(parent):
    try:
        from productos import GestionProductos
        dialog = GestionProductos(parent)
        dialog.exec_()
    except Exception:
        QMessageBox.information(parent, "Productos", "Módulo de productos no disponible.")

def abrir_gestion_usuarios(parent):
    dialog = QDialog(parent)
    dialog.setWindowTitle("Gestión de Usuarios")
    dialog.setFixedSize(400, 300)
    layout = QVBoxLayout(dialog)

    lista = QListWidget()
    layout.addWidget(lista)

    def cargar_usuarios():
        lista.clear()
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT id_usuario, nombre, usuario FROM usuarios ORDER BY id_usuario")
        for row in cursor.fetchall():
            lista.addItem(f"{row[0]} | {row[1]} ({row[2]})")
        conn.close()

    cargar_usuarios()

    btn_eliminar = QPushButton("Eliminar Seleccionado")
    def eliminar_usuario():
        item = lista.currentItem()
        if not item:
            QMessageBox.warning(dialog, "Selecciona un usuario", "Primero selecciona un usuario de la lista.")
            return
        id_usuario = int(item.text().split("|")[0].strip())
        confirm = QMessageBox.question(dialog, "Eliminar", "¿Estás seguro de eliminar este usuario?", QMessageBox.Yes | QMessageBox.No)
        if confirm == QMessageBox.Yes:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM usuarios WHERE id_usuario = ?", (id_usuario,))
            conn.commit()
            conn.close()
            cargar_usuarios()

    btn_eliminar.clicked.connect(eliminar_usuario)
    layout.addWidget(btn_eliminar)

    dialog.exec_()