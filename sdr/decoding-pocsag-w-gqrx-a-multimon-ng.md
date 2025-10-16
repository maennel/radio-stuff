# Decoding POCSAG with GQRX and Multimon-ng

1. Run GQRX
2. Activate "UDP" (configure network: UDP host: `localhost` & UDP port: `65535`)
3. Tune in Narrow FW (BW ~22kHz) to one of (see ):
  a. 147.300MHz
  b. 147.325MHz
  c. 147.375MHz
  d. 147.400MHz
4. Run the multimon-ng decoder:
```bash
nc -ul 127.0.0.1 65535 |sox -t raw -esigned-integer -b16 -r 48000 - -esigned-integer -b16 -r 22050 -t raw - | multimon-ng -t raw -a POCSAG512 -a POCSAG1200 -a POCSAG2400 --timestamp -
```

In my region, I can also clearly hear POCSAG traffic on:
- 145.700MHz
- 145.650MHz

...which is in the middle of the 2m Ham band in Switzerland and therefore probably shouldn't be that way.

Source: https://www.gqrx.dk/doc/streaming-audio-over-udp

## Example output
Multimon-ng's output looks like the following:
```
2025-10-16 21:16:51: POCSAG1200: Address: 2022100  Function: 3  Alpha:   Paessler Test F3 ALLIP Zugang<NUL><NUL>
2025-10-16 21:16:51: POCSAG1200: Address: 2031608  Function: 0 
2025-10-16 21:16:52: POCSAG1200: Address: 2031608  Function: 0 
```