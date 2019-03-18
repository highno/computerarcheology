![Mountains](MoonPatrol.jpg)

# Far Background (Mountains) 

This background is a giant 256x64 pixel image. Each pixel is one of 4 colors.
256*64*2/8 = 4K

Each byte holds 4 pixels. The upper four bits are the first bit-plane and the
second 4 bits are the second bit plane. Thus the screen mapping looks like this:

```
ROM: abcd_ABCD
Screen: aA_bB_cC_dD
```

The actual pixel colors come from the table in PROM2 in a jumbled mapping.
From experimenting, the pixel colors are:
```
;             00    01     10     11
; Hills:      --    20     00     70
; Mountains:  --    C0     00     A0
; City:       --    00     77     70
```

Notice the black area near the top between the mountain peaks. These pixels are solid black instead
of transparent. The background is black, and you can't tell the difference.


```html
<script src="/js/BinaryData.js"></script>
<script src="/Arcade/MoonPatrol/MoonPatrol.js"></script>
<script src="/js/TileEngine.js"></script>
<script src="/js/CANVAS.js"></script>
<canvas width="2304" height="576"
        data-canvasFunction="TileEngine.handleTileCanvas"
        data-getTileDataFunction="MoonPatrol.getBackgroundImage"
        height="150"
        data-pixWidth="8"
        data-gridX="256"
        data-gridY="64"
        data-pixHeight="8"
        data-gap="0.25"
        data-gridPad="1"
        data-colorsName="CS0"
        data-colors='["#808080","#0000FF","#000000","#0097AE"]'
        data-command="0">
</canvas>
```

```plainCode
; For instance, first colored pixel at 0004:
; 40    0100_0000 -> 00 01 00 00  Dark Blue

;Mountains (far background)
0000: 00 00 00 00 40 00 00 00 00 00 00 00 00 00 00 00 
0010: 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 CC 
0020: 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 
0030: 00 00 00 00 00 00 00 00 00 00 00 00 76 00 00 00 
0040: 00 00 00 00 60 00 00 00 00 00 00 00 00 00 00 00 
0050: 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 CC 
0060: 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 
0070: 00 00 00 00 00 00 00 00 00 00 00 00 76 60 00 00 
0080: 00 00 00 00 60 00 00 00 00 00 00 00 00 00 00 00 
0090: 00 00 00 00 00 00 00 00 00 00 00 00 00 00 11 EE 
00A0: 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 
00B0: 00 00 00 00 00 00 00 00 00 00 00 00 FE F0 00 00 
00C0: 00 00 00 00 70 11 00 00 00 00 00 00 00 00 00 00 
00D0: 00 00 00 00 00 00 00 00 00 00 00 00 00 00 11 EE 
00E0: 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 
00F0: 00 00 00 00 00 00 00 00 00 00 00 00 FF F0 00 00 
0100: 00 00 00 00 70 33 88 00 00 00 00 00 00 00 00 00 
0110: 00 00 00 00 00 00 00 00 00 00 00 00 00 00 10 FF 
0120: 80 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 
0130: 00 00 00 00 00 00 00 00 00 00 00 11 F7 F1 00 00 
0140: 00 00 00 00 F1 33 CC 00 00 00 00 00 00 00 00 00 
0150: 00 00 00 00 00 00 00 00 00 00 00 00 00 00 10 FF 
0160: 80 88 00 00 00 00 00 00 00 00 00 00 00 00 00 00 
0170: 00 00 00 00 00 00 00 00 00 00 00 11 F6 F3 00 00 
0180: 00 00 00 00 F1 77 CC 00 00 00 00 00 00 00 00 00 
0190: 00 00 00 00 00 00 00 00 00 00 00 00 00 00 10 F6 
01A0: C0 88 00 00 00 00 00 00 00 00 00 00 00 00 00 00 
01B0: 00 00 00 00 00 00 00 00 00 00 00 11 FF F7 00 00 
01C0: 00 00 00 00 F1 FF E6 00 00 00 00 00 00 00 00 00 
01D0: 00 00 00 00 00 00 00 00 00 00 00 00 00 00 10 F7 
01E0: D1 88 00 00 00 00 00 00 00 00 00 00 00 00 00 00 
01F0: 00 00 00 00 00 00 00 00 00 00 00 11 FF FF 00 00 
0200: 00 00 00 10 F1 FF EE 00 00 00 00 00 00 00 00 00 
0210: 00 00 00 00 00 00 00 00 00 00 00 00 00 00 10 FF 
0220: F3 88 00 00 00 00 00 00 00 00 00 00 00 00 00 00 
0230: 00 00 00 00 00 00 00 00 00 00 00 30 FF FE 00 00 
0240: 00 00 00 10 F3 FB EE 00 00 00 00 00 00 00 00 00 
0250: 00 00 00 00 00 00 00 00 00 00 00 00 00 03 10 FF 
0260: F1 88 00 00 00 00 00 00 00 00 00 00 00 00 00 00 
0270: 00 00 00 00 00 00 00 00 00 00 00 31 FF FC 00 00 
0280: 00 00 00 30 F3 F9 FE 00 00 00 00 11 00 00 00 00 
0290: 00 00 00 00 00 00 00 00 33 00 00 00 00 0F 10 FE 
02A0: F3 CC 00 00 00 00 00 00 00 00 00 00 00 00 00 00 
02B0: 00 00 00 00 00 00 00 00 00 00 00 70 FF F8 00 00 
02C0: 00 00 00 F0 F3 FD FA 00 00 00 00 11 98 80 00 00 
02D0: 00 00 00 00 00 00 00 00 33 00 00 00 08 0F 30 FE 
02E0: F7 CC 00 00 00 00 00 00 00 00 00 00 00 00 00 00 
02F0: 00 00 00 00 00 00 00 00 00 00 CC 71 FF F8 C0 00 
0300: 00 00 00 F0 F1 FF F0 00 00 00 00 33 B8 80 00 00 
0310: 00 00 00 00 00 00 00 00 33 88 00 00 08 09 30 FF 
0320: F3 CC 00 00 00 00 00 00 00 00 00 00 00 00 00 00 
0330: 00 00 00 00 00 00 00 00 00 00 CC F8 FF FC C0 00 
0340: 00 00 00 F0 F1 FF F0 00 00 00 00 33 E8 C0 00 00 
0350: 00 00 00 00 00 00 00 00 33 A8 00 00 09 0C 30 FF 
0360: F3 CC 00 00 00 00 00 00 00 00 00 77 00 00 00 00 
0370: 00 00 00 00 00 00 00 00 00 00 FF F8 FF FE C0 00 
0380: 00 00 10 F0 F3 FF F0 00 00 00 00 77 F8 C0 00 00 
0390: 00 00 00 00 00 00 00 00 75 EC 00 00 09 08 71 FF 
03A0: FB CC 00 00 00 00 00 00 00 00 00 77 00 00 00 00 
03B0: 00 00 00 00 00 00 00 00 00 00 F7 FC F7 FC E0 00 
03C0: 00 00 30 F0 F1 FF F8 00 00 00 00 77 F0 C0 00 00 
03D0: 00 00 00 00 00 00 00 00 75 FC 00 00 09 08 71 FF 
03E0: FB CC 00 00 00 00 00 00 00 00 00 77 00 00 00 00 
03F0: 00 00 00 00 00 00 00 00 00 00 F7 FC F7 F8 E0 00 
0400: 00 10 30 F0 F1 FF F8 80 00 00 00 77 F0 E0 00 00 
0410: 00 33 00 00 00 00 00 00 77 FC 80 00 0B 08 70 FE 
0420: FF CC 00 00 00 00 00 00 00 00 00 77 66 00 00 00 
0430: 00 00 00 00 00 00 00 00 00 00 F7 FE FF F8 E0 00 
0440: 00 30 B0 F0 F3 FF F8 80 00 00 00 FF F8 E0 00 00 
0450: 00 33 88 00 00 00 00 00 F7 F8 80 00 0B 0C 70 FE 
0460: FF C4 00 00 00 00 00 00 00 00 00 77 EE 00 00 00 
0470: 00 00 00 00 00 00 00 00 00 00 F7 FE FF FC E0 00 
0480: 00 30 F0 FD FB FF FC 80 00 00 00 FF F8 E0 00 00 
0490: 00 33 88 00 00 00 00 00 F3 F8 80 00 06 0C 71 FE 
04A0: F7 C4 00 00 00 00 00 00 00 00 00 77 EE CC 00 00 
04B0: 00 00 00 00 00 00 00 00 00 00 F7 FC FF FC E0 00 
04C0: 00 F0 F0 FF FD FF FC C4 00 11 11 FF F8 E0 00 00 
04D0: 00 77 C0 00 00 00 00 00 F7 FC C0 80 00 04 71 FF 
04E0: F6 D5 00 00 00 00 00 00 00 00 00 FF F7 C4 00 00 
04F0: 00 00 00 00 00 00 00 00 00 00 F3 FE FF F8 E0 00 
0500: 00 F0 F0 F7 FE FF FC C4 00 33 BB FB F0 E0 00 00 
0510: 00 FF C0 00 00 00 00 D0 F3 FD D0 80 00 02 70 FF 
0520: F6 D5 00 00 00 00 00 00 00 00 00 FF F7 C4 00 00 
0530: 00 00 00 00 00 00 00 00 00 00 F3 FF FF F0 E0 00 
0540: 30 F0 F0 FB FF FF FF E0 00 33 FF F7 F0 F4 00 00 
0550: 00 FF C8 00 00 00 10 F0 F3 FD F8 80 00 00 70 FF 
0560: F6 DD CC 00 00 00 00 00 00 00 00 FF FF CC 00 00 
0570: 00 00 00 00 00 00 00 00 00 22 F7 FF FF F0 F0 00 
0580: 70 F0 F3 FD FF FF FF E8 00 77 FF FF F8 FC 00 00 
0590: 11 FE C0 00 00 00 10 F4 F7 FF FC 80 00 00 78 FF 
05A0: FE FF CC 00 00 00 00 00 00 00 00 FF FB CC 00 00 
05B0: 00 00 00 00 00 00 00 00 00 33 F7 F7 FE F0 F0 80 
05C0: 71 F8 F7 FF FF FF FF F0 33 FF FF FD F0 F8 00 00 
05D0: 11 FC E0 C0 00 00 10 FC FF FF FC C0 00 00 F3 FE 
05E0: FE FF EE 00 00 00 00 00 00 00 00 FF FB CC 00 00 
05F0: 00 00 00 00 00 00 00 00 00 33 F7 F7 FE F0 F0 E0 
0600: FF FA F7 FF FF FF FF F1 FF FD FF FC F1 F0 C0 00 
0610: 33 F8 E0 C0 00 00 11 FE FF FF FD C4 00 00 F3 FE 
0620: FF FF EE 00 00 00 66 00 00 00 33 FF FF CC 00 00 
0630: 00 00 00 00 00 00 00 00 00 33 F7 F7 FF F0 F1 F1 
0640: FF F2 FF FF FF FF FE F3 FF F0 FF FE F0 F0 C0 00 
0650: 33 F8 E0 E0 00 00 33 FF F7 FF FF F8 00 33 F3 FE 
0660: FF FF FF 88 00 00 77 66 00 00 33 FF FF CC 00 00 
0670: 00 00 00 00 00 00 00 00 00 FF FF FB FF F3 F3 FD 
0680: FF F3 FF FF FF FF FC F7 FE F0 FF FF F0 F0 E0 00 
0690: BB FE E0 E0 00 00 33 FF FF FF FF F8 00 FF F7 FF 
06A0: FF FF FF 88 00 00 77 EC 00 00 33 FF FF CC 00 00 
06B0: 00 11 CC 00 00 00 00 00 11 FD FF FB FE F7 F7 FB 
06C0: FE F7 FF FF FF FF FF FC F8 F0 F7 FE F0 F0 E0 11 
06D0: FF FC F0 E0 00 00 FF FF FF FF FF FC 88 FF F7 FF 
06E0: FF FC FF 88 00 11 FF EC 00 00 33 FF FD CC 00 00 
06F0: 00 11 CC 00 00 00 00 00 11 FC FF FF FD FE FF F7 
0700: FD FF FF FF FF FF FF FB FC F8 FF F8 F0 F1 F0 11 
0710: FF FC FC F1 00 00 FF FF FD FF FF F2 88 FF F7 FF 
0720: FF F8 F3 88 00 11 FF EA 00 00 77 FF FF EC 00 00 
0730: 00 11 FE 00 00 00 00 00 11 FC FF FF FF FF FF FF 
0740: FB FF FF FF FF FF F7 FF FD F9 FF FE F6 F3 F8 11 
0750: FF F9 F9 F9 80 11 FF F7 FD FF FE F5 99 FF FB FF 
0760: FF F0 F3 88 00 30 FF EE 00 00 77 FB FF E8 00 00 
0770: 00 11 FE C0 00 00 00 00 11 FD FF FF FF FF FF FF 
0780: FF FF FF FF FF FF FF FF FF FD FF FD FF F3 FC 33 
0790: FF F7 F9 FB 80 11 FF F1 FF F8 FE F5 99 FF FF FF 
07A0: FE F0 F0 EE 00 31 FF EE 00 00 77 FB FF EA 00 00 
07B0: 00 11 FE C0 00 00 00 00 11 F9 FF FF F7 FF FF FF 
07C0: FF FF FF FC FF FF FF FF FF FE FF F9 FF F7 FE B3 
07D0: FE FF FF FB 80 11 FE F0 F3 FF FE FF 99 FF FF FF 
07E0: FF F1 F5 EE 00 31 FF FE 00 00 FF FE F7 E6 00 00 
07F0: 10 F3 FD F0 00 00 00 00 17 FD FF FF FB FF FF FF 
0800: FF FF FF FF FF FF FF FF FF FF FF F7 FF FF FF F7 
0810: FF FF FF F3 C0 73 FE F0 F3 FF FC FF BB FF FC F7 
0820: FF F1 FF EE 00 F1 FF FC 00 00 FF FE FF FF 00 00 
0830: 10 F3 FB F0 00 00 00 11 F9 FF FF FD FC F3 FF FF 
0840: FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF F3 
0850: FF FF FE FF C0 73 FC F4 FB FF FB FF BB FF FF F7 
0860: FF FB FF FF 88 F3 FF FC 00 10 FF FE FF FF C0 00 
0870: 10 F7 FF F4 80 00 00 32 F8 FF FF F9 FE F1 FF FF 
0880: FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FD 
0890: FF FF FF FF C8 F7 FC F4 FF FF FF FF FF FF FF FB 
08A0: FF FB FF FF 98 FD FF F0 00 30 FF FE F7 FF C0 00 
08B0: 70 FF FF FC 80 00 00 74 F9 F7 FF FF FF F0 FF FF 
08C0: FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FE 
08D0: FF FF FD FF E8 F7 F8 FE FF FF FF FF FF FF FF FD 
08E0: FF FB FF FF F8 FE FE FC E0 30 FF F7 FF FF C0 00 
08F0: 70 FF F7 FC 80 00 00 F8 FB F7 FF FF FF FA FF FF 
0900: FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF 
0910: FF FF FD FF FC F7 F2 FE FF FF FF FF FF FF FF FF 
0920: FF FF FF FF F9 FF FD FE E0 30 FF F7 FF FE C4 00 
0930: 71 F7 F7 FD 80 10 CC F2 FB F7 FF FF FF FF FF FF 
0940: FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF 
0950: FF F9 FB FF FC F7 FF FF F7 FF FF FF FF FF FF FF 
0960: FF FD FF FF FD FF FF FF F0 74 FF F3 FF FE F7 00 
0970: F1 F3 FB FB 80 10 FF FF F3 FB FF FF FF FF FF FF 
0980: FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF 
0990: FF FF FB FF FC FF FF FF FB FF FF FF FF FF FF FF 
09A0: FF FE FF FF FF FF FF F6 F0 F8 FF F7 FF FC F7 CC 
09B0: F3 F7 FF FB C0 30 FF FF F3 FD FF FF FF FF FF FF 
09C0: FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF 
09D0: FF FF FF FF FE FF FF FF FF FF FF FF FF FF FF FF 
09E0: FF FF FF FF FF FF FE FE F0 F0 FF F7 FF FB FF FF 
09F0: FB FB FF F7 FB F9 FF FF FB FF FF FF FF FF FF FF 
0A00: FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF 
0A10: FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF 
0A20: FF FF FF FF FF FF FF FC F0 F0 FC F3 FF FF FF FF 
0A30: FF FF FF F7 FF FF F7 FF FD FF FF FF FF FF FF FF 
0A40: FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF 
0A50: FF FF FF FF FF F7 FF FF FF FF FF FF FF FF FF FF 
0A60: FF FF FF FF FF FF FF F9 F4 F5 FC F7 FF FF FF FE 
0A70: FF FF FF FF FF F7 FF FF FE FF FF FF FF FF FF FF 
0A80: FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF 
0A90: FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF 
0AA0: FF FF FF FF FF FF FF F7 F6 F7 FC FF FF FF FF FD 
0AB0: FF FF FF FF FF F7 FF FF FF FF FF FF FF FF FF FF 
0AC0: FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF 
0AD0: FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF 
0AE0: FF FF FF FF FF FF FF FF FE FF FC F7 FF FF FF FB 
0AF0: FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF 
0B00: FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF 
0B10: FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF 
0B20: FF FF FF FF FF FF FF FF FC FF F8 F7 FF FF FF FF 
0B30: FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF 
0B40: FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF 
0B50: FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF 
0B60: FF FF FF FF FF FF FF FF FB FF F8 F7 FF FF FF FF 
0B70: FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF 
0B80: FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF 
0B90: FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF 
0BA0: FF FF FF FF FF FF FF FF FF FF F8 F1 FF FF FF FF 
0BB0: FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF 
0BC0: FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF 
0BD0: FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF 
0BE0: FF FF FF FF FF FF FF FF FF FF F0 F0 FF FF FF FF 
0BF0: FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF 
0C00: FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF 
0C10: FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF 
0C20: FF FF FF FF FF FF FF FF FF FF F0 F3 FF FF FF FF 
0C30: FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF 
0C40: FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF 
0C50: FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF 
0C60: FF FF FF FF FF FF FF FF FF FF F0 F7 FF FF FF FF 
0C70: FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF 
0C80: FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF 
0C90: FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF 
0CA0: FF FF FF FF FF FF FF FF FF FF F0 F1 FF FF FF FF 
0CB0: FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF 
0CC0: FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF 
0CD0: FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF 
0CE0: FF FF FF FF FF FF FF FF FF FF F0 F0 FF FF FF FF 
0CF0: FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF 
0D00: FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF 
0D10: FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF 
0D20: FF FF FF FF FF FF FF FF FF FF F0 F3 FF FF FF FF 
0D30: FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF 
0D40: FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF 
0D50: FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF 
0D60: FF FF FF FF FF FF FF FF FF FF F4 FF FF FF FF FF 
0D70: FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF 
0D80: FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF 
0D90: FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF 
0DA0: FF FF FF FF FF FF FF FF FF FF F7 FF FF FF FF FF 
0DB0: FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF 
0DC0: FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF 
0DD0: FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF 
0DE0: FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF 
0DF0: FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF 
0E00: FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF 
0E10: FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF 
0E20: FF FF FF FF FF FF FF FF FF FF FF FB FF FF FF FF 
0E30: FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF 
0E40: FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF 
0E50: FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF 
0E60: FF FF FF FF FF FF FF FF FF FF FF F1 FF FF FF FF 
0E70: FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF 
0E80: FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF 
0E90: FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF 
0EA0: FF FF FF FF FF FF FF FF FF FF FE F0 FF FF FF FF 
0EB0: FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF 
0EC0: FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF 
0ED0: FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF 
0EE0: FF FF FF FF FF FF FF FF FF FF FF F3 FF FF FF FF 
0EF0: FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF 
0F00: FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF 
0F10: FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF 
0F20: FF FF FF FF FF FF FF FF FF FF FF FB FF FF FF FF 
0F30: FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF 
0F40: FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF 
0F50: FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF 
0F60: FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF 
0F70: FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF 
0F80: FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF 
0F90: FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF 
0FA0: FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF 
0FB0: FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF 
0FC0: FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF 
0FD0: FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF 
0FE0: FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF 
0FF0: FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF 
```