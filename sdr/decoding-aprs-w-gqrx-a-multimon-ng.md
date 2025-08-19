# Decoding APRS with GQRX and Multimon-ng

## Raw notes
Decode APRS:
- On GQRX: Set to NFM[6kHz], @144.800kHz, squelch: -78dB; UDP out
- On CLI:
```
nc -lu localhost 65535 | \
sox -t raw -esigned-integer -b16 -r 48000 - -esigned-integer -b16 -r 22050 -t raw - | \
multimon-ng -t raw -A --timestamp - 
```
Source: https://www.gqrx.dk/doc/streaming-audio-over-udp
