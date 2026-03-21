import logging
import datetime as dt
from pathlib import Path

logger = logging.getLogger(__name__)
logging.basicConfig(filename=Path('biathlon.log'), level=logging.INFO)


def current_season_id() -> str:
    """Return season ID. For example, the season ID
    for the 2025/2026 season is '2526'.

    :return: The season id.
    :rtype: str
    """
    date = dt.date.today()
    if date.month > 10:
        return str(date.year)[-2:] + str(date.year + 1)[-2:]
    else:
        return str(date.year - 1)[-2:] + str(date.year)[-2:]


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


def competition_type_from_race_id(race_id: str) -> str:
    """Return the correct CompetitionType based on the RaceId.

    Args:
        race_id (str): RaceId from biathlonresults API.

    Raises:
        KeyError: Raised when competition type cannot be derived from id.
    """
    logger.debug("Getting competition type from race_id={}.".format(race_id))
    match race_id[-4:]:
        case "SWRL":
            return CompetitionType.RELAY_WOMEN
        case "SMRL":
            return CompetitionType.RELAY_MEN
        case "MXSR":
            return CompetitionType.SINGLE_MIXED_RELAY
        case "MXRL":
            return CompetitionType.MIXED_RELAY
        case "SWIN":
            return CompetitionType.INDIVIDUAL_WOMEN
        case "SMIN":
            return CompetitionType.INDIVIDUAL_MEN
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
            logger.error(
                "Could not find competition type for {}.".format(race_id))
            raise KeyError(
                "Could not find competition type for {}.".format(race_id)
            )


class CompetitionType:
    RELAY_WOMEN = "Stafett (D)"
    RELAY_MEN = "Stafett (H)"
    SINGLE_MIXED_RELAY = "Singlemixed stafett"
    MIXED_RELAY = "Mixed stafett"
    INDIVIDUAL_WOMEN = "Individuell start (D)"
    INDIVIDUAL_MEN = "Individuell start (H)"
    SPRINT_WOMEN = "Sprint (D)"
    SPRINT_MEN = "Sprint (H)"
    PURSUIT_WOMEN = "Jaktstart (D)"
    PURSUIT_MEN = "Jaktstart (H)"
    MASS_START_WOMEN = "Masstart (D)"
    MASS_START_MEN = "Masstart (H)"
    SHORT_INDIVIDUAL_WOMEN = "Kortdistans (D)"
    SHORT_INDIVIDUAL_MEN = "Kortdistans (H)"


# Broadcast time for each competition type, according to SVT
DURATIONS = {
    CompetitionType.RELAY_WOMEN: 80,
    CompetitionType.RELAY_MEN: 80,
    CompetitionType.SINGLE_MIXED_RELAY: 45,
    CompetitionType.MIXED_RELAY: 70,
    CompetitionType.INDIVIDUAL_WOMEN: 120,
    CompetitionType.INDIVIDUAL_MEN: 120,
    CompetitionType.SHORT_INDIVIDUAL_WOMEN: 120,  # prob too long
    CompetitionType.SHORT_INDIVIDUAL_MEN: 120,  # prob too long
    CompetitionType.SPRINT_WOMEN: 95,
    CompetitionType.SPRINT_MEN: 80,
    CompetitionType.PURSUIT_WOMEN: 45,
    CompetitionType.PURSUIT_MEN: 45,
    CompetitionType.MASS_START_WOMEN: 45,
    CompetitionType.MASS_START_MEN: 45,
}

A, B, C, D, E, F, G, H, I, J, K, L, M, N, \
    O, P, Q, R, S, T, U, V, W, X, Y, Z = (
        '&#' + str(i) + ';' for i in range(127462, 127462 + 26)
    )


FLAGS = {
    'AUS': A+U,
    'AUT': A+T,
    'BEL': B+E,
    'BUL': B+G,
    'CAN': C+A,
    'CHN': C+N,
    'CRO': H+R,
    'CZE': C+Z,
    'DEN': D+K,
    'EST': E+E,
    'FIN': F+I,
    'FRA': F+R,
    'GBR': G+B,
    'GER': D+E,
    'GRL': G+L,
    'ITA': I+T,
    'KAZ': K+Z,
    'KOR': K+R,
    'LAT': L+V,
    'LTU': L+T,
    'MDA': M+D,
    'NOR': N+O,
    'POL': P+L,
    'ROU': R+O,
    'SLO': S+I,
    'SUI': C+H,
    'SVK': S+K,
    'SWE': S+E,
    'UKR': U+A,
    'USA': U+S,
}
