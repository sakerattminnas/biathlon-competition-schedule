import datetime as dt
import os
import re
import time
from operator import itemgetter

import biathlonresults as br

import json
from util import (current_season_id, competition_type_from_race_id,
                  CompetitionType, date_x_days_ago, logger, FLAGS,
                  RESULT_STATUS, is_relay)


def get_season_from_id(_id: str) -> str:
    """Extract season ID from an event or race ID.

    :param _id: An event or race ID.
    :return: The season ID.
    """
    match = re.search(r'\d{4}', _id)
    if not match:
        raise ValueError(f'Could not extract season ID from {_id}')
    return match.group()


def get_event_filename(season: str) -> str:
    """Get file path for the given seasons events.

    :param season: The season ID.
    :type season: str
    :return: Path to the events json-file.
    :rtype: str
    """
    return 'json/{}/events.json'.format(season)


def get_race_filename(event_id: str) -> str:
    """Get file path for the given events races.

    :param event_id: The event ID.
    :type event_id: str
    :return: Path to races json-file.
    :rtype: str
    """
    season = get_season_from_id(event_id)
    return 'json/{}/{}/races.json'.format(season, event_id)


def get_result_filename(race_id: str) -> str:
    """Get file path for the given seasons events.

    :return: Path to the events json-file.
    """
    season = get_season_from_id(race_id)
    event_id = race_id[:-4]
    return 'json/{}/{}/{}/results.json'.format(
        season, event_id, race_id[-4:])


def _fetch_events(season=current_season_id()) -> None:
    """Fetch events from api and save in json file."""
    filename = get_event_filename(season)
    evs = br.events(season, level=br.consts.LevelType.BMW_IBU_WC)
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    file = open(filename, 'w')
    json.dump(evs, file)


def get_events(season=current_season_id()) -> list[dict]:
    """Get events from json file. If the json-file for the events does not
     exist, fetch events, then get them from the created file.

    :param season: The season ID.
    :type season: str
    :return: A list of events.
    :rtype: list[dict]
    """
    try:
        file = open(get_event_filename(season), 'r')
        return json.load(file)
    except FileNotFoundError:
        _fetch_events(season)
        return get_events(season)


def _fetch_races(event_id: str) -> None:
    """Fetch races from api and save in json file."""
    filename = get_race_filename(event_id)

    time.sleep(1)
    races = br.competitions(event_id)
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    file = open(filename, 'w')
    json.dump(races, file)


def get_races(event_id: str | None = None,
              season: str = current_season_id()) -> list[dict]:
    """Get races from json file. If the json-file for the races does not
     exist, fetch races, then get them from the created file.
     If event_id is None, all races for the season are returned
     (if their event is in the json-file).

    :param event_id: The event ID.
    :type event_id: str | None
    :param season: The season ID.
    :type season: str
    :return: A list of races.
    :rtype: list[dict]
    """
    if event_id is None:
        file = open(get_event_filename(season), 'r')
        events = [event['EventId'] for event in json.load(file)
                  if event['EventId'] is not None]
        races = []
        for _id in events:
            try:
                race = get_races(_id, season)
                races += race
            except json.JSONDecodeError:
                print(f'Could not get race for event {_id}')
        return races
    try:
        filename = get_race_filename(event_id)
        file = open(filename, 'r')
        content = json.load(file)
        for race in content:
            race.update({'EventId': event_id})
        return content
    except FileNotFoundError:
        _fetch_races(event_id)
        return get_races(event_id, season)


def _fetch_results(race_id: str) -> None:
    """Fetch results from api and save in json file."""
    filename = get_result_filename(race_id)
    time.sleep(1)
    res = br.results(race_id)
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    file = open(filename, 'w')
    json.dump(res, file)


def get_results(race_id: str) -> dict:
    """Get results from json file. If the json-file for the results does not
     exist, fetch results, then get them from the created file.

    :param race_id:
    :type race_id: str
    :return: A list of races.
    :rtype: list[dict]
    """
    filename = get_result_filename(race_id)
    try:
        file = open(filename, 'r')
        content = json.load(file)
        for result in content['Results']:
            result.update({'RaceId': race_id})
        return content
    except FileNotFoundError:
        _fetch_results(race_id)
        return get_results(race_id)


def get_start_list(race_id: str) -> dict[int, dict]:
    """

    :param race_id: The race ID.
    :return: A dictionary where the key is the place in the start list, and the
    value is information about the athlete that does not reveal the result.
    """
    comp_type = competition_type_from_race_id(race_id)
    race_results = get_results(race_id)
    results = race_results['Results']
    info = ['IBUId', 'Name', 'ShortName', 'FamilyName', 'GivenName']
    if is_relay(race_id):
        start_list = dict()
        teams = [r for r in results if r['IsTeam']]
        athletes = [r for r in results if not r['IsTeam']]
        for team in teams:
            team_start_order = int(team['Bib'])
            nation = team['Nat']
            participants = [athlete for athlete in athletes
                            if athlete['Bib'] == str(team_start_order)]
            if not participants:
                continue
            start_list[team_start_order] = {'Nat': nation, 'Flag': FLAGS[nation]}
            for participant in participants:
                start_list[team_start_order].update({
                    participant['Leg']:
                        dict(zip(info, itemgetter(*info)(participant)))})
        start_list.update({'RaceId': race_id})
        return start_list
    info += ['BibColor', 'Bib', 'Nat']
    if comp_type in (CompetitionType.PURSUIT_WOMEN,
                     CompetitionType.PURSUIT_MEN):
        info.append('PursuitStartDistance')
    start_list = {r['StartOrder']: dict(zip(info, itemgetter(*info)(r)))
                  for r in results}
    for team_start_order, athlete in start_list.items():
        nation = athlete['Nat']
        try:
            athlete.update({'Flag': FLAGS[nation]})
        except KeyError:
            athlete.update({'Flag': '&#127988;'})
    start_list.update({'RaceId': race_id})
    return start_list


def _write_start_lists_to_file(days_ago: int | None = None):
    """Write start lists for all races days_ago days back in time and after to
    the json file. The previous information in the file is overwritten.

    :param days_ago: The number of days back in time from
    which to include start lists, or None if all start lists
    from the current season should be included.
    """
    content = {}
    all_races = get_races()
    races = [(race['RaceId'], race['StartTime'], race['ResultStatus'])
             for race in all_races]
    if days_ago is not None:
        from_date = date_x_days_ago(days_ago)
        races = list(filter(lambda tup: (dt.date.fromisoformat(tup[1][:10])
                                         - from_date
                                         >= dt.timedelta(0)), races))
    for race_id, race_time, status in races:
        desc = competition_type_from_race_id(race_id)
        _time = dt.datetime.fromisoformat(
            race_time).astimezone(tz=None).isoformat(
            sep=' ', timespec='minutes')[:16]
        start_list = get_start_list(race_id)
        if not start_list:
            continue
        content[f'{RESULT_STATUS[status]} {_time}; {desc}'] = \
            {'StartList': start_list, 'Status': status,
             'Relay': is_relay(race_id)}
    filename = 'json/startlists.json'
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    file = open(filename, 'w')
    json.dump(content, file)


def update_results() -> None:
    """Update the races which have non-official results."""
    races = [race for race in filter(
        lambda race: race['ResultStatus'] != 'OFFICIAL', get_races())]
    events = {race['EventId'] for race in races}
    for event_id in events:
        _fetch_races(event_id)
    for race in races:
        logger.debug(
            f'Race {race['RaceId']} has status {race['ResultStatus']}.')
        _fetch_results(race['RaceId'])
    _write_start_lists_to_file(7)


if __name__ == '__main__':
    try:
        update_results()
        logger.info('{} ran at {}\n'.format(__file__.split('\\')[-1],
                                            dt.datetime.now().isoformat()))
    except Exception as e:
        logger.error(e)
