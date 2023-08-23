from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import mysql.connector
import re
import datetime

app = Flask(__name__, template_folder='templates')

app.secret_key = 'your_secret_key'

mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Nandy*001",
    database="nammakadai",
    auth_plugin="mysql_native_password"
)

smt = mydb.cursor(prepared=True)
@app.route('/')
@app.route('/index',methods=['GET','POST'])
def index():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        smt.execute('SELECT * FROM customers WHERE username = %s AND password = %s',(username,password, ))
        account = smt.fetchone()
        if account:
            session['loggedin'] = True
            session['id'] = account[0]
            session['username'] = account[1]
            balance = account[4]
            val = balance
            return render_template('firstpage.html',val=val)
        else:
            msg = 'Incorrect username / password !'
    return render_template('index.html',msg = msg)

@app.route('/register',methods=['GET','POST'])
def register():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        amount = request.form['amount']
        smt.execute('SELECT * FROM customers WHERE username = %s',(username,))
        account = smt.fetchone()
        if account:
            msg = 'Account already exits !'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address !'
        elif not re.match(r'[A-Za-z0-9]+',username):
            msg = 'Username must contain only characters and numbers !'
        elif not username or not password or not email:
            msg = 'Please fill out the form !'
        else:
            smt.execute('INSERT INTO customers VALUES (NULL ,%s,%s,%s,%s)',(username,password,email,amount,))
            mydb.commit()
            msg = 'You have successfully registered !'
    elif request.method == 'POST':
        msg = 'Please fill out the form !'
    return render_template('register.html',msg=msg)


@app.route('/purchase',methods=['GET','POST'])
def purchase():
    return render_template('purchase.html')

@app.route('/showproduct',methods=['GET','POST'])
def showproduct():
    username = session.get('username','Guest')
    smt.execute("SELECT * FROM item WHERE username = %s",(username,))
    data = smt.fetchall()
    return render_template('purchase.html',data=data)

@app.route('/additems',methods=['GET','POST'])
def additems():
    item_name = request.form['item_name']
    price = request.form['price']
    quantity = request.form['quantity']
    username = session.get('username','Guest')
    # smt.execute('SELECT quantity FROM item WHERE username = %s AND item_name = %s',(username,item_name,))
    # account = smt.fetchone()
    # exqty = account[0]
    # exqty = int(exqty)
    # if exqty > 1:
    #     exqty = exqty + int(quantity)
    #     smt.execute('UPDATE item SET quantity = %s WHERE username = %s AND item_name = %s',(exqty,username,item_name,))
    #     mydb.commit()
    # else:
    smt.execute('INSERT INTO item VALUES (NULL,%s,%s,%s,%s)',(item_name,price,username,quantity,))
    mydb.commit()
    val = "Item Inserted Successfully"
    return render_template('purchase.html',val=val)

@app.route('/purches',methods=['GET','POST'])
def purches():
    username = session.get('username','Guest')
    item_name = request.form['item_name']
    no_of_prod = request.form['qty']
    time = datetime.datetime.now()
    smt.execute('SELECT price , quantity , item_name  FROM item WHERE item_name = %s AND username = %s',(item_name,username,))
    account = smt.fetchone()
    try:
        rate = account[0]
        exqty = account[1]
        exqty = int(exqty)
        no_of_prod = int(no_of_prod)
        amt = int(no_of_prod)*int(rate)
        smt.execute('INSERT INTO purchase VALUES (NULL,%s,%s,%s,%s,%s,%s)',(time,no_of_prod,rate,amt,item_name,username,))
        mydb.commit()
        val = "Item Purchased Successfully"
        smt.execute('SELECT * FROM customers WHERE username = %s',(username,))
        account = smt.fetchone()
        balance = account[4]
        bal = int(balance)-amt
        smt.execute('UPDATE customers SET balance = %s WHERE username = %s',(bal,username,))
        mydb.commit()
        currqty = exqty+no_of_prod
        smt.execute('UPDATE item SET quantity = %s WHERE item_name = %s AND username = %s',(currqty,item_name,username,))
        mydb.commit()
        return render_template('purchase.html',val=val)
    except Exception as e:
        val = "Invalid Item"
        return render_template('purchase.html',val=val)


@app.route('/sellingpage',methods=['GET','POST'])
def sellingpage():
    return render_template('sellingpage.html')

@app.route('/sales',methods=['GET','POST'])
def sales():
    username = session.get('username','Guest')
    item_name = request.form['item_name']
    no_of_prod = request.form['qty']
    no_of_prod = int(no_of_prod)
    time = datetime.datetime.now()
    smt.execute('SELECT price , quantity FROM item WHERE item_name = %s AND username = %s',(item_name,username,))
    account = smt.fetchone()
    rate = account[0]
    rate = int(rate)*2
    exqty = account[1]
    exqty = int(exqty)
    amt = int(no_of_prod)*int(rate)
    if exqty < no_of_prod:
        val = "Quantity Insufficient !!! "
        return render_template('sellingpage.html',val=val)
    smt.execute('INSERT INTO sales VALUES (NULL,%s,%s,%s,%s,%s,%s)',(time,no_of_prod,rate,amt,item_name,username,))
    mydb.commit()
    smt.execute('SELECT * FROM customers WHERE username = %s',(username,))
    account = smt.fetchone()
    balance = account[4]
    bal = int(balance)+amt
    smt.execute('UPDATE customers SET balance = %s WHERE username = %s',(bal,username,))
    mydb.commit()
    currqty = exqty-no_of_prod
    smt.execute('UPDATE item SET quantity = %s WHERE item_name = %s AND username = %s',(currqty,item_name,username,))
    mydb.commit()
    val = "Item Sold Successfully"
    return render_template('sellingpage.html',val=val)

@app.route('/showproducts',methods=['GET','POST'])
def showproducts():
    username = session.get('username','Guest')
    smt.execute("SELECT * FROM item WHERE username = %s",(username,))
    data = smt.fetchall()
    processed_data=[]
    for row in data:
        t_data = (row[0],row[1],int(row[2])*2,row[3],row[4])
        processed_data.append(t_data)
    return render_template('sellingpage.html',data=processed_data)

@app.route('/historypage',methods=['GET','POST'])
def historypage():
    username = session.get('username','Guest')
    smt.execute('SELECT * FROM customers WHERE username = %s',(username,))
    account = smt.fetchone()
    balance = account[4]
    return render_template('historypage.html',val=balance)

@app.route('/purchasehistory',methods=['GET','POST'])
def purchasehistory():
    username = session.get('username','Guest')
    smt.execute("SELECT * FROM purchase WHERE username = %s",(username,))
    data = smt.fetchall()
    smt.execute('SELECT * FROM customers WHERE username = %s',(username,))
    account = smt.fetchone()
    balance = account[4]
    return render_template('historypage.html',data=data,val=balance)

@app.route('/saleshistory',methods=['GET','POST'])
def saleshistory():
    username = session.get('username','Guest')
    smt.execute("SELECT * FROM sales WHERE username = %s",(username,))
    data = smt.fetchall()
    smt.execute('SELECT * FROM customers WHERE username = %s',(username,))
    account = smt.fetchone()
    balance = account[4]
    return render_template('historypage.html',data=data,val=balance)

# @app.route('/buypage',methods=['GET','POST'])
# def buypage():
#     return render_template('buypage.html')

# @app.route('/salepage',methods=['GET','POST'])
# def salepage():
#     return render_template('salepage.html')

# @app.route('/pen',methods=['GET','POST'])
# def pen():
#     if request.method == 'POST':
#         prd_count = request.form['Pen_Count']
#         prd_count = int(prd_count)
#         username = session.get('username','Guest')
#         smt.execute('SELECT * FROM customers WHERE username = %s',(username,))
#         account = smt.fetchone()
#         balance = account[4]
#         bal = int(balance)-(prd_count*50) 
#         smt.execute("UPDATE customers SET balance = %s WHERE username = %s",(bal,username,))
#         mydb.commit()
#         msg = "Succesfully Purchased"
#         print(bal)
#         return render_template('index.html',msg=msg)
    
# @app.route('/pencil',methods=['GET','POST'])
# def pencil():
#     if request.method == 'POST':
#         prd_count = request.form['P_Count']
#         prd_count = int(prd_count)
#         username = session.get('username','Guest')
#         smt.execute('SELECT * FROM customers WHERE username = %s',(username,))
#         account = smt.fetchone()
#         balance = account[4]
#         bal = int(balance)-(prd_count*20) 
#         smt.execute("UPDATE customers SET balance = %s WHERE username = %s",(bal,username,))
#         mydb.commit()
#         msg = "Succesfully Purchased"
#         print(bal)
#         return render_template('index.html',msg=msg)
    
# @app.route('/Gbox',methods=['GET','POST'])
# def Gbox():
#     if request.method == 'POST':
#         prd_count = request.form['G_Count']
#         prd_count = int(prd_count)
#         username = session.get('username','Guest')
#         smt.execute('SELECT * FROM customers WHERE username = %s',(username,))
#         account = smt.fetchone()
#         balance = account[4]
#         bal = int(balance)-(prd_count*100) 
#         smt.execute("UPDATE customers SET balance = %s WHERE username = %s",(bal,username,))
#         mydb.commit()
#         msg = "Succesfully Purchased"
#         print(bal)
#         return render_template('index.html',msg=msg)
    
# @app.route('/Sharp',methods=['GET','POST'])
# def Sharp():
#     if request.method == 'POST':
#         prd_count = request.form['S_Count']
#         prd_count = int(prd_count)
#         username = session.get('username','Guest')
#         smt.execute('SELECT * FROM customers WHERE username = %s',(username,))
#         account = smt.fetchone()
#         balance = account[4]
#         bal = int(balance)-(prd_count*10) 
#         smt.execute("UPDATE customers SET balance = %s WHERE username = %s",(bal,username,))
#         mydb.commit()
#         msg = "Succesfully Purchased"
#         print(bal)
#         return render_template('index.html',msg=msg)
    
# @app.route('/Eraser',methods=['GET','POST'])
# def Eraser():
#     if request.method == 'POST':
#         prd_count = request.form['E_Count']
#         prd_count = int(prd_count)
#         username = session.get('username','Guest')
#         smt.execute('SELECT * FROM customers WHERE username = %s',(username,))
#         account = smt.fetchone()
#         balance = account[4]
#         bal = int(balance)-(prd_count*5) 
#         smt.execute("UPDATE customers SET balance = %s WHERE username = %s",(bal,username,))
#         mydb.commit()
#         msg = "Succesfully Purchased"
#         print(bal)
#         return render_template('index.html',msg=msg)
    

# @app.route('/pens',methods=['GET','POST'])
# def pens():
#     if request.method == 'POST':
#         prd_count = request.form['Pen_Count']
#         prd_count = int(prd_count)
#         username = session.get('username','Guest')
#         smt.execute('SELECT * FROM customers WHERE username = %s',(username,))
#         account = smt.fetchone()
#         balance = account[4]
#         bal = int(balance)+(prd_count*100) 
#         smt.execute("UPDATE customers SET balance = %s WHERE username = %s",(bal,username,))
#         mydb.commit()
#         msg = "Succesfully Purchased"
#         print(bal)
#         return render_template('index.html',msg=msg)
    
# @app.route('/pencils',methods=['GET','POST'])
# def pencils():
#     if request.method == 'POST':
#         prd_count = request.form['P_Count']
#         prd_count = int(prd_count)
#         username = session.get('username','Guest')
#         smt.execute('SELECT * FROM customers WHERE username = %s',(username,))
#         account = smt.fetchone()
#         balance = account[4]
#         bal = int(balance)+(prd_count*40) 
#         smt.execute("UPDATE customers SET balance = %s WHERE username = %s",(bal,username,))
#         mydb.commit()
#         msg = "Succesfully Purchased"
#         print(bal)
#         return render_template('index.html',msg=msg)
    
# @app.route('/Gboxs',methods=['GET','POST'])
# def Gboxs():
#     if request.method == 'POST':
#         prd_count = request.form['G_Count']
#         prd_count = int(prd_count)
#         username = session.get('username','Guest')
#         smt.execute('SELECT * FROM customers WHERE username = %s',(username,))
#         account = smt.fetchone()
#         balance = account[4]
#         bal = int(balance)+(prd_count*200) 
#         smt.execute("UPDATE customers SET balance = %s WHERE username = %s",(bal,username,))
#         mydb.commit()
#         msg = "Succesfully Purchased"
#         print(bal)
#         return render_template('index.html',msg=msg)
    
# @app.route('/Sharps',methods=['GET','POST'])
# def Sharps():
#     if request.method == 'POST':
#         prd_count = request.form['S_Count']
#         prd_count = int(prd_count)
#         username = session.get('username','Guest')
#         smt.execute('SELECT * FROM customers WHERE username = %s',(username,))
#         account = smt.fetchone()
#         balance = account[4]
#         bal = int(balance)+(prd_count*20) 
#         smt.execute("UPDATE customers SET balance = %s WHERE username = %s",(bal,username,))
#         mydb.commit()
#         msg = "Succesfully Purchased"
#         print(bal)
#         return render_template('index.html',msg=msg)
    
# @app.route('/Erasers',methods=['GET','POST'])
# def Erasers():
#     if request.method == 'POST':
#         prd_count = request.form['E_Count']
#         prd_count = int(prd_count)
#         username = session.get('username','Guest')
#         smt.execute('SELECT * FROM customers WHERE username = %s',(username,))
#         account = smt.fetchone()
#         balance = account[4]
#         bal = int(balance)+(prd_count*10) 
#         smt.execute("UPDATE customers SET balance = %s WHERE username = %s",(bal,username,))
#         mydb.commit()
#         msg = "Succesfully Purchased"
#         print(bal)
#         return render_template('index.html',msg=msg)


if __name__ == '__main__':
    app.run(debug=True)