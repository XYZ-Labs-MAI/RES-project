import requests
from datetime import date
import logging
from django.contrib.auth import get_user_model

# Настройка логгера
logger = logging.getLogger(__name__)

def get_wms_image(bbox: list, date: date, max_cloud_cover: int,
                 srs: str, user_id: int, layer: str = 'TRUE_COLOR', image_format: str = 'image/jpeg',
                 width: int = 2500, height: int = 2500,) -> bytes:
    """
    Получает изображение через Sentinel Hub WMS API
    
    Args:
        bbox: Список координат [min_lon, min_lat, max_lon, max_lat]
        date: Дата съемки (datetime.date объект)
        max_cloud_cover: Максимальная облачность (0-100)
        layer: Слой WMS (по умолчанию 'TRUE_COLOR')
        image_format: Формат изображения (по умолчанию 'image/jpeg')
        width: Ширина изображения (по умолчанию 1024)
        height: Высота изображения (по умолчанию 1024)
        srs: Система координат (по умолчанию 'EPSG:4326')
        тест для карт BBOX=3238005,5039853,3244050,5045897
    
    Returns:
        bytes: Бинарные данные изображения
    
    Raises:
        ValueError: При ошибках запроса или неверных данных
    """
    # ID вашего инстанса Sentinel Hub
    
    User = get_user_model()
    try:
        user = User.objects.get(pk=user_id)
        instance_id = user.instance_id
        if not instance_id:
            raise ValueError("У пользователя не настроен sentinel_instance_id")
    except User.DoesNotExist:
        raise ValueError("Пользователь не найден")
    
    base_url = f"https://services.sentinel-hub.com/ogc/wms/{instance_id}"
    
    # Проверка входных параметров
    if not isinstance(bbox, list) or len(bbox) != 4:
        raise ValueError("bbox должен быть списком из 4 элементов [min_lon, min_lat, max_lon, max_lat]")
    
    if max_cloud_cover < 0 or max_cloud_cover > 100:
        raise ValueError("max_cloud_cover должен быть между 0 и 100")
    
    # Формирование параметров запроса
    params = {
        'service': 'WMS',
        'request': 'GetMap',
        'layers': layer,
        'bbox': ','.join(str(coord) for coord in bbox),
        'width': width,
        'height': height,
        'srs': srs,
        'format': image_format,
        'time': f"{date}T00:00:00Z/{date}T23:59:59Z",
        'maxcc': max_cloud_cover,
        'transparent': 'false',
    }
    
    try:
        # Выполнение запроса с таймаутом
        response = requests.get(base_url, params=params, timeout=30)
        response.raise_for_status()
        
        # Проверка типа содержимого
        content_type = response.headers.get('Content-Type', '')
        if not content_type.startswith('image/'):
            raise ValueError(f"Ожидалось изображение, получен Content-Type: {content_type}")
            
        return response.content
        
    except requests.exceptions.RequestException as e:
        error_msg = f"WMS Request Failed. URL: {response.url if 'response' in locals() else base_url}\nError: {str(e)}"
        if hasattr(e, 'response'):
            error_msg += f"\nResponse: {e.response.text[:500]}"
        logger.error(error_msg)
        raise ValueError("Ошибка загрузки изображения") from e