import sqlite3
import getpass


class User:
    def __init__(self, id, name, balance, password):
        self.id = id
        self.name = name
        self.balance = balance
        self.password = password


class BankSystem:
    def __init__(self):
        self.conn = sqlite3.connect('bank.db')
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                balance REAL NOT NULL,
                password TEXT NOT NULL
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                type TEXT,
                amount REAL,
                date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')
        self.conn.commit()

    def create_user(self):
        name = input("Enter your name: ")
        balance = float(input("Enter your initial balance: "))
        password = getpass.getpass("Enter your password: ")

        self.cursor.execute('INSERT INTO users (name, balance, password) VALUES (?, ?, ?)', (name, balance, password))
        self.conn.commit()
        print("User created successfully!")

    def login(self):
        name = input("Enter your name: ")
        password = getpass.getpass("Enter your password: ")

        self.cursor.execute('SELECT * FROM users WHERE name=? AND password=?', (name, password))
        user = self.cursor.fetchone()

        if user:
            print("Login successful!")
            return User(user[0], user[1], user[2], user[3])
        else:
            print("Invalid credentials!")
            return None

    def deposit(self, user):
        amount = float(input("Enter amount to deposit: "))
        user.balance += amount

        self.cursor.execute('UPDATE users SET balance=? WHERE id=?', (user.balance, user.id))
        self.cursor.execute('INSERT INTO transactions (user_id, type, amount) VALUES (?, ?, ?)',
                            (user.id, 'deposit', amount))
        self.conn.commit()
        print(f"Deposited {amount} successfully!")

    def withdraw(self, user):
        amount = float(input("Enter amount to withdraw: "))
        if amount > user.balance:
            print("Insufficient funds!")
        else:
            user.balance -= amount
            self.cursor.execute('UPDATE users SET balance=? WHERE id=?', (user.balance, user.id))
            self.cursor.execute('INSERT INTO transactions (user_id, type, amount) VALUES (?, ?, ?)',
                                (user.id, 'withdraw', amount))
            self.conn.commit()
            print(f"Withdrew {amount} successfully!")

    def view_balance(self, user):
        print(f"Your balance is {user.balance}")

    def view_history(self, user):
        self.cursor.execute('SELECT type, amount, date FROM transactions WHERE user_id=?', (user.id,))
        transactions = self.cursor.fetchall()

        print("Transaction History:")
        for transaction in transactions:
            print(f"Type: {transaction[0]}, Amount: {transaction[1]}, Date: {transaction[2]}")

    def main_menu(self):
        while True:
            choice = input("Do you want to login or create a new user? (login/create): ")
            if choice.lower() == "login":
                user = self.login()
                if user:
                    break
            elif choice.lower() == "create":
                self.create_user()
            else:
                print("Invalid choice. Please try again.")

        while True:
            print("\nOptions:")
            print("[1] View Balance")
            print("[2] Deposit")
            print("[3] Withdraw")
            print("[4] View History")
            print("[5] Exit")

            choice = int(input("Enter your choice: "))

            if choice == 1:
                self.view_balance(user)
            elif choice == 2:
                self.deposit(user)
            elif choice == 3:
                self.withdraw(user)
            elif choice == 4:
                self.view_history(user)
            elif choice == 5:
                print("Goodbye!")
                break
            else:
                print("Invalid choice. Please try again.")


if __name__ == "__main__":
    bank_system = BankSystem()
    bank_system.main_menu()
