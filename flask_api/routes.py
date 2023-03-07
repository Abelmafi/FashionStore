#!/usr/bin/python3
"""RESTApi using flask application"""
from flask import redirect, flash, render_template, url_for, request
from fashionshop.forms import RegistrationForm,LoginForm, InforForm, UserForm
from fashionshop import db, bcrypt, app, es
from fashionshop.models import *
from flask_login import current_user, login_user, login_required, logout_user
from product_recommender import *
from chatbot import bot


@app.route("/", methods=['GET', 'POST','PUT'])
@app.route("/home")
def home():
    """Api that redirect to home page"""
    session.permanent = True

    return render_template('home.html')

@app.route("/about")
def about():
    """Api that redirect to about page"""

    return render_template('about.html')

@app.route("/register", methods=['GET', 'POST'])
def register():
    """Api that redirect to registration page"""

    if current_user.is_authenticated:
        redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username = form.username.data,
                    email = form.email.data,
                    password = password)
        db.session.add(user)
        db.session.commit()
        flash(f'Your account have been created!', 'success')
        return redirect(url_for('login'))

    return render_template('register.html', form = form, title = 'Register')

@app.route("/login", methods=['GET','POST'])
def login():
    """Api that redirect to user login page"""

    if current_user.is_authenticated:
        redirect(url_for('home'))
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email = form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember = form.remember.data)
            flash(f'Login succesfully!', 'success')
            return redirect(url_for('home'))
        else:
            flash(f'Please check the information!','danger')
    return render_template('login.html', form = form, title = 'Login')

@app.route('/ssearch')
def ssearch():
    query = request.args.get('q', '')
    if query:
        products = search_products(query)
    else:
        products = []
    print (f"here are the products", products)
    return render_template('search.html', query=query, products=products)

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    """Api that redirect to contact admin page"""

    session['firstname'] = request.form.get('firstname')
    session['lastname'] = request.form.get('lastname')
    session['email'] = request.form.get('email')
    session['subject'] = request.form.get('subject')
    session['message'] = request.form.get('message')
    print(session['firstname'], session['lastname'], session['email'],
          session['subject'],session['message'])
    if session['firstname'] != None:
        flash(f'Message sent!', 'success')
    return render_template('contact.html', tilte = 'Contact')

@app.route('/categories')
def categories():
    """Api that redirect to product caegories page"""

    page = request.args.get('page', 1, type = int)
    products = Product.query.order_by(Product.title.desc()).paginate(page = page, per_page = 12)
    categories = Category.query.all()
    total_results = Product.query.count()
    return render_template('categories.html',
                            title = 'Categories',
                            products = products,
                            categories = categories,
                            totals = total_results)

@app.route('/category/filter/<string:category_name>', methods=['GET'])
def filter(category_name):
    """Api that redirect to product category page"""

    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 12))

    # Get the filter criteria from the request parameters
    min_price = request.args.get('minprice')
    max_price = request.args.get('maxprice')
    product_type = request.args.get('product_type')
    size = request.args.get('size')
    categories = Category.query.all()

    # Create the queries based on the filter criteria
    queries = []
    # Get the filter parameters from the request args
    filters = {
        'minprice': min_price,
        'maxprice': max_price,
        'type': product_type,
        'size': size,
        'category_name': category_name
    }
    if category_name != 'All':
        category = Category.query.filter_by(name = category_name).first()
        query1 = Product.query.filter_by(type=category)
        queries.append(query1)
    else:
        query1 = Product.query
        queries.append(query1)
    if min_price is not None and max_price is not None:
        query2 = Product.query.filter(Product.price >= int(min_price), Product.price <= int(max_price))
        queries.append(query2)
    if product_type is not None:
         query3 = Product.query.filter_by(product_type=product_type)
         queries.append(query3)
    if size is not None:
        query4 = Product.query.filter_by(product_size=size)
        queries.append(query4)

    # Get the intersection of the queries
    if len(queries) > 1:
        filtered_products = queries[0].intersect(*queries[1:])
    else:
        filtered_products = queries[0]

    sort_by = request.args.get('sort')

    # Apply sorting based on the sort_by parameter
    if sort_by == 'price_asc':
        filtered_products = filtered_products.order_by(Product.price.asc())
    elif sort_by == 'price_desc':
        filtered_products = filtered_products.order_by(Product.price.desc())
    elif sort_by == 'name_asc':
        filtered_products = filtered_products.order_by(Product.title.asc())
    elif sort_by == 'name_desc':
        filtered_products = filtered_products.order_by(Product.title.desc())

    # Paginate the results using the paginate() method
    paginated_products = filtered_products.paginate(page, per_page)

    total_results = paginated_products.total #Product.query.filter_by(type = category).count()

    return render_template('filter.html', title = 'Categories',
                            # category = category,
                            products = paginated_products,
                            categories = categories,
                            category_name = category_name,
                            totals = total_results,
                            filters = filters)


@app.route('/product/<int:product_id>', methods=['POST','GET'])
def product(product_id):
    """Api that redirect to product list page"""
    product = Product.query.get_or_404(product_id)
    comments = Comment.query.filter_by(product_id=product.id).order_by(Comment.date_posted.desc())
    # comments = Comment.query.filter_by(product = product).order_by(Comment.date_posted.desc())
    print("product", product.title)

    if request.method == 'POST':
        quantity = int(request.form.get('quantity'))
        if "cart" in session:
            if not any(product.title in d for d in session['cart']):
                session['cart'].append({product.title: quantity})
            elif any(product.title in d for d in session['cart']):
                for d in session['cart']:
                    if product.title in d:
                        d[product.title] += quantity
        else:
            session['cart'] = [{product.title: quantity}]
        print(session['cart'])

        session['quantity'] = 0
        for k in session['cart']:
            for d in k:
                session['quantity'] += k[d]

        flash(f'Adding to shopping cart succesfully!', 'success')

    user_id = get_user_id_from_session_or_cookie()
    recommended_products_id = get_recommendations(user_id)
    recommended_products = []
    for id  in recommended_products_id:
        p = Product.query.get(id)
        recommended_products.append(p)
    if 'content_error' in session:
        content_error = session['content_error']
    else:
        content_error = None

    return render_template('product.html', title = 'Product',
                            product = product,
                            recommended_products = recommended_products,
                            comments = comments,
                            content_error = content_error)

@app.route('/product/<int:product_id>/new_comment', methods = ['POST','GET'])
@login_required
def new_comment(product_id):
    """Api that redirect to comment page"""

    content = request.args.get('content')
    product = Product.query.get_or_404(product_id)
    author = current_user
    content_chatbot = str(bot.get_response(content))
    comment = Comment(content = content, author = author,
                      product = product,
                      content_chatbot = content_chatbot)
    db.session.add(comment)
    db.session.commit()
    flash('Adding new comment successfully!')
    return redirect(url_for('product', product_id = product.id))

@app.route('/checkout', methods=['GET','POST'])
def checkout():
    """Api that manipulate peoduct perchase checkout page"""

    total = session['total']
    subtotal = session['subtotal']
    shipping = session['shipping']
    form = InforForm()
    if form.validate_on_submit():
        country = request.form.get('country_select')
        infor = Infor(name = form.name.data,
                      address = form.address.data,
                      country = country,
                      city = form.city.data,
                      postcode = form.postcode.data,
                      phone = form.phone.data,
                      total_price = total)

        db.session.add(infor)
        db.session.commit()
        item = []
        if 'order' in session:
            for k in session['order']:
                product = Product.query.filter_by(title = k).first()
                c1 = CartItem(product_id = product.id,
                              quantity = session['order'][k][2])
                item.append(c1)
        infor.cartitems.extend(item)
        db.session.add_all(item)
        db.session.commit()
        flash(f'You ordered successully!', 'success')
        session.pop('cart')
        session.pop('order')
        return redirect(url_for('home'))
    return render_template('checkout.html', title = 'Check Out',
            form = form,
            total = total,
                            subtotal = subtotal,
                            shipping = shipping)

@app.route('/cart', methods=['POST','GET'])
def cart():
    """Api that redirect to product inside cart list page"""
    subtotal = 0
    order = {}
    session['quantity'] = 0
    if 'cart' in session:
        print(session['cart'])
        for d in session['cart']:
            for k in d:
                product = Product.query.filter_by(title = k).first()
                order[product.title] = []
                order[product.title].append(product.price)
                order[product.title].append(product.image_file)
                order[product.title].append(d[k])
                order[product.title].append(product.price * d[k])
                subtotal += product.price * d[k]
                session['quantity'] += d[k]
    print(order)
    session['order'] = order
    print('You have your own items!')
    shipping = 10
    coupon = 0
    total = subtotal + shipping
    session['shipping'] = shipping
    session['subtotal'] = subtotal
    session['total'] = total
    return render_template('cart.html', title = 'Cart',
                            total = total,
                            subtotal = subtotal,
                            shipping = shipping,
                            order = order)

@app.route('/cart/remove/<string:product_title>', methods=['POST'])
def remove_from_cart(product_title):
    """Api that remove products from cart"""

    print('before', session['cart'])
    for i in session['cart']:
        if product_title in i:
            i.pop(product_title)
    print('after', session['cart'])
    return redirect(url_for('cart'))

@app.route('/cart/deleteall', methods=['POST'])
def delete_all():
    """Api that delete all product items from cart"""

    session.pop('cart')
    return redirect(url_for('cart'))

@app.route('/cart/update',methods=['POST'])
def update_cart():
    """Api that update cart items """

    qty = request.form.get('update_qty')
    p = request.form.get('update_p')
    print(p,qty)
    print("update_cart")
    for i in session['cart']:
        if p in i:
            i.update({p:int(qty)})
    print(session['cart'])
    return redirect(url_for('cart'))

@app.route('/search', methods=['POST','GET'])
def search():
    """Api that search products using elastic search"""

    index_name = 'fashionshop'
    doc_type = 'product'
    query = request.form.get('query')
    print(query)

    query = es.search(index = index_name,
                      body={'query':{'match': {'title': query}}})
    found = query['hits']['total']['value']
    products = []
    print(query['hits']['hits'])

    for item in query['hits']['hits']:
        product= Product.query.filter_by(title = item['_source']['title']).first()
        print(product)
        products.append(product)

    print(products)
    return render_template('search.html', products = products, found = found)

@app.route('/logout')
def logout():
    """Api that loges user out using flask login method"""

    logout_user()
    return redirect(url_for('home'))

@app.route('/user', methods = ['GET','POST'])
@login_required
def user():
    """Api that add new user to database"""

    form = UserForm()
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.email = form.email.data
        current_user.birthday = form.birthday.data
        current_user.gender = form.gender.data
        db.session.commit()
        print('Save successfully!')
        flash(f'Your account information has updated!','success')
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
        form.birthday.data = current_user.birthday
        form.gender.data = current_user.gender
    return render_template('user.html', title='User',  form= form)

