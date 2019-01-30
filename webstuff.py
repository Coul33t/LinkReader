from flask import Flask, request, render_template, redirect, url_for, session
from funcs import LinkReader
import uuid
import os

import pdb

from secret_key import SECRET_KEY

app = Flask(__name__)
app.secret_key = SECRET_KEY
l_r = LinkReader()

def import_all_links(path):
    l_r.import_links(path + '/likes.csv')
    l_r.import_links(path + '/favorites.csv')

@app.route('/loading', methods=['GET', 'POST'])
def loading():
    if request.method == 'GET':
        return render_template('form.html', sentence='Please upload your likes and favorites CSV files, or enter your ID.')
    elif request.method == 'POST':
        
        if request.files:
            generated_id = str(uuid.uuid4())
            
            if not os.path.exists(generated_id):
                os.makedirs('./uploads/' + generated_id)

            for file_name in request.files:
                if request.files[file_name].filename[-4:] == '.csv':
                    request.files[file_name].save('./uploads/' + generated_id + '/' + request.files[file_name].filename)
                    l_r.import_links('./uploads/'+ generated_id + '/' + request.files[file_name].filename)
            
            session['id'] = generated_id
            return redirect(url_for('index'))

        else:
            import_all_links('./uploads/'+ session['id'])
            return redirect(url_for('index'))


@app.route('/index')
def index():
    if 'id' in session:
        import_all_links('./uploads/'+ session['id'])
        return render_template('display.html', title=f'Here is your stuff', note=f'Welcome back, {session["id"]}', links_list=l_r.get_random_link(50))

    else:
        return redirect(url_for('loading'))

@app.route('/likes')
@app.route('/likes/page/<int:num_page>')
def see_likes(num_page = 1):
    if not l_r.has_links():
        if 'id' in session:
            import_all_links('./uploads/'+ session['id'])
        else:
            return redirect(url_for('loading'))

    return render_template('display.html', title='Here are your likes', links_list=l_r.get_random_link(50, 'likes'))

@app.route('/favs')
@app.route('/favs/page/<int:num_page>') 
def see_favs(num_page = 1):
    if not l_r.has_links():
        if 'id' in session:
            import_all_links('./uploads/'+ session['id'])
        else:
            return redirect(url_for('loading'))
            
    return render_template('display.html', title='Here are your favs', links_list=l_r.get_random_link(50, 'favs'))

@app.route('/soloview')
def solo_view():
    if 'id' in session:
        import_all_links('./uploads/'+ session['id'])
    else:
        return redirect(url_for('loading'))

    return render_template('display.html', title='Russian Roulette', links_list=l_r.get_random_link(1)) 

@app.route('/logout')
def logout():
    session.pop('id')
    return redirect(url_for('index'))

@app.errorhandler(401)
@app.errorhandler(404)
@app.errorhandler(500)
def page_not_found(error):
    return f'Woops... There was a problem processing your request ({error.code}).', error.code


if __name__ == '__main__':
    app.config['PERMANENT_SESSION_LIFETIME'] = 3600*24 # la session dure 24 heure
    app.run(debug=True)
