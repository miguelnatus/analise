# slot_analysis.py
# Script para analisar padrões em vídeo de slots usando OpenCV, TensorFlow e Tesseract

"""
Requisitos:
    pip install opencv-python tensorflow pytesseract numpy
Certifique-se de ter o Tesseract OCR instalado no seu sistema.
No Windows, configure pytesseract.pytesseract.tesseract_cmd se necessário.
"""

import cv2
import numpy as np
from tensorflow.keras.models import load_model
import pytesseract
import csv

# Ajuste este caminho se necessário:
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def carregar_modelo(path_modelo):
    model = load_model(path_modelo)
    return model

def preprocess_roi(roi, target_size=(64, 64)):
    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    resized = cv2.resize(gray, target_size)
    norm = resized.astype('float32') / 255.0
    return np.expand_dims(norm, axis=(0, -1))

def classificar_simbolo(roi, model, classes):
    x = preprocess_roi(roi)
    preds = model.predict(x)
    idx = np.argmax(preds, axis=1)[0]
    return classes[idx]

def ocr_texto(roi):
    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    config = '--psm 7 digits'
    text = pytesseract.image_to_string(thresh, config=config)
    return text.strip()

def processar_video(path_video, model_path, classes, output_csv='resultado_slots.csv'):
    model = carregar_modelo(model_path)

    # Defina as ROIs: (x, y, w, h)
    rolo_rois = [
        (100, 200, 64, 64), (100, 270, 64, 64), (100, 340, 64, 64),
        (200, 200, 64, 64), (200, 270, 64, 64), (200, 340, 64, 64),
        (300, 200, 64, 64), (300, 270, 64, 64), (300, 340, 64, 64),
    ]
    credito_roi = (400, 50, 150, 50)

    cap = cv2.VideoCapture(path_video)
    frame_idx = 0

    with open('/mnt/data/slot_analysis.py', 'w', encoding='utf-8') as f:
        f.write(script_content)

    print("Arquivo criado em /mnt/data/slot_analysis.py")
    print("
--- Conteúdo do script ---
")
    print(script_content)
