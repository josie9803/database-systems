from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import text
import time, datetime

app = Flask(__name__)
# Update the below configuration with your existing PostgreSQL database details
psql_user = 'postgres'
psql_password = ''
db_name = 'pits'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://{}:{}@localhost/{}'.format(psql_user, psql_password, db_name)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

@app.route('/')
def index():
    # Execute a raw SQL query directly
    connection = db.engine.raw_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM Stock WHERE sym = 'AAPL';")
    query_result = cursor.fetchall()
    if len(query_result) > 0:
        res = query_result[0]
    else:
        res = []
    return jsonify(res)

# @app.route('/')
# def index():
#     """
#         an alternative implementation of the index() function
#         with query parameter and placeholder
#     """
#     res = []
#     with db.engine.begin() as conn:
#         query_result = conn.execute(text("SELECT * FROM Stock WHERE sym = :sym ;"), 
#                                     dict(sym='AAPL'))
#         for sym, price in query_result:
#             res.append([sym, price])
#     return jsonify(res[0])

@app.route('/getOwner')
def getOwner():
    """
        This HTTP method takes aid as input, and returns all owner's pid in a list
        If the account does not exist, return [{'pid': -1}]
    """
    # complete the function by replacing the line below with your code
    aid = int(request.args.get('aid', -1))
    connection = db.engine.raw_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT o.pid FROM Owns o WHERE o.aid = %s;", (aid,))
    query_result = cursor.fetchall()
    if len(query_result) > 0:
        res = [{'pid': int(row[0])} for row in query_result]
    else:
        res = [{'pid': -1}]
    return jsonify(res)

@app.route('/getHoldings')
def getHoldings():
    """
        This HTTP method takes aid and sym as input, 
        and returns the total share of holdings for a stock sym of an account
        If the stock does not exist or the account does not exist, return {'shares': -1};
        If the account does not hold any share of the stock, return {'shares': 0} -> USE COALESCE
        DO NOT USE the view you create in P1
    """
    aid = int(request.args.get('aid', -1))
    sym = request.args.get('sym', '')
    # complete the function by replacing the line below with your code
    connection = db.engine.raw_connection()
    cursor = connection.cursor()

    if not check_account_exists(cursor, aid) or not check_stock_exists(cursor, sym):
        return jsonify({'shares': -1})
    shares = getHoldings(cursor, aid, sym)
    return jsonify({'shares': shares})

def currentTime():
    ts = time.time()
    return datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')

def getHoldings(cursor, aid, sym):
    cursor.execute("select coalesce(sum(CASE WHEN t.type = 'buy' THEN shares " 
                "WHEN t.type = 'sell' THEN -shares END),0) AS total_shares "
                "from trade t where t.aid = %s and t.sym = %s;"
                , (aid,sym))
    return cursor.fetchall()[0][0]

def check_oversell(cursor, aid, sym, shares):
    return getHoldings(cursor, aid, sym) >= shares

def check_account_exists(cursor, aid):
    cursor.execute("SELECT COUNT(*) FROM Account WHERE aid = %s;", (aid,))
    return cursor.fetchone()[0] > 0

def check_stock_exists(cursor, sym):
    cursor.execute("SELECT COUNT(*) FROM Stock WHERE sym = %s;", (sym,))
    return cursor.fetchone()[0] > 0

def check_validate_type(type):
    return type in ['buy', 'sell']

@app.route('/trade')
def trade():
    """
        This HTTP method takes the information of a trade as input: aid, sym, type, shares, price 
        You need to retrieve the current maximum seq numer (max_seq) for aid and 
        then insert with max_seq+1 and the current timestamp.
        It returns {'res' : 'fail'} if there is an oversell or other errors like aid/sym/type does not exist;
        Otherwise, it returns {'res': the current seq} and also updates the database accordingly.
        You should implement the check of the violation in the Python function 
        and DO NOT use the view you implemented in P1.
        You will need to finish a multi statement transaction in this function.
        
        Ideally, you need to send a HTTP POST request for such editing requests, 
        but we just choose GET for easier test
    """
    aid = int(request.args.get('aid', -1))
    sym = request.args.get('sym', '')
    type = request.args.get('type', '')
    shares = float(request.args.get('shares', -1))
    price = float(request.args.get('price', -1))

    connection = db.engine.raw_connection()
    cursor = connection.cursor()

    # complete the function by replacing the line below with your code
    cursor.execute("BEGIN;")
    response = {"res": "fail"}

    if check_account_exists(cursor, aid) and check_stock_exists(cursor, sym) and check_validate_type(type):
    # You need to retrieve the current maximum seq numer (max_seq) for aid and 
    #     then insert with max_seq+1 and the current timestamp.
        if type == 'sell':
            if not check_oversell(cursor, aid, sym, shares):
                cursor.execute("ROLLBACK;")
                return jsonify(response)
    
        cursor.execute("SELECT COALESCE(MAX(seq), 0) FROM Trade WHERE aid = %s;", (aid,))
        max_seq = cursor.fetchone()[0]
        new_seq = max_seq + 1
    #INSERT
        cursor.execute("INSERT INTO Trade (aid, seq, type, timestamp, sym, shares, price) "
        "VALUES (%s, %s, %s, %s, %s, %s, %s);"
        , (aid, new_seq, type, currentTime(), sym, shares, price))
        cursor.execute("COMMIT;")
        response = {"res": new_seq}
    else:
        cursor.execute("ROLLBACK;")  

    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=7000)
