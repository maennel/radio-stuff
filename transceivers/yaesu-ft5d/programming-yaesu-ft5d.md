# Programming the Yaesu FT5D

## Problem to solve
Configure all swiss (HB) radio repeaters listed on the [USKA page](https://uska.ch/en/hb-repeater-voice-list/?lang=en) on my [Yaesu FT5D(E)](https://www.yaesu.com/product-detail.aspx?Model=FT5DR&CatName=VHF/UHF%20Handhelds) handheld radio.

## Solution
### Unsuccessful attempts
A first attempt was to reverse engineer the binary format of the backup or the memory export. 

### Setup
I later discovered, that Yaesu offers the software called "ADMS-14" directly from their [FT5D product page](https://www.yaesu.com/product-detail.aspx?Model=FT5DR&CatName=VHF/UHF%20Handhelds) ([download link](https://www.yaesu.com/Files/BB2B47AE-1018-01AF-FAE48FDCB1919193/FT5D_ADMS-14_ENG.zip)). I used version 1.0.1.0 of ADMS-14.

Working on a Linux system, I installed `wine` (along with all fonts) and ran ADMS-14 from there.

### General approach
The general process is to:
1. transfer the FT5D backup file to my computer.
2. load the backup file into ADMS-14 locally.
3. download and transform the list of swiss radio repeaters.
4. import the list of repeaters into the loaded configuration file in ADMS-14.
5. save the file.
6. transfer the updated backup file back to the radio using the SD card and "restore" the backup.

But let's take this step by step.

### Loading the backup file in ADMS-14
From the "Communications" menu, use "Get data from SD card" to load a backup file.

### Transforming the list of repeaters
I noticed that ADMS-14 allows to import a CSV file.
To find out, what this was all about, I created a CSV export first to discover, that the export contains the "Memories", i.e. pre-configured VHF/UHF frequencies, offsets, modes, etc.
Since re-importing the export.csv file worked, I knew about the expected CSV format.

With some trial and error, I manually refactored the list of repeaters from USKA to match the exported format.


## Outcome
Currently, the list of repeaters is at the version of the **2025-08-04**.
Here are the final list in CSV format:
1. [Working copy](data/hb-repeater-list_prepared_20250804.csv), including convenience header line.
2. [Cleaned up, padded, importable CSV](data/hb-repeater-list_prepared_20250804_clean.csv).

Remaining required modifications to the working copy are:
1. Remove the CSV header line. This one is for convenience only.
2. Pad the trailing entries up to 900 by adding the following lines: `N,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,0`, where `N` is the incrementing index of the line up to 900 (which is the last entry).


## Remaining work
- Automate transformation from USKA CSV file.
- Persist USKA CSV files to identify changes applied (e.g. between versions of 2025-08-04 and 2025-08-17).
