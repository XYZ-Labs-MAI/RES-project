Тест модельки работает (иногда может лагать)

ПРОЧЕКАТЬ API вывод

пример результата
0: 672x1024 1465.4ms
Speed: 13.1ms preprocess, 1465.4ms inference, 4.5ms postprocess per image at shape (1, 3, 672, 1024)
{'image_id': 'ffe8f128-1b29-493a-b7fe-ba90e47b51ba', 'result': ('ffe8f128-1b29-493a-b7fe-ba90e47b51ba', {'height': 742, 'objects': [{'confidence': 0.8027605414390564, 'name': 'plane', 'xmax': 96, 'xmin': 638, 'ymax': 66, 'ymin': 365}, {'confidence': 0.5954828858375549, 'name': 'plane', 'xmax': 73, 'xmin': 610, 'ymax': 49, 'ymin': 415}, {'confidence': 0.7371938824653625, 'name': 'plane', 'xmax': 91, 'xmin': 569, 'ymax': 60, 'ymin': 476}, {'confidence': 2.073349714279175, 'name': 'plane', 'xmax': 76, 'xmin': 702, 'ymax': 66, 'ymin': 525}], 'width': 1180})}


формат:
- image_id - идентификатор
- result-list-dict - dict для каждого найденного класса
    - confidence - уверенность
    - name - класс
    - xmax, xmin, ymax, ymin - корды бокса
