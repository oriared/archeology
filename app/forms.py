from flask_wtf import FlaskForm
from wtforms import ValidationError, StringField, PasswordField, \
    BooleanField, SubmitField, TextAreaField, SelectField, SelectMultipleField
from wtforms.validators import DataRequired, Length
from app.models import Article


class LoginForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить')
    submit = SubmitField('Войти')


class AddArticleForm(FlaskForm):
    title = StringField('Заголовок:', validators=[
        DataRequired(message='Поле не может быть пустым'),
        Length(min=3, max=70,
               message='Заголовок должен быть длиной от 3 до 70 символов')])
    text = TextAreaField('Текст:', validators=[
        DataRequired(message='Поле не может быть пустым'),
        Length(min=20, max=10000,
               message='Статья должен быть длиной от 20 до 10000 символов')])
    region = SelectMultipleField('Регионы (современные):', coerce=int, \
        validators=[DataRequired(message='Необходимо выбрать минимум \
        один регион')])
    age = SelectMultipleField('Период:', coerce=int, validators=[
        DataRequired(message='Необходимо выбрать минимум один период')])
    ethnos = SelectField('Этнос:', coerce=int)
    new_ethnos = StringField('Добавить новый этнос:', validators=[
        Length(max=30, message='Название этноса слишком длинное')])
    section = SelectField('Раздел:')
    tag = SelectMultipleField('Теги:', coerce=int)
    new_tags = StringField('Добавить новые теги:')
    submit = SubmitField('Отправить')

    def validate_title(self, title):
        title = Article.query.filter_by(title=title.data).first()
        if title is not None:
            raise ValidationError('Статья с таким названием уже существует')

    def validate_ethnos(self, ethnos):
        if ethnos.data == -1 and not self.new_ethnos.data:
            raise ValidationError('Выберите этнос из списка или добавьте \
                новый')

    def validate_new_ethnos(self, new_ethnos):
        if self.ethnos.data != -1 and new_ethnos == '':
            raise ValidationError('Этнос уже выбран из существующих')


class SelectTagForm(FlaskForm):
    tag = SelectMultipleField('Добавить теги в поиск:')
    submit = SubmitField('Поиск')
