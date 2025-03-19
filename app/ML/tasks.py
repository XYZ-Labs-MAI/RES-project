from celery import shared_task
from PIL import Image
import io
import torch
import torchvision
from torch.serialization import safe_globals
import os
import logging


logger = logging.getLogger(__name__)
MODEL_PATH = './ML/yolo11n-obb.torchscript'

def load_model():
    try:
        # Проверка, существует ли файл модели
        if not os.path.exists(MODEL_PATH):
            log_message = f"Файл модели не найден по пути: {MODEL_PATH}"
            logger.error(log_message)
            raise FileNotFoundError(log_message)
        
        logger.info('Загрузка модели...')
        model = torch.jit.load(MODEL_PATH)
        model.eval()
        return model
    except FileNotFoundError as e:
        logger.error(f"Ошибка загрузки TorchScript модели: {e}")
        return None
    except Exception as e:
        logger.exception(f"Ошибка при загрузке TorchScript модели: {e}")
        return None
    

yolo_model = None

@shared_task
def detect_objects_task(image_data):
    global yolo_model
    if yolo_model is None:
        logger.error("Модель не была загружена, задача не может быть выполнена.")
        yolo_model = load_model() # Загрузка модели при первом вызове

    try:
        logger.info('TorchScript модель успешно загружена.')
        image = Image.open(io.BytesIO(image_data)).convert('RGB')
        image_tensor = torchvision.transforms.ToTensor()(image).unsqueeze(0)
        logger.info('Выполнение инференса TorchScript модели...')

        with torch.no_grad():
            # ЗДЕСЬ БАГ
            results = yolo_model(image_tensor)
        
        detections = []
        logger.info(f"Результаты YOLO: {results}")
        predictions = results.pandas().xyxy[0]
        for _, row in predictions.iterrows():
            x_min, y_min, x_max, y_max, confidence, class_id, class_name = row
            detections.append({
                'box': [int(x_min), int(y_min), int(x_max), int(y_max)],
                'label': class_name,
                'confidence': float(confidence)
            })
        logger.info('Детекция объектов завершена.')
        return detections

    except Exception as e:
        print(f"Ошибка при детекции объектов: {e}")
        return None