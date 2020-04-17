# Import de fonctions depuis le Framework Flask
from flask import Flask
# Import d'une fonction pour convertir un template HTML en y injectant des variables python
from flask import render_template
# Import de la variable request de Flask
from flask import request
# Import d'une fonction pour rediriger la réponse,
# et url_for une méthode pour récupérer l'url avec son nom de fonction
from flask import redirect, url_for
# Import de la lib "os" qui permet d'interagir avec notre système d'exploitation
import os
# Import de la gestion de BDD à l'aide du framework SQLAlchemy
from flask_sqlalchemy import SQLAlchemy
# Import d'une fonction flask pour terminer une requête avec un code d'erreur
from flask import abort

# Création de notre application Flask
app = Flask(__name__)
# Specification du chemin de notre fichier de Base de données
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
# Création de l'instance de notre base de données
db = SQLAlchemy(app)

# Depuis notre fichier tweet.py on importe la classe Tweet
from tweet import Tweet
from user import User

# Récupération du chemin du fichier de la base de données
dbPath = os.path.join(app.root_path, 'data.db')
# Si le fichier n'existe pas
if not os.path.exists(dbPath):
    # Je créer ma base de données
    db.create_all()
    print("Base de données créée")

# Tableau pour stocker nos tweets 
tweets = []

# append = ajouter à la fin
# Créations de tweets d'exemples
# tweets.append(Tweet("John", "Tweet n°1"))
# tweets.append(Tweet("Jane", "Lorem ipsum"))
# tweets.append(Tweet("John", "Dolores sit amet"))
# tweets.append(Tweet("John", "Autre tweet"))
# tweets.append(Tweet("John", "Dernier tweet"))

# Association de la route "/" à notre fonction hello_world()
@app.route('/')
def hello_world():
    # On renvoi à notre navigateur du texte
    return 'Hello, World!'

# Association de la route "/tweets" à notre fonction display_tweets()
@app.route('/tweets')
def display_tweets():
    # récupération des tweets de la BDD.
    allTweets = Tweet.query.all()
    # Conversion du template "tweets.html" en lui injectant notre tableau de tweets récupérés de la BDD
    return render_template('tweets.html', tweets=allTweets)

    # Association de la route "/users" à notre fonction display_users()
@app.route('/users')
def display_users():
    # récupération des utilisateur de la BDD.
    allUsers = User.query.all()
    # Conversion du template "tweets.html" en lui injectant notre tableau de tweets récupérés de la BDD
    return render_template('users.html', users=allUsers)

# Association de la route "/tweets/<identifiant d'un utilisateur>" à notre fonction display_author_tweets()
# exemple de route : /tweets/1 ; l'entier "1" sera donnée en paramètre de notre fonction
@app.route('/tweets/<int:user_id>')
def display_author_tweets(user_id):
    # Récupération de l'utilisateur avec son identifiant
    user = User.query.filter_by(id=user_id).first()
    # Si l'utilisateur n'existe pas
    if user == None:
        # On renvoie une page 404 Not Found
        abort(404)
    # Récupération des tweets en utilisant la relation définie dans le modèle
    authorTweets = user.tweets
    # Réutilisation du template "tweets.html" en y injectant notre tableau 
    # qui contient les tweets d'un auteur
    return render_template('tweets.html', tweets=authorTweets)

# Association de la route "/tweets/create" à notre fonction display_create_tweet()
# Celle ci accepte 2 méthode HTTP : GET & POST
@app.route('/tweets/create', methods=['POST', 'GET'])
def display_create_tweet():
    # Si la méthode est de type "GET"
    if request.method == 'GET':
        #Récupération de la liste des utilisateurs pour la relation tweet<->user
        users = User.query.all()
        # On affiche notre formulaire de création en lui donnant la liste des utilisateurs
        return render_template('create_tweet.html', users=users)
    else:
        # Sinon, notre méthode HTTP est POST
        # on va donc créer un nouveau tweet
        # récupération de l'identifiant de l'utilisateur depuis le corps de la requête
        user_id = request.form['user_id']
        # récupération du contenu depuis le corps de la requête
        content = request.form['content']
        # Création d'une variable image par défaut vide.
        image = None
        # récupération de l'image depuis le corps de la requête
        f = request.files['image']
        # Si il y a bel et bien une image d'uploadé
        if f.filename != '' :
            # On construit le chemin de destination de notre image (où est-ce qu'on va la sauvegarder)
            filepath = os.path.join(app.root_path, 'static', 'uploads', f.filename)
            # On sauvegarde notre image dans ce chemin
            f.save(filepath)
            # création de l'url de l'image pour son affichage (à l'aide de son nom)
            image = url_for('static', filename='uploads/'+f.filename)
        # Création d'un tweet à l'aide du constructeur généré par SQLAlchemy 
        tweet = Tweet(user_id=user_id, content=content, image=image)
        # Insertion de notre tweet dans session de base de données
        # Attention, celui-ci n'est pas encore présent dans la base de données
        db.session.add(tweet)
        # Sauvegarde de notre session dans la base de données
        db.session.commit()
        # Redirection vers la liste de nos tweets
        return redirect(url_for('display_tweets'))

# Association de la route "/tweets/<identifiant d'un tweet/edit" à notre fonction edit_tweet()
# Celle ci accepte 2 méthode HTTP : GET & POST
@app.route('/tweets/<int:tweet_id>/edit', methods=['POST', 'GET'])
def edit_tweet(tweet_id):
    # On récupère le tweet que l'on veut éditer dans notre base de données
    tweet = Tweet.query.filter_by(id=tweet_id).first()
    # Si on ne trouve pas le tweet
    if tweet == None:
        # On émet une erreur 404 Not Found
        abort(404)
    #Si notre méthode HTTP est GET
    if request.method == 'GET':
        # récupération de nos utilisateurs depuis la base de données
        users = User.query.all()
        # On affiche notre formulaire d'édition prérempli avec notre tweet
        # On donne également la liste des utilisateurs pour les afficher dans le select
        return render_template('edit_tweet.html', tweet=tweet, users=users)
    else:
        # Sinon nous avons une méthode HTTP POST, nous modifions donc notre tweet.
        # modification de l'auteur avec son identifiant depuis le corps de la requête
        tweet.user_id = request.form['user_id']
        # modification du contenu depuis le corps de la requête
        tweet.content = request.form['content']
        # Récupération de l'image depuis le corps de la requête.
        f = request.files['image']
        # Si notre fichier est bel et bien présent
        if f.filename != '' :
            # On construit le chemin de destination de notre image (où est-ce qu'on va la sauvegarder)
            filepath = os.path.join(app.root_path, 'static', 'uploads', f.filename)
            # On sauvegarde notre image dans ce chemin
            f.save(filepath)
            # On modifie l'url de l'image pour son affichage (à l'aide de son nom)
            tweet.image = url_for('static', filename='uploads/'+f.filename)
        # Sauvegarde de notre session dans la base de données
        db.session.commit()
        # redirection vers l'affichage de nos tweets.
        return redirect(url_for('display_tweets'))

@app.route('/users/create', methods=['POST', 'GET'])
def create_user():
    # Si la méthode est de type "GET"
    if request.method == 'GET':
        # On affiche notre formulaire de création
        return render_template('create_user.html')
    else:
        # Sinon, notre méthode HTTP est POST
        # on va donc créer un nouvel utilisateur
        # récupération du nom de l'utilisateur depuis le corps de la requête
        name = request.form['name']
        # récupération de l'email depuis le corps de la requête
        email = request.form['email']
        # récupération du mot de passe depuis le corps de la requête
        password = request.form['password']
        # Création d'un utilisateur à l'aide du constructeur généré par SQLAlchemy 
        user = User(name=name, email=email, password=password)
        # Insertion de notre utilisateur dans session de base de données
        # Attention, celui-ci n'est pas encore présent dans la base de données
        db.session.add(user)
        # Sauvegarde de notre session dans la base de données
        db.session.commit()
        # Redirection vers la liste de nos tweets
        return redirect(url_for('display_users'))

# Association de la route "/users/<identifiant d'un utilisateur/edit" à notre fonction edit_user()
# Celle ci accepte 2 méthode HTTP : GET & POST
@app.route('/users/<int:user_id>/edit', methods=['POST', 'GET'])
def edit_user(user_id):
    # On récupère l'utilisateur que l'on veut éditer dans notre base de données
    user = User.query.filter_by(id=user_id).first()
    # Si on ne trouve pas l'utilisateur
    if user == None:
        # On émet une erreur 404 Not Found
        abort(404)
    #Si notre méthode HTTP est GET
    if request.method == 'GET':
        # On affiche notre formulaire d'édition prérempli avec notre utilisateur
        return render_template('edit_user.html', user=user)
    else:
        # Sinon nous avons une méthode HTTP POST, nous modifions donc notre utilisateur.
        # modification du nom de l'utilisateur depuis le corps de la requête
        user.name = request.form['name']
        # modification de l'email depuis le corps de la requête
        user.email = request.form['email']
        # Sauvegarde de notre session dans la base de données
        db.session.commit()
        # redirection vers l'affichage de nos utilisateurs.
        return redirect(url_for('display_users'))