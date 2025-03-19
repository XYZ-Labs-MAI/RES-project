from django.shortcuts import render
from django.http import JsonResponse
from .tasks import detect_objects_task
from django.views.decorators.csrf import csrf_exempt
import logging 


logger = logging.getLogger(__name__)

@csrf_exempt #  Убрать, если настроена отправка CSRF токена с frontend-а
def upload_image(request):
    if request.method == 'POST' and request.FILES.get('image'):
        image_file = request.FILES['image']
        image_data = image_file.read()

        # Запуск Celery
        task = detect_objects_task.delay(image_data) # .delay() запускает задачу в Celery
        logger.info(f"Задача детекции запущена. Task ID: {task.id}")

        return JsonResponse({'task_id': task.id, 'status': 'processing'}) # Возвращаем ID задачи
    
    logger.warning("Попытка загрузки изображения с использованием не-POST метода или без изображения.")
    return JsonResponse({'error': 'No image uploaded or wrong method'}, status=400)


def get_detection_result(request, task_id):
    """
    View для получения результатов задачи детекции по task_id.
    """
    from celery.result import AsyncResult

    task_result = AsyncResult(task_id)
    result = {
        "task_status": task_result.status,
        "task_id": task_id
    }
    if task_result.status == 'SUCCESS':
        detection_results = task_result.get()
        result['detection_results'] = detection_results # Получаем результаты детекции
        logger.info(f"Задача {task_id} выполнена успешно. Результаты: {detection_results}")
    elif task_result.status == 'FAILURE':
        error_message = str(task_result.traceback)
        result['error'] = error_message # Получаем traceback ошибки
        logger.error(f"Задача {task_id} завершилась с ошибкой: {error_message}")

    return JsonResponse(result)


def detection_view(request):
    return render(request, './index.html')