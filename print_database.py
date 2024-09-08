import sqlite3

def print_table(table_name):
    try:
        # Connect to the database
        with sqlite3.connect("users.db") as conn:
            # Create cursor
            cur = conn.cursor()
            
            # Fetch all rows from the specified table
            cur.execute(f"SELECT * FROM {table_name}")
            rows = cur.fetchall()
            
            # Print the table name
            print(f"Contents of table '{table_name}':")
            
            # Print the rows
            for row in rows:
                print(row)
    except sqlite3.Error as e:
        print(f"An error occurred while fetching data from table '{table_name}': {e}")

def print_all_tables():
    # Print contents of all tables
    print_table("users")
    print_table("friends")
    print_table("bookmarks")
    print_table("likes")

if __name__ == "__main__":
    print_all_tables()