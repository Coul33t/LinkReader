from flask import Flask, request, render_template, redirect, url_for, session
import uuid
import os
import sqlite3
from passlib.hash import pbkdf2_sha256

import pdb

from funcs import LinkReader

from constants import SECRET_KEY
from constants import DATABASE

app = Flask(__name__)
app.secret_key = SECRET_KEY
l_r = LinkReader()

def import_all_links(path):
    l_r.import_links(path + '/likes.csv')
    l_r.import_links(path + '/favorites.csv')



def init_db():
    con = sqlite3.connect(DATABASE)
    con.execute('CREATE TABLE IF NOT EXISTS accounts (login TEXT, password TEXT, uuid TEXT)')
    con.commit()
    con.close()



@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'GET':
        return render_template('upload.html', sentence='Please upload at least one valid CSV file.')

    elif request.method =='POST':
        if request.files:
            
            if not os.path.exists('./uploads/' + session['uuid']):
                os.makedirs('./uploads/' + session['uuid'])

            for file_name in request.files:
                if request.files[file_name].filename[-4:] == '.csv':
                    request.files[file_name].save('./uploads/' + session['uuid'] + '/' + request.files[file_name].filename)
                    l_r.import_links('./uploads/'+ session['uuid'] + '/' + request.files[file_name].filename)

            return redirect(url_for('index'))

        else:
            return render_template('upload.html', sentence='Please upload at least one valid CSV file.')


@app.route('/connection', methods=['GET', 'POST'])
def connection():
    if request.method == 'GET':
        return render_template('connection.html')

    elif request.method == 'POST':

        con =  sqlite3.connect(DATABASE)
        cursor = con.cursor()
        cursor.execute("SELECT password, uuid, login FROM accounts WHERE login=?", (request.form['id_login'],))
        response = cursor.fetchone()
        con.close()

        if response and pbkdf2_sha256.verify(request.form['pass_login'], response[0]):
            session['uuid'] = response[1]
            session['id'] = response[2]
            if os.path.exists('./uploads/'+ session['uuid']):
                import_all_links('./uploads/'+ session['uuid'])
                return redirect(url_for('index'))
            else:
                return redirect(url_for('upload'))

        else:
            return render_template('connection.html', error_message='Error: wrong login and/or password.')


@app.route('/create_account', methods=['POST'])
def create_account():
    name = request.form['id_registration']
    password = request.form['pass_registration']
    password_v = request.form['pass_validation_registration']

    if not password == password_v:
        return render_template('connection.html', error_message='Password fields do not match.')

    con = sqlite3.connect(DATABASE)
    cursor = con.cursor()
    new_uuid = str(uuid.uuid4())
    cursor.execute("INSERT INTO accounts (login,password,uuid) VALUES (?,?,?)",(name, pbkdf2_sha256.hash(password), new_uuid))
    con.commit()
    con.close()

    session['uuid'] = new_uuid

    return redirect(url_for('upload'))





@app.route('/index')
def index():
    if 'uuid' in session:
        import_all_links('./uploads/'+ session['uuid'])
        return render_template('display.html', title=f'Here is your stuff', note=f'Welcome back, {session["id"]}', links_list=l_r.get_random_link(50))

    else:
        return redirect(url_for('connection'))

@app.route('/likes')
@app.route('/likes/page/<int:num_page>')
def see_likes(num_page = 1):
    if not l_r.has_links():
        if 'uuid' in session:
            import_all_links('./uploads/'+ session['uuid'])
        else:
            return redirect(url_for('connection'))

    return render_template('display.html', title='Here are your likes', links_list=l_r.get_random_link(50, 'likes'))

@app.route('/favs')
@app.route('/favs/page/<int:num_page>') 
def see_favs(num_page = 1):
    if not l_r.has_links():
        if 'uuid' in session:
            import_all_links('./uploads/'+ session['uuid'])
        else:
            return redirect(url_for('connection'))
            
    return render_template('display.html', title='Here are your favs', links_list=l_r.get_random_link(50, 'favs'))

@app.route('/soloview')
def solo_view():
    if 'uuid' in session:
        import_all_links('./uploads/'+ session['uuid'])
    else:
        return redirect(url_for('connection'))

    return render_template('display.html', title='Russian Roulette', links_list=l_r.get_random_link(1), solo=True) 

@app.route('/logout')
def logout():
    session.pop('uuid')
    session.pop('id')
    return redirect(url_for('index'))

@app.errorhandler(401)
@app.errorhandler(404)
@app.errorhandler(500)
def page_not_found(error):
    return f'Woops... There was a problem processing your request ({error.code}).', error.code


if __name__ == '__main__':
    init_db()
    app.config['PERMANENT_SESSION_LIFETIME'] = 3600*24 # la session dure 24 heure
    app.run(debug=True)
