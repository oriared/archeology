from flask import render_template, url_for, flash, request, redirect
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse
from app import app, db
from app.models import (
    Age,
    Ethnos,
    Region,
    Section,
    Tag,
    Article,
    TagArticle,
    Asera,
    Author,
)
from app.forms import AddArticleForm, LoginForm, SelectTagForm
import re


@app.route("/")
@app.route("/index")
def index():
    return render_template("index.html", title="Артефакт")


@app.route("/article/<path:article_title>", methods=["GET", "POST"])
def article(article_title):
    article = Article.query.filter_by(title=article_title).first_or_404()
    author = Author.query.filter_by(id=article.author_id).first_or_404()

    return render_template(
        "article.html", article=article, author=author.name_author
    )


@app.route("/explore", methods=["GET", "POST"])
def explore():
    # Функция представления, возвращающая страницу поиска статей по тегам.
    # Включает форму с возможностью выбора нескольких тегов из списка,
    # теги передаются как аргументы запроса. В результате на странице будут
    # представлены статьи, имеющие все выбранные теги.
    form = SelectTagForm()
    form.tag.choices = [
        item.name_tag for item in Tag.query.order_by(Tag.name_tag)
    ]
    tags = request.args.getlist("tags")
    page = request.args.get("page", 1, type=int)
    # Для возможности удаления уже выбранных тегов из поискового запроса возле
    # каждого тега находится кнопка "удалить", отправляющая запрос с аргументом
    # "deletetag". Проверяем, есть ли такой аргумент и удаляем тег
    if request.args.get("deletetag"):
        tags.remove(request.args.get("deletetag"))
    # При нажатии кнопки "Поиск" выбранные теги добавляются к выбранным ранее
    if form.validate_on_submit():
        tags.extend(form.tag.data)
        return redirect(url_for("explore", tags=list(set(tags))))
    tags.sort()
    if tags:
        articles = (
            db.session.query(Article.title, Article.summary)
            .join(TagArticle, Article.id == TagArticle.article_id)
            .join(Tag, TagArticle.tag_id == Tag.id)
            .filter(Tag.name_tag.in_(tags))
            .group_by(Article.title, Article.summary, Article.created_on)
            .having(db.func.count(Tag.id) == len(tags))
            .order_by(Article.created_on.desc())
            .paginate(
                page=page, per_page=app.config["PER_PAGE"], error_out=False
            )
        )
    else:
        # Если ни одного тега не задано, отображаем все имеющиеся статьи
        articles = Article.query.order_by(Article.created_on.desc()).paginate(
            page=page, per_page=app.config["PER_PAGE"], error_out=False
        )
    next_url = (
        url_for("explore", tags=tags, page=articles.next_num)
        if articles.has_next
        else None
    )
    prev_url = (
        url_for("explore", tags=tags, page=articles.prev_num)
        if articles.has_prev
        else None
    )
    iter_pages = articles.iter_pages(
        left_edge=2, left_current=2, right_current=5, right_edge=2
    )

    return render_template(
        "explore.html",
        title="Поиск",
        tags=tags,
        articles=articles,
        form=form,
        page=page,
        next_url=next_url,
        prev_url=prev_url,
        iter_pages=iter_pages,
    )


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        author = Author.query.filter_by(name_author=username).first()
        if author is None or not author.check_password(form.password.data):
            flash("Неверные имя пользователя или пароль")
            return redirect(url_for("login"))
        login_user(author, remember=form.remember_me.data)
        next_page = request.args.get("next")
        if not next_page or url_parse(next_page).netloc != "":
            next_page = url_for("index")
        return redirect(next_page)

    return render_template("login.html", title="Авторизация", form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("index"))


@app.route("/profile/<username>")
def profile(username):
    page = request.args.get("page", 1, type=int)
    articles = (
        Author.query.filter_by(name_author=username)
        .first()
        .articles.order_by(Article.created_on.desc())
        .paginate(page=page, per_page=app.config["PER_PAGE"], error_out=False)
    )
    next_url = (
        url_for("profile", username=username, page=articles.next_num)
        if articles.has_next
        else None
    )
    prev_url = (
        url_for("profile", username=username, page=articles.prev_num)
        if articles.has_prev
        else None
    )
    iter_pages = articles.iter_pages(
        left_edge=2, left_current=2, right_current=5, right_edge=2
    )

    return render_template(
        "profile.html",
        username=username,
        articles=articles,
        page=page,
        next_url=next_url,
        prev_url=prev_url,
        iter_pages=iter_pages,
    )


@app.route("/add", methods=["GET", "POST"])
@login_required
def add():
    # Функция представления для добавления на сайт нового материала. Доступна
    # только авторизованным авторам. Эта функция является основой для
    # формирования наполнения сайта, помимо добавления статьи она определяет
    # связи в БД между эпохами, территориями и народами (этносами), их
    # населявшими. Редактор для написания непосредственно текста статьи
    # находится в функции представления 'editor'
    form = AddArticleForm()
    form.section.choices = [
        (item.id, item.name_section) for item in Section.query
    ]
    form.region.choices = [
        (item.id, item.name_region)
        for item in Region.query.order_by(Region.id)
    ]
    form.age.choices = [
        (item.id, f"{item.name_age} ({item.period})") for item in Age.query
    ]
    # Для возможности добавления отсутствующих в базе этносов в форму выбора
    # этноса добавляем пункт "другое"
    form.ethnos.choices = [(-1, "--другое--")] + [
        (item.id, item.name_ethnos)
        for item in Ethnos.query.order_by(Ethnos.name_ethnos)
    ]
    # Теги можно выбрать как из существующих, так и добавить новые
    form.tag.choices = [(-1, "---")] + [
        (item.id, item.name_tag) for item in Tag.query.order_by(Tag.name_tag)
    ]

    if form.validate_on_submit():
        article = Article(
            title=form.title.data,
            summary=form.summary.data,
            author_id=current_user.id,
        )
        db.session.add(article)
        article_id = Article.query.filter_by(title=form.title.data).first().id

        ethnos_id = form.ethnos.data
        if ethnos_id == -1:
            # Если этнос не выбран из существующих, значит автор добавил новый,
            # берём его из поля "new_ethnos" и добавляем в БД
            new_ethnos = Ethnos(name_ethnos=form.new_ethnos.data)
            db.session.add(new_ethnos)
            ethnos_id = (
                Ethnos.query.filter_by(name_ethnos=form.new_ethnos.data)
                .first()
                .id
            )
        # Устанавливаем связи в БД между территориями, эпохами, народами и
        # относящимися к ним статьями через промежуточную таблицу "asera"
        for i in form.region.data:
            for j in form.age.data:
                asera = Asera(
                    article_id=article_id,
                    ethnos_id=ethnos_id,
                    section_id=form.section.data,
                    region_id=i,
                    age_id=j,
                )

                db.session.add(asera)
        tag_id = form.tag.data
        if form.new_tags.data:
            for item in form.new_tags.data.split(", "):
                new_tag = Tag(name_tag=item)
                db.session.add(new_tag)
                tag_id.append(Tag.query.filter_by(name_tag=item).first().id)
        # Определяем связи между статьёй и тегами через промежуточную таблицу
        for i in tag_id:
            ta = TagArticle(tag_id=i, article_id=article_id)
            db.session.add(ta)
        db.session.commit()
        return redirect(url_for("editor", article_title=form.title.data))

    return render_template("add.html", title="Новая статья", form=form)


@app.route("/article/<path:article_title>/editor", methods=["GET", "POST"])
@login_required
def editor(article_title):
    # Редактор текста, используется как для добавления материала, так и для
    # его редактирования
    article = Article.query.filter_by(title=article_title).first_or_404()
    author = Author.query.filter_by(id=article.author_id).first_or_404()
    if current_user != author:
        flash("Ошибка доступа!")
        return redirect(url_for("index"))
    if request.method == "POST":
        article.text = request.form.get("editordata")
        # Если автор не добавил краткое описание материала, вместо него
        # используются первые предложения из текста статьи
        if not article.summary:
            cleantext = re.sub(
                re.compile(
                    "<.*?>|&([a-z0-9]+|#[0-9]{1,6}|#x\
                [0-9a-f]{1,6});"
                ),
                "",
                article.text,
            )[:499]
            article.summary = cleantext[: cleantext.rfind(" ")]
        db.session.add(article)
        db.session.commit()
        flash("Сохранено")
        return redirect(url_for("article", article_title=article_title))
    return render_template(
        "article.html",
        title=article_title + " - редактирование",
        article=article,
        author=author.name_author,
        mode="edit",
    )


@app.route("/region/<name_region>")
def region(name_region):
    # Страница для выбора эпох, народов и территорий. В настоящее время
    # реализована так, что пользователь будет видеть только те пункты,
    # по которым в БД есть хотя бы один материал(статья)
    name_age = request.args.get("age")
    name_ethnos = request.args.get("ethnos")
    name_section = request.args.get("section")
    sections = None
    # Если уже выбраны народ, эпоха и раздел, функция выдаст список статей,
    # отвечающих заданным условиям
    if name_age and name_ethnos and name_section:
        page = request.args.get("page", 1, type=int)
        articles = (
            Article.query.join(Asera, Article.id == Asera.article_id)
            .join(Age, Asera.age_id == Age.id)
            .join(Ethnos, Asera.ethnos_id == Ethnos.id)
            .join(Region, Asera.region_id == Region.id)
            .join(Section, Asera.section_id == Section.id)
            .filter(
                db.and_(
                    Region.name_region == name_region,
                    Ethnos.name_ethnos == name_ethnos,
                    Age.name_age == name_age,
                    Section.name_section == name_section,
                )
            )
            .order_by(Article.created_on.desc())
            .paginate(
                page=page, per_page=app.config["PER_PAGE"], error_out=False
            )
        )
        next_url = (
            url_for(
                "region",
                name_region=name_region,
                age=name_age,
                ethnos=name_ethnos,
                section=name_section,
                page=articles.next_num,
            )
            if articles.has_next
            else None
        )
        prev_url = (
            url_for(
                "region",
                name_region=name_region,
                age=name_age,
                ethnos=name_ethnos,
                section=name_section,
                page=articles.prev_num,
            )
            if articles.has_prev
            else None
        )
        iter_pages = articles.iter_pages(
            left_edge=2, left_current=2, right_current=4, right_edge=2
        )

        return render_template(
            "region.html",
            title=name_region,
            region=name_region,
            age=name_age,
            ethnos=name_ethnos,
            section=name_section,
            articles=articles,
            page=page,
            next_url=next_url,
            prev_url=prev_url,
            iter_pages=iter_pages,
        )
    # Если не выбран раздел, выдаётся список разделов
    elif name_age and name_ethnos:
        sections = [
            item.name_section
            for item in Section.query.join(
                Asera, Section.id == Asera.section_id
            )
            .join(Age, Asera.age_id == Age.id)
            .join(Ethnos, Asera.ethnos_id == Ethnos.id)
            .join(Region, Asera.region_id == Region.id)
            .filter(
                db.and_(
                    Region.name_region == name_region,
                    Ethnos.name_ethnos == name_ethnos,
                    Age.name_age == name_age,
                )
            )
            .all()
        ]

        return render_template(
            "region.html",
            title=name_region,
            region=name_region,
            age=name_age,
            ethnos=name_ethnos,
            sections=sections,
        )
    # Если не выбран народ или эпоха, выдаются списки народов и эпох, между
    # которыми установлены связи в БД
    else:
        if name_age:
            true_ethnoses = [
                item.name_ethnos
                for item in db.session.query(Ethnos)
                .join(Asera, Ethnos.id == Asera.ethnos_id)
                .join(Region, Asera.region_id == Region.id)
                .join(Age, Asera.age_id == Age.id)
                .filter(
                    Region.name_region == name_region, Age.name_age == name_age
                )
                .all()
            ]
        else:
            true_ethnoses = [
                item.name_ethnos
                for item in db.session.query(Ethnos)
                .join(Asera, Ethnos.id == Asera.ethnos_id)
                .join(Region, Asera.region_id == Region.id)
                .filter(Region.name_region == name_region)
                .all()
            ]

        if name_ethnos:
            true_ages = [
                item.name_age
                for item in db.session.query(Age)
                .join(Asera, Age.id == Asera.age_id)
                .join(Region, Asera.region_id == Region.id)
                .join(Ethnos, Asera.ethnos_id == Ethnos.id)
                .filter(
                    Region.name_region == name_region,
                    Ethnos.name_ethnos == name_ethnos,
                )
                .all()
            ]
        else:
            true_ages = [
                item.name_age
                for item in db.session.query(Age)
                .join(Asera, Age.id == Asera.age_id)
                .join(Region, Asera.region_id == Region.id)
                .filter(Region.name_region == name_region)
                .all()
            ]

    return render_template(
        "region.html",
        title=name_region,
        region=name_region,
        age=name_age,
        ethnos=name_ethnos,
        true_ages=true_ages,
        true_ethnoses=true_ethnoses,
    )


@app.route("/about")
def about():
    return render_template("about.html", title="О проекте")


@app.route("/feedback")
def feedback():
    return render_template("feedback.html", title="Обратная связь")
