import os
import cv2
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.utils import ImageReader

# --- CONFIGURACIÓN ---
CARPETA_IMAGENES = 'imgs'
ARCHIVO_SALIDA_PDF = 'cuadricula_separada_3x3.pdf'
LADO_CUADRADO_CM = 3.0  
COLUMNAS = 6
FILAS = 8

# NUEVO: Espacio entre fotos (en centímetros)
ESPACIO_X = 0.5 
ESPACIO_Y = 0.5

CARPETA_TEMPORAL = 'temp_squares'

if not os.path.exists(CARPETA_TEMPORAL):
    os.makedirs(CARPETA_TEMPORAL)

face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

def detectar_y_recortar_cuadrado(ruta_imagen, indice):
    img = cv2.imread(ruta_imagen)
    if img is None: return None
    
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    caras = face_cascade.detectMultiScale(gray, 1.1, 5, minSize=(30, 30))

    if len(caras) == 0:
        print(f"No se detectó rostro en: {ruta_imagen}")
        return None

    (x, y, w, h) = caras[0]
    pil_img = Image.open(ruta_imagen)
    img_w, img_h = pil_img.size

    cx, cy = x + w//2, y + h//2
    lado_recorte = int(max(w, h) * 1.5) # Un poco más de margen para que no quede tan apretado
    
    left = max(0, cx - lado_recorte // 2)
    top = max(0, cy - lado_recorte // 2)
    right = min(img_w, left + lado_recorte)
    bottom = min(img_h, top + lado_recorte)

    cara_recortada = pil_img.crop((left, top, right, bottom))
    cara_recortada = cara_recortada.resize((400, 400), Image.LANCZOS)
    
    ruta_temp = os.path.join(CARPETA_TEMPORAL, f'square_{indice}.jpg')
    cara_recortada.save(ruta_temp, "JPEG", quality=95)
    return ruta_temp

def generar_pdf_con_espacios(lista_fotos, archivo_salida):
    c = canvas.Canvas(archivo_salida, pagesize=A4)
    width_a4, height_a4 = A4
    
    # Conversión a puntos de ReportLab
    lado_pt = LADO_CUADRADO_CM * cm
    gap_x_pt = ESPACIO_X * cm
    gap_y_pt = ESPACIO_Y * cm
    
    # Calcular el ancho y alto TOTAL ocupado por la cuadrícula
    ancho_total_grid = (COLUMNAS * lado_pt) + ((COLUMNAS - 1) * gap_x_pt)
    alto_total_grid = (FILAS * lado_pt) + ((FILAS - 1) * gap_y_pt)
    
    # Centrar la cuadrícula en la página
    margin_x = (width_a4 - ancho_total_grid) / 2
    margin_y = (height_a4 - alto_total_grid) / 2

    idx = 0
    while idx < len(lista_fotos):
        for fila in range(FILAS):
            for col in range(COLUMNAS):
                if idx >= len(lista_fotos): break
                
                # Calcular X: Margen inicial + (columna * (ancho foto + espacio))
                x = margin_x + (col * (lado_pt + gap_x_pt))
                
                # Calcular Y: Empezamos desde arriba. 
                # Coordenada Y es el borde INFERIOR de la foto.
                y = height_a4 - margin_y - (fila * (lado_pt + gap_y_pt)) - lado_pt
                
                foto_path = lista_fotos[idx]
                c.drawImage(ImageReader(foto_path), x, y, width=lado_pt, height=lado_pt)
                
                # Opcional: Borde de corte muy suave (gris claro)
                c.setLineWidth(0.3)
                c.setStrokeColorRGB(0.7, 0.7, 0.7)
                c.rect(x, y, lado_pt, lado_pt, stroke=1, fill=0)
                
                idx += 1
            if idx >= len(lista_fotos): break
            
        c.showPage()
    
    c.save()
    print(f"--- PDF GENERADO: {archivo_salida} ---")

# --- FLUJO PRINCIPAL ---
archivos = [f for f in os.listdir(CARPETA_IMAGENES) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
archivos.sort()

fotos_finales = []
for i, nombre in enumerate(archivos):
    res = detectar_y_recortar_cuadrado(os.path.join(CARPETA_IMAGENES, nombre), i)
    if res: fotos_finales.append(res)

if fotos_finales:
    generar_pdf_con_espacios(fotos_finales, ARCHIVO_SALIDA_PDF)
else:
    print("Error: No se encontraron fotos o no se detectaron rostros.")