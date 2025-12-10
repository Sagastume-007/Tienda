# utils.py

def limpiar_entry(entry, readonly=True):
    """Limpia un entry y lo deja opcionalmente en modo readonly."""
    entry.configure(state="normal")
    entry.delete(0, "end")
    if readonly:
        entry.configure(state="readonly")

def insertar_valor(entry, valor, readonly=True):
    """Inserta un valor en un entry y lo deja opcionalmente en modo readonly."""
    entry.configure(state="normal")
    entry.delete(0, "end")
    entry.insert(0, valor)
    if readonly:
        entry.configure(state="readonly")

def es_numero(valor):
    """Retorna True si el valor se puede convertir a número, sino False."""
    try:
        float(valor)
        return True
    except ValueError:
        return False

def formato_lempiras(valor):
    try:
        v = float(valor)
    except Exception:
        return str(valor)
    return f"L {v:,.2f}"
