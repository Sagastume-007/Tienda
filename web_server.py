import sqlite3
import os
import random
import string
from wsgiref.simple_server import make_server
from urllib.parse import parse_qs, urlencode
from db import (
    conectar,
    asegurar_tabla_productos_sqlite,
    asegurar_columna_pesable_productos_sqlite,
    sembrar_productos_iniciales,
    obtener_info_producto,
    obtener_max_factura,
    insertar_venta,
    insertar_factura_resumen,
    asegurar_tabla_ventas_sqlite,
    asegurar_tabla_facturas_sqlite,
    actualizar_stock,
)
# Define if using PostgreSQL (set to False for SQLite)
USE_POSTGRES = os.environ.get('USE_POSTGRES', 'false').lower() == 'true'

def html_page(title, body_html):
    return (
        "<!DOCTYPE html>\n"
        "<html lang=\"es\">\n"
        "<head>\n"
        "    <meta charset=\"utf-8\" />\n"
        "    <meta name=\"viewport\" content=\"width=device-width, height=device-height, initial-scale=1, minimum-scale=1, maximum-scale=1, user-scalable=no, viewport-fit=cover\" />\n"
        "    <title>" + str(title) + "</title>\n"
        "    <style>\n"
        "        :root { --primario: #74c69d; --borde: #ced4da; --texto: #2c3e50; }\n"
        "        html, body { width:100%; height:100%; overflow-x:hidden; -webkit-text-size-adjust:100%; -ms-text-size-adjust:100%; text-size-adjust:100%; }\n"
        "        *, *::before, *::after { box-sizing: border-box; }\n"
        "        body { font-family: Segoe UI, Arial, sans-serif; background: #ffffff; color: var(--texto); margin: 0; }\n"
        "        header { background: #f1faee; border-bottom: 2px solid var(--primario); padding: 12px 16px; }\n"
        "        header a { text-decoration: none; color: var(--texto); font-weight: bold; }\n"
        "        .container { width: 100%; max-width: 100vw; margin: 0; background: #fff; padding: 16px 16px; border: none; border-radius: 0; box-sizing: border-box; overflow-x: visible; min-height: 100vh; display: flex; flex-direction: column; }\n"
        "        table { width: 100%; border-collapse: collapse; }\n"
        "        th, td { padding: 8px; border-bottom: 1px solid #eee; text-align: left; }\n"
        "        th { background: #FFF9E6; color: #2E7D32; }\n"
        "        .btn { display: inline-block; background: var(--primario); color: #fff; padding: 10px 14px; border-radius: 10px; text-decoration: none; border: none; cursor: pointer; font-weight: bold; font-size:16px; touch-action: manipulation; -webkit-tap-highlight-color: transparent; }\n"
        "        button { font-size:16px; touch-action: manipulation; }\n"
        "        .btn.secondary { background: #457b9d; }\n"
        "        .btn.danger { background: #e63946; }\n"
        "        .btn.success { background: #74c69d; }\n"
        "        .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }\n"
        "        input, select { width: 100%; padding: 8px; border-radius: 6px; border: 1px solid #ccc; font-size:16px; }\n"
        "        .actions { display: flex; gap: 8px; }\n"
        "        .msg { padding: 8px; border-radius: 6px; margin-bottom: 12px; }\n"
        "        .msg.error { background: #ffe8e8; border: 1px solid #e63946; }\n"
        "        .msg.ok { background: #e8fff0; border: 1px solid #74c69d; }\n"
        "        .layout { display: grid; grid-template-columns: 10fr 8fr 36px; gap: 16px; align-items:start; }\n"
        "        .panel { background: #ffffff; border: 1px solid var(--borde); border-radius: 10px; padding: 10px; }\n"
        "        .banner { background:#E0F7F4; border:none; border-radius:10px; padding:12px; position:relative; margin-bottom:10px; display:flex; align-items:center; justify-content:center; }\n"
        "        .banner h1 { margin:0; color:#2D9CDB; font-size:18pt; font-weight:bold; }\n"
        "        #lbl-total { position:absolute; right:12px; top:10px; background:#FFE5F0; border:2px solid #B19CD9; border-radius:12px; padding:8px 16px; color:#B19CD9; font-family:'Impact'; font-size:12pt; }\n"
        "        .actions-col { display:flex; flex-direction:column; gap:12px; align-items:center; }\n"
        "        .act-btn { width:72px; height:72px; border-radius:0; background:transparent; border:none; display:flex; flex-direction:column; align-items:center; justify-content:center; text-decoration:none; color:#2c3e50; font-weight:bold; }\n"
        "        .act-btn .icon { font-size:26px; line-height:26px; }\n"
        "        .act-btn .icon svg { width:26px; height:26px; display:block; }\n"
        "        .act-btn .label { font-size:12px; }\n"
        "        .catalog-table, .catalog-table tbody tr { touch-action: manipulation; }\n"
        "        .table-wrap { overflow-x: auto; }\n"
        "        .productos-wrap { flex: 1; min-height: 0; overflow-y: auto; overflow-x: hidden; position: relative; scrollbar-width: thin; }\n"
        "        .productos-wrap::-webkit-scrollbar { height: 6px; }\n"
        "        .productos-table thead th { position: sticky; top: 0; z-index: 2; background: #FFF9E6; }\n"
        "        .ventas-cart { background-color: #FFE5F0; }\n"
        "        .ventas-cart tbody tr:nth-child(odd) { background-color: #F3E9FF; }\n"
        "        .ventas-cart tbody tr:nth-child(even) { background-color: #FFE5F0; }\n"
        "        .productos-title { font-size: 16px; margin: 0 0 8px; }\n"
        "        .modal-backdrop { position: fixed; inset: 0; background: rgba(0,0,0,0.35); display: none; align-items: center; justify-content: center; z-index: 1000; }\n"
        "        .modal { background: #ffffff; border: 1px solid var(--borde); border-radius: 12px; padding: 16px; width: 420px; max-width: 92vw; box-shadow: 0 6px 24px rgba(0,0,0,0.2); }\n"
        "        .modal h3 { margin: 0 0 8px; font-size: 18px; }\n"
        "        .modal .total-banner { background-color: #FADBD8; color: #C0392B; font-weight: bold; border: 1px solid #C0392B; border-radius: 8px; padding: 8px; text-align: center; margin-bottom: 8px; }\n"
        "        .modal .row { display: flex; gap: 8px; align-items: center; margin: 6px 0; }\n"
        "        .modal .row label { min-width: 92px; }\n"
        "        .modal .actions { display: flex; gap: 8px; justify-content: flex-end; margin-top: 12px; }\n"
"        @media (max-width: 768px) {\n"
"          .layout { grid-template-columns: 1fr; }\n"
"          .grid { grid-template-columns: 1fr; }\n"
"          .grid { gap: 6px; }\n"
"          table { min-width: 0; }\n"
"          .container { padding: 8px 8px; }\n"
"          .banner { flex-direction: column; gap: 8px; }\n"
"          .banner h1 { font-size: 18pt; }\n"
"          #lbl-total { position: static; margin-top: 6px; font-size: 18pt; }\n"
"          th, td { padding: 10px; }\n"
"          label { font-size: 14px; }\n"
"          input, select { padding: 6px; }\n"
"          .panel { padding: 8px; }\n"
"          body { padding-bottom: 92px; }\n"
"          .actions-col { position: fixed; left: 0; right: 0; bottom: 0; background: #ffffff; border-top: 1px solid var(--borde); box-shadow: 0 -2px 8px rgba(0,0,0,0.06); padding: 10px 12px; z-index: 999; flex-direction: row; gap: 8px; justify-content: space-between; }\n"
"          .act-btn { width: 100%; max-width: 120px; height: 60px; font-size:16px; touch-action: manipulation; }\n"
        "          .catalog-table { table-layout: fixed; width: 100%; }\n"
        "          .search-bar input[name='buscar'] { max-width: 55%; padding: 6px 8px; font-size:14px; }\n"
        "          .search-bar .btn { padding: 8px 12px; font-size:14px; }\n"
"          .catalog-table th, .catalog-table td { padding: 4px; font-size: 12px; box-sizing: border-box; }\n"
"          .catalog-table th:nth-child(1), .catalog-table td:nth-child(1) { width: 18%; white-space: nowrap; }\n"
"          .catalog-table th:nth-child(2), .catalog-table td:nth-child(2) { width: 50%; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }\n"
"          .catalog-table th:nth-child(3), .catalog-table td:nth-child(3) { width: 16%; text-align: right; white-space: nowrap; }\n"
"          .catalog-table th:nth-child(4), .catalog-table td:nth-child(4) { width: 12%; text-align:center; }\n"
"          .catalog-table .btn { padding: 3px 6px; font-size: 12px; }\n"
"          .ventas-cart { table-layout: fixed; width: 100%; }"
"          .ventas-cart th, .ventas-cart td { padding: 3px; font-size: 11px; box-sizing: border-box; }"
"          .ventas-cart th:nth-child(1), .ventas-cart td:nth-child(1) { width: 12%; white-space: nowrap; }"
"          .ventas-cart th:nth-child(2), .ventas-cart td:nth-child(2) { width: 30%; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }"
"          .ventas-cart th:nth-child(3), .ventas-cart td:nth-child(3) { width: 14%; white-space: nowrap; }"
"          .ventas-cart th:nth-child(3) { padding-left: 0; }\n"
"          .ventas-cart td:nth-child(3) { padding-left: 0; }\n"
"          .ventas-cart th:nth-child(4), .ventas-cart td:nth-child(4) { width: 16%; text-align: right; white-space: nowrap; }"
"          .ventas-cart th:nth-child(4) { padding-left: 0; }\n"
"          .ventas-cart td:nth-child(4) { padding-left: 0; }\n"
"          .ventas-cart th:nth-child(5), .ventas-cart td:nth-child(5) { width: 18%; text-align: right; white-space: nowrap; }"
"          .ventas-cart td:nth-child(5) { overflow: visible; }\n"
"          .ventas-cart th:nth-child(5) { padding-left: 0; }\n"
"          .ventas-cart td:nth-child(5) { padding-left: 0; }\n"
"          .ventas-cart input[name='cantidad'] { width: 52px; padding: 2px; font-size: inherit; font-family: inherit; color: inherit; }\n"
"          .ventas-cart td { vertical-align: middle; overflow: hidden; }\n"
"          .ventas-cart td:nth-child(5) { overflow: visible; }\n"
"          .ventas-cart .btn { padding: 2px 6px; font-size: 11px; }\n"
"          .ventas-cart td:nth-child(3) .qty { display:flex; align-items:center; gap: 4px; justify-content:flex-start; }\n"
"          .ventas-cart td:nth-child(3) .qty { flex-wrap: nowrap; white-space: nowrap; }\n"
"          .ventas-cart td:nth-child(3) .qty { gap: 2px; }\n"
"          .ventas-cart td:nth-child(3) .value { min-width: 38px; text-align:center; display:inline-block; flex: 0 0 auto; }\n"
"          .ventas-cart td:nth-child(3) .qty .btn { flex: 0 0 auto; }\n"
"          .ventas-cart td:nth-child(5) .total { display:flex; align-items:center; gap: 4px; justify-content:flex-start; }\n"
"          .ventas-cart td:nth-child(5) .total .value { min-width: 80px; text-align:right; display:inline-block; flex: 0 0 auto; }\n"
"          .ventas-cart td:nth-child(5) { overflow: visible; }\n"
"          .ventas-cart td:nth-child(5) .total .btn { flex: 0 0 auto; }\n"
"          .ventas-cart td:nth-child(5) .total .btn.qty-inc, .ventas-cart td:nth-child(5) .total .btn.qty-dec { font-size: 12px; }\n"
"          .ventas-cart td:nth-child(5) .total .btn.qty-inc::after { content: ''; font-size: 0; line-height: 1; }\n"
"          .ventas-cart td:nth-child(5) .total .btn.qty-dec::after { content: ''; font-size: 0; line-height: 1; }\n"
"          .ventas-cart .btn.danger { font-size: 0; }\n"
"          .ventas-cart .btn.danger::after { content: ''; font-size: 0; line-height: 1; }\n"
"          .ventas-cart td:nth-child(5) .total .btn svg { width: 13px; height: 13px; display:inline-block; }\n"
"          .ventas-cart .btn.secondary { font-size: 0; }\n"
"          .ventas-cart .btn.secondary::after { content: '\\21A9'; font-size: 13px; line-height: 1; }\n"
"        }\n"
        "        @media (max-width: 480px) {\n"
        "          .table-wrap { overflow-x: auto; -webkit-overflow-scrolling: touch; }\n"
        "          .catalog-table { table-layout: fixed; width: 100%; }\n"
        "          .search-bar input[name='buscar'] { max-width: 52%; padding: 4px 6px; font-size:12px; }\n"
        "          .search-bar .btn { padding: 6px 10px; font-size:12px; }\n"
"          .catalog-table th, .catalog-table td { padding: 3px; font-size: 10px; box-sizing: border-box; }\n"
"          .catalog-table td.precio::before { content: 'L '; font-size: 10px; margin-right:2px; }\n"
"          .catalog-table th:nth-child(1), .catalog-table td:nth-child(1) { width: 16%; white-space: nowrap; }\n"
"          .catalog-table th:nth-child(2), .catalog-table td:nth-child(2) { width: 50%; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }\n"
"          .catalog-table th:nth-child(3), .catalog-table td:nth-child(3) { width: 16%; text-align: right; white-space: nowrap; font-size:11px; }\n"
"          .catalog-table th:nth-child(4), .catalog-table td:nth-child(4) { width: 8%; text-align:center; }\n"
"          .catalog-table .btn { padding: 2px 6px; font-size: 0; }\n"
"          .catalog-table .btn::after { content: '+'; font-size: 14px; line-height: 1; }\n"
"          .ventas-cart { table-layout: fixed; width: 100%; }\n"
"          .ventas-cart th, .ventas-cart td { padding: 2px; font-size: 10px; box-sizing: border-box; }\n"
"          .ventas-cart th:nth-child(1), .ventas-cart td:nth-child(1) { width: 12%; white-space: nowrap; }\n"
"          .ventas-cart th:nth-child(2), .ventas-cart td:nth-child(2) { width: 50%; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }\n"
"          .ventas-cart th:nth-child(3), .ventas-cart td:nth-child(3) { width: 12%; white-space: nowrap; }\n"
"          .ventas-cart th:nth-child(3) { padding-left: 0; }\n"
"          .ventas-cart td:nth-child(3) { padding-left: 0; }\n"
"          .ventas-cart th:nth-child(4), .ventas-cart td:nth-child(4) { width: 10%; text-align: right; white-space: nowrap; }\n"
"          .ventas-cart th:nth-child(4) { padding-left: 0; }\n"
"          .ventas-cart td:nth-child(4) { padding-left: 0; }\n"
"          .ventas-cart th:nth-child(5), .ventas-cart td:nth-child(5) { width: 38%; white-space: nowrap; }\n"
"          .ventas-cart th:nth-child(5) { padding-left: 0; text-align: left; transform: translateX(15px); }\n"
"          .ventas-cart td:nth-child(5) { padding-left: 0; }\n"
"          .ventas-cart td:nth-child(5) { text-align: right; }\n"
"          .ventas-cart input[name='cantidad'] { width: 46px; padding: 2px; font-size: inherit; font-family: inherit; color: inherit; }\n"
"          .ventas-cart td { vertical-align: middle; overflow: hidden; }\n"
"          .ventas-cart td:nth-child(5) .total { gap: 4px; }\n"
"          .ventas-cart td:nth-child(5) .total { justify-content:flex-end; margin-left: 0; }\n"
"          .ventas-cart td:nth-child(5) .total .value { text-align:right; }\n"
"          .ventas-cart td:nth-child(5) .total .btn.qty-inc, .ventas-cart td:nth-child(5) .total .btn.qty-dec { padding: 1px 4px; font-size: 0; }\n"
"          .ventas-cart td:nth-child(5) .total .btn.qty-inc::after { content: ''; font-size: 0; line-height: 1; }\n"
"          .ventas-cart td:nth-child(5) .total .btn.qty-dec::after { content: ''; font-size: 0; line-height: 1; }\n"
"          .ventas-cart .btn.danger { font-size: 0; }\n"
"          .ventas-cart .btn.danger::after { content: ''; font-size: 0; line-height: 1; }\n"
"          .ventas-cart td:nth-child(5) .total .btn svg { width: 9px; height: 9px; display:inline-block; }\n"
"          .ventas-cart .btn.secondary { font-size: 0; }\n"
"          .ventas-cart .btn.secondary::after { content: '\\21A9'; font-size: 9px; line-height: 1; }\n"
        "        }\n"
        "        /* Desktop (>=769px) */\n"
        "        @media (min-width: 769px) {\n"
        "          .search-bar input[name='buscar'] { max-width: 40%; padding: 5px 6px; font-size: 8px; }\n"
        "          .search-bar .btn { padding: 5px 8px; font-size: 8px; }\n"
        "          .layout { grid-template-columns: 10fr 8fr 40px; }\n"
        "          .catalog-table { table-layout: fixed; width: 100%; }\n"
        "          .catalog-table th, .catalog-table td { padding: 8px; font-size: 10px; box-sizing: border-box; }\n"
        "          .catalog-table th:nth-child(1), .catalog-table td:nth-child(1) { width: 18%; white-space: nowrap; }\n"
        "          .catalog-table th:nth-child(2), .catalog-table td:nth-child(2) { width: 50%; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }\n"
        "          .catalog-table th:nth-child(3), .catalog-table td:nth-child(3) { width: 16%; text-align: right; white-space: nowrap; }\n"
        "          .catalog-table th:nth-child(4), .catalog-table td:nth-child(4) { width: 12%; text-align:center; }\n"
        "          .catalog-table .btn { padding: 4px 3px; font-size: 7px; }\n"
        "          .ventas-cart { table-layout: fixed; width: 100%; }\n"
        "          .ventas-cart th, .ventas-cart td { padding: 8px; font-size: 10px; box-sizing: border-box; }\n"
        "          .ventas-cart th:nth-child(1), .ventas-cart td:nth-child(1) { width: 12%; white-space: nowrap; }\n"
        "          .ventas-cart th:nth-child(2), .ventas-cart td:nth-child(2) { width: 50%; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }\n"
        "          .ventas-cart th:nth-child(3), .ventas-cart td:nth-child(3) { width: 12%; white-space: nowrap; }\n"
        "          .ventas-cart th:nth-child(4), .ventas-cart td:nth-child(4) { width: 12%; text-align: right; white-space: nowrap; }\n"
        "          .ventas-cart th:nth-child(5) { width: 30%; text-align: left; white-space: nowrap; }\n"
        "          .ventas-cart td:nth-child(5) { width: 30%; text-align: right; white-space: nowrap; }\n"
        "          .ventas-cart .btn { padding: 3px 5px; font-size: 8px; }\n"
        "          .ventas-cart td:nth-child(5) .total .btn svg { width: 8px; height: 8px; }\n"
        "          .actions-col .act-btn { width: 30px; height: 30px; }\n"
        "          .actions-col .act-btn .icon svg { width: 22px; height: 22px; }\n"
        "          .actions-col .act-btn .label { font-size: 11px; }\n"
        "          .productos-table { table-layout: fixed; width: 100%; }\n"
        "          .productos-table th, .productos-table td { padding: 6px; font-size: 12px; box-sizing: border-box; }\n"
        "          .productos-table th:nth-child(1), .productos-table td:nth-child(1) { width: 8%; white-space: nowrap; }\n"
        "          .productos-table th:nth-child(2), .productos-table td:nth-child(2) { width: 26%; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }\n"
        "          .productos-table th:nth-child(3), .productos-table td:nth-child(3) { width: 18%; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }\n"
        "          .productos-table th:nth-child(4), .productos-table td:nth-child(4) { width: 12%; text-align: right; white-space: nowrap; }\n"
        "          .productos-table th:nth-child(5), .productos-table td:nth-child(5) { width: 8%; white-space: nowrap; }\n"
        "          .productos-table th:nth-child(6), .productos-table td:nth-child(6) { width: 10%; white-space: nowrap; }\n"
        "          .productos-table th:nth-child(7), .productos-table td:nth-child(7) { width: 8%; white-space: nowrap; }\n"
        "          .productos-table th:nth-child(8), .productos-table td:nth-child(8) { width: 10%; white-space: nowrap; }\n"
        "          .productos-table .actions .btn { padding: 4px 8px; font-size: 12px; }\n"
        "          .productos-filter input[name='buscar'] { max-width: 50%; padding: 6px 8px; font-size: 12px; }\n"
        "          .productos-filter .btn { padding: 6px 10px; font-size: 12px; }\n"
        "          .productos-actions .btn { padding: 6px 10px; font-size: 12px; }\n"
        "        }\n"
        "        /* Tablet (<=768px) */\n"
        "        @media (max-width: 768px) {\n"
        "          .catalog-table { table-layout: fixed; width: 100%; }\n"
        "          .catalog-table th, .catalog-table td { padding: 4px; font-size: 12px; box-sizing: border-box; }\n"
        "          .catalog-table th:nth-child(1), .catalog-table td:nth-child(1) { width: 18%; white-space: nowrap; }\n"
        "          .catalog-table th:nth-child(2), .catalog-table td:nth-child(2) { width: 40%; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }\n"
        "          .catalog-table th:nth-child(3), .catalog-table td:nth-child(3) { width: 16%; text-align: right; white-space: nowrap; }\n"
        "          .catalog-table th:nth-child(4), .catalog-table td:nth-child(4) { width: 12%; text-align:center; }\n"
        "          .ventas-cart { table-layout: fixed; width: 80%; }\n"
        "          .ventas-cart th, .ventas-cart td { padding: 3px; font-size: 11px; box-sizing: border-box; }\n"
        "          .ventas-cart th:nth-child(1), .ventas-cart td:nth-child(1) { width: 8%; white-space: nowrap; }\n"
        "          .ventas-cart th:nth-child(2), .ventas-cart td:nth-child(2) { width: 35%; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }\n"
        "          .ventas-cart th:nth-child(3), .ventas-cart td:nth-child(3) { width: 8%; white-space: nowrap; }\n"
        "          .ventas-cart th:nth-child(4), .ventas-cart td:nth-child(4) { width: 8%; text-align: right; white-space: nowrap; }\n"
        "          .ventas-cart th:nth-child(5), .ventas-cart td:nth-child(5) { width: 14%; text-align: right; white-space: nowrap; }\n"
        "          .productos-table { table-layout: fixed; width: 100%; }\n"
        "          .productos-table th, .productos-table td { padding: 4px; font-size: 11px; box-sizing: border-box; }\n"
        "          .productos-table th:nth-child(1), .productos-table td:nth-child(1) { width: 10%; white-space: nowrap; }\n"
        "          .productos-table th:nth-child(2), .productos-table td:nth-child(2) { width: 28%; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }\n"
        "          .productos-table th:nth-child(3), .productos-table td:nth-child(3) { width: 20%; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }\n"
        "          .productos-table th:nth-child(4), .productos-table td:nth-child(4) { width: 12%; text-align: right; white-space: nowrap; }\n"
        "          .productos-table th:nth-child(5), .productos-table td:nth-child(5) { width: 8%; white-space: nowrap; }\n"
        "          .productos-table th:nth-child(6), .productos-table td:nth-child(6) { width: 10%; white-space: nowrap; }\n"
        "          .productos-table th:nth-child(7), .productos-table td:nth-child(7) { width: 6%; white-space: nowrap; }\n"
        "          .productos-table th:nth-child(8), .productos-table td:nth-child(8) { width: 6%; white-space: nowrap; }\n"
        "          .productos-table .actions .btn { padding: 4px 8px; font-size: 11px; }\n"
        "          .productos-filter input[name='buscar'] { max-width: 60%; padding: 5px 7px; font-size: 11px; }\n"
        "          .productos-filter .btn { padding: 5px 8px; font-size: 11px; }\n"
        "          .productos-actions .btn { padding: 5px 8px; font-size: 11px; }\n"
        "        }\n"
        "        /* Móvil (<=480px) */\n"
        "        @media (max-width: 480px) {\n"
        "          .catalog-table { table-layout: fixed; width: 100%; }\n"
        "          .catalog-table th, .catalog-table td { padding: 3px; font-size: 11px; box-sizing: border-box; }\n"
        "          .catalog-table th:nth-child(1), .catalog-table td:nth-child(1) { width: 16%; white-space: nowrap; }\n"
        "          .catalog-table th:nth-child(2), .catalog-table td:nth-child(2) { width: 50%; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }\n"
        "          .catalog-table th:nth-child(3), .catalog-table td:nth-child(3) { width: 16%; text-align: right; white-space: nowrap; }\n"
        "          .catalog-table th:nth-child(4), .catalog-table td:nth-child(4) { width: 8%; text-align:center; }\n"
        "          .ventas-cart { table-layout: fixed; width: 100%; }\n"
        "          .ventas-cart th, .ventas-cart td { padding: 2px; font-size: 10px; box-sizing: border-box; }\n"
        "          .ventas-cart th:nth-child(1), .ventas-cart td:nth-child(1) { width: 14%; white-space: nowrap; }\n"
        "          .ventas-cart th:nth-child(2), .ventas-cart td:nth-child(2) { width: 38%; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }\n"
        "          .ventas-cart th:nth-child(3), .ventas-cart td:nth-child(3) { width: 14%; white-space: nowrap; }\n"
        "          .ventas-cart th:nth-child(4), .ventas-cart td:nth-child(4) { width: 12%; text-align: center; white-space: nowrap; }\n"
        "          .ventas-cart th:nth-child(5), .ventas-cart td:nth-child(5) { width: 40%; text-align: left; white-space: nowrap; }\n"
        "          .productos-table { table-layout: fixed; width: 90%; }\n"
        "          .productos-table th, .productos-table td { padding: 3px; font-size: 10px; box-sizing: border-box; }\n"
        "          .productos-table th:nth-child(1), .productos-table td:nth-child(1) { width: 10%; white-space: nowrap; }\n"
        "          .productos-table th:nth-child(2), .productos-table td:nth-child(2) { width: 36%; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }\n"
        "          .productos-table th:nth-child(3), .productos-table td:nth-child(3) { width: 20%; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }\n"
        "          .productos-table th:nth-child(4), .productos-table td:nth-child(4) { width: 12%; text-align: right; white-space: nowrap; }\n"
        "          .productos-table th:nth-child(5), .productos-table td:nth-child(5) { width: 6%; white-space: nowrap; }\n"
        "          .productos-table th:nth-child(6), .productos-table td:nth-child(6) { width: 6%; white-space: nowrap; }\n"
        "          .productos-table th:nth-child(7), .productos-table td:nth-child(7) { width: 4%; white-space: nowrap; }\n"
        "          .productos-table th:nth-child(8), .productos-table td:nth-child(8) { width: 4%; white-space: nowrap; }\n"
        "          .productos-table .actions .btn { padding: 3px 6px; font-size: 10px; }\n"
        "          .productos-filter input[name='buscar'] { max-width: 100%; padding: 4px 6px; font-size: 10px; }\n"
        "          .productos-filter .btn { padding: 4px 6px; font-size: 10px; }\n"
        "          .productos-actions .btn { padding: 4px 6px; font-size: 10px; }\n"
        "        }\n"
        "    </style>\n"
        "</head>\n"
        "<body>\n"
        "    <header style='display:none'></header>\n"
        "    <div class=\"container\">\n"
            + str(body_html) + "\n"
        "    </div>\n"
        "    <script>\n"
        "    document.addEventListener('DOMContentLoaded', function(){\n"
        "      var rows = document.querySelectorAll('.catalog-table tbody tr');\n"
        "      var lastTouch = 0;\n"
        "      rows.forEach(function(r){\n"
        "        r.addEventListener('dblclick', function(e){\n"
        "          if(e && e.cancelable){ e.preventDefault(); }\n"
        "          var f = r.querySelector('form');\n"
        "          if(f){ f.submit(); }\n"
        "        });\n"
        "        r.addEventListener('touchend', function(e){\n"
        "          var now = Date.now();\n"
        "          if(now - lastTouch <= 300){\n"
        "            if(e && e.cancelable){ e.preventDefault(); }\n"
        "            var f = r.querySelector('form');\n"
        "            if(f){ f.submit(); }\n"
        "          }\n"
        "          lastTouch = now;\n"
        "        }, { passive: false });\n"
        "      });\n"
        "      var sForm = document.querySelector('form.actions.search-bar');\n"
        "      if(sForm){\n"
        "        var sInput = sForm.querySelector(\"input[name='buscar']\");\n"
        "        if(sInput){\n"
        "          sInput.addEventListener('keydown', function(e){\n"
        "            if(e.key === 'Enter'){\n"
        "              if(e && e.cancelable){ e.preventDefault(); }\n"
        "              var q = (sInput.value || '').trim();\n"
        "              if(!q){ sForm.submit(); return; }\n"
        "              fetch('/ventas/agregar', { method: 'POST', headers: { 'Content-Type': 'application/x-www-form-urlencoded' }, body: 'codigo=' + encodeURIComponent(q) })\n"
        "                .then(function(){ sInput.value=''; window.location.href = '/ventas'; });\n"
        "            }\n"
        "          });\n"
        "        }\n"
        "      }\n"
        "      var pForm = document.querySelector('form.actions.productos-filter');\n"
        "      if(pForm){\n"
        "        var pInput = pForm.querySelector(\"input[name='buscar']\");\n"
        "        var pTableBody = document.querySelector('.productos-table tbody');\n"
        "        var pTimer = null;\n"
        "        function doFetchProductos(q){\n"
        "          fetch('/productos?buscar=' + encodeURIComponent(q))\n"
        "            .then(function(r){ return r.text(); })\n"
        "            .then(function(html){\n"
        "              var tmp = document.createElement('div'); tmp.innerHTML = html;\n"
        "              var newBody = tmp.querySelector('.productos-table tbody');\n"
        "              if(newBody && pTableBody){ pTableBody.innerHTML = newBody.innerHTML; }\n"
        "            }).catch(function(){});\n"
        "        }\n"
        "        if(pInput){\n"
        "          pInput.addEventListener('input', function(){\n"
        "            var q = (pInput.value || '').trim();\n"
        "            if(pTimer){ clearTimeout(pTimer); }\n"
        "            pTimer = setTimeout(function(){ doFetchProductos(q); }, 250);\n"
        "          });\n"
        "        }\n"
        "      }\n"
        "      var payForm = document.getElementById('pay-form');\n"
        "      var backdrop = document.getElementById('pay-modal-backdrop');\n"
        "      var modal = document.getElementById('pay-modal');\n"
        "      var pmMetodo = document.getElementById('pm-metodo');\n"
        "      var pmCliente = document.getElementById('pm-cliente');\n"
        "      var pmEfectivo = document.getElementById('pm-efectivo');\n"
        "      var pmTotal = document.getElementById('pm-total');\n"
        "      var pmCambio = document.getElementById('pm-cambio');\n"
        "      var pmCancel = document.getElementById('pm-cancel');\n"
        "      var pmConfirm = document.getElementById('pm-confirm');\n"
        "      function parseM(s){ var t = String(s||'').trim().replace(',','.'); t = t.replace(/[^0-9.]/g,''); if((t.match(/\./g)||[]).length>1){ var p=t.split('.'); t=p.slice(0,-1).join('')+'.'+p[p.length-1]; } var v=parseFloat(t); return isNaN(v)?0:v; }\n"
        "      function calc(){ var ef = parseM(pmEfectivo.value); pmTotal.textContent = 'Total Pagado: L ' + ef.toFixed(2); var tot = parseFloat(modal.getAttribute('data-total')||'0'); var diff = ef - tot; pmCambio.textContent = (diff>=0 ? 'Cambio: L ' + diff.toFixed(2) : 'Faltan: L ' + (-diff).toFixed(2)); }\n"
        "      if(pmEfectivo){ pmEfectivo.addEventListener('input', calc); }\n"
        "      if(payForm){\n"
        "        payForm.addEventListener('submit', function(e){ if(e && e.cancelable){ e.preventDefault(); } if(backdrop){ backdrop.style.display='flex'; } calc(); });\n"
        "      }\n"
        "      if(pmCancel){ pmCancel.addEventListener('click', function(){ if(backdrop){ backdrop.style.display='none'; } }); }\n"
        "      if(pmConfirm){ pmConfirm.addEventListener('click', function(){ var inpMetodo = payForm.querySelector(\"input[name='metodo_pago']\"); var inpCliente = payForm.querySelector(\"input[name='cliente']\"); var inpEf = payForm.querySelector(\"input[name='efectivo']\"); if(inpMetodo){ inpMetodo.value = pmMetodo ? pmMetodo.value : 'Efectivo'; } if(inpCliente){ inpCliente.value = pmCliente ? pmCliente.value : 'CLIENTE WEB'; } if(inpEf){ inpEf.value = pmEfectivo ? pmEfectivo.value : ''; } backdrop.style.display='none'; payForm.submit(); }); }\n"
        "    });\n"
        "    </script>\n"
        "</body>\n"
        "</html>\n"
    ).encode("utf-8")

def parse_body(environ):
    try:
        size = int(environ.get("CONTENT_LENGTH") or 0)
    except Exception:
        size = 0
    body = environ["wsgi.input"].read(size) if size > 0 else b""
    return parse_qs(body.decode("utf-8"))


def to_int(val, default=0):
    try:
        return int(str(val))
    except Exception:
        return default


def to_float(val, default=0.0):
    try:
        return float(str(val).replace(',', '.'))
    except Exception:
        return default


def escape_html(s):
    if s is None:
        return ''
    t = str(s)
    t = t.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    t = t.replace('"', '&quot;').replace("'", '&#39;')
    return t


def productos_list_html(rows, buscar_text=""):
    items = "".join(
        f"<tr><td>{r[0]}</td><td>{escape_html(r[1])}</td><td>{escape_html(r[2] or '')}</td><td style='text-align:right'>{r[3]:.2f}</td><td>{('15%' if int(r[4] or 3)==1 else ('18%' if int(r[4] or 3)==2 else 'Ex'))}</td><td>{int(r[5] or 0)}</td><td>{'Sí' if int(r[6] or 0)==1 else 'No'}</td><td class='actions'><a class='btn secondary' href='/productos/editar?id={r[0]}'>Editar</a></td></tr>"
        for r in rows
    )
    return f"""
        <h2 class='productos-title'>Productos</h2>
        <form method='get' action='/productos' class='actions productos-filter'>
            <input name='buscar' placeholder='Buscar por nombre o código' value='{escape_html(buscar_text)}' />
            <button class='btn' type='submit'>Buscar</button>
            <a class='btn success add-btn' href='/productos/nuevo' title='Agregar producto'>
                <svg viewBox='0 0 24 24' width='16' height='16'>
                    <path d='M12 5v14M5 12h14' fill='none' stroke='#ffffff' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'/>
                </svg>
                Agregar
            </a>
            <a class='btn secondary back-btn' href='/ventas' title='Regresar a ventas'>
                <svg viewBox='0 0 24 24' width='16' height='16'>
                    <path d='M15 18l-6-6 6-6' fill='none' stroke='#ffffff' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'/>
                </svg>
                Ventas
            </a>
        </form>
        <div class='table-wrap productos-wrap'>
        <table class='productos-table'>
            <thead>
                <tr>
                    <th>ID</th><th>Nombre</th><th>Código</th><th>Precio (L)</th><th>ISV</th><th>Stock</th><th>Pesable</th><th>Acciones</th>
                </tr>
            </thead>
            <tbody>
                {items}
            </tbody>
        </table>
        </div>
    """


def producto_form_html(values=None, error_msg=None):
    v = values or {}
    nombre = v.get('nombre', '')
    precio = v.get('precio', '')
    impuesto = v.get('impuesto', 'Exento')
    codigo = v.get('codigo_barras', '')
    stock = v.get('stock', '0')
    pesable = v.get('pesable', 'No')
    msg = f"<div class='msg error'>{error_msg}</div>" if error_msg else ""
    return f"""
        <h2>Formulario Producto</h2>
        {msg}
        <form method='post'>
            <div class='grid'>
                <div>
                    <label>Nombre</label>
                    <input name='nombre' value='{escape_html(nombre)}' required />
                </div>
                <div>
                    <label>Precio</label>
                    <input name='precio' value='{escape_html(precio)}' required />
                </div>
                <div>
                    <label>Impuesto</label>
                    <select name='impuesto'>
                        <option {('selected' if impuesto=='Exento' else '')}>Exento</option>
                        <option {('selected' if impuesto=='15' else '')}>15</option>
                        <option {('selected' if impuesto=='18' else '')}>18</option>
                    </select>
                </div>
                <div>
                    <label>Código de barras (opcional)</label>
                    <input name='codigo_barras' value='{escape_html(codigo)}' />
                </div>
                <div>
                    <label>Stock</label>
                    <input name='stock' value='{escape_html(stock)}' />
                </div>
                <div>
                    <label>Pesable</label>
                    <select name='pesable'>
                        <option {('selected' if pesable=='No' else '')}>No</option>
                        <option {('selected' if pesable=='Sí' else '')}>Sí</option>
                    </select>
                </div>
            </div>
            <div class='actions' style='margin-top:12px;'>
                <button class='btn' type='submit'>Guardar</button>
                <a class='btn secondary' href='/productos'>Cancelar</a>
            </div>
        </form>
    """


# =====================
# SESIÓN Y UTILIDADES
# =====================
SESSIONS = {}

def _gen_sid():
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(24))

def _get_cookie(environ):
    raw = environ.get('HTTP_COOKIE') or ''
    parts = [p.strip() for p in raw.split(';') if p.strip()]
    kv = {}
    for p in parts:
        if '=' in p:
            k, v = p.split('=', 1)
            kv[k.strip()] = v.strip()
    return kv

def _get_session(environ):
    cookies = _get_cookie(environ)
    sid = cookies.get('sid')
    set_cookie = None
    if not sid or sid not in SESSIONS:
        sid = _gen_sid()
        SESSIONS[sid] = {'cart': []}
        set_cookie = f"sid={sid}; Path=/; HttpOnly; SameSite=Lax"
    return SESSIONS[sid], set_cookie

def _cart_totals(cart):
    gravado15 = 0.0
    gravado18 = 0.0
    exento = 0.0
    for item in cart:
        subtotal = float(item['precio']) * float(item['cantidad'])
        tag = int(item['impuesto'] or 3)
        if tag == 1:
            gravado15 += subtotal
        elif tag == 2:
            gravado18 += subtotal
        else:
            exento += subtotal
    isv15 = round(gravado15 * 0.15, 2)
    isv18 = round(gravado18 * 0.18, 2)
    grantotal = round(gravado15 + gravado18 + exento + isv15 + isv18, 2)
    return (
        round(gravado15, 2),
        round(gravado18, 2),
        round(exento, 2),
        isv15,
        isv18,
        grantotal,
    )

def _ventas_page_html(cart, buscar_text="", resultados=None, ok_msg=None, err_msg=None):
    if resultados is None:
        try:
            conn = conectar()
            cur = conn.cursor()
            if USE_POSTGRES:
                cur.execute("SELECT id_producto, nombre, precio, impuesto FROM productos ORDER BY nombre LIMIT 500")
            else:
                cur.execute("SELECT id_producto, nombre, precio, impuesto FROM productos ORDER BY nombre LIMIT 500")
            rows = cur.fetchall() or []
            resultados = [(r[0], r[1], r[2], r[3]) for r in rows]
            conn.close()
        except Exception:
            resultados = []
    rows_html_parts = []
    for idx, it in enumerate(cart):
        imp_txt = '15%' if int(it['impuesto']) == 1 else ('18%' if int(it['impuesto']) == 2 else 'Ex')
        subtotal = float(it['precio']) * float(it['cantidad'])
        is_pesable = 1 if int(it.get('pesable', 0)) == 1 else 0
        qty_cell = ""
        if is_pesable:
            qty_cell = (
                f"<div class='qty'>"
                f"<form method='post' action='/ventas/actualizar?idx={idx}' style='display:inline'>"
                f"<input name='cantidad' value='{float(it['cantidad']):.2f}' onchange='this.form.submit()' />"
                f"</form>"
                f"</div>"
            )
        else:
            qty_cell = (
                f"<div class='qty'>"
                f"<span class='value'>{float(it['cantidad']):.2f}</span>"
                f"</div>"
            )
        row_html = (
            f"<tr><td>{it['id']}</td><td>{escape_html(it['nombre'])}</td>"
            f"<td>{qty_cell}</td>"
            f"<td style='text-align:right'>{float(it['precio']):.2f}</td>"
            f"<td style='text-align:right'><div class='total'><span class='value'>{subtotal:.2f}</span> "
            f"<form method='post' action='/ventas/reducir?idx={idx}' style='display:inline'><button class='btn qty-dec' type='submit'><svg viewBox='0 0 16 16' fill='none' stroke='currentColor' stroke-width='2' stroke-linecap='round'><line x1='3' y1='8' x2='13' y2='8'></line></svg></button></form> "
            f"<form method='post' action='/ventas/aumentar?idx={idx}' style='display:inline'><button class='btn qty-inc' type='submit'><svg viewBox='0 0 16 16' fill='none' stroke='currentColor' stroke-width='2' stroke-linecap='round'><line x1='8' y1='3' x2='8' y2='13'></line><line x1='3' y1='8' x2='13' y2='8'></line></svg></button></form> "
            f"<form method='post' action='/ventas/eliminar?idx={idx}' style='display:inline'><button class='btn danger' type='submit'><svg viewBox='0 0 16 16' fill='none' stroke='currentColor' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'><polyline points='2 4 4 4 14 4'></polyline><path d='M12 4l-1 10H5L4 4'></path><line x1='7' y1='7' x2='7' y2='12'></line><line x1='9' y1='7' x2='9' y2='12'></line><path d='M6 4V3h4v1'></path></svg></button></form></div></td>"
            f"</tr>"
        )
        rows_html_parts.append(row_html)
    rows_html = ''.join(rows_html_parts)
    empty_row = "<tr><td colspan=7 style='text-align:center'>Carrito vacío</td></tr>"
    g15, g18, ex, i15, i18, total = _cart_totals(cart)
    msg = ""
    if ok_msg:
        msg += f"<div class='msg ok'>{escape_html(ok_msg)}</div>"
    if err_msg:
        msg += f"<div class='msg error'>{escape_html(err_msg)}</div>"
    left_panel = (
        msg
        + "<div class='table-wrap'><table class='ventas-cart'><thead><tr><th>Código</th><th>Descripción</th><th>Cant.</th><th>Precio</th><th>Total</th></tr></thead><tbody>"
        + (rows_html if rows_html_parts else empty_row)
        + "</tbody></table></div>"
    )

    res_rows = []
    for r in (resultados or []):
        try:
            pid = r[0]; nom = r[1]; pre = float(r[2] or 0.0); imp = r[3]
        except Exception:
            continue
        tag = str(imp).strip().lower()
        imp_txt = '15%' if tag in ('15','1') else ('18%' if tag in ('18','2') else 'Ex')
        res_rows.append(
            "<tr data-pid='" + str(pid) + "'>"
            + f"<td>{pid}</td><td>{escape_html(nom)}</td>"
            + f"<td class='precio' style='text-align:right'>{pre:.2f}</td>"
            + "<td>"
            + f"<form method='post' action='/ventas/agregar' class='actions'><input type='hidden' name='codigo' value='{pid}' />"
            + "<button class='btn' type='submit'>Agregar</button></form>"
            + "</td>"
            + "</tr>"
        )
    right_panel = (
        "<form method='get' action='/ventas' class='actions search-bar'>"
        + f"<input name='buscar' placeholder='Buscar por nombre o código' value='{escape_html(buscar_text)}' />"
        + "<button class='btn' type='submit'>Buscar</button>"
        + "</form>"
        + "<div class='table-wrap'><table class='catalog-table'><thead><tr><th>Código</th><th>Nombre</th><th>Precio</th><th></th></tr></thead><tbody>"
        + (''.join(res_rows) if res_rows else "<tr><td colspan=5 style='text-align:center'>Sin resultados</td></tr>")
        + "</tbody></table></div>"
    )

    idx_to_del = len(cart) - 1 if cart else -1

    actions_col = (
        "<div class='actions-col'>"
        + "<form id='pay-form' method='post' action='/ventas/facturar'>"
        + "<input type='hidden' name='cliente' value='CLIENTE WEB' />"
        + "<input type='hidden' name='metodo_pago' value='Efectivo' />"
        + "<input type='hidden' name='efectivo' value='' />"
        + "<button class='act-btn' type='submit'><div class='icon'><svg viewBox='0 0 24 24'><rect x='3' y='3' width='18' height='18' rx='4' fill='#8BC34A' stroke='#6FAF3A' stroke-width='2'/><path d='M7 12l3 3 7-7' fill='none' stroke='#FFFFFF' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'/></svg></div><div class='label'>Pagar</div></button>"
        + "</form>"
        + f"<form method='post' action='/ventas/eliminar?idx={idx_to_del}'>"
        + "<button class='act-btn' type='submit'><div class='icon'><svg viewBox='0 0 24 24'><rect x='5' y='6' width='14' height='15' rx='2' fill='#A5D6A7' stroke='#1E88E5' stroke-width='2'/><rect x='9' y='3' width='6' height='3' rx='1' fill='#90CAF9' stroke='#1E88E5' stroke-width='2'/><line x1='8' y1='10' x2='8' y2='18' stroke='#1E88E5' stroke-width='2'/><line x1='12' y1='10' x2='12' y2='18' stroke='#1E88E5' stroke-width='2'/><line x1='16' y1='10' x2='16' y2='18' stroke='#1E88E5' stroke-width='2'/></svg></div><div class='label'>Eliminar</div></button>"
        + "</form>"
        + "<form method='post' action='/ventas/limpiar'>"
        + "<button class='act-btn' type='submit'><div class='icon'><svg viewBox='0 0 24 24'><path d='M5 17l12-3' stroke='#FB8C00' stroke-width='2' stroke-linecap='round'/><path d='M6 6l6 9' stroke='#FB8C00' stroke-width='2' stroke-linecap='round'/><path d='M4 18l3 2 2-3' fill='none' stroke='#FDD835' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'/></svg></div><div class='label'>Limpiar</div></button>"
        + "</form>"
        + "<a class='act-btn' href='/productos'><div class='icon'><svg viewBox='0 0 24 24'><path d='M5 6h2l2 9h9l2-6H8' fill='none' stroke='#26A69A' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'/><circle cx='10' cy='20' r='2' fill='#26A69A'/><circle cx='18' cy='20' r='2' fill='#26A69A'/></svg></div><div class='label'>Productos</div></a>"
        + "</div>"
    )

    return (
        "<div class='banner'><h1>Ventas</h1>" + f"<div id='lbl-total'>Total L: {total:.2f}</div>" + "</div>"
        + "<div id='pay-modal-backdrop' class='modal-backdrop'><div class='modal' id='pay-modal' data-total='" + f"{total:.2f}" + "'>"
        + "<h3>Pago</h3>"
        + "<div class='total-banner'>Total L: " + f"{total:.2f}" + "</div>"
        + "<div class='row'><label>Método:</label><select id='pm-metodo'><option value='Efectivo'>Efectivo</option><option value='Tarjeta'>Tarjeta</option><option value='Transferencia'>Transferencia</option></select></div>"
        + "<div class='row'><label>Cliente:</label><input id='pm-cliente' value='CLIENTE WEB' /></div>"
        + "<div class='row'><label>Efectivo:</label><input id='pm-efectivo' placeholder='0.00' inputmode='decimal' /></div>"
        + "<div class='row'><div id='pm-total'>Total Pagado: L 0.00</div></div>"
        + "<div class='row'><div id='pm-cambio'>Cambio: L 0.00</div></div>"
        + "<div class='actions'><button id='pm-cancel' class='btn secondary' type='button'>Cancelar</button><button id='pm-confirm' class='btn' type='button'>Confirmar</button></div>"
        + "</div></div>"
        + "<div class='layout'>"
        + "<div class='panel'>" + left_panel + "</div>"
        + "<div class='panel'>" + right_panel + "</div>"
        + actions_col
        + "</div>"
    )


INIT_DONE = False

def app(environ, start_response):
    global INIT_DONE
    if not INIT_DONE:
        try:
            asegurar_tabla_productos_sqlite()
            asegurar_columna_pesable_productos_sqlite()
            sembrar_productos_iniciales()
        except Exception:
            pass
        INIT_DONE = True
    path = environ.get('PATH_INFO', '/')
    method = environ.get('REQUEST_METHOD', 'GET').upper()
    qs = parse_qs(environ.get('QUERY_STRING', ''))
    session, set_cookie = _get_session(environ)

    def _start(status, headers):
        if set_cookie:
            headers = headers + [('Set-Cookie', set_cookie)]
        start_response(status, headers)

    try:
        if path == '/health':
            _start('200 OK', [('Content-Type', 'text/plain; charset=utf-8')])
            return [b'OK']

        if path == '/':
            body = (
                "<h2>Inicio</h2>"
                "<p>Bienvenido al entorno web.</p>"
                "<div class='actions'>"
                "<a class='btn' href='/productos'>Gestión de productos</a>"
                "<a class='btn secondary' href='/ventas' style='margin-left:8px'>Ventas</a>"
                "</div>"
            )
            page = html_page('Inicio', body)
            _start('200 OK', [('Content-Type', 'text/html; charset=utf-8')])
            return [page]

        if path == '/productos' and method == 'GET':
            buscar = (qs.get('buscar', [''])[0]).strip()
            conn = conectar()
            cur = conn.cursor()
            
            if buscar:
                like = '%' + buscar.lower() + '%'
                if USE_POSTGRES:
                    cur.execute("""
                        SELECT id_producto, nombre, codigo_barras, precio, impuesto, stock, pesable 
                        FROM productos 
                        WHERE LOWER(nombre) LIKE %s OR LOWER(codigo_barras) LIKE %s OR CAST(id_producto AS TEXT) LIKE %s 
                        ORDER BY nombre LIMIT 500
                    """, (like, like, like))
                else:
                    cur.execute("""
                        SELECT id_producto, nombre, codigo_barras, precio, impuesto, stock, pesable 
                        FROM productos 
                        WHERE LOWER(nombre) LIKE ? OR LOWER(codigo_barras) LIKE ? OR CAST(id_producto AS TEXT) LIKE ? 
                        ORDER BY nombre LIMIT 500
                    """, (like, like, like))
            else:
                cur.execute("SELECT id_producto, nombre, codigo_barras, precio, impuesto, stock, pesable FROM productos ORDER BY nombre LIMIT 500")

            rows = cur.fetchall() or []
            conn.close()
            body = productos_list_html(rows, buscar_text=buscar)
            page = html_page('Productos', body)
            _start('200 OK', [('Content-Type', 'text/html; charset=utf-8')])
            return [page]

        if path == '/productos/nuevo':
            if method == 'GET':
                page = html_page('Nuevo producto', producto_form_html())
                _start('200 OK', [('Content-Type', 'text/html; charset=utf-8')])
                return [page]
            else:
                form = parse_body(environ)
                nombre = (form.get('nombre', [''])[0]).strip()
                precio = to_float(form.get('precio', [''])[0])
                impuesto = (form.get('impuesto', ['Exento'])[0]).strip()
                codigo = (form.get('codigo_barras', [''])[0]).strip() or None
                stock = to_int(form.get('stock', ['0'])[0], 0)
                pesable_txt = (form.get('pesable', ['No'])[0]).strip()
                pesable = 1 if pesable_txt.lower().startswith('s') else 0
                if not nombre or precio <= 0:
                    _start('200 OK', [('Content-Type', 'text/html; charset=utf-8')])
                    vals = {'nombre': nombre, 'precio': form.get('precio', [''])[0], 'impuesto': impuesto, 'codigo_barras': codigo or '', 'stock': str(stock), 'pesable': ('Sí' if pesable==1 else 'No')}
                    return [html_page('Nuevo producto', producto_form_html(vals, 'Completa los campos obligatorios y precio válido'))]
                imp_tag = 1 if impuesto.startswith('15') else (2 if impuesto.startswith('18') else 3)
                conn = conectar()
                cur = conn.cursor()
                if codigo:
                    if USE_POSTGRES:
                        cur.execute("SELECT id_producto FROM productos WHERE codigo_barras = %s", (codigo,))
                    else:
                        cur.execute("SELECT id_producto FROM productos WHERE codigo_barras = ?", (codigo,))
                    
                    if cur.fetchone():
                        conn.close()
                        _start('200 OK', [('Content-Type', 'text/html; charset=utf-8')])
                        vals = {'nombre': nombre, 'precio': f"{precio}", 'impuesto': impuesto, 'codigo_barras': codigo or '', 'stock': str(stock), 'pesable': ('Sí' if pesable==1 else 'No')}
                        return [html_page('Nuevo producto', producto_form_html(vals, 'El código de barras ya existe'))]
                
                if USE_POSTGRES:
                    cur.execute(
                        "INSERT INTO productos (nombre, codigo_barras, precio, impuesto, stock, pesable) VALUES (%s, %s, %s, %s, %s, %s)",
                        (nombre, codigo, float(precio), imp_tag, int(stock), int(pesable))
                    )
                else:
                    cur.execute(
                        "INSERT INTO productos (nombre, codigo_barras, precio, impuesto, stock, pesable) VALUES (?, ?, ?, ?, ?, ?)",
                        (nombre, codigo, float(precio), imp_tag, int(stock), int(pesable))
                    )
                conn.commit()
                conn.close()
                _start('302 Found', [('Location', '/productos')])
                return [b'']

        if path == '/productos/editar':
            if method == 'GET':
                pid = to_int((qs.get('id', [''])[0]))
                conn = conectar()
                cur = conn.cursor()
                if USE_POSTGRES:
                    cur.execute("SELECT id_producto, nombre, codigo_barras, precio, impuesto, stock, pesable FROM productos WHERE id_producto = %s", (pid,))
                else:
                    cur.execute("SELECT id_producto, nombre, codigo_barras, precio, impuesto, stock, pesable FROM productos WHERE id_producto = ?", (pid,))
                r = cur.fetchone()
                conn.close()
                if not r:
                    page = html_page('No encontrado', "<h2>Producto no encontrado</h2>")
                    _start('404 Not Found', [('Content-Type', 'text/html; charset=utf-8')])
                    return [page]
                impuesto_txt = '18' if str(r[4])=='2' else ('15' if str(r[4])=='1' else 'Exento')
                vals = {
                    'nombre': r[1],
                    'precio': f"{float(r[3]):.2f}",
                    'impuesto': impuesto_txt,
                    'codigo_barras': r[2] or '',
                    'stock': str(int(r[5] or 0)),
                    'pesable': ('Sí' if int(r[6] or 0)==1 else 'No')
                }
                page = html_page('Editar producto', producto_form_html(vals))
                _start('200 OK', [('Content-Type', 'text/html; charset=utf-8')])
                return [page]
            else:
                form = parse_body(environ)
                pid = to_int((qs.get('id', [''])[0]))
                nombre = (form.get('nombre', [''])[0]).strip()
                precio = to_float(form.get('precio', [''])[0])
                impuesto = (form.get('impuesto', ['Exento'])[0]).strip()
                codigo = (form.get('codigo_barras', [''])[0]).strip() or None
                stock = to_int(form.get('stock', ['0'])[0], 0)
                pesable_txt = (form.get('pesable', ['No'])[0]).strip()
                pesable = 1 if pesable_txt.lower().startswith('s') else 0
                if not nombre or precio <= 0:
                    vals = {'nombre': nombre, 'precio': form.get('precio', [''])[0], 'impuesto': impuesto, 'codigo_barras': codigo or '', 'stock': str(stock), 'pesable': ('Sí' if pesable==1 else 'No')}
                    page = html_page('Editar producto', producto_form_html(vals, 'Completa los campos obligatorios y precio válido'))
                    _start('200 OK', [('Content-Type', 'text/html; charset=utf-8')])
                    return [page]
                imp_tag = 1 if impuesto.startswith('15') else (2 if impuesto.startswith('18') else 3)
                conn = conectar()
                cur = conn.cursor()
                if codigo:
                    if USE_POSTGRES:
                        cur.execute("SELECT id_producto FROM productos WHERE codigo_barras = %s", (codigo,))
                    else:
                        cur.execute("SELECT id_producto FROM productos WHERE codigo_barras = ?", (codigo,))
                    r = cur.fetchone()
                    if r and int(r[0]) != int(pid):
                        conn.close()
                        _start('200 OK', [('Content-Type', 'text/html; charset=utf-8')])
                        vals = {'nombre': nombre, 'precio': f"{precio}", 'impuesto': impuesto, 'codigo_barras': codigo or '', 'stock': str(stock), 'pesable': ('Sí' if pesable==1 else 'No')}
                        return [html_page('Editar producto', producto_form_html(vals, 'El código de barras ya existe en otro producto'))]
                
                if USE_POSTGRES:
                    cur.execute(
                        "UPDATE productos SET nombre=%s, codigo_barras=%s, precio=%s, impuesto=%s, stock=%s, pesable=%s WHERE id_producto=%s",
                        (nombre, codigo, float(precio), imp_tag, int(stock), int(pesable), int(pid))
                    )
                else:
                    cur.execute(
                        "UPDATE productos SET nombre=?, codigo_barras=?, precio=?, impuesto=?, stock=?, pesable=? WHERE id_producto=?",
                        (nombre, codigo, float(precio), imp_tag, int(stock), int(pesable), int(pid))
                    )
                conn.commit()
                conn.close()
                _start('302 Found', [('Location', '/productos')])
                return [b'']

        # =====================
        # Ventas Web
        # =====================
        if path == '/ventas' and method == 'GET':
            ok = qs.get('ok', [''])[0]
            err = qs.get('err', [''])[0]
            buscar = (qs.get('buscar', [''])[0]).strip()
            resultados = []
            try:
                conn = conectar()
                cur = conn.cursor()
                if buscar:
                    like = '%' + buscar.lower() + '%'
                    if USE_POSTGRES:
                        cur.execute("SELECT id_producto, nombre, codigo_barras, precio, impuesto, stock, pesable FROM productos WHERE LOWER(nombre) LIKE %s OR LOWER(codigo_barras) LIKE %s OR CAST(id_producto AS TEXT) LIKE %s ORDER BY nombre LIMIT 500", (like, like, like))
                    else:
                        cur.execute("SELECT id_producto, nombre, codigo_barras, precio, impuesto, stock, pesable FROM productos WHERE LOWER(nombre) LIKE ? OR LOWER(codigo_barras) LIKE ? OR CAST(id_producto AS TEXT) LIKE ? ORDER BY nombre LIMIT 500", (like, like, like))
                else:
                    cur.execute("SELECT id_producto, nombre, codigo_barras, precio, impuesto, stock, pesable FROM productos ORDER BY nombre LIMIT 500")
                rows = cur.fetchall() or []
                resultados = [(r[0], r[1], r[3], r[4]) for r in rows]
                try:
                    print('VENTAS catálogo, buscar="' + (buscar or '') + '"; filas=', len(rows))
                except Exception:
                    pass
                conn.close()
            except Exception:
                resultados = []
            body = _ventas_page_html(session.get('cart', []), buscar_text=buscar, resultados=resultados, ok_msg=(ok or None), err_msg=(err or None))
            page = html_page('Ventas', body)
            _start('200 OK', [('Content-Type', 'text/html; charset=utf-8')])
            return [page]

        if path == '/ventas/agregar' and method == 'POST':
            form = parse_body(environ)
            codigo = (form.get('codigo', [''])[0]).strip()
            cantidad = to_float(form.get('cantidad', ['1'])[0], 1.0)
            info = obtener_info_producto(codigo)
            if not info:
                _start('302 Found', [('Location', '/ventas?err=Producto+no+encontrado')])
                return [b'']
            pid, nombre, precio, isv_tag, pesable = info
            session['cart'].append({
                'id': pid,
                'nombre': nombre,
                'precio': float(precio),
                'cantidad': float(cantidad),
                'impuesto': int(isv_tag),
                'pesable': int(pesable),
            })
            _start('302 Found', [('Location', '/ventas')])
            return [b'']

        if path == '/ventas/actualizar' and method == 'POST':
            idx = int(qs.get('idx', ['-1'])[0])
            form = parse_body(environ)
            cantidad = to_float(form.get('cantidad', ['1'])[0], 1.0)
            if 0 <= idx < len(session['cart']):
                session['cart'][idx]['cantidad'] = cantidad
            _start('302 Found', [('Location', '/ventas')])
            return [b'']

        if path == '/ventas/aumentar' and method == 'POST':
            idx = int(qs.get('idx', ['-1'])[0])
            if 0 <= idx < len(session['cart']):
                it = session['cart'][idx]
                step = 0.1 if int(it.get('pesable', 0)) == 1 else 1.0
                it['cantidad'] = round(float(it.get('cantidad', 1.0)) + step, 2)
            _start('302 Found', [('Location', '/ventas')])
            return [b'']

        if path == '/ventas/reducir' and method == 'POST':
            idx = int(qs.get('idx', ['-1'])[0])
            if 0 <= idx < len(session['cart']):
                it = session['cart'][idx]
                step = 0.1 if int(it.get('pesable', 0)) == 1 else 1.0
                nueva = round(float(it.get('cantidad', 1.0)) - step, 2)
                minimo = step if int(it.get('pesable', 0)) == 1 else 1.0
                it['cantidad'] = max(minimo, nueva)
            _start('302 Found', [('Location', '/ventas')])
            return [b'']

        if path == '/ventas/eliminar' and method == 'POST':
            idx = int(qs.get('idx', ['-1'])[0])
            if 0 <= idx < len(session['cart']):
                session['cart'].pop(idx)
            _start('302 Found', [('Location', '/ventas')])
            return [b'']

        if path == '/ventas/limpiar' and method == 'POST':
            session['cart'] = []
            _start('302 Found', [('Location', '/ventas')])
            return [b'']

        if path == '/ventas/facturar' and method == 'POST':
            cart = session.get('cart', [])
            if not cart:
                _start('302 Found', [('Location', '/ventas?err=Carrito+vac%C3%ADo')])
                return [b'']
            form = parse_body(environ)
            cliente = (form.get('cliente', ['CLIENTE WEB'])[0]).strip() or 'CLIENTE WEB'
            metodo = (form.get('metodo_pago', ['Efectivo'])[0]).strip() or 'Efectivo'
            g15, g18, ex, i15, i18, total = _cart_totals(cart)
            try:
                numero = obtener_max_factura() or 0
            except Exception:
                numero = 0
            numero = int(numero or 0) + 1
            conn = None
            try:
                asegurar_tabla_ventas_sqlite()
                asegurar_tabla_facturas_sqlite()
                conn = conectar()
                try:
                    cur = conn.cursor()
                    if USE_POSTGRES:
                        cur.execute("DELETE FROM ventas WHERE factura = %s", (numero,))
                        cur.execute("DELETE FROM facturas WHERE factura = %s", (numero,))
                    else:
                        cur.execute("DELETE FROM ventas WHERE factura = ?", (numero,))
                        cur.execute("DELETE FROM facturas WHERE factura = ?", (numero,))
                except Exception:
                    pass
                for it in cart:
                    pid = str(it['id'])
                    nombre = str(it['nombre'])
                    precio = float(it['precio'])
                    cantidad = float(it['cantidad'])
                    subtotal = round(precio * cantidad, 2)
                    insertar_venta(
                        conn,
                        numero,
                        pid,
                        nombre,
                        precio,
                        cantidad,
                        subtotal,
                        0, 0, 0, 0, 0,
                        total
                    )
                    try:
                        actualizar_stock(conn, pid, cantidad)
                    except Exception:
                        pass
                insertar_factura_resumen(
                    conn,
                    numero,
                    cliente,
                    g15,
                    g18,
                    ex,
                    i15,
                    i18,
                    total,
                    total,
                    0.0,
                    metodo,
                )
                conn.commit()
                session['cart'] = []
                _start('302 Found', [('Location', '/ventas?ok=Factura+emitida')])
                return [b'']
            except Exception as e:
                try:
                    if conn:
                        conn.rollback()
                except Exception:
                    pass
                _start('302 Found', [('Location', '/ventas?err=Error+al+facturar')])
                return [b'']

        _start('404 Not Found', [('Content-Type', 'text/html; charset=utf-8')])
        return [html_page('404', '<h2>Página no encontrada</h2>')]
    except Exception as e:
        try:
            print('ERROR en servidor web:', e)
        except Exception:
            pass
        _start('500 Internal Server Error', [('Content-Type', 'text/html; charset=utf-8')])
        return [html_page('Error', f"<div class='msg error'>Error: {e}</div>")]


if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 8000))
    HOST = '0.0.0.0'
    
    httpd = make_server(HOST, PORT, app)
    print(f'Servidor web en http://{HOST}:{PORT}/')
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print('\nServidor detenido')
        pass
