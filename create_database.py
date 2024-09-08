import sqlite3
import random

# Connect to a new database
conn = sqlite3.connect("users.db")

# Create cursor
cur = conn.cursor()

# Create tables if they don't exist
cur.execute('''CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE,
                password TEXT,
                 fav_team TEXT,
                fav_sport TEXT
            )''')

cur.execute('''CREATE TABLE IF NOT EXISTS bookmarks (
                bookmark_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                title TEXT,
                description TEXT,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )''')

cur.execute('''CREATE TABLE IF NOT EXISTS friends (
                user_id INTEGER,
                friend_id INTEGER,
                PRIMARY KEY (user_id, friend_id),
                FOREIGN KEY (user_id) REFERENCES users(user_id),
                FOREIGN KEY (friend_id) REFERENCES users(user_id)
            )''')

cur.execute('''CREATE TABLE IF NOT EXISTS likes (
    user_id INTEGER,
    title TEXT
)''')

# Commit changes to the database
conn.commit()

# Populate users table with test data
test_accounts = [
    ("123@hotmail.com", "Watson","Youth Basketball", "tennis"),
    ("test@gmail.com", "test", "Oakland Athletics", "football"),
    ("example@aol.com", "aol", "Los Angeles Dodgers", "soccer"),
    ("waldo@google.com", "horse", "Youth Basketball", "basketball"),
    ("james@yahoo.con", "bird", "Chicago White Sox", "baseball"),
    ("mason@yahoo.con", "dog", "Cardinals", "running"),
    # Add more test accounts here
]

for email, password, fav_team, fav_sport in test_accounts:
    cur.execute("INSERT INTO users (email, password, fav_team, fav_sport) VALUES (?, ?, ?, ?)", (email, password, fav_team, fav_sport))

# Populate bookmarks table with test data
for user_id in range(1, len(test_accounts) + 1):
    # Generate random number of bookmarks for each user
    num_bookmarks = random.randint(1, 5)
    for _ in range(num_bookmarks):
        title = f"Example Bookmark Title {random.randint(1, 100)}"
        description = f"Example bookmark description for user {user_id}"
        cur.execute("INSERT INTO bookmarks (user_id, title, description) VALUES (?, ?, ?)", (user_id, title, description))

# Populate friends table with test data (random connections between users)
num_users = len(test_accounts)
for user_id in range(1, num_users + 1):
    # Generate random number of friends for each user (up to half of the total users)
    num_friends = random.randint(0, num_users // 2)
    friend_ids = random.sample(range(1, num_users + 1), num_friends)
    for friend_id in friend_ids:
        if friend_id != user_id:
            cur.execute("INSERT INTO friends (user_id, friend_id) VALUES (?, ?)", (user_id, friend_id))
            
            
#Populate likes for users
num_users = len(test_accounts)
for user_id in range(1,num_users+1):
    num_likes = random.randint(1,5)
    for _ in range(num_likes):
        likes = f"Example Liked Event {random.randint(1,100)}"
        cur.execute("INSERT INTO likes (user_id, title) VALUES (?,?)", (user_id, likes))
        
    

# Commit changes to the database
conn.commit()

print("Table Generated")
# Close database connection
conn.close()
