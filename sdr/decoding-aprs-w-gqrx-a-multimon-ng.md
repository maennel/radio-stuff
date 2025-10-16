# Decoding APRS with GQRX and Multimon-ng

## Raw notes
Decode APRS:
- On GQRX: Set to NFM[6kHz], @144.800kHz, squelch: -78dB; UDP out (localhost, port 65535)
- On CLI:
```
nc -lu localhost 65535 | \
sox -t raw -esigned-integer -b16 -r 48000 - -esigned-integer -b16 -r 22050 -t raw - | \
multimon-ng -t raw -A --timestamp - 
```
Source: https://www.gqrx.dk/doc/streaming-audio-over-udp

## Example output

```
2025-10-16 21:12:17: APRS: HB9TJR-3>APCHVD,WIDE1-1,WIDE2-2:@000001z4642.45N/00633.00E_000/000g000t039r000p000P000b08686h96/16.07V -0.39A 0.1PV 30.52Ah 0W 377Wh 11.1C 71.3% 5.36C
2025-10-16 21:12:19: APRS: DM0ESS>APMI06,DB0ZD-10*,HB9ARI-4*,WIDE2*:@161912z4730.71N/01016.82E#WX3in1Plus2.0 U=13.6V,T=38.2C
2025-10-16 21:12:26: APRS: HB9FIL-10>APGW1K,HB9ARI-4*,WIDE1*:!4656.06N/00737.00E#GW-1000, FT7800 5W, Diamod X30 14.1V
```
