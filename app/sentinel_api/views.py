from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import SentinelSearchForm
from .api import get_wms_image
from datetime import timedelta
from django.http import FileResponse, Http404
import os
from django.conf import settings
from datetime import datetime

@login_required
def search_view(request):
    if request.method == 'POST':
        form = SentinelSearchForm(request.POST)
        if form.is_valid():
            try:
                bbox_data = form.get_bbox()
                start_date = form.cleaned_data['start_date']
                end_date = form.cleaned_data['end_date']
                max_cloud_cover = form.cleaned_data['max_cloud_cover']
                max_images = form.cleaned_data['max_images']
                
                img_dir = os.path.join(settings.MEDIA_ROOT, 'sentinel_images')
                if not os.path.exists(img_dir):
                    os.makedirs(img_dir)
                
                delta = end_date - start_date
                date_step = max(1, delta.days // max_images) if delta.days > 0 else 1
                target_dates = [
                    start_date + timedelta(days=i) 
                    for i in range(0, delta.days + 1, date_step)
                ][:max_images]
                
                images = []
                BLACK_IMAGE_SIZE = 19876  # Размер черного изображения в байтах
                
                for target_date in target_dates:
                    try:
                        image_data = get_wms_image(
                            bbox=bbox_data['bbox'],
                            srs=bbox_data['srs'],
                            date=target_date,
                            max_cloud_cover=max_cloud_cover
                        )
                        
                        # Проверка на черное изображение
                        if len(image_data) == BLACK_IMAGE_SIZE:
                            messages.warning(request, 
                                f"Изображение за {target_date.strftime('%Y-%m-%d')} не содержит данных (черная картинка)")
                            continue
                        
                        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                        filename = f"sentinel_{target_date.strftime('%Y%m%d')}_{timestamp}.jpg"
                        filepath = os.path.join(img_dir, filename)
                        
                        with open(filepath, 'wb') as f:
                            f.write(image_data)
                        
                        images.append({
                            'date': target_date,
                            'filename': filename,
                            'url': os.path.join(settings.MEDIA_URL, 'sentinel_images', filename),
                            'path': filepath
                        })
                        
                    except Exception as e:
                        messages.warning(request, 
                            f"Не удалось загрузить изображение за {target_date.strftime('%Y-%m-%d')}: {str(e)}")
                
                if not images:
                    messages.error(request, "Не удалось загрузить ни одного изображения. Проверьте параметры запроса.")
                    return render(request, 'sentinel/search.html', {'form': form})
                
                return render(request, 'sentinel/results.html', {
                    'images': images,
                    'bbox': bbox_data['bbox'],
                    'start_date': start_date,
                    'end_date': end_date
                })
                
            except Exception as e:
                messages.error(request, f"Произошла ошибка: {str(e)}")
                return render(request, 'sentinel/search.html', {'form': form})
    
    form = SentinelSearchForm()
    return render(request, 'sentinel/search.html', {'form': form})

@login_required
def download_image(request, filename):
    """Безопасная загрузка сохраненных изображений"""
    try:
        img_dir = os.path.join(settings.MEDIA_ROOT, 'sentinel_images')
        filepath = os.path.join(img_dir, filename)
        
        # Валидация пути
        if not os.path.exists(filepath) or not os.path.isfile(filepath):
            raise Http404("Изображение не найдено")
        
        # Проверка расширения файла
        _, ext = os.path.splitext(filename)
        if ext.lower() not in ['.jpg', '.jpeg', '.png']:
            raise Http404("Недопустимый формат файла")
        
        # Определяем Content-Type
        content_type = 'image/jpeg' if ext.lower() in ['.jpg', '.jpeg'] else 'image/png'
        
        response = FileResponse(
            open(filepath, 'rb'),
            content_type=content_type,
            as_attachment=True
        )
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        return response
        
    except PermissionError:
        raise Http404("Ошибка доступа к файлу")
    except Exception as e:
        raise Http404(f"Произошла ошибка при загрузке: {str(e)}")
