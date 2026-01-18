import logging
import datetime as dt
import icalendar as ical
import biathlonresults as br
from constants import CompetitionType, DURATIONS

logger = logging.getLogger(__name__)
logging.basicConfig(filename="biathlon.log", level=logging.DEBUG)


def translate_place(place: str) -> str:
    """Return Swedish translation of place name
       if known, else given place name.
    """
    logger.debug("Translating '{}'.".format(place))
    match place:
        case "Oestersund":
            return "Östersund"
        case "Annecy-Le Grand Bornand":
            return "Annecy"
        case "Nove Mesto na Morave":
            return "Nové Město na Moravě"
        case "Antholz-Anterselva":
            return "Antholz"
        case "Kontiolahti":
            return "Kontiolax"
        case "Otepaa":
            return "Otepää"
        case "Oslo Holmenkollen":
            return "Holmenkollen"
        case _:
            logger.debug("Found no translation for '{}'.".format(place))
            return place


def competition_type_from_raceid(id: str) -> str:
    """Return the correct CompetitionType based on the RaceId.

    Args:
        id (str): RaceId from biathlonresults API.

    Raises:
        KeyError: Raised when competition type cannot be derived from id.
    """
    logger.debug("Getting competition type from race_id={}.".format(id))
    match id[-4:]:
        case "SWRL":
            return CompetitionType.RELAY_WOMEN
        case "SMRL":
            return CompetitionType.RELAY_MEN
        case "MXSR":
            return CompetitionType.SINGLE_MIXED_RELAY
        case "MXRL":
            return CompetitionType.MIXED_RELAY
        case "SWIN":
            return CompetitionType.INIVIDUAL_WOMEN
        case "SMIN":
            return CompetitionType.INIVIDUAL_MEN
        case "SWSP":
            return CompetitionType.SPRINT_WOMEN
        case "SMSP":
            return CompetitionType.SPRINT_MEN
        case "SWPU":
            return CompetitionType.PURSUIT_WOMEN
        case "SMPU":
            return CompetitionType.PURSUIT_MEN
        case "SWMS":
            return CompetitionType.MASS_START_WOMEN
        case "SMMS":
            return CompetitionType.MASS_START_MEN
        case "SWSI":
            return CompetitionType.SHORT_INDIVIDUAL_WOMEN
        case "SMSI":
            return CompetitionType.SHORT_INDIVIDUAL_MEN
        case _:
            logger.error("Could not find competition type for {}.".format(id))
            raise KeyError(
                "Could not find competition type for {}.".format(id)
            )


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
        self.competition_type = competition_type_from_raceid(race_id)
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

    events = br.events("2526", level=br.consts.LevelType.BMW_IBU_WC)

    for event in events:
        place = event["Organizer"]
        id = event["EventId"]
        for race in br.competitions(id):
            try:
                broadcast = Broadcast(
                    race_id=race["RaceId"],
                    place=place,
                    start_time=dt.datetime.fromisoformat(race["StartTime"]),
                    olympics=(event['EventClassificationId'] == 'BTSWRLOG'),
                )
                cal.add_component(broadcast.to_ical_event())
            except KeyError as e:
                logger.warn(
                    "Failed to add event for " + race["Description"] +
                    "(ID=" + race["RaceId"] + "). " + e
                )

    f = open("calendar.ics", "bw")
    f.write(cal.to_ical())
    f.close()


if __name__ == "__main__":
    try:
        update()
        logger.info("biathlon.py ran at {}\n".format(
            dt.datetime.now().isoformat())
            )
    except Exception as e:
        logger.error(e)
