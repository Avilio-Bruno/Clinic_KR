# Подключаем объект приложения Flask из __init__.py
from labapp import app
# Подключаем библиотеку для "рендеринга" html-шаблонов из папки templates
from flask import render_template, make_response, request, jsonify
from labapp.processor.dataprocessor_service import DataProcessorService
import labapp.webservice as webservice  # подключаем модуль с реализацией бизнес-логики обработки запросов
import os
"""
    Модуль регистрации обработчиков маршрутов, т.е. здесь реализуется обработка запросов
    при переходе пользователя на определенные адреса веб-приложения
"""

marked_files = []
files = []


@app.route('/', methods=['GET'])
@app.route('/index', methods=['GET'])
def index():
    global files, marked_files
    files += [file for file in os.listdir('data') if
              ((os.path.isfile(os.path.join('data', file))) and not (file in files))]
    for file in files:
        if file in marked_files:
            continue
        marked_files.append(file)
        service = DataProcessorService(datasource="data/" + file, db_connection_url="sqlite:///test.db")
        service.run_service()
    # Обработка запроса к индексной странице
    # Пример вызова метода с выборкой данных из БД и вставка полученных данных в html-шаблон
    processed_files = webservice.get_processed_data()
    # "рендеринг" (т.е. вставка динамически изменяемых данных) в шаблон index.html и возвращение готовой страницы
    return render_template('index.html',
                           title='Internet Users',
                           page_name='HOME',
                           navmenu=webservice.navmenu,
                           processed_files=processed_files)


@app.route('/contact', methods=['GET'])
def contact():
    """ Обработка запроса к странице contact.html """
    return render_template('contact.html',
                           title='contact',
                           page_name='CONTACT US',
                           navmenu=webservice.navmenu)


@app.route('/about_us', methods=['GET'])
def about_us():
    """ Обработка запроса к странице contact.html """
    return render_template('about_us.html',
                           title='About Us',
                           page_name='About Us',
                           navmenu=webservice.navmenu)


@app.route('/api/contactrequest', methods=['POST'])
def post_contact():
    """ Пример обработки POST-запроса для демонстрации подхода AJAX (см. formsend.js и ЛР№5 АВСиКС) """
    request_data = request.json  # получаeм json-данные из запроса
    # Если в запросе нет данных или неверный заголовок запроса (т.е. нет 'application/json'),
    # или в этом объекте, например, не заполнено обязательное поле 'firstname'
    if not request_data or request_data['firstname'] == '':
        # возвращаем стандартный код 400 HTTP-протокола (неверный запрос)
        return bad_request()
    # Иначе отправляем json-ответ с сообщением об успешном получении запроса
    else:
        msg = request_data['firstname'] + ", ваш запрос получен !"
        return jsonify({'message': msg})


@app.route('/notfound', methods=['GET'])
def not_found_html():
    """ Возврат html-страницы с кодом 404 (Не найдено) """
    return render_template('404.html', title='404', err={'error': 'Not found', 'code': 404})


@app.route('/#', methods=['GET'])
def about():
    return render_template('404.html', title='404', err={'error': 'Not found', 'code': 404})


def bad_request():
    """ Формирование json-ответа с ошибкой 400 протокола HTTP (Неверный запрос) """
    return make_response(jsonify({'message': 'Bad request !'}), 400)
