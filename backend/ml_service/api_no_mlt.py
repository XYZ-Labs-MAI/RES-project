from ninja import NinjaAPI, File
from ninja.responses import Response
from ninja.files import UploadedFile
from ultralytics import YOLO
from pydantic import BaseModel
from .save_pictures import make_rec
from django.core.files.uploadedfile import InMemoryUploadedFile
from tempfile import NamedTemporaryFile
import numpy as np
import cv2
from PIL import Image
from django.views.decorators.csrf import csrf_exempt
from django.core.files import File
import uuid
import os

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


def process_image(image_file, image_id, user_id):
    '''
    Обработка картинки и сохранение результатов в базу данных.
    '''
    try:
        # Проверяем, что image_file является объектом UploadedFile
        if not isinstance(image_file, InMemoryUploadedFile):
            print(f"Invalid file type: {type(image_file)}")
            return (image_id, "Error invalid file type")

        # Читаем изображение из UploadedFile
        img_data = image_file.read()  # Читаем данные файла
        img_array = np.frombuffer(img_data, np.uint8)  # Преобразуем в массив numpy
        img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)  # Декодируем изображение

        if img is None:
            print("Failed to decode image")
            return (image_id, "Error failed to decode image")

        # Обрабатываем изображение с помощью модели
        try:
            # Пример обработки изображения
            results = local_model(img, save=True, 
                                  project='backend/ml_service/test_pictures/serv_test/')[0]
            predictions = get_predictions(results)
            time = results.speed

            # Сохраняем обработанное изображение во временный файл
            with NamedTemporaryFile(delete=False, suffix=".jpg") as temp_file:
                processed_image_path = temp_file.name
                # Используем метод plot() для получения изображения с аннотациями
                annotated_image = results.plot()
                cv2.imwrite(processed_image_path, annotated_image)  # Сохраняем изображение

            # Открываем обработанное изображение как InMemoryUploadedFile
            with open(processed_image_path, 'rb') as processed_file:
                processed_image = InMemoryUploadedFile(
                    processed_file,
                    None,  # field_name
                    f"processed_{image_file.name}",  # file name
                    'image/jpeg',  # content_type
                    os.path.getsize(processed_image_path),  # size
                    None,  # charset
                )

                # Сохраняем запись в базу данных
                response = make_rec(
                    original_img=image_file,
                    processed_img=processed_image,
                    user_id=user_id,
                )

                if response.status_code != 200:
                    print(f"Failed to save record to database: {response.content}")
                    return (image_id, "Error saving record to database")

            out = (image_id, predictions, time)
        except Exception as e:
            print(f"Error processing image: {e}")
            return (image_id, "Error processing image")

        # Удаляем временный файл
        try:
            os.remove(processed_image_path)
            print(f"Deleted temporary file: {processed_image_path}")
        except Exception as e:
            print(f"Error deleting file {processed_image_path}: {e}")
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
def process_image_endpoint(request):
    print("Получен запрос на обработку изображения")
    
    # Проверяем, что файл присутствует в запросе
    if "image" not in request.FILES:
        print("Ошибка: файл не предоставлен")
        return Response({"error": "No image provided"}, status=400)

    image = request.FILES["image"]
    print(f"Имя файла: {image.name}, размер: {image.size} байт")

    try:
        image_id = str(uuid.uuid4())  # id картинки для менеджа
        user_id = request.user.id  # Предполагаем, что пользователь авторизован

        # Process the image
        result = process_image(image, image_id, user_id)
        if isinstance(result[1], str) and result[1].startswith("Error"):
            print(f"Ошибка обработки изображения: {result[1]}")
            return Response({"error": result[1]}, status=400)

        # Проверяем, что result[1] является словарём
        if not isinstance(result[1], dict):
            print(f"Ошибка: результат не является словарём: {result[1]}")
            return Response({"error": "Invalid result format"}, status=500)

        print("Изображение успешно обработано")
        print(aggregate_statistics(result[1]))
        return {"image_id": image_id, "result": result[1]}
    except Exception as e:
        print(f"Неожиданная ошибка: {e}")
        return Response({"error": "Internal server error"}, status=500)

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