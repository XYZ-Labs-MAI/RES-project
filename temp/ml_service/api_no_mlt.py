from ninja import NinjaAPI, File
from ninja.responses import Response
from ninja.files import UploadedFile
from ultralytics import YOLO
from pydantic import BaseModel
import cv2
from PIL import Image
from django.views.decorators.csrf import csrf_exempt
from django.core.files import File
import uuid
import os
import tempfile

api = NinjaAPI()  # для создания api работы с моделькой (back и front связывается с моделькой по api)

# Pydantic-модель для обработки файла
class FileUpload(BaseModel):
    image: UploadedFile = File(...)

    class Config:
        arbitrary_types_allowed = True

try:
    # Инициализация модели YOLO один раз
    local_model = YOLO('backend/ml_service/models/yolo11m-obb.pt')
    print("Model initialized")
except Exception as e:
    print(f"Error initializing model: {e}")


def process_image(image_path, image_id):
    '''
    Обработка картинки
    '''
    try:
        # Проверяем, существует ли файл
        if not os.path.exists(image_path):
            print(f"File not found: {image_path}")
            return (image_id, "Error file not found")

        # Читаем изображение
        img = cv2.imread(image_path, 1)
        if img is None:
            print(f"Failed to read image: {image_path}")
            return (image_id, "Error failed to read image")

        # Обрабатываем изображение с помощью модели
        try:
            # сев предиктов в виде картинки, аккуратно, очень быстро размножается папками
            results = local_model(img, save=True, 
                                  project='backend/ml_service/test_pictures/serv_test/')[0]
            predictions = get_predictions(results)
            time = results.speed
            out = (image_id, predictions, time)
        except Exception as e:
            print(f"Error processing image {image_path}: {e}")
            return (image_id, "Error processing image")

        # Удаляем временный файл
        try:
            os.remove(image_path)
            print(f"Deleted temporary file: {image_path}")
        except Exception as e:
            print(f"Error deleting file {image_path}: {e}")
        return out

    except Exception as e:
        print(f"Unexpected error in process_image: {e}")
        return (image_id, "Unexpected error in process_image")


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


@api.post("/process-image/", response={200: dict, 400: dict})
def process_image_endpoint(request, image: UploadedFile):
    if image:
        image_id = str(uuid.uuid4())  # id картинки для менеджа
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp_file:
            temp_file.write(image.read())
            temp_file_path = temp_file.name

        # Process the image
        result = process_image(temp_file_path, image_id)
        print(aggregate_statistics(result[1]))
        return {"image_id": image_id, "result": result[1]}
    else:
        return Response({"error": "No image provided"}, status=400)

@api.get("/get-info/")
def get_info(request):
    return {"message": "This is a GET request response"}


def aggregate_statistics(result):  # парсинг списка
    class_stats = {}
    objects = result.get('objects', [])
    for obj in objects:
        class_name = obj.get('name')
        confidence = obj.get('confidence', 0.0)
        if class_name:
            if class_name not in class_stats:
                class_stats[class_name] = {'count': 0, 'total_confidence': 0.0}
            class_stats[class_name]['count'] += 1
            class_stats[class_name]['total_confidence'] += confidence

    aggregated_stats = {}
    for class_name, stats in class_stats.items():
        count = stats['count']
        total_confidence = stats['total_confidence']
        if count > 0:
            average_confidence = total_confidence / count
            aggregated_stats[class_name] = {
                'average_confidence': average_confidence,
                'count': count
            }

    return aggregated_stats