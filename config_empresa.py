from db import obtener_datos_compania, guardar_datos_compania
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QTextEdit, QPushButton, QMessageBox

class ConfiguracionEmpresaDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Configuración de Empresa")
        self.setFixedSize(400, 400)
        self.campos = {
            "Nombre de la Compañía": QLineEdit(),
            "Dirección 1": QTextEdit(),
            "Dirección 2": QTextEdit(),
            "RTN": QLineEdit(),
            "Correo": QLineEdit(),
            "Teléfono": QLineEdit()
        }

        layout = QVBoxLayout(self)
        for etiqueta, campo in self.campos.items():
            layout.addWidget(QLabel(etiqueta))
            layout.addWidget(campo)

        self.btn_guardar = QPushButton("Guardar")
        self.btn_guardar.clicked.connect(self.guardar)
        layout.addWidget(self.btn_guardar)

        self.cargar_datos()

    def cargar_datos(self):
        try:
            datos = obtener_datos_compania()
            if datos:
                for campo, valor in zip(self.campos.values(), datos):
                    if isinstance(campo, QTextEdit):
                        campo.setPlainText(str(valor))
                    else:
                        campo.setText(str(valor))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudieron cargar los datos.\n{e}")

    def guardar(self):
        valores = []
        for campo in self.campos.values():
            if isinstance(campo, QTextEdit):
                valores.append(campo.toPlainText().strip())
            else:
                valores.append(campo.text().strip())
        # Aquí puedes agregar una validación especial para el RTN o teléfono si es necesario.
        if any(v == "" for v in valores):
            QMessageBox.warning(self, "Faltan datos", "Completa todos los campos.")
            return

        try:
            ok = guardar_datos_compania(valores)
            if ok:
                QMessageBox.information(self, "Guardado", "Información de empresa actualizada correctamente.")
                self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error al guardar", str(e))
