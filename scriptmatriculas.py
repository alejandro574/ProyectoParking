import cv2
import easyocr
import os

# --- CONFIGURACIÓN ---
IMAGE_PATH = r'c:/Users/alumnomizv/Desktop/protyecto pruebas/coche.jpg.png'
OUTPUT_FOLDER = r'c:/Users/alumnomizv/Desktop/protyecto pruebas/output'

os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# --- CARGAR IMAGEN ---
image = cv2.imread(IMAGE_PATH)
image_display = image.copy()  # copia para dibujar

# --- INICIALIZAR EASYOCR ---
reader = easyocr.Reader(['en'])

# --- DETECTAR TEXTO ---
results = reader.readtext(image)

# --- PROCESAR RESULTADOS ---
best_plate = None
best_prob = 0

for (bbox, text, prob) in results:
    if prob > 0.5:
        (top_left, top_right, bottom_right, bottom_left) = bbox
        top_left = tuple(map(int, top_left))
        bottom_right = tuple(map(int, bottom_right))

        # Dibujar rectángulo y texto
        cv2.rectangle(image_display, top_left, bottom_right, (0, 255, 0), 2)
        cv2.putText(image_display, text, (top_left[0], top_left[1]-10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,255,0), 2)

        # Guardamos la matrícula con mayor probabilidad
        if prob > best_prob:
            best_prob = prob
            best_plate = image[top_left[1]:bottom_right[1], top_left[0]:bottom_right[0]]
            best_text = text

        print(f"Matrícula detectada: {text} (confianza: {prob:.2f})")

# --- GUARDAR MATRÍCULA EXTRAÍDA ---
if best_plate is not None:
    plate_path = os.path.join(OUTPUT_FOLDER, "matricula_extraida.jpg")
    cv2.imwrite(plate_path, best_plate)
    print(f"Matrícula guardada en: {plate_path}")
else:
    print("No se detectó ninguna matrícula.")

# --- GUARDAR IMAGEN FINAL CON RECTÁNGULOS ---
output_path = os.path.join(OUTPUT_FOLDER, "resultado_detectado.jpg")
cv2.imwrite(output_path, image_display)
print(f"Imagen con detecciones guardada en: {output_path}")

print("\nProceso finalizado. Revisa la carpeta 'output' para ver resultados.")
