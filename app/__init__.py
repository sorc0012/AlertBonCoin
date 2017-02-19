# Import flask and template operators
from flask import Flask, render_template, redirect, request, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
# Import SQLAlchemy
# from flask.ext.sqlalchemy import SQLAlchemy

# Define the WSGI application object
app = Flask(__name__)

# Define the database object which is imported
# by modules and controllers
db = SQLAlchemy(app)
from app import models
from app.static.utils import Utils

# Configurations
app.config.from_object('config')

PARAM_AUTOUPDATE = "config_autoupdate"

# Sample HTTP error handling
@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404


@app.route('/')
def index():
    search_list = db.session.query(models.Search.name)
    return render_template('index.html', navlist=search_list, search=None)


@app.route('/save_search', methods=['POST'], defaults={'path': ''})
@app.route('/<path:path>/save_search', methods=['POST'])
def save_search(path):
    if request.method == 'POST':
        i_url = request.form['url']
        i_title = request.form['name']
        i_email = request.form['email']
        i_prix_min = request.form['prix_min']
        i_prix_max = request.form['prix_max']
        i_title.replace("/", "|")
        search = models.Search(url=i_url, name=i_title, email=i_email, price_min=i_prix_min, price_max=i_prix_max)
        if models.Search.query.filter_by(url=i_url).count():
            search = models.Search.query.filter_by(url=i_url).first()
            search.name = i_title
            search.email = i_email
            search.price_min = i_prix_min
            search.price_max = i_prix_max
        else:
            db.session.add(search)
        db.session.commit()
        return redirect('/')
    return render_template('index.html')


@app.route('/delete/<name>')
@app.route('/<path:path>/delete/<name>')
def delete(name, path=''    ):
    print('suppression: ', name)
    search = models.Search.query.filter_by(name=name).first()
    models.Results.query.filter_by(id_search=search.id).delete()
    models.Search.query.filter_by(id=search.id).delete()
    db.session.commit()
    return render_template('index.html')


@app.route('/result/<string:name>')
def result(name):
    if name:
        print("results for %s" % name)
    search_list = db.session.query(models.Search.name)
    results_list = models.Results.query.join(models.Search, models.Search.id == models.Results.id_search) \
        .filter(models.Search.name == name).order_by(models.Results.date.desc()).all()
    search = models.Search.query.filter_by(name=name).first()
    print(search)
    return render_template('index.html', navlist=search_list, result_list=results_list, name=name, search=search)


@app.route('/result/<string:name>/update')
def update(name):
    # results = models.Results.query.join(models.Search, models.Search.id == models.Results.id_search)\
    #     .filter(models.Search.name == name).all()
    search = models.Search.query.filter_by(name=name).first()
    Utils.update_result_url(db.session, i_search_name=search.name, i_url=search.url, i_id_search=search.id, i_max_price=search.price_max, i_min_price= \
                            search.price_min)
    return redirect(url_for('result', name=name))


@app.route('/result/<string:name>/delete')
def delete_results(name):
    search = models.Search.query.filter_by(name=name).first()
    if search.id:
        models.Results.query.filter_by(id_search=search.id).delete()
        db.session.commit()
    return redirect(url_for('result', name=name))


@app.route('/setConfig', methods=['POST'])
def update_config():
    if request.method == 'POST':
        config_old = Utils.getConfig_from_file()
        config_new = request.get_json()
        try:
            if config_old[PARAM_AUTOUPDATE] == False and config_new[PARAM_AUTOUPDATE] == True:
                Utils.add_job()
            elif config_old[PARAM_AUTOUPDATE] == True and config_new[PARAM_AUTOUPDATE] == False:
                Utils.delete_job()
        except:
            print("Error setting autoupdate to %s" % (str(config_new[PARAM_AUTOUPDATE])))
        Utils.save_config_file(config_new)
    return ''

@app.route('/getConfig', methods=['GET'])
def get_config():
    if request.method == 'GET':
        config = Utils.getConfig_from_file()
        print(config)
        return jsonify(config)