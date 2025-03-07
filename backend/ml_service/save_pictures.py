from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from authenticate.models import UserHistory, Users

def make_rec(original_img, processed_img, user_id):
    """
    Сохраняет запись в базу данных с оригинальным и обработанным изображением.
    """
    # Получаем пользователя
    user = get_object_or_404(Users, id=user_id)

    # Создаём запись в UserHistory
    new_record = UserHistory.objects.create(
        user=user,
        original_image=original_img,  # Используем объект UploadedFile напрямую
        processed_image=processed_img, 
    )

    return JsonResponse({
        "status": "success",
        "message": "UserHistory record created",
        "id": new_record.id,
    })