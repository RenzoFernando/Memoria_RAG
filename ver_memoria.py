from almacen import crear_cliente, obtener_coleccion

cliente = crear_cliente()
for nombre in ("hechos", "sesiones"):
    col = obtener_coleccion(cliente, nombre)
    print(f"\n=== {nombre} ({col.count()} registros) ===")
    datos = col.get()
    for doc, meta in zip(datos["documents"], datos["metadatas"]):
        print("-", doc, meta)
