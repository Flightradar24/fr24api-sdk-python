# SPDX-FileCopyrightText: Copyright Flightradar24
#
# SPDX-License-Identifier: MIT
"""Regular expression patterns for Pydantic field validation."""

# Flightradar24 API
RADAR_CODE_REGEXP = r"^(?:[A-Z0-9-]{5,10})$"

# Flight Number: e.g., BA2490, U28171, DLH4LF, ACA888T, 5Y8529
# - Allows 1-3 letters for airline code followed by 1-4 digits and optional letter suffix.
# - Allows char-numeric IATA codes: digit + letter + digits (e.g., 5Y8529).
# - Allows letter + digit + digits pattern.
# - Case-insensitive.
FLIGHT_NUMBER_PATTERN = r"^(?i)(?:[A-Z]{1,3}[0-9]{1,4}[A-Z]?|[0-9][A-Z][0-9]{1,4}|[A-Z][0-9][0-9]{1,4})$"

# Callsign: e.g., BAW123, EIN45X, RYR88, *EIN45X, EIN45X*
# - 3 to 8 alphanumeric characters or hyphens.
# - Can optionally start or end with a '*' but not both, and if so, the alphanumeric/hyphen part is 1 character shorter.
# - Case-insensitive.
CALLSIGN_PATTERN = r"^(?i)(?:[A-Z0-9-]{3,8}|\\*[A-Z0-9-]{3,7}|[A-Z0-9-]{3,7}\\*)$"

# Registration: e.g., G-ABCD, N12345, D-AIQX, 9H-XYZ, *G-ABCD, G-ABCD*
# - 2 to 12 alphanumeric characters or hyphens.
# - Can optionally start or end with a '*' but not both, and if so, the alphanumeric/hyphen part is 1 character shorter.
# - Case-insensitive.
REGISTRATION_PATTERN = (
    r"^(?i)(?:[A-Z0-9-]{2,12}|\\*[A-Z0-9-]{1,11}|[A-Z0-9-]{1,11}\\*)$"
)

# Airline ICAO Code: e.g., BAW, DLH, RYR
# - Exactly 3 uppercase letters.
# - Case-sensitive as per original regex provided.
AIRLINE_ICAO_PATTERN = r"^[A-Z]{3}$"

# Airport Code: e.g., LHR, EGLL, JFK, KJFK, WAW, EPWA
# - Matches 3-letter IATA codes (case-insensitive).
# - Matches 4-character ICAO codes (alphanumeric, case-insensitive).
AIRPORT_CODE_PATTERN = r"^(?i)(?:[A-Z]{3}|[A-Z0-9]{4})$"

# Route: e.g., LHR-JFK, EGLL-KJFK
# - Consists of two airport codes (IATA or ICAO, 2-4 chars each) separated by a hyphen.
# - Case-insensitive.
ROUTE_PATTERN = r"^(?i)[A-Z0-9]{2,4}-[A-Z0-9]{2,4}$"

# IATA Flight Number (less strict than FLIGHT_NUMBER_PATTERN, for specific use cases)
# - (Letter+Digit OR Digit+Letter OR 2 Letters) followed by 1 or more digits.
# - Case-insensitive.
IATA_FLIGHT_NUMBER_PATTERN = r"^(?i)([A-Z][\d]|[\d][A-Z]|[A-Z]{2})(\d{1,})$"

# Squawk Code: e.g., 7000, 1234
# - Exactly 4 digits, each from 0 to 7.
# - Case-insensitive (though not applicable to digits).
SQUAWK_PATTERN = r"^(?:[0-7]{4})$"  # No /i needed as it's digits only

# Alpha-2 Country Code: e.g., US, GB, DE
# - Exactly 2 uppercase letters.
# - Case-insensitive.
ALPHA2_CODE_PATTERN = r"^(?i)[A-Z]{2}$"

# IATA Airport/City Code: e.g., LON, NYC, PAR
# - Exactly 3 uppercase letters.
# - Case-insensitive.
IATA_PATTERN = r"^(?i)[A-Z]{3}$"

# ICAO Airport Code: e.g., EGLL, KJFK, EDDF
# - Exactly 4 alphanumeric characters.
# - Case-insensitive.
ICAO_PATTERN = r"^(?i)[A-Z0-9]{4}$"

# Airport Parameter for more complex queries: e.g., "EGLL,inbound:EPWA,both:KJFK"
# - Allows comma-separated list of ICAO (4 chars) or IATA (3 chars) or Alpha2 (2 chars) codes.
# - Allows "inbound:", "outbound:", "both:" prefixes followed by comma-separated ICAO/IATA/Alpha2 codes.
# - Case-insensitive.
AIRPORT_PARAM_PATTERN = r"^(?i)(?:(?:[A-Z0-9]{4}|[A-Z]{3}|[A-Z]{2}),?(\s)*)*(?:(?:inbound|outbound|both):(?:[A-Z0-9]{2,4},)*[A-Z0-9]{2,4},?)*$"

# Route List: e.g., "LHR-JFK, CDG-DXB"
# - Comma-separated list of routes (each route is AAA-BBB or AAAA-BBBB).
# - Case-insensitive.
ROUTE_LIST_PATTERN = (
    r"^(?i)[A-Z0-9]{2,4}-[A-Z0-9]{2,4}(?:,(\s)*[A-Z0-9]{2,4}-[A-Z0-9]{2,4})*$"
)

# Service Types: e.g., P, C, M
# - Single character from the allowed set: P, C, M, J, T, H, B, G, D, V, O, N.
# - Case-sensitive as per original regex.
SERVICE_TYPES_PATTERN = r"^[PCMJTHBGDVON]$"

# Data Source: e.g., ADSB, MLAT, ESTIMATED
# - One of the specified strings: ADSB, MLAT, ESTIMATED.
# - Case-sensitive as per original regex.
DATA_SOURCE_PATTERN = r"^(ADSB|MLAT|ESTIMATED)$"

# Sort pattern: asc or desc
SORT_PATTERN = r"^(asc|desc)$"
