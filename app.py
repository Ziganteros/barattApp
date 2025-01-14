from flask import Flask, render_template, redirect, url_for, request, flash, session
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from pymongo import MongoClient
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
import base64
from datetime import datetime
#from config import dbUser, dbPass
import os

dbUser = os.getenv("DB_USER")
dbPass = os.getenv("DB_PASS")

app = Flask(__name__)

# Configurazione MongoDB
client = MongoClient(f"mongodb+srv://{dbUser}:{dbPass}@cluster0.hr5ue.mongodb.net/")
db = client.barattApp_DB
#default_user = ObjectId("67586e6e9056b15e364df4e9") # philip pino
#default_user = ObjectId("67586f029056b15e364df4f8") # lallero lara
#default_user = ObjectId("67586f479056b15e364df4ff") # de renzi renzo
#default_user = ObjectId("67586fa59056b15e364df504") # bingo bongo

# Configurazione Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Modello utente per Flask-Login
class User(UserMixin):
    def __init__(self, user_id, name, email):
        self.id = user_id
        self.name = name
        self.email = email


# Registrazione dell'utente
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        
        # Controlla se l'utente esiste già
        existing_user = db.Users.find_one({"email": email})
        if existing_user:
            flash('Email già registrata. Prova ad accedere.', 'danger')
            return redirect(url_for('register'))
        
        # Genera l'hash della password durante la registrazione
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

        # Crea un nuovo utente
        new_user = {
            "name": name,
            "email": email,
            "password": hashed_password,
            "products_offered": [],
            "products_wanted": []
        }
        db.Users.insert_one(new_user)
        flash('Registrazione completata con successo! Ora puoi accedere.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

# Funzione per caricare l'utente
@login_manager.user_loader
def load_user(user_id):
    user = db.Users.find_one({"_id": ObjectId(user_id)})
    if user:
        return User(user_id=user['_id'], name=user['name'], email=user['email'])
    return None

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = db.Users.find_one({"email": email})
        if user and check_password_hash(user['password'], password):
            login_user(User(user_id=user['_id'], name=user['name'], email=user['email']))
            flash('Login effettuato con successo!', 'success')
            return redirect(url_for('profile_page'))
        flash('Credenziali non valide.', 'danger')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logout effettuato con successo.', 'success')
    return redirect(url_for('login'))

@app.route('/')
@login_required
def profile_page():
    user = db.Users.find_one({"_id": current_user.id})
    #user = db.Users.find_one({"_id": default_user})  # utente default !!! eliminare @login_required
    products_offered = db.Products.find({"_id": {"$in": user['products_offered']}})
    products_wanted = db.Products.find({"_id": {"$in": user['products_wanted']}})
    return render_template('profile_page.html', user=user, offered=products_offered, wanted=products_wanted)

@app.route('/product/<product_id>')
def product_page(product_id):
    product = db.Products.find_one({"_id": ObjectId(product_id)})
    images_list_and_index = list(enumerate(product['images']))
    user_name_string = "Offerto da: " if product['type'] == 'offered' else "Desiderato da: "
    user_name = db.Users.find_one({"_id": product['user']})['name']
    offered_in_category = db.Products.find({"category": product['category'], "type": "offered"})
    wanted_in_category = db.Products.find({"category": product['category'], "type": "wanted"})
    return render_template(
        'product_page.html', product=product, images=images_list_and_index,
        user_name_string=user_name_string, user_name=user_name,
        offered_in_category=offered_in_category, wanted_in_category=wanted_in_category)

@app.route('/user/<user_id>')
def user_page(user_id):
    user = db.Users.find_one({"_id": ObjectId(user_id)})
    products_offered = db.Products.find({"_id": {"$in": user['products_offered']}})
    products_wanted = db.Products.find({"_id": {"$in": user['products_wanted']}})
    return render_template('user_page.html', user=user, offered=products_offered, wanted=products_wanted)

@app.route('/manage-products')
def manage_products():
    # Recupera i prodotti offerti dall'utente autenticato
    user = db.Users.find_one({"_id": current_user.id})
    #user = db.Users.find_one({"_id": default_user})  # utente default !!! eliminare @login_required
    products_offered = db.Products.find({"_id": {"$in": user['products_offered']}})
    products_wanted = db.Products.find({"_id": {"$in": user['products_wanted']}})
    return render_template(
        'manage_products.html', offered=products_offered, wanted=products_wanted)

@app.route('/add-product', methods=['GET', 'POST'])
def add_product():
    if request.method == 'POST':
        # Recupera i dati dal form
        product_type = request.form.get('product_type')
        name = request.form.get('name')
        description = request.form.get('description')
        category = request.form.get('category')
        images = request.files.getlist('images')  # Multiple immagini

        # Codifica le immagini come Base64
        image_data = []
        for image in images:
            if image and image.filename != '':
                image_data.append(base64.b64encode(image.read()).decode('utf-8'))

        # Salva il prodotto nel database
        new_product = db.Products.insert_one({
            "name": name,
            "description": description,
            "category": category,
            "images": image_data,
            "type": product_type,
            "user": current_user.id,
        })

        # Aggiorna l'utente
        if product_type == 'offered':
            db.Users.update_one({"_id": current_user.id}, {"$push": {"products_offered": new_product.inserted_id}})
        elif product_type == 'wanted':
            db.Users.update_one({"_id": current_user.id}, {"$push": {"products_wanted": new_product.inserted_id}})

        return redirect(url_for('manage_products'))
    return render_template('add_product.html')

@app.route('/edit-product/<product_id>', methods=['GET', 'POST'])
def edit_product(product_id):
    product = db.Products.find_one({"_id": ObjectId(product_id)})
    images_list_and_index = list(enumerate(product['images']))
    if request.method == 'POST':
        product_name = request.form['name']
        product_description = request.form['description']
        product_category = request.form['category']
        new_images = request.files.getlist('images')  # Recupero nuove immagini

        # Nuove immagini caricate
        new_images = request.files.getlist('images')
        new_image_data = []
        for image in new_images:
            if image and image.filename != '':
                new_image_data.append(base64.b64encode(image.read()).decode('utf-8'))

        # Immagini da rimuovere
        images_to_remove = request.form.getlist('remove_images')  # Riceve gli indici come stringhe
        images_to_remove = [int(index) for index in images_to_remove]

        # Aggiornamento delle immagini nel prodotto
        existing_images = product.get("images", [])
        updated_images = [img for idx, img in enumerate(existing_images) if idx not in images_to_remove]

        # Aggiungi le nuove immagini
        updated_images.extend(new_image_data)

        # Aggiorna il database
        db.Products.update_one(
            {"_id": ObjectId(product_id)},
            {
                "$set": {
                    "name": product_name,
                    "description": product_description,
                    "category": product_category,
                    "images": updated_images,
                }
            }
        )

        return redirect(url_for('manage_products'))
    return render_template('edit_product.html', product=product, images=images_list_and_index)

@app.route('/delete-product/<product_id>')
def delete_product(product_id):
    # Logica per eliminare un prodotto
    db.Products.delete_one({"_id": ObjectId(product_id)})
    return redirect(url_for('manage_products'))

@app.route('/send-message/<recipient_id>', methods=['GET', 'POST'])
@login_required
def send_message(recipient_id):
    recipient = db.Users.find_one({"_id": ObjectId(recipient_id)})

    # Inizializza sessione se non esistente
    if 'selected_offered' not in session:
        session['selected_offered'] = []
    if 'selected_wanted' not in session:
        session['selected_wanted'] = []

    # Logica azione pulsanti
    if request.method == 'POST':
        if 'add_offered' in request.form:
            product_id = request.form['add_offered']
            if product_id not in session['selected_offered']:
                session['selected_offered'].append(product_id)
                session.modified = True

        elif 'remove_offered' in request.form:
            product_id = request.form['remove_offered']
            if product_id in session['selected_offered']:
                session['selected_offered'].remove(product_id)
                session.modified = True

        elif 'add_wanted' in request.form:
            product_id = request.form['add_wanted']
            if product_id not in session['selected_wanted']:
                session['selected_wanted'].append(product_id)
                session.modified = True

        elif 'remove_wanted' in request.form:
            product_id = request.form['remove_wanted']
            if product_id in session['selected_wanted']:
                session['selected_wanted'].remove(product_id)
                session.modified = True

        elif 'send_message' in request.form:
            message_text = request.form['message']
            message = {
                "timestamp": datetime.now(),
                "name": current_user.id,
                "offered_products": [ObjectId(pid) for pid in session['selected_offered']],
                "wanted_products": [ObjectId(pid) for pid in session['selected_wanted']],
                "text": message_text
            }
            chat = db.Messages.find(
                {"$or": [{"peopleA": current_user.id}, {"peopleB": current_user.id}],
                "$or": [{"peopleA": ObjectId(recipient_id)}, {"peopleB": ObjectId(recipient_id)}]})
            if len([m['messages'] for m in chat]) > 0: 
                db.Messages.update_one(
                    {"peopleA": {"$in": [current_user.id, ObjectId(recipient_id)]}, 
                    "peopleB": {"$in": [current_user.id, ObjectId(recipient_id)]}},
                    {"$push": {"messages": message}})
            else: 
                db.Messages.insert_one(
                    {"peopleA":  current_user.id, 
                    "peopleB": ObjectId(recipient_id), 
                    "messages": [message]})
                print("nuova chat inserita")
            session.pop('selected_offered', None)
            session.pop('selected_wanted', None)
            flash('Messaggio inviato con successo!', 'success')
            return redirect(url_for('user_page', user_id=recipient_id))

    # Recupero prodotti
    available_offered = db.Products.find({
        "user": current_user.id, "type": "offered",
        "_id": {"$nin": [ObjectId(pid) for pid in session['selected_offered']]}})
    available_wanted = db.Products.find({
        "user": ObjectId(recipient_id), "type": "offered",
        "_id": {"$nin": [ObjectId(pid) for pid in session['selected_wanted']]}})
    selected_offered = db.Products.find({"_id": {"$in": [ObjectId(pid) for pid in session['selected_offered']]}})
    selected_wanted = db.Products.find({"_id": {"$in": [ObjectId(pid) for pid in session['selected_wanted']]}})

    return render_template('send_message.html', recipient=recipient,
                           available_offered=available_offered,
                           available_wanted=available_wanted,
                           selected_offered=selected_offered,
                           selected_wanted=selected_wanted)

@app.route('/chat')
def chat():
    # Recupera i messaggi dall'utente autenticato
    document = db.Messages.find({"$or": [{"peopleA": current_user.id}, {"peopleB": current_user.id}]})
    chat = [c for c in document]
    # ordinamento delle chat dalla più recente
    def max_timestamp(c): return max([t['timestamp'] for t in c['messages']]) 
    chat_sorted = sorted([c for c in chat], key=lambda x: max_timestamp(x), reverse = True)
    # associo i nomi agli id degli user
    id_name_dict = {}
    for c in chat:
        peopleA = db.Users.find_one({"_id": c['peopleA']})
        peopleB = db.Users.find_one({"_id": c['peopleB']})
        id_name_dict[c['peopleA']], id_name_dict[c['peopleB']] = peopleA['name'], peopleB['name']
    # associo i nomi agli id dei prodotti
    id_product_dict = {}
    for c in chat:
        for m in c['messages']:
            if 'offered_products' in m.keys():
                for p in m['offered_products']:
                    product = db.Products.find_one({"_id": p})
                    id_product_dict[p] = product['name']
            if 'wanted_products' in m.keys():
                for p in m['wanted_products']:
                    product = db.Products.find_one({"_id": p})
                    id_product_dict[p] = product['name']
    print(id_name_dict)
    print(id_product_dict)
    
    return render_template('chat.html',         
        chat=chat_sorted, 
        id_name_dict=id_name_dict, 
        id_product_dict=id_product_dict,
        current_user=current_user.id)


@app.route('/send_reply/<recipient_id>', methods=['POST'])
def send_reply(recipient_id):
    reply_text = request.form['message']

    # Qui salvare il messaggio nel database (o lista di messaggi)
    new_reply = {
        'name': current_user.id,
        'text': reply_text,
        'timestamp': datetime.now()
    }

    db.Messages.update_one(
                    {"peopleA": {"$in": [current_user.id, ObjectId(recipient_id)]}, 
                    "peopleB": {"$in": [current_user.id, ObjectId(recipient_id)]}},
                    {"$push": {"messages": new_reply}})

    # Dopo che il messaggio è stato inviato, redirigi all'area chat
    return redirect(url_for('chat'))


if __name__ == '__main__':
    app.run(debug=True)
