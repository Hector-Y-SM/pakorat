import qrcode
import json
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from io import BytesIO
from PIL import Image

# Configuración de cartas
COLORES = ["amarillo", "rojo", "verde", "azul"]
VALORES = list(range(10))  # 0-9

# Configuración de diseño
QR_SIZE = 3.0 * cm  # Tamaño del QR (aumentado a 3cm)
MARGIN = 0.3 * cm   # Margen alrededor del QR
LABEL_HEIGHT = 0.5 * cm  # Altura para el texto
CELL_WIDTH = QR_SIZE + (2 * MARGIN)
CELL_HEIGHT = QR_SIZE + (2 * MARGIN) + LABEL_HEIGHT

# Configuración de página
PAGE_WIDTH, PAGE_HEIGHT = A4
COLS = 4  # Columnas por página
ROWS = 5  # Filas por página
START_X = 1.5 * cm
START_Y = PAGE_HEIGHT - 2 * cm

def generar_qr(data):
    """Genera un código QR a partir de un diccionario"""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=15,  # Aumentado para mejor calidad
        border=2,     # Borde más visible
    )
    qr.add_data(json.dumps(data, ensure_ascii=False))
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    return img

def crear_pdf_etiquetas(nombre_archivo="etiquetas_uno_qr.pdf"):
    """Crea un PDF con todas las etiquetas QR organizadas"""
    c = canvas.Canvas(nombre_archivo, pagesize=A4)
    
    cartas = []
    for color in COLORES:
        for valor in VALORES:
            cartas.append({"color": color, "valor": valor})
    
    carta_index = 0
    total_cartas = len(cartas)
    
    while carta_index < total_cartas:
        # Dibujar grid en cada página
        for row in range(ROWS):
            for col in range(COLS):
                if carta_index >= total_cartas:
                    break
                
                carta = cartas[carta_index]
                
                # Calcular posición
                x = START_X + (col * CELL_WIDTH)
                y = START_Y - (row * CELL_HEIGHT)
                
                # Generar QR
                qr_img = generar_qr(carta)
                
                # Guardar temporalmente como archivo
                temp_filename = f"temp_qr_{carta['color']}_{carta['valor']}.png"
                qr_img.save(temp_filename)
                
                # Dibujar recuadro de corte (guías)
                c.setStrokeColorRGB(0.7, 0.7, 0.7)
                c.setDash(2, 2)
                c.rect(x, y - QR_SIZE - MARGIN - LABEL_HEIGHT, 
                       CELL_WIDTH, CELL_HEIGHT)
                c.setDash()
                
                # Dibujar QR
                c.drawImage(temp_filename, 
                           x + MARGIN, 
                           y - QR_SIZE - MARGIN, 
                           width=QR_SIZE, 
                           height=QR_SIZE)
                
                # Limpiar archivo temporal
                import os
                os.remove(temp_filename)
                
                # Dibujar texto identificador
                c.setFillColorRGB(0, 0, 0)
                c.setFont("Helvetica-Bold", 8)
                texto = f"{carta['color'].capitalize()} {carta['valor']}"
                text_width = c.stringWidth(texto, "Helvetica-Bold", 8)
                text_x = x + (CELL_WIDTH - text_width) / 2
                text_y = y - QR_SIZE - MARGIN - LABEL_HEIGHT + 0.1*cm
                c.drawString(text_x, text_y, texto)
                
                carta_index += 1
        
        # Nueva página si hay más cartas
        if carta_index < total_cartas:
            c.showPage()
    
    c.save()
    
    # Calcular páginas necesarias
    total_paginas = (total_cartas + (COLS*ROWS) - 1) // (COLS*ROWS)
    
    print(f"✅ PDF generado: {nombre_archivo}")
    print(f"📊 Total de etiquetas: {total_cartas}")
    print(f"📄 Páginas generadas: {total_paginas}")
    print(f"📐 Layout: {COLS} columnas x {ROWS} filas = {COLS*ROWS} por página")

if __name__ == "__main__":
    crear_pdf_etiquetas()
