

#
#   /===============\
#  |     api.py      |
#   \===============/
#
# L'objectif est de créer une API de sentiment analysis. Cette API peut être utilisée 
# par différents utilisateurs qui s’identifieront via un système de username/mot de passe
#
# Deux version du modèles sont considéré, i.e. v1, v2
# La liste des username , password et des permissions pour le modèle v1 et v2 sont 
# contenues dans le fichiers credentials.csv : si un username a une colonne v1 qui 
# vaut 1 alors il a accès à la première version de l’API, de même avec la colonne v2.

#
# > CE MODULE ET L'ARCH GLOBALE 
#
# Le module actuel (api.py) consiste en un ensemble de fonctions accessibles via 
# une API HTTP RESTful. L'implémentation est basée sur FastAPI [2], 
#
# Ce module, ainsi que les modules d'accès/gestion des données d'authentification, 
# ainsi que celle implémentant la logique (sentiment analysis), constituent les composants 
# de base d'une architecture n-tiers. Ce type d'architecture (également appelée multi-tiers) 
# est un modèle architectural dans lequel les fonctions de présentation, de traitement 
# des applications (logique) et de gestion des données sont séparées [1]. 
# Plus de détails sont fournis plus loin.
#
# [1] https://fastapi.tiangolo.com/
# [2] https://en.wikipedia.org/wiki/Multitier_architecture
#
# > FORMAT DE REPONSES
#
# Toutes les réponses sont de la forme suivante:
#  {
#     'response_code': # 0 dans le cas d'une requette réussite, 1 sinon   
#     'username': username, # en cas de requette avec authentification
#     'results': {
#         # - le corps de la réponse, e.g. "status", "score", etc 
#         # - dans le cas particulier d'une erreur (response_code = 1), 
#         #   cette partie contiendra un champs appelé "error_details", 
#         #   donnant plus de détails sur la nature de l'erreur
#     }
#      
#  }
#
# > PLUS SUR LA GESTION D'ERREURS
#
# Au sujet de la gestion des erreurs, on a opté pour une version simple
# consistant à inclure, dans chaque réponse, un champ baptisé 'response_code" 
# En voici les différentes valeurs :
#
#     0 : l'appel est correctement traité 
#     1 : Type d'authentification inconnu
#     2 : Information d'authentification incorrectes ou absentes
#     3 : L’appel est correct, mais la ressource n'est pas accessible pour
#         l'utilisateur en cours
#
#     En plus du code d'erreur, un champ supplémentaire est fourni, 
#     donnant plus de détails sur l'erreur
#



from flask import Flask, request
import data
import sentiments


api = Flask(import_name='my_api')

# --------------------------------------
# GET /status: 
#      renvoie 1 si l’API fonctionne.
# --------------------------------------
@api.route('/status', methods=['GET'])
def is_on():     
     return {
         'response_code':0,
         'results':{
                'status': 1
         }  
     }# ---------------------
# -----



# --------------------------------------------------------------
# Renvoie la liste des permissions d’un utilisateur authentifié 
# par son username et son password. Deux variantes sont possibles;
# chacune avec un code "auth_type" différent :
#
# <auth_type = 1> 
#
# Il s'agit d'une version simple où le couple login/pass est passés
# via "query arguments" (par opposition au "path parameters"). 
# ex : http://127.0.0.1:5000/permissions/1/?password=6837&username=Megan

#
# <auth_type = 2> 
#
# Il s'agit d'une version améliorée. Le 
# couple user/pass est passé en utilisant une authentification de 
# de type "Basic Auth" [1,2], i.e.
#
#       "" It is a method for an HTTP user agent to provide a user 
#          name and password when making a request. In basic HTTP 
#          authentication, a request contains a header field in the 
#          form of Authorization: Basic <credentials>, where credentials 
#          is the Base64 encoding of ID and password joined by a single 
#          colon [2]""
#
# ex : http://127.0.0.1:5000/permissions/2/
# Pour tester, des outils tels postman vous serez utiles. Choisisez une
# authentification de type "Basic Auth" puis essayer avec les login stocké 
# (in plain) dans le fichier credentials.csv.
#
# [1] https://en.wikipedia.org/wiki/Basic_access_authentication
# [2] https://swagger.io/docs/specification/authentication/basic-authentication/
# 
# --------------------------------------
@api.route('/permissions/<auth_type>/', methods=['GET'])
def creds(auth_type):
    if int(auth_type) == 2 :
        username = request.authorization["username"]
        password = request.authorization["password"]
    elif int(auth_type) == 1 :
        username = request.args.get('username')
        password = request.args.get('password')
    else :
        return {
             'response_code': 1,
             'results': {
                 'error_details': 'Unknown authentification type',
             }
        }
    v1, v2 = data.get_creds(username, password)
    if (v1 != None) and (v2 != None) :
        return {
             'response_code': 0,
             'username': username,
             'results': {
                 'v1': v1,
                 'v2': v2
             }
        }
    else :
        return {
             'response_code': 1,
             'username': username,
             'results': {
                 'error_details': 'Unknown <username> or <password>',
             }
        }


# ================================================================================
# Cette partie est responsable du renvoie d'un score de sentiment pour la phrase 
# proposée par l’argument "sentence" (si l’utilisateur username est bien identifié)
# Deux variantes sont possible :
#
# Pour simplifier, la première version (endpoint GET /v1/sentiment) renvoi un nombre 
# aléatoire entre -1 et 1
#
# La 2éme version (endpoint GET /v2/sentiment) devra par contre renvoyer le compound 
# d’un VaderSentiment (SentimentIntensityAnalyzer()). Voir le lien [x] pour plus de 
# détails sur l’utilisation de cette librairie.
#
# De la même façon que les fonctions ci-desus, chaque route est solicité de deux
# manières (chacune avec un type d'authentification à part)
#                                                             ===========================
# [x] https://github.com/cjhutto/vaderSentiment#code-examples |
# ============================================================/



# --------------------------------------------------------------
# GET /v1/1/sentiment username password sentence or
# GET /v1/2/sentiment sentence
# Une version plus simple qui simule le renvoie du score de sentiment de la phrase 
# proposée par l’argument sentence si l’utilisateur username est bien identifié.

# <auth_type> permet de distunger le type d'authentification utilisé
#     - "1" pour une authentification en query
#     - "2" pour une authentification en "Basic Auth"
#
# [exemples] :
#
# 127.0.0.1:5000/v1/2/sentiment/?sentence='I am happy'
# 127.0.0.1:5000/v1/1/sentiment/?username=Steven&password=XXXX&sentence='I am happy'
# --------------------------------------
@api.route('/v1/<auth_type>/sentiment/', methods=['GET'])
def sentiment_v1(auth_type):
    if int(auth_type) == 2 :
        try: 
            username = request.authorization["username"]
            password = request.authorization["password"]
        except :
            return {
                'response_code': 2,
                'username': None,
                'results':{
                    'error_details': 'Unkown <username> or <password>'
                }      
            }
    elif int(auth_type) == 1 :
        username = request.args.get('username')
        password = request.args.get('password')
    else :
        return {
             'response_code': 1,
             'username': username,
             'results': {
                 'error_details': 'Unknown authentification type',
             }
        }
    sentence = request.args.get('sentence')
    v1, v2 = data.get_creds(username, password)
    if (v1 == None) or (v2 == None) :
        return {
            'response_code': 2,
            'username': username,
            'results':{
                'error_details': 'Unkown <username> or <password>'
            }      
        }
    elif (v1 == 0):
        return {
            'response_code': 3,
            'username': username,            
            'results':{
                'error_details': 'Forbiden for the current user'
            }
        }
    else:      
        score = sentiments.get_score_v1(sentence)
        #return str(number)
        return {
            'response_code': 0,
            'username': username,            
            'results':{
                'sentence': sentence,
                'score': str(score),
            }      
        }



# --------------------------------------------------------------
# GET /v2/1/sentiment/ username password sentence or
# GET /v2/2/sentiment sentence
#
# La 2éme version (endpoint GET /v2/sentiment) devra renvoyer le compound 
# d’un VaderSentiment (SentimentIntensityAnalyzer()).

# <auth_type> permet de distunger le type d'authentification utilisé
#
#     - "1" pour une authentification en query
#     - "2" pour une authentification en "Basic Auth"
#
# [exemples] :
#
# 127.0.0.1:5000/v2/2/sentiment/?sentence='I am happy'
# 127.0.0.1:5000/v2/1/sentiment/?username=Steven&password=XXXX&sentence='I am happy'
# --------------------------------------

@api.route('/v2/<auth_type>/sentiment/', methods=['GET'])
def sentiment_v2(auth_type):
    if int(auth_type) == 2 :
        username = request.authorization["username"]
        password = request.authorization["password"]
    elif int(auth_type) == 1 :
        username = request.args.get('username')
        password = request.args.get('password')
    else :
        return {
             'response_code': 1,
             'results': {
                 'details': 'Unknown authentification type',
             }
        }
    sentence = request.args.get('sentence')
    v1, v2 = data.get_creds(username, password)

    if (v1 == None) or (v2 == None) :
        return {
            'response_code': 2,
            'username': username,
            'results':{
                'error_details': 'Unkown <username> or <password>'
            }      
        }
    elif (v2 == 0):
        return {
            'response_code': 3,
            'username': username,            
            'results':{
                'error_details': 'Forbiden for the current user'
            }
        }
    else:      
        score = sentiments.get_score_v2(sentence)
        #return str(number)
        return {
            'response_code': 0,
            'username': username,            
            'results':{
                'sentence': sentence,
                'score': score['compound'],
            }      
        }


if __name__ == '__main__':
    api.run(host="0.0.0.0", port=5000, debug=True)


