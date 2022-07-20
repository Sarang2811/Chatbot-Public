# install and import various libraries like NLTK,RANDOM,STRING,SKLEARN,
# FLASK : It is used to connect Frontend and Backend.
import nltk
import random
import string
from flask import Flask, render_template, request, session, url_for, redirect
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from flask_mysqldb import MySQL
import MySQLdb


# AIML Kernel required for AIML files:
import aiml
kernel = aiml.Kernel()
kernel.learn("std-startup.xml")
kernel.respond("load aiml b")

# Here main database file is attached on which we are going to process our chatbot.
# Right now we are using simple text file as database and it is accessed by its path address.
f = open("C:\\Z_PROGRAMMING\\z\\Project\\College Enquiry Chatbot\\jspm.txt", "rt")
raw = f.read()
raw = raw.lower()

# def update(fromuser):
#     fu = open("C:\\chatbot\\questions.txt", "rt")
#     file = fu.write(fromuser)


sent_tokens = nltk.sent_tokenize(raw)
word_tokens = nltk.word_tokenize(raw)
# sent_tokens[:]
# word_tokens[:]


# now pre-processing of text file
# ----pre-processing ----


# Remove punctuations
remove_punct_dict = dict((ord(punct), None) for punct in string.punctuation)


# Lematization :

lemmer = nltk.stem.WordNetLemmatizer()


def LemTokens(tokens):
    return [lemmer.lemmatize(token) for token in tokens]


def LemNormalize(text):
    return LemTokens(nltk.word_tokenize(text.lower().translate(remove_punct_dict)))


# Now core function of Chatbot

# ---Code for initial response---

GREETING_INPUT = ("hello", "hi", "hii", "hey buddy", "hey", "what's up", "wassup")
GREETING_RESPONSES = ("Hi there...", "hey,how can I help you...", "I am glad! You r talking me...")
ENDING = ("bye", "thanks", "thank you")


def greeting(sentence):
    for word in sentence.split():
        if word.lower() in GREETING_INPUT:
            return random.choice(GREETING_RESPONSES)


# print(greeting("Heyy good morning"))

# the words need to be encoded as integers or floating point values
# for use as input to a machine learning algorithm, called feature extraction (or vectorization).
# find the similarity between words entered by the user and the words in the corpus.
# This is the simplest possible implementation of a chatbot.


# Generating response:
# define a function response which searches the user’s utterance for one or more known keywords
# and returns one of several possible responses. If it doesn't find the input matching any of the keywords,
# it returns a response:” I am sorry! I don’t understand you”
def aiml_response(query):
    resp = kernel.respond(query)
    if resp == '':
        return False
    return resp


def response(user_response):
    robo_response = ''
    sent_tokens.append(user_response)

    # Learn vocabulary and idf, return term-document matrix
    # Returns X : Tf-idf-weighted sparse matrix, [n_samples, n_features]

    TfidfVec = TfidfVectorizer(tokenizer=LemNormalize, stop_words='english')
    tfidf = TfidfVec.fit_transform(sent_tokens)
    # print (tfidf.shape)

    vals = cosine_similarity(tfidf[-1], tfidf)

    idx = vals.argsort()[0][-2]

    flat = vals.flatten()

    flat.sort()
    req_tfidf = flat[-2]

    #    user_response = user_response.lower()
    if user_response.lower() in GREETING_INPUT:
        robo_response = greeting(user_response)
        return robo_response

    elif user_response.lower() in ENDING:
        robo_response = "You are Welcome..I hope your queries get satisfied..HAVE A NICE DAY 😀"
        return robo_response

    elif aiml_response(user_response) is not False:
        robo_response = aiml_response(user_response)
        return robo_response

    elif req_tfidf == 0:
        robo_response = robo_response + "I am sorry! I don't understand you"
        #        update(user_response)
        feed = open("feedback.txt", "a")
        feed.write(user_response + "\n")
        return robo_response

    else:
        greeting(user_response)
        robo_response = robo_response + sent_tokens[idx]
        return robo_response


# Integration of Backend and Frontend:
# Flask API:

app = Flask(__name__)
app.secret_key = "123456789"

app.config["MYSQL_Host"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = "MysqlSD@19"
app.config["MYSQL_DB"] = "logindata"

db = MySQL(app)


@app.route('/', methods={'GET', 'POST'})
def index():
    if request.method == 'POST':
        if 'Email' in request.form and 'Password' in request.form:
            EMAIL = request.form['Email']
            PASSWORD = request.form['Password']
            cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute("SELECT * FROM logininfo WHERE email=%s AND password=%s", (EMAIL, PASSWORD))
            info = cursor.fetchone()

            print(info)
            if info is not None:
                if info['email'] == EMAIL and info['password'] == PASSWORD:
                    session['loginsucces'] = True
                    return redirect(url_for('bot'))
                    # return "Login Success"
            else:
                return "Login Unsuccessful.please Register"

    return render_template('login.html')


@app.route('/new', methods={'GET', 'POST'})
def new_user():
    if request.method == 'POST':
        if "one" in request.form and "two" in request.form and "three" in request.form:
            name = request.form['one']
            email = request.form['two']
            password = request.form['three']
            cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute("INSERT INTO logindata.logininfo (name,email,password) VALUES (%s,%s,%s)", (name, email, password))
            db.connection.commit()
            return redirect(url_for('index'))

    return render_template('register.html')


@app.route('/new/chatbot')
def bot():
    if session['loginsucces'] is True:
        return render_template('bot.html')


@app.route("/get")
def get_bot_response():
    userText = request.args.get("msg")  # get data from input,we write js  to index.html
    s = response(userText)
    sent_tokens.remove(userText)
    return str(s)


if __name__ == "__main__":
    app.run(debug=True)
