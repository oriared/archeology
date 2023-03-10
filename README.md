# Проект 'Артефакт'
---
Написан на Python 3.10.
Использованы библиотеки:
* [Flask](https://github.com/pallets/flask) - микрофреймворк для создания веб-приложений
* Jinja2 - библиотека для рендеринга шаблонов
* [Werkzeug](https://github.com/pallets/werkzeug) - комплексная библиотека веб-приложений WSGI
* [SQLAlchemy](https://github.com/pallets-eco/flask-sqlalchemy) - библиотека для работы с реляционными СУБД с применением технологии ORM
* [Flask-Login](https://github.com/maxcountryman/flask-login) - интеграция системы аутентификации в приложение Flask
* [Flask-Migrate](https://github.com/miguelgrinberg/Flask-Migrate) - обработка миграции базы данных SQLAlchemy для приложений Flask с помощью Alembic
* [Flask-WTF](https://github.com/wtforms/flask-wtf) - интеграция Flask и WTForms
* [Flask-Bootstrap](https://github.com/mbr/flask-bootstrap) - расширение для работы с Bootstrap
* и др.
---
Проект представляет собой WEB-приложение, основная цель которого - популяризация археологии. Это сайт, на котором будут собраны материалы на тему археологии, написанные простым, увлекательным языком. Переработанные научные статьи, описания жизни наших далёких предков, созданные на основе многолетних раскопок, рассказы о вещах, доставшихся нам в наследство. 

![Image](https://raw.githubusercontent.com/oriared/archeology/main/readme_img/001.png)

На данный момент реализованы следующие разделы сайта:
* Главная страница, на которой находится кликабельная карта России 
* Раздел навигации по "времени и пространству". В разделе отображаются только те народы(этносы), которые проживали на территории выбранного региона и с которыми связана хотя бы одна статья в базе данных. Аналогично и с эпохами. Выбрав интересующие регион, этнос, век, и раздел, пользователь увидит список подходящих по параметрам статей.
* Страница просмотра статьи. Отображаются теги, дата публикации, в случае если пользователь является автором данного материала - кнопка "Редактировать"
* Поиск по тегам. Пользователь через форму может выбрать один или несколько тегов и получить набор статей, удовлетворяющих условиям поиска. Далее можно добавлять дополнительные теги или удалять уже выбранные.
* Страница входа для авторов. Предполагается, что свободной регистрации не будет, археологическое сообщество довольно тесное и авторы материала будут привлекаться к наполнению сайта посредством личных приглашений с выдачей пар логин-пароль
* Добавление материала. Авторизованному пользователю будет доступна кнопка "Добавить статью", нажав которую, он перейдёт на страницу с формой для заполнения данных о материале и добавления связей территория-эпоха-этнос. Непосредственно написание текста будет доступно после заполнения данной страницы
* Редактор. Визуальный WYSIWYG редактор Summernote автоматически конвертирует вводимый текст в HTML код с сохранение форматирования текста. Данная страница используется как при создании статьи, так и в случае последующего редактирования.
* Профиль автора со списком статей
---
Для запуска проекта:

1. Git Bash: 
   ```
   $ git clone https://github.com/oriared/archeology.git
   ```
2. CMD:
   ```
   python -m venv venv

   venv\Scripts\activate

   pip install -r requirements.txt

   set FLASK_APP=runner.py
   ```

3. Необходимо создать свою БД и [прописать её URL](https://docs.sqlalchemy.org/en/14/core/engines.html#database-urls) в переменной `SQLALCHEMY_DATABASE_URI` файла example_config.toml. 

4. CMD:
   ```
   flask run
   ```
---
