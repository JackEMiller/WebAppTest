from flask import Flask, render_template, request, session, redirect, url_for
import math
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
# engine = sqlalchemy.create_engine("mysql+mysqlconnector://pyuser:pydemo@localhost:33060/db",echo=True)
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+pymysql://pyuser@34.89.11.19/db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
# session = db.session()
# cursor = session.execute(db).cursor


class Users(db.Model):
    user_name = db.Column(db.String(30), primary_key = True, nullable = False)
    password = db.Column(db.String(30), nullable= False)


class Customers(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(30), nullable=False)
    last_name = db.Column(db.String(30), nullable=False)


class Products(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False)
    price = db.Column(db.String(30), nullable=False)


class Transactions(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer,  db.ForeignKey('customers.id'),nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'),nullable=False)


db.create_all()


@app.route('/viewtransaction/<int:id>', methods=['GET','POST'])
def viewtransaction(id):
    tactions = Transactions.query.filter(Transactions.customer_id == id).all()
    product_names = []
    customer_name = [Customers.query.filter_by(id=id).first().first_name,id]
    for transaction in tactions:
        product = Products.query.filter_by(id = transaction.product_id).first()
        product_names.append([product.name,product.price,transaction.id])
    return render_template('viewtransaction.html',products=product_names,customer= customer_name)


@app.route('/deletetransaction/<int:cid>/<int:tid>')
def deletetransaction(cid,tid):
    item = Transactions.query.get(tid)
    db.session.delete(item)
    db.session.commit()
    return redirect('/viewtransaction/'+str(cid))


@app.route('/updatetransaction/<int:cid>/<int:tid>', methods=['GET','POST'])
def updatetransaction(cid,tid):
    item = Transactions.query.get(tid)
    if request.method == 'POST':
        c_id = request.form['customer']
        pid = request.form['product']
        c_id = c_id.split()
        pid = pid.split()
        item.customer_id = c_id[0]
        item.product_id = pid[0]
        db.session.add(item)
        db.session.commit()
        return redirect('/viewtransaction/'+str(cid))
    else:
        customers_id = []
        customers = Customers.query.all()
        for customer in customers:
            customers_id.append(str(customer.id) + " " + customer.first_name)
        products_id = []
        products = Products.query.all()
        for product in products:
            products_id.append(str(product.id) + " " + product.name)
        return render_template('updatetransaction.html',customers = customers_id,products = products_id)


@app.route('/signup', methods=['GET','POST'])
def signup():
    errortext = ""
    if request.method == 'POST':
        texta = request.form['Username']
        textb = request.form['Password']
        if texta == "":
            errortext = "No username inserted"
            return render_template('signup.html', errortext=errortext)
        if textb == "":
            errortext = "No password inserted"
            return render_template('signup.html', errortext=errortext)
        if Users.query.get(texta) is not None:
            errortext = "Username already exists please choose a different name"
            render_template('signup.html', errortext=errortext)
        else:
            new_user = Users(user_name=texta, password=textb)
            db.session.add(new_user)
            db.session.commit()
            errortext = "success"
            return render_template('signup.html', errortext=errortext)
    return render_template('signup.html')


@app.route('/', methods=['GET','POST'])
def index():
    errortext = ""
    if request.method == 'POST':
        texta = request.form['Username']
        textb = request.form['Password']
        if texta == "":
            errortext = "No username inserted"
            return render_template('index.html', errortext=errortext)
        if textb == "":
            errortext = "No password inserted"
            return render_template('index.html', errortext=errortext)
        if errortext == "":
            user = Users.query.get(texta)
            if user is not None:
                if textb == user.password:
                    return redirect('/view/0')
    else:
        return render_template('index.html')


@app.route('/view/<int:error>')
def view(error):
    errortext = ""
    if error == 1:
        errortext = "Can't delete customer that has transactions, please delete transactions first"
    if error == 2:
        errortext = "Can't delete product that has transactions, please delete transactions first"
    customers = Customers.query.all()
    products = Products.query.all()
    return render_template('view.html',customers=customers, products=products, errortext=errortext)


@app.route('/deletecustomer/<int:id>')
def deletecustomer(id):
    if Transactions.query.filter_by(customer_id = id).first() is not None:
        return redirect('/view/1')
    else:
        item = Customers.query.get(id)
        db.session.delete(item)
        db.session.commit()
        return redirect('/view/0')


@app.route('/updatecustomer/<int:id>', methods=['GET','POST'])
def updatecustomer(id):
    item = Customers.query.get(id)
    if request.method == 'POST':
        texta = request.form['fname']
        textb = request.form['sname']
        item.first_name = texta
        item.last_name = textb
        db.session.commit()
        return redirect('/view/0')
    return render_template('updatecustomer.html', customer=item)


@app.route('/updateproduct/<int:id>', methods=['GET','POST'])
def updateproduct(id):
    item = Products.query.get(id)
    if request.method == 'POST':
        texta = request.form['name']
        textb = request.form['price']
        item.name = texta
        item.price = textb
        db.session.commit()
        return redirect('/view/0')
    return render_template('updateproduct.html', product=item)


@app.route('/deleteproduct/<int:id>')
def deleteproduct(id):
    if Transactions.query.filter_by(product_id = id).first() is not None:
        return redirect('/view/2')
    else:
        item = Products.query.get(id)
        db.session.delete(item)
        db.session.commit()
        return redirect('/view/0')


@app.route('/view/<int:error>', methods=['POST'])
def view_post(error):
    str = request.form['submitbutton']
    if str == "product":
        texta = request.form['name']
        textb = request.form['price']
        new_product = Products(name=texta, price=textb)
        db.session.add(new_product)
        db.session.commit()
    if str == "customer":
        texta = request.form['fname']
        textb = request.form['sname']
        new_customer = Customers(first_name=texta, last_name=textb)
        db.session.add(new_customer)
        db.session.commit()
    if str == "transaction":
        cid = request.form['customer']
        pid = request.form['product']
        cid = cid.split()
        pid = pid.split()
        new_transaction = Transactions(customer_id=cid[0], product_id=pid[0])
        db.session.add(new_transaction)
        db.session.commit()
    return redirect('/view/0')


if __name__ == "__main__":
    app.run(host='127.0.0.1',port=8080,debug = True)

