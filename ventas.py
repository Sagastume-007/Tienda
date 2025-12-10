from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QLineEdit, QComboBox, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QFrame, QMessageBox, QAbstractItemView, QDialog, QDialogButtonBox, QCheckBox, QSizePolicy, QShortcut, QCompleter, QStyledItemDelegate, QSplitter
from PyQt5.QtGui import QFont, QIcon, QKeySequence
from PyQt5.QtCore import Qt, QSize, QTimer, QStringListModel
from datetime import datetime
from db import obtener_productos, obtener_info_producto, verificar_stock, conectar_mysql, sembrar_productos_iniciales, insertar_venta, insertar_factura_resumen, asegurar_tabla_ventas_sqlite, asegurar_tabla_facturas_sqlite, actualizar_stock, conectar, obtener_max_factura

class VentasWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Ventas")
        self.setMinimumSize(1120, 680)
        self.showMaximized()
        self.setStyleSheet(
            "QWidget{background:#F5F7FA;font-family:'Segoe UI';font-size:12pt;color:#1F2937}"
            "QFrame{background:#FFFFFF;border-radius:12px;border:1px solid #E5E7EB}"
            "QFrame#header{background:#E0F7F4;border:none}"
            
            "QFrame#cardProductos{background:#FFF7E9;border:2px solid #F59E0B}"
            "QLabel#titulo{color:#2D9CDB;font-size:22pt;font-weight:bold}"
            "QLabel.seccion{color:#2D9CDB;font-size:14pt;font-weight:bold}"
            "QLabel{background-color: transparent; border: none;}"
            "QLineEdit,QComboBox{background:#FFFFFF;border:1px solid #E5E7EB;border-radius:8px;padding:6px}"
            "QPushButton{background:#2D9CDB;color:white;border-radius:10px;padding:8px 14px;font-weight:bold}"
            "QPushButton:hover{background:#1B7DBF}"
            "QTableWidget{background:#FFFFFF;border:none;gridline-color:#E5E7EB}"
            "QHeaderView::section{background:#FFF9E6;border:none;padding:6px;font-weight:bold;color:#2E7D32}"
        )
        self.numero_factura_actual = 1
        self.total = 0.0
        self._updating = False
        try:
            sembrar_productos_iniciales()
        except Exception:
            pass
        self.build_ui()
        self.insertar_fila_blanco()
        

        try:
            QTimer.singleShot(300, self._focus_codigo)
        except Exception:
            pass
        try:
            QTimer.singleShot(400, self._ajustar_splitter)
        except Exception:
            pass

    def showEvent(self, event):
        try:
            super().showEvent(event)
        except Exception:
            pass

    def focusInEvent(self, event):
        try:
            super().focusInEvent(event)
        except Exception:
            pass

    def format_currency(self, value):
        return f"L {value:,.2f}"

    def parse_currency(self, text):
        try:
            return float(str(text).replace('L', '').replace(',', '').strip())
        except Exception:
            return 0.0

    def format_isv(self, isv):
        val = str(isv).strip().upper()
        if val in ("15", "15.0", "1"):
            return "15%"
        if val in ("18", "18.0", "2"):
            return "18%"
        if val in ("E", "EX", "EXENTO", "3"):
            return "Ex"
        return "Ex"

    def build_ui(self):
        root = QVBoxLayout(self)
        header = QFrame(self)
        header.setObjectName("header")
        header.setFixedHeight(120)
        hl = QHBoxLayout(header)
        titulo = QLabel("Ventas", header)
        titulo.setObjectName("titulo")
        titulo.setAlignment(Qt.AlignCenter)
        hl.addWidget(titulo, 1)
        hl.addStretch(1)
        self.lbl_total = QLabel("Total L: 0.00", header)
        
        self.lbl_total.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.lbl_total.setStyleSheet(
            "background:#FFE5F0;"            # Rosa pastel suave
            "border:3px solid #B19CD9;"      # ⬅️ Morado pastel/lila
            "border-radius:14px;"
            "padding:12px 24px;"
            "color:#B19CD9;"                 # ⬅️ Morado pastel
            "font-family:'Impact';"
            "font-size:58pt;"
            "font-weight:bold;"
            "letter-spacing: 2px;"
        )
        hl.addWidget(self.lbl_total)
        root.addWidget(header)

        contenido = QVBoxLayout()

        botones = QVBoxLayout()
        self.btn_pagar = QPushButton("", self)
        self.btn_eliminar = QPushButton("", self)
        self.btn_limpiar = QPushButton("", self)
        self.btn_productos = QPushButton("", self)
        icon_size = QSize(72, 72)
        for b in (self.btn_pagar, self.btn_eliminar, self.btn_limpiar, self.btn_productos):
            b.setFixedSize(88, 88)
            b.setStyleSheet("background: transparent; border: none; padding: 0;")
        self.btn_pagar.setIcon(QIcon("iconos/pagar.png")); self.btn_pagar.setIconSize(icon_size); self.btn_pagar.setToolTip("Pagar")
        self.btn_eliminar.setIcon(QIcon("iconos/eliminar.png")); self.btn_eliminar.setIconSize(icon_size); self.btn_eliminar.setToolTip("Eliminar item")
        self.btn_limpiar.setIcon(QIcon("iconos/limpiar.png")); self.btn_limpiar.setIconSize(icon_size); self.btn_limpiar.setToolTip("Limpiar todo")
        self.btn_productos.setIcon(QIcon("iconos/productos.svg")); self.btn_productos.setIconSize(icon_size); self.btn_productos.setToolTip("Productos")
        cont_pagar = QWidget()
        lay_pagar = QVBoxLayout(cont_pagar)
        lay_pagar.setContentsMargins(0, 0, 0, 0)
        lay_pagar.setSpacing(0)
        lay_pagar.addWidget(self.btn_pagar, alignment=Qt.AlignHCenter)
        lbl_pagar = QLabel("Pagar")
        lbl_pagar.setAlignment(Qt.AlignHCenter)
        lbl_pagar.setStyleSheet("color:#333;font-size:12px;font-weight:bold;margin-top:2px;")
        lay_pagar.addWidget(lbl_pagar)
        botones.addWidget(cont_pagar)

        cont_eliminar = QWidget()
        lay_eliminar = QVBoxLayout(cont_eliminar)
        lay_eliminar.setContentsMargins(0, 0, 0, 0)
        lay_eliminar.setSpacing(0)
        lay_eliminar.addWidget(self.btn_eliminar, alignment=Qt.AlignHCenter)
        lbl_eliminar = QLabel("Eliminar")
        lbl_eliminar.setAlignment(Qt.AlignHCenter)
        lbl_eliminar.setStyleSheet("color:#333;font-size:12px;font-weight:bold;margin-top:2px;")
        lay_eliminar.addWidget(lbl_eliminar)
        botones.addWidget(cont_eliminar)

        cont_limpiar = QWidget()
        lay_limpiar = QVBoxLayout(cont_limpiar)
        lay_limpiar.setContentsMargins(0, 0, 0, 0)
        lay_limpiar.setSpacing(0)
        lay_limpiar.addWidget(self.btn_limpiar, alignment=Qt.AlignHCenter)
        lbl_limpiar = QLabel("Limpiar")
        lbl_limpiar.setAlignment(Qt.AlignHCenter)
        lbl_limpiar.setStyleSheet("color:#333;font-size:12px;font-weight:bold;margin-top:2px;")
        lay_limpiar.addWidget(lbl_limpiar)
        botones.addWidget(cont_limpiar)
        cont_productos = QWidget()
        lay_productos = QVBoxLayout(cont_productos)
        lay_productos.setContentsMargins(0, 0, 0, 0)
        lay_productos.setSpacing(0)
        lay_productos.addWidget(self.btn_productos, alignment=Qt.AlignHCenter)
        lbl_productos = QLabel("Productos")
        lbl_productos.setAlignment(Qt.AlignHCenter)
        lbl_productos.setStyleSheet("color:#333;font-size:12px;font-weight:bold;margin-top:2px;")
        lay_productos.addWidget(lbl_productos)
        botones.addWidget(cont_productos)
        botones.addStretch(1)

        self.tabla = QTableWidget(self)
        self.tabla.setColumnCount(7)
        self.tabla.setHorizontalHeaderLabels(["Código", "Descripción", "Cantidad", "Precio", "Total", "ISV", ""])
        header = self.tabla.horizontalHeader()
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(0, QHeaderView.Fixed)
        self.tabla.setColumnWidth(0, 110)
        header.setSectionResizeMode(2, QHeaderView.Fixed)
        self.tabla.setColumnWidth(2, 80)
        header.setSectionResizeMode(3, QHeaderView.Fixed)
        self.tabla.setColumnWidth(3, 130)
        header.setSectionResizeMode(4, QHeaderView.Fixed)
        self.tabla.setColumnWidth(4, 150)
        header.setSectionResizeMode(5, QHeaderView.Fixed)
        self.tabla.setColumnWidth(5, 45)
        header.setSectionResizeMode(6, QHeaderView.Fixed)
        self.tabla.setColumnWidth(6, 96)
        detalle_row = QHBoxLayout()
        self.split = QSplitter(Qt.Horizontal, self)
        self.split.setChildrenCollapsible(False)
        self.split.addWidget(self.tabla)
        try:
            self.catalogo_panel = QWidget(self)
            _cat_layout = QVBoxLayout(self.catalogo_panel)
            _cat_layout.setContentsMargins(0, 0, 0, 0)
            _cat_layout.setSpacing(6)
            self.catalogo_buscar = QLineEdit(self.catalogo_panel)
            self.catalogo_buscar.setPlaceholderText("Buscar por nombre, código o barras...")
            _cat_layout.addWidget(self.catalogo_buscar)
            self.catalogo = QTableWidget(self.catalogo_panel)
            self.catalogo.setColumnCount(3)
            self.catalogo.setHorizontalHeaderLabels(["Código", "Nombre", "Precio"])
            self.catalogo.setAlternatingRowColors(True)
            try:
                h = self.catalogo.horizontalHeader()
                h.setSectionResizeMode(1, QHeaderView.Stretch)
                h.setSectionResizeMode(0, QHeaderView.Fixed)
                self.catalogo.setColumnWidth(0, 100)
                h.setSectionResizeMode(2, QHeaderView.Fixed)
                self.catalogo.setColumnWidth(2, 100)
            except Exception:
                pass
            self.catalogo.setEditTriggers(QAbstractItemView.NoEditTriggers)
            self.catalogo.setSelectionBehavior(QAbstractItemView.SelectRows)
            self.catalogo.setSelectionMode(QAbstractItemView.SingleSelection)
            self.catalogo.doubleClicked.connect(self._on_catalogo_dclick)
            _cat_layout.addWidget(self.catalogo, 1)
            self.split.addWidget(self.catalogo_panel)
            try:
                self.split.setStretchFactor(0, 4)
                self.split.setStretchFactor(1, 1)
                self.split.setSizes([1000, 350])
            except Exception:
                pass
            try:
                self.cargar_catalogo_productos("")
                self.catalogo_buscar.textChanged.connect(self.cargar_catalogo_productos)
            except Exception:
                pass
        except Exception:
            pass
        detalle_row.addWidget(self.split, 1)
        detalle_row.addLayout(botones)
        contenido.addLayout(detalle_row)
        self.tabla.setEditTriggers(QAbstractItemView.AllEditTriggers)
        self.tabla.itemChanged.connect(self.on_tabla_item_changed)
        try:
            self.tabla.setItemDelegateForColumn(1, DescripcionDelegate(self))
        except Exception:
            pass

        totalbox = QHBoxLayout()
        totalbox.addStretch(1)

        root.addLayout(contenido)

        try:
            self.btn_pagar.clicked.connect(self._on_pagar_clicked)
        except Exception:
            pass
        self.btn_eliminar.clicked.connect(self.eliminar_seleccion)
        try:
            self.btn_limpiar.clicked.connect(lambda: self._on_limpiar_clicked())
        except Exception:
            pass
        self.btn_productos.clicked.connect(self.abrir_productos_dialog)

    def cargar_clientes(self):
        return

    def actualizar_clientes(self):
        return

    def on_nombre_elegido(self, nombre):
        return

    

    def abrir_gestion_clientes_dialog(self):
        return

    def abrir_productos_dialog(self):
        try:
            from productos import GestionProductos
        except Exception:
            QMessageBox.information(self, "Productos", "Módulo de productos no disponible")
            return
        dlg = None
        try:
            dlg = GestionProductos(parent=self)
        except Exception:
            pass
        if dlg is None:
            return
        try:
            dlg.setModal(False)
            dlg.setWindowModality(Qt.NonModal)
        except Exception:
            pass
        try:
            dlg.show()
            dlg.raise_()
            self.win_productos = dlg
        except Exception:
            pass
        try:
            QTimer.singleShot(150, lambda: getattr(dlg, 'abrir_formulario', lambda: None)())
        except Exception:
            pass
        return

    def cargar_catalogo_productos(self, texto=""):
        resultados = []
        tiene_pesable_col = False
        try:
            t = (texto or "").strip()
            if t:
                resultados = self._buscar_productos(t)
            else:
                conn = conectar()
                cur = conn.cursor()
                try:
                    cur.execute("PRAGMA table_info(productos)")
                    cols = [r[1].lower() for r in cur.fetchall()]
                    tiene_pesable_col = ('pesable' in cols)
                except Exception:
                    pass
                if tiene_pesable_col:
                    cur.execute("SELECT id_producto, nombre, precio, impuesto, pesable FROM productos ORDER BY nombre LIMIT 500")
                else:
                    cur.execute("SELECT id_producto, nombre, precio, impuesto FROM productos ORDER BY nombre LIMIT 500")
                resultados = cur.fetchall() or []
                conn.close()
        except Exception:
            try:
                connm = conectar_mysql()
                curm = connm.cursor()
                if (texto or "").strip():
                    q = "%" + (texto or "").lower() + "%"
                    curm.execute("SELECT id, nombre, precio, id_isv, barra FROM inventario WHERE LOWER(nombre) LIKE %s OR LOWER(barra) LIKE %s OR CAST(id AS CHAR) LIKE %s ORDER BY nombre LIMIT 500", (q, q, q))
                else:
                    curm.execute("SELECT id, nombre, precio, id_isv, barra FROM inventario ORDER BY nombre LIMIT 500")
                resultados = [(r[0], r[1], float(r[2] or 0.0), r[3], 0, r[4]) for r in (curm.fetchall() or [])]
                connm.close()
            except Exception:
                resultados = []
        try:
            self.catalogo.setRowCount(len(resultados))
            for i, r in enumerate(resultados):
                try:
                    pid = r[0]
                    nom = r[1]
                    pre = float(r[2] or 0.0)
                    imp = r[3]
                    pid_item = QTableWidgetItem(str(pid))
                    try:
                        pid_item.setData(Qt.UserRole, imp)
                    except Exception:
                        pass
                    self.catalogo.setItem(i, 0, pid_item)
                    self.catalogo.setItem(i, 1, QTableWidgetItem(str(nom)))
                    itp = QTableWidgetItem(self.format_currency(pre))
                    itp.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                    self.catalogo.setItem(i, 2, itp)
                except Exception:
                    pass
        except Exception:
            pass

    def _on_catalogo_dclick(self, index):
        try:
            row = index.row()
            pid_item = self.catalogo.item(row, 0)
            nom_item = self.catalogo.item(row, 1)
            pre_item = self.catalogo.item(row, 2)
            if not pid_item or not nom_item or not pre_item:
                return
            try:
                precio_val = self.parse_currency(pre_item.text())
            except Exception:
                precio_val = 0.0
            try:
                imp_raw = pid_item.data(Qt.UserRole)
            except Exception:
                imp_raw = None
            if imp_raw is None:
                try:
                    info = obtener_info_producto(pid_item.text())
                    v = str(info[2]).strip().lower()
                    if v in ("15", "1"):
                        imp_val = 1
                    elif v in ("18", "2"):
                        imp_val = 2
                    else:
                        imp_val = 3
                except Exception:
                    imp_val = 3
            else:
                v = str(imp_raw).strip().lower()
                if v in ("15", "1"):
                    imp_val = 1
                elif v in ("18", "2"):
                    imp_val = 2
                else:
                    imp_val = 3
            elegido = (pid_item.text(), nom_item.text(), precio_val, imp_val, 0)
            try:
                r = self.tabla.currentRow()
                if r is None or r < 0:
                    r = self.tabla.rowCount() - 1
                self._aplicar_producto_seleccion(r, elegido, insert_blank=False)
            except Exception:
                pass
        except Exception:
            pass

    def _ajustar_splitter(self):
        try:
            if hasattr(self, 'split') and self.split:
                w = max(self.width() - 240, 600)
                l = int(w * 0.75)
                r = max(w - l, 260)
                self.split.setSizes([l, r])
        except Exception:
            pass

    def on_cliente_creado_desde_dialog(self, rtn, nombre):
        return

    def eliminar_seleccion(self):
        r = self.tabla.currentRow()
        if r < 0:
            return
        self.tabla.removeRow(r)
        self.recalcular_total()
        try:
            self._asegurar_fila_blanco()
            QTimer.singleShot(30, self._focus_codigo)
        except Exception:
            pass

    def on_click_eliminar_fila(self):
        try:
            btn = self.sender()
            if not btn:
                return
            row = self._row_from_sender(btn)
            if row >= 0:
                self.tabla.removeRow(row)
                self.recalcular_total()
                try:
                    self._asegurar_fila_blanco()
                    QTimer.singleShot(30, self._focus_codigo)
                except Exception:
                    pass
        except Exception:
            pass

    def on_click_inc_fila(self):
        try:
            btn = self.sender()
            if not btn:
                return
            row = self._row_from_sender(btn)
            cod = self.tabla.item(row, 0)
            desc = self.tabla.item(row, 1)
            if (not cod or not cod.text() or not cod.text().strip()) or (not desc or not desc.text() or not desc.text().strip()):
                return
            ci = self.tabla.item(row, 2)
            if ci is None:
                ci = QTableWidgetItem("1.00")
                self.tabla.setItem(row, 2, ci)
            else:
                try:
                    val = float(ci.text())
                except Exception:
                    val = 0.0
                val = round(val + 1.0, 2)
                ci.setText(f"{val:.2f}")
            self.actualizar_total_fila(row)
        except Exception:
            pass

    def on_click_dec_fila(self):
        try:
            btn = self.sender()
            if not btn:
                return
            row = self._row_from_sender(btn)
            cod = self.tabla.item(row, 0)
            desc = self.tabla.item(row, 1)
            if (not cod or not cod.text() or not cod.text().strip()) or (not desc or not desc.text() or not desc.text().strip()):
                return
            ci = self.tabla.item(row, 2)
            if ci is None:
                return
            try:
                val = float(ci.text())
            except Exception:
                val = 1.0
            val = max(val - 1.0, 1.0)
            ci.setText(f"{val:.2f}")
            self.actualizar_total_fila(row)
        except Exception:
            pass

    def insertar_fila_blanco(self):
        """Inserta una nueva fila vacía"""
        row = self.tabla.rowCount()
        self.tabla.insertRow(row)
        
        # IMPORTANTE: Crear NUEVOS items cada vez
        codigo_item = QTableWidgetItem("")
        desc_item = QTableWidgetItem("")
        cantidad_item = QTableWidgetItem("")
        precio_item = QTableWidgetItem("")
        total_item = QTableWidgetItem("")
        exento_item = QTableWidgetItem("")
        cont = QWidget()
        lay = QHBoxLayout(cont)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(2)
        btn_dec = QPushButton("")
        btn_inc = QPushButton("")
        btn_del = QPushButton("")
        try:
            btn_dec.setIcon(QIcon("iconos/abajo.png"))
            btn_dec.setIconSize(QSize(20, 20))
            btn_dec.setFixedSize(28, 28)
            btn_dec.setStyleSheet("QPushButton{background:transparent;border:none;padding:0;} QPushButton:hover{background:rgba(0,0,0,0.08)}")
            btn_dec.setToolTip("Reducir")
            btn_inc.setIcon(QIcon("iconos/arriba.png"))
            btn_inc.setIconSize(QSize(20, 20))
            btn_inc.setFixedSize(28, 28)
            btn_inc.setStyleSheet("QPushButton{background:transparent;border:none;padding:0;} QPushButton:hover{background:rgba(0,0,0,0.08)}")
            btn_inc.setToolTip("Aumentar")
            btn_del.setIcon(QIcon("iconos/eliminar.png"))
            btn_del.setIconSize(QSize(20, 20))
            btn_del.setFixedSize(28, 28)
            btn_del.setStyleSheet("QPushButton{background:transparent;border:none;padding:0;} QPushButton:hover{background:rgba(0,0,0,0.08)}")
            btn_del.setToolTip("Eliminar fila")
        except Exception:
            pass
        try:
            btn_dec.clicked.connect(self.on_click_dec_fila)
            btn_inc.clicked.connect(self.on_click_inc_fila)
            btn_del.clicked.connect(self.on_click_eliminar_fila)
        except Exception:
            pass
        lay.addWidget(btn_dec)
        lay.addWidget(btn_inc)
        lay.addWidget(btn_del)
        
        codigo_item.setFlags(codigo_item.flags() | Qt.ItemIsEditable)
        cantidad_item.setFlags(cantidad_item.flags() | Qt.ItemIsEditable)
        
        ro = Qt.ItemIsSelectable | Qt.ItemIsEnabled
        desc_item.setFlags(desc_item.flags() | Qt.ItemIsEditable)
        precio_item.setFlags(ro)
        total_item.setFlags(ro)
        exento_item.setFlags(ro)
        
        precio_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        total_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        
        self.tabla.setItem(row, 0, codigo_item)
        self.tabla.setItem(row, 1, desc_item)
        self.tabla.setItem(row, 2, cantidad_item)
        self.tabla.setItem(row, 3, precio_item)
        self.tabla.setItem(row, 4, total_item)
        self.tabla.setItem(row, 5, exento_item)
        try:
            self.tabla.setCellWidget(row, 6, cont)
        except Exception:
            pass
        
        self.tabla.setCurrentCell(row, 0)
        try:
            self.tabla.editItem(self.tabla.item(row, 0))
        except Exception:
            pass

    def _row_from_sender(self, sender):
        try:
            cont = sender.parent()
        except Exception:
            cont = None
        if cont is not None:
            try:
                for r in range(self.tabla.rowCount()):
                    if self.tabla.cellWidget(r, 6) is cont:
                        return r
            except Exception:
                pass
        try:
            idx = self.tabla.indexAt(sender.parent().mapTo(self.tabla, sender.parent().rect().center()))
            r = idx.row()
        except Exception:
            r = -1
        if r is None or r < 0:
            try:
                r = self.tabla.currentRow()
            except Exception:
                r = -1
        return r

    def _asegurar_fila_blanco(self):
        try:
            rc = self.tabla.rowCount()
            if rc <= 0:
                self.insertar_fila_blanco()
                return
            last = rc - 1
            it = self.tabla.item(last, 0)
            txt = it.text().strip() if it and it.text() is not None else ""
            if txt:
                self.insertar_fila_blanco()
        except Exception:
            try:
                self.insertar_fila_blanco()
            except Exception:
                pass

    def _focus_codigo(self):
        try:
            if self.tabla is None:
                return
            # asegurar enfoque sobre la tabla
            self.tabla.setFocus()
            row = self.tabla.rowCount() - 1
            if row < 0:
                self.insertar_fila_blanco()
                row = self.tabla.rowCount() - 1
            it0 = self.tabla.item(row, 0)
            try:
                if it0 and it0.text() and it0.text().strip():
                    self.insertar_fila_blanco()
                    row = self.tabla.rowCount() - 1
            except Exception:
                pass
            self.tabla.setCurrentCell(row, 0)
            it = self.tabla.item(row, 0)
            if it is None:
                it = QTableWidgetItem("")
                self.tabla.setItem(row, 0, it)
            self.tabla.editItem(it)
        except Exception:
            pass

    def on_tabla_item_changed(self, item):
        if self._updating:
            return
        row, col = item.row(), item.column()
        try:
            self._updating = True
            if col == 0:
                codigo = item.text().strip()
                if not codigo:
                    for c in (1, 3, 4, 5):
                        it = self.tabla.item(row, c)
                        if it:
                            it.setText("")
                    return
                info = obtener_info_producto(codigo)
                if info:
                    pesable_flag = 0
                    if len(info) == 5:
                        pid, nombre, precio, id_isv, pesable_flag = info
                    elif len(info) == 4:
                        nombre, precio, id_isv, pesable_flag = info
                        pid = codigo
                    else:
                        # fallback
                        try:
                            nombre, precio, id_isv = info
                        except Exception:
                            nombre, precio, id_isv = ("", 0.0, 3)
                        pid = codigo
                    desc_item = self.tabla.item(row, 1) or QTableWidgetItem("")
                    self.tabla.setItem(row, 1, desc_item)
                    precio_item = self.tabla.item(row, 3) or QTableWidgetItem("")
                    self.tabla.setItem(row, 3, precio_item)
                    exento_item = self.tabla.item(row, 5) or QTableWidgetItem("")
                    self.tabla.setItem(row, 5, exento_item)
                    desc_item.setText(str(nombre))
                    precio_item.setData(Qt.UserRole, float(precio))
                    precio_item.setText(self.format_currency(float(precio)))
                    precio_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                    exento_item.setText(self.format_isv(id_isv))
                    ci = self.tabla.item(row, 2)
                    if pesable_flag:
                        if ci is None:
                            ci = QTableWidgetItem("")
                            self.tabla.setItem(row, 2, ci)
                        ci.setData(Qt.UserRole + 1, 1)
                        self.tabla.setCurrentCell(row, 2)
                        try:
                            self.tabla.editItem(ci)
                        except Exception:
                            pass
                    else:
                        if not ci or not ci.text().strip():
                            self.tabla.setItem(row, 2, QTableWidgetItem("1.00"))
                        self.actualizar_total_fila(row)
                        self.insertar_fila_blanco()
                else:
                    QMessageBox.warning(self, "Producto", "Código no encontrado")
            elif col == 1:
                texto = item.text().strip()
                if not texto:
                    return
                resultados = []
                tiene_pesable_col = False
                try:
                    conn = conectar()
                    cur = conn.cursor()
                    try:
                        cur.execute("PRAGMA table_info(productos)")
                        cols = [r[1].lower() for r in cur.fetchall()]
                        tiene_pesable_col = ('pesable' in cols)
                    except Exception:
                        pass
                    if tiene_pesable_col:
                        cur.execute("SELECT id_producto, nombre, precio, impuesto, pesable FROM productos WHERE LOWER(nombre) LIKE ? OR LOWER(codigo_barras) LIKE ?", ('%' + texto.lower() + '%','%' + texto.lower() + '%'))
                    else:
                        cur.execute("SELECT id_producto, nombre, precio, impuesto FROM productos WHERE LOWER(nombre) LIKE ? OR LOWER(codigo_barras) LIKE ?", ('%' + texto.lower() + '%','%' + texto.lower() + '%'))
                    resultados = cur.fetchall() or []
                    conn.close()
                except Exception:
                    try:
                        connm = conectar_mysql()
                        curm = connm.cursor()
                        curm.execute("SELECT id, nombre, precio, id_isv, barra FROM inventario WHERE LOWER(nombre) LIKE %s OR LOWER(barra) LIKE %s", ('%' + texto.lower() + '%','%' + texto.lower() + '%'))
                        resultados = [(r[0], r[1], float(r[2] or 0.0), r[3], 0, r[4]) for r in (curm.fetchall() or [])]
                        connm.close()
                    except Exception:
                        resultados = []
                if not resultados:
                    QMessageBox.warning(self, "Producto", "No se encontró producto por descripción")
                    return
                elegido = self._seleccionar_producto_desde_lista(resultados)
                if not elegido:
                    return
                try:
                    pid = elegido[0]
                    nombre = elegido[1]
                    precio = float(elegido[2] or 0.0)
                    imp = elegido[3]
                    try:
                        pesable_flag = int(elegido[4])
                    except Exception:
                        pesable_flag = 0
                    v = str(imp).strip().lower()
                    if v in ("15", "1"):
                        id_isv = 1
                    elif v in ("18", "2"):
                        id_isv = 2
                    else:
                        id_isv = 3
                    cod_item = self.tabla.item(row, 0) or QTableWidgetItem("")
                    self.tabla.setItem(row, 0, cod_item)
                    desc_item = self.tabla.item(row, 1) or QTableWidgetItem("")
                    self.tabla.setItem(row, 1, desc_item)
                    precio_item = self.tabla.item(row, 3) or QTableWidgetItem("")
                    self.tabla.setItem(row, 3, precio_item)
                    exento_item = self.tabla.item(row, 5) or QTableWidgetItem("")
                    self.tabla.setItem(row, 5, exento_item)
                    cod_item.setText(str(pid))
                    desc_item.setText(str(nombre))
                    precio_item.setData(Qt.UserRole, float(precio))
                    precio_item.setText(self.format_currency(float(precio)))
                    precio_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                    exento_item.setText(self.format_isv(id_isv))
                    ci = self.tabla.item(row, 2)
                    if pesable_flag:
                        if ci is None:
                            ci = QTableWidgetItem("")
                            self.tabla.setItem(row, 2, ci)
                        ci.setData(Qt.UserRole + 1, 1)
                        self.tabla.setCurrentCell(row, 2)
                        try:
                            self.tabla.editItem(ci)
                        except Exception:
                            pass
                    else:
                        if not ci or not ci.text().strip():
                            self.tabla.setItem(row, 2, QTableWidgetItem("1.00"))
                        self.actualizar_total_fila(row)
                        self.insertar_fila_blanco()
                except Exception:
                    QMessageBox.warning(self, "Producto", "Error al aplicar selección")
            elif col == 2:
                self.actualizar_total_fila(row)
                ci = self.tabla.item(row, 2)
                try:
                    if ci and ci.data(Qt.UserRole + 1):
                        ci.setData(Qt.UserRole + 1, None)
                        self.insertar_fila_blanco()
                except Exception:
                    pass
        finally:
            self._updating = False

    def actualizar_total_fila(self, row):
        cantidad_item = self.tabla.item(row, 2)
        precio_item = self.tabla.item(row, 3)
        total_item = self.tabla.item(row, 4)
        if cantidad_item is None:
            cantidad_item = QTableWidgetItem("")
            self.tabla.setItem(row, 2, cantidad_item)
        if precio_item is None:
            precio_item = QTableWidgetItem("")
            self.tabla.setItem(row, 3, precio_item)
        if total_item is None:
            total_item = QTableWidgetItem("")
            self.tabla.setItem(row, 4, total_item)
        try:
            cantidad = float(cantidad_item.text())
            precio_val = precio_item.data(Qt.UserRole)
            if precio_val is None:
                precio_val = self.parse_currency(precio_item.text())
            subtotal = round(cantidad * precio_val, 2)
            total_item.setData(Qt.UserRole, subtotal)
            total_item.setText(self.format_currency(subtotal))
            total_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        except Exception:
            total_item.setData(Qt.UserRole, None)
            total_item.setText("")
        self.recalcular_total()

    def recalcular_total(self):
        total = 0.0
        for r in range(self.tabla.rowCount()):
            it = self.tabla.item(r, 4)
            if it:
                val = it.data(Qt.UserRole)
                if val is None:
                    val = self.parse_currency(it.text())
                try:
                    total += float(val)
                except Exception:
                    pass
        self.total = round(total, 2)
        self.lbl_total.setText(f"Total L: {self.total:.2f}")
        

    def _seleccionar_producto_desde_lista(self, resultados):
        try:
            dlg = QDialog(self)
            dlg.setWindowTitle("Productos coincidentes")
            lay = QVBoxLayout(dlg)
            t = QTableWidget(dlg)
            t.setColumnCount(4)
            t.setHorizontalHeaderLabels(["Código", "Nombre", "Precio", "ISV"])
            t.setRowCount(len(resultados))
            for i, r in enumerate(resultados):
                try:
                    pid = r[0]
                    nom = r[1]
                    pre = float(r[2] or 0.0)
                    imp = r[3]
                    v = str(imp).strip().lower()
                    if v in ("15", "1"):
                        tag = "15%"
                    elif v in ("18", "2"):
                        tag = "18%"
                    else:
                        tag = "Ex"
                    t.setItem(i, 0, QTableWidgetItem(str(pid)))
                    t.setItem(i, 1, QTableWidgetItem(str(nom)))
                    itp = QTableWidgetItem(self.format_currency(pre))
                    itp.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                    t.setItem(i, 2, itp)
                    t.setItem(i, 3, QTableWidgetItem(tag))
                except Exception:
                    pass
            t.setEditTriggers(QAbstractItemView.NoEditTriggers)
            t.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
            lay.addWidget(t)
            btns = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, parent=dlg)
            lay.addWidget(btns)
            elegido = {'val': None}
            def aceptar():
                try:
                    idx = t.currentRow()
                    if idx < 0:
                        idx = 0
                    elegido['val'] = resultados[idx]
                    dlg.accept()
                except Exception:
                    dlg.reject()
            btns.accepted.connect(aceptar)
            btns.rejected.connect(dlg.reject)
            t.doubleClicked.connect(lambda _: aceptar())
            if len(resultados) == 1:
                t.selectRow(0)
            dlg.exec_()
            return elegido['val']
        except Exception:
            try:
                return resultados[0] if resultados else None
            except Exception:
                return None

    def _buscar_productos(self, texto):
        resultados = []
        tiene_pesable_col = False
        try:
            conn = conectar()
            cur = conn.cursor()
            try:
                cur.execute("PRAGMA table_info(productos)")
                cols = [r[1].lower() for r in cur.fetchall()]
                tiene_pesable_col = ('pesable' in cols)
            except Exception:
                pass
            like = '%' + texto.lower() + '%'
            if tiene_pesable_col:
                cur.execute("SELECT id_producto, nombre, precio, impuesto, pesable FROM productos WHERE LOWER(nombre) LIKE ? OR LOWER(codigo_barras) LIKE ? OR CAST(id_producto AS TEXT) LIKE ?", (like, like, like))
            else:
                cur.execute("SELECT id_producto, nombre, precio, impuesto FROM productos WHERE LOWER(nombre) LIKE ? OR LOWER(codigo_barras) LIKE ? OR CAST(id_producto AS TEXT) LIKE ?", (like, like, like))
            resultados = cur.fetchall() or []
            conn.close()
        except Exception:
            try:
                connm = conectar_mysql()
                curm = connm.cursor()
                curm.execute("SELECT id, nombre, precio, id_isv, barra FROM inventario WHERE LOWER(nombre) LIKE %s OR LOWER(barra) LIKE %s OR CAST(id AS CHAR) LIKE %s", ('%' + texto.lower() + '%','%' + texto.lower() + '%','%' + texto.lower() + '%'))
                resultados = [(r[0], r[1], float(r[2] or 0.0), r[3], 0, r[4]) for r in (curm.fetchall() or [])]
                connm.close()
            except Exception:
                resultados = []
        return resultados

    def _aplicar_producto_seleccion(self, row, elegido, insert_blank=True):
        try:
            pid = elegido[0]
            nombre = elegido[1]
            precio = float(elegido[2] or 0.0)
            imp = elegido[3]
            try:
                pesable_flag = int(elegido[4])
            except Exception:
                pesable_flag = 0
            v = str(imp).strip().lower()
            if v in ("15", "1"):
                id_isv = 1
            elif v in ("18", "2"):
                id_isv = 2
            else:
                id_isv = 3
            cod_item = self.tabla.item(row, 0) or QTableWidgetItem("")
            self.tabla.setItem(row, 0, cod_item)
            desc_item = self.tabla.item(row, 1) or QTableWidgetItem("")
            self.tabla.setItem(row, 1, desc_item)
            precio_item = self.tabla.item(row, 3) or QTableWidgetItem("")
            self.tabla.setItem(row, 3, precio_item)
            exento_item = self.tabla.item(row, 5) or QTableWidgetItem("")
            self.tabla.setItem(row, 5, exento_item)
            cod_item.setText(str(pid))
            desc_item.setText(str(nombre))
            precio_item.setData(Qt.UserRole, float(precio))
            precio_item.setText(self.format_currency(float(precio)))
            precio_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            exento_item.setText(self.format_isv(id_isv))
            ci = self.tabla.item(row, 2)
            if pesable_flag:
                if ci is None:
                    ci = QTableWidgetItem("")
                    self.tabla.setItem(row, 2, ci)
                ci.setData(Qt.UserRole + 1, 1)
                self.tabla.setCurrentCell(row, 2)
                try:
                    self.tabla.editItem(ci)
                except Exception:
                    pass
            else:
                if not ci or not ci.text().strip():
                    self.tabla.setItem(row, 2, QTableWidgetItem("1.00"))
                self.actualizar_total_fila(row)
                if insert_blank:
                    self.insertar_fila_blanco()
        except Exception:
            QMessageBox.warning(self, "Producto", "Error al aplicar selección")

class DescripcionDelegate(QStyledItemDelegate):
    def __init__(self, ventas):
        super().__init__(ventas)
        self.ventas = ventas

    def createEditor(self, parent, option, index):
        editor = QLineEdit(parent)
        comp = QCompleter(editor)
        comp.setCaseSensitivity(Qt.CaseInsensitive)
        comp.setFilterMode(Qt.MatchContains)
        model = QStringListModel([], comp)
        comp.setModel(model)
        mapa = {'m': {}}
        def on_txt(t):
            res = self.ventas._buscar_productos(t)
            nombres = []
            m = {}
            for r in res:
                try:
                    k = str(r[1])
                    if k not in m:
                        m[k] = r
                        nombres.append(k)
                except Exception:
                    pass
            mapa['m'] = m
            model.setStringList(nombres)
            if t:
                comp.complete()
        editor.textChanged.connect(on_txt)
        def on_pick(s):
            elegido = mapa['m'].get(s)
            if elegido:
                self.ventas._aplicar_producto_seleccion(index.row(), elegido)
        comp.activated[str].connect(on_pick)
        editor.setCompleter(comp)
        return editor

    

    

    

    # ==========================================
    # MÉTODOS OPTIMIZADOS PARA MYSQL
    # ==========================================

    

    

    def _guardar_factura_sqlite(self, numero_doc, numero_fmt, cai, items, cliente, rtn_cli, g15, g18, ex, i15, i18, total, pagado, cambio, metodo):
        ok = False
        conn = None
        try:
            conn = conectar()
            cur = conn.cursor()
            asegurar_tabla_ventas_sqlite()
            asegurar_tabla_facturas_sqlite()
            try:
                cur.execute("DELETE FROM ventas WHERE factura = ?", (int(numero_doc),))
                cur.execute("DELETE FROM facturas WHERE factura = ?", (int(numero_doc),))
            except Exception:
                pass
            for pid, nombre, precio_val, cantidad, subtotal in items:
                insertar_venta(
                    conn,
                    int(numero_doc),
                    str(pid),
                    str(nombre),
                    float(precio_val or 0),
                    float(cantidad or 0),
                    float(subtotal or 0),
                    0, 0, 0, 0, 0,
                    float(total or 0)
                )
                try:
                    actualizar_stock(conn, str(pid), float(cantidad or 0))
                except Exception:
                    pass
            insertar_factura_resumen(
                conn,
                int(numero_doc),
                str(cliente or ""),
                float(g15 or 0),
                float(g18 or 0),
                float(ex or 0),
                float(i15 or 0),
                float(i18 or 0),
                float(total or 0),
                float(pagado or 0),
                float(cambio or 0),
                str(metodo or "Efectivo")
            )
            conn.commit()
            ok = True
        except Exception:
            try:
                if conn:
                    conn.rollback()
            except Exception:
                pass
            ok = False
        finally:
            try:
                if conn:
                    conn.close()
            except Exception:
                pass
        return ok

    

    def abrir_pago(self):
        if self.total <= 0:
            QMessageBox.warning(self, "Pago", "No hay artículos por pagar")
            return
        
        tiene = False
        for r in range(self.tabla.rowCount()):
            it = self.tabla.item(r, 0)
            if it and it.text().strip():
                tiene = True
                break
        if not tiene:
            QMessageBox.warning(self, "Pago", "No hay productos válidos para cobrar")
            return

        dialog = QDialog(self)
        dialog.setWindowTitle("Pago")
        dialog.setFixedSize(420, 480)
        main_layout = QVBoxLayout(dialog)
        try:
            main_layout.setContentsMargins(8, 8, 8, 8)
            main_layout.setSpacing(6)
        except Exception:
            pass
        izq = QVBoxLayout()
        
        # Obtener número de factura local rápido
        try:
            max_fac = obtener_max_factura() or 0
            numero_doc = int(max_fac) + 1
        except Exception:
            try:
                numero_doc = int(getattr(self, 'numero_factura_actual', 1))
            except Exception:
                numero_doc = 1
        numero_factura_fmt = f"{int(numero_doc):08d}"
        
        lf = QLabel(f"Factura: {numero_factura_fmt}")
        lf.setStyleSheet("color: red; font-weight: bold; font-size: 16px;")
        izq.addWidget(lf)
        
        total_lbl = QLabel(f"Total a pagar: {self.format_currency(self.total)}")
        total_lbl.setStyleSheet("QLabel { background-color: #FADBD8; color: #C0392B; font-weight: bold; font-size: 16px; border: 1px solid #C0392B; border-radius: 8px; padding: 6px; qproperty-alignment: AlignCenter; }")
        izq.addWidget(total_lbl)
        
        le_ef = QLineEdit()
        le_ef.setPlaceholderText("0.00")
        izq.addWidget(QLabel("Efectivo:"))
        izq.addWidget(le_ef)
        
        total_pag = QLabel("Total Pagado: L 0.00")
        total_pag.setStyleSheet("QLabel { background-color: #E8F6F3; color: #148F77; font-size: 12px; font-weight: bold; border: 1px solid #52C9B0; border-radius: 5px; padding: 4px; margin-top: 4px; qproperty-alignment: AlignCenter; }")
        izq.addWidget(total_pag)
        
        cambio_lbl = QLabel("Cambio: L 0.00")
        cambio_lbl.setStyleSheet("QLabel { background-color: #D4EFDF; color: #196F3D; font-size: 14px; font-weight: bold; border: 1px solid #27AE60; border-radius: 6px; padding: 6px; margin-top: 8px; qproperty-alignment: AlignCenter; }")
        izq.addWidget(cambio_lbl)
        
        chk_print = QCheckBox("Enviar factura a impresora")
        chk_print.setChecked(False)
        izq.addWidget(chk_print)
        
        main_layout.addLayout(izq)
        
        
        
        def actualizar_campos():
            le_ef.setEnabled(True); le_ef.setReadOnly(False); le_ef.setText(""); le_ef.setFocus()
        
        def parse_m(s):
            t = str(s or "").strip().replace(",", ".")
            import re
            t = re.sub(r"[^0-9.]", "", t)
            if t.count('.') > 1:
                parts = t.split('.')
                t = ''.join(parts[:-1]) + '.' + parts[-1]
            try:
                return float(t) if t not in ("", ".") else 0.0
            except Exception:
                return 0.0
        
        def calc():
            ef = parse_m(le_ef.text())
            tp = ef
            total_pag.setText(f"Total Pagado: {self.format_currency(tp)}")
            if tp >= self.total:
                cambio = tp - self.total
                cambio_lbl.setText(f"Cambio: {self.format_currency(cambio)}")
            else:
                falt = self.total - tp
                cambio_lbl.setText(f"Faltan: {self.format_currency(falt)}")
        
        le_ef.textChanged.connect(calc)
        actualizar_campos()
        calc()
        
        botones = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        botones.button(QDialogButtonBox.Ok).setText("Confirmar Pago")
        try:
            botones.button(QDialogButtonBox.Ok).setStyleSheet("background-color: #58D68D; color: white; font-weight: bold;")
        except Exception:
            pass
        botones.button(QDialogButtonBox.Cancel).setText("Cancelar")
        
        def confirmar():
            ef = parse_m(le_ef.text())
            tp = ef
            
            if tp < self.total:
                QMessageBox.warning(dialog, "Pago", f"Total a pagar: {self.format_currency(self.total)}\nTotal recibido: {self.format_currency(tp)}")
                return
            
            cambio = tp - self.total
            mt = "Efectivo"
            
            g15_local, g18_local, ex_local, i15_local, i18_local = 0.0, 0.0, 0.0, 0.0, 0.0
            
            
            
            # Preparar items
            items_para_guardar = []
            for r in range(self.tabla.rowCount()):
                pid_item = self.tabla.item(r, 0)
                nombre_item = self.tabla.item(r, 1)
                cant_item = self.tabla.item(r, 2)
                precio_item = self.tabla.item(r, 3)
                subtotal_item = self.tabla.item(r, 4)
                
                if not pid_item or not nombre_item or not cant_item or not precio_item or not subtotal_item:
                    continue
                
                try:
                    pid = str(pid_item.text()).strip()
                    nombre = str(nombre_item.text()).strip()
                    cantidad = float(cant_item.text())
                    precio_val = precio_item.data(Qt.UserRole)
                    if precio_val is None:
                        precio_val = self.parse_currency(precio_item.text())
                    subtotal = subtotal_item.data(Qt.UserRole)
                    if subtotal is None:
                        subtotal = self.parse_currency(subtotal_item.text())
                    if not pid or not nombre:
                        continue
                    if float(cantidad) <= 0 and float(subtotal) <= 0:
                        continue
                    items_para_guardar.append((pid, nombre, float(precio_val or 0), float(cantidad or 0), float(subtotal or 0)))
                except Exception:
                    continue
            
            numero_fmt = numero_factura_fmt
            
            ok = self._guardar_factura_sqlite(
                numero_doc, numero_fmt, None, items_para_guardar, "", "",
                0.0, 0.0, 0.0, 0.0, 0.0,
                self.total, tp, cambio, mt
            )
            
            # Generar PDF
            try:
                msg_fac = f"Factura No: {numero_fmt}\n"
            except Exception:
                msg_fac = ""
            
            try:
                filename = self.generar_factura_pdf(
                numero_doc, 
                    efectivo=ef, 
                    cambio=cambio, 
                    abrir=True, 
                    es_exenta=False, 
                    imprimir=chk_print.isChecked(), 
                    numero_fmt=numero_fmt, 
                    cai=None,
                    items_cache=items_para_guardar,
                    totales_cache={
                        'gravado15': 0.0,
                        'gravado18': 0.0,
                        'exento': 0.0,
                        'isv15': 0.0,
                        'isv18': 0.0,
                        'total': self.total,
                        'pagado': tp,
                        'cambio': cambio
                    },
                    cai_cache=None
                )
            except Exception as e:
                QMessageBox.warning(self, "PDF", f"Error al generar PDF: {e}")
            
            QMessageBox.information(self, "Pago", f"{msg_fac}Pagado: {self.format_currency(tp)}\nCambio: {self.format_currency(cambio)}")
            
            self.tabla.setRowCount(0)
            self.recalcular_total()
            self.insertar_fila_blanco()
            self.numero_factura_actual = int(numero_doc) + 1
            dialog.accept()
        
        botones.accepted.connect(confirmar)
        botones.rejected.connect(dialog.reject)
        izq.addWidget(botones)
        
        try:
            sc = QShortcut(QKeySequence(Qt.Key_F10), dialog)
            sc.activated.connect(confirmar)
        except Exception:
            pass
        
        dialog.exec_()

    def _on_pagar_clicked(self):
        try:
            self.abrir_pago()
        except Exception as e:
            try:
                QMessageBox.warning(self, "Pago", f"Error al abrir pago: {e}")
            except Exception:
                pass

    def _on_limpiar_clicked(self):
        try:
            self.tabla.setRowCount(0)
        except Exception:
            pass
        try:
            self.total = 0.0
            self.lbl_total.setText("Total L: 0.00")
        except Exception:
            pass
        try:
            self.insertar_fila_blanco()
        except Exception:
            pass
        try:
            self._focus_codigo()
        except Exception:
            pass
        try:
            if hasattr(self, 'catalogo_buscar') and self.catalogo_buscar:
                self.catalogo_buscar.clear()
                self.cargar_catalogo_productos("")
        except Exception:
            pass

    def generar_factura_pdf(self, factura_id, efectivo=0.0, cambio=0.0, abrir=True, es_exenta=False, 
                            imprimir=False, numero_fmt=None, cai=None, items_cache=None, 
                            totales_cache=None, cai_cache=None):
        """Genera PDF optimizado usando datos cacheados"""
        from reportlab.lib.pagesizes import inch
        from reportlab.pdfgen import canvas
        import os
        
        ticket_width = 3.15 * inch
        ticket_height = 11 * inch
        y = ticket_height - 10
        
        # Datos de compañía
        try:
            from db import obtener_datos_compania
            datos_cia = obtener_datos_compania()
        except Exception:
            datos_cia = None
        
        if datos_cia:
            nombre_cia, direccion1, direccion2, rtn, correo, telefono = datos_cia
        else:
            nombre_cia = ""
            direccion1 = ""
            direccion2 = ""
            rtn = ""
            correo = ""
            telefono = ""
        
        fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Usar datos cacheados
        if totales_cache:
            totales = totales_cache
        else:
            totales = {
                "gravado15": 0.0, "gravado18": 0.0, "exento": 0.0,
                "isv15": 0.0, "isv18": 0.0, "total": self.total,
                "pagado": efectivo, "cambio": cambio
            }
        
        # Items cacheados
        if items_cache:
            items = [
                (pid, nombre, cantidad, precio, subtotal)
                for pid, nombre, precio, cantidad, subtotal in items_cache
                if str(pid).strip() and str(nombre).strip() and (float(cantidad) > 0 or float(subtotal) > 0)
            ]
        else:
            items = []
        
        
        
        # Crear directorio
        output_dir = os.path.expanduser("~/Documents/Restaurante/Facturas")
        try:
            os.makedirs(output_dir, exist_ok=True)
        except Exception:
            pass
        
        num_str = numero_fmt or f"{int(factura_id):08d}"
        filename = os.path.join(output_dir, f"factura_ticket_{num_str}.pdf")
        
        c = canvas.Canvas(filename, pagesize=(ticket_width, ticket_height))
        
        
        def draw_text(text, size=9, bold=False, center=False):
            nonlocal y
            font = "Helvetica-Bold" if bold else "Helvetica"
            c.setFont(font, size)
            if center:
                c.drawCentredString(ticket_width / 2, y, str(text))
            else:
                c.drawString(8, y, str(text))
            y -= size + 2
        
        def draw_line():
            nonlocal y
            c.line(10, y, ticket_width - 10, y)
            y -= 10
        
        def draw_line_punteada():
            nonlocal y
            c.setDash(1, 2)
            c.line(10, y, ticket_width - 10, y)
            c.setDash([])
            y -= 10
        
        # Encabezado
        draw_text("MI TIENDA", size=9, bold=True, center=True)
        
        y -= 5
        draw_text(f"Fecha/Hora: {fecha}")
        
        try:
            ref = str(num_str)[-6:]
        except Exception:
            ref = str(factura_id).zfill(6)
        
        draw_text(f"Nro ref: {ref}")
        
        if numero_fmt:
            draw_text(f"Factura: {numero_fmt}", bold=True, size=10)
        else:
            draw_text(f"Factura: {int(factura_id):08d}", bold=True, size=10)
        
        
        
        y -= 5
        
        # Tabla
        c.setFont("Helvetica-Bold", 7)
        right_x = ticket_width - 15
        x_cod = 8
        x_desc = x_cod + 30
        x_precio_right = right_x - 32
        x_cant_right = x_precio_right - 30
        x_cant_center = x_cant_right - 15
        
        c.drawString(x_cod, y, "Cod.")
        c.drawString(x_desc, y, "Descripcion")
        c.drawCentredString(x_cant_center, y, "Cant.")
        c.drawRightString(x_precio_right, y, "Precio")
        c.drawRightString(right_x, y, "Total")
        y -= 12
        draw_line()
        
        c.setFont("Helvetica", 8)
        for it in items:
            try:
                codigo, nombre, cantidad, precio, subtotal = it
                if not str(codigo).strip() or not str(nombre).strip():
                    continue
                try:
                    cant_val = float(cantidad)
                    sub_val = float(subtotal)
                except Exception:
                    cant_val = 0.0
                    sub_val = 0.0
                if cant_val <= 0 and sub_val <= 0:
                    continue
                unit = (float(subtotal) / float(cantidad)) if cantidad else float(precio or 0)
                
                c.drawString(x_cod, y, str(codigo)[:8])
                
                nombre_corto = str(nombre)[:15]
                c.drawString(x_desc, y, nombre_corto)
                c.drawCentredString(x_cant_center, y, f"{cant_val:.1f}")
                c.drawRightString(x_precio_right, y, f"{float(unit):.2f}")
                c.drawRightString(right_x, y, f"{sub_val:.2f}")
                y -= 10
            except Exception:
                pass
        draw_line()
        
        # Totales simplificados
        
        draw_line_punteada()
        
        c.setFont("Helvetica-Bold", 9)
        c.drawRightString(ticket_width - 15, y, f"TOTAL A PAGAR:        L. {totales['total']:.2f}")
        y -= 8
        draw_line_punteada()
        
        c.setFont("Helvetica", 8)
        c.drawRightString(ticket_width - 15, y, f"Efectivo recibido:    L. {efectivo:.2f}")
        y -= 10
        c.drawRightString(ticket_width - 15, y, f"Su cambio:            L. {cambio:.2f}")
        y -= 15
        
        
        
        # Pie
        c.setFont("Helvetica", 8)
        c.drawCentredString(ticket_width / 2, y, "NO SE ACEPTAN CAMBIOS NI DEVOLUCIONES")
        y -= 10
        
        c.setFont("Helvetica-Bold", 9)
        c.drawCentredString(ticket_width / 2, y, "GRACIAS POR SU COMPRA")
        y -= 10
        
        c.setFont("Helvetica", 7)
        c.drawCentredString(ticket_width / 2, y, "ORIGINAL: CLIENTE    COPIA: EMISOR")
        
        c.save()
        
        # Abrir o imprimir
        try:
            if imprimir:
                try:
                    os.startfile(filename, "print")
                except Exception:
                    try:
                        import win32api
                        win32api.ShellExecute(0, "print", filename, None, ".", 0)
                    except Exception:
                        os.startfile(filename)
            elif abrir:
                os.startfile(filename)
        except Exception:
            pass
        
        return filename

    

if __name__ == "__main__":
    import sys
    import traceback
    
    def _excepthook(t, v, tb):
        print("Excepción no capturada:")
        traceback.print_exception(t, v, tb)
    
    sys.excepthook = _excepthook
    print("Iniciando aplicación de Ventas...")
    app = QApplication(sys.argv)
    
    try:
        app.setQuitOnLastWindowClosed(True)
    except Exception:
        pass

    try:
        print("Tiene abrir_pago:", hasattr(VentasWindow, 'abrir_pago'))
        print("Tiene limpiar_todo:", hasattr(VentasWindow, 'limpiar_todo'))
    except Exception:
        pass
    
    try:
        w = VentasWindow()
    except Exception as e:
        print(f"Error al crear VentasWindow: {e}")
        w = QWidget()
        w.setWindowTitle("Ventas - Error")
    
    w.show()
    
    try:
        w.raise_()
        w.activateWindow()
    except Exception:
        pass
    
    sys.exit(app.exec_())
