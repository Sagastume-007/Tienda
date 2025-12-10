import sqlite3
from db import DB_PATH, asegurar_tabla_productos_sqlite
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, QLabel,
    QTableWidget, QTableWidgetItem, QMessageBox, QFileDialog, QComboBox,
    QSizePolicy, QHeaderView, QStyledItemDelegate, QInputDialog, QListWidget
)
from PyQt5.QtCore import Qt
import os
from utils import formato_lempiras
from estilos import aplicar_estilo, aplicar_estilo_completo

class CurrencyDelegate(QStyledItemDelegate):
    def displayText(self, value, locale):
        try:
            # Si viene como QTableWidgetItem text, intentar convertir
            monto = float(value)
            return formato_lempiras(monto)
        except Exception:
            # Si no es convertible, devolver como está
            return str(value)

class GestionProductos(QDialog):
    def __init__(self, usuario=None, parent=None, embedded=False):
        super().__init__(parent)
        self.usuario = usuario
        self.setWindowTitle("Gestión de Productos")
        # Configurar para expansión completa
        self.setMinimumSize(0, 0)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        # Mostrar ajustado al área disponible si no está embebido
        if not embedded:
            try:
                from PyQt5.QtWidgets import QApplication
                desktop = QApplication.desktop()
                geom = desktop.availableGeometry(self)
                w = max(100, geom.width() - 2)
                h = max(100, geom.height() - 2)
                if hasattr(self, 'setMaximumSize'):
                    self.setMaximumSize(w, h)
                from PyQt5.QtCore import QRect, QSize
                self.setGeometry(QRect(geom.topLeft(), QSize(w, h)))
                self.showNormal()
            except Exception:
                try:
                    self.show()
                except Exception:
                    pass
        # Aplicar estilo global
        aplicar_estilo_completo(self)

        # Layout raíz: contenido a la izquierda y columna de botones a la derecha
        root_layout = QHBoxLayout(self)
        root_layout.setContentsMargins(16, 16, 16, 16)
        root_layout.setSpacing(8)
        content_layout = QVBoxLayout()
        content_layout.setSpacing(8)

        # --- Filtros de búsqueda ---
        filtros_layout = QHBoxLayout()
        self.input_busqueda = QLineEdit()
        self.input_busqueda.setPlaceholderText("🔎 Buscar por nombre o código de barras...")
        self.input_busqueda.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        aplicar_estilo(self.input_busqueda, "input_texto")
        filtros_layout.addWidget(self.input_busqueda)

        self.combo_categoria = QComboBox()
        self.combo_categoria.addItem("Todas las categorías")
        self.combo_categoria.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        aplicar_estilo(self.combo_categoria, "combobox")
        self.cargar_categorias()
        self.combo_categoria.currentTextChanged.connect(self.cargar_productos)
        filtros_layout.addWidget(self.combo_categoria)
        content_layout.addLayout(filtros_layout)

        self.input_busqueda.textChanged.connect(self.cargar_productos)

        self.tabla = QTableWidget()
        self.tabla.setSortingEnabled(True)
        self.tabla.setAlternatingRowColors(True)
        self.tabla.setColumnCount(7)
        self.tabla.setHorizontalHeaderLabels(["ID", "Nombre", "Código de barras", "Precio (L)", "ISV", "Stock", "Pesable"])
        self.tabla.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        aplicar_estilo(self.tabla, "tabla")
        content_layout.addWidget(self.tabla)

        # Ajustar tamaño de columnas para expansión completa
        self.tabla.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.tabla.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.tabla.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.tabla.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.tabla.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        self.tabla.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeToContents)
        self.tabla.horizontalHeader().setSectionResizeMode(6, QHeaderView.ResizeToContents)

        # Detectar columna de precio por encabezado y aplicar delegado de moneda
        self.idx_precio = None
        self.price_columns = []
        try:
            for i in range(self.tabla.columnCount()):
                header_item = self.tabla.horizontalHeaderItem(i)
                if header_item and "precio" in header_item.text().lower():
                    if self.idx_precio is None:
                        self.idx_precio = i
                    self.price_columns.append(i)
            for col in self.price_columns:
                self.tabla.setItemDelegateForColumn(col, CurrencyDelegate(self.tabla))
        except Exception:
            self.idx_precio = 2

        # Columna vertical de botones a la derecha (estilo consistente)
        botones = QVBoxLayout()
        botones.setSpacing(4)
        botones.setContentsMargins(0, 0, 0, 0)
        self.btn_agregar = QPushButton("➕ Agregar")
        self.btn_editar = QPushButton("✏️ Editar")
        self.btn_eliminar = QPushButton("❌ Eliminar")
        
        # Políticas de tamaño y alturas uniformes
        self.btn_agregar.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        self.btn_agregar.setFixedHeight(32)
        self.btn_editar.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        self.btn_editar.setFixedHeight(32)
        self.btn_eliminar.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        self.btn_eliminar.setFixedHeight(32)
        
        botones.addWidget(self.btn_agregar)
        botones.addWidget(self.btn_editar)
        botones.addWidget(self.btn_eliminar)
        botones.addStretch(1)

        # Estilos de botones
        aplicar_estilo(self.btn_agregar, "boton_primario")
        aplicar_estilo(self.btn_editar, "boton_secundario")
        aplicar_estilo(self.btn_eliminar, "boton_peligro")

        # Armar raíz: contenido a la izquierda (expande), botones a la derecha
        root_layout.addLayout(content_layout, 1)
        root_layout.addLayout(botones)

        self.btn_agregar.clicked.connect(self.agregar_producto)
        self.btn_editar.clicked.connect(self.editar_producto)
        self.btn_eliminar.clicked.connect(self.eliminar_producto)

        if self.usuario["rol"] not in ("admin", "cajero"):
            self.btn_agregar.hide()
            self.btn_editar.hide()
            self.btn_eliminar.hide()

        self.cargar_productos()

        # Estilos centralizados aplicados vía estilos.py

    def ensure_precio_agrandado_column(self):
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("PRAGMA table_info(productos)")
            cols = [r[1] for r in cursor.fetchall()]
            if "precio_agrandado" not in cols:
                cursor.execute("ALTER TABLE productos ADD COLUMN precio_agrandado REAL")
                conn.commit()
            # Asegurar columna de código de barras (TEXT)
            cursor.execute("PRAGMA table_info(productos)")
            cols = [r[1] for r in cursor.fetchall()]
            if "codigo_barras" not in cols:
                cursor.execute("ALTER TABLE productos ADD COLUMN codigo_barras TEXT")
                conn.commit()
            cursor.execute("PRAGMA table_info(productos)")
            cols = [r[1] for r in cursor.fetchall()]
            if "tipo" not in cols:
                cursor.execute("ALTER TABLE productos ADD COLUMN tipo TEXT")
                conn.commit()
            cursor.execute("PRAGMA table_info(productos)")
            cols = [r[1] for r in cursor.fetchall()]
            if "pesable" not in cols:
                cursor.execute("ALTER TABLE productos ADD COLUMN pesable INTEGER NOT NULL DEFAULT 0")
                conn.commit()
            cursor.execute("PRAGMA table_info(productos)")
            cols = [r[1] for r in cursor.fetchall()]
            if "stock" not in cols:
                cursor.execute("ALTER TABLE productos ADD COLUMN stock INTEGER NOT NULL DEFAULT 0")
                conn.commit()
            cursor.execute("PRAGMA table_info(productos)")
            cols = [r[1] for r in cursor.fetchall()]
            if "costo" not in cols:
                cursor.execute("ALTER TABLE productos ADD COLUMN costo REAL NOT NULL DEFAULT 0")
                conn.commit()
            cursor.execute("PRAGMA table_info(productos)")
            cols = [r[1] for r in cursor.fetchall()]
            if "proveedor" not in cols:
                cursor.execute("ALTER TABLE productos ADD COLUMN proveedor TEXT")
                conn.commit()
            conn.close()
        except Exception:
            pass

    def ensure_tabla_codigos(self):
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS producto_codigos (
                    id_producto INTEGER,
                    codigo_barras TEXT,
                    UNIQUE(codigo_barras)
                )
                """
            )
            conn.commit()
            conn.close()
        except Exception:
            pass

    def codigo_existe_global(self, codigo: str, exclude_id: int = None) -> bool:
        try:
            if not codigo:
                return False
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute("SELECT id_producto FROM productos WHERE codigo_barras = ?", (codigo,))
            r = c.fetchone()
            if r and (exclude_id is None or int(r[0]) != int(exclude_id)):
                conn.close()
                return True
            c.execute("SELECT id_producto FROM producto_codigos WHERE codigo_barras = ?", (codigo,))
            r = c.fetchone()
            conn.close()
            if r and (exclude_id is None or int(r[0]) != int(exclude_id)):
                return True
            return False
        except Exception:
            return False

    def cargar_productos(self):
        try:
            prev_sorting = self.tabla.isSortingEnabled()
        except Exception:
            prev_sorting = True
        self.tabla.setSortingEnabled(False)
        self.tabla.setRowCount(0)
        try:
            asegurar_tabla_productos_sqlite()
            self.ensure_precio_agrandado_column()
        except Exception:
            pass
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT id_producto, nombre, codigo_barras, precio, impuesto, stock, pesable FROM productos")
            rows = cursor.fetchall()
        except Exception:
            rows = []
        conn.close()
        columnas = ["id_producto","nombre","codigo_barras","precio","impuesto","stock","pesable"]
        try:
            self.idx_precio = columnas.index("precio")
        except Exception:
            self.idx_precio = 3
        for r in rows:
            try:
                pid, nombre, codigo_barras, precio, impuesto, stock_val, pesable = r
            except Exception:
                continue
            # Mapear impuesto a tag 1/2/3
            imp_str = str(impuesto or "").strip().lower()
            if imp_str in ("15","1","15%"):
                tag = 1
            elif imp_str in ("18","2","18%"):
                tag = 2
            else:
                tag = 3
            if self.coincide_filtro(nombre, None, codigo_barras, None):
                rp = self.tabla.rowCount()
                self.tabla.insertRow(rp)
                row = (pid, nombre, codigo_barras, precio, tag, stock_val, pesable)
                for col, value in enumerate(row):
                    if col == self.idx_precio:
                        it = QTableWidgetItem(str(value))
                        try:
                            it.setData(Qt.EditRole, float(value))
                        except Exception:
                            it.setData(Qt.EditRole, 0.0)
                        it.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                    elif col == 4:
                        if int(value or 0) == 1:
                            it = QTableWidgetItem("15%")
                        elif int(value or 0) == 2:
                            it = QTableWidgetItem("18%")
                        else:
                            it = QTableWidgetItem("Ex")
                    elif col == 6:
                        it = QTableWidgetItem("Sí" if int(value or 0) == 1 else "No")
                    else:
                        it = QTableWidgetItem(str(value or ""))
                    if col == 0:
                        try:
                            it.setData(Qt.UserRole, int(value))
                            it.setData(Qt.EditRole, int(value))
                        except Exception:
                            it.setData(Qt.UserRole, value)
                    self.tabla.setItem(rp, col, it)
        try:
            if prev_sorting:
                self.tabla.setSortingEnabled(True)
                self.tabla.sortItems(0, Qt.AscendingOrder)
            else:
                self.tabla.setSortingEnabled(False)
        except Exception:
            self.tabla.setSortingEnabled(True)
        try:
            self.tabla.cellDoubleClicked.disconnect()
        except Exception:
            pass
        self.tabla.cellDoubleClicked.connect(self.abrir_formulario_edicion)

    def agregar_producto(self):
        self.abrir_formulario()

    def editar_producto(self):
        fila = self.tabla.currentRow()
        if fila < 0:
            QMessageBox.warning(self, "Selecciona", "Selecciona un producto para editar.")
            return
        try:
            id_producto = int(self.tabla.item(fila, 0).text())
        except Exception:
            id_producto = self.tabla.item(fila, 0).text()
        try:
            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()
            cur.execute("SELECT id_producto, nombre, codigo_barras, precio, impuesto, pesable FROM productos WHERE id_producto = ?", (id_producto,))
            row = cur.fetchone()
            conn.close()
        except Exception:
            row = None
        if row:
            producto = {
                "id": row[0],
                "nombre": row[1],
                "codigo_barras": row[2] or "",
                "precio": row[3],
                "impuesto": str(row[4]),
                "stock": 0,
                "pesable": int(row[5] or 0)
            }
            self.abrir_formulario(producto)

    def eliminar_producto(self):
        fila = self.tabla.currentRow()
        if fila < 0:
            QMessageBox.warning(self, "Selecciona", "Selecciona un producto para eliminar.")
            return
        try:
            id_producto = int(self.tabla.item(fila, 0).text())
        except Exception:
            id_producto = self.tabla.item(fila, 0).text()
        nombre_producto = self.tabla.item(fila, 1).text()
        confirm = QMessageBox.question(
            self,
            "Confirmar eliminación",
            f"¿Estás seguro de que deseas eliminar el producto '{nombre_producto}'?",
            QMessageBox.Yes | QMessageBox.No
        )
        if confirm == QMessageBox.Yes:
            borrado = False
            try:
                conn = sqlite3.connect(DB_PATH)
                cursor = conn.cursor()
                cursor.execute("DELETE FROM productos WHERE id_producto = ?", (id_producto,))
                conn.commit()
                conn.close()
                borrado = True
            except Exception:
                borrado = False
            if borrado:
                QMessageBox.information(self, "Producto eliminado", f"El producto '{nombre_producto}' fue eliminado correctamente.")
                self.cargar_productos()
            else:
                QMessageBox.warning(self, "Error", "No se pudo eliminar el producto.")

    def cargar_categorias(self):
        self.combo_categoria.clear()
        self.combo_categoria.addItem("Todas las categorías")

    def coincide_filtro(self, nombre, categoria, codigo_barras=None, tipo=None):
        texto = self.input_busqueda.text().strip().lower()
        categoria_filtro = self.combo_categoria.currentText().strip()
        categoria_val = (categoria or "").strip()
        nombre_val = (nombre or "").strip().lower()
        codigo_val = str(codigo_barras or "").strip().lower()
        tipo_val = str(tipo or "").strip().lower()
        coincide_texto = (texto == "") or (texto in nombre_val) or (texto in codigo_val) or (texto in tipo_val)
        coincide_categoria = (categoria_filtro == "Todas las categorías" or categoria_val == categoria_filtro)
        return coincide_texto and coincide_categoria

    def abrir_formulario(self, producto=None):
        form = QDialog(self)
        form.setWindowTitle("Formulario Producto")
        form.setMinimumSize(640, 520)
        try:
            form.resize(640, 520)
        except Exception:
            pass
        form.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout = QVBoxLayout(form)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)

        input_nombre = QLineEdit()
        input_nombre.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        input_precio = QLineEdit()
        input_precio.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        combo_impuesto = QComboBox()
        combo_impuesto.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        combo_impuesto.addItems(["Exento", "15", "18"])
        input_codigo_barras = QLineEdit()
        input_codigo_barras.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        input_stock = QLineEdit()
        input_stock.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        input_pesable = QComboBox()
        input_pesable.addItems(["No", "Sí"])

        layout.addWidget(QLabel("Nombre:"))
        layout.addWidget(input_nombre)
        layout.addWidget(QLabel("Precio:"))
        layout.addWidget(input_precio)
        layout.addWidget(QLabel("Impuesto:"))
        layout.addWidget(combo_impuesto)
        layout.addWidget(QLabel("Código de barras (opcional):"))
        layout.addWidget(input_codigo_barras)
        layout.addWidget(QLabel("Stock:"))
        layout.addWidget(input_stock)
        layout.addWidget(QLabel("Pesable:"))
        layout.addWidget(input_pesable)


        if producto:
            input_nombre.setText(producto["nombre"])
            # Mostrar precio con dos decimales en el formulario (sin prefijo L para facilitar edición)
            try:
                input_precio.setText(f"{float(producto['precio']):.2f}")
            except Exception:
                input_precio.setText(str(producto["precio"]))
            combo_impuesto.setCurrentText("18" if str(producto.get("impuesto",""))=="2" else ("15" if str(producto.get("impuesto",""))=="1" else "Exento"))
            input_codigo_barras.setText(producto.get("codigo_barras", ""))
            try:
                input_stock.setText(str(int(producto.get("stock",0))))
            except Exception:
                input_stock.setText(str(producto.get("stock",0)))
            input_pesable.setCurrentText("Sí" if int(producto.get("pesable",0))==1 else "No")

        def guardar():
            nombre = input_nombre.text().strip()
            precio = input_precio.text().strip()
            impuesto = combo_impuesto.currentText()
            codigo_barras = input_codigo_barras.text().strip()
            stock_txt = input_stock.text().strip()
            pesable_txt = input_pesable.currentText().strip()

            if not nombre or not precio:
                QMessageBox.warning(form, "Campos incompletos", "Completa todos los campos obligatorios.")
                return
            try:
                precio = float(precio)
            except ValueError:
                QMessageBox.warning(form, "Precio inválido", "El precio debe ser un número.")
                return
            try:
                stock_val = int(stock_txt or "0")
            except Exception:
                stock_val = 0
            pesable_val = 1 if pesable_txt.lower().startswith("s") else 0

            try:
                pid_excl = producto["id"] if producto else None
            except Exception:
                pid_excl = None
            if codigo_barras:
                if self.codigo_existe_global(codigo_barras, exclude_id=pid_excl):
                    QMessageBox.warning(form, "Código duplicado", "El código de barras ya existe en otro producto.")
                    return
            try:
                conn = sqlite3.connect(DB_PATH)
                cur = conn.cursor()
                imp_tag = 1 if impuesto.startswith("15") else (2 if impuesto.startswith("18") else 3)
                if producto:
                    cur.execute(
                        "UPDATE productos SET nombre=?, codigo_barras=?, precio=?, impuesto=?, pesable=? WHERE id_producto=?",
                        (nombre, codigo_barras or None, float(precio), imp_tag, int(pesable_val), producto["id"]) 
                    )
                else:
                    cur.execute(
                        "INSERT INTO productos (nombre, codigo_barras, precio, impuesto, pesable) VALUES (?,?,?,?,?)",
                        (nombre, codigo_barras or None, float(precio), imp_tag, int(pesable_val))
                    )
                conn.commit()
                conn.close()
            except Exception as e:
                QMessageBox.warning(form, "BD", f"No se pudo guardar en SQLite: {e}")
                return
            form.accept()
            self.cargar_productos()

        btn_guardar = QPushButton("Guardar")
        btn_guardar.clicked.connect(guardar)
        layout.addWidget(btn_guardar)

        form.setStyleSheet("""
            QDialog {
                background-color: #ffffff;
                border-radius: 12px;
            }
            QLabel {
                font-weight: bold;
                color: #2c3e50;
                margin-top: 10px;
            }
            QLineEdit, QComboBox {
                background-color: #f8f9f9;
                padding: 8px;
                border-radius: 8px;
                border: 1px solid #ccc;
            }
            QPushButton {
                background-color: #58d68d;
                color: white;
                font-weight: bold;
                border-radius: 8px;
                padding: 8px;
            }
            QPushButton:hover {
                background-color: #28b463;
            }
        """)
        form.exec_()

    def abrir_formulario_edicion(self, row, column):
        try:
            # Establecer la fila actual y delegar en el método existente de edición
            self.tabla.setCurrentCell(row, column)
            self.editar_producto()
        except Exception:
            pass

    def abrir_ventas_para_producto(self, row, column):
        try:
            # Obtener datos básicos del producto seleccionado
            item_id = self.tabla.item(row, 0)
            item_nombre = self.tabla.item(row, 1)
            # Precio: usar el índice detectado dinámicamente
            precio_col = self.idx_precio if self.idx_precio is not None else 3
            item_precio = self.tabla.item(row, precio_col)

            if not item_id or not item_nombre or not item_precio:
                return

            nombre = item_nombre.text()
            try:
                precio = float(item_precio.text())
            except Exception:
                # Intentar obtener el EditRole si el texto está formateado
                precio = float(item_precio.data(Qt.EditRole) or 0.0)

            # Import local para evitar importación circular al inicio del módulo
            from ventas import RestauranteApp
            # Instanciar ventana de ventas con el usuario actual
            self.venta_window = RestauranteApp(usuario=self.usuario)
            self.venta_window.show()
            try:
                # Agregar el producto al pedido para edición inmediata
                self.venta_window.agregar_producto(nombre, precio)
                self.venta_window.raise_()
                self.venta_window.activateWindow()
            except Exception:
                pass
        except Exception:
            pass
