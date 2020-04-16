import datetime

def createTweet():
    author = input("Nom de l'auteur du tweet : ")
    text = input("Contenu du tweet : ")
    return Tweet(author, text)

class Tweet:
    numberOfTweets=0
    def __init__(self, authorName, content, image=None):
        Tweet.numberOfTweets += 1
        self.id = Tweet.numberOfTweets
        self.authorName = authorName
        self.content = content
        self.image = image
        self.date = datetime.datetime.now()

    def print(self):
        print("-------------------------")
        print("@"+self.authorName + " said at "+str(self.date)+" :")
        print(self.content)
        print("-------------------------")