from flask import Flask, render_template, request, session
from flask_sqlalchemy import SQLAlchemy
from annoy import AnnoyIndex  # pip install annoy
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import OneHotEncoder
from app import app, db, cache
from app.models.models import Category, Product, User_behavior
import numpy as np
import math

PRODUCT_TYPE_MAPPING = {
    "top": 1,
    "bottom": 2,
    "foot": 3,
    # Add more mappings as needed
}

# Define a mapping for user behavior sizes
USER_BEHAVIOR_SIZE_MAPPING = {
    "S": 1,
    "M": 2,
    "L": 3,
    "XL": 4,
    "XXL": 5,
    "XXXL": 6,
    # Add more mappings as needed
}
EVENT_TYPE_MAPPING = {
    "purchase": 5,
    "view": 1
}
def get_user_id_from_session_or_cookie():
    user_id = None
    if 'user_id' in session:
        user_id = session['user_id']
    elif 'user_id' in request.cookies:
        user_id = request.cookies['user_id']
    return user_id


def get_category_name_from_session_or_cookie():
    category_name = None
    if 'category_name' in session:
        category_name = session['category_name']
    elif 'category_name' in request.cookies:
        category_name = request.cookies['category_name']
    return category_name


@app.route('/record-behavior', methods=['POST'])
def record_behavior():
    data = request.get_json()
    product_id = data.get('product_id')
    behavior_type = data.get('behavior_type')

    # Get the user ID from the session or cookie
    user_id = get_user_id_from_session_or_cookie()

    # Insert the new behavior into the database
    behavior = User_behavior(user_id=user_id, product_id=product_id, behavior_type=behavior_type)
    db.session.add(behavior)
    db.session.commit()

    return 'Behavior recorded successfully!'

# more effective and less time consuming recommendation method 
# Define a function to build an Annoy index from the product features
#def build_annoy_index(product_features):
#    num_features = len(list(product_features.values())[0])
#    t = AnnoyIndex(num_features, 'euclidean')
#    for product_id, features in product_features.items():
#        t.add_item(product_id, list(features.values()))
#    t.build(50)
#    return t
#
## Define the get_top_n_similar_products function using Annoy
#def get_top_n_similar_products_annoy(user_feature_vector, product_features, n):
#    annoy_index = build_annoy_index(product_features)
#    product_ids, distances = annoy_index.get_nns_by_vector(list(user_feature_vector.values()), n, include_distances=True)
#
#    # Sort the results by distance
#    sorted_results = sorted(zip(product_ids, distances), key=lambda x: x[1])
#
#    # Extract the recommended product ids
#    recommended_product_ids = [product_id for product_id, _ in sorted_results]
#    return recommended_product_ids

def get_top_n_similar_products(user_feature_vector, product_features, n=9):
    # Compute the cosine similarity between the user feature vector and the product feature vectors
    similarities = {}
    for product_id, features in product_features.items():
        # Compute the dot product between the user feature vector and the product feature vector
        dot_product = sum([user_feature_vector[feature] * features[feature] for feature in user_feature_vector.keys()])

        # Compute the Euclidean norm of the user feature vector and the product feature vector
        user_norm = math.sqrt(sum([user_feature_vector[feature] ** 2 for feature in user_feature_vector.keys()]))
        product_norm = math.sqrt(sum([features[feature] ** 2 for feature in user_feature_vector.keys()]))

        # Compute the cosine similarity between the user feature vector and the product feature vector
        if user_norm and product_norm:
            similarity = dot_product / (user_norm * product_norm)
        else:
            similarity = 0;

        # Store the similarity score for the product
        similarities[product_id] = similarity

    # Sort the products by similarity score in descending order
    sorted_similarities = sorted(similarities.items(), key=lambda x: x[1], reverse=True)

    # Get the top N most similar products
    top_n_similar_products = [product_id for product_id, similarity in sorted_similarities[:n]]

    return top_n_similar_products

# @cache.memoize(timeout=3600)
def get_product_features():
    """Get the product features from the database"""
    product_features = {}
    category_name = get_category_name_from_session_or_cookie()
    category = Category.query.filter_by(name = category_name).first()
    products = Product.query.filter_by(type = category)
    # products = Product.query.all()
    for product in products:
        product_type = PRODUCT_TYPE_MAPPING.get(product.product_type, 0)
        product_size = USER_BEHAVIOR_SIZE_MAPPING.get(product.product_size, 0)
        product_features[product.id] = {"product_type": product_type, "product_size": product_size}

    return product_features


#@cache.memoize(timeout=3600)
def get_user_feature_vector(user_id):

    user_behaviors = User_behavior.query.filter_by(user_id=user_id).all()
    if not user_behaviors:
        return []

    # Compute the user's feature vector
    user_feature_vector = {"product_type": 0, "product_size": 0}
    for behavior in user_behaviors:
        product = Product.query.get(behavior.product_id)
        if product is not None:
            product_type = PRODUCT_TYPE_MAPPING.get(product.product_type, 0)
            user_behavior_size = USER_BEHAVIOR_SIZE_MAPPING.get(product.product_size, 0)
            event_type = EVENT_TYPE_MAPPING.get(behavior.behavior_type, 0)

            user_feature_vector["product_type"] += product_type * event_type
            user_feature_vector["product_size"] += user_behavior_size * event_type

    return user_feature_vector

def get_recommendations(user_id=None, n=9, event_type="purchase"):
    # If no user_id is provided, return an empty list
    if user_id is None:
        return []

    # Get the product features from the database
    product_features = get_product_features()

    # Compute the user's feature vector
    user_feature_vector = get_user_feature_vector(user_id)

    # Get the most similar products to the user's feature vector
    recommended_product_ids = get_top_n_similar_products(user_feature_vector, product_features, n)

    return recommended_product_ids

