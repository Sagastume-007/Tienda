import sqlite3
_mysql = None
_pymysql = None
try:
    import pymysql as _pymysql
except Exception:
    try:
        import mysql.connector as _mysql
    except Exception:
        _mysql = None

DB_NAME = "mitienda.db"
DB_PATH = DB_NAME
MYSQL_HOST = "localhost"
MYSQL_PORT = 3306
MYSQL_USER = "root"
MYSQL_PASSWORD = "OdusSystem"
MYSQL_DB = "facturacion"

def conectar():
    return sqlite3.connect(DB_NAME)

def conectar_mysql():
    if _pymysql is not None:
        return _pymysql.connect(host=MYSQL_HOST, port=MYSQL_PORT, user=MYSQL_USER, password=MYSQL_PASSWORD, database=MYSQL_DB, connect_timeout=3, charset="utf8mb4")
    if _mysql is not None:
        return _mysql.connect(host=MYSQL_HOST, port=MYSQL_PORT, user=MYSQL_USER, password=MYSQL_PASSWORD, database=MYSQL_DB, connection_timeout=3)
    raise RuntimeError("MySQL no disponible")

def asegurar_tabla_ventas_sqlite():
    with conectar() as conn:
        c = conn.cursor()
        c.execute(
            "CREATE TABLE IF NOT EXISTS ventas (id TEXT, factura INTEGER, nombre_articulo TEXT, valor_articulo REAL, cantidad REAL, subtotal REAL, gravado15 REAL, gravado18 REAL, totalexento REAL, isv15 REAL, isv18 REAL, grantotal REAL)"
        )
        conn.commit()

def asegurar_tabla_inventario_sqlite():
    with conectar() as conn:
        c = conn.cursor()
        c.execute(
            "CREATE TABLE IF NOT EXISTS inventario (id INTEGER PRIMARY KEY AUTOINCREMENT, barra TEXT UNIQUE, nombre TEXT NOT NULL, precio REAL NOT NULL, id_isv INTEGER NOT NULL, stock INTEGER NOT NULL DEFAULT 0, pesable INTEGER NOT NULL DEFAULT 0)"
        )
        try:
            c.execute("PRAGMA table_info(inventario)")
            cols = [r[1].lower() for r in c.fetchall()]
            if 'pesable' not in cols:
                c.execute("ALTER TABLE inventario ADD COLUMN pesable INTEGER NOT NULL DEFAULT 0")
        except Exception:
            pass
        conn.commit()

def asegurar_tabla_clientes_sqlite():
    with conectar() as conn:
        c = conn.cursor()
        c.execute(
            "CREATE TABLE IF NOT EXISTS clientes (id_cliente INTEGER PRIMARY KEY AUTOINCREMENT, rtn TEXT, nombre TEXT NOT NULL)"
        )
        conn.commit()

def asegurar_tabla_categorias_sqlite():
    with conectar() as conn:
        c = conn.cursor()
        c.execute(
            "CREATE TABLE IF NOT EXISTS categorias (id INTEGER PRIMARY KEY AUTOINCREMENT, nombre TEXT NOT NULL UNIQUE)"
        )
        conn.commit()

def asegurar_tabla_tipoisv_sqlite():
    with conectar() as conn:
        c = conn.cursor()
        c.execute(
            "CREATE TABLE IF NOT EXISTS tipoisv (id_isv INTEGER PRIMARY KEY AUTOINCREMENT, tipo_isv TEXT NOT NULL UNIQUE)"
        )
        conn.commit()

def asegurar_tabla_productos_sqlite():
    with conectar() as conn:
        c = conn.cursor()
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS productos (
                id_producto INTEGER PRIMARY KEY,
                nombre TEXT NOT NULL,
                proveedor TEXT,
                codigo_barras TEXT,
                precio REAL NOT NULL,
                costo REAL NOT NULL DEFAULT 0,
                impuesto INTEGER NOT NULL DEFAULT 3,
                stock INTEGER NOT NULL DEFAULT 0,
                pesable INTEGER NOT NULL DEFAULT 0
            )
            """
        )
        conn.commit()

def asegurar_columna_pesable_productos_sqlite():
    asegurar_tabla_productos_sqlite()
    with conectar() as conn:
        c = conn.cursor()
        try:
            c.execute("PRAGMA table_info(productos)")
            cols = [r[1].lower() for r in c.fetchall()]
            if 'pesable' not in cols:
                c.execute("ALTER TABLE productos ADD COLUMN pesable INTEGER NOT NULL DEFAULT 0")
            if 'stock' not in cols:
                c.execute("ALTER TABLE productos ADD COLUMN stock INTEGER NOT NULL DEFAULT 0")
            if 'costo' not in cols:
                c.execute("ALTER TABLE productos ADD COLUMN costo REAL NOT NULL DEFAULT 0")
            if 'proveedor' not in cols:
                c.execute("ALTER TABLE productos ADD COLUMN proveedor TEXT")
        except Exception:
            pass
        conn.commit()

def sembrar_productos_iniciales():
    asegurar_tabla_productos_sqlite()
    asegurar_columna_pesable_productos_sqlite()
    datos = [
        (100001, "Mouse Inalambrico", "Acosa", 126.99, 88.54, 97, None, 1, 0),
        (100002, "Teclado Dell", "Acosa", 255.99, 170.65, 175, None, 1, 0),
        (100003, "Marcador destacador Genial Verde", "Acosa", 13.99, 10.75, 149, "1231556800", 3, 0),
        (100004, "Pasta Naturas 96g", "Unilever", 11.99, 7.99, 85, None, 1, 1),
        (100005, "Corrector", "Pacasa", 14.99, 10.43, 117, "100005", 1, 0),
        (100006, "Lapiz Genial Negro", "Acosa", 10.99, 7.43, 149, "1231558773", 3, 0),
        (100007, "Calko Mapas No.2", "Utiles de Honduras", 154.99, 103.58, 96, "1762157480", 3, 0),
        (100008, "Plantilla Acero para borrador", "Utiles de Honduras", 56.99, 40.13, 192, "-1654489673", 1, 0),
        (100009, "Borrador Grande Softy Plus", "Utiles de Honduras", 10.99, 6.51, 193, "1639122641", 3, 0),
        (100010, "Talonario Comercial Grande copia", "Utiles de Honduras", 30.99, 22.32, 194, "-1691221788", 3, 0),
        (100011, "Talonario Comercial Grande scopia", "Utiles de Honduras", 17.99, 13.24, 199, "-1691133582", 3, 0),
        (100012, "Boligrafo Feel IT BX417 RT 0.7 Azul", "Utiles de Honduras", 7.99, 4.42, 142, "87765160", 3, 0),
        (100013, "Boligrafo Feel IT BX417 RT 0.7 Negro", "Utiles de Honduras", 7.99, 4.51, 287, "87765136", 3, 0),
        (100014, "Boligrafo Feel IT BX417 0.17 Rojo", "Utiles de Honduras", 7.99, 4.51, 144, "87765153", 3, 0),
        (100015, "Corrector Tipo Lapiz Amigo", "Utiles de Honduras", 7.99, 4.42, 144, "-1043384741", 1, 0),
        (100016, "Juego Geometrico Silco", "Utiles de Honduras", 140.99, 120.37, 200, "1634196787", 3, 0),
        (100017, "Juego Geometrico Irrompible Pocket", "Utiles de Honduras", 120.99, 95.38, 96, "-74215554", 3, 0),
        (100018, "Lapices de color Peps 24 largo", "Utiles de Honduras", 99.99, 87.05, 48, "1635836982", 1, 0),
        (100019, "Cuaderno Espiral 1 materia Amigo", "Utiles de Honduras", 44.99, 23.69, 200, "-1691134948", 3, 0),
        (100020, "Leche Sula litro", "Lacthosa", 30.00, 24.98, 185, "-95591064", 3, 0),
        (100021, "Cafe Medalla 454g", "Molino de Cafe Maya", 99.99, 88.00, 120, "-188132402", 3, 0),
        (100022, "Suerox Fresa Kiwi 630ml", "Surtidora Internacional", 60.99, 45.80, 24, "1700001517", 1, 0),
        (100023, "Suerox Chicle 620ml", "Surtidora Internacional", 60.99, 45.99, 24, "-1158364866", 1, 0),
        (100024, "Vaso desechable", "Alvarez", 1.00, 0.50, 200, "370128405", 3, 0),
        (100025, "Lapiz grafito Genial", "Acosa", 5.99, 3.99, 144, "1231557408", 3, 0)
    ]
    with conectar() as conn:
        c = conn.cursor()
        for pid, nombre, proveedor, precio, costo, stock, barra, impuesto, pesable in datos:
            try:
                c.execute("SELECT 1 FROM productos WHERE id_producto = ?", (pid,))
                exists = c.fetchone()
                if exists:
                    c.execute(
                        "UPDATE productos SET nombre=?, proveedor=?, codigo_barras=?, precio=?, costo=?, impuesto=?, stock=?, pesable=? WHERE id_producto=?",
                        (nombre, proveedor, barra, float(precio), float(costo), int(impuesto), int(stock), int(pesable), pid)
                    )
                else:
                    c.execute(
                        "INSERT INTO productos (id_producto, nombre, proveedor, codigo_barras, precio, costo, impuesto, stock, pesable) VALUES (?,?,?,?,?,?,?,?,?)",
                        (pid, nombre, proveedor, barra, float(precio), float(costo), int(impuesto), int(stock), int(pesable))
                    )
            except Exception:
                pass
        conn.commit()

def asegurar_tablas_mysql():
    conn = conectar_mysql()
    try:
        cur = conn.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS inventario (id INT PRIMARY KEY, barra VARCHAR(50), nombre VARCHAR(255) NOT NULL, precio DECIMAL(10,2) NOT NULL, id_isv INT NOT NULL, stock INT NOT NULL, pesable TINYINT(1) NOT NULL DEFAULT 0)")
        try:
            cur.execute("SHOW COLUMNS FROM inventario")
            cols = [r[0].lower() for r in cur.fetchall()]
            if 'pesable' not in cols:
                cur.execute("ALTER TABLE inventario ADD COLUMN pesable TINYINT(1) NOT NULL DEFAULT 0")
        except Exception:
            pass
        cur.execute("CREATE TABLE IF NOT EXISTS clientes (rtn BIGINT, nombre VARCHAR(255), direccion VARCHAR(255), telefono VARCHAR(50), correo VARCHAR(255))")
        cur.execute("CREATE TABLE IF NOT EXISTS ventas (id VARCHAR(50), factura INT, nombre_articulo VARCHAR(255), valor_articulo DECIMAL(10,2), cantidad DECIMAL(10,2), subtotal DECIMAL(10,2), gravado15 DECIMAL(10,2), gravado18 DECIMAL(10,2), totalexento DECIMAL(10,2), isv15 DECIMAL(10,2), isv18 DECIMAL(10,2), grantotal DECIMAL(10,2))")
        conn.commit()
    finally:
        conn.close()

def asegurar_tabla_ventas_mysql():
    try:
        conn = conectar_mysql()
    except Exception:
        return
    try:
        cur = conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS ventas (
                id_venta INT AUTO_INCREMENT PRIMARY KEY,
                cliente VARCHAR(255),
                total DECIMAL(10,2),
                fecha VARCHAR(19),
                numero_factura VARCHAR(64),
                cai VARCHAR(64),
                exento DECIMAL(10,2) DEFAULT 0,
                gravado15 DECIMAL(10,2) DEFAULT 0,
                gravado18 DECIMAL(10,2) DEFAULT 0,
                isv15 DECIMAL(10,2) DEFAULT 0,
                isv18 DECIMAL(10,2) DEFAULT 0,
                estado VARCHAR(20) DEFAULT 'emitida',
                metodo_pago VARCHAR(255) DEFAULT '',
                efectivo DECIMAL(10,2) DEFAULT 0,
                cambio DECIMAL(10,2) DEFAULT 0,
                rtn_cliente VARCHAR(64),
                usuario VARCHAR(255)
            )
            """
        )
        try:
            cur.execute("SHOW COLUMNS FROM ventas")
            cols = [r[0].lower() for r in cur.fetchall()]
            needed = [
                'id_venta','cliente','total','fecha','numero_factura','cai','exento','gravado15','gravado18','isv15','isv18','estado','metodo_pago','efectivo','cambio','rtn_cliente','usuario'
            ]
            for col in needed:
                if col not in cols:
                    # Tipos mínimos para compatibilidad
                    if col in ('id_venta',):
                        try:
                            cur.execute("ALTER TABLE ventas ADD COLUMN id_venta INT NOT NULL AUTO_INCREMENT PRIMARY KEY FIRST")
                        except Exception:
                            pass
                    elif col in ('total','exento','gravado15','gravado18','isv15','isv18','efectivo','cambio'):
                        cur.execute(f"ALTER TABLE ventas ADD COLUMN {col} DECIMAL(10,2) DEFAULT 0")
                    elif col in ('fecha'):
                        cur.execute("ALTER TABLE ventas ADD COLUMN fecha VARCHAR(19)")
                    elif col in ('numero_factura','cai','rtn_cliente','usuario','metodo_pago','estado','cliente'):
                        cur.execute(f"ALTER TABLE ventas ADD COLUMN {col} VARCHAR(255)")
        except Exception:
            pass
        conn.commit()
    finally:
        try:
            conn.close()
        except Exception:
            pass

def insertar_venta_encabezado_mysql(mesa, mesero, cliente, rtn_cliente, total, fecha,
                                    numero_factura, cai, exento, gravado15, gravado18,
                                    isv15, isv18, metodo_pago, efectivo, cambio, usuario,
                                    estado="emitida"):
    conn = conectar_mysql()
    try:
        cur = conn.cursor()
        asegurar_tabla_ventas_mysql()
        cur.execute(
            """
            INSERT INTO ventas (
                cliente, rtn_cliente, total, fecha, numero_factura, cai,
                exento, gravado15, gravado18, isv15, isv18,
                metodo_pago, efectivo, cambio, usuario, estado
            ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """,
            (
                cliente, rtn_cliente, total, fecha, numero_factura, cai,
                exento, gravado15, gravado18, isv15, isv18,
                metodo_pago, efectivo, cambio, usuario, estado
            )
        )
        conn.commit()
        try:
            cur.execute("SELECT LAST_INSERT_ID()")
            rid = cur.fetchone()[0]
        except Exception:
            try:
                rid = cur.lastrowid
            except Exception:
                rid = None
        return rid
    finally:
        try:
            conn.close()
        except Exception:
            pass

def insertar_venta_detalle_mysql(id_venta, numero_factura, codigo, nombre, precio, cantidad, subtotal,
                   gravado15, gravado18, totalexento, isv15, isv18, grantotal):
    conn = conectar_mysql()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS ventas_detalle (
                id_detalle INT AUTO_INCREMENT PRIMARY KEY,
                id_venta INT,
                numero_factura VARCHAR(64),
                id VARCHAR(50),
                nombre_articulo VARCHAR(255),
                valor_articulo DECIMAL(10,2),
                cantidad DECIMAL(10,2),
                subtotal DECIMAL(10,2),
                gravado15 DECIMAL(10,2),
                gravado18 DECIMAL(10,2),
                totalexento DECIMAL(10,2),
                isv15 DECIMAL(10,2),
                isv18 DECIMAL(10,2),
                grantotal DECIMAL(10,2)
            )
            """
        )
        cursor.execute(
            "INSERT INTO ventas_detalle (id_venta, numero_factura, id, nombre_articulo, valor_articulo, cantidad, subtotal, gravado15, gravado18, totalexento, isv15, isv18, grantotal) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
            (id_venta, numero_factura, codigo, nombre, precio, cantidad, subtotal, gravado15, gravado18, totalexento, isv15, isv18, grantotal)
        )
        conn.commit()
    finally:
        try:
            conn.close()
        except Exception:
            pass

def poblar_inventario_desde_compras_si_vacio():
    conn = conectar_mysql()
    try:
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM inventario")
        cnt = cur.fetchone()[0]
        if cnt == 0:
            cur.execute("SELECT DISTINCT codigo, descripcion, costo FROM compras WHERE codigo IS NOT NULL AND descripcion IS NOT NULL")
            rows = cur.fetchall()
            for codigo, descripcion, costo in rows:
                try:
                    cur.execute("INSERT INTO inventario (id, barra, nombre, precio, id_isv, stock) VALUES (%s, %s, %s, %s, %s, %s)", (int(codigo), None, descripcion, float(costo), 3, 0))
                except Exception:
                    pass
            conn.commit()
    finally:
        conn.close()

def obtener_clientes():
    try:
        asegurar_tablas_mysql()
        try:
            poblar_clientes_desde_sqlite_si_vacio()
        except Exception:
            pass
        conn = conectar_mysql()
        try:
            cur = conn.cursor()
            try:
                cur.execute("SHOW COLUMNS FROM clientes")
                cols = [r[0].lower() for r in cur.fetchall()]
            except Exception:
                cols = []
            rtn_col = "rtn" if "rtn" in cols else ("rtn_cliente" if "rtn_cliente" in cols else "rtn")
            cur.execute(f"SELECT {rtn_col} FROM clientes")
            return cur.fetchall()
        finally:
            conn.close()
    except Exception:
        asegurar_tabla_clientes_sqlite()
        with conectar() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute("PRAGMA table_info(clientes)")
                cols = [r[1].lower() for r in cursor.fetchall()]
            except Exception:
                cols = []
            rtn_col = "rtn" if "rtn" in cols else ("rtn_cliente" if "rtn_cliente" in cols else "rtn")
            cursor.execute(f"SELECT {rtn_col} FROM clientes")
            return cursor.fetchall()

def poblar_clientes_desde_sqlite_si_vacio():
    try:
        connm = conectar_mysql()
    except Exception:
        return
    curm = connm.cursor()
    curm.execute("SELECT COUNT(*) FROM clientes")
    cnt = curm.fetchone()[0]
    if cnt and int(cnt) > 0:
        try:
            connm.close()
        except Exception:
            pass
        return
    try:
        with conectar() as conns:
            curs = conns.cursor()
            try:
                curs.execute("PRAGMA table_info(clientes)")
                cols = [r[1].lower() for r in curs.fetchall()]
            except Exception:
                cols = []
            nombre_col = "nombre" if "nombre" in cols else None
            rtn_col = "rtn" if "rtn" in cols else ("rtn_cliente" if "rtn_cliente" in cols else None)
            tel_col = "telefono" if "telefono" in cols else None
            cor_col = "correo" if "correo" in cols else None
            if nombre_col and rtn_col:
                select_cols = ", ".join([c for c in [nombre_col, rtn_col, tel_col, cor_col] if c])
                curs.execute(f"SELECT {select_cols} FROM clientes")
                rows = curs.fetchall()
                curm.execute("SHOW COLUMNS FROM clientes")
                mcols = [r[0].lower() for r in curm.fetchall()]
                m_rtn_col = "rtn" if "rtn" in mcols else ("rtn_cliente" if "rtn_cliente" in mcols else "rtn")
                has_tel = "telefono" in mcols
                has_cor = "correo" in mcols
                has_dir = "direccion" in mcols
                for row in rows:
                    nombre = row[0]
                    rtn = row[1]
                    telefono = row[2] if tel_col else None
                    correo = row[3] if cor_col else None
                    fields = ["nombre", m_rtn_col]
                    values = [nombre, rtn]
                    if has_dir:
                        fields.append("direccion"); values.append("")
                    if has_tel:
                        fields.append("telefono"); values.append(telefono)
                    if has_cor:
                        fields.append("correo"); values.append(correo)
                    placeholders = ",".join(["%s"]*len(values))
                    curm.execute(f"INSERT INTO clientes ({', '.join(fields)}) VALUES ({placeholders})", tuple(values))
                connm.commit()
    except Exception:
        pass
    curm.execute("SELECT COUNT(*) FROM clientes")
    cnt2 = curm.fetchone()[0]
    if not cnt2 or int(cnt2) == 0:
        curm.execute("SHOW COLUMNS FROM clientes")
        mcols = [r[0].lower() for r in cur.fetchall()] if False else [r[0].lower() for r in curm.fetchall()]
        m_rtn_col = "rtn" if "rtn" in mcols else ("rtn_cliente" if "rtn_cliente" in mcols else "rtn")
        fields = [m_rtn_col, "nombre"]
        values = [0, "CONSUMIDOR FINAL"]
        if "direccion" in mcols:
            fields.append("direccion"); values.append("")
        if "telefono" in mcols:
            fields.append("telefono"); values.append("")
        if "correo" in mcols:
            fields.append("correo"); values.append("")
        placeholders = ",".join(["%s"]*len(values))
        curm.execute(f"INSERT INTO clientes ({', '.join(fields)}) VALUES ({placeholders})", tuple(values))
        connm.commit()
    try:
        connm.close()
    except Exception:
        pass

def obtener_nombre_cliente(rtn):
    try:
        conn = conectar_mysql()
        try:
            cur = conn.cursor()
            try:
                cur.execute("SHOW COLUMNS FROM clientes")
                cols = [r[0].lower() for r in cur.fetchall()]
            except Exception:
                cols = []
            rtn_col = "rtn" if "rtn" in cols else ("rtn_cliente" if "rtn_cliente" in cols else "rtn")
            cur.execute(f"SELECT nombre FROM clientes WHERE {rtn_col} = %s", (rtn,))
            return cur.fetchone()
        finally:
            conn.close()
    except Exception:
        asegurar_tabla_clientes_sqlite()
        with conectar() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute("PRAGMA table_info(clientes)")
                cols = [r[1].lower() for r in cursor.fetchall()]
            except Exception:
                cols = []
            rtn_col = "rtn" if "rtn" in cols else ("rtn_cliente" if "rtn_cliente" in cols else "rtn")
            cursor.execute(f"SELECT nombre FROM clientes WHERE {rtn_col} = ?", (rtn,))
            return cursor.fetchone()

def obtener_clientes_detalle():
    try:
        asegurar_tablas_mysql()
        conn = conectar_mysql()
        try:
            cur = conn.cursor()
            try:
                cur.execute("SHOW COLUMNS FROM clientes")
                cols = [r[0].lower() for r in cur.fetchall()]
            except Exception:
                cols = []
            rtn_col = "rtn" if "rtn" in cols else ("rtn_cliente" if "rtn_cliente" in cols else "rtn")
            cur.execute(f"SELECT {rtn_col}, nombre FROM clientes ORDER BY nombre")
            return cur.fetchall()
        finally:
            conn.close()
    except Exception:
        asegurar_tabla_clientes_sqlite()
        with conectar() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute("PRAGMA table_info(clientes)")
                cols = [r[1].lower() for r in cursor.fetchall()]
            except Exception:
                cols = []
            rtn_col = "rtn" if "rtn" in cols else ("rtn_cliente" if "rtn_cliente" in cols else "rtn")
            cursor.execute(f"SELECT {rtn_col}, nombre FROM clientes ORDER BY nombre")
            return cursor.fetchall()

def obtener_productos():
    try:
        asegurar_tablas_mysql()
        poblar_inventario_desde_compras_si_vacio()
        conn = conectar_mysql()
        try:
            cur = conn.cursor()
            cur.execute("SELECT id FROM inventario")
            return cur.fetchall()
        finally:
            conn.close()
    except Exception:
        asegurar_tabla_inventario_sqlite()
        with conectar() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM inventario")
            return cursor.fetchall()

def obtener_info_producto(codigo):
    try:
        asegurar_columna_pesable_productos_sqlite()
        with conectar() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute("SELECT id_producto, nombre, precio, impuesto, pesable FROM productos WHERE id_producto = ? OR codigo_barras = ?", (codigo, codigo))
            except Exception:
                cursor.execute("SELECT id_producto, nombre, precio, impuesto FROM productos WHERE id_producto = ? OR codigo_barras = ?", (codigo, codigo))
            row = cursor.fetchone()
            if not row:
                return None
            try:
                imp = str(row[3]).strip().lower()
            except Exception:
                imp = ""
            if imp in ("15", "1"):
                isv = 1
            elif imp in ("18", "2"):
                isv = 2
            else:
                isv = 3
            try:
                pesable = int(row[4])
            except Exception:
                pesable = 0
            return (row[1], float(row[2]), isv, pesable)
    except Exception:
        return None

def verificar_stock(codigo, cantidad):
    try:
        asegurar_tablas_mysql()
        conn = conectar_mysql()
        try:
            cur = conn.cursor()
            cur.execute("SELECT stock FROM inventario WHERE id = %s OR barra = %s", (codigo, codigo))
            result = cur.fetchone()
            return result and result[0] >= cantidad
        finally:
            conn.close()
    except sqlite3.OperationalError:
        return False
    except Exception:
        asegurar_tabla_inventario_sqlite()
        with conectar() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT stock FROM inventario WHERE id = ? OR barra = ?", (codigo, codigo))
            result = cursor.fetchone()
            return result and result[0] >= cantidad

def obtener_max_factura():
    asegurar_tabla_ventas_sqlite()
    with conectar() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT MAX(factura) FROM ventas")
        return cursor.fetchone()[0]

def insertar_venta(conn, factura, codigo, nombre, precio, cantidad, subtotal,
                   gravado15, gravado18, totalexento, isv15, isv18, grantotal):
    asegurar_tabla_ventas_sqlite()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO ventas(
            id, factura, nombre_articulo, valor_articulo, cantidad, subtotal,
            gravado15, gravado18, totalexento, isv15, isv18, grantotal
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (codigo, factura, nombre, precio, cantidad, subtotal,
         gravado15, gravado18, totalexento, isv15, isv18, grantotal)
    )

def insertar_venta_mysql(factura, codigo, nombre, precio, cantidad, subtotal,
                   gravado15, gravado18, totalexento, isv15, isv18, grantotal):
    conn = conectar_mysql()
    try:
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS ventas (id VARCHAR(50), factura INT, nombre_articulo VARCHAR(255), valor_articulo DECIMAL(10,2), cantidad DECIMAL(10,2), subtotal DECIMAL(10,2), gravado15 DECIMAL(10,2), gravado18 DECIMAL(10,2), totalexento DECIMAL(10,2), isv15 DECIMAL(10,2), isv18 DECIMAL(10,2), grantotal DECIMAL(10,2))")
        cursor.execute(
            "INSERT INTO ventas (id, factura, nombre_articulo, valor_articulo, cantidad, subtotal, gravado15, gravado18, totalexento, isv15, isv18, grantotal) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
            (codigo, factura, nombre, precio, cantidad, subtotal, gravado15, gravado18, totalexento, isv15, isv18, grantotal)
        )
        conn.commit()
    finally:
        conn.close()

def insertar_factura_resumen_mysql(factura, cliente, gravado15, gravado18, exento, isv15, isv18, grantotal, pagado, cambio, metodo_pago):
    conn = conectar_mysql()
    try:
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS facturas (factura INT, cliente VARCHAR(255), gravado15 DECIMAL(16,13), gravado18 DECIMAL(15,13), totalexento DECIMAL(10,2), isv15 DECIMAL(16,14), isv18 DECIMAL(15,14), grantotal DECIMAL(10,2), fecha VARCHAR(19), pagado VARCHAR(20), cambio VARCHAR(20), metodo_pago VARCHAR(50))")
        from datetime import datetime
        fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute(
            "INSERT INTO facturas (factura, cliente, gravado15, gravado18, totalexento, isv15, isv18, grantotal, fecha, pagado, cambio, metodo_pago) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
            (factura, cliente, gravado15, gravado18, exento, isv15, isv18, grantotal, fecha, str(pagado), str(cambio), metodo_pago)
        )
        conn.commit()
    finally:
        conn.close()

def actualizar_stock(conn, codigo, cantidad):
    asegurar_tabla_inventario_sqlite()
    cursor = conn.cursor()
    cursor.execute("UPDATE inventario SET stock = stock - ? WHERE id = ? OR barra = ?", (cantidad, codigo, codigo))

def actualizar_stock_mysql(codigo, cantidad):
    conn = conectar_mysql()
    try:
        cur = conn.cursor()
        cur.execute("UPDATE inventario SET stock = stock - %s WHERE id = %s OR barra = %s", (cantidad, codigo, codigo))
        conn.commit()
    finally:
        conn.close()

def obtener_ventas_por_factura(factura_id):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 
            v.id,         -- Código
            v.nombre_articulo, 
            v.cantidad, 
            v.valor_articulo, 
            v.subtotal,
            p.id_isv               -- Tipo de ISV (15, 18, E)
        FROM ventas v
        JOIN inventario p ON v.id = p.id
        WHERE v.factura = ?
    """, (factura_id,))
    resultado = cursor.fetchall()
    conn.close()
    return resultado

def asegurar_tabla_compania_sqlite():
    with conectar() as conn:
        c = conn.cursor()
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS compañia (
                id_cia INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre_cia TEXT,
                direccion1 TEXT,
                direccion2 TEXT,
                rtn_cia TEXT,
                correo TEXT,
                telefono TEXT
            )
            """
        )
        conn.commit()
        
def asegurar_tabla_compania_mysql():
    try:
        conn = conectar_mysql()
    except Exception:
        return
    try:
        cur = conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS `compañia` (
                `id_cia` INT AUTO_INCREMENT PRIMARY KEY,
                `nombre_cia` TEXT,
                `direccion1` TEXT,
                `direccion2` TEXT,
                `rtn_cia` VARCHAR(64),
                `correo` TEXT,
                `telefono` VARCHAR(64)
            )
            """
        )
        try:
            cur.execute("ALTER TABLE `compañia` MODIFY `nombre_cia` TEXT")
        except Exception:
            pass
        try:
            cur.execute("ALTER TABLE `compañia` MODIFY `direccion1` TEXT")
        except Exception:
            pass
        try:
            cur.execute("ALTER TABLE `compañia` MODIFY `direccion2` TEXT")
        except Exception:
            pass
        try:
            cur.execute("ALTER TABLE `compañia` MODIFY `correo` TEXT")
        except Exception:
            pass
        try:
            cur.execute("ALTER TABLE `compañia` MODIFY `rtn_cia` VARCHAR(64)")
        except Exception:
            pass
        conn.commit()
    finally:
        conn.close()

def asegurar_tabla_facturas_sqlite():
    with conectar() as conn:
        c = conn.cursor()
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS facturas (
                factura INTEGER,
                cliente TEXT,
                gravado15 REAL,
                gravado18 REAL,
                totalexento REAL,
                isv15 REAL,
                isv18 REAL,
                grantotal REAL,
                fecha TEXT,
                pagado REAL,
                cambio REAL,
                metodo_pago TEXT
            )
            """
        )
        conn.commit()

def obtener_datos_compania():
    try:
        asegurar_tabla_compania_mysql()
        conn = conectar_mysql()
        try:
            cur = conn.cursor()
            try:
                cur.execute("SELECT nombre_cia, direccion1, direccion2, rtn_cia, correo, telefono FROM `compañia` LIMIT 1")
            except Exception:
                cur.execute("SELECT nombre_cia, direccion1, direccion2, rtn_cia, correo, telefono FROM compania LIMIT 1")
            return cur.fetchone()
        finally:
            conn.close()
    except Exception:
        asegurar_tabla_compania_sqlite()
        with conectar() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute("SELECT nombre_cia, direccion1, direccion2, rtn_cia, correo, telefono FROM compañia LIMIT 1")
            except Exception:
                cursor.execute("SELECT nombre_cia, direccion1, direccion2, rtn_cia, correo, telefono FROM compania LIMIT 1")
            return cursor.fetchone()

def guardar_datos_compania(valores):
    # valores: [nombre_cia, direccion1, direccion2, rtn_cia, correo, telefono]
    try:
        asegurar_tabla_compania_mysql()
        conn = conectar_mysql()
        try:
            cur = conn.cursor()
            try:
                cur.execute("SELECT id_cia FROM `compañia` LIMIT 1")
            except Exception:
                cur.execute("SELECT id_cia FROM compania LIMIT 1")
            row = cur.fetchone()
            if row:
                try:
                    cur.execute(
                        "UPDATE `compañia` SET nombre_cia=%s, direccion1=%s, direccion2=%s, rtn_cia=%s, correo=%s, telefono=%s WHERE id_cia=%s",
                        (*valores, row[0])
                    )
                except Exception:
                    cur.execute(
                        "UPDATE compania SET nombre_cia=%s, direccion1=%s, direccion2=%s, rtn_cia=%s, correo=%s, telefono=%s WHERE id_cia=%s",
                        (*valores, row[0])
                    )
            else:
                try:
                    cur.execute(
                        "INSERT INTO `compañia` (nombre_cia, direccion1, direccion2, rtn_cia, correo, telefono) VALUES (%s,%s,%s,%s,%s,%s)",
                        valores
                    )
                except Exception:
                    cur.execute(
                        "INSERT INTO compania (nombre_cia, direccion1, direccion2, rtn_cia, correo, telefono) VALUES (%s,%s,%s,%s,%s,%s)",
                        valores
                    )
            conn.commit()
            return True
        finally:
            conn.close()
    except Exception:
        asegurar_tabla_compania_sqlite()
        with conectar() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute("SELECT id_cia FROM compañia LIMIT 1")
            except Exception:
                cursor.execute("SELECT id_cia FROM compania LIMIT 1")
            row = cursor.fetchone()
            if row:
                try:
                    cursor.execute(
                        "UPDATE compañia SET nombre_cia=?, direccion1=?, direccion2=?, rtn_cia=?, correo=?, telefono=? WHERE id_cia=?",
                        (*valores, row[0])
                    )
                except Exception:
                    cursor.execute(
                        "UPDATE compania SET nombre_cia=?, direccion1=?, direccion2=?, rtn_cia=?, correo=?, telefono=? WHERE id_cia=?",
                        (*valores, row[0])
                    )
            else:
                try:
                    cursor.execute(
                        "INSERT INTO compañia (nombre_cia, direccion1, direccion2, rtn_cia, correo, telefono) VALUES (?,?,?,?,?,?)",
                        valores
                    )
                except Exception:
                    cursor.execute(
                        "INSERT INTO compania (nombre_cia, direccion1, direccion2, rtn_cia, correo, telefono) VALUES (?,?,?,?,?,?)",
                        valores
                    )
            conn.commit()
            return True

import sqlite3
from datetime import datetime

def insertar_factura_resumen(conn, factura, cliente, gravado15, gravado18, exento, isv15, isv18, grantotal, pagado, cambio, metodo_pago):
    fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor = conn.cursor()
    asegurar_tabla_facturas_sqlite()
    cursor.execute("""
        INSERT INTO facturas (
            factura, cliente, gravado15, gravado18, totalexento,
            isv15, isv18, grantotal, fecha, pagado, cambio, metodo_pago
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        factura, cliente, gravado15, gravado18, exento,
        isv15, isv18, grantotal, fecha, pagado, cambio, metodo_pago
    ))

def obtener_totales_factura(factura_id):
    conn = conectar()
    c = conn.cursor()
    c.execute("""
        SELECT gravado15, gravado18, totalexento, isv15, isv18, grantotal, pagado, cambio
        FROM facturas 
        WHERE factura = ?
    """, (factura_id,))
    return c.fetchone()

def obtener_info_producto(codigo):
    try:
        asegurar_columna_pesable_productos_sqlite()
        with conectar() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute("SELECT id_producto, nombre, precio, impuesto, pesable FROM productos WHERE id_producto = ? OR codigo_barras = ?", (codigo, codigo))
            except Exception:
                cursor.execute("SELECT id_producto, nombre, precio, impuesto FROM productos WHERE id_producto = ? OR codigo_barras = ?", (codigo, codigo))
            row = cursor.fetchone()
            if not row:
                return None
            try:
                imp = str(row[3]).strip().lower()
            except Exception:
                imp = ""
            if imp in ("15", "1"):
                isv = 1
            elif imp in ("18", "2"):
                isv = 2
            else:
                isv = 3
            try:
                pesable = int(row[4])
            except Exception:
                pesable = 0
            return (row[0], row[1], float(row[2]), isv, pesable)
    except Exception:
        return None
    
def obtener_metodo_pago_factura(factura_id):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT metodo_pago FROM facturas WHERE factura = ?", (factura_id,))
    resultado = cursor.fetchone()
    conn.close()
    return resultado[0] if resultado else "Efectivo"
