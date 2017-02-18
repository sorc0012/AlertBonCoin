from app import db

class Search(db.Model):

    __tablename__ = 'search'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True, unique=True)
    url = db.Column(db.String(1024), index=True, unique=True)
    email = db.Column(db.String(120))
    price_min = db.Column(db.Integer)
    price_max = db.Column(db.Integer)
    def __repr__(self):
        return '<Recherche %r>' % self.name


class Results(db.Model):

    __tablename__ = 'results'

    id = db.Column(db.Integer, primary_key=True)
    id_search = db.Column(db.Integer, db.ForeignKey('search.id'))
    url = db.Column(db.String(250))
    img_url = db.Column(db.String(250))
    lbc_id = db.Column(db.Integer, unique=True)
    title = db.Column(db.String(100))
    price = db.Column(db.Integer)
    date = db.Column(db.Date)

    def __repr__(self):
        return '<Resultat %r>' % self.title