from flask import Flask, render_template, request, redirect, url_for, flash
import cx_Oracle

app = Flask(__name__)
app.secret_key = '3d74f8a9d9f99ac7fc35c9dcca283175'

# Oracle DB config
DB_USERNAME = "system"
DB_PASSWORD = "system"
DB_DSN = cx_Oracle.makedsn("localhost", 1521, service_name="XE")

@app.route("/")
def home():
    return render_template("home.html")


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        user_id = request.form['user_id']
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        phone = request.form['phone']
        address = request.form['address']
        try:
            conn = cx_Oracle.connect(user=DB_USERNAME, password=DB_PASSWORD, dsn=DB_DSN)
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO users (user_id, username, email, password, phone_number, address)
                VALUES (:1, :2, :3, :4, :5, :6)
            """, (user_id, username, email, password, phone, address))
            conn.commit()
            flash("✅ Registration successful!", "success")
            return redirect(url_for('home'))

        except Exception as e:
            flash(f"❌ Error: {e}", "danger")

        finally:
            cursor.close()
            conn.close()

    return render_template("register.html")


@app.route('/create_account', methods=['GET', 'POST'])
def create_account():
    if request.method == 'POST':
        aid = request.form['account_id']
        uid = request.form['user_id']
        try:
            conn = cx_Oracle.connect(user=DB_USERNAME, password=DB_PASSWORD, dsn=DB_DSN)
            cursor = conn.cursor()

            cursor.execute(
                "INSERT INTO accounts (account_id, user_id, balance) VALUES (:1, :2, 0)",
                (aid, uid)
            )
            conn.commit()
            flash("✅ Account created successfully!", "success")
            return redirect(url_for('home'))

        except cx_Oracle.IntegrityError as e:
            error_msg = str(e)
            if 'ORA-00001' in error_msg:
                flash("❌ Account ID already exists!", "danger")
            elif 'ORA-02291' in error_msg:
                flash("❌ User ID does not exist!", "danger")
            else:
                flash(f"❌ Error: {error_msg}", "danger")

        except Exception as e:
            flash(f"❌ Unexpected error: {str(e)}", "danger")

        finally:
            cursor.close()
            conn.close()

    return render_template('create_account.html')


@app.route('/deposit', methods=['GET', 'POST'])
def deposit():
    if request.method == 'POST':
        account_id = request.form['account_id']
        amount = request.form['amount']

        try:
            amount = float(amount)

            conn = cx_Oracle.connect(user=DB_USERNAME, password=DB_PASSWORD, dsn=DB_DSN)
            cursor = conn.cursor()

            cursor.execute("SELECT * FROM accounts WHERE account_id = :id", {'id': account_id})
            account = cursor.fetchone()

            if not account:
                flash('❌ Account ID not found.', 'error')
            else:
                cursor.execute("""
                    UPDATE accounts
                    SET balance = balance + :amt
                    WHERE account_id = :id
                """, {'amt': amount, 'id': account_id})

                cursor.execute("""
                    INSERT INTO transactions (transaction_id, account_id, amount, type)
                    VALUES (transactions_seq.NEXTVAL, :id, :amt, 'deposit')
                """, {'id': account_id, 'amt': amount})

                conn.commit()
                flash('✅ Deposit successful!', 'success')

        except Exception as e:
            flash(f"❌ Error: {str(e)}", 'error')

        finally:
            cursor.close()
            conn.close()

    return render_template('deposit.html')


@app.route('/withdraw', methods=['GET', 'POST'])
def withdraw():
    if request.method == 'POST':
        account_id = request.form['account_id']
        amount = request.form['amount']

        try:
            amount = float(amount)

            conn = cx_Oracle.connect(user=DB_USERNAME, password=DB_PASSWORD, dsn=DB_DSN)
            cursor = conn.cursor()

            cursor.execute("SELECT balance FROM accounts WHERE account_id = :1", (account_id,))
            row = cursor.fetchone()

            if row is None:
                flash("❌ Account not found.", "error")
            elif row[0] < amount:
                flash("❌ Insufficient balance.", "error")
            else:
                new_balance = row[0] - amount
                cursor.execute("UPDATE accounts SET balance = :1 WHERE account_id = :2", (new_balance, account_id))

                cursor.execute("""
                    INSERT INTO transactions (transaction_id, account_id, amount, type)
                    VALUES (transactions_seq.NEXTVAL, :id, :amt, 'withdraw')
                """, {'id': account_id, 'amt': amount})

                conn.commit()
                flash("✅ Withdrawal successful!", "success")

        except Exception as e:
            flash(f"❌ Error: {e}", "error")

        finally:
            cursor.close()
            conn.close()

    return render_template("withdraw.html")


@app.route('/balance', methods=['GET', 'POST'])
def balance():
    balance = None

    if request.method == 'POST':
        account_id = request.form['account_id']

        try:
            conn = cx_Oracle.connect(DB_USERNAME, DB_PASSWORD, DB_DSN)
            cursor = conn.cursor()

            cursor.execute("SELECT balance FROM accounts WHERE account_id = :id", {'id': account_id})

            result = cursor.fetchone()

            if result:
                balance = result[0]
            else:
                flash("Account ID not found.", "error")

            cursor.close()
            conn.close()
        except Exception as e:
            flash(f"Error: {str(e)}", "error")

    return render_template('balance.html', balance=balance)



if __name__ == "__main__":
    app.run(debug=True)
