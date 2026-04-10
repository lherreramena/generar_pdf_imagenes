import os
import cv2
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.utils import ImageReader

# --- CONFIGURACIÓN ---
CARPETA_IMAGENES = 'imgs'
ARCHIVO_SALIDA_PDF = 'cuadricula_3x3.pdf'
LADO_CUADRADO_CM = 3.0  # Tamaño de cada foto
COLUMNAS = 6
FILAS = 8

# Rutas temporales
CARPETA_TEMPORAL = 'temp_squares'

if not os.path.exists(CARPETA_TEMPORAL):
    os.makedirs(CARPETA_TEMPORAL)

# Detector de rostros
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

def detectar_y_recortar_cuadrado(ruta_imagen, indice):
    """Detecta el rostro y lo recorta en un cuadrado perfecto."""
    img = cv2.imread(ruta_imagen)
    if img is None: return None
    
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    caras = face_cascade.detectMultiScale(gray, 1.1, 5, minSize=(30, 30))

    if len(caras) == 0:
        print(f"No se detectó rostro en: {ruta_imagen}")
        return None

    (x, y, w, h) = caras[0]
    
    # Abrir con Pillow para el recorte final
    pil_img = Image.open(ruta_imagen)
    img_w, img_h = pil_img.size

    # Calcular el centro de la cara detectada
    cx, cy = x + w//2, y + h//2
    
    # Determinar el tamaño del recorte (usamos el lado más grande de la detección + margen)
    lado_recorte = int(max(w, h) * 1.4) 
    
    # Definir coordenadas del cuadrado
    left = max(0, cx - lado_recorte // 2)
    top = max(0, cy - lado_recorte // 2)
    right = min(img_w, left + lado_recorte)
    bottom = min(img_h, top + lado_recorte)

    # Recortar y guardar
    cara_recortada = pil_img.crop((left, top, right, bottom))
    # Forzar a que sea un cuadrado perfecto de 300x300 px para uniformidad
    cara_recortada = cara_recortada.resize((300, 300), Image.LANCZOS)
    
    ruta_temp = os.path.join(CARPETA_TEMPORAL, f'square_{indice}.jpg')
    cara_recortada.save(ruta_temp, "JPEG")
    return ruta_temp

def generar_pdf_cuadricula(lista_fotos, archivo_salida):
    c = canvas.Canvas(archivo_salida, pagesize=A4)
    width_a4, height_a4 = A4
    
    lado_pt = LADO_CUADRADO_CM * cm
    
    # Ajuste de márgenes para centrar la cuadrícula de 6x8
    # 6 col * 3cm = 18cm (A4 mide 21cm, sobran 3cm / 2 = 1.5cm margen x)
    # 8 filas * 3cm = 24cm (A4 mide 29.7cm, sobran 5.7cm / 2 = 2.8cm margen y)
    margin_x = (width_a4 - (COLUMNAS * lado_pt)) / 2
    margin_y = (height_a4 - (FILAS * lado_pt)) / 2

    idx = 0
    while idx < len(lista_fotos):
        for fila in range(FILAS):
            for col in range(COLUMNAS):
                if idx >= len(lista_fotos): break
                
                # Calcular coordenadas (0,0 es abajo a la izquierda en ReportLab)
                x = margin_x + (col * lado_pt)
                y = height_a4 - margin_y - ((fila + 1) * lado_pt)
                
                foto_path = lista_fotos[idx]
                c.drawImage(ImageReader(foto_path), x, y, width=lado_pt, height=lado_pt)
                
                # Dibujar un borde fino negro alrededor de cada foto
                c.setLineWidth(0.5)
                c.setStrokeColorRGB(0, 0, 0)
                c.rect(x, y, lado_pt, lado_pt, stroke=1, fill=0)
                
                idx += 1
            if idx >= len(lista_fotos): break
            
        c.showPage() # Nueva página si faltan fotos
    
    c.save()
    print(f"PDF creado: {archivo_salida}")

# --- EJECUCIÓN ---
archivos = [f for f in os.listdir(CARPETA_IMAGENES) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
archivos.sort()

fotos_finales = []
for i, nombre in enumerate(archivos):
    res = detectar_y_recortar_cuadrado(os.path.join(CARPETA_IMAGENES, nombre), i)
    if res: fotos_finales.append(res)

if fotos_finales:
    generar_pdf_cuadricula(fotos_finales, ARCHIVO_SALIDA_PDF)
else:
    print("No se pudieron procesar rostros.")