from flask import render_template, url_for, request, redirect
from app import app, db
from app.models import Age, Ethnos, Region, Section, Tag, Article, TagArticle, Asera
from app.forms import AddArticleForm


@app.route('/')
@app.route('/index')
def index():
    regions = [item.name_region for item in db.session.query(Region).all()]
    return render_template('index.html', title='Археология без воды', regions=regions)


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
    return render_template('article.html', title=article_title, article_title=article_title)


@app.route('/add', methods=['GET', 'POST'])
def add():
    form = AddArticleForm()
    form.section.choices = [(item.id, item.name_section) for item in db.session.query(Section)]
    form.region.choices = [(item.id, item.name_region) for item in db.session.query(Region)]
    form.age.choices = [(item.id, f"{item.name_age} ({item.period})") for item in db.session.query(Age)]
    form.ethnos.choices = [(-1, '---другое---')]\
                          + [(item.id, item.name_ethnos) for item in db.session.query(Ethnos)
                           .order_by(Ethnos.name_ethnos)]
    form.tag.choices = [(-1, '---')]\
                        + [(item.id, item.name_tag) for item in db.session.query(Tag)
                        .order_by(Tag.name_tag)]
    if form.validate_on_submit():
        article = Article(title=form.title.data, text=form.text.data)
        db.session.add(article)
        article_id = db.session.query(Article).filter(Article.title==form.title.data).first().id

        ethnos_id = form.ethnos.data
        if ethnos_id == -1:
            new_ethnos = Ethnos(name_ethnos=form.new_ethnos.data)
            db.session.add(new_ethnos)
            ethnos_id = Ethnos.query.filter(Ethnos.name_ethnos==form.new_ethnos.data).first().id

        for i in form.region.data:
            for j in form.age.data:
                asera = Asera(article_id=article_id,
                              section_id=form.section.data,
                              ethnos_id=ethnos_id,
                              region_id=i,
                              age_id=j)
                db.session.add(asera)
        
        tag_id = form.tag.data
        if form.new_tags.data:
            for item in form.new_tags.data.split(', '):
                new_tag = Tag(name_tag=item)
                db.session.add(new_tag)
                tag_id.append(Tag.query.filter(Tag.name_tag==item).first().id)

        for i in tag_id:
            ta = TagArticle(tag_id=i, article_id=article_id)
            db.session.add(ta)

        db.session.commit()
        return redirect(url_for('region', name_region=Region.query.filter_by(id=form.region.data[0]).first().name_region))

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
        .join(Asera, Ethnos.id==Asera.ethnos_id)
        .join(Region, Asera.region_id==Region.id)
        .join(Age, Asera.age_id==Age.id)
        .filter(Region.name_region==name_region, Age.name_age==name_age)
        .all()]
    else:
        true_ethnoses = [item.name_ethnos for item in 
        db.session.query(Ethnos)
        .join(Asera, Ethnos.id==Asera.ethnos_id)
        .join(Region, Asera.region_id==Region.id)
        .filter(Region.name_region==name_region)
        .all()]

    if name_ethnos:
        true_ages = [item.name_age for item in 
        db.session.query(Age)
        .join(Asera, Age.id==Asera.age_id)
        .join(Region, Asera.region_id==Region.id)
        .join(Ethnos, Asera.ethnos_id==Ethnos.id)
        .filter(Region.name_region==name_region, Ethnos.name_ethnos==name_ethnos)
        .all()]
    else:
        true_ages = [item.name_age for item in 
        db.session.query(Age)
        .join(Asera, Age.id==Asera.age_id)
        .join(Region, Asera.region_id==Region.id)
        .filter(Region.name_region==name_region)
        .all()]
    if name_age and name_ethnos:
        query_sections = [item for item in
        db.session.query(Section)
        .join(Asera, Section.id==Asera.section_id)
        .join(Age, Asera.age_id==Age.id)
        .join(Ethnos, Asera.ethnos_id==Ethnos.id)
        .join(Region, Asera.region_id==Region.id)
        .filter(Region.name_region==name_region, Ethnos.name_ethnos==name_ethnos, Age.name_age==name_age)
        .all()]
        if name_section:
            for item in query_sections:
                if item.name_section==name_section:
                    articles = [i.title for i in item.articles]
                    break
        else:
            sections = [item.name_section for item in query_sections]
    
    return render_template('region.html', 
                           title=name_region, 
                           region=name_region, 
                           age=name_age, 
                           ethnos=name_ethnos,
                           section=name_section,
                           sections=sections,
                           true_ages=true_ages, 
                           true_ethnoses=true_ethnoses,
                           articles=articles
                          )
