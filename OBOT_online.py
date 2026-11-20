import streamlit as st
import math
import urllib.parse

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
    {'name': 'Wayne Ellis',      'skill': 1, 'pos': 'Forward'},
    {'name': 'Daryl Irvine',     'skill': 2, 'pos': 'Forward'},
    {'name': 'Kevin Falk',       'skill': 1, 'pos': 'Goalie'},
    {'name': 'Donnie McLean',    'skill': 1, 'pos': 'Goalie'},
    {'name': 'Chris Saley',      'skill': 1, 'pos': 'Goalie'}
]

# --- KEEP-TOGETHER PAIRS ---
KEEP_TOGETHER_PAIRS = [
    ('Dave Snell', 'Wayne Ellis'),
]

# --- FORMATTING FUNCTION ---
def format_team_output(team_name, team_list):
    """
    Creates formatted text output for a team.
    Sorts by Position (Goalie -> Defence -> Forward), then Name.
    """
    output = f"--- {team_name} ---\n"
    output += f"Total Players: {len(team_list)}\n\n"

    # Define custom position order
    pos_order = {'Goalie': 0, 'Defence': 1, 'Forward': 2}
    
    # Sort by custom position order, then alphabetically by name
    sorted_team = sorted(team_list, key=lambda p: (pos_order.get(p['pos'], 3), p['name']))

    for player in sorted_team:
        output += f"  - {player['name']}\n"
    return output + "\n"

# --- BALANCING FUNCTION (FORWARD-FIRST) ---
def generate_balanced_teams(present_players):
    by_name = {p['name']: p for p in present_players}

    team_A = []
    team_B = []
    locked = set()
    remaining = list(present_players)

    def team_skill(t):
        return sum(p['skill'] for p in t)

    def pos_list(t, pos):
        return [p for p in t if p['pos'] == pos]

    def pos_skill(t, pos):
        return sum(p['skill'] for p in t if p['pos'] == pos)

    def skater_count(t):
        return sum(1 for p in t if p['pos'] != 'Goalie')

    # 1. Goalies (1 per team, split evenly based on present goalies)
    goalies = [p for p in remaining if p['pos'] == 'Goalie']
    for i, g in enumerate(goalies):
        if i % 2 == 0:
            team_A.append(g)
        else:
            team_B.append(g)
        remaining.remove(g)

    # 2. Lock Keep-Together Pairs (Alternate target teams A/B across pairs)
    pair_target_team = 'A'
    for a, b in KEEP_TOGETHER_PAIRS:
        if a in by_name and b in by_name:
            p1, p2 = by_name[a], by_name[b]
            target_list = team_A if pair_target_team == 'A' else team_B

            for p in (p1, p2):
                if p in remaining:
                    target_list.append(p)
                    remaining.remove(p)
                    locked.add(p['name'])

            pair_target_team = 'B' if pair_target_team == 'A' else 'A'

    # 3. Balance FORWARDS first (equal forward count, then equalize forward skill)
    forwards = sorted([p for p in remaining if p['pos'] == 'Forward'], key=lambda p: p['skill'], reverse=True)
    locked_fwd_A = len(pos_list(team_A, 'Forward'))
    locked_fwd_B = len(pos_list(team_B, 'Forward'))
    total_fwd = len(forwards) + locked_fwd_A + locked_fwd_B
    target_fwd_A = max(total_fwd // 2, locked_fwd_A)
    target_fwd_B = max(total_fwd - target_fwd_A, locked_fwd_B)

    # Adjust if a locked pair already pushed one side above half
    if locked_fwd_A + locked_fwd_B + len(forwards) == total_fwd:
        if target_fwd_A + target_fwd_B > total_fwd:
            if locked_fwd_A > total_fwd - locked_fwd_A:
                target_fwd_A = locked_fwd_A
                target_fwd_B = total_fwd - target_fwd_A
            else:
                target_fwd_B = locked_fwd_B
                target_fwd_A = total_fwd - target_fwd_B

    for f in forwards:
        fwd_A = len(pos_list(team_A, 'Forward'))
        fwd_B = len(pos_list(team_B, 'Forward'))

        if fwd_A < target_fwd_A and fwd_B < target_fwd_B:
            fwd_skill_A = pos_skill(team_A, 'Forward')
            fwd_skill_B = pos_skill(team_B, 'Forward')
            if fwd_skill_A <= fwd_skill_B:
                team_A.append(f)
            else:
                team_B.append(f)
        elif fwd_A < target_fwd_A:
            team_A.append(f)
        else:
            team_B.append(f)
        remaining.remove(f)

    # Swap pass strictly among unlocked Forwards to equalize Forward skill
    improved = True
    while improved:
        improved = False
        best = None
        cur_fwd_diff = abs(pos_skill(team_A, 'Forward') - pos_skill(team_B, 'Forward'))

        for i, pa in enumerate(team_A):
            if pa['pos'] != 'Forward' or pa['name'] in locked:
                continue
            for j, pb in enumerate(team_B):
                if pb['pos'] != 'Forward' or pb['name'] in locked:
                    continue

                new_fwd_A = pos_skill(team_A, 'Forward') - pa['skill'] + pb['skill']
                new_fwd_B = pos_skill(team_B, 'Forward') - pb['skill'] + pa['skill']
                new_fwd_diff = abs(new_fwd_A - new_fwd_B)

                if new_fwd_diff < cur_fwd_diff:
                    if best is None or new_fwd_diff < best[0]:
                        best = (new_fwd_diff, i, j)

        if best:
            _, i, j = best
            team_A[i], team_B[j] = team_B[j], team_A[i]
            improved = True

    # 4. Balance DEFENCE next (equalize total skater count and overall team skill)
    defences = sorted([p for p in remaining if p['pos'] == 'Defence'], key=lambda p: p['skill'], reverse=True)
    n_skaters = len([p for p in present_players if p['pos'] != 'Goalie'])
    target_skaters_A = max(n_skaters // 2, skater_count(team_A))
    target_skaters_B = n_skaters - target_skaters_A
    if target_skaters_B < skater_count(team_B):
        target_skaters_B = skater_count(team_B)
        target_skaters_A = n_skaters - target_skaters_B

    for d in defences:
        s_A = skater_count(team_A)
        s_B = skater_count(team_B)

        if s_A < target_skaters_A and s_B < target_skaters_B:
            if team_skill(team_A) <= team_skill(team_B):
                team_A.append(d)
            else:
                team_B.append(d)
        elif s_A < target_skaters_A:
            team_A.append(d)
        else:
            team_B.append(d)
        remaining.remove(d)

    # Swap pass strictly among unlocked Defence to equalize overall team skill
    improved = True
    while improved:
        improved = False
        best = None
        cur_diff = abs(team_skill(team_A) - team_skill(team_B))

        for i, pa in enumerate(team_A):
            if pa['pos'] != 'Defence' or pa['name'] in locked:
                continue
            for j, pb in enumerate(team_B):
                if pb['pos'] != 'Defence' or pb['name'] in locked:
                    continue

                new_skill_A = team_skill(team_A) - pa['skill'] + pb['skill']
                new_skill_B = team_skill(team_B) - pb['skill'] + pa['skill']
                new_diff = abs(new_skill_A - new_skill_B)

                if new_diff < cur_diff:
                    if best is None or new_diff < best[0]:
                        best = (new_diff, i, j)

        if best:
            _, i, j = best
            team_A[i], team_B[j] = team_B[j], team_A[i]
            improved = True

    output_A = format_team_output("TEAM A (YELLOW)", team_A)
    output_B = format_team_output("TEAM B (BLACK)", team_B)

    return output_A + output_B

# --- STREAMLIT WEB APP UI ---

st.set_page_config(layout="wide")
st.title("🏒 OBOT Team Builder")

player_vars = {}
# Sort skaters alphabetically first, followed by goalies alphabetically at the bottom
player_list_sorted = sorted(MASTER_PLAYER_LIST, key=lambda p: (p['pos'] == 'Goalie', p['name']))

# --- Select/Deselect All Buttons ---
col1, col2, col3_spacer = st.columns([1, 1, 5])
if col1.button("Select All"):
    for player in player_list_sorted:
        st.session_state[player['name']] = True
    st.rerun()

if col2.button("Deselect All"):
    for player in player_list_sorted:
        st.session_state[player['name']] = False
    st.rerun()

st.header("Select Players Present:", divider="grey")

# --- 3-Column Checkbox Layout ---
num_players = len(player_list_sorted)
num_per_col = math.ceil(num_players / 3)

col1, col2, col3 = st.columns(3)

for i, player in enumerate(player_list_sorted):
    pos_letter = player['pos'][0]
    label = f"{player['name']} ({pos_letter})"

    if player['name'] not in st.session_state:
        st.session_state[player['name']] = False

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

    for player_name, var_is_checked in player_vars.items():
        if var_is_checked:
            for master_player in MASTER_PLAYER_LIST:
                if master_player['name'] == player_name:
                    present_players.append(master_player)
                    break

    if not present_players:
        st.warning("No players selected.")
    elif len(present_players) < 2:
        st.warning("Not enough players to make two teams.")
    else:
        try:
            team_output = generate_balanced_teams(present_players)
            
            st.text_area("Generated Teams:", value=team_output, height=350)

            # --- Export Options ---
            st.subheader("📲 Export Teams")
            
            # 1. SMS / iMessage Direct Link
            encoded_text = urllib.parse.quote(team_output)
            sms_href = f"sms:?&body={encoded_text}"
            st.markdown(f'<a href="{sms_href}" target="_blank"><button style="padding: 10px 20px; font-size:16px; cursor:pointer;">📱 Send Teams via SMS / iMessage</button></a>', unsafe_allow_html=True)

        except Exception as e:
            st.error(f"An error occurred: {e}")
