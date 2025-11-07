import streamlit as st
import math

# --- YOUR MASTER PLAYER ROSTER (Unchanged) ---
MASTER_PLAYER_LIST = [
    {'name': 'Dave Snell',       'skill': 9, 'pos': 'Forward'},
    {'name': 'Hartley Krulicki', 'skill': 8, 'pos': 'Forward'},
    {'name': 'Martin Windus',    'skill': 7, 'pos': 'Forward'},
    {'name': 'Mike Mancer',      'skill': 7, 'pos': 'Forward'},
    {'name': 'Dean Lewko',       'skill': 6, 'pos': 'Forward'},
    {'name': 'Brent Sadler',     'skill': 6, 'pos': 'Forward'},
    {'name': 'Perry Buydens',    'skill': 6, 'pos': 'Forward'},
    {'name': 'Michael Douglas',  'skill': 6, 'pos': 'Forward'},
    {'name': 'Travis Bosch',     'skill': 6, 'pos': 'Forward'},
    {'name': 'Jody Windsor',     'skill': 5, 'pos': 'Forward'},
    {'name': 'Trevor Boulanger', 'skill': 5, 'pos': 'Defence'},
    {'name': 'Alex Hammond',     'skill': 5, 'pos': 'Forward'},
    {'name': 'Trevor Boulet',    'skill': 5, 'pos': 'Defence'},
    {'name': 'Max Paganelli',    'skill': 5, 'pos': 'Forward'},
    {'name': 'Derek East',       'skill': 5, 'pos': 'Forward'},
    {'name': 'Bryan Reimer',     'skill': 5, 'pos': 'Forward'},
    {'name': 'Tyler Nobiss',     'skill': 5, 'pos': 'Forward'},
    {'name': 'Brent Metcalfe',   'skill': 4, 'pos': 'Forward'},
    {'name': 'Brian Fehr',       'skill': 4, 'pos': 'Defence'},
    {'name': 'Clayton Wood',     'skill': 4, 'pos': 'Defence'},
    {'name': 'Rob Mirrlees',     'skill': 4, 'pos': 'Forward'},
    {'name': 'Ryan Mackie',      'skill': 4, 'pos': 'Forward'},
    {'name': 'Stephen Barlow',   'skill': 4, 'pos': 'Defence'},
    {'name': 'Rob Fleming',      'skill': 4, 'pos': 'Forward'},
    {'name': 'Tanner Dueck',     'skill': 3, 'pos': 'Forward'},
    {'name': 'Colton Bossuyt',   'skill': 3, 'pos': 'Defence'},
    {'name': 'Corey Bossuyt',    'skill': 2, 'pos': 'Defence'},
    {'name': 'Mark Kaminsky',    'skill': 2, 'pos': 'Forward'},
    {'name': 'Bretton Eisner',   'skill': 2, 'pos': 'Forward'},
    {'name': 'Scot Snow',        'skill': 2, 'pos': 'Defence'},
    {'name': 'Kevin Anseeuw',    'skill': 2, 'pos': 'Forward'},
    {'name': 'Syl Precourt',     'skill': 1, 'pos': 'Defence'},
    {'name': 'Wayne Ellis',      'skill': 1, 'pos': 'Defenccmde'},
]

# --- FORMATTING FUNCTION (Unchanged) ---
def format_team_output(team_name, team_list, team_skill):
    output = f"--- {team_name} ---\n"
    output += f"Total Players: {len(team_list)}\n"
    output += f"Total Skill: {team_skill}\n"
    output += f"Avg Skill: {team_skill / len(team_list) if team_list else 0:.2f}\n\n"
    
    team_list.sort(key=lambda p: p['pos'])
    
    for player in team_list:
        pos_letter = player['pos'][0]  
        output += f"  - {player['name']} ({pos_letter})\n"
    return output + "\n"

# --- BALANCING FUNCTION (Unchanged) ---
def generate_balanced_teams(present_players):
    all_sorted = sorted(present_players, key=lambda p: p['skill'], reverse=True)
    
    team_A = []
    team_B = []
    team_A_skill = 0
    team_B_skill = 0
    
    remaining_players = list(all_sorted)
    
    if len(remaining_players) >= 4:
        player1 = remaining_players.pop(0) 
        team_A.append(player1)
        team_A_skill += player1['skill']
        
        player2 = remaining_players.pop(0) 
        team_B.append(player2)
        team_B_skill += player2['skill']

        player_worst1 = remaining_players.pop(-1)
        player_worst2 = remaining_players.pop(-1)
        
        scenario1_A = team_A_skill + player_worst1['skill']
        scenario1_B = team_B_skill + player_worst2['skill']
        diff1 = abs(scenario1_A - scenario1_B)
        
        scenario2_A = team_A_skill + player_worst2['skill']
        scenario2_B = team_B_skill + player_worst1['skill']
        diff2 = abs(scenario2_A - scenario2_B)
        
        if diff1 <= diff2:
            team_A.append(player_worst1)
            team_A_skill = scenario1_A
            team_B.append(player_worst2)
            team_B_skill = scenario1_B
        else:
            team_A.append(player_worst2)
            team_A_skill = scenario2_A
            team_B.append(player_worst1)
            team_B_skill = scenario2_B

    for player in remaining_players:
        if team_A_skill <= team_B_skill:
            team_A.append(player)
            team_A_skill += player['skill']
        else:
            team_B.append(player)
            team_B_skill += player['skill']
            
    output_A = format_team_output("TEAM A (WHITE)", team_A, team_A_skill)
    output_B = format_team_output("TEAM B (DARK)", team_B, team_B_skill)
    
    return output_A + output_B

# --- STREAMLIT WEB APP UI ---

# Set page to be wide
st.set_page_config(layout="wide")

st.title("🏒 OBOT Team Builder")

# This dictionary will hold the state of the checkboxes
player_vars = {}

# Sort master list alphabetically for the GUI
player_list_sorted = sorted(MASTER_PLAYER_LIST, key=lambda p: p['name'])

# --- Select/Deselect All Buttons ---
col1, col2, col3_spacer = st.columns([1, 1, 5])
if col1.button("Select All"):
    for player in player_list_sorted:
        st.session_state[player['name']] = True # Use session_state to store selections

if col2.button("Deselect All"):
    for player in player_list_sorted:
        st.session_state[player['name']] = False

st.header("Select Players Present:", divider="grey")

# --- 3-Column Checkbox Layout ---
num_players = len(player_list_sorted)
num_per_col = math.ceil(num_players / 3)

col1, col2, col3 = st.columns(3)

# Populate the columns with checkboxes
for i, player in enumerate(player_list_sorted):
    # Get first letter of position
    pos_letter = player['pos'][0]
    label = f"{player['name']} ({pos_letter})"
    
    # Use st.session_state to make selections "stick"
    if player['name'] not in st.session_state:
        st.session_state[player['name']] = False
    
    # Place in 3-column grid
    if i < num_per_col:
        player_vars[player['name']] = col1.checkbox(label, key=player['name'])
    elif i < num_per_col * 2:
        player_vars[player['name']] = col2.checkbox(label, key=player['name'])
    else:
        player_vars[player['name']] = col3.checkbox(label, key=player['name'])

st.divider()

# --- Generate Button and Output ---
if st.button("Generate Teams", type="primary", use_container_width=True):
    present_players = []
    
    # Find which checkboxes are ticked from the state
    for player_name, var_is_checked in player_vars.items():
        if var_is_checked:
            # Find the full player-dict from the master list
            for master_player in MASTER_PLAYER_LIST:
                if master_player['name'] == player_name:
                    present_players.append(master_player)
                    break
                    
    if not present_players:
        team_output = "No players selected."
    elif len(present_players) < 2:
        team_output = "Not enough players to make two teams."
    else:
        try:
            team_output = generate_balanced_teams(present_players)
        except Exception as e:
            team_output = f"An error occurred: {e}"

    # Display the output in a text box
    st.text(team_output)