import datetime
from application import db

def createTweet():
    author = input("Nom de l'auteur du tweet : ")
    text = input("Contenu du tweet : ")
    return Tweet(author, text)

class Tweet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    authorName = db.Column(db.String(80), nullable=False)
    content = db.Column(db.String(140), nullable=False)
    image = db.Column(db.String(80), nullable=True)
    date = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def print(self):
        print("-------------------------")
        print("@"+self.authorName + " said at "+str(self.date)+" :")
        print(self.content)
        print("-------------------------")