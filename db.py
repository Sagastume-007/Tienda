import os
import sqlite3

# Detectar si estamos usando PostgreSQL o SQLite
DATABASE_URL = os.environ.get('DATABASE_URL')
USE_POSTGRES = DATABASE_URL is not None

if USE_POSTGRES:
    import psycopg2
    from psycopg2.extras import RealDictCursor

def conectar():
    """Conectar a PostgreSQL o SQLite según el entorno"""
    if USE_POSTGRES:
        # PostgreSQL en producción
        conn = psycopg2.connect(DATABASE_URL)
        return conn
    else:
        # SQLite en desarrollo local
        conn = sqlite3.connect('pos.db', check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn

def asegurar_tabla_productos_sqlite():
    """Crear tabla productos si no existe"""
    conn = conectar()
    cur = conn.cursor()
    
    if USE_POSTGRES:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS productos (
                id_producto SERIAL PRIMARY KEY,
                nombre VARCHAR(255) NOT NULL,
                codigo_barras VARCHAR(100),
                precio DECIMAL(10,2) NOT NULL,
                impuesto INTEGER DEFAULT 3,
                stock INTEGER DEFAULT 0,
                pesable INTEGER DEFAULT 0,
                UNIQUE(codigo_barras)
            )
        """)
    else:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS productos (
                id_producto INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                codigo_barras TEXT,
                precio REAL NOT NULL,
                impuesto INTEGER DEFAULT 3,
                stock INTEGER DEFAULT 0,
                pesable INTEGER DEFAULT 0,
                UNIQUE(codigo_barras)
            )
        """)
    
    conn.commit()
    conn.close()

def asegurar_columna_pesable_productos_sqlite():
    """Agregar columna pesable si no existe"""
    conn = conectar()
    cur = conn.cursor()
    
    try:
        if USE_POSTGRES:
            # PostgreSQL: verificar si la columna existe
            cur.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='productos' AND column_name='pesable'
            """)
            if not cur.fetchone():
                cur.execute("ALTER TABLE productos ADD COLUMN pesable INTEGER DEFAULT 0")
        else:
            # SQLite: intentar agregar columna
            cur.execute("ALTER TABLE productos ADD COLUMN pesable INTEGER DEFAULT 0")
        
        conn.commit()
    except Exception as e:
        # La columna ya existe o hubo otro error
        conn.rollback()
    finally:
        conn.close()

def asegurar_tabla_ventas_sqlite():
    """Crear tabla ventas si no existe"""
    conn = conectar()
    cur = conn.cursor()
    
    if USE_POSTGRES:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS ventas (
                id_venta SERIAL PRIMARY KEY,
                factura INTEGER NOT NULL,
                codigo_producto VARCHAR(50),
                descripcion VARCHAR(255),
                precio DECIMAL(10,2),
                cantidad DECIMAL(10,2),
                subtotal DECIMAL(10,2),
                gravado15 DECIMAL(10,2) DEFAULT 0,
                gravado18 DECIMAL(10,2) DEFAULT 0,
                exento DECIMAL(10,2) DEFAULT 0,
                isv15 DECIMAL(10,2) DEFAULT 0,
                isv18 DECIMAL(10,2) DEFAULT 0,
                total DECIMAL(10,2)
            )
        """)
    else:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS ventas (
                id_venta INTEGER PRIMARY KEY AUTOINCREMENT,
                factura INTEGER NOT NULL,
                codigo_producto TEXT,
                descripcion TEXT,
                precio REAL,
                cantidad REAL,
                subtotal REAL,
                gravado15 REAL DEFAULT 0,
                gravado18 REAL DEFAULT 0,
                exento REAL DEFAULT 0,
                isv15 REAL DEFAULT 0,
                isv18 REAL DEFAULT 0,
                total REAL
            )
        """)
    
    conn.commit()
    conn.close()

def asegurar_tabla_facturas_sqlite():
    """Crear tabla facturas si no existe"""
    conn = conectar()
    cur = conn.cursor()
    
    if USE_POSTGRES:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS facturas (
                factura INTEGER PRIMARY KEY,
                cliente VARCHAR(255),
                gravado15 DECIMAL(10,2) DEFAULT 0,
                gravado18 DECIMAL(10,2) DEFAULT 0,
                exento DECIMAL(10,2) DEFAULT 0,
                isv15 DECIMAL(10,2) DEFAULT 0,
                isv18 DECIMAL(10,2) DEFAULT 0,
                total DECIMAL(10,2),
                pagado DECIMAL(10,2),
                cambio DECIMAL(10,2),
                metodo_pago VARCHAR(50),
                fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
    else:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS facturas (
                factura INTEGER PRIMARY KEY,
                cliente TEXT,
                gravado15 REAL DEFAULT 0,
                gravado18 REAL DEFAULT 0,
                exento REAL DEFAULT 0,
                isv15 REAL DEFAULT 0,
                isv18 REAL DEFAULT 0,
                total REAL,
                pagado REAL,
                cambio REAL,
                metodo_pago TEXT,
                fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
    
    conn.commit()
    conn.close()

def sembrar_productos_iniciales():
    """Agregar productos de ejemplo si la tabla está vacía"""
    conn = conectar()
    cur = conn.cursor()
    
    # Verificar si ya hay productos
    cur.execute("SELECT COUNT(*) FROM productos")
    result = cur.fetchone()
    count = result[0] if USE_POSTGRES else result[0]
    
    if count == 0:
        productos = [
            ('Coca Cola 2L', '7501055300013', 25.00, 1, 50, 0),
            ('Pan Bimbo Blanco', '7501000110014', 18.50, 1, 30, 0),
            ('Arroz Supremo 1kg', '7501234567890', 15.00, 3, 100, 0),
            ('Aceite Capullo 1L', '7501098765432', 35.00, 1, 40, 0),
            ('Huevos Kacao 12pz', '7501234509876', 42.00, 3, 60, 0),
            ('Plátano Verde', '2001', 8.00, 3, 0, 1),
            ('Tomate', '2002', 12.00, 3, 0, 1),
            ('Cebolla', '2003', 10.00, 3, 0, 1),
        ]
        
        if USE_POSTGRES:
            cur.executemany(
                """INSERT INTO productos (nombre, codigo_barras, precio, impuesto, stock, pesable) 
                   VALUES (%s, %s, %s, %s, %s, %s)""",
                productos
            )
        else:
            cur.executemany(
                """INSERT INTO productos (nombre, codigo_barras, precio, impuesto, stock, pesable) 
                   VALUES (?, ?, ?, ?, ?, ?)""",
                productos
            )
        
        conn.commit()
    
    conn.close()

def obtener_info_producto(codigo):
    """Obtener información de un producto por código o ID"""
    conn = conectar()
    cur = conn.cursor()
    
    placeholder = "%s" if USE_POSTGRES else "?"
    
    # Intentar por código de barras
    cur.execute(
        f"SELECT id_producto, nombre, precio, impuesto, pesable FROM productos WHERE codigo_barras = {placeholder}",
        (codigo,)
    )
    result = cur.fetchone()
    
    # Si no se encuentra, intentar por ID
    if not result:
        try:
            id_prod = int(codigo)
            cur.execute(
                f"SELECT id_producto, nombre, precio, impuesto, pesable FROM productos WHERE id_producto = {placeholder}",
                (id_prod,)
            )
            result = cur.fetchone()
        except ValueError:
            pass
    
    conn.close()
    
    if result:
        if USE_POSTGRES:
            return (result[0], result[1], result[2], result[3], result[4])
        else:
            return result
    return None

def obtener_max_factura():
    """Obtener el número de factura más alto"""
    conn = conectar()
    cur = conn.cursor()
    
    cur.execute("SELECT MAX(factura) FROM facturas")
    result = cur.fetchone()
    conn.close()
    
    max_factura = result[0] if result and result[0] else 0
    return max_factura

def insertar_venta(conn, factura, codigo, descripcion, precio, cantidad, subtotal, 
                   gravado15, gravado18, exento, isv15, isv18, total):
    """Insertar un detalle de venta"""
    cur = conn.cursor()
    
    if USE_POSTGRES:
        cur.execute("""
            INSERT INTO ventas (factura, codigo_producto, descripcion, precio, cantidad, subtotal,
                              gravado15, gravado18, exento, isv15, isv18, total)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (factura, codigo, descripcion, precio, cantidad, subtotal,
              gravado15, gravado18, exento, isv15, isv18, total))
    else:
        cur.execute("""
            INSERT INTO ventas (factura, codigo_producto, descripcion, precio, cantidad, subtotal,
                              gravado15, gravado18, exento, isv15, isv18, total)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (factura, codigo, descripcion, precio, cantidad, subtotal,
              gravado15, gravado18, exento, isv15, isv18, total))

def insertar_factura_resumen(conn, factura, cliente, gravado15, gravado18, exento,
                            isv15, isv18, total, pagado, cambio, metodo_pago):
    """Insertar resumen de factura"""
    cur = conn.cursor()
    
    if USE_POSTGRES:
        cur.execute("""
            INSERT INTO facturas (factura, cliente, gravado15, gravado18, exento, isv15, isv18,
                                total, pagado, cambio, metodo_pago)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (factura, cliente, gravado15, gravado18, exento, isv15, isv18,
              total, pagado, cambio, metodo_pago))
    else:
        cur.execute("""
            INSERT INTO facturas (factura, cliente, gravado15, gravado18, exento, isv15, isv18,
                                total, pagado, cambio, metodo_pago)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (factura, cliente, gravado15, gravado18, exento, isv15, isv18,
              total, pagado, cambio, metodo_pago))

def actualizar_stock(conn, codigo_producto, cantidad_vendida):
    """Actualizar el stock de un producto"""
    cur = conn.cursor()
    
    placeholder = "%s" if USE_POSTGRES else "?"
    
    try:
        id_prod = int(codigo_producto)
        cur.execute(
            f"UPDATE productos SET stock = stock - {placeholder} WHERE id_producto = {placeholder}",
            (cantidad_vendida, id_prod)
        )
    except ValueError:
        cur.execute(
            f"UPDATE productos SET stock = stock - {placeholder} WHERE codigo_barras = {placeholder}",
            (cantidad_vendida, codigo_producto)
        )
