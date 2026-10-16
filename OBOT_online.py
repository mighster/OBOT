import streamlit as st
import math

# --- YOUR MASTER PLAYER ROSTER (2026-2027) ---
MASTER_PLAYER_LIST = [
    {'name': 'Dave Snell',       'skill': 9, 'pos': 'Forward'},
    {'name': 'Hartley Krulicki', 'skill': 8, 'pos': 'Forward'},
    {'name': 'Martin Windus',    'skill': 7, 'pos': 'Defence'},
    {'name': 'Mike Mancer',      'skill': 7, 'pos': 'Forward'},
    {'name': 'Dean Lewko',       'skill': 6, 'pos': 'Forward'},
    {'name': 'Brent Sadler',     'skill': 5, 'pos': 'Defence'},
    {'name': 'Perry Buydens',    'skill': 6, 'pos': 'Forward'},
    {'name': 'Michael Douglas',  'skill': 6, 'pos': 'Forward'},
    {'name': 'Matt Brykaliuk',   'skill': 6, 'pos': 'Forward'},
    {'name': 'Travis Bosch',     'skill': 7, 'pos': 'Forward'},
    {'name': 'Jody Windsor',     'skill': 4, 'pos': 'Forward'},
    {'name': 'Trevor Boulanger', 'skill': 4, 'pos': 'Defence'},
    {'name': 'Alex Hammond',     'skill': 5, 'pos': 'Forward'},
    {'name': 'Trevor Boulet',    'skill': 4, 'pos': 'Defence'},
    {'name': 'Max Paganelli',    'skill': 4, 'pos': 'Forward'},
    {'name': 'Derek East',       'skill': 5, 'pos': 'Forward'},
    {'name': 'Bryan Reimer',     'skill': 4, 'pos': 'Forward'},
    {'name': 'Tyler Nobiss',     'skill': 4, 'pos': 'Forward'},
    {'name': 'Brent Metcalfe',   'skill': 4, 'pos': 'Forward'},
    {'name': 'Brian Fehr',       'skill': 4, 'pos': 'Defence'},
    {'name': 'Clayton Wood',     'skill': 4, 'pos': 'Defence'},
    {'name': 'Rob Mirrlees',     'skill': 3, 'pos': 'Forward'},
    {'name': 'Ryan Mackie',      'skill': 4, 'pos': 'Forward'},
    {'name': 'Stephen Barlow',   'skill': 4, 'pos': 'Defence'},
    {'name': 'Tanner Dueck',     'skill': 3, 'pos': 'Forward'},
    {'name': 'Colton Bossuyt',   'skill': 4, 'pos': 'Defence'},
    {'name': 'Mark Kaminsky',    'skill': 2, 'pos': 'Defence'},
    {'name': 'Bretton Eisner',   'skill': 4, 'pos': 'Forward'},
    {'name': 'Scot Snow',        'skill': 2, 'pos': 'Defence'},
    {'name': 'Brad Olinyk',      'skill': 3, 'pos': 'Forward'},
    {'name': 'Steve McFarlane',  'skill': 8, 'pos': 'Forward'},
    {'name': 'Wayne Ellis',      'skill': 1, 'pos': 'Defence'},
    {'name': 'Kevin Falk',      'skill': 1, 'pos': 'Goalie'},
    {'name': 'Donnie McLean',     'skill': 1, 'pos': 'Goalie'},
    {'name': 'Chris Saley',      'skill': 1, 'pos': 'Goalie'}
]

# --- KEEP-TOGETHER PAIRS ---
# Players listed here always land on the same team when both are present.
# Add more tuples as needed, e.g. ('John Doe', 'Jane Doe').
KEEP_TOGETHER_PAIRS = [
    ('Dave Snell', 'Wayne Ellis'),
]

# --- FORMATTING FUNCTION (*** MODIFIED ***) ---
def format_team_output(team_name, team_list, team_skill):
    """
    Helper function to create a nicely formatted string for the output.
    MODIFIED:
    1. Removed Total Skill and Avg Skill lines.
    2. Sorts by Position, then alphabetically by Name.
    """
    output = f"--- {team_name} ---\n"
    output += f"Total Players: {len(team_list)}\n\n" # Removed skill lines, added \n

    # Sort by position, then alphabetically by name to mask skill
    team_list.sort(key=lambda p: (p['pos'], p['name']))

    for player in team_list:
        pos_letter = player['pos'][0]
        output += f"  - {player['name']} ({pos_letter})\n"
    return output + "\n"

# --- BALANCING FUNCTION (*** MODIFIED ***) ---
def generate_balanced_teams(present_players):
    """
    MODIFIED:
    1. Nobody is ever cut. Odd turnout means one team carries the extra man.
    2. KEEP_TOGETHER_PAIRS are locked onto the same team before the draft.
    3. Swap pass at the end tightens the skill gap without splitting pairs.
    """
    players = list(present_players)
    by_name = {p['name']: p for p in players}

    team_A = []
    team_B = []
    locked = set()  # keep-together players: placed first, never swapped
    remaining = list(players)

    # Lock keep-together pairs onto Team A
    for a, b in KEEP_TOGETHER_PAIRS:
        if a in by_name and b in by_name:
            for p in (by_name[a], by_name[b]):
                team_A.append(p)
                remaining.remove(p)
                locked.add(p['name'])

    # Even counts, or off by exactly one when turnout is odd. Nobody sits.
    n = len(players)
    target_A = max(n // 2, len(team_A))
    target_B = n - target_A

    def team_skill(t):
        return sum(q['skill'] for q in t)

    # Greedy draft: best remaining player goes to the lower-skill team
    for p in sorted(remaining, key=lambda p: p['skill'], reverse=True):
        if len(team_A) < target_A and len(team_B) < target_B:
            if team_skill(team_A) <= team_skill(team_B):
                team_A.append(p)
            else:
                team_B.append(p)
        elif len(team_A) < target_A:
            team_A.append(p)
        else:
            team_B.append(p)

    # Swap pass: trade unlocked players between teams while it tightens skill
    improved = True
    while improved:
        improved = False
        best = None
        cur_diff = abs(team_skill(team_A) - team_skill(team_B))
        for i, pa in enumerate(team_A):
            if pa['name'] in locked:
                continue
            for j, pb in enumerate(team_B):
                if pb['name'] in locked:
                    continue
                new_diff = abs((team_skill(team_A) - pa['skill'] + pb['skill']) -
                               (team_skill(team_B) - pb['skill'] + pa['skill']))
                if new_diff < cur_diff and (best is None or new_diff < best[0]):
                    best = (new_diff, i, j)
        if best:
            _, i, j = best
            team_A[i], team_B[j] = team_B[j], team_A[i]
            improved = True

    # The team_skill variables are still passed here, but the
    # format_team_output function just ignores them now.
    output_A = format_team_output("TEAM A (WHITE)", team_A, team_skill(team_A))
    output_B = format_team_output("TEAM B (DARK)", team_B, team_skill(team_B))

    return output_A + output_B

# --- STREAMLIT WEB APP UI (Unchanged) ---

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
