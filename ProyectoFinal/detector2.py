import cv2
from ultralytics import YOLO
import easyocr
from collections import defaultdict, Counter
from guardar_db import guardar_matricula
import re

# =========================
# CONFIG
# =========================
VIDEO_PATH = "video2.mp4"
MODEL_PATH = "best.pt"

model = YOLO(MODEL_PATH)
reader = easyocr.Reader(['en'])

cap = cv2.VideoCapture(VIDEO_PATH)

# =========================
# DATA
# =========================
readings = defaultdict(list)
final_plate = {}

# =========================
# LIMPIEZA OCR
# =========================
def corregir_matricula(texto):

    texto = texto.upper()

    texto = re.sub(r'[^A-Z0-9]', '', texto)

    texto = texto.replace("O", "0")
    texto = texto.replace("I", "1")
    texto = texto.replace("Z", "2")
    texto = texto.replace("S", "5")
    texto = texto.replace("B", "8")

    return texto

# =========================
# LOOP PRINCIPAL
# =========================
while cap.isOpened():

    ret, frame = cap.read()

    if not ret:
        break

    results = model.track(
        frame,
        persist=True,
        conf=0.5
    )

    if results[0].boxes.id is not None:

        boxes = results[0].boxes.xyxy.cpu().numpy()

        ids = results[0].boxes.id.cpu().numpy().astype(int)

        for box, tid in zip(boxes, ids):

            x1, y1, x2, y2 = map(int, box)

            crop = frame[y1:y2, x1:x2]

            if crop.size == 0:
                continue

            gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)

            text = reader.readtext(
                gray,
                allowlist="ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
            )

            if text:

                raw = "".join([t[1] for t in text])

                plate = corregir_matricula(raw)

                if 5 <= len(plate) <= 10:

                    readings[tid].append(plate)

            # =========================
            # DIBUJAR
            # =========================
            cv2.rectangle(
                frame,
                (x1, y1),
                (x2, y2),
                (0, 255, 0),
                2
            )

            cv2.putText(
                frame,
                f"ID {tid}",
                (x1, y1 - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 255, 0),
                2
            )

    cv2.imshow("Parking AI", frame)

    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()

# =========================
# MATRÍCULA FINAL
# =========================
for tid, vals in readings.items():

    if vals:

        mejor = Counter(vals).most_common(1)[0][0]

        final_plate[tid] = mejor

# =========================
# GUARDAR DB
# =========================
for tid, plate in final_plate.items():

    guardar_matricula(tid, plate)

# =========================
# RESULTADO FINAL
# =========================
print("\n✅ RESULTADO FINAL\n")

for tid, plate in final_plate.items():

    print(f"Coche {tid} -> {plate}")