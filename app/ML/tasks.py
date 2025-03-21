from celery import shared_task
import numpy as np
import os
import logging
from torchvision import transforms
from ultralytics import YOLO
import cv2


logger = logging.getLogger(__name__)
MODEL_PATH = './ML/yolo11n-obb.pt'
yolo_model = None

def load_model():
    try:
        # Проверка, существует ли файл модели
        if not os.path.exists(MODEL_PATH):
            log_message = f"Файл модели не найден по пути: {MODEL_PATH}"
            logger.error(log_message)
            raise FileNotFoundError(log_message)
        
        logger.info('Загрузка модели...')
        model = YOLO(MODEL_PATH)
        model.to('cpu')
        return model
    except FileNotFoundError as e:
        logger.error(f"Ошибка загрузки модели: {e}")
        return None
    except Exception as e:
        logger.exception(f"Ошибка при загрузке модели: {e}")
        return None


def create_dict(**kwargs) -> dict:
    '''
    преобразует list из results в dict
    '''
    keys = ['confidence', 'name', 'X', 'Y', 'Width', 'Heigth', 'Rotation']
    result_dict = {key: kwargs.get(key, None) for key in keys}
    return result_dict

def get_predictions(results) -> dict:
    '''
    получает результаты работы YOLO и преобразует в dict для вывода
    params: results -- list предиктов модели
    '''
    image_height, image_width = results.orig_shape
    names = results.names
    obboxes = results.obb.data.tolist()
    obj = results.obb
    # print(obj.xyxyxyxy.tolist(), obj.xyxyxyxyn.tolist(), (( obj.xywhr.tolist() )), sep='\n')
    objects = []
    for obj in obboxes:
        X, Y, W, H, R = int(obj[0]), int(obj[1]), int(obj[2]), int(obj[3]), int(obj[4])
        confidence = obj[5]
        label = int(obj[6])
        result_dict = create_dict(confidence=confidence, name=names[label], X=X, Y=Y, Width=W, Heigth=H, Rotation=R)
        objects.append(result_dict)
    return {
        "height": int(image_height),
        "objects": objects,
        "width": int(image_width),
    }

@shared_task
def detect_objects_task(image_data):
    global yolo_model
    if yolo_model is None:
        logger.error("Модель не была загружена, задача не может быть выполнена.")
        yolo_model = load_model() # Загрузка модели при первом вызове
    try:
        logger.info('модель успешно загружена.')
        logger.info('Выполнение инференса модели...')
        if isinstance(image_data, (bytes, bytearray)):
            nparr = np.fromstring(image_data, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        else:
            img = image_data

        results = yolo_model(img)[0]

        detections = []
        detections = get_predictions(results)
        time = results.speed
        logger.info('Детекция объектов завершена.')
        return (detections, time)
    except Exception as e:
        logger.error(f"Ошибка при детекции объектов: {e}")
        return None
    
def main():
    img = cv2.imread('ML/test.png', 1)
    res = detect_objects_task(img)
    return res


if __name__ == "__main__":
    print(main())