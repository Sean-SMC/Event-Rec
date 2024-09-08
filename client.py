import socket
import json
import sys

# Function to send JSON data to the server
def send_json_data(data):
    # Create a socket with IPv4 and TCP
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        # Connect to the server
        client_socket.connect((HOST, PORT))

        # Convert data to JSON string
        json_data = json.dumps(data)

        # Send JSON data to the server
        client_socket.sendall(json_data.encode('utf-8'))
        
        # Receive a message
        message = client_socket.recv(4096)
        print(message.decode('utf-8'))
    finally:
        # Close connection
        client_socket.close()

def print_help():
    print("Usage: python client.py [flags]")
    print("Flags:")
    print("  -h               Show this help menu") #display this help menu, can also ommit al flags and see the menu calling python3 client.py
    print("  -u <user_id>     User ID   (integer)") #flag for user id
    print("  -c <command>     Command   (e.g., search)") # flag for command which is processed by the server to indicate the function it should perform
    print("  -la <latitude>   Latitude  (float)") # simulate current location/lattitude of the client
    print("  -lo <longitude>  Longitude (float)") # simulate current location/longitude of the client
    print("  -r <radius>      Radius    (20km)")# Radius from the location to search events, must have km behind integer
    print("  -li <limit>      Limit     (integer)" )# Number of events to display in the screen, wonky behavior, might be due to the buffer size on the server not being large enough
    print("  -e <email>       Email     (bob@bob.com)") # Email to login / create accounts
    print("  -p <password>    Password  (string)") # Passowrd to login / create accounts
    print("  -t <title>       Title     (string)") # Title of event, bookmark, or general string for fav_sport and team commands
    print("  -d <description> Descript  (string)")# Description of the bookmark
    print("  -s <sport>       sport     (string/list)") #type of sport to search for, can search for multiple "baseball, basketball"
    print("  -f <friend_id>   friend_id (integer)")# friend id, which is just a user id for another person
    print("Required flags per command:")# this displays all the commands and which flags are required to use them. Note: no error checking on invalid types
    print("  -c <search>            -la 38 -lo -122 -r 30km -li 5 -s mlb") # search events
    print("  -c <add_bookmark>      -u 1 -t example_bookmark -d example_description") # add bookmark to database
    print("  -c <remove_bookmark>   -u 1 -t example_bookmark")# remove
    print("  -c <add_like>          -u 1 -t example_title") #button, click the event, add said event to liked list
    print("  -c <remove_like>       -u 1 -t example_title")#remove 
    print("  -c <add_friend>        -u 1 -f 2")# add friend
    print("  -c <remove_friend>     -u 1 -f 2")# remove friend both reqire user_id and friend_id
    print("  -c <display_likes>     -u 4") #display all entries for specified user
    print("  -c <display_bookmarks  -u 4>")#..
    print("  -c <display_friends>   -u 4")#..
    print("  -c <set_team>          -u 4 -t chicago_cubs")# set the fav team for user id using -u and -t flag for title
    print("  -c <set_sport>          -u 4 -t baseball")# same except set sport
    print("  -c <login> -e Emily@yahoo.com -p cheese") # Login to account in database, will faill if user does not exist or password is not correct
    print("  -c <create> -e Emily@yahoo.com -p cheese")# Create accoount, will fail if account already exists
    print("  -c <recommend> -la 38 -lo -122 -u 4")#Recommend event to client, assumes we have its location and user id,
    #example format for the sports type for predicthq to successfully process the search, there are others that i left out such as baseball, basketball, running etc
    print("Sports format ['nba', 'mlb', 'nfl', 'nhl', 'mls','pga', 'ncaa','wwe','nascar','tennis','mma','volleyball','wnba' ,'football']")
    


if __name__ == "__main__":
    # Port number of the server
    PORT = 9000
    # Host
    HOST = 'localhost'
    
    if len(sys.argv) < 2 or sys.argv[1] == '-h':
        print_help()
        sys.exit(0)
    
    # Define available flags and their corresponding variables
    flag_mapping = {
        '-u': 'user_id',
        '-c': 'command',
        '-la': 'latitude',
        '-lo': 'longitude',
        '-r': 'radius',
        '-li': 'limit',
        '-e': 'email',
        '-p': 'password',
        '-t': 'title',
        '-d': 'description',
        '-s': 'sport',
        '-f': 'friend_id',
    }
    
    # Parse command-line arguments
    data = {}
    i = 1  # Start from index 1 to skip the script name
    while i < len(sys.argv):
        arg = sys.argv[i]
        if arg in flag_mapping:
            flag = flag_mapping[arg]
            i += 1
            value = sys.argv[i]
            data[flag] = value
        else:
            print(f"Invalid flag: {arg}")
            sys.exit(1)
        i += 1

    # Send JSON data to the server
    send_json_data(data)
