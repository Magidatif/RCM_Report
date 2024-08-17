import json
from pywebio import start_server
from pywebio.input import *
from pywebio.output import *
from pywebio.session import *

# JSON file paths for storing users
REGISTERED_USERS_FILE = 'registered_users.json'
PENDING_USERS_FILE = 'pending_users.json'

# Admin user credentials
admin_credentials = {'username': 'RCM', 'password': 'EHA'}

# Hospital options based on branch
hospital_options = {
    'رئاسة الهيئة': ['اللجنة المركزية برئاسة الهيئة'],
    'جنوب سيناء': ['شرم الشيخ الدولي', 'رأس سدر', 'طابا', 'سانت كاترين', 'الطور', 'فرع جنوب سيناء'],
    'بورسعيد': ['مجمع الشفاء الطبي', 'رمد بورسعيد', 'الحياة', 'النصر', 'السلام', '30 يونيو', 'الزهور', 'فرع بورسعيد'],
    'الاقصر': ['مجمع الاقصر الدولي', 'الكرنك الدولي', 'ايزيس', 'الاطفال', 'حورس', 'طيبة', 'فرع الاقصر'],
    'الاسماعلية': ['مجمع الاسماعلية الطبي', 'مركز 30 يونيو للكلي', 'ابوخليفة', 'فايد', 'القصاصين', 'فرع الاسماعلية'],
    'اسوان': ['اسوان التخصصي', 'المسلة', 'النيل', 'رمد اسوان', 'فرع اسوان'],
    'السويس': ['اللجان الطبية', 'الجراحات الدقيقة', 'الصدر', 'المجمع الطبي بالسويس', 'فرع السويس']
}

# Load users from JSON files
def load_users():
    try:
        with open(REGISTERED_USERS_FILE, 'r') as f:
            registered_users = json.load(f)
    except FileNotFoundError:
        registered_users = {}

    try:
        with open(PENDING_USERS_FILE, 'r') as f:
            pending_users = json.load(f)
    except FileNotFoundError:
        pending_users = {}

    return registered_users, pending_users

# Save users to JSON files
def save_users():
    with open(REGISTERED_USERS_FILE, 'w') as f:
        json.dump(registered_users, f)

    with open(PENDING_USERS_FILE, 'w') as f:
        json.dump(pending_users, f)

registered_users, pending_users = load_users()

def app():
    put_html('''
        <center>
            <h2>Welcome Page</h2>
            <h3>Welcome to the RCM Team!</h3>
            <img src="https://www.medigy.com/offering/24015.JPEG" width=600>
        </center>
    ''')

    # Main action buttons
    actions = [
        {'label': 'Sign Up', 'action': sign_up},
        {'label': 'Login', 'action': login},
        {'label': 'Admin', 'action': manage_users}
    ]
    
    # Display buttons for each action
    put_buttons([action['label'] for action in actions], onclick=[action['action'] for action in actions])

def sign_up():
    # Select branch first
    branch = select("Select Branch", options=list(hospital_options.keys()))
    
    # Select hospital based on the selected branch
    hospital = select("Select Hospital", options=hospital_options[branch])
    
    # Input group for new user registration
    data = input_group("New User Registration", [
        input('User Name', name='username'),
        input('Password', name='password', type=PASSWORD)
    ])
    
    # Store pending user
    pending_users[data['username']] = {'branch': branch, 'hospital': hospital, 'password': data['password']}
    save_users()  # Save users after each signup

    put_text("Request submitted successfully!")
    put_buttons(['Back to Main Page'], onclick=[app])  # Return to main page

def login():
    data = input_group("User Login", [
        input('User Name', name='username'),
        input('Password', name='password', type=PASSWORD)
    ])
    
    # Check login credentials
    if data['username'] in registered_users and registered_users[data['username']]['password'] == data['password']:
        put_success("Login successful!")
        main_page()  # Open the Main Page after successful login
    else:
        put_error("Invalid credentials. Please try again.")
        put_buttons(['Back to Main Page'], onclick=[app])  # Return to main page

def main_page():
    put_html("<h2>Main Page</h2>")
    actions = [
        {'label': 'Branch Report', 'action': branch_report_page},
        {'label': 'Hospital Report', 'action': hospital_report_page},
        #{'label': 'PHC Report', 'action': lambda: put_text("PHC Report is selected.")}
    ]
    
    put_buttons([action['label'] for action in actions], onclick=[action['action'] for action in actions])
    put_buttons(['Logout'], onclick=[app])  # Add a Logout button

def branch_report_page():
    put_html("<h2>Branch Report</h2>")
    buttons = [
        'OP', 'IP', 'Lab', 'Rad',   'Pharmacy', 'B.Rep.', 'Supply&Demand'
    ]
    put_buttons(buttons, onclick=[lambda button=button: put_text(f"{button} selected.") for button in buttons])
    put_buttons(['Back'], onclick=[main_page])  # Add a Back button to return to the main page

def hospital_report_page():
    put_html("<h2>Hospital Report</h2>")
    buttons = [
        'OP', 'IP', 'Operations', 'ICU&Dialysis', 'ER', 
        'Pharmacy', 'Lab', 'Rad', 'H.Rep.', 'Supply&Demand'
    ]
    put_buttons(buttons, onclick=[lambda button=button: put_text(f"{button} selected.") for button in buttons])
    put_buttons(['Back'], onclick=[main_page])  # Add a Back button to return to the main page

def manage_users():
    # Admin authentication
    username = input("Enter admin username:", type=TEXT)
    password = input("Enter admin password:", type=PASSWORD)
    
    if username == admin_credentials['username'] and password == admin_credentials['password']:
        while True:
            action = select("Admin Actions", ["View Pending Users", "Approve User", "Delete User", "Show All Users", "Logout"])
            if action == "View Pending Users":
                if pending_users:
                    # Create a table with masked passwords
                    table_data = [["Username", "Branch", "Hospital", "Password", "Action"]]
                    for user, details in pending_users.items():
                        masked_password = details['password'][0] + '*' * (len(details['password']) - 1)  # Mask password
                        table_data.append([user, details['branch'], details['hospital'], masked_password, 
                                           put_buttons(['Approve', 'Delete'], 
                                                       onclick=[lambda u=user: approve_user(u), lambda u=user: delete_user(u)])])
                    put_table(table_data)
                else:
                    put_text("No pending users.")
            elif action == "Approve User":
                username_to_approve = input("Enter the username to approve:")
                approve_user(username_to_approve)
            elif action == "Delete User":
                username_to_delete = input("Enter the username to delete:")
                delete_user(username_to_delete)
            elif action == "Show All Users":
                if registered_users:
                    # Create a table with all registered users
                    table_data = [["Username", "Branch", "Hospital", "Password"]]
                    for user, details in registered_users.items():
                        table_data.append([user, details['branch'], details['hospital'], details['password']])
                    put_table(table_data)
                else:
                    put_text("No registered users.")
            elif action == "Logout":
                break
    else:
        put_error("Invalid admin credentials.")
    
    put_buttons(['Back to Main Page'], onclick=[app])  # Return to main menu

def approve_user(username):
    if username in pending_users:
        registered_users[username] = pending_users[username]  # Move user to registered
        del pending_users[username]  # Remove from pending
        save_users()  # Save users after approval
        put_text(f'User {username} approved successfully.')
    else:
        put_error("User not found in pending list.")

def delete_user(username):
    if username in pending_users:
        del pending_users[username]
        save_users()  # Save users after deletion
        put_text(f'Pending user {username} deleted successfully.')
    elif username in registered_users:
        del registered_users[username]
        save_users()  # Save users after deletion
        put_text(f'Registered user {username} deleted successfully.')
    else:
        put_error("User not found.")

if __name__ == '__main__':
    start_server(app, port=4567, debug=True)
