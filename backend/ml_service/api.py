from ninja import NinjaAPI, File
from ninja.responses import Response
from ninja.files import UploadedFile
from ultralytics import YOLO
from pydantic import BaseModel, Field
import cv2
from django.views.decorators.csrf import csrf_exempt
from multiprocessing import Manager, Process, freeze_support, set_start_method
import uuid
import os
import tempfile

manager = Manager()
image_queue = manager.Queue()  # создаёт очередь FIFO для подачи данных на обработку
result_queue = manager.Queue()  # вывод данных
NUM_PROCESS = 2

api = NinjaAPI()  # для создания api работы с моделькой (back и front связывается с моделькой по api)

# Pydantic-модель для обработки файла
class FileUpload(BaseModel):
    image: UploadedFile = File(...)

    class Config:
        arbitrary_types_allowed = True

def process_image(image_queue, result_queue):
    '''
    Обработка картинки
    '''
    try:
        # Инициализация модели YOLO один раз
        local_model = YOLO('backend/ml_service/models/yolo11m-obb.pt')
        print("Model initialized:", local_model)
    except Exception as e:
        print(f"Error initializing model: {e}")
        return

    while True:
<<<<<<< HEAD
        try:
            # Получаем изображение из очереди
            image_path, image_id = image_queue.get()
            if image_path is None:
                print("Received None, stopping process")
                break  # Останавливаем процесс
=======
        image_path, image_id = image_queue.get()
        if image_path is None:
            break                                 # изображение не найдено
        img = cv2.imread(image_path,1)
        results = local_model(img)[0]
        result_queue.put((image_id, get_predictions(results)), get_inference_time(results))  # закидываем вывод в result очередь
        image_queue.task_done()  # процесс закончен
>>>>>>> 411eadd6b75f0f11795dd94959f7d800a78299c0

            # Проверяем, существует ли файл
            if not os.path.exists(image_path):
                print(f"File not found: {image_path}")
                result_queue.put((image_id, "File not found"))
                image_queue.task_done()
                continue

            # Читаем изображение
            img = cv2.imread(image_path, 1)
            if img is None:
                print(f"Failed to read image: {image_path}")
                result_queue.put((image_id, "Failed to read image"))
                image_queue.task_done()
                continue

            # Обрабатываем изображение с помощью модели
            try:
                results = local_model(img)[0]
                predictions = get_predictions(results)  # Ваша функция для обработки результатов
                result_queue.put((image_id, predictions))
            except Exception as e:
                print(f"Error processing image {image_path}: {e}")
                result_queue.put((image_id, "Error processing image"))

            # Помечаем задачу как выполненную
            image_queue.task_done()

            # Удаляем временный файл
            try:
                os.remove(image_path)
                print(f"Deleted temporary file: {image_path}")
            except Exception as e:
                print(f"Error deleting file {image_path}: {e}")

        except Exception as e:
            print(f"Unexpected error in process_image: {e}")

def start_worker_processes(num_processes, image_queue, result_queue):
    '''
    параллеливание на процессы
    params: num_processes -- кол-во процессов
    '''
    processes = []
    for i in range(num_processes):
        process = Process(target=process_image, args=(image_queue, result_queue))
        process.start()
        processes.append(process)
    return processes  # для винды обязательно / для линукса отключить

def create_dict(**kwargs) -> dict:
    '''
    преобразует list из results в dict
    '''
    keys = ['confidence', 'name', 'xmax', 'xmin', 'ymax', 'ymin']
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
    objects = []
    for obj in obboxes:
        left, top, right, bottom = int(obj[0]), int(obj[1]), int(obj[2]), int(obj[3])
        confidence = obj[4]
        label = int(obj[5])
        result_dict = create_dict(confidence=confidence, name=names[label], xmax=right, xmin=left, ymax=bottom, ymin=top)
        objects.append(result_dict)
    return {
        "height": int(image_height),
        "objects": objects,
        "width": int(image_width),
    }

<<<<<<< HEAD
@api.post("/process-image/", response={200: dict, 400: dict})
def process_image(request, image: UploadedFile = File(...)):
    print("GOOD")
=======

def get_inference_time(results: str) -> dict:
    '''
    Получает время препроцессинга, инференса и постпроцессинга работы YOLO в dict для вывода


    params: results -- list предиктов модели
    '''
    try:

        if "Speed:" in results:
            results = results.split("Speed:")[1].strip()
        times = results.split(",")[:3]
        preprocess_time = float(times[0].split("ms")[0].strip())
        inference_time = float(times[1].split("ms")[0].strip())
        postprocess_time = float(times[2].split("ms")[0].strip())

        return {
            "preprocess_time_ms": preprocess_time,
            "inference_time_ms": inference_time,
            "postprocess_time_ms": postprocess_time,
        }
    except (IndexError, ValueError):
        return {
            "preprocess_time_ms": None,
            "inference_time_ms": None,
            "postprocess_time_ms": None,
        }


'''
#  boiler-plate code ПРОЧЕКАТЬ ЕГО 
@api.post("/process-image/")
def process_image(request, image: File):
>>>>>>> 411eadd6b75f0f11795dd94959f7d800a78299c0
    if image:
        image_id = str(uuid.uuid4())  # id картинки для менеджа
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp_file:
            temp_file.write(image.read())
            temp_file_path = temp_file.name
        image_queue.put((temp_file_path, image_id)) # закидываем картинку в очередь на процесс
        print('25')
        image_queue.join()  # join-ним процессы
        print('52')
        result = result_queue.get()
        print('2')
        return {"image_id": image_id, "result": result[1]}
    else:
        return Response({"error": "No image provided"}, status=400)

@api.get("/get-info/")
def get_info(request):
    return {"message": "This is a GET request response"}

def aggregate_statistics(results):  # парсинг списка
    class_stats = {}
    for result in results:
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
