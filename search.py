from . import db, es
from .models import Product


#def index_products():
#    for product in Product.query.all():
#        es.index(index='products', id=product.id, body={
#            'title': product.title,
#            'description': product.description,
#            'category_id': product.category_id,
#            'price': product.price
#        })


def search_products(query):
    products = Product.query.all()

    index_name = "products"
    if not es.indices.exists(index_name):
        mapping = {
            "mappings": {
                "properties": {
                    "id": {"type": "integer"},
                    "title": {"type": "text"},
                    "description": {"type": "text"},
                    "category_id": {"type": "integer"},
                    "price": {"type": "integer"},
                    "date_posted": {"type": "date"}
                }
            }
        }
        es.indices.create(index=index_name, body=mapping)

    for product in products:
    # create document in Elasticsearch
        es.index(index='products', id=product.id, body={
            'id': product.id,
            'title': product.title,
            'description': product.description,
            #'category': product.category.name,
            'price': product.price,
            'date_posted': product.date_posted
        })
    search_body = {
        'query': {
            'multi_match': {
                'query': query,
                'fields': ['title', 'description']
            }
        }
    }
    response = es.search(index='products', body=search_body)
    product_ids = [hit['_id'] for hit in response['hits']['hits']]
    return Product.query.filter(Product.id.in_(product_ids)).all()

