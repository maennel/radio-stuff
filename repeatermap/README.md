# Repeater Mapper

Repeater Mapper is a utility which ingests and parses data from official Repeater lists, allows to filter them and write
into a particular format (e.g. to program your radio, or present the data on a map).

Find the source code at https://github.com/maennel/radio-stuff/tree/main/repeatermap.

## Sources

The available sources controlled via the `--source` are:

| Name                     | Description                                                                                                                                                            | CLI parameter              |
|--------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------|----------------------------|
| USKA                     | Ingests repeaters from [USKA](https://uska.ch/hb-repeater-voice-list/)                                                                                                 | `uska`                     |
| Radio emetteurs français | Consumes repeaters from [R-E-F](https://www.r-e-f.org/index.php?option=com_content&view=article&id=1279&Itemid=492)                                                    | `radio-emetteurs-francais` |
| JSON                     | Consumes repeaters from the local file provided via the `--json-file` parameter. The format of the JSON file needs to follow the format that's written by the program. | `json`                     |

Several sources can be combined.

## Filters

From all repeaters, ingested from the selected sources, you can filter them for the following criteria using the
`--filter` and the `--area-filter` argument:

### Filtering for pre-defied criteria

Using the `--filer` argument, you can filter repeaters for pre-defined criteria.

| Criterion         | Available options                                           |
|-------------------|-------------------------------------------------------------|
| Band (`band`)     | - `10m`<br />- `6m`<br />- `2m`<br />- `70cm`<br />- `23cm` |
| Status (`status`) | - `planned`<br />- `qrv`<br />- `qrx`<br />- `qrt`          |

Filters from the same category are combined with a boolean OR.
Filters across different categories are combined with a boolean AND.

I.e. `band-2m band-70 status-qrv`, which is the equivalent of `(band-2m OR band-70cm) AND status-qrv`

### Filtering repeaters by area

Using the `--area-filter` argument, you can filter the set of repeaters by area, i.e. retain only filters that are
within reach from a particular point expressed as a [Maidenhead Locator](https://www.f5len.org/tools/locator/).

You can pass in one or several areas.
If set, only repeaters withing these areas will be returned.

Example values to this filter are:

- `jn36kr-20km` - this takes the center coordinate of the Maidenhead locator and returns all repeaters within a 20km
  radius of this point.
- `jn36kr-20km jn36lr-20km jn36mr-20km` - this returns repeaters within the total area covered by these three circles.

## Presentations

| Name                         | Description                                                                         | CLI parameters    |
|------------------------------|-------------------------------------------------------------------------------------|-------------------|
| JSON                         | Writes out the repeaters in a JSON format.                                          | `json`            |
| Yaesu ADMS-14 importable CSV | Writes a CSV file, which can be imported via Yaesu's ADMS-14 tool.                  | `yaesu-csv`       |
| Google Maps CSV              | Writes a CSV which can be imported to Google Maps, so you can create your own maps. | `google-maps-csv` |

Provide the destination file via the `--output` argument.
If not provided, output will be written to stdout.

### Yaesu ADMS-14

ADMS-14 is a tool that helps you program
your [Yaesu FT5-D radio](https://www.yaesu.com/product-detail.aspx?Model=FT5DR&CatName=VHF/UHF%20Handhelds).
With the `yaesu-csv` option, the tool will create a CSV file that can be imported to ADMS-14 to make programming
repeaters on the FT5-D easy.

> [!NOTE]
> I don't currently know whether the generated file-format is compatible with ADMS-10 or ADMS-18, which are tools to
> program other Yaesu radios.

### Google Maps

Create your own repeater maps on Google Maps at [MyMaps](https://www.google.com/maps/d/u/0/) (choose your layers,
points, etc.).
MyMaps is also reachable from within Google Drive > + New > More > Google My Maps.

To do so:

1. Upload your CSV file to Google Drive.
2. Click on "Create a new Map".
3. Click on "Add layer" (each layer has to be an own Google Spreadsheet file).

## Examples

### Use Case: I want all operational swiss 2m and 70cm repeaters on a map

To configure your radio with all QRV repeaters on the 2m and 70cm bands, run the following CLI command:

```shell
repeater-mapper --source uska --filter band-2m band-70cm status-qrv --presentation google-maps-csv --output google-maps.csv
```

...and import the output data to Google's MyMaps.

### Use Case: I want all operational swiss 70cm repeaters in proximity of my holiday location on my radio

```text
repeater-mapper --source uska --filter band-70cm status-qrv --area-filter jn46ap-30km --presentation yaesu-csv --output adms-14.csv
```

...and import the output file to ADMS-14