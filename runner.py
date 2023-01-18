from app import app, db

# Оболочка для работы с базой данных из консоли
@app.shell_context_processor
def make_shell_context():
    return {'db': db,
            'Author': Author,
            'Article': Article,
            'Tag': Tag,
            'Section': Section,
            'Subscriber': Subscriber,
            'Region': Region,
            'Ethnos': Ethnos,
            'Age': Age,
            'Asera': Asera,
            'TagArticle': TagArticle,
            'SubscriberAuthor': SubscriberAuthor,
            'SubscriberTag': SubscriberTag
            }
