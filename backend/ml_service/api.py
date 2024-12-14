# from ninja import NinjaAPI, File
# from ninja.responses import Response
from ultralytics import YOLO
import cv2
from multiprocessing import Manager, Process, freeze_support, set_start_method
from uuid import uuid4

# manager = Manager()
# image_queue = manager.Queue()  # создаёт очередь FIFO для подачи данных на обработку
# result_queue = manager.Queue()  # вывод данных
NUM_PROCESS = 2

# api = NinjaAPI()  # для создания api работы с моделькой (back и front связывается с моделькой по api)


def process_image(image_queue, result_queue):  # чек this
    '''
    обработка картинки

    '''
    local_model = YOLO('backend/ml_service/models/yolo11m-obb.pt')  # инициализация модели
    print(local_model)
    while True:
        image_path, image_id = image_queue.get()
        if image_path is None:
            break                                 # изображение не найдено
        img = cv2.imread(image_path,1)
        results = local_model(img)[0]
        result_queue.put((image_id, get_predictions(results)), get_inference_time(results))  # закидываем вывод в result очередь
        image_queue.task_done()  # процесс закончен


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
    return processes #  для винды обязательно / для линукса отключить


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
    if image:
        image_id = str(uuid.uuid4())            #  id картинки для менеджа
        image_queue.put((image, image_id))      #  закидываем картинку в очередь на процесс
        image_queue.join()                      #  join-ним процессы
        result = result_queue.get(image_id)
        return {"image_id": image_id, "result": result}
    else:
        return Response({"error": "No image path provided"}, status=400)

@api.get("/process-image/")
def invalid_request(request):
    return Response({"error": "Invalid request"}, status=400)
'''


def test(image, image_queue, result_queue):
    # ошибка файл дампа на винде, передаю агрументы как путь, а не как файл (аккуратно с кодом)
    #with open(image_path, 'rb') as image:      
   
    image_id = str(uuid4())                #  id картинки для менеджа
    image_queue.put((image, image_id))          #  закидываем картинку в очередь на процесс
    image_queue.join()                          #  join-ним процессы
    result = result_queue.get(image_id)

    return {"image_id": image_id, "result": result}
    

if __name__ == "__main__":
    #  необходимо для винды, потому что она не юзает fork 
    freeze_support()
    set_start_method('spawn')
    manager = Manager()
    image_queue = manager.Queue()  # создаёт очередь FIFO для подачи данных на обработку
    result_queue = manager.Queue()  # вывод данных
    manager.start
    #  пока комментим, потому что в винде ошибки из за запуска не в теле "__main__"
    # start_worker_processes(2)  # два процесса на работу инференса

    processes = start_worker_processes(NUM_PROCESS, image_queue, result_queue) #  под винду 
    image_path = 'backend/ml_service/test_pictures/su-57.png'
    response = test(image_path, image_queue, result_queue)
    print(response)

    for _ in range(NUM_PROCESS):
        image_queue.put((None, None))
    for process in processes:
        process.join()