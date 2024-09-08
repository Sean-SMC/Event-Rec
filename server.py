import socket
import sqlite3
import requests
import sys 
import json
from datetime import datetime, timedelta

#port number of machine
PORT = 9000
HOST = 'localhost'

# Define API key and base URL
API_KEY = 'yFRy9lxCITAb_SiVV0W-9QoJstTUywycxzg0SsKH'  
BASE_URL = 'https://api.predicthq.com/v1/events/'
sportsdb_base_url = "https://www.thesportsdb.com/api/v1/json/3"

def insert_bookmark(user_id, title, description):
    try:
        # Connect to the database
        with sqlite3.connect("users.db") as conn:
            
            cur = conn.cursor()

            # Check if the user exists
            cur.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
            existing_user = cur.fetchone()
            
            if not existing_user:
                message = f"User with ID '{user_id}' does not exist. Bookmark insertion failed."
                return {
                    'status': "fail",
                    'message': message,
                }
            
            # Insert bookmark for the user
            cur.execute("INSERT INTO bookmarks (user_id, title, description) VALUES (?, ?, ?)",
                        (user_id, title, description))
            conn.commit()  # Commit the transaction
            
            message = f"Bookmark '{title}' inserted successfully for user with ID '{user_id}'"
            return {
                'status': "success",
                'message': message,
            }
    
    except sqlite3.Error as e:
        message = f"An error occurred while inserting the bookmark: {e}"
        return {
            'status': "fail",
            'message': message,
        }

def remove_bookmark(user_id, title):
    try:
        # Connect to the database
        conn = sqlite3.connect("users.db")
        cur = conn.cursor()
        
        # Check if the user exists
        cur.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
        existing_user = cur.fetchone()
        
        if not existing_user:
            return {
                'status': "fail",
                'message': f"User with ID '{user_id}' does not exist. Bookmark removal failed.",
            }
        
        # Check if the bookmark exists for the user
        cur.execute("SELECT * FROM bookmarks WHERE user_id=? AND title=?", (user_id, title))
        existing_bookmark = cur.fetchone()
        
        if not existing_bookmark:
            return {
                'status': "fail",
                'message': f"Bookmark '{title}' does not exist for user with ID '{user_id}'. Bookmark removal failed.",
            }
        
        # Remove the bookmark for the user
        cur.execute("DELETE FROM bookmarks WHERE user_id=? AND title=?", (user_id, title))
        conn.commit()  # Commit the transaction
        
        return {
            'status': "success",
            'message': f"Bookmark '{title}' removed successfully for user with ID '{user_id}'",
        }
    
    except sqlite3.Error as e:
        return {
            'status': "fail",
            'message': f"An error occurred while removing the bookmark: {e}",
        }
    
    finally:
        # Close the connection
        conn.close()
             
#grab sports data within a certain radius from a certain position
def get_sports_events(latitude, longitude, radius, limit, sport):
    
    #define parameters for the api request
    

    #date from when we make the request,
    today = datetime.now().strftime('%Y-%m-%d')
    #days ahead that we will look for events, set to 90 days
    end_date = (datetime.now() + timedelta(days=90)).strftime('%Y-%m-%d')
 
    # Define a list of major sports labels
    #major_sports_labels = ['nba', 'mlb', 'nfl', 'nhl', 'mls','pga', 'ncaa','wwe','nascar','tennis','mma','volleyball','wnba']
    
    # Convert the list to a comma-separated string for the API parameter
    #major_sports_labels_str = ','.join(major_sports_labels)



    # API parameters
    user_params = {
        'category': 'sports',
        'within': f'{radius}@{latitude},{longitude}',
        'start': today,
        'end': end_date,
        'duplicates': 'ignore',  # Specify how to handle duplicates,
        'label': sport,
        'limit': limit,
    }
    user_headers = {
        'Authorization': f'Bearer {API_KEY}',
    }
    
    #send get request to the predicthq api
    response = requests.get(BASE_URL, params=user_params, headers = user_headers)
    
    #check if request was successful
    if response.status_code == 200:
        data = response.json()
        events = data.get('results', [])
        
         # Filter out events with the same title on the same day
        unique_events = []
        titles_dates = set()
        for event in events:
            title = event['title']
            start_date = event['start'].split('T')[0]  # Extract only the date part
            if (title, start_date) not in titles_dates:
                unique_events.append(event)
                titles_dates.add((title, start_date))
                
        data = {'status': "success",
                'message': unique_events,
                }
        return unique_events
    else:
        data = {'status':"fail",
                'message': "Failed to retrieve events",}
        #print(f"Failed to retrieve events. Status code: {response.status_code}")
        return data
    
    #return the list of events from predict hq
    
def return_events(events, radius):
    data = {'status': "success", 'events': []}
    
    if events:
        data['message'] = f"Sports events within {radius} km radius:"
        
        for event in events:
            event_title = event['title']
            start_time = event['start']
            end_time = event['end']
            description = event['description']
            label = event['labels']
            country = event['country']  # Corrected to get the country from the event
            
            event_data = {
                'Title': event_title,
                'Start Time': start_time,
                'End Time': end_time,
                'Description': description,
                'Image': get_event_details_from_sportsdb(event_title),
                'Label': label,
                'Country': country,
                'Entities': [],
            }

            # Extract entities information
            entities = event.get('entities', [])
            if entities:
                for entity in entities:
                    entity_type = entity.get('type', 'Unknown Type')
                    entity_name = entity.get('name', 'Unknown Name')
                    formatted_address = entity.get('formatted_address', 'Unknown Address')
                    event_data['Entities'].append({
                        'Type': entity_type,
                        'Name': entity_name,
                        'Address': formatted_address,
                    })

            data['events'].append(event_data)
    else:
        data['status'] = "fail"
        data['message'] = "No events found."
    
    return data

def get_event_details_from_sportsdb(event_title):
    response = requests.get(f"{sportsdb_base_url}/searchevents.php?e={event_title}")
    
    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        data = response.json()
        events = data.get("event", [])
        if events:
            # Ensure there are events before accessing the first one
            first_event = events[0]
            return first_event.get("strThumb", None)
        else:
            print("No Images found")
            return None
    else:
        print(f"Failed to retrieve data from theSportsDB API. Status code: {response.status_code}")
        return None


def add_friend(user_id, friend_id):
    # Connect to the database
    conn = sqlite3.connect("users.db")
    cur = conn.cursor()
    
    # Check if both user and friend exist
    cur.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    existing_user = cur.fetchone()
    cur.execute("SELECT * FROM users WHERE user_id=?", (friend_id,))
    existing_friend = cur.fetchone()
    
    if not existing_user:
        return {
            'status': "fail",
            'message': f"User with ID '{user_id}' does not exist. Add friend failed.",
        }
    
    if not existing_friend:
        return {
            'status': "fail",
            'message': f"User with ID '{friend_id}' does not exist. Add friend failed.",
        }
    
    # Check if they are already friends
    cur.execute("SELECT * FROM friends WHERE user_id=? AND friend_id=?", (user_id, friend_id))
    existing_relationship = cur.fetchone()
    
    if existing_relationship:
        return {
            'status': "fail",
            'message': f"Users '{user_id}' and '{friend_id}' are already friends.",
        }
    
    # Check if they are already friends in reverse direction
    cur.execute("SELECT * FROM friends WHERE user_id=? AND friend_id=?", (friend_id, user_id))
    reverse_relationship = cur.fetchone()
    
    if reverse_relationship:
        return {
            'status': "fail",
            'message': f"Users '{friend_id}' and '{user_id}' are already friends.",
        }
        
    # Insert friendship into the table
    cur.execute("INSERT INTO friends (user_id, friend_id) VALUES (?, ?)", (user_id, friend_id))
    conn.commit()
    
    message = f"Friend '{friend_id}' successfully added to user '{user_id}'"
    
    return {
        'status': "success",
        'message': message,
    }

def remove_friend(user_id, friend_id):
    # Connect to the database
    conn = sqlite3.connect("users.db")
    cur = conn.cursor()
    
    # Check if both user and friend exist
    cur.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    existing_user = cur.fetchone()
    cur.execute("SELECT * FROM users WHERE user_id=?", (friend_id,))
    existing_friend = cur.fetchone()
    
    if not existing_user:
        return {
            'status': "fail",
            'message': f"User with ID '{user_id}' does not exist. Remove friend failed.",
        }
    
    if not existing_friend:
        return {
            'status': "fail",
            'message': f"User with ID '{friend_id}' does not exist. Remove friend failed.",
        }
    
    # Check if they are friends
    cur.execute("SELECT * FROM friends WHERE (user_id=? AND friend_id=?) OR (user_id=? AND friend_id=?)", 
                (user_id, friend_id, friend_id, user_id))
    existing_relationship = cur.fetchone()
    
    if not existing_relationship:
        return {
            'status': "fail",
            'message': f"Users '{user_id}' and '{friend_id}' are not friends. Remove friend failed.",
        }
        
    # Remove friendship from the table
    cur.execute("DELETE FROM friends WHERE (user_id=? AND friend_id=?) OR (user_id=? AND friend_id=?)", 
                (user_id, friend_id, friend_id, user_id))
    conn.commit()
    
    message = f"Friendship between '{user_id}' and '{friend_id}' successfully removed."
    
    return {
        'status': "success",
        'message': message,
    }
    
def add_like(user_id, title):
    # Connect to the database
    conn = sqlite3.connect("users.db")
    cur = conn.cursor()
    
    # Check if user exists
    cur.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    existing_user = cur.fetchone()
    
    if not existing_user:
        return {
            'status': "fail",
            'message': f"User with ID '{user_id}' does not exist. Add like failed.",
        }
    
    # Check if the like already exists for the user
    cur.execute("SELECT * FROM likes WHERE user_id=? AND title=?", (user_id, title))
    existing_like = cur.fetchone()
    
    if existing_like:
        return {
            'status': "fail",
            'message': f"User '{user_id}' already likes '{title}'. Add like failed.",
        }
        
    # Insert like into the table
    cur.execute("INSERT INTO likes (user_id, title) VALUES (?, ?)", (user_id, title))
    conn.commit()
    
    message = f"Like '{title}' successfully added for user '{user_id}'"
    
    return {
        'status': "success",
        'message': message,
    }

def remove_like(user_id, title):
    # Connect to the database
    conn = sqlite3.connect("users.db")
    cur = conn.cursor()
    
    # Check if user exists
    cur.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    existing_user = cur.fetchone()
    
    if not existing_user:
        return {
            'status': "fail",
            'message': f"User with ID '{user_id}' does not exist. Remove like failed.",
        }
    
    # Check if the like exists for the user
    cur.execute("SELECT * FROM likes WHERE user_id=? AND title=?", (user_id, title))
    existing_like = cur.fetchone()
    
    if not existing_like:
        return {
            'status': "fail",
            'message': f"User '{user_id}' does not like '{title}'. Remove like failed.",
        }
        
    # Remove like from the table
    cur.execute("DELETE FROM likes WHERE user_id=? AND title=?", (user_id, title))
    conn.commit()
    
    message = f"Like '{title}' successfully removed for user '{user_id}'"
    
    return {
        'status': "success",
        'message': message,
    }
def login(email, password):
    # Connect to the database
    conn = sqlite3.connect("users.db")
    
    # Create a cursor
    cur = conn.cursor()
    
    # Validate user credentials using a parameterized query
    statement = "SELECT user_id, email FROM users WHERE email=? AND password=?"
    cur.execute(statement, (email, password))
    
    # Fetch the result
    user = cur.fetchone()
    
    # Check if the user exists
    if user:
        user_id, email = user
        #print(f"Welcome {email} (UserID: {user_id})")
        
        data = {
        'user_id': user_id,
        'status': "success",
        'message': f"Welcome {email} (UserID: {user_id})",
    }
        return data
    else:
        data = {
            'status': "fail",
            'message': "Unsucessful login attempt",
        }
        return data
    
    # Close the cursor and connection
    cur.close()
    conn.close()

 #create user account
def create_account(email, password):
    try:
        # Connect to the database
        with sqlite3.connect("users.db") as conn:
            # Create cursor
            cur = conn.cursor()
            
            # Check if the email already exists in the database
            cur.execute("SELECT * FROM users WHERE email=?", (email,))
            existing_user = cur.fetchone()
            
            if existing_user:
                #print(f"User with email '{email}' already exists. Account creation failed.")
                
                data = {
                    'status':"fail",
                    'message': f"User with email '{email}' already exists. Account creation failed.",
                }
                return data
            else:
                # Insert new user into the database with auto-generated UserID
                cur.execute("INSERT INTO users (email, password) VALUES (?, ?)", (email, password))
                conn.commit()  # Commit the transaction
                #print(f"Account created successfully for {email}")
                
                # Retrieve the UserID of the newly created user
                cur.execute("SELECT last_insert_rowid()")
                new_user_id = cur.fetchone()[0]
                
                data = {
                    'user_id': new_user_id,
                    'status': "success",
                    'message': f"Account created successfully for {email}",
                }
                
                return data
    except sqlite3.Error as e:
        # Raise an exception to indicate the failure
        raise RuntimeError(f"An error occurred while creating the account: {e}")

# Function to display bookmarks for a specific user_id
def display_bookmarks(user_id):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    # Check if user exists
    cursor.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    existing_user = cursor.fetchone()
    
    if not existing_user:
        return {
            'status': "fail",
            'message': f"User with ID '{user_id}' does not exist. Display bookmarks failed.",
            'bookmarks': []
        }
    
    # Retrieve bookmarks for the user
    cursor.execute("SELECT * FROM bookmarks WHERE user_id=?", (user_id,))
    bookmarks = cursor.fetchall()

    return {
        'status': "success",
        'message': f"Bookmarks for user '{user_id}' retrieved successfully.",
        'bookmarks': bookmarks
    }

# Function to display likes for a specific user_id
def display_likes(user_id):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    # Check if user exists
    cursor.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    existing_user = cursor.fetchone()
    
    if not existing_user:
        return {
            'status': "fail",
            'message': f"User with ID '{user_id}' does not exist. Display likes failed.",
            'likes': []
        }
    
    # Retrieve likes for the user
    cursor.execute("SELECT * FROM likes WHERE user_id=?", (user_id,))
    likes = cursor.fetchall()

    return {
        'status': "success",
        'message': f"Likes for user '{user_id}' retrieved successfully.",
        'likes': likes
    }

# Function to display friends for a specific user_id
def display_friends(user_id):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    # Check if user exists
    cursor.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    existing_user = cursor.fetchone()
    
    if not existing_user:
        return {
            'status': "fail",
            'message': f"User with ID '{user_id}' does not exist. Display friends failed.",
            'friends': []
        }
    
    # Retrieve friends for the user (user_id, friend_id)
    cursor.execute("SELECT user_id, friend_id FROM friends WHERE user_id=?", (user_id,))
    friends_1 = cursor.fetchall()

    # Retrieve friends for the user (friend_id, user_id)
    cursor.execute("SELECT friend_id, user_id FROM friends WHERE friend_id=?", (user_id,))
    friends_2 = cursor.fetchall()

    # Combine the two lists of friends
    friends = friends_1 + friends_2

    return {
        'status': "success",
        'message': f"Friends for user '{user_id}' retrieved successfully.",
        'friends': friends
    }
    
def set_fav_team(user_id, new_fav_team):
    # Connect to the database
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    
    # Check if user exists
    cursor.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    existing_user = cursor.fetchone()
    
    if not existing_user:
        return {
            'status': "fail",
            'message': f"User with ID '{user_id}' does not exist."
        }

    # Update the user's favorite team
    cursor.execute("UPDATE users SET fav_team=? WHERE user_id=?", (new_fav_team, user_id))
    conn.commit()
    
    return {
        'status': "success",
        'message': f"Favorite team for user '{user_id}' set to '{new_fav_team}' successfully."
    }

def set_fav_sport(user_id, new_fav_sport):
    # Connect to the database
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    
    # Check if user exists
    cursor.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    existing_user = cursor.fetchone()
    
    if not existing_user:
        return {
            'status': "fail",
            'message': f"User with ID '{user_id}' does not exist."
        }

    # Update the user's favorite sport
    cursor.execute("UPDATE users SET fav_sport=? WHERE user_id=?", (new_fav_sport, user_id))
    conn.commit()
    
    return {
        'status': "success",
        'message': f"Favorite sport for user '{user_id}' set to '{new_fav_sport}' successfully."
    }

def handle_command(data):
    # Extract data fron json that we may potentially need
# Extract data from the dictionary
    user_id = data.get('user_id')
    command = data.get('command')
    latitude = data.get('latitude')
    longitude = data.get('longitude')
    email = data.get('email')
    password = data.get('password')
    radius = data.get('radius')
    limit = data.get('limit')
    status = data.get('status')
    message = data.get('message')
    title = data.get('title')
    description = data.get('description')
    sport = data.get('sport')
    friend_id = data.get('friend_id')
    
    data_from_function = None
    # Handle the received command
    if  command:
        print(f"Received command '{command}'")
        
        # Call the appropriate function based on the command       
        if command == 'login':
            if email and password:
                data_from_function = login(email, password)
            else:
                data_from_function = "Invalid arguments for this command"
        if command == 'create':
            if email and password:
                data_from_function = create_account(email, password)
            else:
                data_from_function = "Invalid arguments for this command"
                
        if command == 'search':
            if latitude and longitude and radius and limit and sport:
                events = get_sports_events(latitude, longitude, radius, limit, sport)
                data_from_function = return_events(events, radius)
            else:
                data_from_function = "Invalid arguments for this command"
          
        if command == 'add_bookmark':
             if user_id and title and description:
                data_from_function = insert_bookmark(user_id, title, description)
             else:
                data_from_function = "Invalid arguments for this command"
            
        if command == 'remove_bookmark':
            if user_id and title:
                data_from_function = remove_bookmark(user_id, title)
            else:
                data_from_function = "Invalid arguments for this command"
        
        if command == 'add_friend':
            if user_id and friend_id:
                data_from_function = add_friend(user_id, friend_id)
            else:
                data_from_function = "Invalid arguments for this command"
            
        if command == 'remove_friend':
            if user_id and friend_id:
                data_from_function = remove_friend(user_id, friend_id)
            else:
                data_from_function = "Invalid arguments for this command"
        
        if command == 'add_like':
            if user_id and title:
                data_from_function = add_like(user_id, title)
            else:
                data_from_function = "Invalid arguments for this command"
            
        if command == 'remove_like':
            if user_id and title:
                data_from_function = remove_like(user_id, title)
            else:
                data_from_function = "Invalid arguments for this command"
              
        if command == 'display_likes':
            if user_id:
                data_from_function = display_likes(user_id)
            else:
                data_from_function = "Invalid arguments for this command"
              
        if command == 'display_friends':
            if user_id:
                data_from_function = display_friends(user_id)
            else:
                data_from_function = "Invalid arguments for this command"
              
        if command == 'display_bookmarks':
            if user_id:
                data_from_function = display_bookmarks(user_id)
            else:
                data_from_function = "Invalid arguments for this command"
                
        if command == 'set_team':
            if user_id and title:
                data_from_function = set_fav_team(user_id, title)
            else:
                data_from_function = "Invalid arguments for this command"
                
        if command == 'set_sport':
            if user_id and title:
                data_from_function = set_fav_sport(user_id, title)
            else:
                data_from_function = "Invalid arguments for this command"
                
        if command == 'recommend':
            if user_id and latitude and longitude:
                data_from_function = recommend_events(latitude, longitude, user_id)
            else:
                data_from_function = "Invalid arguments for this command"
        
        return data_from_function   
    
def create_server():
  # Create the socket using IPv4 and TCP
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Bind the socket
    server_socket.bind((HOST, PORT))
    # Listen for up to 5 simultaneous connections
    server_socket.listen(5)
    print("Server is listening...")

    try:
        # While server is running
        while True:
            # Save the incoming connection from the client to a variable
            client_socket, address = server_socket.accept()
            # Print connection status
            print(f"Connection established from address {address}")

            # Receive JSON data from the client
            json_data = client_socket.recv(4096)
            data_to_send = None

            # If there is a command, parse and run the command
            if json_data:
                try:
                    # Decode the received JSON data and parse it
                    data = json.loads(json_data.decode('utf-8'))
                    print(data)
                    # Extract user ID and command from the parsed data
                    user_id = data.get('user_id')
                    command_to_run = data.get('command')

                    # If there is a command to run, handle it
                    if command_to_run:
                        data_to_send = handle_command(data)
                    else:
                        print("No command to run in the received data")
                except json.JSONDecodeError as e:
                    print(f"Error decoding JSON data: {e}")
            else:
                print("No data received from client")
            
            # If there is data from our command, send it to the client
            if data_to_send:
                json_data = json.dumps(data_to_send)
                client_socket.sendall(json_data.encode('utf-8'))

            # Close connection with the client
            client_socket.close()
    except KeyboardInterrupt:
        print("Server shutting down...")
    finally:
        server_socket.close()
def main():
    radius_user = 0
    limit_user = 0
    # Check if the correct number of arguments are provided
    if len(sys.argv) != 5:
        print("Usage: python script.py latitude longitude radius limit")
        return

    # Parse longitude and latitude from command-line arguments
    try:
        longitude = float(sys.argv[2])
        latitude = float(sys.argv[1])
        radius_user = (sys.argv[3])
        limit_user = int(sys.argv[4])
    except ValueError:
        print("Error: Longitude and latitude must be numeric values")
        return
    
    print("Longitude:", longitude)
    print("Latitude:", latitude)
    print("Limit", limit_user)
    print("radius", radius_user)
    print("")

    # offset by one since the input starts at 0
    events = get_sports_events(latitude, longitude,radius_user,limit_user+1)
    return_events(events, radius_user)
    #create_account("test@test.com", "test")
    #login("test@test.com", "test")
    
import sqlite3

def get_all_friend_ids(user_id):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    # Retrieve friends for the user (user_id, friend_id)
    cursor.execute("SELECT user_id, friend_id FROM friends WHERE user_id=?", (user_id,))
    friends_1 = cursor.fetchall()

    # Retrieve friends for the user (friend_id, user_id)
    cursor.execute("SELECT friend_id, user_id FROM friends WHERE friend_id=?", (user_id,))
    friends_2 = cursor.fetchall()

    # Combine the two lists of friends
    friends = friends_1 + friends_2

    # Extract friend IDs
    friend_ids = set()
    for friend_pair in friends:
        # Add both user_id and friend_id to ensure all friends are included
        if friend_pair[0] != user_id:  # Exclude the user's own ID
            friend_ids.add(friend_pair[0])
        if friend_pair[1] != user_id:  # Exclude the user's own ID
            friend_ids.add(friend_pair[1])
    return list(friend_ids)

def get_user_preferences(user_id):
    # Connect to the database
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    # Retrieve friends' IDs
    friend_ids = get_all_friend_ids(user_id)

    # Execute a query to fetch user preferences
    cursor.execute("SELECT fav_team, fav_sport FROM users WHERE user_id = ?", (user_id,))
    user_preferences = cursor.fetchone()
    
    # Fetch preferences for friends
    friends_preferences = []
    for friend_id in friend_ids:
        if friend_id != user_id:  # Skip the user's own ID
            cursor.execute("SELECT fav_team, fav_sport FROM users WHERE user_id = ?", (friend_id,))
            friend_preference = cursor.fetchone()
            if friend_preference:
                friends_preferences.append(friend_preference)

    # Close the connection
    conn.close()
    return user_preferences, friends_preferences

def recommend_events(latitude, longitude, user_id):
    radius = "50km"
    # Retrieve user preferences and friends' preferences from the database
    user_preferences, friends_preferences = get_user_preferences(user_id)
    if user_preferences is None:
        print("User preferences not found.")
        return None

    fav_team, fav_sport = user_preferences

    # API parameters
    user_params = {
        'category': 'sports',
        'within': f'{radius}@{latitude},{longitude}',
        'duplicates': 'ignore',  # Specify how to handle duplicates,
    }
    user_headers = {
        'Authorization': f'Bearer {API_KEY}',
    }
    
    # Send get request to the predicthq api
    response = requests.get(BASE_URL, params=user_params, headers=user_headers)
    
    # Check if the request was successful
    if response.status_code == 200:
        # Parse and process the response JSON
        events_data = response.json()["results"]
        
        # Rank events based on relevance 
        ranked_events = []
        for event in events_data:
            # Calculate relevance score
            relevance_score = 0
            # Check if event title or labels contain the user's favorite team or sport
            if fav_sport in event["title"] or fav_sport in event["labels"]:
                relevance_score += 1
            if fav_team in event["title"] or fav_team in event["labels"]:
                relevance_score += 1
            
            # Add relevance score for user's preferences
            for friend_preference in friends_preferences:
                friend_fav_team, friend_fav_sport = friend_preference
                if friend_fav_team in event["title"] or friend_fav_team in event["labels"]:
                    relevance_score += 0.5
                if friend_fav_sport in event["title"] or friend_fav_sport in event["labels"]:
                    relevance_score += 0.5
            
            # Add ranking score to event data
            event["rank"] = relevance_score
            
            ranked_events.append(event)
        
        # Sort events by ranking score
        ranked_events.sort(key=lambda x: x["rank"], reverse=True)
        
        # Return the event with the highest rank as JSON
        if ranked_events:
            highest_rank_event = ranked_events[0]
            event_data = {
                "status": "Success",
                "event": {
                    "Title": highest_rank_event["title"],
                    "Rank Score": highest_rank_event["rank"],
                    "Labels": highest_rank_event.get("labels", []),
                    "Entities": highest_rank_event.get("entities", [])
                }
            }
            return event_data
        else:
            print("No events found.")
            return {"status": "No events found."}
    
    else:
        print("Failed to retrieve events:", response.status_code)
        return None
if __name__ == "__main__":
    #main()
    create_server()
    
    #recommend_events(38,-122, 2)
    #recommend_events(38,-122, 5)
    
    #recommend_events(38,-90.2, 1)
    #recommend_events(38,-90.2, 3)
    #recommend_events(38, -122, 4)

# create connection to the database
# Example usage:
#latitude = 37.7749  # Example latitude (San Francisco)
#longitude = -122.4194  # Example longitude (San Francisco)
# 38.7114952, -90.3086675
#events = get_sports_events(latitude, longitude)
#return_events(events)

