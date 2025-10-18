import argparse
from itertools import chain

from repeater_mapper import Status, Band, StandardRepeater
from repeater_mapper.filters import RepeaterFilter
from repeater_mapper.sources.uska import UskaRepeaterReader
from repeater_mapper.presentations import JsonPresentation, YaesuFt5deAdms14CsvPresentation, \
    GoogleMapsCSVPresentation

SOURCE_USKA = "uska"
SOURCE_ARGUMENTS_MAP = {
    SOURCE_USKA: UskaRepeaterReader,
}

FILTER_SEPARATOR = "-"
FILTER_BAND = "band"
FILTER_STATUS = "status"
FILTER_ARGUMENTS_MAP = {
    FILTER_BAND: [b.name.lower().replace("band_", "") for b in Band if b != Band.BAND_UNKNOWN],
    FILTER_STATUS: [s.name.lower() for s in Status],
}

PRESENTATION_JSON = "json"
PRESENTATION_YAESU_CSV = "yaesu-csv"
PRESENTATION_GOOGLE_MAPS_CSV = "google-maps-csv"
PRESENTATION_ARGUMENTS_MAP = {
    PRESENTATION_JSON: JsonPresentation,
    PRESENTATION_YAESU_CSV: YaesuFt5deAdms14CsvPresentation,
    PRESENTATION_GOOGLE_MAPS_CSV: GoogleMapsCSVPresentation,
}


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Repeater Mapper to map repeater information from various sources to well-formatted output.",
        add_help=True,
    )

    # Repeater sources: USKA, ...
    parser.add_argument("--source", dest="sources", action="append", choices=SOURCE_ARGUMENTS_MAP.keys(), nargs="*")

    # Filter: Status, Band, Callsign
    # TODO: Filter by callsign (regex?)
    choices = [f"{arg_type}{FILTER_SEPARATOR}{arg_value}" for arg_type, arg_values in FILTER_ARGUMENTS_MAP.items() for
               arg_value in arg_values]
    parser.add_argument("--filter", dest="filters", action="append", choices=choices, nargs="*")

    # Presentation formats: JSON, Yaesu FT5D, Google Maps
    parser.add_argument("--presentation", action="store", choices=PRESENTATION_ARGUMENTS_MAP.keys(),
                        default=PRESENTATION_JSON)

    # Output file
    parser.add_argument("--output", default="-", type=argparse.FileType("w"))

    return parser.parse_args()


def main() -> None:
    args = _parse_args()

    # Read arguments
    sources = [SOURCE_ARGUMENTS_MAP.get(s) for s in list(chain(*args.sources))]
    if len(sources) == 0:
        sources = [SOURCE_USKA]

    _filters: list[str] = list(chain(*args.filters))
    filter_builder = RepeaterFilter.Builder()
    for _filter in _filters:
        filter_type, filter_value = _filter.split(FILTER_SEPARATOR, maxsplit=1)
        if filter_type == FILTER_BAND:
            filter_builder.add_band(Band.from_str(filter_value))
        elif filter_type == FILTER_STATUS:
            filter_builder.add_status(Status[filter_value.upper()])
    repeater_filter = filter_builder.build()

    presentation = PRESENTATION_ARGUMENTS_MAP.get(args.presentation)

    output = args.output

    # Run logic
    repeaters: list[StandardRepeater] = []
    for source in sources:
        repeaters.extend(source().read())
    filtered_repeaters = repeater_filter.filter(repeaters)
    presentation(filtered_repeaters).write(output)


if __name__ == "__main__":
    main()
