import os
import cv2
from PIL import Image, ImageDraw, ImageOps
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.utils import ImageReader

# --- CONFIGURACIÓN ---
CARPETA_IMAGENES = 'imgs'  # Carpeta donde están tus JPEGs
ARCHIVO_SALIDA_PDF = 'hoja_caras.pdf'
DIAMETRO_CM = 7.0               # Diámetro objetivo para el círculo en el PDF

# Rutas para guardar archivos temporales
CARPETA_TEMPORAL = 'temp_faces'

# --- INICIALIZACIÓN ---
if not os.path.exists(CARPETA_TEMPORAL):
    os.makedirs(CARPETA_TEMPORAL)

# Cargar el detector de rostros preentrenado de OpenCV
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# --- FUNCIONES ---

def detectar_y_recortar_circular(ruta_imagen, num_rostro):
    """Detecta el rostro, lo recorta circularmente y lo guarda como PNG."""
    try:
        # 1. Cargar imagen con OpenCV
        img = cv2.imread(ruta_imagen)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    except Exception as e:
        print(f"Error cargando {ruta_imagen}: {e}")
        return None

    # 2. Detectar rostros
    # Ajusta 'scaleFactor' y 'minNeighbors' si la detección no es buena
    caras = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

    if len(caras) == 0:
        print(f"No se detectó rostro en: {ruta_imagen}")
        return None

    # Tomar la primera cara detectada (x, y, ancho, alto)
    (x, y, w, h) = caras[0]

    # 3. Preparar el recorte circular (usando Pillow)
    pil_image = Image.open(ruta_imagen).convert("RGBA")
    
    # Crear una máscara circular
    # El recorte será un cuadrado centrado en la cara detectada
    # Añadimos un pequeño margen alrededor de la cara detectada
    margin_percent = 0.2
    mw = int(w * margin_percent)
    mh = int(h * margin_percent)
    
    # Asegurarse de que el cuadrado de recorte no se salga de la imagen
    img_w, img_h = pil_image.size
    cx = x + w // 2
    cy = y + h // 2
    
    # Determinar el radio del círculo de recorte
    r = max(w, h) // 2 + max(mw, mh)
    
    # Coordenadas del cuadrado de recorte
    left = max(0, cx - r)
    top = max(0, cy - r)
    right = min(img_w, cx + r)
    bottom = min(img_h, cy + r)
    
    # Recortar el cuadrado
    face_square = pil_image.crop((left, top, right, bottom))
    size = face_square.size # Debería ser cuadrado o casi cuadrado
    
    # Crear la máscara circular
    mask = Image.new('L', size, 0)
    draw = ImageDraw.Draw(mask)
    # Dibujar el círculo blanco (opaco) que define la forma
    draw.ellipse((0, 0) + size, fill=255)
    
    # Aplicar la máscara
    face_circular = ImageOps.fit(face_square, mask.size, centering=(0.5, 0.5))
    face_circular.putalpha(mask)

    # 4. Guardar como PNG temporal (para mantener la transparencia)
    ruta_temp_png = os.path.join(CARPETA_TEMPORAL, f'face_{num_rostro}.png')
    face_circular.save(ruta_temp_png, format="PNG")
    
    return ruta_temp_png

def generar_pdf(lista_rostros_recortados, archivo_salida):
    """Crea un PDF A4 con 6 imágenes por hoja en una cuadrícula."""
    c = canvas.Canvas(archivo_salida, pagesize=A4)
    width, height = A4 # Ancho y alto de A4 en puntos

    # Conversión de CM a puntos de PDF (ReportLab usa puntos)
    d_pt = DIAMETRO_CM * cm
    
    # Definir márgenes y espacios para la cuadrícula (A4 es ~21x29.7 cm)
    margin_x = 3 * cm  # Margen izquierdo total
    margin_y = 3 * cm  # Margen superior total
    gap_x = 2 * cm     # Espacio horizontal entre círculos
    gap_y = 2 * cm     # Espacio vertical entre círculos
    
    # Diseño de cuadrícula: 2 columnas, 3 filas
    num_cols = 2
    num_rows = 3
    rostros_por_pagina = num_cols * num_rows

    contador_rostros = 0
    
    print(f"Iniciando creación de PDF con {len(lista_rostros_recortados)} rostros...")

    while contador_rostros < len(lista_rostros_recortados):
        
        # Iterar sobre las filas y columnas de la página actual
        for row in range(num_rows):
            for col in range(num_cols):
                
                if contador_rostros >= len(lista_rostros_recortados):
                    break # No hay más rostros

                ruta_cara = lista_rostros_recortados[contador_rostros]
                
                # Calcular la posición (x, y) de la esquina superior izquierda del círculo
                # ReportLab usa coordenadas (0,0) en la esquina inferior izquierda
                x = margin_x + col * (d_pt + gap_x)
                y = height - margin_y - (row + 1) * d_pt - row * gap_y
                
                # Dibujar la imagen recortada
                try:
                    cara_reader = ImageReader(ruta_cara)
                    # drawImage(image, x, y, width, height, mask='auto')
                    # x, y son las coordenadas de la esquina inferior izquierda de la imagen
                    c.drawImage(cara_reader, x, y, width=d_pt, height=d_pt, mask='auto')
                    
                    # Opcional: Dibujar un borde circular para verificar el tamaño
                    # c.setStrokeColorRGB(0.8, 0.8, 0.8) # Gris claro
                    # c.setLineWidth(1)
                    # c.circle(x + d_pt/2, y + d_pt/2, d_pt/2, stroke=1, fill=0)

                except Exception as e:
                    print(f"Error al dibujar imagen en PDF: {e}")

                contador_rostros += 1

            if contador_rostros >= len(lista_rostros_recortados):
                break
        
        # Si quedan más rostros, finalizar la página actual y crear una nueva
        if contador_rostros < len(lista_rostros_recortados):
            c.showPage()
            print("Página añadida al PDF.")

    c.save()
    print(f"PDF generado exitosamente: {archivo_salida}")

# --- FLUJO PRINCIPAL ---

def main():
    # 1. Obtener lista de imágenes
    formatos_soportados = ('.jpg', '.jpeg', '.png')
    archivos = [f for f in os.listdir(CARPETA_IMAGENES) if f.lower().endswith(formatos_soportados)]
    archivos.sort() # Opcional: ordenar por nombre
    
    if not archivos:
        print(f"No se encontraron imágenes válidas en '{CARPETA_IMAGENES}'.")
        return

    # 2. Procesar imágenes una por una
    rostros_procesados = []
    print(f"Procesando {len(archivos)} imágenes...")
    
    for i, archivo in enumerate(archivos):
        ruta_completa = os.path.join(CARPETA_IMAGENES, archivo)
        print(f"[{i+1}/{len(archivos)}] Procesando {archivo}...")
        
        # Detectar cara, recortar circularmente y guardar PNG temp
        ruta_temp = detectar_y_recortar_circular(ruta_completa, i)
        
        if ruta_temp:
            rostros_procesados.append(ruta_temp)

    # 3. Generar el PDF
    if rostros_procesados:
        generar_pdf(rostros_procesados, ARCHIVO_SALIDA_PDF)
    else:
        print("No se detectaron rostros válidos para generar el PDF.")

    # 4. Limpieza (Opcional: borrar la carpeta temporal)
    # import shutil
    # shutil.rmtree(CARPETA_TEMPORAL)
    # print("Archivos temporales eliminados.")

if __name__ == '__main__':
    main()
    