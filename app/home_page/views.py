from django.shortcuts import render
from django.core.files.storage import default_storage
from django.contrib import messages
from django.views.generic import ListView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from .forms import ImageUploadForm
from authenticate.models import Users_History

# сделать проверку на авторизацию, если авторизован - базовая страница с моделью, если нет - страница с саламами

def home_page_show(request):
    return render(request, 'home_page/general_page.html') # не авторизован должна начальная страница или с регистром


@login_required
def main_page(request):
    if request.method == 'POST':
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file = form.cleaned_data['original_image'] 
            user_history = form.save(commit= False)
            user_history.user = request.user #изображения уже сохраняются в бд (путь)!
            user_history.save() #дальше будем отправлять на сервер
        else:
            messages.error(request, 'Ошибка при обработке изображения.')
    else:
        form = ImageUploadForm()
    return render(request, 'home_page/home_page.html', {'form': form})


@login_required
def profile(request): # При нажатии на кнопку юзера
    return render(request,  ) # должна быть страница пользователя        
    

@method_decorator(login_required, name='dispatch')
class HistoryListView(ListView):
    model = Users_History
    template_name = 'history_page/history_page.html'  # Указываем шаблон
    context_object_name = 'history_entries'  # Имя переменной в шаблоне


    def get_queryset(self):
        # Возвращаем только записи, связанные с текущим пользователем, будут отображаться сначала новые
        return Users_History.objects.filter(user=self.request.user).order_by('-created_at')