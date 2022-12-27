from flask import render_template, url_for, flash, request, redirect
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse
from app import app, db
from app.models import Age, Ethnos, Region, Section, Tag, Article, \
    TagArticle, Asera, Author
from app.forms import AddArticleForm, LoginForm, SelectTagForm


@app.route('/')
@app.route('/index')
def index():
    regions = [item.name_region for item in db.session.query(Region).all()]
    return render_template('index.html', title='Археология без воды', 
        regions=regions)


@app.route('/about')
def about():
    return render_template('about.html', title='О проекте')


@app.route('/feedback')
def feedback():
    return render_template('feedback.html', title='Обратная связь')


@app.route('/subscribe')
def subscribe():
    return render_template('subscribe.html', title='Подписка')


@app.route('/article/<article_title>')
def article(article_title):
    article = Article.query.filter(Article.title == article_title).first()
    text = article.text
    created_on = article.created_on
    author = Author.query.filter_by(id=article.author_id).first_or_404() \
        .name_author
    tags = [item.name_tag for item in Tag.query
            .join(TagArticle, Tag.id == TagArticle.tag_id)
            .join(Article, TagArticle.article_id == Article.id)
            .filter(Article.title == article_title).all()]
    
    return render_template('article.html', 
                           title=article_title, 
                           article_title=article_title, 
                           text=text, 
                           created_on=created_on, 
                           author=author, 
                           tags=tags)


@app.route('/explore', methods=['GET', 'POST'])
def explore():
    form = SelectTagForm()
    form.tag.choices = [item.name_tag for item in db.session.query(Tag) \
        .order_by(Tag.name_tag)]
    tags = request.args.getlist('tags')
    page = request.args.get('page', 1, type=int)
    if form.validate_on_submit():
            tags.extend(form.tag.data)
            return redirect(url_for('explore', tags=list(set(tags))))
    if tags:    
        if request.args.get('deltag'):
            tags.remove(request.args.get('deltag'))
        articles = Article.query \
                   .join(TagArticle, Article.id == TagArticle.article_id) \
                   .join(Tag, TagArticle.tag_id == Tag.id) \
                   .filter(Tag.name_tag.in_(tags)) \
                   .order_by(Article.created_on.desc()) \
                   .paginate(page=page, per_page=app.config['PER_PAGE'],
                    error_out=False)
    else:
        articles = Article.query.order_by(Article.created_on.desc()) \
            .paginate(page=page, per_page=app.config['PER_PAGE'], 
                error_out=False)
    next_url = url_for('explore', tags=tags, page=articles.next_num) \
        if articles.has_next else None
    prev_url = url_for('explore', tags=tags, page=articles.prev_num) \
        if articles.has_prev else None
    iter_pages = articles.iter_pages(left_edge=2, left_current=2, 
        right_current=5, right_edge=2)

    return render_template('explore.html', title='Поиск', tags=tags,
        articles=articles.items, form=form, page=page, next_url=next_url, 
        prev_url=prev_url, iter_pages=iter_pages)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        author = Author.query.filter(Author.name_author == 
            form.username.data).first()
        if author is None or not author.check_password(form.password.data):
            flash('Неверные имя пользователя или пароль')
            return redirect(url_for('login'))
        login_user(author, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)

    return render_template('login.html', title='Авторизация', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/profile/<username>')
def profile(username):
    page = request.args.get('page', 1, type=int)
    articles = Author.query.filter(Author.name_author == username).first(). \
        articles.paginate(page=page, per_page=app.config['PER_PAGE'], 
            error_out=False)
    next_url = url_for('profile', username=username, page=articles.next_num) \
        if articles.has_next else None
    prev_url = url_for('profile', username=username, page=articles.prev_num) \
        if articles.has_prev else None
    iter_pages = articles.iter_pages(left_edge=2, left_current=2, 
        right_current=5, right_edge=2)

    return render_template('profile.html', username=username, 
        articles=articles.items, page=page, next_url=next_url, 
        prev_url=prev_url, iter_pages=iter_pages)


@app.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    form = AddArticleForm()
    form.section.choices = [(item.id, item.name_section) for item in \
        db.session.query(Section)]
    form.region.choices = [(item.id, item.name_region) for item in \
        db.session.query(Region)]
    form.age.choices = [(item.id, f"{item.name_age} ({item.period})") for \
        item in db.session.query(Age)]
    form.ethnos.choices = [(-1, '---другое---')] \
        + [(item.id, item.name_ethnos) for item in db.session.query(Ethnos) \
        .order_by(Ethnos.name_ethnos)]
    form.tag.choices = [(-1, '---')] + [(item.id, item.name_tag) for item in \
        db.session.query(Tag).order_by(Tag.name_tag)]
    
    if form.validate_on_submit():
        article = Article(title=form.title.data, text=form.text.data, 
            author_id=current_user.id)
        db.session.add(article)
        article_id = db.session.query(Article).filter(Article.title == 
            form.title.data).first().id

        ethnos_id = form.ethnos.data
        if ethnos_id == -1:
            new_ethnos = Ethnos(name_ethnos=form.new_ethnos.data)
            db.session.add(new_ethnos)
            ethnos_id = Ethnos.query.filter(Ethnos.name_ethnos == 
                form.new_ethnos.data).first().id

        for i in form.region.data:
            for j in form.age.data:
                asera = Asera(article_id=article_id, 
                    section_id=form.section.data, ethnos_id=ethnos_id,
                    region_id=i, age_id=j)
                db.session.add(asera)

        tag_id = form.tag.data
        if form.new_tags.data:
            for item in form.new_tags.data.split(', '):
                new_tag = Tag(name_tag=item)
                db.session.add(new_tag)
                tag_id.append(Tag.query.filter(Tag.name_tag == 
                    item).first().id)

        for i in tag_id:
            ta = TagArticle(tag_id=i, article_id=article_id)
            db.session.add(ta)

        db.session.commit()
        return redirect(
            url_for('region', name_region=Region.query.filter_by(id=form.
                region.data[0]).first().name_region))

    return render_template('add.html', title='Добавить статью', form=form)


@app.route('/region/<name_region>')
def region(name_region):
    name_age = request.args.get('age')
    name_ethnos = request.args.get('ethnos')
    name_section = request.args.get('section')
    sections = None
    articles = None

    if name_age:
        true_ethnoses = [item.name_ethnos for item in
                         db.session.query(Ethnos)
                         .join(Asera, Ethnos.id == Asera.ethnos_id)
                         .join(Region, Asera.region_id == Region.id)
                         .join(Age, Asera.age_id == Age.id)
                         .filter(Region.name_region == name_region, 
                             Age.name_age == name_age)
                         .all()]
    else:
        true_ethnoses = [item.name_ethnos for item in
                         db.session.query(Ethnos)
                         .join(Asera, Ethnos.id == Asera.ethnos_id)
                         .join(Region, Asera.region_id == Region.id)
                         .filter(Region.name_region == name_region)
                         .all()]

    if name_ethnos:
        true_ages = [item.name_age for item in
                     db.session.query(Age)
                     .join(Asera, Age.id == Asera.age_id)
                     .join(Region, Asera.region_id == Region.id)
                     .join(Ethnos, Asera.ethnos_id == Ethnos.id)
                     .filter(Region.name_region == name_region, 
                         Ethnos.name_ethnos == name_ethnos)
                     .all()]
    else:
        true_ages = [item.name_age for item in
                     db.session.query(Age)
                         .join(Asera, Age.id == Asera.age_id)
                         .join(Region, Asera.region_id == Region.id)
                         .filter(Region.name_region == name_region)
                         .all()]
    if name_age and name_ethnos:
        query_sections = [item for item in
                          db.session.query(Section)
                          .join(Asera, Section.id == Asera.section_id)
                          .join(Age, Asera.age_id == Age.id)
                          .join(Ethnos, Asera.ethnos_id == Ethnos.id)
                          .join(Region, Asera.region_id == Region.id)
                          .filter(Region.name_region == name_region, 
                              Ethnos.name_ethnos == name_ethnos,
                              Age.name_age == name_age)
                          .all()]
        if name_section:
            for item in query_sections:
                if item.name_section == name_section:
                    articles = [i.title for i in item.articles]
                    break
        else:
            sections = [item.name_section for item in query_sections]

    return render_template('region.html', title=name_region, 
        region=name_region, age=name_age, ethnos=name_ethnos,
        section=name_section, sections=sections, true_ages=true_ages,
        true_ethnoses=true_ethnoses, articles=articles)
