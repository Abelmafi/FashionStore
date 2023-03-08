from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from datetime import timedelta
from elasticsearch import Elasticsearch
import os
from flask_caching import Cache

db = SQLAlchemy()
app = Flask(__name__)
# app.permanent_session_lifetime = timedelta(minutes = 20)
app.config['SECRET_KEY'] = 'mydesign1234'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:bdu0600052@localhost/fashion_store_db'
db.init_app(app)
es = Elasticsearch()
with app.app_context():
    db.create_all()


#index_settings = {
#    'settings': {
#        'analysis': {
#            'analyzer': {
#                'autocomplete': {
#                    'tokenizer': 'autocomplete',
#                    'filter': [
#                        'lowercase'
#                    ]
#                },
#                'autocomplete_search': {
#                    'tokenizer': 'lowercase'
#                }
#            },
#            'tokenizer': {
#                'autocomplete': {
#                    'type': 'edge_ngram',
#                    'min_gram': 2,
#                    'max_gram': 10,
#                    'token_chars': [
#                        'letter',
#                        'digit'
#                    ]
#                }
#            }
#        }
#    },
#    'mappings': {
#        'properties': {
#            'id': {'type': 'integer'},
#            'title': {'type': 'text', 'analyzer': 'autocomplete', 'search_analyzer': 'autocomplete_search'},
#            'description': {'type': 'text', 'analyzer': 'autocomplete', 'search_analyzer': 'autocomplete_search'},
#            'category': {'type': 'keyword'},
#            'price': {'type': 'integer'},
#            'image_file': {'type': 'keyword'},
#        }
#    }
#}
#
#def create_index():
#    index_name = "products"
#    es = Elasticsearch()
#    if not es.indices.exists(index_name):
#        mapping = {
#            "mappings": {
#                "properties": {
#                    "id": {"type": "integer"},
#                    "title": {"type": "text"},
#                    "description": {"type": "text"},
#                    "category_id": {"type": "integer"},
#                    "price": {"type": "integer"},
#                    "date_posted": {"type": "date"}
#                }
#            }
#        }
#        es.indices.create(index=index_name, body=mapping)
#    else:
#        print(f"Index '{index_name}' already exists.")
#
## Call create_index function
#create_index()

bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'
cache = Cache(app, config={'CACHE_TYPE': 'simple'})
cache.init_app(app)

from app.api import routes
from app.views import product_recommender
from app.views import search                     
