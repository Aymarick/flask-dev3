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

# Création de notre application Flask
app = Flask(__name__)
# Specification du chemin de notre fichier de Base de données
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
# Création de l'instance de notre base de données
db = SQLAlchemy(app)

# Depuis notre fichier tweet.py on importe la classe Tweet
from tweet import Tweet

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
    # Conversion du template "tweets.html" en lui injectant notre tableau de tweets definit plus haut
    return render_template('tweets.html', tweets=tweets)

# Association de la route "/tweets/<nom d'un auteur>" à notre fonction display_author_tweets()
# exemple de route : /tweets/John ; la chaine de caractère "John" sera donnée en paramètre de notre fonction
@app.route('/tweets/<author>')
def display_author_tweets(author):
    # Création d'un tableau temporaire qui contiendra les tweets de notre auteur
    authorTweets = []
    # Boucle pour parcourir les tweets existants
    for tweet in tweets: 
        # Comparaison du nom d'auteur entre celui du tweet et celui récupéré dans l'url
        if tweet.authorName == author :
            # Si les noms sont identiques, notre tweet appartient à l'auteur souhaité
            # On l'ajoute donc dans notre tableau temporaire.
            authorTweets.append(tweet)
    # Réutilisation du template "tweets.html" en y injectant notre tableau temporaire
    # qui contient les tweets d'un auteur
    return render_template('tweets.html', tweets=authorTweets)

# Association de la route "/tweets/create" à notre fonction display_create_tweet()
# Celle ci accepte 2 méthode HTTP : GET & POST
@app.route('/tweets/create', methods=['POST', 'GET'])
def display_create_tweet():
    # Si la méthode est de type "GET"
    if request.method == 'GET':
        # On affiche notre formulaire de création 
        return render_template('create_tweet.html')
    else:
        # Sinon, notre méthode HTTP est POST
        # on va donc créer un nouveau tweet
        # récupération du nom de l'auteur depuis le corps de la requête
        authorName = request.form['author']
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
        # Création d'un tweet à l'aide de notre constructeur (qui se trouve dans le fichier tweet.py)
        tweet = Tweet(authorName, content, image)
        # Insertion de notre tweet en première position dans notre tableau
        tweets.insert(0, tweet)
        # Redirection vers la liste de nos tweets
        return redirect(url_for('display_tweets'))

# Définition d'une fonction (hors Flask) nous permettant de retrouver
# un tweet avec son identifiant
def find_tweet_by_id(tweet_id):
    # Boucle pour parcourir les tweets existants
    for tweet in tweets :
        # si l'identifiant est celui dont on a besoin
        if tweet.id == tweet_id :
            # on retourne notre tweet
            return tweet
    # Si on arrive ici, c'est qu'aucun tweet n'a été trouvé avec cet id
    # on renvoie donc une valeur vide
    return None

# Association de la route "/tweets/<identifiant d'un tweet/edit" à notre fonction edit_tweet()
# Celle ci accepte 2 méthode HTTP : GET & POST
@app.route('/tweets/<int:tweet_id>/edit', methods=['POST', 'GET'])
def edit_tweet(tweet_id):
    # On récupère le tweet que l'on veut éditer à l'aide de notre fonction find_tweet_by_id
    tweet = find_tweet_by_id(tweet_id)
    #Si notre méthode HTTP est GET
    if request.method == 'GET':
        # On affiche notre formulaire d'édition prérempli avec notre tweet
        return render_template('edit_tweet.html', tweet=tweet)
    else:
        # Sinon nous avons une méthode HTTP POST, nous modifions donc notre tweet.
        # modification du nom de l'auteur depuis le corps de la requête
        tweet.authorName = request.form['author']
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
        #redirection vers l'affichage de nos tweets.
        return redirect(url_for('display_tweets'))
