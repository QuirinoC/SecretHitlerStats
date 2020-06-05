import os
from sys import argv
from glob import glob
from pprint import pprint
import re


def atoi(text):
    return int(text) if text.isdigit() else text


def natural_keys(text):
    '''
    alist.sort(key=natural_keys) sorts in human order
    http://nedbatchelder.com/blog/200712/human_sorting.html
    (See Toothy's implementation in the comments)
    '''
    return [atoi(c) for c in re.split(r'(\d+)', text)]


def get_games(html):
    with open(html) as file:
        messages = file.read()
        lines = messages.split('\n')

    games = []

    for idx, line in enumerate(lines):
        if 'win by' in line:
            games.append(line)
    return games


def get_all_games(path):
    html_files = glob(path)

    html_files.sort(key=natural_keys)
    html_files = [html_files[-1]] + html_files[:-1]
    games = []

    for html in html_files:
        games.extend(get_games(html))

    return games


def get_winners(result):
    return result.split(' ')[3]


def parse_player(player):
    player = player[:-3]
    if player[-1] == '(dead)':
        player = player[:-1]
    player = ' '.join(player)
    player = player[:-7]
    return player


def get_role(player):
    *player, role = player.split(' ')
    role = role.lower()
    player = parse_player(player)
    return player, role


def parse_game(game):
    lines = game.split('<br>')
    result, *players = lines
    players = players[1:]

    winners = get_winners(result)

    results = []

    for player in players:
        name, role = get_role(player)

        results.append(
            [name, role, winners]
        )

    return results


def get_full_results(games):
    full_results = []

    for game in games:
        full_results.extend(
            parse_game(game)
        )

    return full_results


def build_player_data(full_results):
    player_data = {}

    for result in full_results:
        name, role, winners = result
        party = 'liberals' if role == 'liberal' else 'fascists'
        player_data[name] = player_data.get(
            name, []) + [{'role': role, 'party': party, 'winners': winners}]

    return player_data


def print_stats(player_data):
    for player, games in player_data.items():
        games_played = len(games)
        win_count = 0
        for game in games:
            if game['party'] == game['winners']:
                win_count += 1

        print(
            f'{player}:\n  Games played: {games_played}\n  Win rate: {round(win_count / games_played * 100, 2)}%\n')


# Main code

# Get only the messages with results


if __name__ == '__main__':

    path = argv[1]
    limit = int(argv[2])
    games = get_all_games(path+'/*.html')

    # Get the results of the games
    full_results = get_full_results(games)

    # Build player data as a dict
    player_data = build_player_data(full_results)

    for player, games in player_data.items():
        player_data[player] = games[-limit:]

    # player_data['Javier'].extend(player_data['José'])
    # player_data['Javier'].extend(player_data['Quirino'])
    #del player_data['Quirino']
    #del player_data['José']
    print_stats(player_data)
