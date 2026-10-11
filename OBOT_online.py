# --- BALANCING FUNCTION (Unchanged) ---
def generate_balanced_teams(present_players):
    players = list(present_players)
    cut_player = None

    # Even bodies only: cut the lowest-skilled player when odd
    if len(players) % 2 == 1:
        players.sort(key=lambda p: p['skill'])
        cut_player = players.pop(0)

    all_sorted = sorted(players, key=lambda p: p['skill'], reverse=True)
    target = len(all_sorted) // 2

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
        # Keep counts even: fill whichever team is short first
        if len(team_A) >= target:
            team_B.append(player)
            team_B_skill += player['skill']
        elif len(team_B) >= target:
            team_A.append(player)
            team_A_skill += player['skill']
        elif team_A_skill <= team_B_skill:
            team_A.append(player)
            team_A_skill += player['skill']
        else:
            team_B.append(player)
            team_B_skill += player['skill']

    output_A = format_team_output("TEAM A (WHITE)", team_A, team_A_skill)
    output_B = format_team_output("TEAM B (DARK)", team_B, team_B_skill)
    output = output_A + output_B

    if cut_player:
        output += f"\nCut (odd man out): {cut_player['name']}\n"

    return output