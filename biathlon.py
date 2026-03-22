import datetime as dt
import icalendar as ical
import biathlonresults as br

from api_to_json import update_results
from util import (logger, DURATIONS, translate_place,
                  competition_type_from_race_id)


class Broadcast:
    def __init__(
        self,
        race_id: str,
        place: str,
        start_time: dt.datetime,
        end_time: dt.datetime | None = None,
        olympics: bool = False,
    ):
        self.start_time = start_time
        self.place_en = place
        self.place_sv = translate_place(place)
        self.competition_type = competition_type_from_race_id(race_id)
        self.race_id = race_id
        self.olympics = olympics
        if end_time is None:
            end_time = self.start_time + dt.timedelta(
                minutes=DURATIONS[self.competition_type]
            )
        self.end_time = end_time
        logger.debug("Created Broadcast object {}.".format(self.__repr__()))

    def to_ical_event(self) -> ical.Event:
        """Create an icalendar Event from this object."""
        event = ical.Event()

        event.add("dtstamp", ical.vDatetime(self.start_time))
        event.add("uid", self.race_id)
        event.add("dtstart", ical.vDatetime(self.start_time))
        event.add("dtend", ical.vDatetime(self.end_time))

        if self.olympics:
            event.add("summary", f'OS: {self.competition_type}')
        else:
            event.add("summary", self.competition_type)
        event.add("description", self.place_sv)

        return event

    def __str__(self):
        res = self.competition_type
        res += " - " + self.start_time.strftime("%d %b")
        return res

    def __repr__(self):
        return self.race_id + "-" + self.start_time.strftime("%Y%m%dT%H%M") + "-" + self.place_en.upper()


def update():
    """Retrieve biathlon events and overwrite the calendar.ics
       file with icalendar events based on them.
    """
    cal = ical.Calendar()
    cal.add("prodid", "sakerattminnas, " + dt.datetime.now().isoformat()[:22])
    cal.add("version", "0.4")

    date = dt.date.today()
    if date.month > 7:
        season = str(date.year)[-2:] + str(date.year + 1)[-2:]
    else:
        season = str(date.year - 1)[-2:] + str(date.year)[-2:]

    events = br.events(season, level=br.consts.LevelType.BMW_IBU_WC)

    for event in events:
        place = event["Organizer"]
        event_id = event["EventId"]
        for race in br.competitions(event_id):
            race_id = race["RaceId"]
            try:
                broadcast = Broadcast(
                    race_id=race_id,
                    place=place,
                    start_time=dt.datetime.fromisoformat(race["StartTime"]),
                    olympics=event['EventClassificationId'].endswith('OG'),
                )
                cal.add_component(broadcast.to_ical_event())
            except KeyError as ke:
                logger.warning(
                    "Failed to add event for " + race["Description"] +
                    "(ID=" + race["RaceId"] + f"). {ke}"
                )

    f = open("calendar.ics", "bw")
    f.write(cal.to_ical())
    f.close()

    update_results()


if __name__ == "__main__":
    try:
        update()
        logger.info("biathlon.py ran at {}\n".format(
            dt.datetime.now().isoformat())
            )
    except Exception as e:
        logger.error(e)
