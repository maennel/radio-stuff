"""
Credits for this code to DH1TW.
Code borrowed from https://github.com/dh1tw/pyhamtools under the MIT license.
"""

def latlong_to_locator (latitude, longitude, precision=6):
    """converts WGS84 coordinates into the corresponding Maidenhead Locator

        Args:
            latitude (float): Latitude
            longitude (float): Longitude
            precision (int): 4,6,8,10 chars (default 6)

        Returns:
            string: Maidenhead locator

        Raises:
            ValueError: When called with wrong or invalid input args
            TypeError: When args are non float values

        Example:
           The following example converts latitude and longitude into the Maidenhead locator

           >>> from pyhamtools.locator import latlong_to_locator
           >>> latitude = 48.5208333
           >>> longitude = 9.375
           >>> latlong_to_locator(latitude, longitude)
           'JN48QM'

        Note:
             Latitude (negative = West, positive = East)
             Longitude (negative = South, positive = North)

    """

    if precision < 4 or precision == 5 or precision == 7 or precision == 9 or precision > 10:
        return ValueError

    if longitude >= 180 or longitude <= -180:
        raise ValueError

    if latitude >= 90 or latitude <= -90:
        raise ValueError

    longitude +=180
    latitude +=90

    # copied & adapted from github.com/space-physics/maidenhead
    A = ord('A')
    a = divmod(longitude, 20)
    b = divmod(latitude, 10)
    locator = chr(A + int(a[0])) + chr(A + int(b[0]))
    lon = a[1] / 2.0
    lat = b[1]
    i = 1

    while i < precision/2:
        i += 1
        a = divmod(lon, 1)
        b = divmod(lat, 1)
        if not (i % 2):
            locator += str(int(a[0])) + str(int(b[0]))
            lon = 24 * a[1]
            lat = 24 * b[1]
        else:
            locator += chr(A + int(a[0])) + chr(A + int(b[0]))
            lon = 10 * a[1]
            lat = 10 * b[1]

    return locator

def locator_to_latlong (locator, center=True):
    """converts Maidenhead locator in the corresponding WGS84 coordinates

        Args:
            locator (string): Locator, either 4, 6 or 8 characters
            center (bool): Center of (sub)square. By default True. If False, the south/western corner will be returned

        Returns:
            tuple (float, float): Latitude, Longitude

        Raises:
            ValueError: When called with wrong or invalid Maidenhead locator string
            TypeError: When arg is not a string

        Example:
           The following example converts a Maidenhead locator into Latitude and Longitude

           >>> from pyhamtools.locator import locator_to_latlong
           >>> latitude, longitude = locator_to_latlong("JN48QM")
           >>> print latitude, longitude
           48.5208333333 9.375

        Note:
             Latitude (negative = West, positive = East)
             Longitude (negative = South, positive = North)

    """

    locator = locator.upper()

    if len(locator) < 4 or len(locator) == 5 or len(locator) == 7 or len(locator) == 9:
        raise ValueError

    if ord(locator[0]) > ord('R') or ord(locator[0]) < ord('A'):
        raise ValueError

    if ord(locator[1]) > ord('R') or ord(locator[1]) < ord('A'):
        raise ValueError

    if ord(locator[2]) > ord('9') or ord(locator[2]) < ord('0'):
        raise ValueError

    if ord(locator[3]) > ord('9') or ord(locator[3]) < ord('0'):
        raise ValueError

    if len(locator) == 6:
        if ord(locator[4]) > ord('X') or ord(locator[4]) < ord('A'):
            raise ValueError
        if ord (locator[5]) > ord('X') or ord(locator[5]) < ord('A'):
            raise ValueError

    if len(locator) == 8:
        if ord(locator[6]) > ord('9') or ord(locator[6]) < ord('0'):
            raise ValueError
        if ord (locator[7]) > ord('9') or ord(locator[7]) < ord('0'):
            raise ValueError

    if len(locator) == 10:
        if ord(locator[8]) > ord('X') or ord(locator[8]) < ord('A'):
            raise ValueError
        if ord (locator[9]) > ord('X') or ord(locator[9]) < ord('A'):
            raise ValueError

    longitude = (ord(locator[0]) - ord('A')) * 20 - 180
    latitude = (ord(locator[1]) - ord('A')) * 10 - 90
    longitude += (ord(locator[2]) - ord('0')) * 2
    latitude += (ord(locator[3]) - ord('0')) * 1

    if len(locator) == 4:

        if center:
            longitude += 2 / 2
            latitude += 1.0 / 2

    elif len(locator) == 6:
        longitude += (ord(locator[4]) - ord('A')) * 5.0 / 60
        latitude += (ord(locator[5]) - ord('A')) * 2.5 / 60

        if center:
            longitude += 5.0 / 60 / 2
            latitude += 2.5 / 60 / 2

    elif len(locator) == 8:
        longitude += (ord(locator[4]) - ord('A')) * 5.0 / 60
        latitude += (ord(locator[5]) - ord('A')) * 2.5 / 60

        longitude += int(locator[6]) * 5.0 / 600
        latitude += int(locator[7]) * 2.5 / 600

        if center:
            longitude += 5.0 / 600 / 2
            latitude += 2.5 / 600 / 2

    elif len(locator) == 10:
        longitude += (ord(locator[4]) - ord('A')) * 5.0 / 60
        latitude += (ord(locator[5]) - ord('A')) * 2.5 / 60

        longitude += int(locator[6]) * 5.0 / 600
        latitude += int(locator[7]) * 2.5 / 600

        longitude += (ord(locator[8]) - ord('A')) * 1.0 / 2880
        latitude += (ord(locator[9]) - ord('A')) * 1.0 / 5760

        if center:
            longitude += 1.0 / 2880 / 2
            latitude += 1.0 / 5760 / 2

    else:
        raise ValueError

    return latitude, longitude
