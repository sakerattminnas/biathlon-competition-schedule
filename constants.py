class CompetitionType:
    RELAY_WOMEN = "Stafett (D)"
    RELAY_MEN = "Stafett (H)"
    SINGLE_MIXED_RELAY = "Singlemixed stafett"
    MIXED_RELAY = "Mixed stafett"
    INIVIDUAL_WOMEN = "Individuell start (D)"
    INIVIDUAL_MEN = "Individuell start (H)"
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
    CompetitionType.INIVIDUAL_WOMEN: 120,
    CompetitionType.INIVIDUAL_MEN: 120,
    CompetitionType.SHORT_INDIVIDUAL_WOMEN: 120,  # prob too long
    CompetitionType.SHORT_INDIVIDUAL_MEN: 120,  # prob too long
    CompetitionType.SPRINT_WOMEN: 95,
    CompetitionType.SPRINT_MEN: 80,
    CompetitionType.PURSUIT_WOMEN: 45,
    CompetitionType.PURSUIT_MEN: 45,
    CompetitionType.MASS_START_WOMEN: 45,
    CompetitionType.MASS_START_MEN: 45,
}
