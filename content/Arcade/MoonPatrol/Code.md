![Moon Patrol](MoonPatrol.jpg)

# Moon Patrol

>>> cpu Z80

| ROM      | Size | Content  | Ofs  | CRC      | SHA1                                     |
| -------- | ---- | -------- | ---- | -------- | ---------------------------------------- |
| mpa-1.3m | 4096 | maincpu  |    0 | 5873a860 | 8c03726d6e049c3edbc277440184e31679f78258 |
| mpa-2.3l | 4096 | maincpu  | 1000 | f4b85974 | dfb2efb57378a20af6f20569f4360cde95596f93 |
| mpa-3.3k | 4096 | maincpu  | 2000 | 2e1a598c | 112c3c9678db8a8540a8df3708020c87fd10c91b |
| mpa-4.3j | 4096 | maincpu  | 3000 | dd05b587 | 727961b0dafa4a96b580d51013336db2a18aff1e |

>>> memoryTable hard 
[Hardware Info](Hardware.md)

>>> memoryTable ram 
[RAM Usage](RAMUse.md)

# START

```code
START: 
; Starts here at power up
;
0000: F3             DI                       ; Disable interrupts
0001: 31 00 E8       LD    SP,$E800           ; Stack builds down from end of RAM
0004: ED 56          IM    1                  ; Interrupt mode 1: IRQ->$38 and NMI->$66
0006: 3A 04 D0       LD    A,($D004)          ;{-2_DSW2} Service mode ...
0009: A7             AND   A                  ; ... switch set?
000A: F2 00 33       JP    P,$3300            ;{ServiceMode} 0=Yes ... go do service mode (not in the same ROM chip but should be)
000D: CD F4 05       CALL  $05F4              ;{ClearRAM} Clear RAM (E000..E6FF)
0010: CD F2 06       CALL  $06F2              ;{ReadSettings} Read the dip-switch settings
0013: CD 29 0D       CALL  $0D29              ; ?? Clear screen, screen flip, clear ram mirror, clear sound queue
0016: C3 68 00       JP    $0068              ;{StartupCont} Continue startup

; Padding to RST 0x28 handler
0019: 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00

; RST 0x28 handler (software interrupt)
; Jump to a specific routine in a table of routines.
; HL = pointer to jumps (2 bytes each)
;  A = routine number in table
;
0028: 87             ADD   A,A                ; A*2 ...
0029: 5F             LD    E,A                ; ... to ...
002A: 16 00          LD    D,$00              ; ... DE
002C: 19             ADD   HL,DE              ; Offset HL
002D: 5E             LD    E,(HL)             ; Read ...
002E: 23             INC   HL                 ; ... jump address ...
002F: 56             LD    D,(HL)             ; ... to DE
0030: EB             EX    DE,HL              ; Into HL for jump
0031: E9             JP    (HL)               ; Jump to routine

; Padding to 0x38 IRQ handler
0032: 00 00 00 00 00 00
```

# IRQ

```code
IRQ: 
; This is triggered every VBLANK ... 56.74Hz.
; -Copy RAM mirror to hardware registers
; -Bump the counters (E04E++, E04F every 16, E050--, E051--)
; -If in service mode twiddle timer, kill time, and out
; -Game mode:
;  -
;
0038: 08             EX    AF,AF'             ; Switch to ...
0039: D9             EXX                      ; ... interrupt-handlers registers
003A: CD 6D 05       CALL  $056D              ;{RegMirror} Copy RAM mirror to hardware at start of VBLANK
;
003D: 21 4E E0       LD    HL,$E04E           ; Counter area
0040: 34             INC   (HL)               ; Bump the counter byte
0041: 7E             LD    A,(HL)             ; Get counter value
0042: 23             INC   HL                 ; Next counter byte
0043: E6 0F          AND   $0F                ; Did we overflow first nibble?
0045: 20 01          JR    NZ,$48             ; No ... skip bumping second
0047: 34             INC   (HL)               ; Increment 2nd counter byte
0048: 23             INC   HL                 ; Next counter byte * J0045
0049: 35             DEC   (HL)               ; -1
004A: 23             INC   HL                 ; Next counter byte
004B: 35             DEC   (HL)               ; -1
;
004C: 3A 04 D0       LD    A,($D004)          ;{-2_DSW2} Are we ...
004F: A7             AND   A                  ; ... in service mode?
0050: FA 93 00       JP    M,$0093            ; No ... process game
;
; Strange twiddling of "timing" counter while in service mode
0053: 21 4E E0       LD    HL,$E04E           ; Point to counter1
0056: 34             INC   (HL)               ; Bump it again (will dec it in 3)
0057: 01 03 00       LD    BC,$0003           ; Count of 3*256
005A: 21 4E E0       LD    HL,$E04E           ; Point to counter1 again
005D: 35             DEC   (HL)               ; Bump back down
;
005E: 10 FE          DJNZ  $5E                ; Inner count 256 * J005E,J0061
0060: 0D             DEC   C                  ; Outer count ...
0061: 20 FB          JR    NZ,$5E             ; ... 3 (3*256 total)
;
0063: D9             EXX                      ; Restore main ...
0064: 08             EX    AF,AF'             ; ... registers
0065: FB             EI                       ; Reenable interrupts (fall into return)
```

# NMI

```code
NMI: 
; Ignored
;
0066: FB             EI                       ; Re-enable interrupts (didn't quite line up with 65)
0067: C9             RET                      ; Ignore

# START (Continued)

StartupCont:
;
;Startup continues here
;
0068: FB             EI                       ; Enable interrupts * J0016,J0120,J01D7
0069: CD 8A 0B       CALL  $0B8A              ; 
006C: 3E 01          LD    A,$01              ;
006E: 32 4D E0       LD    ($E04D),A          ; 
0071: 32 0F E5       LD    ($E50F),A          ; 
0074: 3C             INC   A                  ;
0075: 32 08 E5       LD    ($E508),A          ; 
0078: C3 B7 0B       JP    $0BB7              ; 

007B: 06 00          LD    B,$00              ; * J0504
007D: AF             XOR   A                  ; * J0091
007E: 32 4D E0       LD    ($E04D),A          ; 
0081: 21 46 E0       LD    HL,$E046           ;
0084: 70             LD    (HL),B             ;
0085: FB             EI                       ;
0086: CD 45 07       CALL  $0745              ; 
0089: CD 8A 0B       CALL  $0B8A              ; 
008C: C3 B7 0B       JP    $0BB7              ; 
008F: 06 04          LD    B,$04              ; * J00EF
0091: 18 EA          JR    $7D                ; 

; ISR game specific (not in service mode)
0093: CD CB 05       CALL  $05CB              ;{NextSound} Play next waiting sound (if any) * J0050
0096: 3A 00 D0       LD    A,($D000)          ;{-2_IN0} Coins and start
0099: 2F             CPL                      ; Active high
009A: 32 53 E0       LD    ($E053),A          ;{-1_coinStart} Hold for whoever wants it
009D: CB 4F          BIT   1,A                ; Start-2 pressed?
009F: 28 15          JR    Z,$B6              ; No ... move on
00A1: 3A 04 D0       LD    A,($D004)          ;{-2_DSW2} DSW2
00A4: CB 67          BIT   4,A                ; Stop-mode cheat switch flipped?
00A6: 20 0E          JR    NZ,$B6             ; No ... move on
;
00A8: 21 46 E0       LD    HL,$E046           ; ??
00AB: CB 4E          BIT   1,(HL)             ; ??
00AD: 20 07          JR    NZ,$B6             ; Skip the pause
;
; Stop-mode switch and start-2 pressed (pause game, but not sound)
00AF: 3A 00 D0       LD    A,($D000)          ;{-2_IN0} Start buttons * J00B4
00B2: E6 01          AND   $01                ; Is start-1 pressed?
00B4: 20 F9          JR    NZ,$AF             ; No ... wait for it
;
00B6: 3A 04 D0       LD    A,($D004)          ;{-2_DSW2} DSW2 again * J009F,J00A6,J00AD
00B9: CB 5F          BIT   3,A                ; ?? unused switch
00BB: 20 06          JR    NZ,$C3             ; Not flipped ... move on
00BD: 21 F3 E0       LD    HL,$E0F3           ; Bump ...
00C0: 34             INC   (HL)               ; ... ?? mysterious counter
00C1: CB 46          BIT   0,(HL)             ; ?? Old code left behind? The flags are never used
;
00C3: FD E5          PUSH  IY                 ; Preserve these ... * J00BB,J05B7
00C5: DD E5          PUSH  IX                 ; .. since the others are EXX to safety
00C7: CD 0E 04       CALL  $040E              ;{CoinsAndCredits} Handle coins and credits
00CA: 3A 41 E0       LD    A,($E041)          ;{-1_slotModeA} Coin mode slot A
00CD: A7             AND   A                  ; Free play?
00CE: 20 05          JR    NZ,$D5             ; No ... keep credits
00D0: 3E 02          LD    A,$02              ; Free play ...
00D2: 32 48 E0       LD    ($E048),A          ;{-1_Credits} ... always 2 credits
00D5: 21 46 E0       LD    HL,$E046           ; * J00CE
00D8: 46             LD    B,(HL)             ;
00D9: CB 78          BIT   7,B                ;
00DB: 20 15          JR    NZ,$F2             ; 
00DD: CB 48          BIT   1,B                ;
00DF: 20 1B          JR    NZ,$FC             ; 
00E1: 3A 48 E0       LD    A,($E048)          ;{-1_Credits} 
00E4: A7             AND   A                  ;
00E5: 20 1D          JR    NZ,$104            ; 
00E7: CB 50          BIT   2,B                ;
00E9: 20 11          JR    NZ,$FC             ; 
00EB: 3A 47 E0       LD    A,($E047)          ;{-1_cntTillCred} 
00EE: A7             AND   A                  ;
00EF: C2 8F 00       JP    NZ,$008F           ; 
00F2: CB 40          BIT   0,B                ; * J00DB
00F4: 28 06          JR    Z,$FC              ; Skip game objects
00F6: CD 7A 04       CALL  $047A              ;{GetInputs} Get inputs (or demo mode ??)
00F9: CD EC 01       CALL  $01EC              ;{RunObjects} Run the game objects
00FC: DD E1          POP   IX                 ; Restore IX and ... * J00DF,J00E9,J00F4
00FE: FD E1          POP   IY                 ; ... IY
0100: D9             EXX                      ; Restore the other ...
0101: 08             EX    AF,AF'             ; ... registers
0102: FB             EI                       ; Re-enable interrupts
0103: C9             RET                      ; Done with ISR

0104: 36 02          LD    (HL),$02           ; * J00E5
0106: 31 00 E8       LD    SP,$E800           ;
0109: FB             EI                       ;
010A: CD 29 0D       CALL  $0D29              ; 
010D: CD 33 05       CALL  $0533              ; * J0110
0110: 28 FB          JR    Z,$10D             ; 
0112: CD 38 0B       CALL  $0B38              ; 
0115: C3 B7 0B       JP    $0BB7              ; 
0118: 31 00 E8       LD    SP,$E800           ; * J13F8
011B: 21 46 E0       LD    HL,$E046           ;
011E: 35             DEC   (HL)               ;
011F: FB             EI                       ;
0120: F2 68 00       JP    P,$0068            ;{StartupCont} 
0123: CD 96 0B       CALL  $0B96              ; 
0126: AF             XOR   A                  ;
0127: 32 A6 E1       LD    ($E1A6),A          ; 
012A: 21 15 E5       LD    HL,$E515           ;
012D: 35             DEC   (HL)               ;
012E: 28 1B          JR    Z,$14B             ; 
0130: CD D5 06       CALL  $06D5              ; 
0133: 21 46 E0       LD    HL,$E046           ;
0136: CB 66          BIT   4,(HL)             ;
0138: CA B7 0B       JP    Z,$0BB7            ; 
013B: CD 03 06       CALL  $0603              ;{SwapPlayers} 
013E: 3A 15 E5       LD    A,($E515)          ; 
0141: A7             AND   A                  ;
0142: C2 B7 0B       JP    NZ,$0BB7           ; 
0145: CD 03 06       CALL  $0603              ;{SwapPlayers} 
0148: C3 B7 0B       JP    $0BB7              ; 

014B: 3E 1B          LD    A,$1B              ; Play ... * J012E
014D: CD 75 0D       CALL  $0D75              ;{AddSound} ... ending music
0150: 21 46 E0       LD    HL,$E046           ;
0153: CB 66          BIT   4,(HL)             ;
0155: 28 1F          JR    Z,$176             ; 
0157: 21 ED 2A       LD    HL,$2AED           ; "GAME OVER PLAYER " script
015A: CD 4E 03       CALL  $034E              ;{SlowScript} 
015D: 3A 46 E0       LD    A,($E046)          ; 
0160: 1F             RRA                      ;
0161: 1F             RRA                      ;
0162: 1F             RRA                      ;
0163: E6 01          AND   $01                ;
0165: 3C             INC   A                  ;
0166: CD BD 03       CALL  $03BD              ;{PrintDigit} 
0169: CD 03 06       CALL  $0603              ;{SwapPlayers} 
016C: CD E4 05       CALL  $05E4              ;{Delay1Sec} 
016F: 3A 15 E5       LD    A,($E515)          ; 
0172: A7             AND   A                  ;
0173: C2 B7 0B       JP    NZ,$0BB7           ; 
0176: 21 02 2B       LD    HL,$2B02           ; "GAME OVER" script * J0155
0179: CD 4E 03       CALL  $034E              ;{SlowScript} 
017C: CD 1C 06       CALL  $061C              ;{WhichPlayer} 
017F: 28 03          JR    Z,$184             ; 
0181: CD 03 06       CALL  $0603              ;{SwapPlayers} 
0184: CD E8 05       CALL  $05E8              ;{Delay3Sec} * J017F
0187: CD 29 0D       CALL  $0D29              ; 
018A: 21 2A 2A       LD    HL,$2A2A           ; "TO COUNTINUE GAME" script
018D: CD 00 03       CALL  $0300              ;{RunTextScript} Print it
0190: 3E 11          LD    A,$11              ;
0192: A7             AND   A                  ; * J01AE
0193: 28 3D          JR    Z,$1D2             ; 
0195: 3D             DEC   A                  ;
0196: 27             DAA                      ;
0197: 32 54 E0       LD    ($E054),A          ; 
019A: 11 33 82       LD    DE,$8233           ;
019D: 0E 02          LD    C,$02              ;
019F: CD AE 03       CALL  $03AE              ;{PrintBCD} 
01A2: 3E 40          LD    A,$40              ;
01A4: 32 50 E0       LD    ($E050),A          ;{-1_isrCount3} 
01A7: 3A 50 E0       LD    A,($E050)          ;{-1_isrCount3} * J01BF,J01C4
01AA: A7             AND   A                  ;
01AB: 3A 54 E0       LD    A,($E054)          ; 
01AE: 28 E2          JR    Z,$192             ; 
01B0: 3A 48 E0       LD    A,($E048)          ;{-1_Credits} 
01B3: A7             AND   A                  ;
01B4: 20 0B          JR    NZ,$1C1            ; 
01B6: 21 57 2C       LD    HL,$2C57           ; "INSERT COIN" script
01B9: CD 74 03       CALL  $0374              ;{FlashScript} 
01BC: CD 27 05       CALL  $0527              ;{PrintCreds} 
01BF: 18 E6          JR    $1A7               ; 
01C1: CD 33 05       CALL  $0533              ; * J01B4
01C4: 28 E1          JR    Z,$1A7             ; 
01C6: CD DA 01       CALL  $01DA              ; 
01C9: CD DA 01       CALL  $01DA              ; 
01CC: CD BF 0C       CALL  $0CBF              ; 
01CF: C3 B7 0B       JP    $0BB7              ; 
01D2: F3             DI                       ; * J0193
01D3: AF             XOR   A                  ;
01D4: 32 46 E0       LD    ($E046),A          ; 
01D7: C3 68 00       JP    $0068              ;{StartupCont} 
01DA: 3A 40 E0       LD    A,($E040)          ;{-1_PerCredit} * C01C6,C01C9
01DD: 32 15 E5       LD    ($E515),A          ; 
01E0: 21 00 00       LD    HL,$0000           ;
01E3: 22 00 E5       LD    ($E500),HL         ; 
01E6: 22 02 E5       LD    ($E502),HL         ; 
01E9: C3 03 06       JP    $0603              ;{SwapPlayers} 
```

# RunObjects 

```code
RunObjects: 
; This routine runs up to 32 game object commands in turn. 
; There is room for 32 commands of 16 bytes beginning in the buffer at E300.
; This routine is called every ISR.
;
; The first byte of each object is the command number. A 0 is invalid. 
; The command numbers are indexed in the table beginning with "1".
;
01EC: DD 21 00 E3    LD    IX,$E300           ; Pointer to command buffer (32 slots of 16 bytes) * C00F9
01F0: 3E 20          LD    A,$20              ; 32 command slots
01F2: 32 E8 E0       LD    ($E0E8),A          ; Hold the count
01F5: DD 7E 00       LD    A,(IX+$00)         ; Get the command number * J0209
01F8: 3D             DEC   A                  ; 0 means "invalid"
01F9: FA 00 02       JP    M,$0200            ; Not a valid command. Skip it
01FC: 21 0C 02       LD    HL,$020C           ; Routine jump table table
01FF: EF             RST   0X28               ; Call the routine by index number
0200: 11 10 00       LD    DE,$0010           ; Bytes to next slot * J01F9
0203: DD 19          ADD   IX,DE              ; Point to next slot
0205: 21 E8 E0       LD    HL,$E0E8           ; Get current count
0208: 35             DEC   (HL)               ; Decrement the count
0209: 20 EA          JR    NZ,$1F5            ; Do all 32 slots
020B: C9             RET                      ; Done
```

# Object Commands

```code
ObjectCommands: 
; The calling routine indexes them by subtracting 1 first (0 means invalid).
; Thus they are numbered starting with 1 here.
;
020C: 11 13    ; 01  1311 ISROBJRun_01 Buggy waiting for start
020E: 31 13    ; 02  1331 ISROBJRun_02 Run buggy normally
0210: 70 13    ; 03  1370 ISROBJRun_03 Init buggy jump
0212: 88 13    ; 04  1388 ISROBJRun_04 Handle buggy in air (jumping)
0214: BC 13    ; 05  13BC ISROBJRun_05 Hanlde buggy landing
0216: C2 13    ; 06  13C2 ISROBJRun_06 Init buggy crash
0218: EB 13    ; 07  13EB ISROBJRun_07 Handle buggy crash
021A: 21 14    ; 08  1421 ISROBJRun_08 Hold buggy in air durring splash
021C: 09 18    ; 09  1809 ISROBJRun_09
021E: E0 15    ; 0A  15E0 ISROBJRun_0A Init player forward shot
0220: FA 15    ; 0B  15FA ISROBJRun_0B
0222: 2D 16    ; 0C  162D ISROBJRun_0C
0224: 2D 16    ; 0D  162D ISROBJRun_0D
0226: 49 16    ; 0E  1649 ISROBJRun_0E Init player air shot
0228: 5D 16    ; 0F  165D ISROBJRun_0F
022A: 8F 16    ; 10  168F ISROBJRun_10
022C: 3D 19    ; 11  193D ISROBJRun_11
022E: 57 19    ; 12  1957 ISROBJRun_12
0230: 5E 19    ; 13  195E ISROBJRun_13
0232: D1 19    ; 14  19D1 ISROBJRun_14
0234: 2F 1A    ; 15  1A2F ISROBJRun_15
0236: 44 1A    ; 16  1A44 ISROBJRun_16
0238: 92 1A    ; 17  1A92 ISROBJRun_17
023A: B9 1A    ; 18  1AB9 ISROBJRun_18
023C: F0 1A    ; 19  1AF0 ISROBJRun_19
023E: 01 1B    ; 1A  1B01 ISROBJRun_1A
0240: 27 1B    ; 1B  1B27 ISROBJRun_1B
0242: 33 14    ; 1C  1433 ISROBJRun_1C
0244: E0 18    ; 1D  18E0 ISROBJRun_1D
0246: AA 1E    ; 1E  1EAA ISROBJRun_1E
0248: 28 1F    ; 1F  1F28 ISROBJRun_1F
024A: AC 20    ; 20  20AC ISROBJRun_20
024C: C4 20    ; 21  20C4 ISROBJRun_21
024E: AA 1E    ; 22  1EAA ISROBJRun_22
0250: 28 1F    ; 23  1F28 ISROBJRun_23
0252: 00 20    ; 24  2000 ISROBJRun_24
0254: 1A 20    ; 25  201A ISROBJRun_25
0256: A4 1E    ; 26  1EA4 ISROBJRun_26
0258: 28 1F    ; 27  1F28 ISROBJRun_27
025A: 4D 20    ; 28  204D ISROBJRun_28
025C: 9C 20    ; 29  209C ISROBJRun_29
025E: 23 1D    ; 2A  1D23 ISROBJRun_2A
0260: F3 1D    ; 2B  1DF3 ISROBJRun_2B
0262: 51 1E    ; 2C  1E51 ISROBJRun_2C
0264: 9B 1E    ; 2D  1E9B ISROBJRun_2D
0266: 9B 1C    ; 2E  1C9B ISROBJRun_2E
0268: BC 1C    ; 2F  1CBC ISROBJRun_2F
026A: 14 1E    ; 30  1E14 ISROBJRun_30
026C: 29 1E    ; 31  1E29 ISROBJRun_31
      
; Main loop
;
026E: CD DC 0D       CALL  $0DDC              ; ?? Change terrain
0271: CD 0D 21       CALL  $0D21              ; Draw "point letter" in upper center status window
0274: CD 3A 1B       CALL  $1B3A              ; ?? Start UFO shot
0277: CD C7 1B       CALL  $1BC7              ; ?? Init aliens
027A: CD A7 12       CALL  $12A7              ; ?? Alien sounds
027D: CD E7 12       CALL  $12E7              ; ??
0280: CD DC 0D       CALL  $0DDC              ; ?? Change terrain
```

# Run Text Commands

```code
RunTxtCmds: 
; Run the list of text commands from start to finish
;
0283: 3A CF E1       LD    A,($E1CF)          ;{-1_comListHead} LSB of head of text command list
;
0286: 21 D0 E1       LD    HL,$E1D0           ; Next available text command pointer * J02AB
0289: BE             CP    (HL)               ; Have we reached the end of the list?
028A: 28 E2          JR    Z,$26E             ; Yes ... back to the top
;
028C: 5F             LD    E,A                ; IX ...
028D: 16 E6          LD    D,$E6              ; ... becomes ...
028F: DD 21 00 00    LD    IX,$0000           ; ... E6xx ...
0293: DD 19          ADD   IX,DE              ; ... pointer to current ??command
0295: DD 4E 00       LD    C,(IX+$00)         ; Get command address
0298: CB 21          SLA   C                  ; Two bytes per jump address
029A: 20 11          JR    NZ,$2AD            ; 0 means no-command. Otherwise run it.
```

# Remove Text Command

```code
RemoveTxtCmd: 
; Commands are removed from the head of the list as they go
; inactive. But commands in the middle of the list must wait for earlier 
; commands to be removed before they go away. All commands eventually go
; away, so this works and saves the time spent closing up gaps.
;
029C: 21 CF E1       LD    HL,$E1CF           ; Is this inactive command ...
029F: BE             CP    (HL)               ; .. the first command in the list?
02A0: 20 03          JR    NZ,$2A5            ; No ... the "first" pointer is OK
02A2: C6 04          ADD   $04                ; Remove this command ...
02A4: 77             LD    (HL),A             ; ... from the head of the list
;
; After running, all commands return to here
02A5: DD E5          PUSH  IX                 ; Pointer ... * J02A0
02A7: C1             POP   BC                 ; ... to BC
02A8: 79             LD    A,C                ; LSB plus ...
02A9: C6 04          ADD   $04                ; ... 4 (next object LSB in A)
02AB: 18 D9          JR    $286               ; Loop over all objects in list
;
02AD: 06 00          LD    B,$00              ; Reset command value ... * J029A
02AF: DD 70 00       LD    (IX+$00),B         ; ... so (default) doesn't run again
02B2: DD 7E 01       LD    A,(IX+$01)         ; Parameter data e.g. ISR count or score-adjust
02B5: 21 A5 02       LD    HL,$02A5           ; Return to ...
02B8: E5             PUSH  HL                 ; ... 2A5
02B9: 21 D3 02       LD    HL,$02D3           ; Jump table (back up one entry ... first entry is 1)
02BC: 09             ADD   HL,BC              ; Offset to jump address
02BD: 4E             LD    C,(HL)             ; LSB to C
02BE: 23             INC   HL                 ; SKip over
02BF: 66             LD    H,(HL)             ; MSB to H
02C0: 69             LD    L,C                ; Now LSB to L
02C1: E9             JP    (HL)               ; Jump to routine (return to 2A5)
```

# New Text Command

```code
NewTxtCmd: 
; Add a new text command to the processing list
;   C = Command routine number
;   A = Parameter ... like ISR value for next execution or score adjust
;   E = Text script LSB
;   D = Text script MSB
02C2: 21 D0 E1       LD    HL,$E1D0           ; LSB of next-available text command * J0518,C1528,C1778,C1789,C17A3,J17E7,J19CE,C1DE7,C1E7A
02C5: 6E             LD    L,(HL)             ; Set HL to ...
02C6: 26 E6          LD    H,$E6              ; ... E6xx
02C8: 71             LD    (HL),C             ; Set command number
02C9: 23             INC   HL                 ; Next 
02CA: 77             LD    (HL),A             ; Store text command parameter ... ISR value or score-adjust
02CB: 23             INC   HL                 ; Next
02CC: 73             LD    (HL),E             ; Store ...
02CD: 23             INC   HL                 ; ... text-script ...
02CE: 72             LD    (HL),D             ; ... pointer
02CF: 2C             INC   L                  ; Next
02D0: 7D             LD    A,L                ; New LSB ...
02D1: 32 D0 E1       LD    ($E1D0),A          ;{-1_comListTail} ... of next available text command
02D4: C9             RET                      ; Done

TxtCmdTable:
02D5: 22 06 ; 0622 01 TxtCmd_01 Adjust Score
02D7: FA 02 ; 02FA 02 TxtCmd_02 Run text script
02D9: ED 02 ; 02ED 03 TxtCmd_03 Set timer for next run and run script
02DB: 22 03 ; 0322 04 TxtCmd_04 Run the text-script if it is time
02DD: 2F 03 ; 032F 05 TxtCmd_05 Run the text-script but erase it from screen
02DF: 67 03 ; 0367 06 TxtCmd_06 Init flashing-text process (transition to 7)
02E1: 61 03 ; 0361 07 TxtCmd_07 Flashing-text draw state (transitions to 8)
02E3: 37 03 ; 0337 08 TxtCmd_08 Flashing-text erase state (transitions to 7 or dies after X loops)
02E5: A6 0D ; 0DA6 09 TxtCmd_09 Open crater in ground when alien shot hits
02E7: 01 12 ; 1201 0A TxtCmd_0A Init "MOON PATROL" splash sequence
02E9: 18 12 ; 1218 0B TxtCmd_0B Run "MOON PATROL" splash sequence

02EB: 00 00 ; Room for one more text command

TxtCmd_03:
;
02ED: 3A 4E E0       LD    A,($E04E)          ;{-1_isrCNT_1} Get current ISR value
02F0: DD 86 01       ADD   A,(IX+$01)         ; Add time ...
02F3: DD 77 01       LD    (IX+$01),A         ; ... offset to next run
02F6: DD 36 00 04    LD    (IX+$00),$04       ; Next pass execute the "wait for time" state

TxtCmd_02:
; Run text script from object
;
02FA: DD 6E 02       LD    L,(IX+$02)         ; Get script ... * C036C
02FD: DD 66 03       LD    H,(IX+$03)         ; ... pointer (fall into run)
;
RunTextScript:
; Process a text script pointed to by HL.
; The first 3 bytes of the script are the screen pointer and the color-set number.
;
; Characters from the script are written to the screen, but there are
; special command values:
; $21   ... abort script (return to caller's caller)
; $22   ... set screen cursor (tile and color) and load color
; $23   ... change color value (NEVER USED)
; $24   ... not checked for (NEVER USED)
; $25   ... write a repeated character to screen
; $26   ... 0.3 second delay (NEVER USED)
; $27   ... 0.8 second delay (NEVER USED)
; 
0300: CD DB 03       CALL  $03DB              ; Get screen pointer and color from script * C018D,J0379,C052A,C0548,C074B,C0B47,C0C31,C0C89,C0CEA,C0D06,J1258,C1285,C27EA,C27F3
0303: 7E             LD    A,(HL)             ; Get command * J031B,J0320
0304: 06 12          LD    B,$12              ; 18 ISR delay (0.3 seconds)
0306: FE 26          CP    $26                ; 26 ... 
0308: 28 06          JR    Z,$310             ; ... 0.3 second delay
030A: 06 30          LD    B,$30              ; 48 ISR delay (0.8 seconds)
030C: FE 27          CP    $27                ; 27 ... 0.8 second delay
030E: 20 0D          JR    NZ,$31D            ; Not a delay ... do normal
;
; value 26 ... 0.3 second delay
; value 27 ... 0.8 second delay
0310: 23             INC   HL                 ; Skip delay command value * J0308
0311: 78             LD    A,B                ; Set ISR ...
0312: 32 50 E0       LD    ($E050),A          ;{-1_isrCount3} count down
0315: 3A 50 E0       LD    A,($E050)          ;{-1_isrCount3} ISR counted ... * J0319
0318: A7             AND   A                  ; ... to 0 ?
0319: 20 FA          JR    NZ,$315            ; No ... keep waiting
031B: 18 E6          JR    $303               ; Back to top of loop
;
; Try other special commands
031D: CD C9 03       CALL  $03C9              ;{RunTextScript2} Process normal character or command sequence * J030E
0320: 18 E1          JR    $303               ; Back to top of loop

TxtCmd_04:
; Run the text-script if it is time
;
0322: 3A 4E E0       LD    A,($E04E)          ;{-1_isrCNT_1} Count from ISR
0325: DD BE 01       CP    (IX+$01)           ; Target count value
0328: 28 05          JR    Z,$32F             ;{TxtCmd_05} It is time to run script
032A: DD 36 00 04    LD    (IX+$00),$04       ; Stay in this state (the main run loop clears this)
032E: C9             RET                      ; Done

TxtCmd_05:
; Run the text-script but erase it from screen
;
032F: DD 6E 02       LD    L,(IX+$02)         ; Get the ... * J0328,C033D
0332: DD 66 03       LD    H,(IX+$03)         ; ... script pointer
0335: 18 44          JR    $37B               ;{EraseScript} Erase the script and done

TxtCmd_08:
; Flashing-text erase state
; If the countdown has reached 0 then reinit the countdown,
; erase the script, and transition to state 7. Otherwise just
; transition to state 7. BUT after every erase check to see if 
; the "erase count" has reached zero and let the command die
; when this time expires.
;
0337: 3A 50 E0       LD    A,($E050)          ;{-1_isrCount3} Count-down ...
033A: A7             AND   A                  ; ... reached 0?
033B: 20 0C          JR    NZ,$349            ; No ... go to state 7
033D: CD 2F 03       CALL  $032F              ;{TxtCmd_05} Erase the script
0340: DD 35 01       DEC   (IX+$01)           ; Has this been active for requested time?
0343: C8             RET   Z                  ; Yes. Leave the command "inactive" and pulled from duty
0344: 3E 04          LD    A,$04              ; No. Reset the count-down ...
0346: 32 50 E0       LD    ($E050),A          ;{-1_isrCount3} ... timer to 4 interrupts
0349: DD 36 00 07    LD    (IX+$00),$07       ; Transition to state 7 * J033B
034D: C9             RET                      ; Out

SlowScript:
; Run a text script, but pause between characters. This is used
; in the "between rounds" to show the time and bonus points.
;
034E: CD DB 03       CALL  $03DB              ; Get screen cursor and color 
0351: CD C9 03       CALL  $03C9              ;{RunTextScript2} Process one script command (abort takes us back to caller) * J035F
0354: 3E 03          LD    A,$03              ; Set ...
0356: 32 50 E0       LD    ($E050),A          ;{-1_isrCount3} ... ISR delay
0359: 3A 50 E0       LD    A,($E050)          ;{-1_isrCount3} Has ISR counted ... * J035D
035C: A7             AND   A                  ; ... this down to zero?
035D: 20 FA          JR    NZ,$359            ; No ... wait for zero
035F: 18 F0          JR    $351               ; Keep processing script
;
TxtCmd_07:
; Flashing-text draw state
; If the countdown has reached 0 then reinit the countdown,
; draw the script, and transition to state 8. Otherwise just
; transition to state 8.
;
0361: 3A 50 E0       LD    A,($E050)          ;{-1_isrCount3} Count-down timer ...
0364: A7             AND   A                  ; ... reached zero?
0365: 20 08          JR    NZ,$36F            ; No ... transition to state 8
;
TxtCmd_06:
; Init flashing-text
; Set the interrupt count-down to 4, draw the object, and
; transition to state 8
;
0367: 3E 04          LD    A,$04              ; Set count-down timer ...
0369: 32 50 E0       LD    ($E050),A          ;{-1_isrCount3} ... to 4 interrupts
036C: CD FA 02       CALL  $02FA              ;{TxtCmd_02} Run object script
036F: DD 36 00 08    LD    (IX+$00),$08       ; Transition to state 8 * J0365
0373: C9             RET                      ; Done

FlashScript:
; Print or erase the script alternating every 16 interrupts.
; This produces a flashing effect
;
0374: 3A 4E E0       LD    A,($E04E)          ;{-1_isrCNT_1} ISR up counter * C01B9,C0536
0377: CB 67          BIT   4,A                ; Every 16 interrupts
0379: 20 85          JR    NZ,$300            ;{RunTextScript} Bit set ... print text (bit cleared ... fall into erase)

EraseScript:
; This function runs the script but prints blanks where characters would go.
; This effectively erases whatever text the script put on the screen.
; The set-color command is ignored.
; The repeat-character is ignored.
;
037B: CD DB 03       CALL  $03DB              ; Load cursor and color from script * J0335,J0389,C126D,C1327
037E: 7E             LD    A,(HL)             ; Get next character/command * J038E,J0391
037F: 23             INC   HL                 ; Next in script
0380: FE 21          CP    $21                ; Abort script ...
0382: C8             RET   Z                  ; ... by returning
0383: FE 23          CP    $23                ; Ignore ...
0385: 28 09          JR    Z,$390             ; ... set-color command (Should jump to 38D)
0387: FE 22          CP    $22                ; Set screen cursor ...
0389: 28 F0          JR    Z,$37B             ;{EraseScript} ... and continue script
;
038B: AF             XOR   A                  ; Clear ...
038C: 12             LD    (DE),A             ; ... screen character
038D: 13             INC   DE                 ; Back up one
038E: 18 EE          JR    $37E               ; Keep processing
;
0390: 23             INC   HL                 ; Next in script * J0385
0391: 18 EB          JR    $37E               ; Continue running script

Print3BCD:
; Print a 3 digit BCD number. If the leading digit is 0
; then print blank instead of "0".
; HL points to the MSB of the value (2 bytes)
; DE points to screen
;
0393: 7E             LD    A,(HL)             ; Get BCD number (most significant) * C2977
0394: 13             INC   DE                 ; Skip potentially 0 leading digit
0395: E6 0F          AND   $0F                ; If the lower digit is 0 then ...
0397: 28 04          JR    Z,$39D             ; ... skip printing it
0399: 1B             DEC   DE                 ; We will be printing this digit after all
039A: CD A6 03       CALL  $03A6              ; Print lower BCD digit * C2924,C293A,J296E
039D: 2B             DEC   HL                 ; Next less-significant BCD value * J0397
039E: 7E             LD    A,(HL)             ; Get BCD number
039F: 1F             RRA                      ; Isolate ...
03A0: 1F             RRA                      ; ... upper ...
03A1: 1F             RRA                      ; ... BCD ...
03A2: 1F             RRA                      ; ... digit
03A3: CD A7 03       CALL  $03A7              ; Print digit (without color change)
03A6: 7E             LD    A,(HL)             ; Get BCD number * C039A
03A7: E6 0F          AND   $0F                ; Isolate lower digit * C03A3
03A9: C6 30          ADD   $30                ; Make it ASCII (tile number)
03AB: 12             LD    (DE),A             ; Store it on the screen
03AC: 13             INC   DE                 ; Advance screen pointer
03AD: C9             RET                      ; Done

PrintBCD:
; Print the two digit BCD number in A to screen at DE with color C.
; The cursor DE is incremented with each digit.
;
03AE: FD 21 00 04    LD    IY,$0400           ; Set color memory ... * C019F,J0530,C067E,J2141
03B2: FD 19          ADD   IY,DE              ; ... pointer to same slot as tile pointer
03B4: F5             PUSH  AF                 ; Hold A
03B5: 1F             RRA                      ; Do ...
03B6: 1F             RRA                      ; ... upper ...
03B7: 1F             RRA                      ; ... BCD ...
03B8: 1F             RRA                      ; ... digit
03B9: CD BD 03       CALL  $03BD              ;{PrintDigit} Print digit
03BC: F1             POP   AF                 ; Lower ...
;
PrintDigit:
; Print number digit in A to screen at DE/IY with color C.
;
03BD: E6 0F          AND   $0F                ; ... BDC digit * C0166,C03B9,C213B
03BF: C6 30          ADD   $30                ; Convert to number (ASCII)
;
; Store character A to screen at DE and color C to screen at IY
03C1: 12             LD    (DE),A             ; Store character (tile number) to screen * J03D9,C0408
03C2: FD 71 00       LD    (IY+$00),C         ; Store background to color memory
03C5: 13             INC   DE                 ; Next on screen
03C6: FD 23          INC   IY                 ; Next in color
03C8: C9             RET                      ; Done

RunTextScript2:
; Read a character or command from script pointer (HL) and process it. 
; C is current color value
; DE is pointer to tile memory
; IY is pointer to color memory
;
; $21   ... abort script (return to caller's caller)
; $22   ... set screen cursor (tile and color) and load color
; $23   ... change color value (NEVER USED)
; $24   ... not checked for (NEVER USED)
; $25   ... write a repeated character to screen
;
03C9: 7E             LD    A,(HL)             ; Get command or character from script * C031D,C0351
03CA: 23             INC   HL                 ; Next in script
03CB: FE 21          CP    $21                ; Abort script?
03CD: 28 33          JR    Z,$402             ; Yes ... POP return and abort script
03CF: FE 23          CP    $23                ; Command 23 ...
03D1: 28 12          JR    Z,$3E5             ; ... set color value
03D3: FE 25          CP    $25                ; Command 25 ...
03D5: 28 2D          JR    Z,$404             ; ... write repeated character
03D7: FE 22          CP    $22                ; Command 22 ... set cursor and load color
03D9: 20 E6          JR    NZ,$3C1            ; Normal character (not a command) ... store it to screen
;
; value 22 ... set screen cursor (tile and color) and load color
03DB: 5E             LD    E,(HL)             ; Load ... * C0300,C034E,C037B
03DC: 23             INC   HL                 ; ... the ...
03DD: 56             LD    D,(HL)             ; ... tile memory ...
03DE: 23             INC   HL                 ; ... pointer
03DF: FD 21 00 04    LD    IY,$0400           ; Color is tile ...
03E3: FD 19          ADD   IY,DE              ; ... plus 400
;
; value 23 ... load color value
03E5: 4E             LD    C,(HL)             ; Load color ... * J03D1
03E6: 23             INC   HL                 ; ... from script
;
TransColor:
; There is a different color scheme when on the "champion" course. The
; champion buggy is red and the status window is pink. This routine
; transforms the background color-set value is C as follows:
;
; If E0F9 is 0 then do nothing. Otherwise:
;
; 01 -> 0C (+0B) ?? Used for
; 02 -> 0D (+0B) ?? Used for
; 06 -> 0B (+05) ?? Used for
; 09 -> 0E (+05) ?? Used for
; All other values left alone
;
03E7: 3A F9 E0       LD    A,($E0F9)          ;{-1_champColors} Get champion-color flag * C0678,C06A9,C0CD7,C2135,C2993
03EA: A7             AND   A                  ; If 0 ...
03EB: C8             RET   Z                  ; ... skip color translation
;
; Champion colors transformation
03EC: 79             LD    A,C                ; Color to accumulator
03ED: A7             AND   A                  ; Leave it alone ...
03EE: C8             RET   Z                  ; ... if it is 0
03EF: FE 03          CP    $03                ; Less than 3?
03F1: 38 0B          JR    C,$3FE             ; Yes ... 1 or 2 becomes C or D
03F3: FE 06          CP    $06                ; Value 6?
03F5: 28 03          JR    Z,$3FA             ; Yes ... becomes B
03F7: FE 09          CP    $09                ; Value 9?
03F9: C0             RET   NZ                 ; No ... leave it (9 becomes E)
;
03FA: C6 05          ADD   $05                ; Values 6 and 9 ... * J03F5
03FC: 4F             LD    C,A                ; ... become B and E
03FD: C9             RET                      ; Done
;
03FE: C6 0B          ADD   $0B                ; Values 1 and 2 ... * J03F1
0400: 4F             LD    C,A                ; ... become C and D
0401: C9             RET                      ; Done
;
; value 21 ... abort script (return to caller's caller)
0402: E1             POP   HL                 ; Don't return to script processor * J03CD
0403: C9             RET                      ; Return out of script (abort)
;
; value 25 ... write a repeated character to screen
0404: 46             LD    B,(HL)             ; Get the count * J03D5
0405: 23             INC   HL                 ; Skip count byte
0406: 7E             LD    A,(HL)             ; Get the character value
0407: 23             INC   HL                 ; Skip to next
0408: CD C1 03       CALL  $03C1              ; Write the character/color * J040B
040B: 10 FB          DJNZ  $408               ; Do all loops
040D: C9             RET                      ; Done
```

# Coins and Credits

```code
CoinsAndCredits: 
; Process coins and credits for each coin slot in turn.
;
; Coin slot A comes in on D000. There is also a service-credit button mapped here that
; can be held down for credits. Coin slot B comes in on D002.
;
; When a coin is registered, the slot's hardware coin counter is triggered.
;
040E: 21 3E E0       LD    HL,$E03E           ; Coin and service-credit signal history for slot A * C00C7
0411: 11 41 E0       LD    DE,$E041           ; Slot A coin mode
0414: 3A 00 D0       LD    A,($D000)          ;{-2_IN0} Current switch values
0417: 01 02 00       LD    BC,$0002           ; B=0 (coin counter trigger) C=2 (to trigger counter A)
041A: CD 34 04       CALL  $0434              ; Process coins and credits for slot A
;
041D: 21 3F E0       LD    HL,$E03F           ; Coin and service-credit signal history for slot B
0420: 13             INC   DE                 ; Slot B coin mode
0421: 3A 02 D0       LD    A,($D002)          ;{-2_IN2} Current switch values
0424: 1F             RRA                      ; Make it look like D000
0425: F6 04          OR    $04                ; There is no service-credit for slot B ... turn it off
0427: 0E 20          LD    C,$20              ; C=20 (to trigger counter B)
0429: CD 34 04       CALL  $0434              ; Process coins and credits for slot B
;
042C: 3A 4C E0       LD    A,($E04C)          ;{-1_flipValue} Current flip status
042F: B0             OR    B                  ; OR in coin-counter triggers
0430: 32 01 D0       LD    ($D001),A          ;{-2_FLIP} Trigger hardware coin counters
0433: C9             RET                      ; Done
;
; Look at coin-slot signal history and register coins/credits
; For the coin signal we capture transitions. For the service-credit
; we give a credit every 16 ISRs the button is held down.
0434: 1F             RRA                      ; Service-credit ... * C041A,C0429
0435: 1F             RRA                      ; ... to ...
0436: 1F             RRA                      ; ... bit 0 ...
0437: CB 16          RL    (HL)               ; ... of memory
0439: 1F             RRA                      ; Coin to bit 0 ...
043A: CB 16          RL    (HL)               ; ... service-credit to bit 1
043C: 7E             LD    A,(HL)             ; Get switch value
043D: E6 55          AND   $55                ; Only looking for bit 0 (coin)
043F: FE 54          CP    $54                ; Transitioned from low to high?
0441: 28 0E          JR    Z,$451             ; Yes ... register a coin
0443: 7E             LD    A,(HL)             ; Get switch value
0444: E6 AA          AND   $AA                ; Only looking for bit 1 (service-credit)
0446: C0             RET   NZ                 ; Return if not triggered for 4 loops (debounce)
0447: 21 ED E0       LD    HL,$E0ED           ; Count for number of ISRs that ...
044A: 34             INC   (HL)               ; ... service-credit has been held down
044B: 7E             LD    A,(HL)             ; Held down ...
044C: E6 0F          AND   $0F                ; ... for 16 ISRs?
044E: C0             RET   NZ                 ; No
044F: 18 19          JR    $46A               ; Yes ... add one credit
;
; Register coin
0451: 78             LD    A,B                ; Or in ... * J0441
0452: B1             OR    C                  ; ... bit to trigger ...
0453: 47             LD    B,A                ; ... hardware coin counter
0454: 3E 13          LD    A,$13              ; Play ...
0456: CD 7D 0D       CALL  $0D7D              ;{AddSound2} ... coin sound
0459: 1A             LD    A,(DE)             ; Coin mode
045A: FE 01          CP    $01                ; One-coin = one-play?
045C: 28 11          JR    Z,$46F             ; Yes ... register one credit for this coin
;
; If bit 4 is one then a coin gives multiple credits. 
; Otherwise multiple coins make one credit.
045E: FE 08          CP    $08                ; What do we have multiples of?
0460: 30 0B          JR    NC,$46D            ; Bit 4 is 1 ... multiple credits per coin
0462: 21 47 E0       LD    HL,$E047           ; Get the coins-till-credit counter
0465: 34             INC   (HL)               ; Add a coin
0466: BE             CP    (HL)               ; Enough coins for a credit?
0467: C0             RET   NZ                 ; No ... out
0468: AF             XOR   A                  ; Reset the ...
0469: 77             LD    (HL),A             ; ... coin-till-credit count
046A: 3C             INC   A                  ; Add one ... * J044F
046B: 18 02          JR    $46F               ; ... credit
;
046D: D6 08          SUB   $08                ; Drop the bit 4 and add multiple credits for one coin * J0460
;
; Bump credits
; Max is 99. They get lost after that.
046F: 21 48 E0       LD    HL,$E048           ; Will be using the number-of-credits * J045C,J046B
0472: 86             ADD   A,(HL)             ; Add the new coin credit count
0473: 27             DAA                      ; Adjust to BCD
0474: 30 02          JR    NC,$478            ; Didn't overflow ... keep this value
0476: 3E 99          LD    A,$99              ; Max 99 coins
0478: 77             LD    (HL),A             ; Store the new number of credits * J0474
0479: C9             RET                      ; Done
```

# Get Inputs

```code
GetInputs: 
; Get the player inputs (or demo commands if demo mode).
; The last inputs are moved to E04B.
; Current inputs are in E04A.
; Status of start-buttons is in E049.
;
047A: 3A 46 E0       LD    A,($E046)          ; ??Demo mode flag * C00F6
047D: 07             RLCA                     ; ??Are we in demo mode?
047E: 30 5B          JR    NC,$4DB            ; ??Yes ... go get demo inputs
;
0480: 11 01 D0       LD    DE,$D001           ; Player 1 inputs
0483: CB 67          BIT   4,A                ;
0485: 28 07          JR    Z,$48E             ; 
0487: 3A 43 E0       LD    A,($E043)          ;{-1_cabMode} Cabinet type
048A: 3D             DEC   A                  ; Upright?
048B: 28 01          JR    Z,$48E             ; Yes ... use player 1
048D: 13             INC   DE                 ; Cocktail ... use player 2
048E: 21 4A E0       LD    HL,$E04A           ; Get last ... * J0485,J048B,J04B3
0491: 7E             LD    A,(HL)             ; ... inputs
0492: 23             INC   HL                 ; Remember ...
0493: 77             LD    (HL),A             ; ... last inputs
0494: 2B             DEC   HL                 ; Back to current
0495: 1A             LD    A,(DE)             ; Get inputs from D001 or D002
0496: 2F             CPL                      ; Active high
0497: 77             LD    (HL),A             ; Store them
0498: 2B             DEC   HL                 ; E049
0499: E6 03          AND   $03                ; Keep only the start buttons
049B: 77             LD    (HL),A             ; Store the start buttons
049C: C9             RET                      ; Done

049D: 3A 0B E5       LD    A,($E50B)          ; * J04E4
04A0: 2A F7 E0       LD    HL,($E0F7)         ; 
04A3: BE             CP    (HL)               ;
04A4: 20 13          JR    NZ,$4B9            ; 
04A6: 23             INC   HL                 ;
04A7: 7E             LD    A,(HL)             ;
04A8: 54             LD    D,H                ;
04A9: 5D             LD    E,L                ;
04AA: 23             INC   HL                 ;
04AB: 22 F7 E0       LD    ($E0F7),HL         ; 
04AE: A7             AND   A                  ;
04AF: 28 04          JR    Z,$4B5             ; 
04B1: FE FF          CP    $FF                ;
04B3: 20 D9          JR    NZ,$48E            ; 
04B5: 32 E0 E1       LD    ($E1E0),A          ; * J04AF
04B8: C9             RET                      ;
;
04B9: 21 4A E0       LD    HL,$E04A           ; * J04A4
04BC: 3A E0 E1       LD    A,($E1E0)          ; 
04BF: A7             AND   A                  ;
04C0: 28 13          JR    Z,$4D5             ; 
04C2: 3A 4E E0       LD    A,($E04E)          ;{-1_isrCNT_1} 
04C5: 07             RLCA                     ;
04C6: 47             LD    B,A                ;
04C7: E6 01          AND   $01                ;
04C9: 3C             INC   A                  ;
04CA: 32 49 E0       LD    ($E049),A          ; 
04CD: 78             LD    A,B                ;
04CE: E6 1E          AND   $1E                ;
04D0: 20 03          JR    NZ,$4D5            ; 
04D2: 36 20          LD    (HL),$20           ;
04D4: C9             RET                      ;
;
04D5: 7E             LD    A,(HL)             ; * J04C0,J04D0
04D6: 36 FF          LD    (HL),$FF           ;
04D8: 23             INC   HL                 ;
04D9: 77             LD    (HL),A             ;
04DA: C9             RET                      ;

; Automated inputs
04DB: 21 4D E0       LD    HL,$E04D           ; * J047E
04DE: 3A 4E E0       LD    A,($E04E)          ;{-1_isrCNT_1} ISR incrementing counter
04E1: 47             LD    B,A                ;
04E2: 7E             LD    A,(HL)             ;
04E3: A7             AND   A                  ;
04E4: 28 B7          JR    Z,$49D             ; 
04E6: FE 50          CP    $50                ;
04E8: 28 1D          JR    Z,$507             ; 
04EA: CB 18          RR    B                  ;
04EC: 38 05          JR    C,$4F3             ; 
04EE: CB 18          RR    B                  ;
04F0: 38 01          JR    C,$4F3             ; 
04F2: 34             INC   (HL)               ;
;
04F3: 0E 02          LD    C,$02              ; Value for "left button" * J04EC,J04F0
04F5: 21 49 E0       LD    HL,$E049           ; Current button value spot
04F8: FE 18          CP    $18                ;
04FA: 38 01          JR    C,$4FD             ; 
04FC: 0D             DEC   C                  ; Now value for "right button"
04FD: 71             LD    (HL),C             ; Store left or right button down * J04FA
04FE: 23             INC   HL                 ; Point to last inputs
04FF: 36 00          LD    (HL),$00           ; Last inputs now 00 (triggers a transition)
0501: FE B0          CP    $B0                ;
0503: D8             RET   C                  ;
0504: C3 7B 00       JP    $007B              ; 
;
0507: 21 00 E3       LD    HL,$E300           ; MoonBuggy object * J04E8
050A: 7E             LD    A,(HL)             ; Get the current command
050B: FE 04          CP    $04                ; Is the buggy in the air?
050D: 20 0C          JR    NZ,$51B            ; No ... move on
050F: 3A 09 E3       LD    A,($E309)          ; 
0512: 17             RLA                      ;
0513: D8             RET   C                  ; ?? falls through when jump buggy is at apex
0514: 36 08          LD    (HL),$08           ; Transition to "hold buggy in air" sequence
0516: 0E 0A          LD    C,$0A              ; Init "MOOD PATROL" splash sequence
0518: C3 C2 02       JP    $02C2              ;{NewTxtCmd} Add the text-command and out


051B: FE 08          CP    $08                ; Buggy-held-in-air sequence? * J050D
051D: C8             RET   Z                  ; Yes ... no inputs
;
051E: 21 4A E0       LD    HL,$E04A           ; Current inputs
0521: 36 20          LD    (HL),$20           ; Current input is a JUMP
0523: 23             INC   HL                 ; Last input is ...
0524: 36 00          LD    (HL),$00           ; ... nothing (register transition)
0526: C9             RET                      ; Done
```

# Print Credits

```code
PrintCreds: 
0527: 21 E2 2A       LD    HL,$2AE2           ; "CREDIT " script * C01BC,C0539,C074E
052A: CD 00 03       CALL  $0300              ;{RunTextScript} Print it
052D: 3A 48 E0       LD    A,($E048)          ;{-1_Credits} Number of credits
0530: C3 AE 03       JP    $03AE              ;{PrintBCD} Print it and out

0533: 21 D1 2A       LD    HL,$2AD1           ; " PUSH BUTTON " script * C010D,C01C1
0536: CD 74 03       CALL  $0374              ;{FlashScript} Print the flashing script
0539: CD 27 05       CALL  $0527              ;{PrintCreds} Print number of credits
053C: 21 86 2A       LD    HL,$2A86           ; "ONLY 1 PLAYER" script
053F: 3A 48 E0       LD    A,($E048)          ;{-1_Credits} Number of credits
0542: 3D             DEC   A                  ; Only one player?
0543: 28 03          JR    Z,$548             ; Yes ... leave this message
0545: 21 97 2A       LD    HL,$2A97           ; "1 OR 2 PLAYERS" script
0548: CD 00 03       CALL  $0300              ;{RunTextScript} Print it * J0543
054B: 3A 53 E0       LD    A,($E053)          ;{-1_coinStart} 
054E: E6 03          AND   $03                ;
0550: C8             RET   Z                  ;
0551: 1F             RRA                      ;
0552: 3A 48 E0       LD    A,($E048)          ;{-1_Credits} 
0555: 06 80          LD    B,$80              ;
0557: 38 06          JR    C,$55F             ; 
0559: D6 01          SUB   $01                ;
055B: 27             DAA                      ;
055C: C8             RET   Z                  ;
055D: 06 90          LD    B,$90              ;
055F: D6 01          SUB   $01                ; * J0557
0561: 27             DAA                      ;
0562: F3             DI                       ;
0563: 32 48 E0       LD    ($E048),A          ;{-1_Credits} 
0566: 78             LD    A,B                ;
0567: 32 46 E0       LD    ($E046),A          ; 
056A: 3C             INC   A                  ;
056B: FB             EI                       ;
056C: C9             RET                      ;

RegMirror:
; Called from ISR to copy memory to hardware.
; E100..E13F to C840..C87F (40 bytes, 16 sprites)
; E140..E15F to C820..C83F (20 bytes, 8 sprites)
; E160..E19F to C8C0..C8FF (40 bytes, 16 sprites)
; E1A0..E1BF to C8A0..C8BF (20 bytes, 8 sprites)
; E1C0 -> 1C, 1D, 1E, 1F (last 4 scroll registers)
; E1C1 -> 40 BKG1X
; E1C2 -> 80 BKG2X
; E1C3 -> 60 BKG1Y
; E1C4 -> A0 BKG2Y
; E1C5 -> C0 BkgControl
;
056D: 21 00 E1       LD    HL,$E100           ; Start of mirror memory * C003A
0570: 11 40 C8       LD    DE,$C840           ; ?? Sprite memory Enemy ships and rocks
0573: 01 40 00       LD    BC,$0040           ; 40 bytes, 16 sprites
0576: ED B0          LDIR                     ; E100..E13F to C840..C87F (40 bytes, 16 sprites)
;
0578: 1E 20          LD    E,$20              ; Sprite memory
057A: 0E 20          LD    C,$20              ; 20 bytes
057C: ED B0          LDIR                     ; E140..E15F to C820..C83F (20 bytes, 8 sprites)
;
057E: 1E C0          LD    E,$C0              ; Sprite memory
0580: 0E 40          LD    C,$40              ; 40 bytes
0582: ED B0          LDIR                     ; E160..E19F to C8C0..C8FF (40 bytes, 16 sprites)
;
0584: 11 A0 C8       LD    DE,$C8A0           ; ?? Sprite memory Buggy, wheels, forward shot
0587: 0E 20          LD    C,$20              ; 20 bytes
0589: ED B0          LDIR                     ; E1A0..E1BF to C8A0..C8BF (20 bytes, 8 sprites)
;
058B: 0E 1C          LD    C,$1C              ; Copy ...
058D: 7E             LD    A,(HL)             ; ... E1C0 ...
058E: 06 04          LD    B,$04              ; ... to ...
0590: ED 79          OUT   (C),A              ; ... last ... * J0593
0592: 0C             INC   C                  ; ... four ...
0593: 10 FB          DJNZ  $590               ; ... scroll registers
;
0595: 23             INC   HL                 ; Now E1C1
0596: 3A C3 E1       LD    A,($E1C3)          ; Value destined for BKG1Y
0599: A7             AND   A                  ; ?? 1Y is 0?
059A: 28 2B          JR    Z,$5C7             ; Change to FF and disable all backgrounds
;
059C: 7E             LD    A,(HL)             ; Value to be written to BKG1X.
059D: E6 7F          AND   $7F                ; ... The "protection" chip returns a ...
059F: 01 40 00       LD    BC,$0040           ; ... mangled ...
05A2: CB 3F          SRL   A                  ; ... value based on ... * J05A7
05A4: 30 01          JR    NC,$5A7            ; ... the value ...
05A6: 04             INC   B                  ; ... written to ...
05A7: 20 F9          JR    NZ,$5A2            ; ... BKG1X. We ... * J05A4
05A9: 7E             LD    A,(HL)             ; ... calculate ...
05AA: 07             RLCA                     ; ... what ...
05AB: E6 01          AND   $01                ; ... it ...
05AD: A8             XOR   B                  ; ... should ...
05AE: 5F             LD    E,A                ; ... return
05AF: ED A3          OUTI                     ; From E1C1 to port 40 (BKG1X) 
05B1: 3A 00 88       LD    A,($8800)          ;{-2_PROTECT} Get mangled bkg1X from protection
05B4: E6 07          AND   $07                ; Keep lower 3 bits
05B6: BB             CP    E                  ; Make sure protection chip did its thing
05B7: C2 C3 00       JP    NZ,$00C3           ; Protection chip failed
05BA: 0E 80          LD    C,$80              ; BKG2X
05BC: ED A3          OUTI                     ; From E1C2 to port 80 (BKG2X)
05BE: 0E 60          LD    C,$60              ; BKG1Y
05C0: ED A3          OUTI                     ; From E1C3 to port 60 (BKG1Y)
05C2: 0E A0          LD    C,$A0              ; BKG2Y
05C4: ED A3          OUTI                     ; From E1C4 to port A0 (BKG2Y) 
05C6: 7E             LD    A,(HL)             ; From E1C5 (to BkgControl)
05C7: 2F             CPL                      ; Reverse bits to active high * J059A
05C8: D3 C0          OUT   ($C0),A            ;{-2_BKGCtrl} Turn selected backgrounds on
05CA: C9             RET                      ; Done

NextSound:
; Plays next sound from 7 byte sound-effect queue. E1DD is the LSB of the next
; to play (the front). E1DE is the LSB of the next available (the back).
; The queue itself is in RAM from E000..E007 (8 entries).
;
; If the front and back are the same pointer then nothing happens. Otherwise the
; value from the front is sent to the sound processor and the front is bumped
; and wrapped.
;
; Thanks to Leo Bodnar for explaining the sound-command sequence.
; The main CPU address D000 (write) is connected to the sound CPU's AY0 sound chip general I/O.
; The upper most bit triggers the IRQ on the sound CPU. The main CPU writes the command to D000
; and toggles the upper bit of D000 bit low then high. The sound CPU clears the IRQ by accessing
; memory $9xxx.
; 
05CB: 2A DD E1       LD    HL,($E1DD)         ;{-1_SndQFront} Get front (L) and back (H) of sound effect queue pointer * C0093
05CE: 7D             LD    A,L                ; Head and tail ...
05CF: BC             CP    H                  ; ... the same?
05D0: C8             RET   Z                  ; Yes ... nothing to queue up
05D1: 26 E0          LD    H,$E0              ; MSB is E0
05D3: 7E             LD    A,(HL)             ; Get sound effect number from
05D4: 32 00 D0       LD    ($D000),A          ; Write sound command with IRQ triggered (D7=0)
05D7: CB FF          SET   7,A                ; Release the IRQ ...
05D9: 32 00 D0       LD    ($D000),A          ; ... trigger D7=1
05DC: 7D             LD    A,L                ; Bump to the ...
05DD: 3C             INC   A                  ; ... next effect in the queue
05DE: E6 07          AND   $07                ; Only 8 bytes in queue ... then we wrap
05E0: 32 DD E1       LD    ($E1DD),A          ;{-1_SndQFront} Store the updated front
05E3: C9             RET                      ; Done

Delay1Sec:
; Set countdown timer to 1 second and wait for it
05E4: 3E 40          LD    A,$40              ; About 1 second * C016C
05E6: 18 02          JR    $5EA               ; Wait for it and return

Delay3Sec:
; Set countdown timer to 3 seconds and wait for it.
05E8: 3E C0          LD    A,$C0              ; About 3 seconds * C0184,J0794,C27E4,C2889,C288E,C28BA
05EA: 32 50 E0       LD    ($E050),A          ;{-1_isrCount3} Set countdown timer * J05E6,C2859,C286E
05ED: 3A 50 E0       LD    A,($E050)          ;{-1_isrCount3} Wait for ... * J05F1
05F0: A7             AND   A                  ; ... count to ...
05F1: 20 FA          JR    NZ,$5ED            ; ... reach 0
05F3: C9             RET                      ; Done

ClearRAM:
; Clear RAM from $E000-E6FF.
;
05F4: 21 00 E0       LD    HL,$E000           ; Point to start of RAM * C000D
05F7: 01 00 07       LD    BC,$0700           ; Number of bytes to clear
05FA: 36 00          LD    (HL),$00           ; Clear location * J0600,C0BBD,C0C9E,C0D2F,C0D38,C294E,J2957,C2960
05FC: 23             INC   HL                 ; Next in RAM
05FD: 0B             DEC   BC                 ; Decrement counter
05FE: 78             LD    A,B                ; Is counter ...
05FF: B1             OR    C                  ; ... all 0's?
0600: 20 F8          JR    NZ,$5FA            ; No ... keep clearing
0602: C9             RET                      ; Done

SwapPlayers:
; This function swaps the data structures for the players as they
; alternate playing.
;
0603: 21 46 E0       LD    HL,$E046           ; Game mode * C013B,C0145,C0169,C0181,J01E9,C0C95,C0CFA,C0D00
0606: 7E             LD    A,(HL)             ; Get game mode
0607: EE 08          XOR   $08                ; Change ...
0609: 77             LD    (HL),A             ; ... players
060A: 21 00 E5       LD    HL,$E500           ; Pointer to current player
060D: 11 18 E5       LD    DE,$E518           ; Pointer to "other" player
0610: 06 18          LD    B,$18              ; 24 bytes to swap
;
0612: 1A             LD    A,(DE)             ; From other player * J0619
0613: 4F             LD    C,A                ; Now in C
0614: 7E             LD    A,(HL)             ; From current player
0615: 12             LD    (DE),A             ; Swap current ...
0616: 71             LD    (HL),C             ; ... and other player data
0617: 23             INC   HL                 ; Next in current
0618: 13             INC   DE                 ; Next in other
0619: 10 F7          DJNZ  $612               ; Do all 24 bytes
061B: C9             RET                      ; Done

WhichPlayer:
; Check the game-mode "player" bit.
; Return Z if player 1
; Return NZ if player 2
;
061C: 3A 46 E0       LD    A,($E046)          ; Get game-mode * C017C,C066B
061F: CB 5F          BIT   3,A                ; Test value of bit-3
0621: C9             RET                      ; Return in Z flag

TxtCmd_01:
; Adjust Score
; Lookup A in 6-digit score add table and add value to score
; if not in demo mode. Update the current score on the
; screen (player 1 or player 2) and update the high-score
; and high-passed-point on the screen. Handle extended-play.
;
0622: 4F             LD    C,A                ; A = A * 3 ...
0623: 81             ADD   A,C                ; ... three byte add ...
0624: 81             ADD   A,C                ; ... for 6-digit BCD
0625: 4F             LD    C,A                ; Now to ...
0626: 06 00          LD    B,$00              ; ... BC
0628: 21 0C 2A       LD    HL,$2A0C           ; Offset into ...
062B: 09             ADD   HL,BC              ; ... score table 
062C: 3A 46 E0       LD    A,($E046)          ; Game mode
062F: A7             AND   A                  ; Are we in demo mode?
0630: F0             RET   P                  ; Yes ... don't register score
;
0631: 11 00 E5       LD    DE,$E500           ; Score for current player
0634: 06 03          LD    B,$03              ; Do three bytes (6 digits)
0636: A7             AND   A                  ; Clear carry for first pass * C2899
0637: 1A             LD    A,(DE)             ; Add current value ... * J063D
0638: 8E             ADC   A,(HL)             ; ... to score offset
0639: 27             DAA                      ; Adjust to BCD value
063A: 12             LD    (DE),A             ; New current value
063B: 13             INC   DE                 ; Next in value
063C: 23             INC   HL                 ; Next in offset
063D: 10 F8          DJNZ  $637               ; Do all digits
063F: CD AF 06       CALL  $06AF              ;{CheckExtPlay} Check and handle extended play
;
0642: 06 03          LD    B,$03              ; Three bytes (six digits)
0644: 11 00 E5       LD    DE,$E500           ; Current score
0647: 21 08 E0       LD    HL,$E008           ; High Score
064A: A7             AND   A                  ; Start with clear carry
064B: 1A             LD    A,(DE)             ; Compare current ... * J064F
064C: 9E             SBC   (HL)               ; ... to high score
064D: 23             INC   HL                 ; Next in high
064E: 13             INC   DE                 ; Next in current
064F: 10 FA          DJNZ  $64B               ; Compare all digits
0651: 38 15          JR    C,$668             ; Current score is lower ... don't update high score
;
0653: 2A 00 E5       LD    HL,($E500)         ; Copy ...
0656: 22 08 E0       LD    ($E008),HL         ;{-1_highScore} ... current score ...
0659: 3A 02 E5       LD    A,($E502)          ; ... to ...
065C: 32 0A E0       LD    ($E00A),A          ;{-1_highScore2} ... high score
;
065F: 3A 0E E5       LD    A,($E50E)          ; Current passed-point
0662: 32 0B E0       LD    ($E00B),A          ;{-1_highPoint} Copy to high passed-point
0665: CD 85 06       CALL  $0685              ;{PrintHigh} Print high-score and high-passed-point
;
0668: 11 84 80       LD    DE,$8084           ; Player 1's score on screen * J0651,C0CED,C0CFD
066B: CD 1C 06       CALL  $061C              ;{WhichPlayer} Player 1 or 2?
066E: 28 03          JR    Z,$673             ; This is player 1 ... we have the right screen location
0670: 11 A4 80       LD    DE,$80A4           ; Player 2's score on screen (+32 ... one row)
0673: 21 02 E5       LD    HL,$E502           ; * J066E
0676: 0E 01          LD    C,$01              ; Color set
0678: CD E7 03       CALL  $03E7              ;{TransColor} Translate colors
;
067B: 06 03          LD    B,$03              ; Three bytes to print * J06AD
067D: 7E             LD    A,(HL)             ; Get BCD double digit * J0682
067E: CD AE 03       CALL  $03AE              ;{PrintBCD} Print two digits to screen at DE
0681: 2B             DEC   HL                 ; Back up a byte (these are stored in memory LSB first)
0682: 10 F9          DJNZ  $67D               ; Do all digits
0684: C9             RET                      ; Out
```

# Print High Score

```code
PrintHigh: 
; Print the high-score and high-passed-point.
; The color is different for champion course
0685: 21 0B E0       LD    HL,$E00B           ; Location of high passed-point * C0665,C0CF0
0688: 7E             LD    A,(HL)             ; Get high passed-point
0689: 0E 09          LD    C,$09              ; Color for 1st pass through letters
068B: FE 1B          CP    $1B                ; Rolled past letter 'Z' ?
068D: 38 04          JR    C,$693             ; No ... keep it
068F: D6 1A          SUB   $1A                ; Roll back around
0691: 0E 06          LD    C,$06              ; Color for 2nd pass through letters
0693: C6 40          ADD   $40                ; Becomes an ASCII letter * J068D
0695: 32 4A 80       LD    ($804A),A          ; Store it to screen
0698: 3A F9 E0       LD    A,($E0F9)          ;{-1_champColors} Champion ...
069B: 1F             RRA                      ; ... course?
069C: 79             LD    A,C                ; Color 
069D: 30 02          JR    NC,$6A1            ; Normal colors
069F: C6 05          ADD   $05                ; Champion colors
06A1: 32 4A 84       LD    ($844A),A          ; Set the color of the high passed-point character * J069D
;
06A4: 11 43 80       LD    DE,$8043           ; Location of high-score on screen
06A7: 0E 09          LD    C,$09              ; Color set
06A9: CD E7 03       CALL  $03E7              ;{TransColor} Do color translation
06AC: 2B             DEC   HL                 ; Back up to MSB of high score (E00A)
06AD: 18 CC          JR    $67B               ; Print high score digits to screen and out

CheckExtPlay:
; Check and handle extended play based on current score.
;
06AF: 2A 01 E5       LD    HL,($E501)         ; * C063F
06B2: 3A 45 E0       LD    A,($E045)          ;{-1_extPoints} Extra points setting
06B5: 3D             DEC   A                  ;
06B6: F8             RET   M                  ;
06B7: 3D             DEC   A                  ;
06B8: 28 01          JR    Z,$6BB             ; 
06BA: 24             INC   H                  ;
06BB: CB 2C          SRA   H                  ; * J06B8
06BD: 25             DEC   H                  ;
06BE: 3C             INC   A                  ;
06BF: 7C             LD    A,H                ;
06C0: 20 05          JR    NZ,$6C7            ; 
06C2: A7             AND   A                  ;
06C3: 28 02          JR    Z,$6C7             ; 
06C5: 3E FE          LD    A,$FE              ;
06C7: 21 03 E5       LD    HL,$E503           ; * J06C0,J06C3
06CA: BE             CP    (HL)               ;
06CB: C0             RET   NZ                 ;
06CC: 7E             LD    A,(HL)             ;
06CD: FE 03          CP    $03                ;
06CF: C8             RET   Z                  ;
06D0: 34             INC   (HL)               ;
06D1: 21 15 E5       LD    HL,$E515           ;
06D4: 34             INC   (HL)               ;
06D5: 3A 15 E5       LD    A,($E515)          ; * C0130,C0D09
06D8: 3D             DEC   A                  ;
06D9: 28 03          JR    Z,$6DE             ; 
06DB: 4F             LD    C,A                ;
06DC: 3E 01          LD    A,$01              ;
06DE: 21 7C 80       LD    HL,$807C           ; * J06D9
06E1: CD EC 06       CALL  $06EC              ; 
06E4: CD EC 06       CALL  $06EC              ; 
06E7: 28 03          JR    Z,$6EC             ; 
06E9: 79             LD    A,C                ;
06EA: C6 30          ADD   $30                ;
06EC: 77             LD    (HL),A             ; * C06E1,C06E4,J06E7
06ED: 23             INC   HL                 ;
06EE: A7             AND   A                  ;
06EF: C8             RET   Z                  ;
06F0: 3C             INC   A                  ;
06F1: C9             RET                      ;

ReadSettings:
; E040  lives-per-credit (1,2,3, or 5)
; E041  coin mode slot A
; E042  coin mode slot B
; E043  cabinet mode (1=UPRIGHT, 0=TABLE)
; E044  slot mode (1=two slots, 0=one slot)
; E045  extended points
;
; The logic for the coin modes is easier to understand with tables:
;
; 1 Slot coin mode settings
;
; DIP   Effect   NEG-DIP
; 0000  FREE      0000      =   0_000 note 1 -- becomes FREE PLAY
; 0001  *1C-8P    1111    +1= 1_0_000 note 2 -- becomes 1C-8P
; 0010   1C-7P    1110    +1=   1_111 Multi-play count 7
; 0011   1C-6P    1101    +1=   1_110                  6
; 0100   1C-5P    1100    +1=   1_101                  5
; 0101   1C-4P    1011    +1=   1_100                  4
; 0110   1C-3P    1010    +1=   1_011                  3
; 0111   1C-2P    1001    +1=   1_010                  2
; 1000 * 1C-1P   1000    +1=   1_001                  1 This option not available in MAME
; 1001 * 7C-1P    0111          0_111 Multi-coin count 7
; 1010   6C-1P    0110          0_110                  6
; 1011   5C-1P    0101          0_101                  5
; 1100   4C-1P    0100          0_100                  4
; 1101   3C-1P    0011          0_001                  3
; 1110   2C-1P    0010          0_010                  2
; 1111   1C-1P    0001          0_001                  1
;
; note 1:
; The logic at 0719 checks bit 3 before adding one. Thus this value
; remains 0. At 00CA the ISR checks this for 0 and sets the number
; of credits to 2 (FREE PLAY). 
;
; note 2:
; The logic at 045E compares to 8 instead of looking at bit. This falls into
; multi-play. The logic drops the flag bit by subtracting 8. Thus 16-8=8.
;
;
; 2 Slot coin mode for A
; DIP     Effect    NEG-DIP
; xx00               xx00    0_000 See note 1 -- becomes FREE PLAY
; xx01    3C-1P      xx11    0_011 Multi-coin count 3
; xx10    2C-1P      xx10    0_010                  2
; xx11    1C-1P      xx01    0_001                  1
;
; 2 Slot coin mode for B
;                   CPL-DIP
; 00xx               11xx    11-F5   = 1_110 Multi-play count 6
; 01xx               10xx    10-F5   = 1_101                  5
; 10xx               01xx    01-F5-1 = 1_011                  3
; 11xx               00xx    00-F5-1 = 1_010                  2
;
06F2: 21 40 E0       LD    HL,$E040           ; Holds lives-per-credit * C0010
06F5: 3A 03 D0       LD    A,($D003)          ;{-2_DSW1} Read the number of lives-per-credit
06F8: 47             LD    B,A                ; Hold original in B
06F9: 3C             INC   A                  ; Value is now 1,2,3, 4
06FA: E6 03          AND   $03                ; Is it 1,2, or 3?
06FC: 20 02          JR    NZ,$700            ; Yes ... keep 1,2, or 3
06FE: 3E 05          LD    A,$05              ; 4 becomes 5 lives
0700: 77             LD    (HL),A             ; Store lives-per-credit; * J06FC
0701: 23             INC   HL                 ; E041 (holds coin mode for slot A)
;
0702: 78             LD    A,B                ; Original port value just read
0703: 0F             RRCA                     ; Skip over ...
0704: 0F             RRCA                     ; ... number of lives-per-credit
0705: 47             LD    B,A                ; Drop num-cars field from the original value
0706: E6 03          AND   $03                ; Store ...
0708: 32 45 E0       LD    ($E045),A          ;{-1_extPoints} ... extended points field
;
070B: 3A 04 D0       LD    A,($D004)          ;{-2_DSW2} Get ...
070E: CB 57          BIT   2,A                ; ... coin mode
0710: 78             LD    A,B                ; original value
0711: 28 1F          JR    Z,$732             ; In modeB (two different slot currencies)
;
; Decode coin mode A (one slot)
0713: 1F             RRA                      ; Drop the ...
0714: 1F             RRA                      ; ... extended points field
;
0715: ED 44          NEG                      ; A = 0-A. Make active high then add one
0717: E6 0F          AND   $0F                ; Only 4 bits in coin modes
0719: CB 5F          BIT   3,A                ; Multi plays per coin?
071B: 28 01          JR    Z,$71E             ; No ... leave the value alone.
071D: 3C             INC   A                  ; Multi-plays-per-coin value goes 1-7 with 0 and 1 on the end 
071E: 77             LD    (HL),A             ; Store coin mode slot A * J071B
071F: 23             INC   HL                 ; E042 ... mode for slot B * J0743
0720: 77             LD    (HL),A             ; Same coin mode for slot B
;
0721: 3A 04 D0       LD    A,($D004)          ;{-2_DSW2} Various settings
0724: 2F             CPL                      ; Active 1 now
0725: 1F             RRA                      ; Skip the "flip screen" bit
0726: 47             LD    B,A                ; Hold new value
0727: E6 01          AND   $01                ; Cabinet mode
0729: 23             INC   HL                 ; Store cabinet mode ...
072A: 77             LD    (HL),A             ; ... to E043
072B: 78             LD    A,B                ; Original value
072C: 1F             RRA                      ; Skip the "cabinet" bit
072D: E6 01          AND   $01                ; Slot mode
072F: 23             INC   HL                 ; Store slot mode ...
0730: 77             LD    (HL),A             ; ... to E044
0731: C9             RET                      ; Done
;
; Decode coin mode B (two slots)
0732: 1F             RRA                      ; Skip the ... * J0711
0733: 1F             RRA                      ; ... extended points field
0734: 2F             CPL                      ; Straight reverse now
0735: 47             LD    B,A                ; Hold this
0736: 3C             INC   A                  ; NOW make it NEG like in 1 coin mode
0737: E6 03          AND   $03                ; Keep lower 2 bits. This is a multi-coin-per-play setting
0739: 77             LD    (HL),A             ; Store coin mode
073A: 78             LD    A,B                ; Complimented value
073B: 1F             RRA                      ; Drop ...
073C: 1F             RRA                      ; ... slot A bits
073D: E6 03          AND   $03                ; Only 2 bits
073F: FE 02          CP    $02                ; This becomes a ...
0741: DE F5          SBC   $F5                ; ... multi-play-per-coin setting
0743: 18 DA          JR    $71F               ; Store it


0745: CD 29 0D       CALL  $0D29              ; * C0086
0748: 21 97 2C       LD    HL,$2C97           ; "1982 IREM CORP" script
074B: CD 00 03       CALL  $0300              ;{RunTextScript} 
074E: CD 27 05       CALL  $0527              ;{PrintCreds} 
0751: 21 57 2C       LD    HL,$2C57           ; "INSERT COIN" script
0754: CD 4E 03       CALL  $034E              ;{SlowScript} 
0757: 11 54 E0       LD    DE,$E054           ;
075A: 01 20 00       LD    BC,$0020           ;
075D: 3A 44 E0       LD    A,($E044)          ;{-1_slotMode} 
0760: A7             AND   A                  ;
0761: 20 34          JR    NZ,$797            ; 
0763: CD 9F 07       CALL  $079F              ; 
0766: CD E8 07       CALL  $07E8              ; 
0769: 7E             LD    A,(HL)             ;
076A: FE 32          CP    $32                ;
076C: 20 20          JR    NZ,$78E            ; 
076E: 3E 53          LD    A,$53              ;
0770: 32 5F E0       LD    ($E05F),A          ; 
0773: 32 68 E0       LD    ($E068),A          ; 
0776: 21 62 E0       LD    HL,$E062           ;
0779: 7E             LD    A,(HL)             ;
077A: 87             ADD   A,A                ;
077B: D6 30          SUB   $30                ;
077D: FE 3A          CP    $3A                ;
077F: 38 06          JR    C,$787             ; 
0781: D6 0A          SUB   $0A                ;
0783: 77             LD    (HL),A             ;
0784: 2B             DEC   HL                 ;
0785: 3E 31          LD    A,$31              ;
0787: 77             LD    (HL),A             ; * J077F
0788: 21 54 E0       LD    HL,$E054           ; * J079D
078B: CD 4E 03       CALL  $034E              ;{SlowScript} 
078E: 3A 47 E0       LD    A,($E047)          ;{-1_cntTillCred} * J076C,J0792
0791: A7             AND   A                  ;
0792: 20 FA          JR    NZ,$78E            ; 
0794: C3 E8 05       JP    $05E8              ;{Delay3Sec} 
0797: CD D3 07       CALL  $07D3              ; * J0761
079A: CD DD 07       CALL  $07DD              ; 
079D: 18 E9          JR    $788               ; 
079F: 21 67 2C       LD    HL,$2C67           ; "1 PLAYER 1 COIN" script * C0763
07A2: ED B0          LDIR                     ;
07A4: 21 57 E0       LD    HL,$E057           ;
07A7: 3A 41 E0       LD    A,($E041)          ;{-1_slotModeA} * J07DB
07AA: 11 08 00       LD    DE,$0008           ; * J07E6
07AD: FE 08          CP    $08                ;
07AF: 38 12          JR    C,$7C3             ; 
07B1: C6 28          ADD   $28                ;
07B3: 77             LD    (HL),A             ;
07B4: 19             ADD   HL,DE              ;
07B5: 36 53          LD    (HL),$53           ;
07B7: 23             INC   HL                 ;
07B8: 23             INC   HL                 ;
07B9: 23             INC   HL                 ;
07BA: 36 31          LD    (HL),$31           ;
07BC: 11 06 00       LD    DE,$0006           ;
07BF: 19             ADD   HL,DE              ;
07C0: 36 00          LD    (HL),$00           ;
07C2: C9             RET                      ;
07C3: 3D             DEC   A                  ; * J07AF
07C4: C8             RET   Z                  ;
07C5: 11 0B 00       LD    DE,$000B           ;
07C8: 19             ADD   HL,DE              ;
07C9: C6 31          ADD   $31                ;
07CB: 77             LD    (HL),A             ;
07CC: 11 06 00       LD    DE,$0006           ;
07CF: 19             ADD   HL,DE              ;
07D0: 36 53          LD    (HL),$53           ;
07D2: C9             RET                      ;
07D3: 21 7D 2C       LD    HL,$2C7D           ; "A 1 PLAYER 1 COIN" script * C0797
07D6: ED B0          LDIR                     ;
07D8: 21 5B E0       LD    HL,$E05B           ;
07DB: 18 CA          JR    $7A7               ; 
07DD: CD E8 07       CALL  $07E8              ; * C079A
07E0: 21 5B E0       LD    HL,$E05B           ;
07E3: 3A 42 E0       LD    A,($E042)          ;{-1_slotModeB} 
07E6: 18 C2          JR    $7AA               ; 
07E8: 21 54 E0       LD    HL,$E054           ; * C0766,C07DD
07EB: CD 4E 03       CALL  $034E              ;{SlowScript} 
07EE: 2A 54 E0       LD    HL,($E054)         ; 
07F1: 11 40 00       LD    DE,$0040           ;
07F4: 19             ADD   HL,DE              ;
07F5: 22 54 E0       LD    ($E054),HL         ; 
07F8: 21 57 E0       LD    HL,$E057           ;
07FB: 34             INC   (HL)               ;
07FC: C9             RET                      ;
07FD: 21 77 E2       LD    HL,$E277           ; * C0E48
0800: 06 07          LD    B,$07              ;
0802: 7E             LD    A,(HL)             ; * J0807,J080F
0803: A7             AND   A                  ;
0804: 28 0B          JR    Z,$811             ; 
0806: 2B             DEC   HL                 ;
0807: 10 F9          DJNZ  $802               ; 
0809: C9             RET                      ;
080A: 21 61 E2       LD    HL,$E261           ; * C1C54
080D: 06 12          LD    B,$12              ;
080F: 18 F1          JR    $802               ; 
0811: 34             INC   (HL)               ; * J0804
0812: 7D             LD    A,L                ;
0813: D6 50          SUB   $50                ;
0815: 87             ADD   A,A                ;
0816: 87             ADD   A,A                ;
0817: DD 77 01       LD    (IX+$01),A         ;
081A: C9             RET                      ;

XYToTextPtr:
; Convert an object X,Y coordinate to pointer on tile screen. This
; is only used to draw the player's air shot.
;
; IX is the object pointer (always the air shot)
; Return text tile map pointer in HL.
; Return X/2 in D (used to draw shot)
;
081B: DD 7E 07       LD    A,(IX+$07)         ; Get the Y coordinate * C1670,C168F
081E: E6 F8          AND   $F8                ; Drop the divide-by-eight remainder (1111_1000)
0820: 6F             LD    L,A                ; To HL
0821: 26 20          LD    H,$20              ; Will be 40xx ... tile memory
0823: 29             ADD   HL,HL              ; Original Y value of 8 become 16
0824: 29             ADD   HL,HL              ; Value 8 becomes 32 ... multiply by 32 (bytes per row)
0825: DD 7E 03       LD    A,(IX+$03)         ; Get X coordinate
0828: 1F             RRA                      ; Divide by 2
0829: 57             LD    D,A                ; Hold this for use in drawing shot
082A: 1F             RRA                      ; Divide by 4
082B: 1F             RRA                      ; Divide by 8 (8 bits in a tile)
082C: E6 1F          AND   $1F                ; Only keep the row offset
082E: 85             ADD   A,L                ; Add in the offset on the tile row
082F: 6F             LD    L,A                ; Back to L
0830: C9             RET                      ; Return pointer in HL

0831: 3A 00 E3       LD    A,($E300)          ;{-1_buggyHandler} * C162D,C18E0,C1957,C195E,C1A2F,C1E25
0834: FE 06          CP    $06                ;
0836: 30 7A          JR    NC,$8B2            ; 
0838: 3A E2 E1       LD    A,($E1E2)          ; * C1950,C1A22,C1A73
083B: DD 96 0F       SUB   (IX+$0F)           ;
083E: ED 44          NEG                      ;
0840: DD 77 03       LD    (IX+$03),A         ;
0843: FE E0          CP    $E0                ;
0845: 38 6D          JR    C,$8B4             ; 
0847: DD 4E 0B       LD    C,(IX+$0B)         ;
084A: 0D             DEC   C                  ;
084B: 20 6B          JR    NZ,$8B8            ;{DrawObject} 
084D: FE E8          CP    $E8                ;
084F: 30 67          JR    NC,$8B8            ;{DrawObject} 
0851: E1             POP   HL                 ;
0852: DD 36 00 00    LD    (IX+$00),$00       ; * J143E,J1639,J163E,C1711,J177C,J1B13,J1CE0,C1D98,J1E11,J1E30,J1E38,J1E45,J1E55,J1E9E,J2028,J2039,J20BB,J20CF
0856: DD 7E 0D       LD    A,(IX+$0D)         ; A = object.layoutIndex * C1794,J17C1,J1D20,C1E8B
0859: 37             SCF                      ; A = 2 * object.layoutIndex ...
085A: 17             RLA                      ; ... + 1
085B: D8             RET   C                  ; A was >= 0x80 ... not valid
085C: 37             SCF                      ; A = 4 * object.layoutIndex ...
085D: 17             RLA                      ; ... + 3
085E: 21 18 2E       LD    HL,$2E18           ; 
0861: 30 01          JR    NC,$864            ; 
0863: 24             INC   H                  ;
0864: 5F             LD    E,A                ; DE = ... * J0861
0865: 16 00          LD    D,$00              ; ... 4 * object.layoutIndex + 3
0867: 19             ADD   HL,DE              ;
0868: 46             LD    B,(HL)             ; B = ObjectLaout[object.layoutIndex].numberOfTiles
0869: DD 5E 01       LD    E,(IX+$01)         ; * J20D8
086C: 16 E1          LD    D,$E1              ;
086E: 78             LD    A,B                ;
086F: 17             RLA                      ;
0870: 30 10          JR    NC,$882            ; 
0872: 06 01          LD    B,$01              ;
0874: 17             RLA                      ;
0875: 38 27          JR    C,$89E             ; 
0877: 7B             LD    A,E                ;
0878: FE 60          CP    $60                ;
087A: 38 06          JR    C,$882             ; 
087C: 62             LD    H,D                ;
087D: D6 5E          SUB   $5E                ;
087F: 6F             LD    L,A                ;
0880: 36 00          LD    (HL),$00           ;
0882: FD 21 00 00    LD    IY,$0000           ; * J0870,J087A,C089E
0886: FD 19          ADD   IY,DE              ;
0888: 7B             LD    A,E                ;
0889: 1F             RRA                      ;
088A: 1F             RRA                      ;
088B: E6 3F          AND   $3F                ;
088D: C6 50          ADD   $50                ;
088F: 6F             LD    L,A                ;
0890: 26 E2          LD    H,$E2              ;
0892: 11 04 00       LD    DE,$0004           ;
0895: FD 72 02       LD    (IY+$02),D         ; * J089A
0898: FD 19          ADD   IY,DE              ;
089A: 10 F9          DJNZ  $895               ; 
089C: 72             LD    (HL),D             ;
089D: C9             RET                      ;
089E: CD 82 08       CALL  $0882              ; * J0875
08A1: 21 74 E1       LD    HL,$E174           ; * C1746
08A4: 01 00 18       LD    BC,$1800           ;
08A7: 71             LD    (HL),C             ; * J08A9
08A8: 23             INC   HL                 ;
08A9: 10 FC          DJNZ  $8A7               ; 
08AB: 21 D1 E1       LD    HL,$E1D1           ;
08AE: 70             LD    (HL),B             ;
08AF: 23             INC   HL                 ;
08B0: 70             LD    (HL),B             ;
08B1: C9             RET                      ;
08B2: E1             POP   HL                 ; * J0836
08B3: C9             RET                      ;
08B4: DD 36 0B 01    LD    (IX+$0B),$01       ; * J0845

DrawObject:
; This routine draws the graphics object associated with the ISR game object.
; IX is the ISR Object
;
08B8: DD 7E 0D       LD    A,(IX+$0D)         ; Object number * J084B,J084F,J1360,J13B9,C13D8,C13FF,J1419,C1484,J1615,J1AED,J1D3F,J1D7F,J1D8D,J1D95,J1EA1,J20AF,J20C1,J20C7
08BB: 07             RLCA                     ; Was upper bit set (Thus A*4>=512)?
08BC: D8             RET   C                  ; Yes ... skip 
08BD: 17             RLA                      ; Now *4
08BE: 21 18 2E       LD    HL,$2E18           ; Base pointer
08C1: 30 01          JR    NC,$8C4            ; The *4 was all within LSB ... skip
08C3: 24             INC   H                  ; The *4 overflowed ... bump MSB (there is no shift-left-into-H)
08C4: 5F             LD    E,A                ; A*4 ... * J08C1
08C5: 16 00          LD    D,$00              ; ... now in DE
08C7: 19             ADD   HL,DE              ; HL = 2E18 + A*4 ( A*4 must be less than 512 )
08C8: DD 5E 01       LD    E,(IX+$01)         ; LSB of object mirror pointer (4 bytes each)
08CB: 16 E1          LD    D,$E1              ; Sprite mirror
08CD: FD 21 00 00    LD    IY,$0000           ; Sprite mirror object ...
08D1: FD 19          ADD   IY,DE              ; ... pointer to IY
08D3: 56             LD    D,(HL)             ; Get starting tile number
08D4: 23             INC   HL                 ; Next
08D5: 5E             LD    E,(HL)             ; Get flips/color
08D6: 23             INC   HL                 ; Next
08D7: 4E             LD    C,(HL)             ; Get draw routine
08D8: 06 00          LD    B,$00              ; Now in BC
08DA: 21 F5 08       LD    HL,$08F5           ; Offset into table
08DD: 09             ADD   HL,BC              ; Point to jump address
08DE: 4E             LD    C,(HL)             ; Get jump LSB
08DF: 23             INC   HL                 ; Next
08E0: 66             LD    H,(HL)             ; Get jump MSB
08E1: 69             LD    L,C                ; Now in HL
08E2: DD 4E 03       LD    C,(IX+$03)         ; X coordinate to C
08E5: DD 7E 07       LD    A,(IX+$07)         ; Y coordinate to A
08E8: CD ED 08       CALL  $08ED              ; ?? adjusted Y coordinate to B
08EB: AF             XOR   A                  ; Clear A ... many handlers need a zero
08EC: E9             JP    (HL)               ; Jump to the draw routine

; B = (E03C) - A - 1
;
08ED: 2F             CPL                      ; * C08E8,C159D,C15CA
08EE: 47             LD    B,A                ;
08EF: 3A 3C E0       LD    A,($E03C)          ; 
08F2: 80             ADD   A,B                ;
08F3: 47             LD    B,A                ;
08F4: C9             RET                      ;

ObjectDraws:
; Table of routines used to draw specific objects. Many objects share a handler. The
; handlers are usually about geometry (1x2 or 2x2 etc). Some pick a tile animation
; while other object control their own tile animation.
;
;                Handler     Routine   Use
08F5: 69 09    ; ObjDraw_00  0969      Rocks, boulders, exploding rocks and boulders, tank, ??3E
08F7: 5A 09    ; ObjDraw_01  095A      Hover craft
08F9: CF 09    ; ObjDraw_02  09CF      Space Plant leaf 1
08FB: CD 09    ; ObjDraw_03  09CD      Space Plant leaf 2
08FD: F5 0A    ; ObjDraw_04  0AF5      Moon buggy explosion 3x2
08FF: 43 09    ; ObjDraw_05  0943      Moon buggy explosion 2x1
0901: E2 0A    ; ObjDraw_06  0AE2      Moon buggy explosion 1x1
0903: 90 0A    ; ObjDraw_07  0A90      Moon buggy
0905: 56 0A    ; ObjDraw_08  0A56      Crater explosion
0907: B7 0A    ; ObjDraw_09  0AB7      ??42 ground explosion
0909: 52 0A    ; ObjDraw_0A  0A52      Alien shot hitting ground 2x2
090B: 9F 0A    ; ObjDraw_0B  0A9F      ??48 Rubble 1
090D: C9 09    ; ObjDraw_0C  09C9      Space Plant leaf 3
090F: 25 0B    ; ObjDraw_0D  0B25      Alien ships, shots, and shot explosions, ??4F small round explosion
0911: 76 09    ; ObjDraw_0E  0976      Player forward shot
0913: 97 09    ; ObjDraw_0F  0997      Alien shot hitting ground 1x1
0915: BA 09    ; ObjDraw_10  09BA      Space Plant leaf 4
0917: 1E 0A    ; ObjDraw_11  0A1E      Space Plant base
0919: 44 0A    ; ObjDraw_12  0A44      Moon buggy crashing in crater
091B: 34 09    ; ObjDraw_13  0934      Hover craft full boost
091D: 25 09    ; ObjDraw_14  0925      Ground mine
091F: 1D 0B    ; ObjDraw_15  0B1D      Bubble alien shot
0921: B0 09    ; ObjDraw_16  09B0      Buggy wheel
0923: 83 09    ; ObjDraw_17  0983      Score value

ObjDraw_14: ; Ground mine
0925: DD 34 0A       INC   (IX+$0A)           ;
0928: DD 7E 0A       LD    A,(IX+$0A)         ;
092B: E6 1F          AND   $1F                ;
092D: FE 0B          CP    $0B                ;
092F: 38 38          JR    C,$969             ;{ObjDraw_00} 
0931: 1C             INC   E                  ; Next color set
0932: 18 35          JR    $969               ;{ObjDraw_00} 

ObjDraw_13: ; Hover craft full boost
0934: 3A 4E E0       LD    A,($E04E)          ;{-1_isrCNT_1} 
0937: E6 03          AND   $03                ;
0939: 28 01          JR    Z,$93C             ; 
093B: 14             INC   D                  ;
093C: CD 69 09       CALL  $0969              ;{ObjDraw_00} * J0939
093F: 16 3B          LD    D,$3B              ;
0941: 18 1B          JR    $95E               ; 

ObjDraw_05: ; Moon buggy explosion 2x1
0943: FD 21 A4 E1    LD    IY,$E1A4           ;
0947: FD 77 0A       LD    (IY+$0A),A         ;
094A: FD 77 0E       LD    (IY+$0E),A         ;
094D: FD 77 12       LD    (IY+$12),A         ;
0950: FD 77 16       LD    (IY+$16),A         ;
0953: CD 95 0A       CALL  $0A95              ;{TrnsSprColor} 
0956: 3E F8          LD    A,$F8              ;
0958: 80             ADD   A,B                ;
0959: 47             LD    B,A                ;
;
ObjDraw_01: ; Hover craft
095A: CD 69 09       CALL  $0969              ;{ObjDraw_00} 
095D: 14             INC   D                  ;
095E: 3E 10          LD    A,$10              ; * J0941
0960: 81             ADD   A,C                ;
0961: 4F             LD    C,A                ;
0962: 21 04 00       LD    HL,$0004           ;
0965: EB             EX    DE,HL              ;
0966: FD 19          ADD   IY,DE              ;
0968: EB             EX    DE,HL              ;
;
ObjDraw_00: ;  Rocks, boulders, tank
0969: DD 7E 0B       LD    A,(IX+$0B)         ; * J092F,J0932,C093C,C095A,C09E4
096C: A7             AND   A                  ;
096D: 79             LD    A,C                ;
096E: 20 35          JR    NZ,$9A5            ; 
0970: C6 08          ADD   $08                ;
0972: FE 20          CP    $20                ;
0974: 38 35          JR    C,$9AB             ; Blank the tile number

ObjDraw_0E: ; Player forward shot
; Set the sprite data in the RAM mirror
; B=Y
; C=X
; D=tile
; E=flips/color
;
0976: FD 70 00       LD    (IY+$00),B         ; Set Y coordinate * J0995,J09A3,J09A9,J09B5,J09B8,J0AF2,C0B25,J0B35,J15A9,J15DD
0979: FD 73 01       LD    (IY+$01),E         ; Set tile flips/color
097C: FD 72 02       LD    (IY+$02),D         ; Set tile number
097F: FD 71 03       LD    (IY+$03),C         ; Set X coordinate
0982: C9             RET                      ; Done

ObjDraw_17: ;  Graphic score 300, 800, 500, or 1000
0983: DD 7E 08       LD    A,(IX+$08)         ; 3->300 5->500 8->800, 10->1000 * C0A2D
0986: 1E 07          LD    E,$07              ; Color set (will be 14)
0988: CB 3F          SRL   A                  ; Lower bit to C
098A: CB 13          RL    E                  ; Now either 14 or 15 ... correct color set
098C: C6 7A          ADD   $7A                ; Offset to either 7D or 7E
098E: 57             LD    D,A                ; Tile number
098F: 78             LD    A,B                ; Y coordinate
0990: FE 80          CP    $80                ; ?? Duplicate if on lower half of screen ??
0992: D2 25 0B       JP    NC,$0B25           ;{ObjDraw_0D} 
0995: 18 DF          JR    $976               ;{ObjDraw_0E} Store the image

ObjDraw_0F: ; Alien shot hitting ground 1x1
0997: 3E 08          LD    A,$08              ;
0999: 80             ADD   A,B                ;
099A: 47             LD    B,A                ;
099B: FD 21 74 E1    LD    IY,$E174           ; ?? change to object ??
099F: 79             LD    A,C                ;
09A0: FE F8          CP    $F8                ;
09A2: D0             RET   NC                 ;
09A3: 18 D1          JR    $976               ;{ObjDraw_0E} 
;
09A5: C6 08          ADD   $08                ; * J096E
09A7: FE F0          CP    $F0                ;
09A9: 38 CB          JR    C,$976             ;{ObjDraw_0E} 
09AB: FD 36 02 00    LD    (IY+$02),$00       ; Blank the tile number * J0974
09AF: C9             RET                      ;

ObjDraw_16: ;  Buggy wheel
; Buggy wheel that flies off in a crash. Flip between two images.
; Store either the given data or the given data but next tile number.
09B0: 3A 4E E0       LD    A,($E04E)          ;{-1_isrCNT_1} ISR1 up counter
09B3: CB 57          BIT   2,A                ; Chance ...
09B5: 28 BF          JR    Z,$976             ;{ObjDraw_0E} ... to use ...
09B7: 14             INC   D                  ; ... next image
09B8: 18 BC          JR    $976               ;{ObjDraw_0E} Store sprite details

ObjDraw_10: ; Space Plant leaf 4
09BA: 3E 0E          LD    A,$0E              ;
09BC: 80             ADD   A,B                ;
09BD: 60             LD    H,B                ;
09BE: 47             LD    B,A                ;
09BF: 2E 01          LD    L,$01              ;
09C1: CD E4 09       CALL  $09E4              ; 
09C4: 11 08 76       LD    DE,$7608           ;
09C7: 18 11          JR    $9DA               ; 

ObjDraw_0C: ; Space Plant leaf 3
09C9: 3E 0A          LD    A,$0A              ;
09CB: 18 02          JR    $9CF               ;{ObjDraw_02} 

ObjDraw_03: ; Space Plant leaf 2
09CD: 3E 05          LD    A,$05              ;
;
ObjDraw_02: ; Space Plant leaf 1
09CF: 80             ADD   A,B                ; * J09CB
09D0: 60             LD    H,B                ;
09D1: 47             LD    B,A                ;
09D2: 2E 01          LD    L,$01              ;
09D4: CD E4 09       CALL  $09E4              ; 
09D7: 11 08 71       LD    DE,$7108           ;
09DA: 44             LD    B,H                ; * J09C7
09DB: 21 08 00       LD    HL,$0008           ;
09DE: EB             EX    DE,HL              ;
09DF: FD 19          ADD   IY,DE              ;
09E1: EB             EX    DE,HL              ;
09E2: 2E 00          LD    L,$00              ;
09E4: CD 69 09       CALL  $0969              ;{ObjDraw_00} * C09C1,C09D4,J0A3C
09E7: FD 70 04       LD    (IY+$04),B         ;
09EA: 2D             DEC   L                  ;
09EB: 20 29          JR    NZ,$A16            ; 
09ED: 3E 40          LD    A,$40              ;
09EF: AB             XOR   E                  ;
09F0: FD 77 05       LD    (IY+$05),A         ;
09F3: 3E 08          LD    A,$08              ;
09F5: FD 72 06       LD    (IY+$06),D         ; * J0A1C
09F8: 81             ADD   A,C                ;
09F9: FD 77 07       LD    (IY+$07),A         ;
09FC: C6 08          ADD   $08                ;
09FE: FE F8          CP    $F8                ;
0A00: 30 0A          JR    NC,$A0C            ; 
0A02: FE 20          CP    $20                ;
0A04: D0             RET   NC                 ;
0A05: DD 7E 0B       LD    A,(IX+$0B)         ;
0A08: A7             AND   A                  ;
0A09: 28 06          JR    Z,$A11             ; 
0A0B: C9             RET                      ;
0A0C: DD 7E 0B       LD    A,(IX+$0B)         ; * J0A00
0A0F: A7             AND   A                  ;
0A10: C8             RET   Z                  ;
0A11: FD 36 06 00    LD    (IY+$06),$00       ; * J0A09
0A15: C9             RET                      ;
0A16: 14             INC   D                  ; * J09EB
0A17: FD 73 05       LD    (IY+$05),E         ;
0A1A: 3E 10          LD    A,$10              ;
0A1C: 18 D7          JR    $9F5               ; 

ObjDraw_11: ; Space Plant base
0A1E: C5             PUSH  BC                 ;
0A1F: D5             PUSH  DE                 ;
0A20: 21 02 08       LD    HL,$0802           ;
0A23: 09             ADD   HL,BC              ;
0A24: 44             LD    B,H                ;
0A25: 4D             LD    C,L                ;
0A26: 79             LD    A,C                ;
0A27: C6 08          ADD   $08                ;
0A29: FE D0          CP    $D0                ;
0A2B: 30 11          JR    NC,$A3E            ; 
0A2D: CD 83 09       CALL  $0983              ;{ObjDraw_17} 
0A30: 11 04 00       LD    DE,$0004           ; * J0A42
0A33: FD 19          ADD   IY,DE              ;
0A35: D1             POP   DE                 ;
0A36: C1             POP   BC                 ;
0A37: 2E 00          LD    L,$00              ;
0A39: FD 75 0A       LD    (IY+$0A),L         ;
0A3C: 18 A6          JR    $9E4               ; 
0A3E: FD 36 02 00    LD    (IY+$02),$00       ; * J0A2B
0A42: 18 EC          JR    $A30               ; 

ObjDraw_12: ; Moon buggy crashing in crater
0A44: 32 A6 E1       LD    ($E1A6),A          ; 
0A47: 32 AA E1       LD    ($E1AA),A          ; 
0A4A: 32 AE E1       LD    ($E1AE),A          ; 
0A4D: CD 95 0A       CALL  $0A95              ;{TrnsSprColor} 
0A50: 18 10          JR    $A62               ; 

ObjDraw_0A: ;  2x2 Alien shot hitting ground
0A52: 3E 18          LD    A,$18              ; Offset by -$18 when drawing
0A54: 18 02          JR    $A58               ; Draw the 2x2

ObjDraw_08: ; 2x2 Alien bubble shot opening crater
0A56: 3E 0D          LD    A,$0D              ; Offset by -$0D when drawing
;
0A58: FD 21 74 E1    LD    IY,$E174           ; * J0A54
0A5C: 80             ADD   A,B                ; Offset ...
0A5D: 47             LD    B,A                ; ... Y coordinate
0A5E: 3E F8          LD    A,$F8              ; Offset X ...
0A60: 81             ADD   A,C                ; ... back 8 ...
0A61: 4F             LD    C,A                ; ... to center on X
;
0A62: AF             XOR   A                  ; X coordinate offset is 0 * J0A50,J0A93
0A63: CD 6F 0A       CALL  $0A6F              ;{Draw1x2Sprites} Do top and bottom tiles
0A66: EB             EX    DE,HL              ; Skip over ...
0A67: 11 08 00       LD    DE,$0008           ; ... the two ...
0A6A: FD 19          ADD   IY,DE              ; ... sprite ...
0A6C: EB             EX    DE,HL              ; ... slots
0A6D: 3E 10          LD    A,$10              ; X coordinate offset is 16
```

# Draw 1x2 Sprites

```code
Draw1x2Sprites: 
0A6F: 81             ADD   A,C                ; Add the X coordinate offset * C0A63,C0AB0,C0ACD,C0B13
0A70: 6F             LD    L,A                ; Hold in L
0A71: FD 77 03       LD    (IY+$03),A         ; Set the X coordinate for top sprite
0A74: FD 77 07       LD    (IY+$07),A         ; Set the X coordinate for the bottom sprite
0A77: FD 70 00       LD    (IY+$00),B         ; Set the Y coordinate for top sprite
0A7A: 3E F0          LD    A,$F0              ; Back up ...
0A7C: 80             ADD   A,B                ; ... 8
0A7D: FD 77 04       LD    (IY+$04),A         ; Set the Y coordinate for the bottom sprite
0A80: FD 73 01       LD    (IY+$01),E         ; Set the color/flip for top sprite
0A83: FD 73 05       LD    (IY+$05),E         ; Set the color/flip for bottom sprite
0A86: FD 72 02       LD    (IY+$02),D         ; Store tile number
0A89: 14             INC   D                  ; Add 2 for ...
0A8A: 14             INC   D                  ; ... next tile
0A8B: FD 72 06       LD    (IY+$06),D         ; Set next tile
0A8E: 15             DEC   D                  ; Now back to just tile+1
0A8F: C9             RET                      ; Done

ObjDraw_07: ; Moon buggy
0A90: CD 95 0A       CALL  $0A95              ;{TrnsSprColor} 
0A93: 18 CD          JR    $A62               ; 

TrnsSprColor:
; Change the color set for for buggy if on the champion course.
; The buggy is usually color-set-0. But on the champion course
; it is color-set-C. The only difference is the buggy body is
; red on the champion course instead of the usual pink.
;
0A95: 3A F9 E0       LD    A,($E0F9)          ;{-1_champColors} Are we on ... * C0953,C0A4D,C0A90,C0AE9,C0AFD
0A98: 1F             RRA                      ; ... the champion course?
0A99: D0             RET   NC                 ; No ... leave color set 0
0A9A: 7B             LD    A,E                ; Get the color set value
0A9B: F6 0C          OR    $0C                ; Transform to C
0A9D: 5F             LD    E,A                ; Back to color set value
0A9E: C9             RET                      ; Done

ObjDraw_0B: ; ??48 Rubble 1
0A9F: FD 21 74 E1    LD    IY,$E174           ;
0AA3: FD 36 0A 00    LD    (IY+$0A),$00       ;
0AA7: FD 36 0E 00    LD    (IY+$0E),$00       ;
0AAB: 3E 18          LD    A,$18              ;
0AAD: 80             ADD   A,B                ;
0AAE: 47             LD    B,A                ;
0AAF: AF             XOR   A                  ;
0AB0: CD 6F 0A       CALL  $0A6F              ;{Draw1x2Sprites} 
0AB3: FD 72 06       LD    (IY+$06),D         ;
0AB6: C9             RET                      ;

ObjDraw_09: ; ??42 ground explosion
0AB7: 3E 18          LD    A,$18              ;
0AB9: 80             ADD   A,B                ;
0ABA: 47             LD    B,A                ;
0ABB: FD 21 74 E1    LD    IY,$E174           ;
0ABF: 3E F8          LD    A,$F8              ;
0AC1: CD CD 0A       CALL  $0ACD              ; 
0AC4: 21 0C 00       LD    HL,$000C           ;
0AC7: EB             EX    DE,HL              ;
0AC8: FD 19          ADD   IY,DE              ;
0ACA: EB             EX    DE,HL              ;
0ACB: 3E 08          LD    A,$08              ;
0ACD: CD 6F 0A       CALL  $0A6F              ;{Draw1x2Sprites} * C0AC1
0AD0: FD 75 0B       LD    (IY+$0B),L         ;
0AD3: D6 10          SUB   $10                ;
0AD5: FD 77 08       LD    (IY+$08),A         ;
0AD8: FD 77 09       LD    (IY+$09),A         ;
0ADB: 7A             LD    A,D                ;
0ADC: C6 03          ADD   $03                ;
0ADE: FD 77 0A       LD    (IY+$0A),A         ;
0AE1: C9             RET                      ;

ObjDraw_06: ; Moon buggy explosion 1x1
0AE2: FD 21 A4 E1    LD    IY,$E1A4           ;
0AE6: FD 77 06       LD    (IY+$06),A         ;
0AE9: CD 95 0A       CALL  $0A95              ;{TrnsSprColor} 
0AEC: 21 08 F8       LD    HL,$F808           ;
0AEF: 09             ADD   HL,BC              ;
0AF0: 44             LD    B,H                ;
0AF1: 4D             LD    C,L                ;
0AF2: C3 76 09       JP    $0976              ;{ObjDraw_0E} 

ObjDraw_04: ; Moon buggy explosion 3x2
0AF5: FD 21 A4 E1    LD    IY,$E1A4           ;
0AF9: FD 36 1A 00    LD    (IY+$1A),$00       ;
0AFD: CD 95 0A       CALL  $0A95              ;{TrnsSprColor} 
0B00: 3E F8          LD    A,$F8              ;
0B02: CD 13 0B       CALL  $0B13              ; 
0B05: 3E 08          LD    A,$08              ;
0B07: CD 0C 0B       CALL  $0B0C              ; 
0B0A: 3E 18          LD    A,$18              ;
0B0C: EB             EX    DE,HL              ; * C0B07
0B0D: 11 08 00       LD    DE,$0008           ;
0B10: FD 19          ADD   IY,DE              ;
0B12: EB             EX    DE,HL              ;
0B13: CD 6F 0A       CALL  $0A6F              ;{Draw1x2Sprites} * C0B02
0B16: 7A             LD    A,D                ;
0B17: C6 02          ADD   $02                ;
0B19: FD 77 06       LD    (IY+$06),A         ;
0B1C: C9             RET                      ;

ObjDraw_15: ; Bubble alien shot
0B1D: 3A 4E E0       LD    A,($E04E)          ;{-1_isrCNT_1} 
0B20: CB 4F          BIT   1,A                ;
0B22: 28 01          JR    Z,$B25             ;{ObjDraw_0D} 
0B24: 1C             INC   E                  ;
;
ObjDraw_0D: ; Alien ships and shots
0B25: CD 76 09       CALL  $0976              ;{ObjDraw_0E} * J0992,J0B22
0B28: DD 7E 01       LD    A,(IX+$01)         ; LSB of object pointer
0B2B: FE 60          CP    $60                ; Less than 96?
0B2D: D8             RET   C                  ; Yes ... done
;
; If the object number is 60 or greater then a duplicate object is drawn on top
; of it. I see this with first saucer and fin ship (but not bubble) and all
; alien shots. Maybe make sure processed in the upper half of the frame ...
; the last sprites are processed in lower part of frame? Odd
;
0B2E: EB             EX    DE,HL              ; Hold DE
0B2F: 11 A0 FF       LD    DE,$FFA0           ; Value -96
0B32: FD 19          ADD   IY,DE              ; IY = IY - 96
0B34: EB             EX    DE,HL              ; Restore DE
0B35: C3 76 09       JP    $0976              ;{ObjDraw_0E} ?? Initialize "other" object to same


0B38: CD 8E 0C       CALL  $0C8E              ; * C0112
0B3B: CD BF 0C       CALL  $0CBF              ; 
0B3E: 3A 04 D0       LD    A,($D004)          ;{-2_DSW2}
0B41: CB 6F          BIT   5,A                ;
0B43: C0             RET   NZ                 ;
0B44: 21 A9 2A       LD    HL,$2AA9           ; "PICTURE NUMBER SET" message
0B47: CD 00 03       CALL  $0300              ;{RunTextScript} 
0B4A: 3E FF          LD    A,$FF              ; * J0B68,J0B88
0B4C: 32 51 E0       LD    ($E051),A          ;{-1_isrCount4} 
0B4F: 21 53 E0       LD    HL,$E053           ;
0B52: 7E             LD    A,(HL)             ;
0B53: 4E             LD    C,(HL)             ; * J0B5E
0B54: A9             XOR   C                  ;
0B55: A1             AND   C                  ;
0B56: 1F             RRA                      ;
0B57: 38 08          JR    C,$B61             ; 
0B59: 3A 51 E0       LD    A,($E051)          ;{-1_isrCount4} 
0B5C: 47             LD    B,A                ;
0B5D: 79             LD    A,C                ;
0B5E: 10 F3          DJNZ  $B53               ; 
0B60: C9             RET                      ;
0B61: 21 0E E5       LD    HL,$E50E           ; Current passed point * J0B57
0B64: 7E             LD    A,(HL)             ; Get the current point
0B65: 3C             INC   A                  ; Increment to next
0B66: FE 34          CP    $34                ;
0B68: 30 E0          JR    NC,$B4A            ; 
0B6A: 77             LD    (HL),A             ; New passed point
0B6B: 2A 16 E5       LD    HL,($E516)         ; 
0B6E: 46             LD    B,(HL)             ; * J0B76
0B6F: 23             INC   HL                 ;
0B70: 7E             LD    A,(HL)             ;
0B71: E6 7F          AND   $7F                ;
0B73: 23             INC   HL                 ;
0B74: FE 06          CP    $06                ;
0B76: 20 F6          JR    NZ,$B6E            ; 
0B78: 78             LD    A,B                ;
0B79: 32 0B E5       LD    ($E50B),A          ; 
0B7C: 22 16 E5       LD    ($E516),HL         ; 
0B7F: 32 23 E5       LD    ($E523),A          ; 
0B82: 22 2E E5       LD    ($E52E),HL         ; 
0B85: CD 12 0D       CALL  $0D12              ; 
0B88: 18 C0          JR    $B4A               ; 
0B8A: CD B1 0C       CALL  $0CB1              ; * C0069,C0089
0B8D: 21 94 26       LD    HL,$2694           ;
0B90: 22 16 E5       LD    ($E516),HL         ; 
0B93: C3 BF 0C       JP    $0CBF              ; 

0B96: 2A 16 E5       LD    HL,($E516)         ; * C0123,C0BE8
0B99: 2B             DEC   HL                 ; * J0BA0,J0BAB
0B9A: 7E             LD    A,(HL)             ;
0B9B: 2B             DEC   HL                 ;
0B9C: E6 7F          AND   $7F                ;
0B9E: FE 06          CP    $06                ;
0BA0: 20 F7          JR    NZ,$B99            ; 
0BA2: 11 DC E1       LD    DE,$E1DC           ;
0BA5: EB             EX    DE,HL              ;
0BA6: 7E             LD    A,(HL)             ;
0BA7: 36 00          LD    (HL),$00           ;
0BA9: EB             EX    DE,HL              ;
0BAA: A7             AND   A                  ;
0BAB: 20 EC          JR    NZ,$B99            ; 
0BAD: 7E             LD    A,(HL)             ;
0BAE: 32 0B E5       LD    ($E50B),A          ; 
0BB1: 23             INC   HL                 ;
0BB2: 23             INC   HL                 ;
0BB3: 22 16 E5       LD    ($E516),HL         ; 
0BB6: C9             RET                      ;


0BB7: 21 00 E1       LD    HL,$E100           ; Clear sprite mirror ... * J0078,J008C,J0115,J0138,J0142,J0148,J0173,J01CF,J28A7,J28B7
0BBA: 01 00 04       LD    BC,$0400           ; ... and game objects ...
0BBD: CD FA 05       CALL  $05FA              ; ... up to high-score
;
0BC0: DD 21 00 E3    LD    IX,$E300           ; Moon buggy ISRObject 00
0BC4: DD 36 00 01    LD    (IX+$00),$01       ; Moon buggy's start-game handler
0BC8: DD 36 10 09    LD    (IX+$10),$09       ; ?? handler
0BCC: DD 36 01 B0    LD    (IX+$01),$B0       ; Moon buggy uses sprites B0
0BD0: DD 36 21 A0    LD    (IX+$21),$A0       ; ?? uses sprites A0
;
0BD4: DD 21 70 E3    LD    IX,$E370           ; 
0BD8: 3E 60          LD    A,$60              ;
0BDA: 06 09          LD    B,$09              ;  ?? This code makes the wheels fly off in a crash ??
0BDC: 11 10 00       LD    DE,$0010           ;
0BDF: DD 77 01       LD    (IX+$01),A         ; * J0BE6
0BE2: DD 19          ADD   IX,DE              ;
0BE4: C6 04          ADD   $04                ;
0BE6: 10 F7          DJNZ  $BDF               ; 
;
0BE8: CD 96 0B       CALL  $0B96              ; 
0BEB: 2B             DEC   HL                 ;
0BEC: 46             LD    B,(HL)             ;
0BED: 3E 04          LD    A,$04              ;
0BEF: 21 00 C0       LD    HL,$C000           ;
0BF2: 05             DEC   B                  ;
0BF3: F2 FA 0B       JP    P,$0BFA            ; 
0BF6: 3E 07          LD    A,$07              ;
0BF8: 26 A8          LD    H,$A8              ;
0BFA: 32 14 E5       LD    ($E514),A          ; * J0BF3
0BFD: 22 06 E3       LD    ($E306),HL         ; 
0C00: 3E 02          LD    A,$02              ;
0C02: 32 08 E5       LD    ($E508),A          ; 
0C05: CD 8D 0D       CALL  $0D8D              ; 
0C08: 3A 13 E5       LD    A,($E513)          ; 
0C0B: 3D             DEC   A                  ;
0C0C: FE 05          CP    $05                ;
0C0E: CE 00          ADC   $00                ;
0C10: 06 FB          LD    B,$FB              ;
0C12: 1F             RRA                      ;
0C13: 38 01          JR    C,$C16             ; 
0C15: 04             INC   B                  ;
0C16: 78             LD    A,B                ; * J0C13
0C17: 32 C5 E1       LD    ($E1C5),A          ; 
0C1A: CD 81 29       CALL  $2981              ; 
0C1D: A7             AND   A                  ;
0C1E: 20 5F          JR    NZ,$C7F            ; 
0C20: 21 0F E5       LD    HL,$E50F           ;
0C23: CB 46          BIT   0,(HL)             ;
0C25: 20 58          JR    NZ,$C7F            ; 
0C27: 34             INC   (HL)               ;
;
0C28: 3A 10 E5       LD    A,($E510)          ; Get the course number
0C2B: A7             AND   A                  ; Is this the first time?
0C2C: 28 58          JR    Z,$C86             ; Yes ... go start "BEGINNER" course
0C2E: 21 5F 2A       LD    HL,$2A5F           ; "CHAMPION COURSE 1 GO" script
0C31: CD 00 03       CALL  $0300              ;{RunTextScript} Print the banner
0C34: 3A 10 E5       LD    A,($E510)          ; Get the champion course number
0C37: FE 04          CP    $04                ; Is it a 1, 2, or 3?
0C39: 38 02          JR    C,$C3D             ; Yes keep it
0C3B: 3E 03          LD    A,$03              ; No ... cap the number at 3
0C3D: C6 30          ADD   $30                ; Convert to number * J0C39
0C3F: 32 56 81       LD    ($8156),A          ; Change the "1" in the message just printed to the right number
;
0C42: 3E 1C          LD    A,$1C              ; Play intro ... * J0C8C
0C44: CD 6F 0D       CALL  $0D6F              ; ... song
0C47: 3E 40          LD    A,$40              ; Set timer for ...
0C49: 32 0A E3       LD    ($E30A),A          ; ... intro song to end
0C4C: 0E 68          LD    C,$68              ;
0C4E: 21 B6 30       LD    HL,$30B6           ;
0C51: 46             LD    B,(HL)             ; * J0C68
0C52: CB 78          BIT   7,B                ;
0C54: 20 14          JR    NZ,$C6A            ; 
0C56: 23             INC   HL                 ;
0C57: 5E             LD    E,(HL)             ;
0C58: 23             INC   HL                 ;
0C59: 7E             LD    A,(HL)             ;
0C5A: 23             INC   HL                 ;
0C5B: EB             EX    DE,HL              ;
;
0C5C: 26 83          LD    H,$83              ; In screen tile memory ?? * J0C65
0C5E: 71             LD    (HL),C             ;
0C5F: 26 87          LD    H,$87              ; In screen color memory ??
0C61: 70             LD    (HL),B             ;
0C62: 0C             INC   C                  ;
0C63: 2C             INC   L                  ;
0C64: BD             CP    L                  ;
0C65: 20 F5          JR    NZ,$C5C            ; 
0C67: EB             EX    DE,HL              ;
0C68: 18 E7          JR    $C51               ; 
0C6A: 3E D3          LD    A,$D3              ; * J0C54
0C6C: 21 D8 30       LD    HL,$30D8           ;
0C6F: 11 10 E2       LD    DE,$E210           ;
0C72: 46             LD    B,(HL)             ; * J0C7D
0C73: CB 78          BIT   7,B                ;
0C75: 20 08          JR    NZ,$C7F            ; 
0C77: 12             LD    (DE),A             ; * J0C79
0C78: 13             INC   DE                 ;
0C79: 10 FC          DJNZ  $C77               ; 
0C7B: 3C             INC   A                  ;
0C7C: 23             INC   HL                 ;
0C7D: 18 F3          JR    $C72               ; 
0C7F: 21 46 E0       LD    HL,$E046           ; * J0C1E,J0C25,J0C75
0C82: 34             INC   (HL)               ;
0C83: C3 6E 02       JP    $026E              ; ?? Main text loop for game

0C86: 21 47 2A       LD    HL,$2A47           ; "BEGINNER COURSE GO" script * J0C2C
0C89: CD 00 03       CALL  $0300              ;{RunTextScript} Print the banner
0C8C: 18 B4          JR    $C42               ; Back to start-course sequence

0C8E: AF             XOR   A                  ; * C0B38
0C8F: 32 4D E0       LD    ($E04D),A          ; 
0C92: CD 95 0C       CALL  $0C95              ; 
0C95: CD 03 06       CALL  $0603              ;{SwapPlayers} * C0C92
0C98: 21 00 E5       LD    HL,$E500           ;
0C9B: 01 16 00       LD    BC,$0016           ;
0C9E: CD FA 05       CALL  $05FA              ; * J0CBD
0CA1: 32 0F E5       LD    ($E50F),A          ; 
0CA4: 3A 40 E0       LD    A,($E040)          ;{-1_PerCredit} 
0CA7: 32 15 E5       LD    ($E515),A          ; 
0CAA: 21 62 21       LD    HL,$2162           ;
0CAD: 22 16 E5       LD    ($E516),HL         ; 
0CB0: C9             RET                      ;

0CB1: 21 DE 26       LD    HL,$26DE           ; * C0B8A
0CB4: 22 F7 E0       LD    ($E0F7),HL         ; 
0CB7: 21 03 E5       LD    HL,$E503           ;
0CBA: 01 11 00       LD    BC,$0011           ;
0CBD: 18 DF          JR    $C9E               ; 
0CBF: CD 29 0D       CALL  $0D29              ; * C01CC,C0B3B,J0B93
0CC2: 21 21 84       LD    HL,$8421           ; * C0D90
0CC5: 0E 06          LD    C,$06              ;
0CC7: 3A 0E E5       LD    A,($E50E)          ; Current passed point
0CCA: FE 1A          CP    $1A                ; Is this the "champion" course
0CCC: 3E 00          LD    A,$00              ; No ... use
0CCE: 38 01          JR    C,$CD1             ; ... normal colors
0CD0: 3C             INC   A                  ; Yes ... flat champ colors
0CD1: 32 F9 E0       LD    ($E0F9),A          ;{-1_champColors} Store champion colors flag * J0CCE
0CD4: C5             PUSH  BC                 ;
0CD5: 0E 01          LD    C,$01              ;
0CD7: CD E7 03       CALL  $03E7              ;{TransColor} 
0CDA: 79             LD    A,C                ;
0CDB: C1             POP   BC                 ;
0CDC: 06 1E          LD    B,$1E              ; * J0CE5
0CDE: 77             LD    (HL),A             ; * J0CE0
0CDF: 23             INC   HL                 ;
0CE0: 10 FC          DJNZ  $CDE               ; 
0CE2: 23             INC   HL                 ;
0CE3: 23             INC   HL                 ;
0CE4: 0D             DEC   C                  ;
0CE5: 20 F5          JR    NZ,$CDC            ; 
0CE7: 21 0F 2B       LD    HL,$2B0F           ; Status box script
0CEA: CD 00 03       CALL  $0300              ;{RunTextScript} 
0CED: CD 68 06       CALL  $0668              ; 
0CF0: CD 85 06       CALL  $0685              ;{PrintHigh} 
0CF3: 3A 46 E0       LD    A,($E046)          ; 
0CF6: CB 67          BIT   4,A                ;
0CF8: 28 0F          JR    Z,$D09             ; 
0CFA: CD 03 06       CALL  $0603              ;{SwapPlayers} 
0CFD: CD 68 06       CALL  $0668              ; 
0D00: CD 03 06       CALL  $0603              ;{SwapPlayers} 
0D03: 21 72 2B       LD    HL,$2B72           ; "P2 " status box script
0D06: CD 00 03       CALL  $0300              ;{RunTextScript} 
0D09: CD D5 06       CALL  $06D5              ; * J0CF8
0D0C: CD 2C 21       CALL  $212C              ; 
0D0F: CD 8A 29       CALL  $298A              ; 
0D12: 3A 0E E5       LD    A,($E50E)          ; * C0B85,J152B,C2866
0D15: 0E 02          LD    C,$02              ;
0D17: FE 1A          CP    $1A                ;
0D19: 38 04          JR    C,$D1F             ; 
0D1B: D6 1A          SUB   $1A                ;
0D1D: 0E 07          LD    C,$07              ;
0D1F: C6 40          ADD   $40                ; * J0D19
;
0D21: 32 52 80       LD    ($8052),A          ; Put "point letter" ... * C0271
0D24: 79             LD    A,C                ; ... in top center ...
0D25: 32 52 84       LD    ($8452),A          ; ... status area
0D28: C9             RET                      ; Done


0D29: 21 00 80       LD    HL,$8000           ; * C0013,C010A,C0187,C0745,C0CBF
0D2C: 01 00 08       LD    BC,$0800           ;
0D2F: CD FA 05       CALL  $05FA              ; 
0D32: 21 00 E1       LD    HL,$E100           ;
0D35: 01 C6 00       LD    BC,$00C6           ;
0D38: CD FA 05       CALL  $05FA              ; 
0D3B: 3A 43 E0       LD    A,($E043)          ;{-1_cabMode} Cabinet mode * J0DA3
0D3E: 3D             DEC   A                  ;
0D3F: 28 09          JR    Z,$D4A             ; 
0D41: 21 46 E0       LD    HL,$E046           ;
0D44: AF             XOR   A                  ;
0D45: CB 5E          BIT   3,(HL)             ;
0D47: 28 01          JR    Z,$D4A             ; 
0D49: 3C             INC   A                  ;
0D4A: 32 4C E0       LD    ($E04C),A          ;{-1_flipValue} * J0D3F,J0D47
;
0D4D: 21 04 D0       LD    HL,$D004           ;
0D50: AE             XOR   (HL)               ;
0D51: 21 3C E0       LD    HL,$E03C           ;
0D54: 36 EF          LD    (HL),$EF           ;
0D56: 16 FF          LD    D,$FF              ;
0D58: 1F             RRA                      ;
0D59: 30 03          JR    NC,$D5E            ; 
0D5B: 14             INC   D                  ;
0D5C: 36 F1          LD    (HL),$F1           ;
0D5E: 23             INC   HL                 ; * J0D59
0D5F: 72             LD    (HL),D             ;
0D60: 01 00 40       LD    BC,$4000           ; B=40, C=0
0D63: AF             XOR   A                  ; A is now 0
0D64: ED 79          OUT   (C),A              ; Write 0 ... * J0D67
0D66: 0C             INC   C                  ; ... to ports ...
0D67: 10 FB          DJNZ  $D64               ; ... 00 through 3F
0D69: F3             DI                       ;
0D6A: CD 7D 0D       CALL  $0D7D              ;{AddSound2} Queue up a stop-sound command
0D6D: FB             EI                       ;
0D6E: C9             RET                      ;

0D6F: F3             DI                       ; * C0C44,J12D1
0D70: CD 75 0D       CALL  $0D75              ;{AddSound} 
0D73: FB             EI                       ;
0D74: C9             RET                      ;
```

# Add Sound

```code
AddSound: 
; Add sound command A to the sound effect queue.
;
0D75: E5             PUSH  HL                 ; Save HL * C014D,C0D70,C132C,C1375,J13E8,C1522,C1571,J174B,C1768,C1D1D,C1DCC,C27D7,C2854,C2860
0D76: 21 46 E0       LD    HL,$E046           ;
0D79: CB 7E          BIT   7,(HL)             ;
0D7B: E1             POP   HL                 ;
0D7C: F0             RET   P                  ;
;
AddSound2: 
0D7D: E5             PUSH  HL                 ; * C0456,C0D6A
0D7E: 2A DE E1       LD    HL,($E1DE)         ;{-1_SndQBack} Get the back (next to store) of the sound queue
0D81: 26 E0          LD    H,$E0              ; Sound queue is at $E000..$E007
0D83: 77             LD    (HL),A             ; Store next sound effect to play
0D84: 7D             LD    A,L                ; Bump the ...
0D85: 3C             INC   A                  ; ... back
0D86: E6 07          AND   $07                ; And wrap it (only 8 bytes in queue)
0D88: 32 DE E1       LD    ($E1DE),A          ;{-1_SndQBack} Store the new back
0D8B: E1             POP   HL                 ; Restore HL
0D8C: C9             RET                      ; Done

0D8D: CD 48 29       CALL  $2948              ; * C0C05
0D90: CD C2 0C       CALL  $0CC2              ; 
0D93: 06 20          LD    B,$20              ;
0D95: C5             PUSH  BC                 ; * J0DA1
0D96: CD 06 11       CALL  $1106              ; 
0D99: 21 E2 E1       LD    HL,$E1E2           ;
0D9C: 7E             LD    A,(HL)             ;
0D9D: C6 08          ADD   $08                ;
0D9F: 77             LD    (HL),A             ;
0DA0: C1             POP   BC                 ;
0DA1: 10 F2          DJNZ  $D95               ; 
0DA3: C3 3B 0D       JP    $0D3B              ; 

TxtCmd_09:
; Handle the bubble-ship shot opening a crater in the ground.
;
0DA6: DD 5E 02       LD    E,(IX+$02)         ; Get ...
0DA9: DD 56 03       LD    D,(IX+$03)         ; ... text script
0DAC: 01 4A 30       LD    BC,$304A           ;
0DAF: 81             ADD   A,C                ;
0DB0: 4F             LD    C,A                ;
0DB1: 0A             LD    A,(BC)             ;
0DB2: 4F             LD    C,A                ;
0DB3: EB             EX    DE,HL              ;
0DB4: 11 20 00       LD    DE,$0020           ;
0DB7: 7E             LD    A,(HL)             ; * J0DBC
0DB8: A7             AND   A                  ;
0DB9: 20 03          JR    NZ,$DBE            ; 
0DBB: 19             ADD   HL,DE              ;
0DBC: 18 F9          JR    $DB7               ; 
0DBE: 22 54 E0       LD    ($E054),HL         ; * J0DB9,J0DD4,J0DDA
0DC1: 0A             LD    A,(BC)             ; * J0DCB
0DC2: 03             INC   BC                 ;
0DC3: 3D             DEC   A                  ;
0DC4: C8             RET   Z                  ;
0DC5: F2 CD 0D       JP    P,$0DCD            ; 
0DC8: 3C             INC   A                  ;
0DC9: 77             LD    (HL),A             ;
0DCA: 19             ADD   HL,DE              ;
0DCB: 18 F4          JR    $DC1               ; 
0DCD: 3A 54 E0       LD    A,($E054)          ; * J0DC5
0DD0: 3C             INC   A                  ;
0DD1: 6F             LD    L,A                ;
0DD2: E6 1F          AND   $1F                ;
0DD4: 20 E8          JR    NZ,$DBE            ; 
0DD6: 7D             LD    A,L                ;
0DD7: D6 20          SUB   $20                ;
0DD9: 6F             LD    L,A                ;
0DDA: 18 E2          JR    $DBE               ; 
0DDC: CD 5B 12       CALL  $125B              ; * C026E,C0280
0DDF: 3A E2 E1       LD    A,($E1E2)          ; 
0DE2: 21 09 E5       LD    HL,$E509           ;
0DE5: 47             LD    B,A                ;
0DE6: AE             XOR   (HL)               ;
0DE7: E6 F8          AND   $F8                ;
0DE9: C8             RET   Z                  ;
0DEA: 78             LD    A,B                ;
0DEB: E6 F8          AND   $F8                ;
0DED: 77             LD    (HL),A             ;
0DEE: CD 06 11       CALL  $1106              ; 
0DF1: 3A 4D E0       LD    A,($E04D)          ; 
0DF4: A7             AND   A                  ;
0DF5: C0             RET   NZ                 ;
0DF6: 21 0B E5       LD    HL,$E50B           ;
0DF9: 34             INC   (HL)               ;
0DFA: 7E             LD    A,(HL)             ;
0DFB: 5F             LD    E,A                ;
0DFC: A7             AND   A                  ;
0DFD: 28 07          JR    Z,$E06             ; 
0DFF: E6 1F          AND   $1F                ;
0E01: 20 03          JR    NZ,$E06            ; 
0E03: CD D6 29       CALL  $29D6              ; 
0E06: 7B             LD    A,E                ; * J0DFD,J0E01
0E07: 2A 16 E5       LD    HL,($E516)         ; 
0E0A: BE             CP    (HL)               ;
0E0B: 20 0B          JR    NZ,$E18            ; 
0E0D: 23             INC   HL                 ;
0E0E: 7E             LD    A,(HL)             ;
0E0F: E6 7F          AND   $7F                ;
0E11: 32 D7 E1       LD    ($E1D7),A          ; 
0E14: 23             INC   HL                 ;
0E15: 22 16 E5       LD    ($E516),HL         ; 
0E18: 21 D7 E1       LD    HL,$E1D7           ; * J0E0B
0E1B: 7E             LD    A,(HL)             ;
0E1C: 3D             DEC   A                  ;
0E1D: F8             RET   M                  ;
0E1E: 36 00          LD    (HL),$00           ;
0E20: FE 18          CP    $18                ;
0E22: D2 45 0F       JP    NC,$0F45           ; 
0E25: FE 17          CP    $17                ;
0E27: 28 26          JR    Z,$E4F             ; 
0E29: D6 06          SUB   $06                ;
0E2B: FA 8A 0E       JP    M,$0E8A            ; 
0E2E: D6 07          SUB   $07                ;
0E30: FA F0 0E       JP    M,$0EF0            ; 
0E33: 87             ADD   A,A                ;
0E34: 87             ADD   A,A                ;
0E35: 87             ADD   A,A                ;
0E36: 5F             LD    E,A                ;
0E37: 16 00          LD    D,$00              ;
0E39: FD 21 00 10    LD    IY,$1000           ;
0E3D: FD 19          ADD   IY,DE              ;
0E3F: CD 93 0E       CALL  $0E93              ; 
0E42: FD 7E 06       LD    A,(IY+$06)         ;
0E45: A7             AND   A                  ;
0E46: 28 03          JR    Z,$E4B             ; 
0E48: CD FD 07       CALL  $07FD              ; 
0E4B: DD 71 00       LD    (IX+$00),C         ; * J0E46
0E4E: C9             RET                      ;
0E4F: 3E 19          LD    A,$19              ; * J0E27
0E51: 32 70 E3       LD    ($E370),A          ;{-1_??object7??} 
0E54: C9             RET                      ;
0E55: 3E 01          LD    A,$01              ; * J0E8B
0E57: 32 DC E1       LD    ($E1DC),A          ; 
0E5A: 2A E4 E0       LD    HL,($E0E4)         ; 
0E5D: 7D             LD    A,L                ;
0E5E: E6 1F          AND   $1F                ;
0E60: F6 C0          OR    $C0                ;
0E62: 6F             LD    L,A                ;
0E63: 36 0A          LD    (HL),$0A           ;
0E65: 01 20 00       LD    BC,$0020           ;
0E68: 5D             LD    E,L                ;
0E69: 09             ADD   HL,BC              ;
0E6A: 36 0B          LD    (HL),$0B           ;
0E6C: 7B             LD    A,E                ;
0E6D: 3D             DEC   A                  ;
0E6E: E6 1F          AND   $1F                ;
0E70: F6 C0          OR    $C0                ;
0E72: 6F             LD    L,A                ;
0E73: CD 81 29       CALL  $2981              ; 
0E76: C6 41          ADD   $41                ;
0E78: 77             LD    (HL),A             ;
0E79: 22 DA E1       LD    ($E1DA),HL         ; 
0E7C: 09             ADD   HL,BC              ;
0E7D: 36 F2          LD    (HL),$F2           ;
0E7F: 01 E0 03       LD    BC,$03E0           ;
0E82: 09             ADD   HL,BC              ;
0E83: 3A F9 E0       LD    A,($E0F9)          ;{-1_champColors} 
0E86: C6 05          ADD   $05                ;
0E88: 77             LD    (HL),A             ;
0E89: C9             RET                      ;
0E8A: 3C             INC   A                  ; * J0E2B
0E8B: 28 C8          JR    Z,$E55             ; 
0E8D: C6 05          ADD   $05                ;
0E8F: 32 08 E5       LD    ($E508),A          ; 
0E92: C9             RET                      ;
0E93: FD 7E 00       LD    A,(IY+$00)         ; * C0E3F
0E96: FE 02          CP    $02                ;
0E98: 28 1B          JR    Z,$EB5             ; 
0E9A: FE 07          CP    $07                ;
0E9C: 38 1C          JR    C,$EBA             ; 
0E9E: 16 00          LD    D,$00              ; * C0F2D
0EA0: FD 5E 05       LD    E,(IY+$05)         ;
0EA3: DD 21 70 E3    LD    IX,$E370           ;
0EA7: FD 46 04       LD    B,(IY+$04)         ; * J0EC1
0EAA: DD 7E 00       LD    A,(IX+$00)         ; * J0EB2
0EAD: A7             AND   A                  ;
0EAE: 28 13          JR    Z,$EC3             ; 
0EB0: DD 19          ADD   IX,DE              ;
0EB2: 10 F6          DJNZ  $EAA               ; 
0EB4: C9             RET                      ;
0EB5: 21 D7 E1       LD    HL,$E1D7           ; * J0E98
0EB8: 36 11          LD    (HL),$11           ;
0EBA: 11 F0 FF       LD    DE,$FFF0           ; * J0E9C,C0EF9
0EBD: DD 21 F0 E4    LD    IX,$E4F0           ;
0EC1: 18 E4          JR    $EA7               ; 
0EC3: FD 7E 00       LD    A,(IY+$00)         ; * J0EAE
0EC6: DD 77 0C       LD    (IX+$0C),A         ;
0EC9: FD 7E 01       LD    A,(IY+$01)         ;
0ECC: DD 77 0D       LD    (IX+$0D),A         ;
0ECF: 3A 09 E5       LD    A,($E509)          ; 
0ED2: D6 02          SUB   $02                ;
0ED4: DD 77 0F       LD    (IX+$0F),A         ;
0ED7: CD 3D 15       CALL  $153D              ; 
0EDA: FD 86 03       ADD   A,(IY+$03)         ;
0EDD: DD 77 07       LD    (IX+$07),A         ;
0EE0: DD 36 0B 00    LD    (IX+$0B),$00       ;
0EE4: DD 36 03 00    LD    (IX+$03),$00       ;
0EE8: DD 36 0E 00    LD    (IX+$0E),$00       ;
0EEC: FD 4E 02       LD    C,(IY+$02)         ;
0EEF: C9             RET                      ;
0EF0: 3C             INC   A                  ; * J0E30
0EF1: CA 40 0F       JP    Z,$0F40            ; 
0EF4: F5             PUSH  AF                 ;
0EF5: FD 21 4E 10    LD    IY,$104E           ;
0EF9: CD BA 0E       CALL  $0EBA              ; 
0EFC: F1             POP   AF                 ;
0EFD: C6 86          ADD   $86                ;
0EFF: DD 77 0D       LD    (IX+$0D),A         ;
0F02: DD 71 00       LD    (IX+$00),C         ;
0F05: 21 4A 30       LD    HL,$304A           ;
0F08: 85             ADD   A,L                ;
0F09: C6 80          ADD   $80                ;
0F0B: 6F             LD    L,A                ;
0F0C: 6E             LD    L,(HL)             ;
0F0D: FD 2A E4 E0    LD    IY,($E0E4)         ; * J0F43
0F11: 11 20 00       LD    DE,$0020           ;
0F14: 7E             LD    A,(HL)             ; * J0F20
0F15: 23             INC   HL                 ;
0F16: 3D             DEC   A                  ;
0F17: F2 22 0F       JP    P,$0F22            ; 
0F1A: 3C             INC   A                  ;
0F1B: FD 77 00       LD    (IY+$00),A         ;
0F1E: FD 19          ADD   IY,DE              ;
0F20: 18 F2          JR    $F14               ; 
0F22: C8             RET   Z                  ; * J0F17
0F23: 22 E6 E0       LD    ($E0E6),HL         ; 
0F26: 3D             DEC   A                  ;
0F27: 28 11          JR    Z,$F3A             ; 
0F29: FD 21 55 10    LD    IY,$1055           ;
0F2D: CD 9E 0E       CALL  $0E9E              ; 
0F30: DD 36 0A 00    LD    (IX+$0A),$00       ;
0F34: DD 34 0E       INC   (IX+$0E)           ;
0F37: DD 71 00       LD    (IX+$00),C         ;
0F3A: 3E 0D          LD    A,$0D              ; * J0F27
0F3C: 32 D7 E1       LD    ($E1D7),A          ; 
0F3F: C9             RET                      ;
0F40: 2A E6 E0       LD    HL,($E0E6)         ; * J0EF1
0F43: 18 C8          JR    $F0D               ; 
0F45: D6 1F          SUB   $1F                ; * J0E22
0F47: FA B7 0F       JP    M,$0FB7            ; 
0F4A: 21 C5 E1       LD    HL,$E1C5           ;
0F4D: 0E FF          LD    C,$FF              ;
0F4F: 23             INC   HL                 ; * J0F53
0F50: 0C             INC   C                  ;
0F51: D6 08          SUB   $08                ;
0F53: F2 4F 0F       JP    P,$0F4F            ; 
0F56: C6 08          ADD   $08                ;
0F58: 28 10          JR    Z,$F6A             ; 
0F5A: 77             LD    (HL),A             ;
0F5B: 23             INC   HL                 ;
0F5C: 23             INC   HL                 ;
0F5D: 23             INC   HL                 ;
0F5E: 77             LD    (HL),A             ;
0F5F: 23             INC   HL                 ;
0F60: 23             INC   HL                 ;
0F61: 23             INC   HL                 ;
0F62: 77             LD    (HL),A             ;
0F63: 0D             DEC   C                  ;
0F64: F8             RET   M                  ;
0F65: 21 D6 E1       LD    HL,$E1D6           ;
0F68: 34             INC   (HL)               ;
0F69: C9             RET                      ;
0F6A: 77             LD    (HL),A             ; * J0F58
0F6B: FD 21 70 E3    LD    IY,$E370           ;
0F6F: 11 10 00       LD    DE,$0010           ;
0F72: 06 19          LD    B,$19              ;
0F74: 0D             DEC   C                  ;
0F75: FA A5 0F       JP    M,$0FA5            ; 
0F78: FD 7E 00       LD    A,(IY+$00)         ; * J0F9C
0F7B: D6 22          SUB   $22                ;
0F7D: FE 06          CP    $06                ;
0F7F: 30 19          JR    NC,$F9A            ; 
0F81: 6F             LD    L,A                ;
0F82: CB 4D          BIT   1,L                ;
0F84: 20 14          JR    NZ,$F9A            ; 
0F86: 61             LD    H,C                ;
0F87: FD 7E 0D       LD    A,(IY+$0D)         ;
0F8A: FE 2A          CP    $2A                ;
0F8C: 20 01          JR    NZ,$F8F            ; 
0F8E: 24             INC   H                  ;
0F8F: 25             DEC   H                  ; * J0F8C
0F90: 20 08          JR    NZ,$F9A            ; 
0F92: CB 55          BIT   2,L                ;
0F94: 20 09          JR    NZ,$F9F            ; 
0F96: FD 36 00 24    LD    (IY+$00),$24       ;
0F9A: FD 19          ADD   IY,DE              ; * J0F7F,J0F84,J0F90,J0FA3
0F9C: 10 DA          DJNZ  $F78               ; 
0F9E: C9             RET                      ;
0F9F: FD 36 0F 01    LD    (IY+$0F),$01       ; * J0F94
0FA3: 18 F5          JR    $F9A               ; 
0FA5: FD 7E 00       LD    A,(IY+$00)         ; * J0F75,J0FB4
0FA8: D6 1E          SUB   $1E                ;
0FAA: FE 02          CP    $02                ;
0FAC: 30 04          JR    NC,$FB2            ; 
0FAE: FD 36 00 24    LD    (IY+$00),$24       ;
0FB2: FD 19          ADD   IY,DE              ; * J0FAC
0FB4: 10 EF          DJNZ  $FA5               ; 
0FB6: C9             RET                      ;
0FB7: C6 08          ADD   $08                ; * J0F47
0FB9: FE 04          CP    $04                ;
0FBB: 30 08          JR    NC,$FC5            ; 
0FBD: 21 0B E5       LD    HL,$E50B           ;
0FC0: 46             LD    B,(HL)             ;
0FC1: 23             INC   HL                 ;
0FC2: 70             LD    (HL),B             ;
0FC3: 23             INC   HL                 ;
0FC4: 77             LD    (HL),A             ;
0FC5: 3A D5 E1       LD    A,($E1D5)          ; * J0FBB
0FC8: A7             AND   A                  ;
0FC9: C8             RET   Z                  ;
0FCA: 5F             LD    E,A                ;
0FCB: 16 00          LD    D,$00              ;
0FCD: FD 21 FF E3    LD    IY,$E3FF           ;
0FD1: FD 19          ADD   IY,DE              ;
0FD3: 21 70 E3       LD    HL,$E370           ;
0FD6: 1E 10          LD    E,$10              ;
0FD8: 01 3A 05       LD    BC,$053A           ;
0FDB: 7E             LD    A,(HL)             ; * J0FE1
0FDC: A7             AND   A                  ;
0FDD: CA 5D 10       JP    Z,$105D            ; 
0FE0: 19             ADD   HL,DE              ;
0FE1: 10 F8          DJNZ  $FDB               ; 
0FE3: C9             RET                      ;


0FE4: 00             NOP                      ;
0FE5: 00             NOP                      ;
0FE6: 00             NOP                      ;
0FE7: 00             NOP                      ;
0FE8: 00             NOP                      ;
0FE9: 00             NOP                      ;
0FEA: 00             NOP                      ;
0FEB: 00             NOP                      ;
0FEC: 00             NOP                      ;
0FED: 00             NOP                      ;
0FEE: 00             NOP                      ;
0FEF: 00             NOP                      ;
0FF0: 00             NOP                      ;
0FF1: 00             NOP                      ;
0FF2: 00             NOP                      ;
0FF3: 00             NOP                      ;
0FF4: 00             NOP                      ;
0FF5: 00             NOP                      ;
0FF6: 00             NOP                      ;
0FF7: 00             NOP                      ;
0FF8: 00             NOP                      ;
0FF9: 00             NOP                      ;
0FFA: 00             NOP                      ;
0FFB: 00             NOP                      ;
0FFC: 00             NOP                      ;
0FFD: 00             NOP                      ;
0FFE: 00             NOP                      ;
0FFF: A5             AND   L                  ;
1000: 00             NOP                      ;
1001: 0E 12          LD    C,$12              ;
1003: F0             RET   P                  ;
1004: 10 00          DJNZ  $1006              ; 
1006: 01 00 01       LD    BC,$0100           ; * J1004
1009: 0F             RRCA                     ;
100A: 12             LD    (DE),A             ;
100B: F0             RET   P                  ;
100C: 10 00          DJNZ  $100E              ; 
100E: 01 00 02       LD    BC,$0200           ; * J100C
1011: 10 12          DJNZ  $1025              ; 
1013: F0             RET   P                  ;
1014: 10 00          DJNZ  $1016              ; 
1016: 01 00 03       LD    BC,$0300           ; * J1014
1019: 11 12 F0       LD    DE,$F012           ;
101C: 10 00          DJNZ  $101E              ; 
101E: 01 00 0D       LD    BC,$0D00           ; * J101C
1021: 25             DEC   H                  ;
1022: 12             LD    (DE),A             ;
1023: FD 
1024: 06 10          LD    B,$10              ;
1026: 00             NOP                      ;
1027: 00             NOP                      ;
1028: 0A             LD    A,(BC)             ;
1029: 21 1D F0       LD    HL,$F01D           ;
102C: 05             DEC   B                  ;
102D: 10 00          DJNZ  $102F              ; 
102F: 00             NOP                      ; * J102D
1030: 04             INC   B                  ;
1031: 12             LD    (DE),A             ;
1032: 16 F4          LD    D,$F4              ;
1034: 18 10          JR    $1046              ; 
1036: 01 00 05       LD    BC,$0500           ;
1039: 16 16          LD    D,$16              ;
103B: F2 18 10       JP    P,$1018            ; 
103E: 01 00 06       LD    BC,$0600           ;
1041: 1B             DEC   DE                 ;
1042: 16 F0          LD    D,$F0              ;
1044: 18 10          JR    $1056              ; 
1046: 01 00 0B       LD    BC,$0B00           ; * J1034
1049: 23             INC   HL                 ;
104A: 17             RLA                      ;
104B: F0             RET   P                  ;
104C: 01 20 00       LD    BC,$0020           ;
104F: 00             NOP                      ;
1050: 13             INC   DE                 ;
1051: 00             NOP                      ;
1052: 10 00          DJNZ  $1054              ; 
1054: 00             NOP                      ; * J1052
1055: 00             NOP                      ;
1056: 4A             LD    C,D                ; * J1044
1057: 14             INC   D                  ;
1058: 00             NOP                      ;
1059: 03             INC   BC                 ;
105A: 40             LD    B,B                ;
105B: 00             NOP                      ;
105C: 00             NOP                      ;
105D: EB             EX    DE,HL              ; * J0FDD
105E: DD 21 00 00    LD    IX,$0000           ;
1062: DD 19          ADD   IX,DE              ;
1064: DD 71 0D       LD    (IX+$0D),C         ; * J1BBD
1067: DD 36 09 00    LD    (IX+$09),$00       ;
106B: DD 36 08 00    LD    (IX+$08),$00       ;
106F: FD 56 07       LD    D,(IY+$07)         ;
1072: DD 72 07       LD    (IX+$07),D         ;
1075: FD 7E 00       LD    A,(IY+$00)         ;
1078: D6 1E          SUB   $1E                ;
107A: FE 0A          CP    $0A                ;
107C: D0             RET   NC                 ;
107D: CB 4F          BIT   1,A                ;
107F: C0             RET   NZ                 ;
1080: FD 7E 03       LD    A,(IY+$03)         ;
1083: D6 10          SUB   $10                ;
1085: FE E0          CP    $E0                ;
1087: D0             RET   NC                 ;
1088: 79             LD    A,C                ;
1089: FE 3A          CP    $3A                ;
108B: 28 36          JR    Z,$10C3            ; 
108D: CD 92 20       CALL  $2092              ; 
1090: ED 5F          LD    A,R                ;
1092: E6 7F          AND   $7F                ;
1094: 47             LD    B,A                ;
1095: 3A 03 E3       LD    A,($E303)          ;{-1_buggyX} 
1098: 80             ADD   A,B                ;
1099: D6 2F          SUB   $2F                ;
109B: 4F             LD    C,A                ;
109C: DD 96 03       SUB   (IX+$03)           ;
109F: C6 08          ADD   $08                ;
10A1: FE 11          CP    $11                ;
10A3: 79             LD    A,C                ;
10A4: 30 03          JR    NC,$10A9           ; 
10A6: EE 10          XOR   $10                ;
10A8: 4F             LD    C,A                ;
10A9: FD BE 03       CP    (IY+$03)           ; * J10A4
10AC: 17             RLA                      ;
10AD: DD 77 0C       LD    (IX+$0C),A         ;
10B0: 79             LD    A,C                ;
10B1: CD 38 15       CALL  $1538              ; 
10B4: 92             SUB   D                  ;
10B5: 1F             RRA                      ;
10B6: 1F             RRA                      ;
10B7: 1F             RRA                      ;
10B8: E6 1F          AND   $1F                ;
10BA: C6 02          ADD   $02                ;
10BC: 41             LD    B,C                ;
10BD: CB 38          SRL   B                  ;
10BF: 0E 2E          LD    C,$2E              ;
10C1: 18 0F          JR    $10D2              ; 
10C3: 01 2A 8F       LD    BC,$8F2A           ; * J108B
10C6: CB 3A          SRL   D                  ;
10C8: CB 3A          SRL   D                  ;
10CA: CB 3A          SRL   D                  ;
10CC: 3A 14 E5       LD    A,($E514)          ; 
10CF: EE 1F          XOR   $1F                ;
10D1: 92             SUB   D                  ;
10D2: 21 00 31       LD    HL,$3100           ; * J10C1
10D5: 85             ADD   A,L                ;
10D6: 6F             LD    L,A                ;
10D7: 56             LD    D,(HL)             ;
10D8: FD 7E 03       LD    A,(IY+$03)         ;
10DB: DD 77 03       LD    (IX+$03),A         ;
10DE: CB 3F          SRL   A                  ;
10E0: 90             SUB   B                  ;
10E1: 30 02          JR    NC,$10E5           ; 
10E3: ED 44          NEG                      ;
10E5: 1E FF          LD    E,$FF              ; * J10E1
10E7: 1C             INC   E                  ; * J10E9
10E8: 92             SUB   D                  ;
10E9: 30 FC          JR    NC,$10E7           ; 
10EB: 82             ADD   A,D                ;
10EC: DD 73 05       LD    (IX+$05),E         ;
10EF: 06 08          LD    B,$08              ;
10F1: CB 27          SLA   A                  ; * J10FB
10F3: BA             CP    D                  ;
10F4: CB 13          RL    E                  ;
10F6: CB 43          BIT   0,E                ;
10F8: 20 01          JR    NZ,$10FB           ; 
10FA: 92             SUB   D                  ;
10FB: 10 F4          DJNZ  $10F1              ; * J10F8
10FD: 7B             LD    A,E                ;
10FE: 2F             CPL                      ;
10FF: DD 77 04       LD    (IX+$04),A         ;
1102: DD 71 00       LD    (IX+$00),C         ;
1105: C9             RET                      ;
1106: 21 D9 E1       LD    HL,$E1D9           ; * C0D96,C0DEE
1109: 7E             LD    A,(HL)             ;
110A: A7             AND   A                  ;
110B: C2 9A 11       JP    NZ,$119A           ; 
110E: 3A 08 E5       LD    A,($E508)          ; 
1111: FE 03          CP    $03                ;
1113: 30 79          JR    NC,$118E           ; 
1115: 47             LD    B,A                ;
1116: 05             DEC   B                  ;
1117: 21 B4 2C       LD    HL,$2CB4           ;
111A: 3A E2 E1       LD    A,($E1E2)          ; 
111D: 1F             RRA                      ;
111E: 1F             RRA                      ;
111F: 1F             RRA                      ;
1120: E6 1F          AND   $1F                ;
1122: 85             ADD   A,L                ;
1123: 10 02          DJNZ  $1127              ; 
1125: C6 20          ADD   $20                ;
1127: 6F             LD    L,A                ; * J1123
1128: 4E             LD    C,(HL)             ;
1129: 3A E2 E1       LD    A,($E1E2)          ; * J11CE,J11D5,J11E7
112C: 1F             RRA                      ;
112D: 1F             RRA                      ;
112E: 1F             RRA                      ;
112F: E6 1F          AND   $1F                ;
1131: 5F             LD    E,A                ;
1132: 16 83          LD    D,$83              ;
1134: FD 21 00 04    LD    IY,$0400           ;
1138: FD 19          ADD   IY,DE              ;
113A: EB             EX    DE,HL              ;
113B: 11 20 00       LD    DE,$0020           ;
113E: 06 07          LD    B,$07              ;
1140: 3A 14 E5       LD    A,($E514)          ; 
1143: B8             CP    B                  ; * J114B
1144: 28 07          JR    Z,$114D            ; 
1146: 36 00          LD    (HL),$00           ;
1148: 19             ADD   HL,DE              ;
1149: FD 19          ADD   IY,DE              ;
114B: 10 F6          DJNZ  $1143              ; 
114D: 22 E4 E0       LD    ($E0E4),HL         ; * J1144
1150: 71             LD    (HL),C             ;
1151: FD 36 00 04    LD    (IY+$00),$04       ;
1155: 19             ADD   HL,DE              ; * J115E
1156: FD 19          ADD   IY,DE              ;
1158: 36 F3          LD    (HL),$F3           ;
115A: FD 36 00 04    LD    (IY+$00),$04       ;
115E: 10 F5          DJNZ  $1155              ; 
1160: 3A E2 E1       LD    A,($E1E2)          ; 
1163: 1F             RRA                      ;
1164: 1F             RRA                      ;
1165: E6 3E          AND   $3E                ;
1167: C6 00          ADD   $00                ;
1169: 6F             LD    L,A                ;
116A: 26 E2          LD    H,$E2              ;
116C: 3A 14 E5       LD    A,($E514)          ; 
116F: EE 1F          XOR   $1F                ;
1171: 57             LD    D,A                ;
1172: FD 21 24 2C    LD    IY,$2C24           ;
1176: FD 09          ADD   IY,BC              ;
1178: FD 7E 00       LD    A,(IY+$00)         ;
117B: 5F             LD    E,A                ;
117C: E6 70          AND   $70                ;
117E: 07             RLCA                     ;
117F: B2             OR    D                  ;
1180: 07             RLCA                     ;
1181: 07             RLCA                     ;
1182: 07             RLCA                     ;
1183: 77             LD    (HL),A             ;
1184: E6 F8          AND   $F8                ;
1186: 57             LD    D,A                ;
1187: 7B             LD    A,E                ;
1188: E6 07          AND   $07                ;
118A: B2             OR    D                  ;
118B: 23             INC   HL                 ;
118C: 77             LD    (HL),A             ;
118D: C9             RET                      ;
118E: 87             ADD   A,A                ; * J1113
118F: C6 7A          ADD   $7A                ;
1191: 77             LD    (HL),A             ;
1192: 87             ADD   A,A                ;
1193: 28 02          JR    Z,$1197            ; 
1195: 3E 0A          LD    A,$0A              ;
1197: 32 D8 E1       LD    ($E1D8),A          ; * J1193
119A: 4E             LD    C,(HL)             ; * J110B
119B: CB 19          RR    C                  ;
119D: D8             RET   C                  ;
119E: CB 19          RR    C                  ;
11A0: 21 D8 E1       LD    HL,$E1D8           ;
11A3: 35             DEC   (HL)               ;
11A4: F2 B6 11       JP    P,$11B6            ; 
11A7: 36 0B          LD    (HL),$0B           ;
11A9: 3A 14 E5       LD    A,($E514)          ; 
11AC: 38 3C          JR    C,$11EA            ; 
11AE: FE 07          CP    $07                ;
11B0: 28 3E          JR    Z,$11F0            ; 
11B2: 3E 0B          LD    A,$0B              ;
11B4: 18 27          JR    $11DD              ; 
11B6: 7E             LD    A,(HL)             ; * J11A4
11B7: 21 14 E5       LD    HL,$E514           ;
11BA: 30 1C          JR    NC,$11D8           ; 
11BC: A7             AND   A                  ;
11BD: 20 01          JR    NZ,$11C0           ; 
11BF: 35             DEC   (HL)               ;
11C0: C6 F3          ADD   $F3                ; * J11BD,J11EE
11C2: FE FC          CP    $FC                ;
11C4: 38 02          JR    C,$11C8            ; 
11C6: D6 0C          SUB   $0C                ;
11C8: 4F             LD    C,A                ; * J11C4
11C9: C6 03          ADD   $03                ; * J11CB
11CB: FA C9 11       JP    M,$11C9            ; 
11CE: C2 29 11       JP    NZ,$1129           ; 
11D1: 79             LD    A,C                ;
11D2: D6 10          SUB   $10                ;
11D4: 4F             LD    C,A                ;
11D5: C3 29 11       JP    $1129              ; 
11D8: FE 09          CP    $09                ; * J11BA
11DA: 20 01          JR    NZ,$11DD           ; 
11DC: 34             INC   (HL)               ;
11DD: 2F             CPL                      ; * J11B4,J11DA
11DE: C6 F2          ADD   $F2                ;
11E0: FE F0          CP    $F0                ;
11E2: 30 02          JR    NC,$11E6           ; 
11E4: C6 0C          ADD   $0C                ;
11E6: 4F             LD    C,A                ; * J11E2
11E7: C3 29 11       JP    $1129              ; 
11EA: FE 04          CP    $04                ; * J11AC
11EC: 3E 0B          LD    A,$0B              ;
11EE: 20 D0          JR    NZ,$11C0           ; 
11F0: 21 D9 E1       LD    HL,$E1D9           ; * J11B0
11F3: 34             INC   (HL)               ;
11F4: 2A E1 E1       LD    HL,($E1E1)         ; 
11F7: 22 F1 E0       LD    ($E0F1),HL         ; 
11FA: 21 00 00       LD    HL,$0000           ;
11FD: 22 EF E0       LD    ($E0EF),HL         ; 
1200: C9             RET                      ;

TxtCmd_0A:
; Init "MOON PATROL" splash sequence 
;
1201: 21 44 2D       LD    HL,$2D44           ; Data for splash text
1204: ED 53 EB E0    LD    ($E0EB),DE         ;{-1_splshObjLSB} Will be pointer to screen, but this isn't a pointer to screen memory yet * J1253
1208: 22 E9 E0       LD    ($E0E9),HL         ;{-1_splashLSB} Hold pointer to splash text data * J124D
120B: 3A 4E E0       LD    A,($E04E)          ;{-1_isrCNT_1} Current ISR
120E: C6 03          ADD   $03                ; Next action is in current+3
1210: DD 77 01       LD    (IX+$01),A         ; Set trigger time
1213: DD 36 00 0B    LD    (IX+$00),$0B       ; Transition to state 0B (running) * J121E
1217: C9             RET                      ; Done

TxtCmd_0B:
; Run "MOON PATROL" splash sequence
;
1218: 3A 4E E0       LD    A,($E04E)          ;{-1_isrCNT_1} Current ISR
121B: DD BE 01       CP    (IX+$01)           ; Time to take action?
121E: 20 F3          JR    NZ,$1213           ; No ... stay in state 0B and out
;
1220: 2A EB E0       LD    HL,($E0EB)         ;{-1_splshObjLSB} Pointer to screen
1223: 23             INC   HL                 ; Next column ...
1224: 22 EB E0       LD    ($E0EB),HL         ;{-1_splshObjLSB} ... over
1227: 2B             DEC   HL                 ; But this column for now
1228: EB             EX    DE,HL              ; To DE
1229: FD 21 00 04    LD    IY,$0400           ; Offset to Color set
122D: FD 19          ADD   IY,DE              ; IY now points to color memory
122F: 2A E9 E0       LD    HL,($E0E9)         ;{-1_splashLSB} Get data cursor
1232: 01 20 00       LD    BC,$0020           ; Constant for down one row
;
1235: 7E             LD    A,(HL)             ; Get next data value * J1247
1236: 23             INC   HL                 ; Next in script
1237: 3D             DEC   A                  ; Is this ...
1238: FE 03          CP    $03                ; ... a special byte?
123A: 38 0D          JR    C,$1249            ; Yes ... go handle it
123C: 3C             INC   A                  ; No ... restore the value
123D: 12             LD    (DE),A             ; Character to screen
123E: FD 36 00 80    LD    (IY+$00),$80       ; Color set to screen (plus upper tile bit = 1)
1242: EB             EX    DE,HL              ; Add $20 ...
1243: 09             ADD   HL,BC              ; ... to ...
1244: EB             EX    DE,HL              ; ... next ...
1245: FD 09          ADD   IY,BC              ; ... row ...
1247: 18 EC          JR    $1235              ; Continue with next byte
;
; Command byte is 3, 2, 1
;
; 1 = print "1982 IREM CORP" and let command end
; 2 = store cursor and continue (go to next column)
; 3 = set screen pointer and continue
;
1249: 3D             DEC   A                  ; Subtract 1 again * J123A
124A: FA 55 12       JP    M,$1255            ; Data byte is 1 or 0
124D: 28 B9          JR    Z,$1208            ; Jump if byte is 2 ... store cursor and continue
;
124F: 5E             LD    E,(HL)             ; Screen pointer LSB
1250: 23             INC   HL                 ; Next in script
1251: 56             LD    D,(HL)             ; Screen pointer MSB
1252: 23             INC   HL                 ; Next in script
1253: 18 AF          JR    $1204              ; Save pointers and continue

1255: 21 97 2C       LD    HL,$2C97           ; "1982 IREM CORP" script * J124A
1258: C3 00 03       JP    $0300              ;{RunTextScript} Print script and return



125B: 3A 0D E5       LD    A,($E50D)          ; * C0DDC
125E: 3D             DEC   A                  ;
125F: F8             RET   M                  ; No indicator to print ... out
;
1260: 21 AB 2C       LD    HL,$2CAB           ; "CAUTION" script
1263: 3A 4E E0       LD    A,($E04E)          ;{-1_isrCNT_1} 
1266: E6 3F          AND   $3F                ;
1268: 28 1B          JR    Z,$1285            ;{PrintCaution} Print "CAUTION", show indicators, out
126A: E6 1F          AND   $1F                ;
126C: C0             RET   NZ                 ;
126D: CD 7B 03       CALL  $037B              ;{EraseScript} Erase "CAUTION"
1270: CD 88 12       CALL  $1288              ; Show caution indicators
1273: 36 02          LD    (HL),$02           ;
1275: EB             EX    DE,HL              ;
1276: 36 12          LD    (HL),$12           ;
1278: 21 0B E5       LD    HL,$E50B           ;
127B: 7E             LD    A,(HL)             ;
127C: 23             INC   HL                 ;
127D: 96             SUB   (HL)               ;
127E: FE 40          CP    $40                ;
1280: D8             RET   C                  ;
1281: 23             INC   HL                 ;
1282: 36 00          LD    (HL),$00           ;
1284: C9             RET                      ;

PrintCaution:
; Print word "CAUTION" then fill in one of the 3 bubbles as follows:
; E50D ==1 : First row, character 19, color 2
; E50D ==2 : Second row, character 18, color 3
; E50D ==* : Third row, character 19, color 3
;
1285: CD 00 03       CALL  $0300              ;{RunTextScript} Print "CAUTION" * J1268
1288: 3A 0D E5       LD    A,($E50D)          ; * C1270
128B: 21 55 80       LD    HL,$8055           ; Screen location for caution indicator
128E: 01 02 13       LD    BC,$1302           ; Caution-bubble character, color set 2
1291: 11 20 00       LD    DE,$0020           ; Offset for one row
1294: 3D             DEC   A                  ; ??First row?
1295: 28 08          JR    Z,$129F            ; Yes ... we are set up
1297: 19             ADD   HL,DE              ; Point to second row
1298: 0C             INC   C                  ; Color set 3
1299: 05             DEC   B                  ; 1st bubble (character 18)
129A: 3D             DEC   A                  ; ??Second row?
129B: 28 02          JR    Z,$129F            ; Yes ... we are set up
129D: 04             INC   B                  ; Back to 2nd bubble (character 19)
129E: 19             ADD   HL,DE              ; Next row
;
129F: 70             LD    (HL),B             ; Put bubble ... * J1295,J129B
12A0: 11 00 04       LD    DE,$0400           ; ... on screen ...
12A3: EB             EX    DE,HL              ; ... with ...
12A4: 19             ADD   HL,DE              ; ... desired ...
12A5: 71             LD    (HL),C             ; ... color
12A6: C9             RET                      ; Done

12A7: 21 70 E3       LD    HL,$E370           ; * C027A
12AA: 11 10 00       LD    DE,$0010           ;
12AD: 01 02 19       LD    BC,$1902           ;
12B0: 7E             LD    A,(HL)             ; * J12D5
12B1: FE 14          CP    $14                ;
12B3: 28 2A          JR    Z,$12DF            ; 
12B5: FE 1E          CP    $1E                ;
12B7: 38 1B          JR    C,$12D4            ; 
12B9: FE 20          CP    $20                ;
12BB: 38 08          JR    C,$12C5            ; 
12BD: FE 22          CP    $22                ;
12BF: 38 13          JR    C,$12D4            ; 
12C1: FE 2A          CP    $2A                ;
12C3: 30 0F          JR    NC,$12D4           ; 
12C5: 3A DF E1       LD    A,($E1DF)          ; * J12BB
12C8: 1F             RRA                      ;
12C9: 1F             RRA                      ;
12CA: D8             RET   C                  ;
12CB: 79             LD    A,C                ; * J12E4
12CC: 32 DF E1       LD    ($E1DF),A          ; * J12DD
12CF: C6 15          ADD   $15                ;
12D1: C3 6F 0D       JP    $0D6F              ; Make flying ship sound and out

12D4: 19             ADD   HL,DE              ; * J12B7,J12BF,J12C3
12D5: 10 D9          DJNZ  $12B0              ; 
12D7: 3A DF E1       LD    A,($E1DF)          ; 
12DA: A7             AND   A                  ;
12DB: C8             RET   Z                  ;
12DC: AF             XOR   A                  ;
12DD: 18 ED          JR    $12CC              ; 
12DF: 3A DF E1       LD    A,($E1DF)          ; * J12B3
12E2: 1F             RRA                      ;
12E3: 0D             DEC   C                  ;
12E4: 30 E5          JR    NC,$12CB           ; 
12E6: C9             RET                      ;
12E7: 3A DC E1       LD    A,($E1DC)          ; * C027D
12EA: A7             AND   A                  ;
12EB: C8             RET   Z                  ;
12EC: 3A 4E E0       LD    A,($E04E)          ;{-1_isrCNT_1} 
12EF: E6 0F          AND   $0F                ;
12F1: 28 04          JR    Z,$12F7            ; 
12F3: E6 07          AND   $07                ;
12F5: C0             RET   NZ                 ;
12F6: 3C             INC   A                  ;
12F7: 3C             INC   A                  ; * J12F1
12F8: 4F             LD    C,A                ;
12F9: 2A DA E1       LD    HL,($E1DA)         ; 
12FC: 7E             LD    A,(HL)             ;
12FD: D6 5A          SUB   $5A                ;
12FF: 28 0A          JR    Z,$130B            ; 
1301: 3C             INC   A                  ;
1302: 06 04          LD    B,$04              ;
1304: C6 05          ADD   $05                ; * J1308
1306: 28 03          JR    Z,$130B            ; 
1308: 10 FA          DJNZ  $1304              ; 
130A: C9             RET                      ;
130B: 11 00 04       LD    DE,$0400           ; * J12FF,J1306
130E: 19             ADD   HL,DE              ;
130F: 71             LD    (HL),C             ;
1310: C9             RET                      ;

ISROBJRun_01: ; Buggy waiting to start
;
1311: 21 00 40       LD    HL,$4000           ; ?? and initial X (40)
1314: 22 02 E3       LD    ($E302),HL         ; Store ?? and initial X
1317: 3A 4E E0       LD    A,($E04E)          ;{-1_isrCNT_1} Decrement counter ...
131A: E6 03          AND   $03                ; ... at 1/4 ISR rate
131C: 20 48          JR    NZ,$1366           ; Not time to decrement
131E: DD 35 0A       DEC   (IX+$0A)           ; Decrement the counter for waiting to start
1321: F2 66 13       JP    P,$1366            ; Not time to start
;
1324: 21 5F 2A       LD    HL,$2A5F           ; "CHAMPION COURSE 1 GO" script
1327: CD 7B 03       CALL  $037B              ;{EraseScript} Erase the text
132A: 3E 18          LD    A,$18              ; Start ...
132C: CD 75 0D       CALL  $0D75              ;{AddSound} ... background music
132F: 18 29          JR    $135A              ; 

ISROBJRun_02: ; Buggy running normally
;
1331: CD 48 15       CALL  $1548              ;{PlayerShot} Check starting player shot
1334: 07             RLCA                     ;
1335: 07             RLCA                     ;
1336: 30 2B          JR    NC,$1363           ; 
1338: 2A 1A E3       LD    HL,($E31A)         ; 
133B: 11 79 FF       LD    DE,$FF79           ;
133E: 19             ADD   HL,DE              ;
133F: 7C             LD    A,H                ;
1340: A7             AND   A                  ;
1341: 20 05          JR    NZ,$1348           ; 
1343: 7D             LD    A,L                ;
1344: FE D1          CP    $D1                ;
1346: 38 02          JR    C,$134A            ; 
1348: 3E D1          LD    A,$D1              ; * J1341
134A: 5F             LD    E,A                ; * J1346
134B: CB 3B          SRL   E                  ;
134D: 83             ADD   A,E                ;
134E: 2F             CPL                      ;
134F: 6F             LD    L,A                ;
1350: 3E FF          LD    A,$FF              ;
1352: DE 00          SBC   $00                ;
1354: 67             LD    H,A                ;
1355: 2B             DEC   HL                 ;
1356: 67             LD    H,A                ;
1357: 22 08 E3       LD    ($E308),HL         ; 
;
135A: DD 34 00       INC   (IX+$00)           ; Transition buggy to "next" state (running or jumping) * J132F
135D: CD 76 15       CALL  $1576              ; * J136E
1360: C3 B8 08       JP    $08B8              ;{DrawObject} Draw the buggy

1363: CD 8A 14       CALL  $148A              ; * J1336
1366: CD 33 15       CALL  $1533              ; * J131C,J1321
1369: D6 1C          SUB   $1C                ;
136B: 32 07 E3       LD    ($E307),A          ;{-1_buggyY} * J1386
136E: 18 ED          JR    $135D              ; 

ISROBJRun_03: ; Start player jump
;
1370: DD 34 00       INC   (IX+$00)           ; Player is now in state "jumping"
1373: 3E 14          LD    A,$14              ; Play ...
1375: CD 75 0D       CALL  $0D75              ;{AddSound} ... car jump
1378: CD 48 15       CALL  $1548              ;{PlayerShot} Check starting player shot * J13C0
137B: 2A 0E E3       LD    HL,($E30E)         ; 
137E: CD A4 14       CALL  $14A4              ; 
1381: CD 33 15       CALL  $1533              ; 
1384: D6 1E          SUB   $1E                ; Initial Y offset to start jump
1386: 18 E3          JR    $136B              ; Set Y and draw buggy

ISROBJRun_04: ; Handle buggy jumping
;
1388: CD 48 15       CALL  $1548              ;{PlayerShot} Check starting player shot
138B: 2A 0E E3       LD    HL,($E30E)         ; 
138E: CD A4 14       CALL  $14A4              ; 
1391: 2A 06 E3       LD    HL,($E306)         ; 
1394: ED 5B 08 E3    LD    DE,($E308)         ; 
1398: 19             ADD   HL,DE              ;
1399: 22 06 E3       LD    ($E306),HL         ; 
139C: 21 0C 00       LD    HL,$000C           ;
139F: 19             ADD   HL,DE              ;
13A0: 22 08 E3       LD    ($E308),HL         ; 
13A3: CB 14          RL    H                  ;
13A5: 38 0F          JR    C,$13B6            ; 
13A7: CD 33 15       CALL  $1533              ; 
13AA: D6 1D          SUB   $1D                ;
13AC: 47             LD    B,A                ;
13AD: 3A 07 E3       LD    A,($E307)          ;{-1_buggyY} 
13B0: B8             CP    B                  ;
13B1: 38 03          JR    C,$13B6            ; 
13B3: DD 34 00       INC   (IX+$00)           ; Player is now in state "landing"
13B6: CD AC 15       CALL  $15AC              ; * J13A5,J13B1
13B9: C3 B8 08       JP    $08B8              ;{DrawObject} 

ISROBJRun_05: ; ?? Handle player landing
;
13BC: DD 36 00 02    LD    (IX+$00),$02       ;
13C0: 18 B6          JR    $1378              ; 

ISROBJRun_06: ; ?? Start player crash
;
13C2: 2A 02 E3       LD    HL,($E302)         ; 
13C5: ED 5B 04 E3    LD    DE,($E304)         ; 
13C9: 19             ADD   HL,DE              ;
13CA: 22 02 E3       LD    ($E302),HL         ; 
13CD: 2A 06 E3       LD    HL,($E306)         ; 
13D0: ED 5B 08 E3    LD    DE,($E308)         ; 
13D4: 19             ADD   HL,DE              ;
13D5: 22 06 E3       LD    ($E306),HL         ; 
13D8: CD B8 08       CALL  $08B8              ;{DrawObject} 
13DB: DD 35 0A       DEC   (IX+$0A)           ;
13DE: C0             RET   NZ                 ;
13DF: DD 34 00       INC   (IX+$00)           ;
13E2: DD 36 0D 03    LD    (IX+$0D),$03       ;
13E6: 3E 1F          LD    A,$1F              ; Play ...
13E8: C3 75 0D       JP    $0D75              ;{AddSound} ... car explosion then return


ISROBJRun_07: ; ?? Handle player crash ?? wheels?
;
13EB: AF             XOR   A                  ;
13EC: 32 A2 E1       LD    ($E1A2),A          ; 
13EF: DD 35 0A       DEC   (IX+$0A)           ;
13F2: F0             RET   P                  ;
13F3: DD 7E 0D       LD    A,(IX+$0D)         ;
13F6: FE 09          CP    $09                ;
13F8: D2 18 01       JP    NC,$0118           ; 
13FB: FE 05          CP    $05                ;
13FD: 38 0B          JR    C,$140A            ; 
13FF: CD B8 08       CALL  $08B8              ;{DrawObject} 
1402: DD 34 0D       INC   (IX+$0D)           ;
1405: DD 36 0A 0E    LD    (IX+$0A),$0E       ;
1409: C9             RET                      ;
;
140A: DD CB 0A 4E    BIT   1,(IX+$0A)         ; * J13FD
140E: C0             RET   NZ                 ;
140F: EE 07          XOR   $07                ;
1411: DD 77 0D       LD    (IX+$0D),A         ;
1414: DD 7E 0A       LD    A,(IX+$0A)         ;
1417: FE C0          CP    $C0                ;
1419: D2 B8 08       JP    NC,$08B8           ;{DrawObject} 
141C: DD 36 0D 05    LD    (IX+$0D),$05       ;
1420: C9             RET                      ;

ISROBJRun_08:
; Hold buggy in air during splash sequence.
; Then return to the bugging-jumping handler
;
1421: DD 35 0A       DEC   (IX+$0A)           ; Decrement the count-down timer
1424: DD 7E 0A       LD    A,(IX+$0A)         ; Has the counter ...
1427: FE 50          CP    $50                ; ... dropped low enough?
1429: D0             RET   NC                 ; No ... stay in this state
142A: 21 4D E0       LD    HL,$E04D           ; ??
142D: 34             INC   (HL)               ;
142E: DD 36 00 04    LD    (IX+$00),$04       ; Transition to handling buggy jumping
1432: C9             RET                      ; Done

ISROBJRun_1C:
;
1433: CD DB 20       CALL  $20DB              ; 
1436: 22 D6 E0       LD    ($E0D6),HL         ; 
1439: 7C             LD    A,H                ;
143A: D6 08          SUB   $08                ;
143C: FE F0          CP    $F0                ;
143E: D2 52 08       JP    NC,$0852           ; 
1441: 2A D8 E0       LD    HL,($E0D8)         ; 
1444: 23             INC   HL                 ;
1445: CB 7C          BIT   7,H                ;
1447: 20 02          JR    NZ,$144B           ; 
1449: 2B             DEC   HL                 ;
144A: 2B             DEC   HL                 ;
144B: 22 D8 E0       LD    ($E0D8),HL         ; * J1447
144E: 2A DA E0       LD    HL,($E0DA)         ; 
1451: ED 5B DC E0    LD    DE,($E0DC)         ; 
1455: 19             ADD   HL,DE              ;
1456: 4C             LD    C,H                ;
1457: 22 DA E0       LD    ($E0DA),HL         ; 
145A: 21 24 00       LD    HL,$0024           ;
145D: 19             ADD   HL,DE              ;
145E: 22 DC E0       LD    ($E0DC),HL         ; 
1461: CB 14          RL    H                  ;
1463: 38 1F          JR    C,$1484            ; 
1465: C6 0B          ADD   $0B                ;
1467: CD 38 15       CALL  $1538              ; 
146A: D6 08          SUB   $08                ;
146C: B9             CP    C                  ;
146D: 30 15          JR    NC,$1484           ; 
146F: ED 5B DC E0    LD    DE,($E0DC)         ; 
1473: 21 00 00       LD    HL,$0000           ;
1476: ED 52          SBC   HL,DE              ;
1478: CB 3A          SRL   D                  ;
147A: CB 1B          RR    E                  ;
147C: CB 3A          SRL   D                  ;
147E: CB 1B          RR    E                  ;
1480: 19             ADD   HL,DE              ;
1481: 22 DC E0       LD    ($E0DC),HL         ; 
1484: CD B8 08       CALL  $08B8              ;{DrawObject} * J1463,J146D
1487: C3 EF 20       JP    $20EF              ; 
148A: 3A 49 E0       LD    A,($E049)          ; * C1363
148D: 87             ADD   A,A                ;
148E: 21 28 30       LD    HL,$3028           ;
1491: 85             ADD   A,L                ;
1492: 6F             LD    L,A                ;
1493: 5E             LD    E,(HL)             ;
1494: 23             INC   HL                 ;
1495: 66             LD    H,(HL)             ;
1496: 2E 00          LD    L,$00              ;
1498: 22 0E E3       LD    ($E30E),HL         ; 
149B: AF             XOR   A                  ;
149C: CB 13          RL    E                  ;
149E: 17             RLA                      ;
149F: 57             LD    D,A                ;
14A0: ED 53 1C E3    LD    ($E31C),DE         ; 
14A4: ED 5B 02 E3    LD    DE,($E302)         ; * C137E,C138E
14A8: AF             XOR   A                  ;
14A9: ED 52          SBC   HL,DE              ;
14AB: 4F             LD    C,A                ;
14AC: 7C             LD    A,H                ;
14AD: 30 03          JR    NC,$14B2           ; 
14AF: ED 44          NEG                      ;
14B1: 0C             INC   C                  ;
14B2: FE 18          CP    $18                ; * J14AD
14B4: 38 02          JR    C,$14B8            ; 
14B6: 3E 18          LD    A,$18              ;
14B8: 21 30 30       LD    HL,$3030           ; * J14B4
14BB: 85             ADD   A,L                ;
14BC: 6F             LD    L,A                ;
14BD: 5E             LD    E,(HL)             ;
14BE: 16 00          LD    D,$00              ;
14C0: 2A 04 E3       LD    HL,($E304)         ; 
14C3: 7C             LD    A,H                ;
14C4: A7             AND   A                  ;
14C5: F2 D4 14       JP    P,$14D4            ; 
14C8: 0D             DEC   C                  ;
14C9: 20 11          JR    NZ,$14DC           ; 
14CB: 2F             CPL                      ;
14CC: 67             LD    H,A                ;
14CD: 7D             LD    A,L                ;
14CE: 2F             CPL                      ;
14CF: 6F             LD    L,A                ;
14D0: 23             INC   HL                 ;
14D1: EB             EX    DE,HL              ;
14D2: 18 03          JR    $14D7              ; 
14D4: 0D             DEC   C                  ; * J14C5
14D5: 28 57          JR    Z,$152E            ; 
14D7: A7             AND   A                  ; * J14D2
14D8: ED 52          SBC   HL,DE              ;
14DA: 30 52          JR    NC,$152E           ; 
14DC: 11 02 00       LD    DE,$0002           ; * J14C9
14DF: 3A 4E E0       LD    A,($E04E)          ;{-1_isrCNT_1} * J1531
14E2: 1F             RRA                      ;
14E3: 2A 04 E3       LD    HL,($E304)         ; 
14E6: ED 5A          ADC   HL,DE              ;
14E8: 22 04 E3       LD    ($E304),HL         ; 
14EB: ED 5B 02 E3    LD    DE,($E302)         ; 
14EF: 19             ADD   HL,DE              ;
14F0: 22 02 E3       LD    ($E302),HL         ; 
14F3: 54             LD    D,H                ;
14F4: 21 DC E1       LD    HL,$E1DC           ;
14F7: 7E             LD    A,(HL)             ;
14F8: 3D             DEC   A                  ;
14F9: C0             RET   NZ                 ;
14FA: 3A 0B E5       LD    A,($E50B)          ; 
14FD: 87             ADD   A,A                ;
14FE: 87             ADD   A,A                ;
14FF: 87             ADD   A,A                ;
1500: C6 08          ADD   $08                ;
1502: 82             ADD   A,D                ;
1503: D0             RET   NC                 ;
1504: 36 00          LD    (HL),$00           ;
1506: 21 0E E5       LD    HL,$E50E           ;
1509: 34             INC   (HL)               ;
150A: 7E             LD    A,(HL)             ;
150B: 06 09          LD    B,$09              ;
150D: FE 19          CP    $19                ;
150F: 28 0F          JR    Z,$1520            ; 
1511: 38 01          JR    C,$1514            ; 
1513: 3D             DEC   A                  ;
1514: D6 05          SUB   $05                ; * J1511,J1519
1516: CA C0 27       JP    Z,$27C0            ; 
1519: 10 F9          DJNZ  $1514              ; 
151B: FE 06          CP    $06                ;
151D: CA C0 27       JP    Z,$27C0            ; 
1520: 3E 10          LD    A,$10              ; Play ... * J150F
1522: CD 75 0D       CALL  $0D75              ;{AddSound} ... passing point
1525: AF             XOR   A                  ;
1526: 0E 01          LD    C,$01              ;
1528: CD C2 02       CALL  $02C2              ;{NewTxtCmd} 
152B: C3 12 0D       JP    $0D12              ; 
152E: 11 FD FF       LD    DE,$FFFD           ; * J14D5,J14DA
1531: 18 AC          JR    $14DF              ; 

1533: 3A 03 E3       LD    A,($E303)          ;{-1_buggyX} * C1366,C1381,C13A7,C18C3
1536: C6 20          ADD   $20                ;
1538: 47             LD    B,A                ; * C10B1,C1467,C157C,C1A83,C1AE5,C1CFA
1539: 3A E2 E1       LD    A,($E1E2)          ; 
153C: 80             ADD   A,B                ;
153D: C6 06          ADD   $06                ; * C0ED7
153F: CB 3F          SRL   A                  ;
1541: CB 3F          SRL   A                  ;
1543: 6F             LD    L,A                ;
1544: 26 E2          LD    H,$E2              ;
1546: 7E             LD    A,(HL)             ;
1547: C9             RET                      ;
``` 

# Player Shot

```code 
PlayerShot: 
; Check the fire button and initiate a player shot if
; there is room (only 1 forward shot and 4 air shots at
; a time).
;
1548: 2A 4A E0       LD    HL,($E04A)         ; Current inputs to L, last inputs to H * C1331,C1378,C1388
154B: 7C             LD    A,H                ; Last inputs to accumulator
154C: AD             XOR   L                  ; Bits are only "1" now if inputs have changed
154D: A5             AND   L                  ; Bits are only "1" now if buttons have transitioned from off to on (pressed)
154E: 07             RLCA                     ; Upper bit is the "fire" button
154F: D0             RET   NC                 ; Fire button not pressed ... out
1550: 4F             LD    C,A                ; Hold transition status
1551: 3A 20 E3       LD    A,($E320)          ; Player forward shot
1554: A7             AND   A                  ; Object already active?
1555: 20 05          JR    NZ,$155C           ; Yes ... only allow one forward shot
1557: 3E 0A          LD    A,$0A              ; Init player ...
1559: 32 20 E3       LD    ($E320),A          ; ... forward shot routine
;
155C: 21 30 E3       LD    HL,$E330           ; Start of player air shot objects * J1555
155F: 06 04          LD    B,$04              ; Maximum of 4 shots in the air
1561: 11 10 00       LD    DE,$0010           ; 16 bytes per shot structure
1564: 7E             LD    A,(HL)             ; Is slot ... * J1569
1565: A7             AND   A                  ; ... available?
1566: 28 05          JR    Z,$156D            ; Yes ... use this one
;
1568: 19             ADD   HL,DE              ; Point to next slot
1569: 10 F9          DJNZ  $1564              ; Do all 4 slots
156B: 79             LD    A,C                ; Restore A
156C: C9             RET                      ; Done ... no air shot
; 
156D: 36 0E          LD    (HL),$0E           ; Init player air shot routine * J1566
156F: 3E 12          LD    A,$12              ; Play ...
1571: CD 75 0D       CALL  $0D75              ;{AddSound} ... missile from car
1574: 79             LD    A,C                ; Restore A
1575: C9             RET                      ; Done

1576: 3A 03 E3       LD    A,($E303)          ;{-1_buggyX} * C135D
1579: 4F             LD    C,A                ;
157A: C6 04          ADD   $04                ;
157C: CD 38 15       CALL  $1538              ; 
157F: D6 09          SUB   $09                ;
1581: CD C9 15       CALL  $15C9              ; 
1584: 7A             LD    A,D                ;
1585: EE 03          XOR   $03                ;
1587: 57             LD    D,A                ;
1588: 3E 09          LD    A,$09              ;
158A: CD 92 15       CALL  $1592              ; 
158D: 2C             INC   L                  ;
158E: 14             INC   D                  ;
158F: 14             INC   D                  ;
1590: 3E 0D          LD    A,$0D              ;
1592: 81             ADD   A,C                ; * C158A
1593: 4F             LD    C,A                ;
1594: 2C             INC   L                  ;
1595: 2C             INC   L                  ;
1596: 7D             LD    A,L                ;
1597: E6 3F          AND   $3F                ;
1599: 6F             LD    L,A                ;
159A: 7E             LD    A,(HL)             ;
159B: D6 09          SUB   $09                ;
159D: CD ED 08       CALL  $08ED              ; 
15A0: 47             LD    B,A                ;
15A1: FD 23          INC   IY                 ; * J15C7
15A3: FD 23          INC   IY                 ;
15A5: FD 23          INC   IY                 ;
15A7: FD 23          INC   IY                 ;
15A9: C3 76 09       JP    $0976              ;{ObjDraw_0E} 
15AC: 3A 03 E3       LD    A,($E303)          ;{-1_buggyX} * C13B6
15AF: 4F             LD    C,A                ;
15B0: 3A 07 E3       LD    A,($E307)          ;{-1_buggyY} 
15B3: C6 11          ADD   $11                ;
15B5: CD C9 15       CALL  $15C9              ; 
15B8: 7A             LD    A,D                ;
15B9: EE 03          XOR   $03                ;
15BB: 57             LD    D,A                ;
15BC: 3E 09          LD    A,$09              ;
15BE: CD C5 15       CALL  $15C5              ; 
15C1: 14             INC   D                  ;
15C2: 14             INC   D                  ;
15C3: 3E 0D          LD    A,$0D              ;
15C5: 81             ADD   A,C                ; * C15BE
15C6: 4F             LD    C,A                ;
15C7: 18 D8          JR    $15A1              ; 
15C9: 0C             INC   C                  ; * C1581,C15B5
15CA: CD ED 08       CALL  $08ED              ; 
15CD: 47             LD    B,A                ;
15CE: 11 00 05       LD    DE,$0500           ;
15D1: 3A E2 E1       LD    A,($E1E2)          ; 
15D4: CB 67          BIT   4,A                ;
15D6: 20 01          JR    NZ,$15D9           ; 
15D8: 14             INC   D                  ;
15D9: FD 21 A4 E1    LD    IY,$E1A4           ; * J15D6
15DD: C3 76 09       JP    $0976              ;{ObjDraw_0E} 

ISROBJRun_0A: ; Init player forward shot
;
15E0: DD 36 0A 0C    LD    (IX+$0A),$0C       ; 12 movements before ending
15E4: 3A 07 E3       LD    A,($E307)          ;{-1_buggyY} Moon buggy Y coordinate
15E7: C6 0A          ADD   $0A                ; Start shot in front of gun
15E9: 32 27 E3       LD    ($E327),A          ; Set the forward shot's Y coordinate
15EC: 2A 02 E3       LD    HL,($E302)         ; X coordinate to H
15EF: 11 00 1C       LD    DE,$1C00           ; 1C offset for Y
15F2: 19             ADD   HL,DE              ; Add 1C to H (Y coordinate of shot)
15F3: 22 22 E3       LD    ($E322),HL         ; Store Y coordinate for forward shot (set ?? to 0)
15F6: DD 34 00       INC   (IX+$00)           ; Handler is now "0B Run player forward shot"
15F9: C9             RET                      ; Done

ISROBJRun_0B: ; Run player forward shot
;
15FA: DD 35 0A       DEC   (IX+$0A)           ; Has the shot moved all of its allocated time?
15FD: 28 19          JR    Z,$1618            ; Yes ... begin its death
15FF: 2A 22 E3       LD    HL,($E322)         ; Forward shot X coordinate (and ???)
1602: 11 5D 04       LD    DE,$045D           ; +4 X forward rate
1605: 19             ADD   HL,DE              ;
1606: 22 22 E3       LD    ($E322),HL         ; 
1609: DD 7E 0A       LD    A,(IX+$0A)         ; Count
160C: 1F             RRA                      ; Is it odd or even?
160D: 3E 09          LD    A,$09              ; Object_09 First shot image
160F: 38 01          JR    C,$1612            ; It is odd ... use first shot image
1611: 3C             INC   A                  ; It is even ... use Object_0A second shot image
1612: DD 77 0D       LD    (IX+$0D),A         ; Set new shot image * J160F
1615: C3 B8 08       JP    $08B8              ;{DrawObject} 
;
1618: DD 34 00       INC   (IX+$00)           ; Transition to 0C to show the shot exploding * J15FD
161B: DD 36 0A 03    LD    (IX+$0A),$03       ; Three runs before changing sprite image
161F: DD 36 0D 0B    LD    (IX+$0D),$0B       ; Start with first explosion Object_0B
;
1623: 3A E2 E1       LD    A,($E1E2)          ; * C1DF7,C1E18
1626: DD 86 03       ADD   A,(IX+$03)         ;
1629: DD 77 0F       LD    (IX+$0F),A         ; ?? X offset accounting for speed ??
162C: C9             RET                      ;

ISROBJRun_0C: ; Run player forward shot exploding (miss)
ISROBJRun_0D: ; Run exploding boulder (hit)
;
162D: CD 31 08       CALL  $0831              ; ?? changing X based on speed
1630: DD 35 0A       DEC   (IX+$0A)           ; Count down delay between image changes
1633: F0             RET   P                  ; Return ... not time to change image
1634: DD 7E 0D       LD    A,(IX+$0D)         ; Get image number
1637: FE 0D          CP    $0D                ; Player shot miss explosion end Object_0D?
1639: CA 52 08       JP    Z,$0852            ; Yes ... end the explosion
163C: FE 29          CP    $29                ; Player shot hit explosion end Object_29?
163E: CA 52 08       JP    Z,$0852            ; Yes ... end the explosion
1641: DD 34 0D       INC   (IX+$0D)           ; Next image
1644: DD 36 0A 03    LD    (IX+$0A),$03       ; Set new image delay
1648: C9             RET                      ; Done

ISROBJRun_0E: ; Init player air shot
;
1649: 3A 03 E3       LD    A,($E303)          ;{-1_buggyX} Get the player-object X coordinate
164C: C6 0A          ADD   $0A                ; Offset to where the up-gun is in the image
164E: DD 77 03       LD    (IX+$03),A         ; Set the air-shot's X coordinate
1651: 3A 07 E3       LD    A,($E307)          ;{-1_buggyY} Get the player's Y coordinate
1654: C6 02          ADD   $02                ; Offset to where shot starts
1656: DD 77 07       LD    (IX+$07),A         ; Set shot Y coordinate
1659: DD 34 00       INC   (IX+$00)           ; Next command ... 0F (run the air shot)
165C: C9             RET                      ; Done

ISROBJRun_0F: ; Run player air shot
;
; The player-air-shot is drawn on the text screen using 8 different tile pictures.
; A tile is 8x8 pixels and the shot's tile picture depends on the the x-remainder
; and y-remainder within an 8x8 tile area.
;
; There are 2 Y positions: at the top of the tile and at the bottom of the tile. The
; shot is 4 pixels tall. If the remainder is 0,1,2, or 3 the image tile picture
; draws the shot at the top of the area. For higher Y coordinates the image is drawn
; in the lower part of the area.
;
; There are 4 X positions from left to right with remainder=0,2,4, and 6. The shot is
; 1 pixel wide.
;
; The X and Y coordinates change normally, but the shot itself is drawn on even X and
; every 4 Y.
;
; The shot moves up at the rate of Y = Y-3 every ISR.
;
; The shot leaves the screen (and is removed from play) when the Y coordinate < $3A.
;
165D: 3A 00 E3       LD    A,($E300)          ;{-1_buggyHandler} Moon buggy command
1660: FE 06          CP    $06                ; Is buggy crashing?
1662: 30 2B          JR    NC,$168F           ;{ISROBJRun_10} Yes ... command 6 or greater ... remove shot from active duty
1664: DD 7E 07       LD    A,(IX+$07)         ; Get shot Y coordinate
1667: D6 03          SUB   $03                ; Move it up
1669: FE 3A          CP    $3A                ; Less than 58 (status area) ?
166B: 38 22          JR    C,$168F            ;{ISROBJRun_10} Shot has left the screen ... remove it
166D: DD 77 07       LD    (IX+$07),A         ; New shot Y coordinate
1670: CD 1B 08       CALL  $081B              ;{XYToTextPtr} Get text screen pointer for X,Y coordinates
1673: DD 7E 07       LD    A,(IX+$07)         ; Get Y coordinate
1676: 1F             RRA                      ; Rotate ...
1677: 1F             RRA                      ; ... bit 2 (fours-place) ...
1678: 1F             RRA                      ; ... into carry
1679: 7A             LD    A,D                ; X coordinate divided by 2
167A: 17             RLA                      ; Pull in Y bit to select top (0) or bottom (1) for shot's position in tile
167B: E6 07          AND   $07                ; Select picture tile 60..67 to match x remainder and y
167D: F6 60          OR    $60                ; 8 shot tile pictures at x=0,2,4,6 for bottom and top of tile
167F: 77             LD    (HL),A             ; Store player shot tile on text screen
1680: 11 00 04       LD    DE,$0400           ; Offset ...
1683: 19             ADD   HL,DE              ; ... to tile color
1684: 36 00          LD    (HL),$00           ; Set the color-set to 0
1686: 1F             RRA                      ; Picture is odd? (next picture is at the top of the same tile)
1687: D0             RET   NC                 ; No ... even picture ... no "old shot" to erase
1688: 11 20 FC       LD    DE,$FC20           ; Back around to tile map and down a row
168B: 19             ADD   HL,DE              ; Point to last shot position on the screen
168C: 36 00          LD    (HL),$00           ; Erase the last shot position on the screen
168E: C9             RET                      ; Done

ISROBJRun_10: ; Stop player air shot
;
168F: CD 1B 08       CALL  $081B              ;{XYToTextPtr} Get text screen pointer for X,Y coordinates * J1662,J166B
1692: 36 00          LD    (HL),$00           ; Clear the shot from the screen
1694: DD 36 00 00    LD    (IX+$00),$00       ; Remove the shot object from active duty
1698: C9             RET                      ; Done

1699: DD 4E 03       LD    C,(IX+$03)         ; * C18E3,C1953,C195A,C1A2B,C1A8A,C1B16,C1B27
169C: DD 7E 0C       LD    A,(IX+$0C)         ;
169F: 87             ADD   A,A                ;
16A0: 87             ADD   A,A                ;
16A1: 87             ADD   A,A                ;
16A2: 21 1C 31       LD    HL,$311C           ;
16A5: 85             ADD   A,L                ;
16A6: 6F             LD    L,A                ;
16A7: 3A 20 E3       LD    A,($E320)          ; 
16AA: 11 04 F8       LD    DE,$F804           ;
16AD: D6 0B          SUB   $0B                ;
16AF: 28 06          JR    Z,$16B7            ; 
16B1: 3D             DEC   A                  ;
16B2: 20 17          JR    NZ,$16CB           ; 
16B4: 11 0A F0       LD    DE,$F00A           ;
16B7: 3A 23 E3       LD    A,($E323)          ; * J16AF
16BA: 82             ADD   A,D                ;
16BB: 91             SUB   C                  ;
16BC: FE E8          CP    $E8                ;
16BE: 38 0B          JR    C,$16CB            ; 
16C0: 3A 27 E3       LD    A,($E327)          ; 
16C3: DD 96 07       SUB   (IX+$07)           ;
16C6: 86             ADD   A,(HL)             ;
16C7: 83             ADD   A,E                ;
16C8: F2 4E 17       JP    P,$174E            ; 
16CB: DD 7E 0C       LD    A,(IX+$0C)         ; * J16B2,J16BE
16CE: A7             AND   A                  ;
16CF: F8             RET   M                  ;
16D0: 23             INC   HL                 ;
16D1: 3A 03 E3       LD    A,($E303)          ;{-1_buggyX} 
16D4: 91             SUB   C                  ;
16D5: 86             ADD   A,(HL)             ;
16D6: 23             INC   HL                 ;
16D7: 46             LD    B,(HL)             ;
16D8: 23             INC   HL                 ;
16D9: B8             CP    B                  ;
16DA: 38 05          JR    C,$16E1            ; 
16DC: 96             SUB   (HL)               ;
16DD: 30 01          JR    NC,$16E0           ; 
16DF: AF             XOR   A                  ;
16E0: 80             ADD   A,B                ; * J16DD
16E1: 23             INC   HL                 ; * J16DA
16E2: BE             CP    (HL)               ;
16E3: D2 C4 17       JP    NC,$17C4           ; 
16E6: 23             INC   HL                 ;
16E7: 46             LD    B,(HL)             ;
16E8: 23             INC   HL                 ;
16E9: 86             ADD   A,(HL)             ;
16EA: 6F             LD    L,A                ;
16EB: 24             INC   H                  ;
16EC: 3A 07 E3       LD    A,($E307)          ;{-1_buggyY} 
16EF: 86             ADD   A,(HL)             ;
16F0: DD 96 07       SUB   (IX+$07)           ;
16F3: 3D             DEC   A                  ;
16F4: 80             ADD   A,B                ;
16F5: F8             RET   M                  ;
16F6: 3A 04 D0       LD    A,($D004)          ;{-2_DSW2} Get DIP switches DSW2
16F9: CB 77          BIT   6,A                ; Is invulnerable set?
16FB: C8             RET   Z                  ; Yes ... no crash
;
; Player crash
16FC: E1             POP   HL                 ; We won't be returning
16FD: 3E 07          LD    A,$07              ; Set first command to ... * J1A1F,J1D9B
16FF: 32 00 E3       LD    ($E300),A          ;{-1_buggyHandler} ... handle player crash
1702: 3E 03          LD    A,$03              ;
1704: 32 0D E3       LD    ($E30D),A          ;
1707: AF             XOR   A                  ;
1708: 32 0A E3       LD    ($E30A),A          ;
170B: 32 B0 E3       LD    ($E3B0),A          ;{-1_??objectB??} 
170E: 32 72 E1       LD    ($E172),A          ;
1711: CD 52 08       CALL  $0852              ; 
1714: 06 03          LD    B,$03              ;
1716: 3A 07 E3       LD    A,($E307)          ;{-1_buggyY} 
1719: C6 14          ADD   $14                ;
171B: 4F             LD    C,A                ;
171C: 3A 03 E3       LD    A,($E303)          ;{-1_buggyX} 
171F: 21 D3 E1       LD    HL,$E1D3           ;
1722: 34             INC   (HL)               ;
1723: 21 C0 E3       LD    HL,$E3C0           ;
1726: FD 21 DF 30    LD    IY,$30DF           ;
172A: 36 1C          LD    (HL),$1C           ; * J1744
172C: 23             INC   HL                 ;
172D: 23             INC   HL                 ;
172E: 23             INC   HL                 ;
172F: 77             LD    (HL),A             ;
1730: C6 10          ADD   $10                ;
1732: CD F8 17       CALL  $17F8              ; 
1735: 71             LD    (HL),C             ;
1736: CD F8 17       CALL  $17F8              ; 
1739: 23             INC   HL                 ;
173A: 23             INC   HL                 ;
173B: FD 5E 00       LD    E,(IY+$00)         ;
173E: 73             LD    (HL),E             ;
173F: FD 23          INC   IY                 ;
1741: 23             INC   HL                 ;
1742: 23             INC   HL                 ;
1743: 23             INC   HL                 ;
1744: 10 E4          DJNZ  $172A              ; 
1746: CD A1 08       CALL  $08A1              ; 
1749: 3E 1F          LD    A,$1F              ; Play ...
174B: C3 75 0D       JP    $0D75              ;{AddSound} ... car explosion

174E: 3A E2 E1       LD    A,($E1E2)          ; * J16C8
1751: DD 86 03       ADD   A,(IX+$03)         ;
1754: 32 2F E3       LD    ($E32F),A          ; 
1757: 3E 0D          LD    A,$0D              ;
1759: 32 20 E3       LD    ($E320),A          ; 
175C: 3E 26          LD    A,$26              ;
175E: 32 2D E3       LD    ($E32D),A          ; 
1761: 3E 03          LD    A,$03              ;
1763: 32 2A E3       LD    ($E32A),A          ; 
1766: 3E 01          LD    A,$01              ; Play ...
1768: CD 75 0D       CALL  $0D75              ;{AddSound} ... shot a rock
176B: 11 07 00       LD    DE,$0007           ;
176E: 19             ADD   HL,DE              ;
176F: 7E             LD    A,(HL)             ;
1770: E6 0F          AND   $0F                ;
1772: 0E 01          LD    C,$01              ;
1774: FE 0E          CP    $0E                ;
1776: 30 07          JR    NC,$177F           ; 
1778: CD C2 02       CALL  $02C2              ;{NewTxtCmd} 
177B: E1             POP   HL                 ;
177C: C3 52 08       JP    $0852              ; 
177F: 20 13          JR    NZ,$1794           ; * J1776
1781: CD F0 17       CALL  $17F0              ; 
1784: C6 05          ADD   $05                ;
1786: DD 77 08       LD    (IX+$08),A         ;
1789: CD C2 02       CALL  $02C2              ;{NewTxtCmd} 
178C: DD 34 00       INC   (IX+$00)           ;
178F: DD 36 0A 00    LD    (IX+$0A),$00       ;
1793: C9             RET                      ;
1794: CD 56 08       CALL  $0856              ; * J177F
1797: CD F0 17       CALL  $17F0              ; 
179A: 21 10 FB       LD    HL,$FB10           ;
179D: C6 06          ADD   $06                ; * J1DF0
179F: DD 77 08       LD    (IX+$08),A         ;
17A2: E5             PUSH  HL                 ;
17A3: CD C2 02       CALL  $02C2              ;{NewTxtCmd} 
17A6: E1             POP   HL                 ;
17A7: DD 7E 07       LD    A,(IX+$07)         ;
17AA: 84             ADD   A,H                ;
17AB: DD 77 07       LD    (IX+$07),A         ;
17AE: DD 7E 03       LD    A,(IX+$03)         ;
17B1: 85             ADD   A,L                ;
17B2: DD 77 03       LD    (IX+$03),A         ;
17B5: DD 36 0D 54    LD    (IX+$0D),$54       ;
17B9: DD 36 00 21    LD    (IX+$00),$21       ;
17BD: DD 36 0A 3B    LD    (IX+$0A),$3B       ;
17C1: C3 56 08       JP    $0856              ; 
17C4: 47             LD    B,A                ; * J16E3
17C5: DD 7E 0C       LD    A,(IX+$0C)         ;
17C8: C6 80          ADD   $80                ;
17CA: 4F             LD    C,A                ;
17CB: FE 8B          CP    $8B                ;
17CD: 28 1B          JR    Z,$17EA            ; 
17CF: FE 8E          CP    $8E                ;
17D1: 28 17          JR    Z,$17EA            ; 
17D3: 78             LD    A,B                ;
17D4: 96             SUB   (HL)               ;
17D5: FE 04          CP    $04                ;
17D7: D0             RET   NC                 ;
17D8: DD 71 0C       LD    (IX+$0C),C         ; * J17ED
17DB: 23             INC   HL                 ;
17DC: 23             INC   HL                 ;
17DD: 23             INC   HL                 ;
17DE: 7E             LD    A,(HL)             ;
17DF: 1F             RRA                      ;
17E0: 1F             RRA                      ;
17E1: 1F             RRA                      ;
17E2: 1F             RRA                      ;
17E3: E6 0F          AND   $0F                ;
17E5: 0E 01          LD    C,$01              ;
17E7: C3 C2 02       JP    $02C2              ;{NewTxtCmd} 
17EA: 78             LD    A,B                ; * J17CD,J17D1
17EB: FE FC          CP    $FC                ;
17ED: 30 E9          JR    NC,$17D8           ; 
17EF: C9             RET                      ;
17F0: ED 5F          LD    A,R                ; * C1781,C1797
17F2: E6 03          AND   $03                ;
17F4: C0             RET   NZ                 ;
17F5: 3E 02          LD    A,$02              ;
17F7: C9             RET                      ;
17F8: 23             INC   HL                 ; * C1732,C1736
17F9: FD 5E 00       LD    E,(IY+$00)         ;
17FC: 73             LD    (HL),E             ;
17FD: 23             INC   HL                 ;
17FE: FD 5E 01       LD    E,(IY+$01)         ;
1801: 73             LD    (HL),E             ;
1802: 23             INC   HL                 ;
1803: 23             INC   HL                 ;
1804: FD 23          INC   IY                 ;
1806: FD 23          INC   IY                 ;
1808: C9             RET                      ;

ISROBJRun_09:
;
; ?? Moves background
;
1809: 3A 00 E3       LD    A,($E300)          ;{-1_buggyHandler} Buggy command
180C: FE 06          CP    $06                ; Buggy running normally?
180E: D0             RET   NC                 ; No ... skip
180F: FE 01          CP    $01                ;
1811: 26 00          LD    H,$00              ;
1813: 28 76          JR    Z,$188B            ; 
1815: 2A 1C E3       LD    HL,($E31C)         ; 
1818: ED 5B 1A E3    LD    DE,($E31A)         ; 
181C: 7A             LD    A,D                ;
181D: A7             AND   A                  ;
181E: FA 23 18       JP    M,$1823            ; 
1821: ED 52          SBC   HL,DE              ;
1823: 21 03 00       LD    HL,$0003           ; * J181E
1826: 30 03          JR    NC,$182B           ; 
1828: 21 FE FF       LD    HL,$FFFE           ;
182B: 3A 4E E0       LD    A,($E04E)          ;{-1_isrCNT_1} * J1826
182E: 1F             RRA                      ;
182F: 38 01          JR    C,$1832            ; 
1831: 1D             DEC   E                  ;
1832: 19             ADD   HL,DE              ; * J182F
1833: 22 1A E3       LD    ($E31A),HL         ; 
1836: ED 5B 04 E3    LD    DE,($E304)         ; 
183A: A7             AND   A                  ;
183B: ED 52          SBC   HL,DE              ;
183D: 22 14 E3       LD    ($E314),HL         ; 
1840: EB             EX    DE,HL              ;
1841: 2A E1 E1       LD    HL,($E1E1)         ; 
1844: 19             ADD   HL,DE              ;
1845: 22 E1 E1       LD    ($E1E1),HL         ; 
1848: 3A D9 E1       LD    A,($E1D9)          ; 
184B: 1F             RRA                      ;
184C: 30 3D          JR    NC,$188B           ; 
184E: 2A EF E0       LD    HL,($E0EF)         ; 
1851: 19             ADD   HL,DE              ;
1852: 7C             LD    A,H                ;
1853: C6 06          ADD   $06                ;
1855: FE 0C          CP    $0C                ;
1857: 38 17          JR    C,$1870            ; 
1859: D6 12          SUB   $12                ;
185B: 67             LD    H,A                ;
185C: E5             PUSH  HL                 ;
185D: 21 3F E2       LD    HL,$E23F           ;
1860: 11 42 E2       LD    DE,$E242           ;
1863: 01 40 00       LD    BC,$0040           ;
1866: ED B8          LDDR                     ;
1868: 21 42 E2       LD    HL,$E242           ;
186B: 0E 03          LD    C,$03              ;
186D: ED B8          LDDR                     ;
186F: E1             POP   HL                 ;
1870: 22 EF E0       LD    ($E0EF),HL         ; * J1857
1873: ED 5B F1 E0    LD    DE,($E0F1)         ; 
1877: 19             ADD   HL,DE              ;
1878: 3A 08 E5       LD    A,($E508)          ; 
187B: FE 03          CP    $03                ;
187D: 30 0C          JR    NC,$188B           ; 
187F: 3A E2 E1       LD    A,($E1E2)          ; 
1882: 94             SUB   H                  ;
1883: FE F4          CP    $F4                ;
1885: 38 04          JR    C,$188B            ; 
1887: AF             XOR   A                  ;
1888: 32 D9 E1       LD    ($E1D9),A          ; 
188B: 7C             LD    A,H                ; * J1813,J184C,J187D,J1885
188C: 2F             CPL                      ;
188D: 21 3D E0       LD    HL,$E03D           ;
1890: 86             ADD   A,(HL)             ;
1891: 32 C0 E1       LD    ($E1C0),A          ; 
1894: 2A 14 E3       LD    HL,($E314)         ; 
1897: 54             LD    D,H                ;
1898: 5D             LD    E,L                ;
1899: CB 3C          SRL   H                  ;
189B: CB 1D          RR    L                  ;
189D: 19             ADD   HL,DE              ;
189E: CB 3C          SRL   H                  ;
18A0: CB 1D          RR    L                  ;
18A2: CB 3C          SRL   H                  ;
18A4: CB 1D          RR    L                  ;
18A6: EB             EX    DE,HL              ;
18A7: 2A 04 E5       LD    HL,($E504)         ; 
18AA: 19             ADD   HL,DE              ;
18AB: 22 04 E5       LD    ($E504),HL         ; 
18AE: 7C             LD    A,H                ;
18AF: 2F             CPL                      ;
18B0: 32 C1 E1       LD    ($E1C1),A          ; 
18B3: CB 3A          SRL   D                  ;
18B5: CB 1B          RR    E                  ;
18B7: 2A 06 E5       LD    HL,($E506)         ; 
18BA: 19             ADD   HL,DE              ;
18BB: 22 06 E5       LD    ($E506),HL         ; 
18BE: 7C             LD    A,H                ;
18BF: 2F             CPL                      ;
18C0: 32 C2 E1       LD    ($E1C2),A          ; 
18C3: CD 33 15       CALL  $1533              ; 
18C6: FE C4          CP    $C4                ;
18C8: 30 02          JR    NC,$18CC           ; 
18CA: 3E C4          LD    A,$C4              ;
18CC: C6 28          ADD   $28                ; * J18C8
18CE: 30 01          JR    NC,$18D1           ; 
18D0: AF             XOR   A                  ;
18D1: 47             LD    B,A                ; * J18CE
18D2: C6 94          ADD   $94                ;
18D4: 32 C3 E1       LD    ($E1C3),A          ; 
18D7: CB 28          SRA   B                  ;
18D9: 78             LD    A,B                ;
18DA: C6 72          ADD   $72                ;
18DC: 32 C4 E1       LD    ($E1C4),A          ; 
18DF: C9             RET                      ;

ISROBJRun_1D:
;
18E0: CD 31 08       CALL  $0831              ; 
18E3: CD 99 16       CALL  $1699              ; 
18E6: DD 35 0A       DEC   (IX+$0A)           ;
18E9: F0             RET   P                  ;
18EA: DD 34 0A       INC   (IX+$0A)           ;
18ED: DD 7E 03       LD    A,(IX+$03)         ;
18F0: FE E0          CP    $E0                ;
18F2: D0             RET   NC                 ;
18F3: DD 7E 0C       LD    A,(IX+$0C)         ;
18F6: 17             RLA                      ;
18F7: D8             RET   C                  ;
18F8: 3A C0 E3       LD    A,($E3C0)          ;{-1_??objectC??} 
18FB: A7             AND   A                  ;
18FC: C0             RET   NZ                 ;
18FD: FD 21 70 E3    LD    IY,$E370           ;
1901: 11 10 00       LD    DE,$0010           ;
1904: 06 05          LD    B,$05              ;
1906: FD 7E 00       LD    A,(IY+$00)         ; * J191C
1909: FE 1D          CP    $1D                ;
190B: 20 0D          JR    NZ,$191A           ; 
190D: FD 7E 0C       LD    A,(IY+$0C)         ;
1910: 17             RLA                      ;
1911: 38 07          JR    C,$191A            ; 
1913: DD 7E 03       LD    A,(IX+$03)         ;
1916: FD 96 03       SUB   (IY+$03)           ;
1919: D8             RET   C                  ;
191A: FD 19          ADD   IY,DE              ; * J190B,J1911
191C: 10 E8          DJNZ  $1906              ; 
191E: DD 7E 07       LD    A,(IX+$07)         ;
1921: FD 77 07       LD    (IY+$07),A         ;
1924: DD 7E 0F       LD    A,(IX+$0F)         ;
1927: D6 04          SUB   $04                ;
1929: FD 77 0F       LD    (IY+$0F),A         ;
192C: FD 36 00 11    LD    (IY+$00),$11       ;
1930: FD 36 0D 22    LD    (IY+$0D),$22       ;
1934: FD 36 0C 0C    LD    (IY+$0C),$0C       ;
1938: DD 36 0A 43    LD    (IX+$0A),$43       ;
193C: C9             RET                      ;

ISROBJRun_11:
;
193D: 3A 00 E3       LD    A,($E300)          ;{-1_buggyHandler} 
1940: FE 06          CP    $06                ;
1942: D0             RET   NC                 ;
1943: DD 7E 04       LD    A,(IX+$04)         ;
1946: C6 DD          ADD   $DD                ;
1948: DD 77 04       LD    (IX+$04),A         ;
194B: 30 03          JR    NC,$1950           ; 
194D: DD 35 0F       DEC   (IX+$0F)           ;
1950: CD 38 08       CALL  $0838              ; * J194B
1953: CD 99 16       CALL  $1699              ; 
1956: C9             RET                      ;

ISROBJRun_12:
;
1957: CD 31 08       CALL  $0831              ; 
195A: CD 99 16       CALL  $1699              ; 
195D: C9             RET                      ;

ISROBJRun_13:
;
195E: CD 31 08       CALL  $0831              ; 
1961: DD 7E 0C       LD    A,(IX+$0C)         ;
1964: A7             AND   A                  ;
1965: C0             RET   NZ                 ;
1966: DD 7E 0D       LD    A,(IX+$0D)         ;
1969: 07             RLCA                     ;
196A: 07             RLCA                     ;
196B: E6 1C          AND   $1C                ;
196D: 21 00 2E       LD    HL,$2E00           ;
1970: 85             ADD   A,L                ;
1971: 6F             LD    L,A                ;
1972: 3A 03 E3       LD    A,($E303)          ;{-1_buggyX} 
1975: DD 96 03       SUB   (IX+$03)           ;
1978: 86             ADD   A,(HL)             ;
1979: 23             INC   HL                 ;
197A: BE             CP    (HL)               ;
197B: 30 45          JR    NC,$19C2           ; 
197D: 47             LD    B,A                ;
197E: 3A 00 E3       LD    A,($E300)          ;{-1_buggyHandler} 
1981: FE 04          CP    $04                ;
1983: C8             RET   Z                  ;
1984: 3A 04 D0       LD    A,($D004)          ;{-2_DSW2} 
1987: CB 77          BIT   6,A                ;
1989: C8             RET   Z                  ;
198A: 78             LD    A,B                ;
198B: 46             LD    B,(HL)             ;
198C: 0E 02          LD    C,$02              ;
198E: CB 38          SRL   B                  ;
1990: 50             LD    D,B                ;
1991: CB 38          SRL   B                  ;
1993: BA             CP    D                  ;
1994: 38 04          JR    C,$199A            ; 
1996: 78             LD    A,B                ;
1997: 82             ADD   A,D                ;
1998: 47             LD    B,A                ;
1999: 0D             DEC   C                  ;
199A: DD 7E 03       LD    A,(IX+$03)         ; * J1994
199D: 80             ADD   A,B                ;
199E: D6 1C          SUB   $1C                ;
19A0: 32 03 E3       LD    ($E303),A          ;{-1_buggyX} 
19A3: 79             LD    A,C                ;
19A4: 32 0D E3       LD    ($E30D),A          ; 
19A7: 3D             DEC   A                  ;
19A8: 3D             DEC   A                  ;
19A9: 32 05 E3       LD    ($E305),A          ; 
19AC: 3E 80          LD    A,$80              ;
19AE: 32 04 E3       LD    ($E304),A          ; 
19B1: 23             INC   HL                 ;
19B2: 7E             LD    A,(HL)             ;
19B3: 32 0A E3       LD    ($E30A),A          ; 
19B6: 21 00 02       LD    HL,$0200           ;
19B9: 22 08 E3       LD    ($E308),HL         ; 
19BC: 3E 06          LD    A,$06              ;
19BE: 32 00 E3       LD    ($E300),A          ;{-1_buggyHandler} 
19C1: C9             RET                      ;
19C2: 96             SUB   (HL)               ; * J197B
19C3: FE 04          CP    $04                ;
19C5: D0             RET   NC                 ;
19C6: DD 34 0C       INC   (IX+$0C)           ;
19C9: 23             INC   HL                 ;
19CA: 23             INC   HL                 ;
19CB: 7E             LD    A,(HL)             ;
19CC: 0E 01          LD    C,$01              ;
19CE: C3 C2 02       JP    $02C2              ;{NewTxtCmd} 

ISROBJRun_14:
;
19D1: DD 35 0A       DEC   (IX+$0A)           ;
19D4: F2 0D 1A       JP    P,$1A0D            ; 
19D7: DD 7E 0E       LD    A,(IX+$0E)         ;
19DA: 47             LD    B,A                ;
19DB: 3C             INC   A                  ;
19DC: 0E 07          LD    C,$07              ;
19DE: FE 06          CP    $06                ;
19E0: 38 0B          JR    C,$19ED            ; 
19E2: 3A 4E E0       LD    A,($E04E)          ;{-1_isrCNT_1} 
19E5: E6 30          AND   $30                ;
19E7: 20 02          JR    NZ,$19EB           ; 
19E9: 3E 30          LD    A,$30              ;
19EB: 4F             LD    C,A                ; * J19E7
19EC: AF             XOR   A                  ;
19ED: DD 77 0E       LD    (IX+$0E),A         ; * J19E0
19F0: DD 71 0A       LD    (IX+$0A),C         ;
19F3: 78             LD    A,B                ;
19F4: FE 04          CP    $04                ;
19F6: 38 04          JR    C,$19FC            ; 
19F8: EE 07          XOR   $07                ;
19FA: 3D             DEC   A                  ;
19FB: 47             LD    B,A                ;
19FC: C6 06          ADD   $06                ; * J19F6
19FE: DD 46 0C       LD    B,(IX+$0C)         ;
1A01: 04             INC   B                  ;
1A02: FA 08 1A       JP    M,$1A08            ; 
1A05: DD 77 0C       LD    (IX+$0C),A         ;
1A08: C6 45          ADD   $45                ; * J1A02
1A0A: DD 77 0D       LD    (IX+$0D),A         ;
1A0D: 3A 20 E3       LD    A,($E320)          ; * J19D4
1A10: FE 0F          CP    $0F                ;
1A12: 38 0E          JR    C,$1A22            ; 
1A14: C0             RET   NZ                 ;
1A15: 3A 03 E3       LD    A,($E303)          ;{-1_buggyX} 
1A18: DD 96 03       SUB   (IX+$03)           ;
1A1B: C6 10          ADD   $10                ;
1A1D: FE 30          CP    $30                ;
1A1F: DA FD 16       JP    C,$16FD            ; 
1A22: CD 38 08       CALL  $0838              ; * J1A12
1A25: DD 7E 0C       LD    A,(IX+$0C)         ;
1A28: FE 06          CP    $06                ;
1A2A: C8             RET   Z                  ;
1A2B: CD 99 16       CALL  $1699              ; 
1A2E: C9             RET                      ;

ISROBJRun_15:
;
1A2F: CD 31 08       CALL  $0831              ; 
1A32: DD 35 0A       DEC   (IX+$0A)           ;
1A35: F0             RET   P                  ;
1A36: DD 7E 0D       LD    A,(IX+$0D)         ;
1A39: FE 4A          CP    $4A                ;
1A3B: C8             RET   Z                  ;
1A3C: DD 35 0D       DEC   (IX+$0D)           ;
1A3F: DD 36 0A 07    LD    (IX+$0A),$07       ;
1A43: C9             RET                      ;

ISROBJRun_16:
;
1A44: 3A 00 E3       LD    A,($E300)          ;{-1_buggyHandler} 
1A47: FE 06          CP    $06                ;
1A49: D0             RET   NC                 ;
1A4A: DD 35 0E       DEC   (IX+$0E)           ;
1A4D: F2 66 1A       JP    P,$1A66            ; 
1A50: DD 36 0E 06    LD    (IX+$0E),$06       ;
1A54: DD 7E 0D       LD    A,(IX+$0D)         ;
1A57: 3D             DEC   A                  ;
1A58: 01 03 00       LD    BC,$0003           ;
1A5B: 21 8E 1A       LD    HL,$1A8E           ;
1A5E: ED B1          CPIR                     ;
1A60: 20 01          JR    NZ,$1A63           ; 
1A62: 7E             LD    A,(HL)             ;
1A63: DD 77 0D       LD    (IX+$0D),A         ; * J1A60
1A66: DD 7E 04       LD    A,(IX+$04)         ; * J1A4D
1A69: C6 C0          ADD   $C0                ;
1A6B: DD 77 04       LD    (IX+$04),A         ;
1A6E: 30 03          JR    NC,$1A73           ; 
1A70: DD 35 0F       DEC   (IX+$0F)           ; * J1A91
1A73: CD 38 08       CALL  $0838              ; * J1A6E
1A76: DD 7E 0C       LD    A,(IX+$0C)         ;
1A79: D6 04          SUB   $04                ;
1A7B: CB 27          SLA   A                  ;
1A7D: C6 0C          ADD   $0C                ;
1A7F: 4F             LD    C,A                ;
1A80: DD 7E 03       LD    A,(IX+$03)         ;
1A83: CD 38 15       CALL  $1538              ; 
1A86: 91             SUB   C                  ;
1A87: DD 77 07       LD    (IX+$07),A         ;
1A8A: CD 99 16       CALL  $1699              ; 
1A8D: C9             RET                      ;

1A8E: 11 15 1A 20 

ISROBJRun_17:
;
1A92: DD 36 0B 01    LD    (IX+$0B),$01       ; 
1A96: 3A 00 E3       LD    A($E300)           ;{-1_buggyHandler} 
1A99: FE 06          CP    $06                ;
1A9B: D0             RET   NC                 ;
1A9C: 2A 72 E3       LD    HL,($E372)         ; 
1A9F: 7C             LD    A,H                ;
1AA0: FE 08          CP    $08                ;
1AA2: 28 09          JR    Z,$1AAD            ; 
1AA4: 11 70 00       LD    DE,$0070           ;
1AA7: 19             ADD   HL,DE              ;
1AA8: 22 72 E3       LD    ($E372),HL         ; 
1AAB: 18 2C          JR    $1AD9              ; 
1AAD: DD 36 0A 00    LD    (IX+$0A),$00       ; * J1AA2
1AB1: DD 34 00       INC   (IX+$00)           ;
1AB4: DD 36 0E 80    LD    (IX+$0E),$80       ;
1AB8: C9             RET                      ;

ISROBJRun_18:
;
1AB9: 3A 4E E0       LD    A,($E04E)          ;{-1_isrCNT_1} 
1ABC: 1F             RRA                      ;
1ABD: D8             RET   C                  ;
1ABE: 3A 00 E3       LD    A,($E300)          ;{-1_buggyHandler} 
1AC1: FE 06          CP    $06                ;
1AC3: D0             RET   NC                 ;
1AC4: 3A 4E E0       LD    A,($E04E)          ;{-1_isrCNT_1} * J1AF3,J1B2D
1AC7: 47             LD    B,A                ;
1AC8: E6 03          AND   $03                ;
1ACA: 20 0D          JR    NZ,$1AD9           ; 
1ACC: DD 34 03       INC   (IX+$03)           ;
1ACF: CB 68          BIT   5,B                ;
1AD1: 28 06          JR    Z,$1AD9            ; 
1AD3: DD 35 03       DEC   (IX+$03)           ;
1AD6: DD 35 03       DEC   (IX+$03)           ;
1AD9: 3A 4E E0       LD    A,($E04E)          ;{-1_isrCNT_1} * J1AAB,J1ACA,J1AD1,J1B19
1ADC: E6 07          AND   $07                ;
1ADE: 20 0D          JR    NZ,$1AED           ; 
1AE0: DD 7E 03       LD    A,(IX+$03)         ;
1AE3: C6 18          ADD   $18                ;
1AE5: CD 38 15       CALL  $1538              ; 
1AE8: D6 10          SUB   $10                ;
1AEA: DD 77 07       LD    (IX+$07),A         ;
1AED: C3 B8 08       JP    $08B8              ;{DrawObject} * J1ADE

ISROBJRun_19:
;
1AF0: DD 35 0E       DEC   (IX+$0E)           ;
1AF3: 20 CF          JR    NZ,$1AC4           ; 
1AF5: DD 36 0A 58    LD    (IX+$0A),$58       ;
1AF9: DD 34 00       INC   (IX+$00)           ;
1AFC: DD 36 0D 52    LD    (IX+$0D),$52       ;
1B00: C9             RET                      ;

ISROBJRun_1A:
;
1B01: DD 35 0A       DEC   (IX+$0A)           ;
1B04: 28 15          JR    Z,$1B1B            ; 
1B06: 2A 72 E3       LD    HL,($E372)         ; 
1B09: 11 80 01       LD    DE,$0180           ;
1B0C: 19             ADD   HL,DE              ;
1B0D: 22 72 E3       LD    ($E372),HL         ; 
1B10: 7C             LD    A,H                ;
1B11: FE F0          CP    $F0                ;
1B13: D2 52 08       JP    NC,$0852           ; 
1B16: CD 99 16       CALL  $1699              ; 
1B19: 18 BE          JR    $1AD9              ; 
1B1B: DD 34 00       INC   (IX+$00)           ; * J1B04
1B1E: DD 36 0A 6E    LD    (IX+$0A),$6E       ;
1B22: DD 36 0D 23    LD    (IX+$0D),$23       ;
1B26: C9             RET                      ;

ISROBJRun_1B:
;
1B27: CD 99 16       CALL  $1699              ; 
1B2A: DD 35 0A       DEC   (IX+$0A)           ;
1B2D: 20 95          JR    NZ,$1AC4           ; 
1B2F: DD 35 00       DEC   (IX+$00)           ;
1B32: DD 35 0B       DEC   (IX+$0B)           ;
1B35: DD 36 0D 52    LD    (IX+$0D),$52       ;
1B39: C9             RET                      ;
1B3A: 21 EE E0       LD    HL,$E0EE           ; * C0274
1B3D: 3A 4E E0       LD    A,($E04E)          ;{-1_isrCNT_1} 
1B40: 96             SUB   (HL)               ;
1B41: F8             RET   M                  ;
1B42: 01 00 10       LD    BC,$1000           ;
1B45: ED 5F          LD    A,R                ;
1B47: E6 F0          AND   $F0                ;
1B49: 26 E4          LD    H,$E4              ;
1B4B: 51             LD    D,C                ;
1B4C: 59             LD    E,C                ;
1B4D: 6F             LD    L,A                ; * J1B62
1B4E: 7E             LD    A,(HL)             ;
1B4F: D6 1E          SUB   $1E                ;
1B51: FE 0A          CP    $0A                ;
1B53: 30 0A          JR    NC,$1B5F           ; 
1B55: CB 4F          BIT   1,A                ;
1B57: 20 06          JR    NZ,$1B5F           ; 
1B59: FE 04          CP    $04                ;
1B5B: 38 63          JR    C,$1BC0            ; 
1B5D: 0C             INC   C                  ;
1B5E: 5D             LD    E,L                ;
1B5F: 7D             LD    A,L                ; * J1B53,J1B57,J1BC2
1B60: C6 10          ADD   $10                ;
1B62: 10 E9          DJNZ  $1B4D              ; 
1B64: ED 53 D4 E1    LD    ($E1D4),DE         ; 
1B68: 0D             DEC   C                  ;
1B69: F8             RET   M                  ;
1B6A: 3A 10 E5       LD    A,($E510)          ; Course number
1B6D: E6 03          AND   $03                ;
1B6F: FE 01          CP    $01                ;
1B71: 89             ADC   A,C                ;
1B72: 4F             LD    C,A                ;
1B73: FE 09          CP    $09                ;
1B75: DA 7A 1B       JP    C,$1B7A            ; 
1B78: 0E 08          LD    C,$08              ;
1B7A: 21 FF 2F       LD    HL,$2FFF           ; * J1B75
1B7D: 09             ADD   HL,BC              ;
1B7E: 4E             LD    C,(HL)             ;
1B7F: 06 05          LD    B,$05              ;
1B81: 21 70 E3       LD    HL,$E370           ;
1B84: 11 00 00       LD    DE,$0000           ;
1B87: 7E             LD    A,(HL)             ; * J1B94
1B88: A7             AND   A                  ;
1B89: 28 39          JR    Z,$1BC4            ; 
1B8B: D6 2F          SUB   $2F                ;
1B8D: 20 01          JR    NZ,$1B90           ; 
1B8F: 14             INC   D                  ;
1B90: 7D             LD    A,L                ; * J1B8D,J1BC5
1B91: C6 10          ADD   $10                ;
1B93: 6F             LD    L,A                ;
1B94: 10 F1          DJNZ  $1B87              ; 
1B96: 7A             LD    A,D                ;
1B97: B9             CP    C                  ;
1B98: D0             RET   NC                 ;
1B99: 1C             INC   E                  ;
1B9A: 1D             DEC   E                  ;
1B9B: C8             RET   Z                  ;
1B9C: ED 5F          LD    A,R                ;
1B9E: E6 0F          AND   $0F                ;
1BA0: C6 19          ADD   $19                ;
1BA2: 21 4E E0       LD    HL,$E04E           ;
1BA5: 86             ADD   A,(HL)             ;
1BA6: 32 EE E0       LD    ($E0EE),A          ; 
1BA9: 16 00          LD    D,$00              ;
1BAB: DD 21 00 E3    LD    IX,$E300           ;
1BAF: DD 19          ADD   IX,DE              ;
1BB1: 21 D4 E1       LD    HL,$E1D4           ;
1BB4: 5E             LD    E,(HL)             ;
1BB5: FD 21 00 E4    LD    IY,$E400           ;
1BB9: FD 19          ADD   IY,DE              ;
1BBB: 0E 3B          LD    C,$3B              ;
1BBD: C3 64 10       JP    $1064              ; 
1BC0: 55             LD    D,L                ; * J1B5B
1BC1: 14             INC   D                  ;
1BC2: 18 9B          JR    $1B5F              ; 
1BC4: 5D             LD    E,L                ; * J1B89
1BC5: 18 C9          JR    $1B90              ; 
1BC7: 3A 4E E0       LD    A,($E04E)          ;{-1_isrCNT_1} * C0277
1BCA: 21 52 E0       LD    HL,$E052           ;
1BCD: AE             XOR   (HL)               ;
1BCE: E6 1F          AND   $1F                ;
1BD0: C0             RET   NZ                 ;
1BD1: ED 5F          LD    A,R                ;
1BD3: 77             LD    (HL),A             ;
1BD4: 21 C6 E1       LD    HL,$E1C6           ;
1BD7: 06 03          LD    B,$03              ;
1BD9: 7E             LD    A,(HL)             ; * J1BDE
1BDA: A7             AND   A                  ;
1BDB: 20 04          JR    NZ,$1BE1           ; 
1BDD: 23             INC   HL                 ;
1BDE: 10 F9          DJNZ  $1BD9              ; 
1BE0: C9             RET                      ;
1BE1: DD 21 00 E4    LD    IX,$E400           ; * J1BDB
1BE5: 04             INC   B                  ;
1BE6: 78             LD    A,B                ;
1BE7: 48             LD    C,B                ;
1BE8: 06 10          LD    B,$10              ;
1BEA: FE 04          CP    $04                ;
1BEC: 28 0F          JR    Z,$1BFD            ; 
1BEE: 3A D6 E1       LD    A,($E1D6)          ; 
1BF1: 3D             DEC   A                  ;
1BF2: FA FD 1B       JP    M,$1BFD            ; 
1BF5: 0D             DEC   C                  ;
1BF6: 0D             DEC   C                  ;
1BF7: DD 21 70 E3    LD    IX,$E370           ;
1BFB: 06 05          LD    B,$05              ;
1BFD: 11 10 00       LD    DE,$0010           ; * J1BEC,J1BF2
1C00: DD 7E 00       LD    A,(IX+$00)         ; * J1C08
1C03: A7             AND   A                  ;
1C04: 28 05          JR    Z,$1C0B            ; 
1C06: DD 19          ADD   IX,DE              ;
1C08: 10 F6          DJNZ  $1C00              ; 
1C0A: C9             RET                      ;
1C0B: 35             DEC   (HL)               ; * J1C04
1C0C: 79             LD    A,C                ;
1C0D: FE 02          CP    $02                ;
1C0F: 30 43          JR    NC,$1C54           ; 
1C11: ED 5F          LD    A,R                ;
1C13: E6 1F          AND   $1F                ;
1C15: C6 20          ADD   $20                ;
1C17: DD 77 0F       LD    (IX+$0F),A         ;
1C1A: 21 D6 E1       LD    HL,$E1D6           ;
1C1D: 35             DEC   (HL)               ;
1C1E: ED 5F          LD    A,R                ; * J1C57
1C20: E6 1E          AND   $1E                ;
1C22: 5F             LD    E,A                ;
1C23: 16 00          LD    D,$00              ;
1C25: FE 0E          CP    $0E                ;
1C27: 3E 82          LD    A,$82              ;
1C29: 38 04          JR    C,$1C2F            ; 
1C2B: ED 5F          LD    A,R                ;
1C2D: E6 80          AND   $80                ;
1C2F: DD 77 0C       LD    (IX+$0C),A         ; * J1C29
1C32: 21 08 30       LD    HL,$3008           ;
1C35: 19             ADD   HL,DE              ;
1C36: 7E             LD    A,(HL)             ;
1C37: DD 77 07       LD    (IX+$07),A         ;
1C3A: 23             INC   HL                 ;
1C3B: 7E             LD    A,(HL)             ;
1C3C: DD 77 03       LD    (IX+$03),A         ;
1C3F: 06 00          LD    B,$00              ;
1C41: 21 59 1C       LD    HL,$1C59           ;
1C44: 09             ADD   HL,BC              ;
1C45: 09             ADD   HL,BC              ;
1C46: 7E             LD    A,(HL)             ;
1C47: DD 77 0D       LD    (IX+$0D),A         ;
1C4A: DD 36 0E 00    LD    (IX+$0E),$00       ;
1C4E: 23             INC   HL                 ;
1C4F: 7E             LD    A,(HL)             ;
1C50: DD 77 00       LD    (IX+$00),A         ;
1C53: C9             RET                      ;
1C54: CD 0A 08       CALL  $080A              ; * J1C0F
1C57: 18 C5          JR    $1C1E              ; 
1C59: 2B             DEC   HL                 ;
1C5A: 26 2A          LD    H,$2A              ;
1C5C: 26 2B          LD    H,$2B              ;
1C5E: 22 2A 22       LD    ($222A),HL         ; 
1C61: 31 1E DD       LD    SP,$DD1E           ;
1C64: 7E             LD    A,(HL)             ;
1C65: 0D             DEC   C                  ;
1C66: FE 2B          CP    $2B                ;
1C68: D8             RET   C                  ;
1C69: DD CB 0E 7E    BIT   7,(IX+$0E)         ;
1C6D: 20 18          JR    NZ,$1C87           ; 
1C6F: DD 35 0E       DEC   (IX+$0E)           ;
1C72: F0             RET   P                  ;
1C73: DD 34 0D       INC   (IX+$0D)           ;
1C76: FE 2F          CP    $2F                ;
1C78: 28 1C          JR    Z,$1C96            ; 
1C7A: FE 34          CP    $34                ;
1C7C: 20 04          JR    NZ,$1C82           ; 
1C7E: DD 36 0D 31    LD    (IX+$0D),$31       ;
1C82: DD 36 0E 08    LD    (IX+$0E),$08       ; * J1C7C,J1C90,J1C94
1C86: C9             RET                      ;
1C87: DD 34 0E       INC   (IX+$0E)           ; * J1C6D
1C8A: F8             RET   M                  ;
1C8B: DD 35 0D       DEC   (IX+$0D)           ;
1C8E: FE 2C          CP    $2C                ;
1C90: 28 F0          JR    Z,$1C82            ; 
1C92: FE 32          CP    $32                ;
1C94: 28 EC          JR    Z,$1C82            ; 
1C96: DD 36 0E F8    LD    (IX+$0E),$F8       ; * J1C78
1C9A: C9             RET                      ;

ISROBJRun_2E:
;
1C9B: DD 6E 04       LD    L,(IX+$04)         ;
1C9E: DD 66 05       LD    H,(IX+$05)         ;
1CA1: CB 3C          SRL   H                  ;
1CA3: CB 1D          RR    L                  ;
1CA5: DD CB 0C 46    BIT   0,(IX+$0C)         ;
1CA9: 28 07          JR    Z,$1CB2            ; 
1CAB: EB             EX    DE,HL              ;
1CAC: 21 00 00       LD    HL,$0000           ;
1CAF: A7             AND   A                  ;
1CB0: ED 52          SBC   HL,DE              ;
1CB2: DD 75 04       LD    (IX+$04),L         ; * J1CA9
1CB5: DD 74 05       LD    (IX+$05),H         ;
1CB8: DD 34 00       INC   (IX+$00)           ;
1CBB: C9             RET                      ;

ISROBJRun_2F:
;
1CBC: 0E 3D          LD    C,$3D              ;
1CBE: DD 7E 09       LD    A,(IX+$09)         ;
1CC1: A7             AND   A                  ;
1CC2: 20 13          JR    NZ,$1CD7           ; 
1CC4: 0E 3B          LD    C,$3B              ;
1CC6: DD 46 05       LD    B,(IX+$05)         ;
1CC9: CB 10          RL    B                  ;
1CCB: 30 02          JR    NC,$1CCF           ; 
1CCD: 0E 50          LD    C,$50              ;
1CCF: DD 7E 08       LD    A,(IX+$08)         ; * J1CCB
1CD2: FE 60          CP    $60                ;
1CD4: 38 01          JR    C,$1CD7            ; 
1CD6: 0C             INC   C                  ;
1CD7: DD 71 0D       LD    (IX+$0D),C         ; * J1CC2,J1CD4
1CDA: CD FB 20       CALL  $20FB              ; 
1CDD: 7C             LD    A,H                ;
1CDE: FE 06          CP    $06                ;
1CE0: DA 52 08       JP    C,$0852            ; 
1CE3: 01 05 00       LD    BC,$0005           ;
1CE6: 22 D6 E0       LD    ($E0D6),HL         ; * J1D38
1CE9: 7C             LD    A,H                ;
1CEA: 2A DC E0       LD    HL,($E0DC)         ; 
1CED: 09             ADD   HL,BC              ;
1CEE: 22 DC E0       LD    ($E0DC),HL         ; 
1CF1: ED 5B DA E0    LD    DE,($E0DA)         ; * J20A9
1CF5: 19             ADD   HL,DE              ;
1CF6: 22 DA E0       LD    ($E0DA),HL         ; 
1CF9: 54             LD    D,H                ;
1CFA: CD 38 15       CALL  $1538              ; 
1CFD: D6 08          SUB   $08                ;
1CFF: BA             CP    D                  ;
1D00: CD EF 20       CALL  $20EF              ; 
1D03: 30 35          JR    NC,$1D3A           ; 
1D05: DD 77 07       LD    (IX+$07),A         ;
1D08: DD 34 00       INC   (IX+$00)           ;
1D0B: DD 36 0B 00    LD    (IX+$0B),$00       ;
1D0F: DD 7E 00       LD    A,(IX+$00)         ;
1D12: FE 2A          CP    $2A                ;
1D14: 3E 03          LD    A,$03              ; Sound effect 3 ... ?? played right after sound effect 2
1D16: 20 05          JR    NZ,$1D1D           ; 
1D18: DD 36 00 30    LD    (IX+$00),$30       ;
1D1C: 3D             DEC   A                  ; Sound effect 2 ... missile hitting ground
1D1D: CD 75 0D       CALL  $0D75              ;{AddSound} Play missile hitting ground or effect played after that * J1D16
1D20: C3 56 08       JP    $0856              ; 

ISROBJRun_2A:
;
1D23: CD DB 20       CALL  $20DB              ; 
1D26: ED 5B 14 E3    LD    DE,($E314)         ; 
1D2A: CB 2A          SRA   D                  ;
1D2C: CB 1B          RR    E                  ;
1D2E: ED 52          SBC   HL,DE              ;
1D30: 11 8E 00       LD    DE,$008E           ;
1D33: ED 52          SBC   HL,DE              ;
1D35: 01 10 00       LD    BC,$0010           ;
1D38: 18 AC          JR    $1CE6              ; 
1D3A: 3A 00 E3       LD    A,($E300)          ;{-1_buggyHandler} * J1D03
1D3D: FE 06          CP    $06                ;
1D3F: D2 B8 08       JP    NC,$08B8           ;{DrawObject} 
1D42: 21 05 06       LD    HL,$0605           ;
1D45: DD 7E 00       LD    A,(IX+$00)         ;
1D48: FE 2A          CP    $2A                ;
1D4A: 30 03          JR    NC,$1D4F           ; 
1D4C: 21 0B 02       LD    HL,$020B           ; * J1F7B
1D4F: FD 21 30 E3    LD    IY,$E330           ; Start of player air-shots (4 of them, 16 bytes each) * J1D4A
1D53: 11 10 00       LD    DE,$0010           ; Each structure is 16 bytes
1D56: 06 04          LD    B,$04              ; There are 4 structures
;
1D58: FD 7E 00       LD    A,(IY+$00)         ; * J1D75
1D5B: FE 0F          CP    $0F                ;
1D5D: 20 14          JR    NZ,$1D73           ; Not a shot ... move on
1D5F: FD 7E 07       LD    A,(IY+$07)         ;
1D62: DD 96 07       SUB   (IX+$07)           ;
1D65: FE 0A          CP    $0A                ;
1D67: 30 0A          JR    NC,$1D73           ; 
1D69: FD 7E 03       LD    A,(IY+$03)         ;
1D6C: DD 96 03       SUB   (IX+$03)           ;
1D6F: 94             SUB   H                  ;
1D70: BD             CP    L                  ;
1D71: 38 2B          JR    C,$1D9E            ; 
1D73: FD 19          ADD   IY,DE              ; Bump to next structure * J1D5D,J1D67
1D75: 10 E1          DJNZ  $1D58              ; Do all structures
;
1D77: 3A 07 E3       LD    A,($E307)          ;{-1_buggyY} 
1D7A: DD 96 07       SUB   (IX+$07)           ;
1D7D: FE F0          CP    $F0                ;
1D7F: DA B8 08       JP    C,$08B8            ;{DrawObject} 
1D82: 57             LD    D,A                ;
1D83: 3A 03 E3       LD    A,($E303)          ;{-1_buggyX} 
1D86: DD 96 03       SUB   (IX+$03)           ;
1D89: D6 04          SUB   $04                ;
1D8B: FE EA          CP    $EA                ;
1D8D: DA B8 08       JP    C,$08B8            ;{DrawObject} 
1D90: 3A 04 D0       LD    A,($D004)          ;{-2_DSW2} 
1D93: CB 77          BIT   6,A                ;
1D95: CA B8 08       JP    Z,$08B8            ;{DrawObject} 
1D98: CD 52 08       CALL  $0852              ; 
1D9B: C3 FD 16       JP    $16FD              ; 


1D9E: FD 34 00       INC   (IY+$00)           ; ?? From E (initial) to F (moved above) * J1D71
1DA1: DD 7E 0D       LD    A,(IX+$0D)         ;
1DA4: FE 37          CP    $37                ;
1DA6: 38 11          JR    C,$1DB9            ; 
1DA8: DD 36 0C 00    LD    (IX+$0C),$00       ;
1DAC: DD 36 00 2D    LD    (IX+$00),$2D       ;
1DB0: DD 36 0A 0A    LD    (IX+$0A),$0A       ;
1DB4: DD 36 0D 4F    LD    (IX+$0D),$4F       ;
1DB8: C9             RET                      ;

; Collision detection ??
1DB9: 21 C9 E1       LD    HL,$E1C9           ; * J1DA6
1DBC: 01 01 05       LD    BC,$0501           ;
1DBF: FE 31          CP    $31                ;
1DC1: 30 07          JR    NC,$1DCA           ; 
1DC3: 23             INC   HL                 ;
1DC4: 05             DEC   B                  ;
1DC5: FE 2A          CP    $2A                ;
1DC7: 28 01          JR    Z,$1DCA            ; 
1DC9: 23             INC   HL                 ;
1DCA: 3E 11          LD    A,$11              ; Play ... * J1DC1,J1DC7
1DCC: CD 75 0D       CALL  $0D75              ;{AddSound} ... UFO explosion
1DCF: 35             DEC   (HL)               ;
1DD0: 20 08          JR    NZ,$1DDA           ; 
1DD2: 23             INC   HL                 ;
1DD3: 23             INC   HL                 ;
1DD4: 23             INC   HL                 ;
1DD5: 7E             LD    A,(HL)             ;
1DD6: FE 03          CP    $03                ;
1DD8: 30 11          JR    NC,$1DEB           ; 
1DDA: DD 36 00 20    LD    (IX+$00),$20       ; * J1DD0
1DDE: DD 36 0A 06    LD    (IX+$0A),$06       ;
1DE2: DD 36 0D 37    LD    (IX+$0D),$37       ;
1DE6: 78             LD    A,B                ;
1DE7: CD C2 02       CALL  $02C2              ;{NewTxtCmd} 
1DEA: C9             RET                      ;
;
1DEB: 21 00 FC       LD    HL,$FC00           ; * J1DD8
1DEE: D6 02          SUB   $02                ;
1DF0: C3 9D 17       JP    $179D              ; 

ISROBJRun_2B:
;
1DF3: DD 36 0D 3E    LD    (IX+$0D),$3E       ;
1DF7: CD 23 16       CALL  $1623              ; 
1DFA: D6 03          SUB   $03                ;
1DFC: E6 F8          AND   $F8                ;
1DFE: C6 06          ADD   $06                ;
1E00: DD 77 0F       LD    (IX+$0F),A         ;
1E03: 21 D1 E1       LD    HL,$E1D1           ; * J1E1B
1E06: 7E             LD    A,(HL)             ;
1E07: A7             AND   A                  ;
1E08: 28 13          JR    Z,$1E1D            ; 
1E0A: 23             INC   HL                 ;
1E0B: 36 01          LD    (HL),$01           ;
1E0D: 23             INC   HL                 ;
1E0E: 7E             LD    A,(HL)             ;
1E0F: A7             AND   A                  ;
1E10: C8             RET   Z                  ;
1E11: C3 52 08       JP    $0852              ; 

ISROBJRun_30:
;
1E14: DD 36 0D 43    LD    (IX+$0D),$43       ;
1E18: CD 23 16       CALL  $1623              ; 
1E1B: 18 E6          JR    $1E03              ; 
1E1D: 34             INC   (HL)               ; * J1E08
1E1E: DD 34 00       INC   (IX+$00)           ;
1E21: DD 36 0A 04    LD    (IX+$0A),$04       ;
1E25: CD 31 08       CALL  $0831              ; * J1E3E,J1E4F,J1E5B,J1E81
1E28: C9             RET                      ;

ISROBJRun_31:
;
1E29: 21 D2 E1       LD    HL,$E1D2           ;
1E2C: 7E             LD    A,(HL)             ;
1E2D: 23             INC   HL                 ;
1E2E: B6             OR    (HL)               ;
1E2F: A7             AND   A                  ;
1E30: C2 52 08       JP    NZ,$0852           ; 
1E33: DD 7E 03       LD    A,(IX+$03)         ;
1E36: FE F8          CP    $F8                ;
1E38: D2 52 08       JP    NC,$0852           ; 
1E3B: DD 35 0A       DEC   (IX+$0A)           ;
1E3E: 20 E5          JR    NZ,$1E25           ; 
1E40: DD 7E 0D       LD    A,(IX+$0D)         ;
1E43: FE 49          CP    $49                ;
1E45: CA 52 08       JP    Z,$0852            ; 
1E48: DD 34 0D       INC   (IX+$0D)           ;
1E4B: DD 36 0A 05    LD    (IX+$0A),$05       ;
1E4F: 18 D4          JR    $1E25              ; 

ISROBJRun_2C:
;
1E51: 3A D3 E1       LD    A,($E1D3)          ; 
1E54: A7             AND   A                  ;
1E55: C2 52 08       JP    NZ,$0852           ; 
1E58: DD 35 0A       DEC   (IX+$0A)           ;
1E5B: 20 C8          JR    NZ,$1E25           ; 
1E5D: DD 7E 0D       LD    A,(IX+$0D)         ;
1E60: FE 42          CP    $42                ;
1E62: 30 1F          JR    NC,$1E83           ; 
1E64: DD 34 0D       INC   (IX+$0D)           ;
1E67: FE 3F          CP    $3F                ;
1E69: 20 12          JR    NZ,$1E7D           ; 
1E6B: DD 7E 0F       LD    A,(IX+$0F)         ;
1E6E: 1F             RRA                      ;
1E6F: 1F             RRA                      ;
1E70: 1F             RRA                      ;
1E71: E6 1F          AND   $1F                ;
1E73: 5F             LD    E,A                ;
1E74: 16 83          LD    D,$83              ;
1E76: 0E 09          LD    C,$09              ;
1E78: 3E 01          LD    A,$01              ;
1E7A: CD C2 02       CALL  $02C2              ;{NewTxtCmd} 
1E7D: DD 36 0A 02    LD    (IX+$0A),$02       ; * J1E69
1E81: 18 A2          JR    $1E25              ; 
1E83: DD 7E 07       LD    A,(IX+$07)         ; * J1E62
1E86: C6 08          ADD   $08                ;
1E88: DD 77 07       LD    (IX+$07),A         ;
1E8B: CD 56 08       CALL  $0856              ; 
1E8E: DD 36 0C 00    LD    (IX+$0C),$00       ;
1E92: DD 36 0D 81    LD    (IX+$0D),$81       ;
1E96: DD 36 00 13    LD    (IX+$00),$13       ;
1E9A: C9             RET                      ;

ISROBJRun_2D:
;
1E9B: DD 35 0A       DEC   (IX+$0A)           ;
1E9E: CA 52 08       JP    Z,$0852            ; 
1EA1: C3 B8 08       JP    $08B8              ;{DrawObject} 

ISROBJRun_26:
;
1EA4: DD 35 0F       DEC   (IX+$0F)           ;
1EA7: CA 4D 20       JP    Z,$204D            ;{ISROBJRun_28} 

ISROBJRun_1E:
ISROBJRun_22:
;
1EAA: DD 34 00       INC   (IX+$00)           ; * J2016
1EAD: DD 7E 0C       LD    A,(IX+$0C)         ;
1EB0: CB 27          SLA   A                  ;
1EB2: 28 3D          JR    Z,$1EF1            ; 
1EB4: 3F             CCF                      ;
1EB5: 1F             RRA                      ;
1EB6: E6 80          AND   $80                ;
1EB8: DD 77 0C       LD    (IX+$0C),A         ;
1EBB: 4F             LD    C,A                ;
1EBC: ED 5F          LD    A,R                ;
1EBE: E6 3F          AND   $3F                ;
1EC0: 5F             LD    E,A                ;
1EC1: 16 00          LD    D,$00              ;
1EC3: 21 26 01       LD    HL,$0126           ;
1EC6: 19             ADD   HL,DE              ;
1EC7: 0C             INC   C                  ;
1EC8: F2 D2 1E       JP    P,$1ED2            ; 
1ECB: EB             EX    DE,HL              ;
1ECC: A7             AND   A                  ;
1ECD: 21 00 00       LD    HL,$0000           ;
1ED0: ED 52          SBC   HL,DE              ;
1ED2: DD 74 05       LD    (IX+$05),H         ; * J1EC8
1ED5: DD 75 04       LD    (IX+$04),L         ;
1ED8: EE 3F          XOR   $3F                ;
1EDA: D6 20          SUB   $20                ;
1EDC: 87             ADD   A,A                ;
1EDD: DD 77 08       LD    (IX+$08),A         ;
1EE0: 3E 00          LD    A,$00              ;
1EE2: DE 00          SBC   $00                ;
1EE4: DD 77 09       LD    (IX+$09),A         ;
1EE7: ED 5F          LD    A,R                ;
1EE9: E6 7F          AND   $7F                ;
1EEB: C6 20          ADD   $20                ;
1EED: DD 77 0A       LD    (IX+$0A),A         ;
1EF0: C9             RET                      ;
1EF1: 06 01          LD    B,$01              ; * J1EB2
1EF3: DD 7E 07       LD    A,(IX+$07)         ;
1EF6: FE 44          CP    $44                ;
1EF8: 38 0C          JR    C,$1F06            ; 
1EFA: 06 03          LD    B,$03              ;
1EFC: FE 58          CP    $58                ;
1EFE: 30 06          JR    NC,$1F06           ; 
1F00: ED 5F          LD    A,R                ;
1F02: E6 02          AND   $02                ;
1F04: 3C             INC   A                  ;
1F05: 47             LD    B,A                ;
1F06: 78             LD    A,B                ; * J1EF8,J1EFE
1F07: DD 86 0C       ADD   A,(IX+$0C)         ;
1F0A: DD 77 0C       LD    (IX+$0C),A         ;
1F0D: ED 5F          LD    A,R                ;
1F0F: E6 0F          AND   $0F                ;
1F11: C6 24          ADD   $24                ;
1F13: DD 77 0B       LD    (IX+$0B),A         ;
1F16: 21 66 01       LD    HL,$0166           ;
1F19: DD 75 04       LD    (IX+$04),L         ;
1F1C: DD 74 05       LD    (IX+$05),H         ;
1F1F: DD 36 08 00    LD    (IX+$08),$00       ;
1F23: DD 36 09 00    LD    (IX+$09),$00       ;
1F27: C9             RET                      ;

ISROBJRun_1F:
ISROBJRun_23:
ISROBJRun_27:
;
1F28: CD 63 1C       CALL  $1C63              ; * C2009
1F2B: CD DB 20       CALL  $20DB              ; 
1F2E: DD 7E 0C       LD    A,(IX+$0C)         ;
1F31: CB 27          SLA   A                  ;
1F33: 20 52          JR    NZ,$1F87           ; 
1F35: DD 35 0A       DEC   (IX+$0A)           ;
1F38: 28 49          JR    Z,$1F83            ; 
1F3A: 2A D6 E0       LD    HL,($E0D6)         ; 
1F3D: ED 5B D8 E0    LD    DE,($E0D8)         ; 
1F41: 19             ADD   HL,DE              ;
1F42: 7A             LD    A,D                ;
1F43: ED 5B 04 E3    LD    DE,($E304)         ; 
1F47: ED 52          SBC   HL,DE              ;
1F49: 22 D6 E0       LD    ($E0D6),HL         ; 
1F4C: 17             RLA                      ;
1F4D: 38 2F          JR    C,$1F7E            ; 
1F4F: DD 7E 0D       LD    A,(IX+$0D)         ;
1F52: 06 A0          LD    B,$A0              ;
1F54: D6 2A          SUB   $2A                ;
1F56: 28 08          JR    Z,$1F60            ; 
1F58: 06 80          LD    B,$80              ;
1F5A: D6 07          SUB   $07                ;
1F5C: 38 02          JR    C,$1F60            ; 
1F5E: 06 D0          LD    B,$D0              ;
1F60: 7C             LD    A,H                ; * J1F56,J1F5C
1F61: B8             CP    B                  ;
1F62: 30 1F          JR    NC,$1F83           ; 
1F64: 2A DA E0       LD    HL,($E0DA)         ; * J1F81
1F67: ED 5B DC E0    LD    DE,($E0DC)         ; 
1F6B: 19             ADD   HL,DE              ;
1F6C: 22 DA E0       LD    ($E0DA),HL         ; 
1F6F: 7C             LD    A,H                ;
1F70: FE 38          CP    $38                ;
1F72: 38 0F          JR    C,$1F83            ; 
1F74: FE 70          CP    $70                ;
1F76: 30 0B          JR    NC,$1F83           ; 
1F78: CD EF 20       CALL  $20EF              ; * J1FE8,J203E,J204A
1F7B: C3 4C 1D       JP    $1D4C              ; 
1F7E: 7C             LD    A,H                ; * J1F4D
1F7F: FE 16          CP    $16                ;
1F81: 30 E1          JR    NC,$1F64           ; 
1F83: DD 35 00       DEC   (IX+$00)           ; * J1F38,J1F62,J1F72,J1F76,J1FD4,J2011
1F86: C9             RET                      ;
1F87: 2A D8 E0       LD    HL,($E0D8)         ; * J1F33
1F8A: DD 5E 0B       LD    E,(IX+$0B)         ;
1F8D: 16 00          LD    D,$00              ;
1F8F: A7             AND   A                  ;
1F90: ED 52          SBC   HL,DE              ;
1F92: 22 D8 E0       LD    ($E0D8),HL         ; 
1F95: 30 16          JR    NC,$1FAD           ; 
1F97: DD 7E 03       LD    A,(IX+$03)         ;
1F9A: D6 30          SUB   $30                ;
1F9C: FE 40          CP    $40                ;
1F9E: 3E 00          LD    A,$00              ;
1FA0: 30 04          JR    NC,$1FA6           ; 
1FA2: ED 5F          LD    A,R                ;
1FA4: E6 80          AND   $80                ;
1FA6: DD 86 0C       ADD   A,(IX+$0C)         ; * J1FA0
1FA9: 3C             INC   A                  ;
1FAA: DD 77 0C       LD    (IX+$0C),A         ;
1FAD: EB             EX    DE,HL              ; * J1F95
1FAE: 2A D6 E0       LD    HL,($E0D6)         ; 
1FB1: ED 52          SBC   HL,DE              ;
1FB3: DD 7E 0C       LD    A,(IX+$0C)         ;
1FB6: 07             RLCA                     ;
1FB7: 38 02          JR    C,$1FBB            ; 
1FB9: 19             ADD   HL,DE              ;
1FBA: 19             ADD   HL,DE              ;
1FBB: ED 5B 04 E3    LD    DE,($E304)         ; * J1FB7
1FBF: ED 52          SBC   HL,DE              ;
1FC1: 22 D6 E0       LD    ($E0D6),HL         ; 
1FC4: 2A DC E0       LD    HL,($E0DC)         ; 
1FC7: DD 5E 0B       LD    E,(IX+$0B)         ;
1FCA: 16 00          LD    D,$00              ;
1FCC: 0F             RRCA                     ;
1FCD: 3D             DEC   A                  ;
1FCE: 0F             RRCA                     ;
1FCF: 30 1A          JR    NC,$1FEB           ; 
1FD1: A7             AND   A                  ;
1FD2: ED 52          SBC   HL,DE              ;
1FD4: 38 AD          JR    C,$1F83            ; 
1FD6: 22 DC E0       LD    ($E0DC),HL         ; * J1FEC
1FD9: EB             EX    DE,HL              ;
1FDA: 2A DA E0       LD    HL,($E0DA)         ; 
1FDD: A7             AND   A                  ;
1FDE: ED 52          SBC   HL,DE              ;
1FE0: 0F             RRCA                     ;
1FE1: 38 02          JR    C,$1FE5            ; 
1FE3: 19             ADD   HL,DE              ;
1FE4: 19             ADD   HL,DE              ;
1FE5: 22 DA E0       LD    ($E0DA),HL         ; * J1FE1
1FE8: C3 78 1F       JP    $1F78              ; 
1FEB: 19             ADD   HL,DE              ; * J1FCF
1FEC: 18 E8          JR    $1FD6              ; 



1FEE: 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00


; Padded to make 2000 special

ISROBJRun_24:
;
2000: DD 34 00       INC   (IX+$00)           ;
2003: DD 7E 0C       LD    A,(IX+$0C)         ;
2006: E6 7F          AND   $7F                ;
2008: C8             RET   Z                  ;
2009: CD 28 1F       CALL  $1F28              ;{ISROBJRun_1F} 
200C: DD 7E 00       LD    A,(IX+$00)         ;
200F: FE 25          CP    $25                ;
2011: CA 83 1F       JP    Z,$1F83            ; 
2014: FE 24          CP    $24                ;
2016: CA AA 1E       JP    Z,$1EAA            ;{ISROBJRun_1E} 
2019: C9             RET                      ;

ISROBJRun_25:
;
201A: CD 63 1C       CALL  $1C63              ; 
201D: CD DB 20       CALL  $20DB              ; 
2020: 22 D6 E0       LD    ($E0D6),HL         ; 
2023: 7C             LD    A,H                ;
2024: D6 08          SUB   $08                ;
2026: FE F0          CP    $F0                ;
2028: D2 52 08       JP    NC,$0852           ; 
202B: ED 5B DC E0    LD    DE,($E0DC)         ; 
202F: 2A DA E0       LD    HL,($E0DA)         ; 
2032: 19             ADD   HL,DE              ;
2033: 22 DA E0       LD    ($E0DA),HL         ; 
2036: 7C             LD    A,H                ;
2037: FE 30          CP    $30                ;
2039: DA 52 08       JP    C,$0852            ; 
203C: 7A             LD    A,D                ;
203D: A7             AND   A                  ;
203E: FA 78 1F       JP    M,$1F78            ; 
2041: 21 00 00       LD    HL,$0000           ;
2044: A7             AND   A                  ;
2045: ED 52          SBC   HL,DE              ;
2047: 22 DC E0       LD    ($E0DC),HL         ; 
204A: C3 78 1F       JP    $1F78              ; 

ISROBJRun_28:
;
204D: 3A 03 E3       LD    A,($E303)          ;{-1_buggyX} * J1EA7
2050: 16 00          LD    D,$00              ;
2052: C6 10          ADD   $10                ;
2054: DD 96 03       SUB   (IX+$03)           ;
2057: 30 03          JR    NC,$205C           ; 
2059: ED 44          NEG                      ;
205B: 15             DEC   D                  ;
205C: 1F             RRA                      ; * J2057
205D: 1F             RRA                      ;
205E: 1F             RRA                      ;
205F: E6 1E          AND   $1E                ;
2061: 4F             LD    C,A                ;
2062: 06 00          LD    B,$00              ;
2064: 21 24 2D       LD    HL,$2D24           ;
2067: 09             ADD   HL,BC              ;
2068: FE 12          CP    $12                ;
206A: 38 01          JR    C,$206D            ; 
206C: 04             INC   B                  ;
206D: 7E             LD    A,(HL)             ; * J206A
206E: CB 7A          BIT   7,D                ;
2070: 28 06          JR    Z,$2078            ; 
2072: 2F             CPL                      ;
2073: 5F             LD    E,A                ;
2074: 78             LD    A,B                ;
2075: 2F             CPL                      ;
2076: 47             LD    B,A                ;
2077: 7B             LD    A,E                ;
2078: DD 77 04       LD    (IX+$04),A         ; * J2070
207B: DD 70 05       LD    (IX+$05),B         ;
207E: 23             INC   HL                 ;
207F: 5E             LD    E,(HL)             ;
2080: 16 00          LD    D,$00              ;
2082: 79             LD    A,C                ;
2083: FE 0A          CP    $0A                ;
2085: 30 01          JR    NC,$2088           ; 
2087: 14             INC   D                  ;
2088: DD 72 09       LD    (IX+$09),D         ; * J2085
208B: DD 73 08       LD    (IX+$08),E         ;
208E: DD 36 00 29    LD    (IX+$00),$29       ;
2092: 2A 1A E3       LD    HL,($E31A)         ; * C108D
2095: DD 75 0B       LD    (IX+$0B),L         ;
2098: DD 74 0F       LD    (IX+$0F),H         ;
209B: C9             RET                      ;

ISROBJRun_29:
;
209C: CD 63 1C       CALL  $1C63              ; 
209F: CD FB 20       CALL  $20FB              ; 
20A2: 22 D6 E0       LD    ($E0D6),HL         ; 
20A5: 7C             LD    A,H                ;
20A6: 2A DC E0       LD    HL,($E0DC)         ; 
20A9: C3 F1 1C       JP    $1CF1              ; 

ISROBJRun_20:
;
20AC: DD 35 0A       DEC   (IX+$0A)           ;
20AF: C2 B8 08       JP    NZ,$08B8           ;{DrawObject} 
20B2: DD 36 0A 06    LD    (IX+$0A),$06       ;
20B6: DD 7E 0D       LD    A,(IX+$0D)         ;
20B9: FE 39          CP    $39                ;
20BB: D2 52 08       JP    NC,$0852           ; 
20BE: DD 34 0D       INC   (IX+$0D)           ;
20C1: C3 B8 08       JP    $08B8              ;{DrawObject} 

ISROBJRun_21:
;
20C4: DD 35 0A       DEC   (IX+$0A)           ;
20C7: C2 B8 08       JP    NZ,$08B8           ;{DrawObject} 
20CA: DD 7E 07       LD    A,(IX+$07)         ;
20CD: FE 80          CP    $80                ;
20CF: D2 52 08       JP    NC,$0852           ; 
20D2: 06 80          LD    B,$80              ;
20D4: DD 36 00 00    LD    (IX+$00),$00       ;
20D8: C3 69 08       JP    $0869              ; 
20DB: DD E5          PUSH  IX                 ; * C1433,C1D23,C1F2B,C201D,C20FB
20DD: E1             POP   HL                 ;
20DE: 11 D4 E0       LD    DE,$E0D4           ;
20E1: 01 0A 00       LD    BC,$000A           ;
20E4: ED B0          LDIR                     ;
20E6: ED 5B D6 E0    LD    DE,($E0D6)         ; 
20EA: 2A D8 E0       LD    HL,($E0D8)         ; 
20ED: 19             ADD   HL,DE              ;
20EE: C9             RET                      ;
20EF: DD E5          PUSH  IX                 ; * J1487,C1D00,C1F78
20F1: D1             POP   DE                 ;
20F2: 21 D4 E0       LD    HL,$E0D4           ;
20F5: 01 0A 00       LD    BC,$000A           ;
20F8: ED B0          LDIR                     ;
20FA: C9             RET                      ;
20FB: CD DB 20       CALL  $20DB              ; * C1CDA,C209F
20FE: EB             EX    DE,HL              ;
20FF: DD 6E 0B       LD    L,(IX+$0B)         ;
2102: DD 66 0F       LD    H,(IX+$0F)         ;
2105: ED 4B 1A E3    LD    BC,($E31A)         ; 
2109: ED 42          SBC   HL,BC              ;
210B: 19             ADD   HL,DE              ;
210C: C9             RET                      ;
210D: 21 51 E0       LD    HL,$E051           ;
2110: 3A 00 E3       LD    A,($E300)          ;{-1_buggyHandler} 
2113: 3D             DEC   A                  ;
2114: 28 11          JR    Z,$2127            ; 
2116: 7E             LD    A,(HL)             ;
2117: A7             AND   A                  ;
2118: F0             RET   P                  ;
2119: 21 11 E5       LD    HL,$E511           ;
211C: 3E 01          LD    A,$01              ;
211E: 86             ADD   A,(HL)             ;
211F: 27             DAA                      ;
2120: 77             LD    (HL),A             ;
2121: 23             INC   HL                 ;
2122: 7E             LD    A,(HL)             ;
2123: CE 00          ADC   $00                ;
2125: 27             DAA                      ;
2126: 77             LD    (HL),A             ;
2127: 3E 37          LD    A,$37              ; * J2114
2129: 32 51 E0       LD    ($E051),A          ;{-1_isrCount4} 
212C: 11 90 80       LD    DE,$8090           ; * C0D0C
212F: FD 21 90 84    LD    IY,$8490           ;
2133: 0E 02          LD    C,$02              ;
2135: CD E7 03       CALL  $03E7              ;{TransColor} 
2138: 3A 12 E5       LD    A,($E512)          ; 
213B: CD BD 03       CALL  $03BD              ;{PrintDigit} 
213E: 3A 11 E5       LD    A,($E511)          ; 
2141: C3 AE 03       JP    $03AE              ;{PrintBCD} 

; Big chunk of data

2144: 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 
2154: 00 00 00 00 00 00 00 00 00 00 00 00 00 06 01 03 
2164: 34 07 49 08 63 0F 73 07 80 19 92 0F A0 06 A1 03 
2174: A2 2A E0 32 FF 28 0F 0F 3F 30 40 06 41 03 42 2A 
2184: 4C 0F 92 0F 9F 28 A5 07 B8 0F CD 0F E0 06 E1 03 
2194: 00 19 01 08 14 07 20 33 4F 0F 7F 30 80 06 81 03 
21A4: 82 22 9C 1C B6 1C C0 2A D9 1C DF 20 03 0F 08 28 
21B4: 16 07 20 06 21 03 3C 22 52 1C 60 32 6E 1C 7F 20 
21C4: A6 08 B7 0F BF 30 C0 06 C1 03 C4 08 D3 0A E6 0E 
21D4: F6 0F 0C 10 1C 0F 2D 0E 39 07 4A 0F 5B 0F 60 06 
21E4: 61 03 6E 19 6F 09 82 0F 8F 09 A0 2B A2 0F B1 0F 
21F4: FF 28 00 06 01 03 02 22 14 1C 28 1C 40 2A 54 1C 
2204: 5F 20 9F 28 A0 06 A1 03 A2 23 A6 1C D3 1C E9 0F 
2214: F7 0A FF 20 07 10 17 0E 29 10 35 0A 40 06 41 02 
2224: 42 1A 60 03 6F 12 78 12 88 12 92 12 A3 12 A4 12 
2234: B1 12 C2 12 CD 12 CE 12 D9 12 E0 06 E1 03 EB 12 
2244: FA 12 06 12 07 12 14 12 23 12 2C 12 37 12 42 12 
2254: 56 12 57 12 65 12 6E 12 7A 12 80 06 81 03 85 12 
2264: 86 12 91 12 92 12 A3 12 A4 12 AE 12 B8 12 B9 12 
2274: CA 12 CB 12 D7 12 E3 12 F3 12 00 19 20 06 21 03 
2284: 22 2C 60 33 9F 28 BF 30 C0 06 C1 03 C2 24 D5 1C 
2294: EA 1C 00 33 05 1C 18 1C 31 1C 3F 20 48 30 60 06 
22A4: 61 03 7B 24 87 1C 99 1C A0 2B AE 1C C5 1C D7 1C 
22B4: DF 20 E0 28 00 06 01 04 13 14 1E 16 2D 16 2F 16 
22C4: 3A 15 4C 16 4E 16 58 16 66 16 68 16 72 02 73 14 
22D4: 7E 16 80 19 A0 86 A1 03 A2 34 C7 0F EC 10 0F 0A 
22E4: 1F 30 2A 10 40 86 41 02 42 19 60 32 61 05 80 2A 
22F4: BF 30 C0 02 DF 28 E0 06 E1 03 E2 2B 00 23 01 03 
2304: 2A 1C 3F 28 45 1C 57 1C 6C 1C 6D 20 80 06 81 02 
2314: A0 03 A8 10 B4 0A C5 07 DC 0F E3 09 F2 07 0A 10 
2324: 0D 09 1C 08 20 06 21 03 2C 0F 2F 0F 32 0A 45 13 
2334: 54 13 66 13 77 0A 8A 13 98 13 A7 13 B4 13 C0 06 
2344: C1 03 C5 09 D4 0A E0 02 E7 0A F5 09 00 04 1C 16 
2354: 2A 15 2C 15 35 16 3D 14 40 02 48 14 4A 14 60 86 
2364: 61 02 62 19 80 03 81 2C A0 33 DF 28 FF 30 00 86 
2374: 01 03 02 2C 40 23 57 1C 5F 28 6C 1C 83 1C 9A 1C 
2384: A0 86 A1 03 A2 23 AE 1C C5 1C D5 1C E0 33 E8 1C 
2394: F5 0F FF 20 0A 09 1C 0A 28 30 32 10 40 06 42 02 
23A4: 5B 2B 60 03 80 33 9F 28 D0 30 E0 06 E1 03 E2 1B 
23B4: 20 17 60 18 80 06 81 03 C6 13 D2 0F DD 0F EE 0E 
23C4: FC 0A 01 13 0D 09 20 06 21 03 22 13 2B 13 39 13 
23D4: 49 13 4C 0A 5C 0F 6A 0F 79 13 84 13 86 0A 95 0F 
23E4: A4 13 B3 13 B5 09 C0 06 C1 02 C2 19 E0 03 E1 2C 
23F4: EA 07 F9 09 07 0A 19 0F 2A 0F 39 09 48 28 54 0F 
2404: 60 06 61 03 7B 23 84 1C 92 1C A0 23 A3 1C B3 1C 
2414: C3 1C DC 1C EF 1C FF 20 00 06 01 03 07 10 0A 0A 
2424: 1A 0F 2C 09 32 0F 41 07 4F 08 5C 0F 63 09 70 07 
2434: 7D 0E 80 19 A0 06 A1 03 A2 24 AF 1C BC 1C C0 2C 
2444: CA 1C D9 1C E8 1C F6 1C FF 28 05 0A 10 1C 11 20 
2454: 25 0C 32 0F 35 0C 40 06 41 03 42 19 60 33 80 2B 
2464: 83 0A 92 07 BF 30 C6 0F C9 0A D9 09 DF 28 E0 06 
2474: E1 03 E2 24 EA 1C 04 0A 14 0F 1C 1C 24 20 34 09 
2484: 45 0F 49 0F 4B 0C 58 0C 67 0C 75 0C 7A 0F 80 06 
2494: 81 02 90 04 AD 16 B7 15 BE 14 C5 16 C7 16 D4 14 
24A4: DB 15 E6 14 E8 14 E9 16 F0 14 F1 16 F2 14 02 15 
24B4: 04 15 0E 16 0F 02 10 14 13 16 17 14 19 14 20 86 
24C4: 21 03 22 19 40 2C 41 33 42 03 BE 28 BF 30 C0 86 
24D4: C1 03 C2 1A E8 12 F2 12 F4 12 FD 12 08 12 13 12 
24E4: 22 12 23 12 2E 12 36 12 42 12 4E 12 57 12 60 86 
24F4: 61 03 65 12 67 12 72 12 7A 12 83 12 8F 12 97 12 
2504: A2 12 AB 12 B7 12 C2 12 D0 12 D8 12 E4 12 00 86 
2514: 01 03 20 25 25 09 33 1C 40 2C 48 10 54 1C 65 0F 
2524: 6F 1C 7F 20 80 02 88 28 A0 86 A1 05 BB 35 C0 2C 
2534: DF 02 FF 30 0A 10 19 0A 1F 28 20 03 29 0F 2C 0A 
2544: 32 0F 3A 0F 40 06 41 02 47 0F 4A 0A 50 0F 60 03 
2554: 65 07 79 08 80 17 8A 0A A0 18 C8 09 E0 06 E1 03 
2564: EF 10 F4 0F F7 0A 06 0F 11 10 14 09 1A 1A 3A 12 
2574: 42 12 44 12 4E 12 57 12 59 12 63 12 6B 12 80 06 
2584: 81 02 8F 13 92 0A A0 03 A5 10 A8 07 B2 0F B5 0F 
2594: C5 13 D4 09 E4 0F E6 0C F4 0C 04 10 06 0C 13 0C 
25A4: 20 06 21 03 22 10 23 19 28 10 2A 0A 3B 10 40 25 
25B4: 41 33 4A 1C 55 1C 65 1C 74 1C 82 0F 88 1C 95 0F 
25C4: A5 1C A8 30 B1 1C B2 20 BE 0F C0 06 C1 02 C2 1B 
25D4: CA 10 E0 03 E6 0A F0 17 03 08 12 18 13 09 40 1A 
25E4: 4A 0A 60 06 61 03 74 12 85 12 87 12 92 12 94 12 
25F4: A9 12 AA 12 B4 10 BD 12 C3 12 CC 0F D5 12 D7 12 
2604: E5 12 E7 12 F4 12 00 06 01 02 02 25 03 2C 0A 1C 
2614: 17 1C 20 03 27 10 37 1C 48 1C 59 1C 6A 0A 79 1C 
2624: 80 28 8D 0F 90 1C 91 20 A0 06 A1 03 AD 0C B2 0F 
2634: BB 0C CB 0C D8 0F E5 0F E7 10 F1 0F F9 0F 08 0C 
2644: 0D 0F 16 0C 20 19 25 0F 28 09 36 10 40 06 41 02 
2654: 42 25 4A 1C 5A 0F 60 03 61 2C 65 10 79 1C 88 1C 
2664: 94 1C A2 1C AE 1C BB 1C BF 20 CA 0F D0 28 DC 10 
2674: E0 06 E1 03 E8 0F EA 10 EC 0A F9 0F 08 13 0A 07 
2684: 17 0F 1A 0A 2A 0C 37 10 3C 0C 43 02 80 06 00 06 
2694: 20 03 28 10 34 0A 47 0C 55 0C 5A 0F 63 09 72 07 
26A4: 85 13 94 13 A0 06 A1 04 B3 14 BF 16 CD 16 DA 15 
26B4: EC 16 EE 16 F8 16 F9 03 00 2B 20 23 40 86 4A 1C 
26C4: 50 28 65 1C 77 1C 7E 05 7F 20 80 33 C8 03 CF 30 
26D4: E0 06 00 17 20 18 6A 0A 73 07 01 02 20 01 34 C0 
26E4: 3A C2 48 20 54 C2 59 20 64 C2 69 E2 6D C2 76 22 
26F4: 82 20 90 C0 96 C0 9C C0 A2 C0 BE C1 CB C0 D8 20 
2704: E6 C2 F4 22 00 C2 05 FF 4D 00 4E 02 5E 22 77 22 
2714: 8A 22 8B FF D8 00 E0 02 45 22 55 C2 00 00 00 00 
2724: 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 
2734: 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 
2744: 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 
2754: 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 
2764: 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 
2774: 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 
2784: 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 
2794: 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 
27A4: 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 
27B4: 00 00 00 00 00 00 00 00 00 00 00 00 

27C0: 21 46 E0       LD    HL,$E046           ; * J1516,J151D
27C3: 35             DEC   (HL)               ;
27C4: FB             EI                       ;
27C5: 78             LD    A,B                ;
27C6: 32 13 E5       LD    ($E513),A          ; 
27C9: FE 05          CP    $05                ;
27CB: CA D2 27       JP    Z,$27D2            ; 
27CE: A7             AND   A                  ;
27CF: C2 5E 28       JP    NZ,$285E           ; 
27D2: CD FA 29       CALL  $29FA              ; * J27CB
27D5: 3E 1E          LD    A,$1E              ; Play ...
27D7: CD 75 0D       CALL  $0D75              ;{AddSound} ... congratulations music
27DA: 21 0F E5       LD    HL,$E50F           ;
27DD: 36 00          LD    (HL),$00           ;
27DF: 23             INC   HL                 ; Now E510
27E0: 34             INC   (HL)               ; Increment the course number
27E1: CD 48 29       CALL  $2948              ; 
27E4: CD E8 05       CALL  $05E8              ;{Delay3Sec} 
27E7: 21 24 2C       LD    HL,$2C24           ; "CONGRATULATIONS" script
27EA: CD 00 03       CALL  $0300              ;{RunTextScript} 
27ED: CD BA 28       CALL  $28BA              ; 
27F0: 21 0C 2C       LD    HL,$2C0C           ; "SPECIAL BOUNS POINTS" script
27F3: CD 00 03       CALL  $0300              ;{RunTextScript} 
27F6: 3A 13 E5       LD    A,($E513)          ; 
27F9: 17             RLA                      ; * J2880
27FA: 17             RLA                      ;
27FB: 17             RLA                      ;
27FC: 17             RLA                      ;
27FD: 26 00          LD    H,$00              ;
27FF: E6 F0          AND   $F0                ;
2801: 6F             LD    L,A                ;
2802: 20 01          JR    NZ,$2805           ; 
2804: 24             INC   H                  ;
2805: 22 98 E0       LD    ($E098),HL         ; * J2802
2808: CD 71 29       CALL  $2971              ; 
280B: 2A 96 E0       LD    HL,($E096)         ; 
280E: 56             LD    D,(HL)             ;
280F: 2B             DEC   HL                 ;
2810: 5E             LD    E,(HL)             ;
2811: 2A 11 E5       LD    HL,($E511)         ; 
2814: A7             AND   A                  ;
2815: ED 52          SBC   HL,DE              ;
2817: 30 0E          JR    NC,$2827           ; 
2819: 19             ADD   HL,DE              ;
281A: EB             EX    DE,HL              ;
281B: 2A 96 E0       LD    HL,($E096)         ; 
281E: 72             LD    (HL),D             ;
281F: 2B             DEC   HL                 ;
2820: 73             LD    (HL),E             ;
2821: 21 39 2C       LD    HL,$2C39           ; "YOU HAVE BROKEN A RECORD" script
2824: CD 4E 03       CALL  $034E              ;{SlowScript} 
2827: 2A 94 E0       LD    HL,($E094)         ; * J2817,J285C
282A: ED 5B 11 E5    LD    DE,($E511)         ; 
282E: 7D             LD    A,L                ;
282F: D6 01          SUB   $01                ;
2831: 27             DAA                      ;
2832: 6F             LD    L,A                ;
2833: 30 01          JR    NC,$2836           ; 
2835: 25             DEC   H                  ;
2836: 22 94 E0       LD    ($E094),HL         ; * J2833
2839: A7             AND   A                  ;
283A: ED 52          SBC   HL,DE              ;
283C: 38 50          JR    C,$288E            ; 
283E: CD 68 29       CALL  $2968              ; 
2841: 2A 98 E0       LD    HL,($E098)         ; 
2844: 7D             LD    A,L                ;
2845: C6 01          ADD   $01                ;
2847: 27             DAA                      ;
2848: 6F             LD    L,A                ;
2849: 30 01          JR    NC,$284C           ; 
284B: 24             INC   H                  ;
284C: 22 98 E0       LD    ($E098),HL         ; * J2849
284F: CD 71 29       CALL  $2971              ; 
2852: 3E 10          LD    A,$10              ; Play ...
2854: CD 75 0D       CALL  $0D75              ;{AddSound} ... passing point
2857: 3E 0C          LD    A,$0C              ;
2859: CD EA 05       CALL  $05EA              ; 
285C: 18 C9          JR    $2827              ; 
285E: 3E 1D          LD    A,$1D              ; Play ... * J27CF
2860: CD 75 0D       CALL  $0D75              ;{AddSound} ... reached goal
2863: CD D6 29       CALL  $29D6              ; 
2866: CD 12 0D       CALL  $0D12              ; 
2869: CD 48 29       CALL  $2948              ; 
286C: 3E 30          LD    A,$30              ;
286E: CD EA 05       CALL  $05EA              ; 
2871: CD BA 28       CALL  $28BA              ; 
2874: 38 0D          JR    C,$2883            ; 
2876: 21 E4 2B       LD    HL,$2BE4           ; "GOOD BONUS POINTS" script
2879: CD 4E 03       CALL  $034E              ;{SlowScript} 
287C: 3A F9 E0       LD    A,($E0F9)          ;{-1_champColors} 
287F: 3C             INC   A                  ;
2880: C3 F9 27       JP    $27F9              ; 
2883: 21 F9 2B       LD    HL,$2BF9           ; "SORRY NO BONUS" script * J2874
2886: CD 4E 03       CALL  $034E              ;{SlowScript} 
2889: CD E8 05       CALL  $05E8              ;{Delay3Sec} 
288C: 18 0E          JR    $289C              ; 
288E: CD E8 05       CALL  $05E8              ;{Delay3Sec} * J283C
2891: 11 01 E5       LD    DE,$E501           ;
2894: 21 98 E0       LD    HL,$E098           ;
2897: 06 02          LD    B,$02              ;
2899: CD 36 06       CALL  $0636              ; 
289C: 21 00 00       LD    HL,$0000           ; * J288C
289F: 22 11 E5       LD    ($E511),HL         ; 
28A2: 21 13 E5       LD    HL,$E513           ;
28A5: 7E             LD    A,(HL)             ;
28A6: A7             AND   A                  ;
28A7: C2 B7 0B       JP    NZ,$0BB7           ; 
28AA: 36 05          LD    (HL),$05           ;
28AC: 21 A2 23       LD    HL,$23A2           ;
28AF: 22 16 E5       LD    ($E516),HL         ; 
28B2: 3E 1A          LD    A,$1A              ;
28B4: 32 0E E5       LD    ($E50E),A          ; 
28B7: C3 B7 0B       JP    $0BB7              ; 
28BA: CD E8 05       CALL  $05E8              ;{Delay3Sec} * C27ED,C2871
28BD: CD 5A 29       CALL  $295A              ; 
28C0: 3A 10 E5       LD    A,($E510)          ; Course number
28C3: D6 02          SUB   $02                ;
28C5: 28 07          JR    Z,$28CE            ; 
28C7: 3E 0A          LD    A,$0A              ;
28C9: FA CE 28       JP    M,$28CE            ; 
28CC: 3E 05          LD    A,$05              ;
28CE: 5F             LD    E,A                ; * J28C5,J28C9
28CF: 3A 13 E5       LD    A,($E513)          ; 
28D2: 01 80 00       LD    BC,$0080           ;
28D5: FE 08          CP    $08                ;
28D7: 30 09          JR    NC,$28E2           ; 
28D9: 01 00 01       LD    BC,$0100           ;
28DC: FE 03          CP    $03                ;
28DE: 30 02          JR    NC,$28E2           ; 
28E0: 0E 20          LD    C,$20              ;
28E2: ED 43 94 E0    LD    ($E094),BC         ; * J28D7,J28DE
28E6: 83             ADD   A,E                ;
28E7: 87             ADD   A,A                ;
28E8: 5F             LD    E,A                ;
28E9: FE 0A          CP    $0A                ;
28EB: 20 09          JR    NZ,$28F6           ; 
28ED: 3A 10 E5       LD    A,($E510)          ; Course number
28F0: FE 03          CP    $03                ;
28F2: 28 02          JR    Z,$28F6            ; 
28F4: 1E 14          LD    E,$14              ;
28F6: 16 00          LD    D,$00              ; * J28EB,J28F2
28F8: 21 0C E0       LD    HL,$E00C           ;
28FB: 19             ADD   HL,DE              ;
28FC: 7E             LD    A,(HL)             ;
28FD: 23             INC   HL                 ;
28FE: 22 96 E0       LD    ($E096),HL         ; 
2901: B6             OR    (HL)               ;
2902: 20 03          JR    NZ,$2907           ; 
2904: 70             LD    (HL),B             ;
2905: 2B             DEC   HL                 ;
2906: 71             LD    (HL),C             ;
2907: 21 79 2B       LD    HL,$2B79           ; "TIME TO REACH POINT " script * J2902
290A: CD 4E 03       CALL  $034E              ;{SlowScript} 
290D: CD 81 29       CALL  $2981              ; 
2910: A7             AND   A                  ;
2911: 20 02          JR    NZ,$2915           ; 
2913: 3E 1A          LD    A,$1A              ;
2915: C6 40          ADD   $40                ; * J2911
2917: 1B             DEC   DE                 ;
2918: 1B             DEC   DE                 ;
2919: 12             LD    (DE),A             ;
291A: 21 94 2B       LD    HL,$2B94           ;
291D: CD 4E 03       CALL  $034E              ;{SlowScript} 
2920: 21 12 E5       LD    HL,$E512           ;
2923: 13             INC   DE                 ;
2924: CD 9A 03       CALL  $039A              ; 
2927: 21 B0 2B       LD    HL,$2BB0           ; "THE AVERAGE TIME " script
292A: CD 4E 03       CALL  $034E              ;{SlowScript} 
292D: CD 68 29       CALL  $2968              ; 
2930: 21 CC 2B       LD    HL,$2BCC           ; "TOP RECORD " script
2933: CD 4E 03       CALL  $034E              ;{SlowScript} 
2936: 2A 96 E0       LD    HL,($E096)         ; 
2939: 13             INC   DE                 ;
293A: CD 9A 03       CALL  $039A              ; 
293D: 2A 94 E0       LD    HL,($E094)         ; 
2940: ED 5B 11 E5    LD    DE,($E511)         ; 
2944: A7             AND   A                  ;
2945: ED 52          SBC   HL,DE              ;
2947: C9             RET                      ;
2948: 21 00 E1       LD    HL,$E100           ; * C0D8D,C27E1,C2869
294B: 01 A4 00       LD    BC,$00A4           ;
294E: CD FA 05       CALL  $05FA              ; 
2951: 01 20 02       LD    BC,$0220           ;
2954: 21 E0 80       LD    HL,$80E0           ; * J2966
2957: C3 FA 05       JP    $05FA              ; 
295A: 21 00 E1       LD    HL,$E100           ; * C28BD
295D: 01 C6 00       LD    BC,$00C6           ;
2960: CD FA 05       CALL  $05FA              ; 
2963: 01 20 03       LD    BC,$0320           ;
2966: 18 EC          JR    $2954              ; 
2968: 11 D9 81       LD    DE,$81D9           ; * C283E,C292D
296B: 21 95 E0       LD    HL,$E095           ;
296E: C3 9A 03       JP    $039A              ; 
2971: 21 99 E0       LD    HL,$E099           ; * C2808,C284F
2974: 11 97 82       LD    DE,$8297           ;
2977: CD 93 03       CALL  $0393              ;{Print3BCD} 
297A: EB             EX    DE,HL              ;
297B: 36 30          LD    (HL),$30           ;
297D: 23             INC   HL                 ;
297E: 36 30          LD    (HL),$30           ;
2980: C9             RET                      ;
2981: 3A 0E E5       LD    A,($E50E)          ; * C0C1A,C0E73,C290D,C29AB
2984: FE 1A          CP    $1A                ;
2986: D8             RET   C                  ;
2987: D6 1A          SUB   $1A                ;
2989: C9             RET                      ;
298A: 21 CC 80       LD    HL,$80CC           ; * C0D0F
298D: 11 CC 84       LD    DE,$84CC           ;
2990: 01 02 10       LD    BC,$1002           ;
2993: CD E7 03       CALL  $03E7              ;{TransColor} 
2996: 79             LD    A,C                ;
2997: 36 21          LD    (HL),$21           ; * J299C
2999: 12             LD    (DE),A             ;
299A: 23             INC   HL                 ;
299B: 13             INC   DE                 ;
299C: 10 F9          DJNZ  $2997              ; 
299E: 21 CC 80       LD    HL,$80CC           ;
29A1: 06 05          LD    B,$05              ;
29A3: 34             INC   (HL)               ; * J29A7
29A4: 23             INC   HL                 ;
29A5: 23             INC   HL                 ;
29A6: 23             INC   HL                 ;
29A7: 10 FA          DJNZ  $29A3              ; 
29A9: 36 1B          LD    (HL),$1B           ;
29AB: CD 81 29       CALL  $2981              ; 
29AE: 21 CC 80       LD    HL,$80CC           ;
29B1: 06 05          LD    B,$05              ;
29B3: FE 05          CP    $05                ; * J29C1
29B5: 38 0C          JR    C,$29C3            ; 
29B7: 16 03          LD    D,$03              ;
29B9: 36 29          LD    (HL),$29           ; * J29BD
29BB: 23             INC   HL                 ;
29BC: 15             DEC   D                  ;
29BD: 20 FA          JR    NZ,$29B9           ; 
29BF: D6 05          SUB   $05                ;
29C1: 10 F0          DJNZ  $29B3              ; 
29C3: 57             LD    D,A                ; * J29B5
29C4: 87             ADD   A,A                ;
29C5: 87             ADD   A,A                ;
29C6: 82             ADD   A,D                ;
29C7: 5F             LD    E,A                ;
29C8: FE 08          CP    $08                ; * J29D4
29CA: 38 10          JR    C,$29DC            ; 
29CC: 28 01          JR    Z,$29CF            ; 
29CE: 3D             DEC   A                  ;
29CF: 36 29          LD    (HL),$29           ; * J29CC
29D1: 23             INC   HL                 ;
29D2: D6 08          SUB   $08                ;
29D4: 18 F2          JR    $29C8              ; 
29D6: 2A F4 E0       LD    HL,($E0F4)         ; * C0E03,C2863
29D9: 3A F6 E0       LD    A,($E0F6)          ; 
29DC: 3C             INC   A                  ; * J29CA
29DD: 57             LD    D,A                ;
29DE: C6 21          ADD   $21                ;
29E0: CB 66          BIT   4,(HL)             ;
29E2: 28 07          JR    Z,$29EB            ; 
29E4: D6 06          SUB   $06                ;
29E6: FE 20          CP    $20                ;
29E8: 20 01          JR    NZ,$29EB           ; 
29EA: 3D             DEC   A                  ;
29EB: 77             LD    (HL),A             ; * J29E2,J29E8
29EC: 7A             LD    A,D                ;
29ED: FE 08          CP    $08                ;
29EF: 38 02          JR    C,$29F3            ; 
29F1: AF             XOR   A                  ;
29F2: 2C             INC   L                  ;
29F3: 32 F6 E0       LD    ($E0F6),A          ; * J29EF
29F6: 22 F4 E0       LD    ($E0F4),HL         ; 
29F9: C9             RET                      ;
29FA: 21 CC 80       LD    HL,$80CC           ; * C27D2
29FD: 06 0F          LD    B,$0F              ;
29FF: 36 29          LD    (HL),$29           ; * J2A02
2A01: 23             INC   HL                 ;
2A02: 10 FB          DJNZ  $29FF              ; 
2A04: 36 1F          LD    (HL),$1F           ;
2A06: 3E 5A          LD    A,$5A              ;
2A08: 32 52 80       LD    ($8052),A          ; 
2A0B: C9             RET                      ;


; Looks like data from here down

; Score values for various things
2A0C: 00 00 00 ; 000000 
2A0F: 20 00 00 ; 000020
2A12: 50 00 00 ; 000050    Successfully jumping a crater
2A15: 80 00 00 ; 000080
2A18: 00 01 00 ; 000100    Shooting a rock, shooting an alien ship
2A1B: 00 02 00 ; 000200
2A1E: 00 03 00 ; 000300
2A21: 00 05 00 ; 000500
2A24: 00 08 00 ; 000800
2A27: 00 10 00 ; 001000
      
; CODEBUG1 : "Continue" is spelled wrong
2A2A: 08 81 08  ; Screen:8108 Color:8
2A2D: 54 4F 20 43 4F 55 4E 54 49 4E 55 45 20 47 41 4D 45  ; "TO_COUNTINUE_GAME"
2A3E: 22  ; Set Cursor and Color
2A3F: 2D 82 08  ; Screen:822D Color:8
2A42: 54 49 4D 45  ; "TIME"
2A46: 21  ; END OF SCRIPT

2A47: 46 81 08  ; Screen:8146 Color:8
2A4A: 42 45 47 49 4E 4E 45 52 20 43 4F 55 52 53 45 20 47 4F 20 5B  ; "BEGINNER_COURSE_GO__"
2A5E: 21  ; END OF SCRIPT

2A5F: 46 81 00  ; Screen:8146 Color:0
2A62: 43 48 41 4D 50 49 4F 4E 20 43 4F 55 52 53 45 20 31 20 47 4F 20 5B  ; "CHAMPION_COURSE_1_GO__"
2A78: 21  ; END OF SCRIPT

; CODEBUG2: This doesn't appear to be used anywhere. Free-play is implemented by always having 2 credits.
2A79: 4C 82 00  ; Screen:824C Color:0
2A7C: 46 52 45 45 20 50 4C 41 59  ; "FREE_PLAY"
2A85: 21  ; END OF SCRIPT

2A86: EA 81 00  ; Screen:81EA Color:0
2A89: 4F 4E 4C 59 20 31 20 50 4C 41 59 45 52  ; "ONLY_1_PLAYER"
2A96: 21  ; END OF SCRIPT

2A97: EA 81 00  ; Screen:81EA Color:0
2A9A: 31 20 4F 52 20 32 20 50 4C 41 59 45 52 53  ; "1_OR_2_PLAYERS"
2AA8: 21  ; END OF SCRIPT

2AA9: 06 82 00  ; Screen:8206 Color:0
2AAC: 50 49 43 54 55 52 45 20 4E 55 4D 42 45 52 20 53 45 54  ; "PICTURE_NUMBER_SET"
2ABE: 22  ; Set Cursor and Color
2ABF: 4A 82 00  ; Screen:824A Color:0
2AC2: 4E 45 58 54 20 31 50 20 42 55 54 54 4F 4E  ; "NEXT_1P_BUTTON"
2AD0: 21  ; END OF SCRIPT

2AD1: 6A 81 00  ; Screen:816A Color:0
2AD4: 20 50 55 53 48 20 42 55 54 54 4F 4E 20  ; "_PUSH_BUTTON_"
2AE1: 21  ; END OF SCRIPT

2AE2: D4 83 00  ; Screen:83D4 Color:0
2AE5: 43 52 45 44 49 54 20  ; "CREDIT_"
2AEC: 21  ; END OF SCRIPT

2AED: 88 81 00  ; Screen:8188 Color:0
2AF0: 47 41 4D 45 20 4F 56 45 52 20 50 4C 41 59 45 52 20  ; "GAME_OVER_PLAYER_"
2B01: 21  ; END OF SCRIPT

2B02: 0C 82 00  ; Screen:820C Color:0
2B05: 47 41 4D 45 20 4F 56 45 52  ; "GAME_OVER"
2B0E: 21  ; END OF SCRIPT

2B0F: 2B 80 02  ; Screen:802B Color:2
2B12: 04  ; "_" Border
2B13: 25 0F 14  ; Repeat character 20 for 15 times
2B16: 05  ; "_" Border
2B17: 22  ; Set Cursor and Color
2B18: 41 80 01  ; Screen:8041 Color:1
2B1B: 0C 0D  ; "__" Crown
2B1D: 25 06 00  ; Repeat character 0 for 6 times
2B20: 22  ; Set Cursor and Color
2B21: 49 80 09  ; Screen:8049 Color:9
2B24: 3F  ; "_" black circle
2B25: 22  ; 
2B26: 4B 80 02  ; Screen:804B Color:2
2B29: 06 50 4F 49 4E 54  ; "_POINT"
2B2F: 25 04 00  ; Repeat character 0 for 4 times
2B32: 12  ; "_" Black circle
2B33: 25 05 00  ; Repeat character 0 for 5 times
2B36: 07  ; "_" Border
2B37: 22  ; Set Cursor and Color
2B38: 6B 80 02  ; Screen:806B Color:2
2B3B: 06  ; "_"
2B3C: 25 09 00  ; Repeat character 0 for 9 times
2B3F: 12  ; "_"
2B40: 25 05 00  ; Repeat character 0 for 5 times
2B43: 07  ; "_"
2B44: 22  ; Set Cursor and Color
2B45: 8B 80 02  ; Screen:808B Color:2
2B48: 06 0E 0F 10 11  ; "_____"
2B4D: 25 05 00  ; Repeat character 0 for 5 times
2B50: 12  ; "_"
2B51: 25 05 00  ; Repeat character 0 for 5 times
2B54: 07  ; "_"
2B55: 22  ; Set Cursor and Color
2B56: AB 80 02  ; Screen:80AB Color:2
2B59: 08 16 15 15 17 15 15 18 15 15 19 15 15 1A 15 15 09  ; "_________________"
2B6A: 22  ; Set Cursor and Color
2B6B: 81 80 01  ; Screen:8081 Color:1
2B6E: 31 50 3F  ; "1P_"
2B71: 21  ; END OF SCRIPT

2B72: A1 80 01  ; Screen:80A1 Color:1
2B75: 32 50 3F  ; "2P_"
2B78: 21  ; END OF SCRIPT

2B79: 25 81 01  ; Screen:8125 Color:1
2B7C: 54 49 4D 45 20 54 4F 20 52 45 41 43 48 20 50 4F 49 4E 54 20 5E 00 5E  ; "TIME_TO_REACH_POINT__ _"
2B93: 21  ; END OF SCRIPT

2B94: 84 81 00  ; Screen:8184 Color:0
2B97: 59 4F 55 52 20 54 49 4D 45 20 20 20 20 20 20 20 20 20 20  ; "YOUR_TIME__________"
2BAA: 22  ; Set Cursor and Color
2BAB: 97 81 01  ; Screen:8197 Color:1
2BAE: 5D  ; "_"
2BAF: 21  ; END OF SCRIPT

2BB0: C4 81 00  ; Screen:81C4 Color:0
2BB3: 54 48 45 20 41 56 45 52 41 47 45 20 54 49 4D 45 20 20 20  ; "THE_AVERAGE_TIME___"
2BC6: 22  ; Set Cursor and Color
2BC7: D7 81 01  ; Screen:81D7 Color:1
2BCA: 5D  ; "_"
2BCB: 21  ; END OF SCRIPT

2BCC: 04 82 01  ; Screen:8204 Color:1
2BCF: 54 4F 50 20 52 45 43 4F 52 44 20 20 20 20 20 20 20 20 20 5D  ; "TOP_RECORD__________"
2BE3: 21  ; END OF SCRIPT

2BE4: 85 82 00  ; Screen:8285 Color:0
2BE7: 47 4F 4F 44 20 42 4F 4E 55 53 20 50 4F 49 4E 54 53  ; "GOOD_BONUS_POINTS"
2BF8: 21  ; END OF SCRIPT

2BF9: 67 82 00  ; Screen:8267 Color:0
2BFC: 53 4F 52 52 59 20 4E 4F 20 42 4F 4E 55 53 5B  ; "SORRY_NO_BONUS_"
2C0B: 21  ; END OF SCRIPT

2C0C: 65 82 01  ; Screen:8265 Color:1
2C0F: 53 50 45 43 49 41 4C 20 42 4F 4E 55 53 20 50 4F 49 4E 54 53  ; "SPECIAL_BONUS_POINTS"
2C23: 21  ; END OF SCRIPT

2C24: 25 81 00  ; Screen:8125 Color:0
2C27: 43 4F 4E 47 52 41 54 55 4C 41 54 49 4F 4E 53 20 5B  ; "CONGRATULATIONS__"
2C38: 21  ; END OF SCRIPT

2C39: E5 82 01  ; Screen:82E5 Color:1
2C3C: 59 4F 55 20 48 41 56 45 20 42 52 4F 4B 45 4E 20 41 20 52 45 43 4F 52 44 20 5B  ; "YOU_HAVE_BROKEN_A_RECORD__"
2C56: 21  ; END OF SCRIPT

2C57: 6A 81 00  ; Screen:816A Color:0
2C5A: 49 4E 53 45 52 54 20 43 4F 49 4E 20  ; "INSERT_COIN_"
2C66: 21  ; END OF SCRIPT

2C67: C7 81 00  ; Screen:81C7 Color:0
2C6A: 31 20 50 4C 41 59 45 52 20 20 20 31 20 43 4F 49 4E 20  ; "1_PLAYER___1_COIN_"
2C7C: 21  ; END OF SCRIPT

2C7D: C5 81 00  ; Screen:81C5 Color:0
2C80: 41 20 5F 20 31 20 50 4C 41 59 45 52 20 20 20 31 20 43 4F 49 4E 20  ; "A___1_PLAYER___1_COIN_"
2C96: 21  ; END OF SCRIPT

2C97: C8 82 00  ; Screen:82C8 Color:0
2C9A: 5C 31 39 38 32 20 49 52 45 4D 20 43 4F 52 50 2F  ; "_1982_IREM_CORP."
2CAA: 21  ; END OF SCRIPT

2CAB: 76 80 02  ; Screen:8076 Color:2
2CAE: 3A 3B 3C 3D 3E  ; "_____" CAUTION (small letters)
2CB3: 21  ; END OF SCRIPT

2CB4: F0 F0 ED F0 F0 FB FB FB 
2CBC: F0 E8 F0 F0 F0 EE F0 F0 F0 F0 E0 F0 F0 FB FB FB 
2CCC: F0 F0 F0 F2 F2 F0 F0 F0 E9 F2 EF E3 D2 FC FD FE 
2CDC: E0 D4 D3 EB FF D5 F1 E5 E2 D0 D6 E6 D7 F0 E1 D8 
2CEC: F9 FB F0 F2 D9 EC FC D1 34 32 32 43 34 23 32 11 
2CFC: 23 01 00 00 00 00 00 00 12 12 12 24 77 21 10 56 
2D0C: 21 10 34 21 23 23 21 31 22 21 11 00 77 77 66 65 
2D1C: 55 44 43 33 43 33 21 31 00 9A 51 98 8D 5F B6 30 
2D2C: D2 06 E3 E3 EF C7 F7 B0 FC 9E 00 8E 03 82 06 77 
2D3C: 07 6E 08 66 09 5F 0A 59 
```

```html
<script src="/js/BinaryData.js"></script>
<script src="MoonPatrol.js"></script>
<script src="/js/TileEngine.js"></script>
<script src="/js/CANVAS.js"></script>
```

```code
Splash:
; Text printing for MOON PATROL on the splash
```

```html
<canvas width="1000" height="330"
data-canvasFunction="TileEngine.handleTileCanvas"
data-file="GFX1.html"
data-getTileDataFunction="MoonPatrol.getBackground8x8Data"
data-pixWidth="8"
data-gridX="8"
data-gridY="8"
data-pixHeight="8"
data-gap="0.25"
data-gridPad="1"
data-colors='["#808080","#00B8FF","#FFFFFF","#FF2100"]'
data-command=":14x5:1B0,1B5,1B9,1BE,1C3,,,,,,,,,,
1B1,1B6,1BA,1BF,1C4,1C7,1CB,1CD,1D0,1D3,1D6,1D8,1D9,1DB,
1B2,1B7,1BB,1C0,1C5,1C8,1BF,1BC,1D1,1D4,1D7,1C0,1BC,1C1,
1B3,1B8,1BC,1C1,1C6,1C9,1CC,1CE,1D2,1D5,1BC,1C1,1C5,1DC,
1B4,,1BD,1C2,1BD,1CA,,1CF,1CA,1C2,1BD,1C2,1DA,">
</canvas>
<canvas width="1400" height="330"
data-command=":18x5:1B0,1DD,1E0,1E3,100,100,100,100,1F3,1F7,100,100,100,100,100,100,1C5,1C3,
1B1,1DE,1E1,1E4,1E6,1E9,1ED,1F0,1F4,1F8,1B2,1FD,1FE,1D0,1D3,1D6,1BF,,
1B2,1DF,1E2,1E5,1B2,1EA,1EE,1F1,1F5,1F9,1B3,1B8,1BC,1D1,1D4,1D7,1C0,,
1B3,1B8,,,1E7,1EB,1EF,1F2,1BF,1B0,1FB,,1CE,1D2,1D5,1BC,1FF,,
1B4,,,,1E8,1EC,1B4,,,1FA,1FC,,1CF,1CA,1C2,1BD,1EC,">
</canvas>
```

```code
; This data is a text string with values 1,2, and 3 being special:
; 1 = print "1982 IREM CORP" and END
; 2 = move to top of next column
; 3 = set screen pointer and continue
;
; Any other value is written to the screen and the cursor moves DOWN to
; the next row.
;
; The values are written with color-set 0 and the upper bit set (B0 is tile 1B0).
;
2D44: 03 48 81 
2D47: B0 B1 B2 B3 B4 02 
2D4D: B5 B6 B7 B8 02 
2D52: B9 BA BB BC BD 02 
2D58: BE BF C0 C1 C2 02 
2D5E: C3 C4 C5 C6 BD 02 
2D64: 03 6D 81 
2D67: C7 C8 C9 CA 02 
2D6C: CB BF CC 02 
2D70: CD BC CE CF 02 
2D75: D0 D1 D2 CA 02 
2D7A: D3 D4 D5 C2 02 
2D7F: D6 D7 BC BD 02 
2D84: D8 C0 C1 C2 02 
2D89: D9 BC C5 DA 02 
2D8E: DB C1 DC 02
2D92: 03 06 82 
2D95: B0 B1 B2 B3 B4 02 
2D9B: DD DE DF B8 02 
2DA0: E0 E1 E2 02 
2DA4: E3 E4 E5 02 
2DA8: 00 E6 B2 E7 E8 02 
2DAE: 00 E9 EA EB EC 02 
2DB4: 00 ED EE EF B4 02 
2DBA: 00 F0 F1 F2 02 
2DBF: F3 F4 F5 BF 02 
2DC4: F7 F8 F9 B0 FA 02 
2DCA: 00 B2 B3 FB FC 02 
2DD0: 00 FD B8 02 
2DD4: 00 FE BC CE CF 02 
2DDA: 00 D0 D1 D2 CA 02 
2DE0: 00 D3 D4 D5 C2 02 
2DE6: 00 D6 D7 BC BD 02 
2DEC: C5 BF C0 FF EC 02 
2DF2: C3 
2DF3: 01                        ; Print "1982 IREM CORP" and done
       
2DF4: 00 00 00 00 00 00 00 00 00 00 00 00 

2E00: 19 2F 08 02 18 2F 08 02 15 38 0D 04 
2E0C: 15 38 0D 04 15 42 10 04 15 33 10 00 

ObjectLayout:
;
;     AA BB CC DD
;      AA = starting sprite number
;      BB = yx_cccccc flipX, flipY, colorSet
;      CC = Drawing Routine (pure offset into jump table)
;      DD = ?? total number of tiles. Doesn't seem to be used in moonpatrol. May be part of a library. 
;
;     Data          Number   Drawer         Description
2E18: 01 00 0E 04 ; 00       ObjDraw_07     2x2 Moon buggy normal
2E1C: 09 00 24 04 ; 01       ObjDraw_12     2x2 Moon buggy angled up (crashing)
2E20: 0D 00 24 04 ; 02       ObjDraw_12     2x2 Moon buggy angled down (crashing)
;
2E24: 11 01 08 06 ; 03       ObjDraw_04     3x2 Large explosion pattern 1
2E28: 17 01 08 06 ; 04       ObjDraw_04     3x2 Large explosion pattern 2
2E2C: 1D 01 08 06 ; 05       ObjDraw_04     3x2 Large explosion pattern 3
;
2E30: 23 01 0A 02 ; 06       ObjDraw_05     2x1 Medium explosion pattern 1
2E34: 25 01 0A 02 ; 07       ObjDraw_05     2x1 Medium explosion pattern 2
;
2E38: 27 01 0C 01 ; 08       ObjDraw_06     1x1 Small explosion pattern 1
;
2E3C: 28 01 1C 01 ; 09       ObjDraw_0E     1x1 Player forward shot 1
2E40: 29 01 1C 01 ; 0A       ObjDraw_0E     1x1 Player forward shot 2
2E44: 2A 01 1C 01 ; 0B       ObjDraw_0E     1x1 Player forward shot 3
2E48: 2B 01 1C 01 ; 0C       ObjDraw_0E     1x1 Player forward shot 4
2E4C: 2C 01 1C 01 ; 0D       ObjDraw_0E     1x1 Player forward shot 5
; 
2E50: 2D 04 00 01 ; 0E       ObjDraw_00     1x1 Rock 1 (small, un-shootable)
2E54: 2E 04 00 01 ; 0F       ObjDraw_00     1x1 Rock 2 (medium)
2E58: 2F 04 00 01 ; 10       ObjDraw_00     1x1 Rock 3 (tall)
2E5C: 30 04 00 01 ; 11       ObjDraw_00     1x1 Rock 4 (tall)
;
2E60: 31 04 00 01 ; 12       ObjDraw_00     1x1 Small boulder
2E64: 31 84 00 01 ; 13       ObjDraw_00     1x1 Small boulder (y flip)
2E68: 31 C4 00 01 ; 14       ObjDraw_00     1x1 Small boulder (y flip and x flip)
2E6C: 31 44 00 01 ; 15       ObjDraw_00     1x1 Small boulder (x flip)
;
2E70: 32 04 00 01 ; 16       ObjDraw_00     1x1 Medium boulder rotation 1
2E74: 33 04 00 01 ; 17       ObjDraw_00     1x1 Medium boulder rotation 2
2E78: 34 04 00 01 ; 18       ObjDraw_00     1x1 Medium boulder rotation 3
2E7C: 33 C4 00 01 ; 19       ObjDraw_00     1x1 Medium boulder rotation 2 (y flip and x flip)
2E80: 34 C4 00 01 ; 1A       ObjDraw_00     1x1 Medium boulder rotation 3 (y flip and x flip)
;
2E84: 36 04 00 01 ; 1B       ObjDraw_00     1x1 Large boulder rotation 1 
2E88: 36 84 00 01 ; 1C       ObjDraw_00     1x1 Large boulder rotation 1 (y flip)
2E8C: 37 04 00 01 ; 1D       ObjDraw_00     1x1 Large boulder rotation 2 
2E90: 36 C4 00 01 ; 1E       ObjDraw_00     1x1 Large boulder rotation 1 (x flip and y flip)
2E94: 36 44 00 01 ; 1F       ObjDraw_00     1x1 Large boulder rotation 1 (x flip)
2E98: 37 C4 00 01 ; 20       ObjDraw_00     1x1 Large boulder rotation 2 (x flip and y flip)
;
2E9C: 38 09 00 01 ; 21       ObjDraw_00     1x1 Tank
2EA0: 39 00 00 01 ; 22       ObjDraw_00     1x1 Tank shot 
;
2EA4: 3A 09 02 02 ; 23       ObjDraw_01     2x1 Hover craft (no boost)
2EA8: 05 00 2C 01 ; 24       ObjDraw_16     1x1 Buggy wheel (large) that bounces away in a crash
2EAC: 3D 0A 28 01 ; 25       ObjDraw_14     1x1 Ground mine
;
2EB0: 3E 01 00 01 ; 26       ObjDraw_00     1x1 Exploding rock 1
2EB4: 3F 01 00 01 ; 27       ObjDraw_00     1x1 Exploding rock 2
2EB8: 40 01 00 01 ; 28       ObjDraw_00     1x1 Exploding rock 3
2EBC: 41 01 00 01 ; 29       ObjDraw_00     1x1 Exploding rock 4
;
2EC0: 42 07 1A 80 ; 2A       ObjDraw_0D     1x1 Fin alien
;
2EC4: 45 07 1A 80 ; 2B       ObjDraw_0D     1x1 Saucer alien rotation 1 
2EC8: 46 07 1A 80 ; 2C       ObjDraw_0D     1x1 Saucer alien rotation 2
2ECC: 47 07 1A 80 ; 2D       ObjDraw_0D     1x1 Saucer alien rotation 3
2ED0: 47 47 1A 80 ; 2E       ObjDraw_0D     1x1 Saucer alien rotation 3 (flip x)
2ED4: 46 47 1A 80 ; 2F       ObjDraw_0D     1x1 Saucer alien rotation 2 (flip x)
2ED8: 45 47 1A 80 ; 30       ObjDraw_0D     1x1 Saucer alien rotation 1 (flip x)
;
2EDC: 43 07 1A 01 ; 31       ObjDraw_0D     1x1 Bubble alien rotation 1 
2EE0: 44 07 1A 01 ; 32       ObjDraw_0D     1x1 Bubble alien rotation 2
2EE4: 43 87 1A 01 ; 33       ObjDraw_0D     1x1 Bubble alien rotation 1 (flip y)
2EE8: 44 47 1A 01 ; 34       ObjDraw_0D     1x1 Bubble alien rotation 2 (flip x)
; 
2EEC: 00 00 00 00 ; 35
2EF0: 00 00 00 00 ; 36
;
2EF4: 48 01 1A 80 ; 37       ObjDraw_0D     1x1 Alien explosion 1
2EF8: 49 01 1A 80 ; 38       ObjDraw_0D     1x1 Alien explosion 2
2EFC: 4A 01 1A 80 ; 39       ObjDraw_0D     1x1 Alien explosion 3
;
2F00: 35 0A 2A 80 ; 3A       ObjDraw_15     1x1 Bubble alien shot
;
2F04: 4B 01 1A 80 ; 3B       ObjDraw_0D     1x1 Alien shot roll 1 
2F08: 4C 01 1A 80 ; 3C       ObjDraw_0D     1x1 Alien shot roll 2
2F0C: 4D 01 1A 80 ; 3D       ObjDraw_0D     1x1 Alien shot roll done
;
2F10: 4E 01 00 C0 ; 3E       ObjDraw_00     1x1 Bubble alien shot open crater 1
2F14: 4F 01 10 C0 ; 3F       ObjDraw_08     2x2 Bubble alien shot open crater 2 
2F18: 53 01 10 C0 ; 40       ObjDraw_08     2x2 Bubble alien shot open crater 3
2F1C: 57 01 10 C0 ; 41       ObjDraw_08     2x2 Bubble alien shot open crater 4
2F20: 5B 01 12 C0 ; 42       ObjDraw_09     2x3 Bubble alien shot open crater 5

2F24: 61 03 1E C0 ; 43       ObjDraw_0F     1x1 Alien shot hitting ground 1
2F28: 62 03 1E C0 ; 44       ObjDraw_0F     1x1 Alien shot hitting ground 2
2F2C: 63 03 1E C0 ; 45       ObjDraw_0F     1x1 Alien shot hitting ground 3
2F30: 64 03 14 C0 ; 46       ObjDraw_0A     2x2 Alien shot hitting ground 4
2F34: 68 03 14 C0 ; 47       ObjDraw_0A     2x2 Alien shot hitting ground 5
;
2F38: 6C 03 16 C0 ; 48       ObjDraw_0B     1x2 ?? Rubble 1
2F3C: 6E 03 16 C0 ; 49       ObjDraw_0F     1x2 ?? Rubble 2
;
2F40: 78 08 22 02 ; 4A       ObjDraw_11     2x1 Space plant base 3
2F44: 70 02 04 04 ; 4B       ObjDraw_02     1x1 Space plant leaf 1
2F48: 73 02 06 04 ; 4C       ObjDraw_03     1x1 Space plant leaf 2
2F4C: 74 02 18 04 ; 4D       ObjDraw_0C     1x1 Space plant leaf 3
2F50: 75 02 20 04 ; 4E       ObjDraw_10     1x1 Space plant leaf 4
;
2F54: 7A 01 1A 80 ; 4F       ObjDraw_0D     1x1 Shot hitting shot explosion 
;
2F58: 4B 41 1A 80 ; 50       ObjDraw_0D     1x1 Alien shot roll 1 (flip x) 
2F5C: 4C 41 1A 80 ; 51       ObjDraw_0D     1x1 Alien shot roll 2 (flip x)
;
2F60: 7B 09 26 02 ; 52       ObjDraw_13     1x1 Hover craft full boost back 
;
2F64: 07 00 2C 01 ; 53       ObjDraw_16     1x1 Buggy wheel (small) that bounces away in a crash
;
2F68: 7D 0E 2E 01 ; 54       ObjDraw_17     1x1 "500" graphic
; 
2F6C: 00 00 00 00 ; 55
2F70: 00 00 00 00 ; 56
2F74: 00 00 00 00 ; 57
2F78: 00 00 00 00 ; 58
2F7C: 00 00 00 00 ; 59
2F80: 00 00 00 00 ; 5A
2F84: 00 00 00 00 ; 5B
2F88: 00 00 00 00 ; 5C
2F8C: 00 00 00 00 ; 5D
2F90: 00 00 00 00 ; 5E
2F94: 00 00 00 00 ; 5F
2F98: 00 00 00 00 ; 60
2F9C: 00 00 00 00 ; 61
2FA0: 00 00 00 00 ; 62
2FA4: 00 00 00 00 ; 63
2FA8: 00 00 00 00 ; 64
2FAC: 00 00 00 00 ; 65
2FB0: 00 00 00 00 ; 66
2FB4: 00 00 00 00 ; 67
2FB8: 00 00 00 00 ; 68
2FBC: 00 00 00 00 ; 69
2FC0: 00 00 00 00 ; 6A
2FC4: 00 00 00 00 ; 6B
2FC8: 00 00 00 00 ; 6C
2FCC: 00 00 00 00 ; 6D
2FD0: 00 00 00 00 ; 6E
2FD4: 00 00 00 00 ; 6F
2FD8: 00 00 00 00 ; 70
2FDC: 00 00 00 00 ; 71
2FE0: 00 00 00 00 ; 72
2FE4: 00 00 00 00 ; 73
2FE8: 00 00 00 00 ; 74
2FEC: 00 00 00 00 ; 75
2FF0: 00 00 00 00 ; 76
2FF4: 00 00 00 00 ; 77
2FF8: 00 00 00 00 ; 78
 
2FFC: 00 00 00

2FFF: A3 01 02 02 03 03 04 04 05 60 01 58 01 
300C: 50 01 48 01 40 01 38 01 39 10 39 20 39 30 39 48 
301C: 39 60 39 70 39 80 39 98 39 B0 39 D0 B4 38 FF 58 
302C: 8E 28 B4 38 00 19 24 2C 33 39 3E 43 48 4C 50 54 
303C: 58 5B 5F 62 65 68 6B 6E 71 74 77 79 7C 7E 50 5E 
304C: 6B 87 87 A2 A2 A3 02 00 A4 A5 02 00 A6 A7 02 A8 
305C: A9 01 AA 02 AB AC AD 02 00 AE AF 02 B0 B1 01 B2 
306C: B3 B4 02 00 B5 B6 B7 02 00 00 00 B8 B9 02 00 00 
307C: 00 BA 02 00 BB BC BD 02 BE BF 01 C0 C1 02 00 C2 
308C: C3 C4 02 00 00 00 C5 C6 02 00 00 00 C7 C8 02 00 
309C: C9 CA CB 02 CC 01 DA DB DC 02 00 00 F0 03 00 00 
30AC: F0 02 00 00 F0 02 DD DE DF 01 0F 04 05 0F 24 27 
30BC: 0F 43 48 11 48 4E 12 4E 53 10 63 68 13 68 6C 0F 
30CC: 6C 6D 14 6D 6E 12 6E 74 10 89 8E FF 0C 03 03 03 
30DC: 02 01 FF 3B FF 70 FC 24 B9 FF 10 FC 24 3B 01 A0 
30EC: FC 53 00 00 00 00 00 00 00 00 00 00 00 00 00 00 
30FC: 00 00 00 00 07 0A 0D 0F 11 13 15 16 18 19 1A 1B 
310C: 1D 1E 1F 20 21 22 23 24 25 26 27 28 28 28 28 28 
311C: FF 1F 01 1C 04 0C 00 24 02 1D 05 20 08 0C 04 34 
312C: 05 21 06 07 07 0C 0C 14 05 1E 08 1E 0F 0C 12 34 
313C: 02 1B 03 1A 06 10 21 42 02 1D 04 1D 08 0F 27 42 
314C: 05 20 06 20 0B 0C 2F 42 09 16 02 22 06 1C 3A 4E 
315C: 0E 19 03 26 07 1C 40 4E 12 1D 05 2A 0A 1C 47 4E 
316C: 05 20 05 26 08 0C 51 45 05 19 05 1F 11 0C 58 7F 
317C: 08 1E 04 1E 09 0C 69 00 00 1B 16 1C 17 1A 72 20 
318C: 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 
319C: 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 
31AC: 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 
31BC: 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 
31CC: 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 
31DC: 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 
31EC: 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 
31FC: 00 00 00 00 02 04 03 01 01 03 04 06 07 08 07 05 
320C: 02 04 06 08 09 0B 01 03 04 06 07 09 0A 0C 0D 0C 
321C: 0A 08 07 05 03 01 02 04 05 04 02 01 03 05 06 08 
322C: 07 05 03 02 04 06 08 0A 0B 0D 0B 09 07 05 01 02 
323C: 03 02 02 01 04 06 07 08 06 04 01 02 04 06 08 0A 
324C: 0C 0B 0A 05 02 03 07 09 0A 0C 0B 09 03 03 07 09 
325C: 09 0B 0A 0A 0A 09 08 08 07 06 06 04 04 02 04 05 
326C: 07 08 07 05 03 00 02 02 02 02 02 F8 F8 F8 F8 F8 
327C: F8 F8 02 02 02 02 02 F8 F8 F8 F8 F8 02 00 00 00 
328C: 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 
329C: 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 
32AC: 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 
32BC: 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 
32CC: 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 
32DC: 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 
32EC: 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 
32FC: 00 00 00 00  


; This is a fantastic find! The program from 3300 on is a self-contained system test 
; and interactive service mode menu. Each menu option is a small piece of code that 
; demonstrates how the hardware works ... perfect for tinkering and documenting 
; what-does-what.
;
; It does use the ISR to manage sprites and ?sounds? however. It COULD be more 
; self contained if it didn't.
```

# Service Mode

```code
ServiceMode: 
; This should really be in the first ROM bank in case there are problems with
; the other ROM banks.
;
3300: 3E FF          LD    A,$FF              ; Enable all ... * J000A
3302: D3 C0          OUT   ($C0),A            ;{-2_BKGCtrl} ... backgrounds
3304: 32 C5 E1       LD    ($E1C5),A          ; Now ISR disable all backgrounds
;
3307: 21 00 E1       LD    HL,$E100           ; Clear 208 bytes ...
330A: 36 00          LD    (HL),$00           ; ... sprite ...
330C: 54             LD    D,H                ; ... info ...
330D: 5D             LD    E,L                ; ... copied to ...
330E: 13             INC   DE                 ; ... hardware by ...
330F: 01 CF 00       LD    BC,$00CF           ; ... ISR from ...
3312: ED B0          LDIR                     ; ... E100 .. E1CF

; 1st RAM test:
; Walk value  00000001 through all of RAM.
; Repeat with 00000010 through all of RAM.
; Continue with every bit.
;
3314: 3E 01          LD    A,$01              ; Start with bit 0
3316: 57             LD    D,A                ; Hold bit pattern in D * J332C
3317: 01 00 08       LD    BC,$0800           ; All of RAM ... 2K
331A: 21 00 E0       LD    HL,$E000           ; Start of RAM
331D: 7A             LD    A,D                ; Store bit to ... * J3328
331E: 77             LD    (HL),A             ; ... RAM
331F: 5E             LD    E,(HL)             ; Did we write the bit ...
3320: BB             CP    E                  ; ... correctly?
3321: C2 BB 34       JP    NZ,$34BB           ;{BadRAM} No ... RAM error
3324: 23             INC   HL                 ; Next in RAM * J3534
3325: 0B             DEC   BC                 ; Decrement the count
3326: 79             LD    A,C                ; More to ...
3327: B0             OR    B                  ; ... do?
3328: 20 F3          JR    NZ,$331D           ; Yes ... write bit through all of RAM
332A: 7A             LD    A,D                ; Current bit pattern
332B: 07             RLCA                     ; Next bit to the left
332C: 30 E8          JR    NC,$3316           ; Go back for all 8 bits

; 2nd RAM test:
; Write incrementing values through all of RAM. Write 01010101 through 10101010
; and wrap back to 01010101 all through RAM. Then repeat the whole thing but with
; an incremented start value 01010110. Continue to repeat with incremented start
; value until value reaches 10101010.
;
332E: 16 55          LD    D,$55              ; Alternating bits 01010101
3330: 7A             LD    A,D                ; Hold bit pattern in D * J3368
3331: 01 00 08       LD    BC,$0800           ; All of RAM ... 2K
3334: 21 00 E0       LD    HL,$E000           ; Start of RAM
3337: 77             LD    (HL),A             ; Store pattern to RAM * J3343,J3347
3338: 23             INC   HL                 ; Next in RAM
3339: 3C             INC   A                  ; Next bit pattern value
333A: 5F             LD    E,A                ; Hold the pattern
333B: 0B             DEC   BC                 ; Count down
333C: 79             LD    A,C                ; Count reached ...
333D: B0             OR    B                  ; ... zero?
333E: 28 09          JR    Z,$3349            ; Yes ... done
3340: 7B             LD    A,E                ; Next pattern we will write
3341: FE AB          CP    $AB                ; Value reached 10101010 +1?
3343: 20 F2          JR    NZ,$3337           ; No ... keep trying a different pattern
3345: 3E 55          LD    A,$55              ; Restart with 01010101
3347: 18 EE          JR    $3337              ; Keep going
;
3349: 7A             LD    A,D                ; Starting value again * J333E
334A: 01 00 08       LD    BC,$0800           ; All of RAM ... 2K
334D: 21 00 E0       LD    HL,$E000           ; Back to the start of RAM
3350: BE             CP    (HL)               ; Do we read what we wrote? * J335E,J3362
3351: 20 19          JR    NZ,$336C           ; No ... show the error
3353: 23             INC   HL                 ; Next in RAM * J3373
3354: 3C             INC   A                  ; Next value to write
3355: 5F             LD    E,A                ; Hold it
3356: 0B             DEC   BC                 ; Count down
3357: 79             LD    A,C                ; Count reached ...
3358: B0             OR    B                  ; ... zero?
3359: 28 09          JR    Z,$3364            ; Yes ... start again
335B: 7B             LD    A,E                ; Next pattern we will write
335C: FE AB          CP    $AB                ; Value reached 10101010 +1?
335E: 20 F0          JR    NZ,$3350           ; No ... keep trying a different pattern
3360: 3E 55          LD    A,$55              ; Restart with 01010101
3362: 18 EC          JR    $3350              ; Do all of RAM
;
3364: 14             INC   D                  ; Next starting point * J3359
3365: 7A             LD    A,D                ; Have we reached ...
3366: FE AB          CP    $AB                ; ... end of patterns?
3368: 20 C6          JR    NZ,$3330           ; No ... do all of RAM starting here
336A: 18 09          JR    $3375              ; Looks like general purpose RAM is OK
;
336C: 5E             LD    E,(HL)             ; What we read * J3351
336D: 57             LD    D,A                ; What we expected
336E: AF             XOR   A                  ; Tell error-print where to come back to when START-1 is pressed
336F: C3 BB 34       JP    $34BB              ;{BadRAM} Go show the error
;
3372: 7A             LD    A,D                ; When restarted after message, put current back to D * J3531
3373: 18 DE          JR    $3353              ; Continue with loop

3375: 31 00 E8       LD    SP,$E800           ; RAM is OK ... we can call routines and use RAM variables * J336A
3378: 3E 01          LD    A,$01              ; Same bit walk we did above
337A: 57             LD    D,A                ; ...  * J3397
337B: 01 00 08       LD    BC,$0800           ; ... 
337E: 21 00 80       LD    HL,$8000           ; ... 
3381: 7A             LD    A,D                ; ...  * J3393
3382: 77             LD    (HL),A             ; ... 
3383: 5E             LD    E,(HL)             ; ...
3384: BB             CP    E                  ; ...
3385: 28 08          JR    Z,$338F            ; ...
3387: CD 3B 35       CALL  $353B              ; Print error
338A: CB 4F          BIT   1,A                ; START-2 pressed?
338C: CA F5 33       JP    Z,$33F5            ; Yes ... skip past RAM test
338F: 23             INC   HL                 ; ... * J3385
3390: 0B             DEC   BC                 ; ...
3391: 79             LD    A,C                ; ...
3392: B0             OR    B                  ; ...
3393: 20 EC          JR    NZ,$3381           ; ...
;
3395: 7A             LD    A,D                ; ...
3396: 07             RLCA                     ; ...
3397: 30 E1          JR    NC,$337A           ; Same bit walk we did above

3399: 16 55          LD    D,$55              ; ...
339B: 7A             LD    A,D                ; ... * J33D3
339C: 01 00 08       LD    BC,$0800           ; ...
339F: 21 00 80       LD    HL,$8000           ; ...
33A2: 77             LD    (HL),A             ; ... * J33AE,J33B2
33A3: 23             INC   HL                 ; ...
33A4: 3C             INC   A                  ; ...
33A5: 5F             LD    E,A                ; ...
33A6: 0B             DEC   BC                 ; ...
33A7: 79             LD    A,C                ; ...
33A8: B0             OR    B                  ; ...
33A9: 28 09          JR    Z,$33B4            ; ...
33AB: 7B             LD    A,E                ; ...
33AC: FE AB          CP    $AB                ; ...
33AE: 20 F2          JR    NZ,$33A2           ; ...
33B0: 3E 55          LD    A,$55              ; ...
33B2: 18 EE          JR    $33A2              ; ...
33B4: 7A             LD    A,D                ; ... * J33A9
33B5: 01 00 08       LD    BC,$0800           ; ...
33B8: 21 00 80       LD    HL,$8000           ; ...
33BB: BE             CP    (HL)               ; ... * J33C9,J33CD
33BC: 20 19          JR    NZ,$33D7           ; Error out here
33BE: 23             INC   HL                 ; ... * J33E2
33BF: 3C             INC   A                  ; ...
33C0: 5F             LD    E,A                ; ...
33C1: 0B             DEC   BC                 ; ...
33C2: 79             LD    A,C                ; ...
33C3: B0             OR    B                  ; ...
33C4: 28 09          JR    Z,$33CF            ; ...
33C6: 7B             LD    A,E                ; ...
33C7: FE AB          CP    $AB                ; ...
33C9: 20 F0          JR    NZ,$33BB           ; ...
33CB: 3E 55          LD    A,$55              ; ...
33CD: 18 EC          JR    $33BB              ; ...
33CF: 14             INC   D                  ; ... * J33C4
33D0: 7A             LD    A,D                ; ...
33D1: FE AB          CP    $AB                ; ...
33D3: 20 C6          JR    NZ,$339B           ; ...
33D5: 18 0D          JR    $33E4              ; ...

33D7: 5E             LD    E,(HL)             ; Value read to E * J33BC
33D8: 57             LD    D,A                ; Expected value to D
33D9: CD 37 35       CALL  $3537              ; Print error
33DC: CB 4F          BIT   1,A                ; START-2 pressed?
33DE: CA F5 33       JP    Z,$33F5            ; Yes ... skip past RAM test
33E1: 7A             LD    A,D                ; Restore expected
33E2: 18 DA          JR    $33BE              ; Back to loop

33E4: DD 21 EB 33    LD    IX,$33EB           ; Next line (reuse existing routine) * J33D5
33E8: C3 B1 35       JP    $35B1              ;{ClearVideo} Clear the screen
33EB: 21 66 3A       LD    HL,$3A66           ; "RAM  OK" message
33EE: DD 21 F5 33    LD    IX,$33F5           ; Next line (reuse existing routine)
33F2: C3 65 34       JP    $3465              ;{MultiCopy} Print RAM is OK

33F5: 21 00 E1       LD    HL,$E100           ; Clear ... * J338C,J33DE,J352C
33F8: 36 00          LD    (HL),$00           ; ... E100 ...
33FA: 54             LD    D,H                ; ... through ...
33FB: 5D             LD    E,L                ; ... E1CF ...
33FC: 13             INC   DE                 ; ...
33FD: 01 CF 00       LD    BC,$00CF           ; ... (Sprites RAM Copy)
3400: ED B0          LDIR                     ; ...
3402: 21 00 00       LD    HL,$0000           ; Start of ROM
3405: AF             XOR   A                  ; Start with ...
3406: 32 00 E7       LD    ($E700),A          ; .. chip 0 * J3420
3409: 06 00          LD    B,$00              ; 256 bytes
340B: 0E 10          LD    C,$10              ; 256*16 = 4K (per chip)
340D: AF             XOR   A                  ; Zero out A (accumulated XOR)
340E: AE             XOR   (HL)               ; XOR accumulate byte * J3410,J3413
340F: 23             INC   HL                 ; Do ...
3410: 10 FC          DJNZ  $340E              ; ... all 256
3412: 0D             DEC   C                  ; Do ...
3413: 20 F9          JR    NZ,$340E           ; ... all 4K
;
3415: E5             PUSH  HL                 ; Hold our ROM pointer
3416: CD 35 34       CALL  $3435              ;{ROMReport} Print report
3419: E1             POP   HL                 ; Restore ROM pointer
341A: 3A 00 E7       LD    A,($E700)          ; Chip number
341D: 3C             INC   A                  ; Next chip
341E: FE 04          CP    $04                ; Done all 4 chips?
3420: 20 E4          JR    NZ,$3406           ; No ... go back for all 4

3422: AF             XOR   A                  ; ??
3423: D3 1C          OUT   ($1C),A            ;{-2_SCROLLC} ?? Clear Scroll register 0C ??
3425: FB             EI                       ; ??
3426: 3A 00 D0       LD    A,($D000)          ;{-2_IN0} Read inputs * J342B
3429: CB 4F          BIT   1,A                ; START-2 pressed?
342B: 20 F9          JR    NZ,$3426           ; No ... wait for it
342D: 3E 03          LD    A,$03              ; 3 means first row of options
342F: 32 01 E7       LD    ($E701),A          ;{-1_menuRow} Start menu on 1st row
3432: C3 CD 35       JP    $35CD              ;{ServiceMenu} Continue with interactive menu

ROMReport:
;
; Print "ROMn  ss  xx" on correct row (skip a row between)
; Where n is chip number 0-3 from E700.
; Where ss is OK or NG (not good)
; Where xx is XOR accumulate (should be FF) from A
;
3435: F5             PUSH  AF                 ; Hold registers * C3416
3436: FE FF          CP    $FF                ; XOR work out to be FF?
3438: 28 02          JR    Z,$343C            ; Yes ... leave C as 00 (ROM___OK)
343A: 0E 08          LD    C,$08              ; No ... offset to (ROM___NG)
343C: 21 86 3A       LD    HL,$3A86           ; OK message * J3438
343F: 09             ADD   HL,BC              ; Offset if not OK
3440: EB             EX    DE,HL              ; Data pointer in DE
3441: 3A 00 E7       LD    A,($E700)          ; Chip number
3444: 0F             RRCA                     ; Shift left 6 ...
3445: 0F             RRCA                     ; ... which is *64 (two rows)
3446: 4F             LD    C,A                ; B remains 0 ... row offset to BC
3447: 21 C4 80       LD    HL,$80C4           ; Screen location
344A: 09             ADD   HL,BC              ; Add row offset
344B: E5             PUSH  HL                 ; Hold location
344C: EB             EX    DE,HL              ; HL points to data, DE to screen
344D: 0E 08          LD    C,$08              ; 8 bytes
344F: ED B0          LDIR                     ; Copy OK or NG message to screen
3451: 13             INC   DE                 ; Skip 2 ...
3452: 13             INC   DE                 ; .. on screen
3453: D5             PUSH  DE                 ; Screen ...
3454: FD E1          POP   IY                 ; ... to IY
3456: DD E1          POP   IX                 ; Screen location to IX
3458: F1             POP   AF                 ; Restore registers
3459: CD 9A 34       CALL  $349A              ;{PrintHex} Print checksum to screen at IY
345C: 3A 00 E7       LD    A,($E700)          ; Chip number
345F: C6 30          ADD   $30                ; Offset to ASCII
3461: DD 77 03       LD    (IX+$03),A         ; Print bank number on screen
3464: C9             RET                      ; Done

MultiCopy:
; Do multiple block copies.
; Each copy begins is defined by a size byte, a two byte destination, and the data. Blocks
; are defined in memory right after one another. A size of "0" ends the sequence.
;
3465: 7E             LD    A,(HL)             ; Get count * J33F2,J3474,J34CB,J3563
3466: 23             INC   HL                 ; Point to destination
3467: FE 00          CP    $00                ; Length is 0?
3469: 28 0B          JR    Z,$3476            ; Yes ... out
346B: 5E             LD    E,(HL)             ; Get ...
346C: 23             INC   HL                 ; ... destination ...
346D: 56             LD    D,(HL)             ; ... to DE
346E: 23             INC   HL                 ; Point to data
346F: 4F             LD    C,A                ; Count to C
3470: 06 00          LD    B,$00              ; MSB of count is 0
3472: ED B0          LDIR                     ; Copy the data
3474: 18 EF          JR    $3465              ;{MultiCopy} Do next copy
3476: DD E9          JP    (IX)               ; Return * J3469

PrintUpperHex:
; Print one digit hex value from upper nibble of A to screen at IY
;
3478: 0F             RRCA                     ; Isolate ... * J34D8,J34EC,J3500,J3514
3479: 0F             RRCA                     ; ... the ...
347A: 0F             RRCA                     ; ... upper ...
347B: 0F             RRCA                     ; ... nibble ...
347C: E6 0F          AND   $0F                ; ... value
347E: C6 30          ADD   $30                ; Add to ASCII '0'
3480: FE 3A          CP    $3A                ; Is this a number?
3482: 38 02          JR    C,$3486            ; Yes ... keep what we have
3484: C6 07          ADD   $07                ; Further offset to letters
3486: FD 77 00       LD    (IY+$00),A         ; Put digit on screen * J3482
3489: DD E9          JP    (IX)               ; Return

PrintLowerHex:
; Print one digit hex value from lower nibble of A to screen at IY+1
;
348B: E6 0F          AND   $0F                ; Isolate the lower nibble * J34E0,J34F4,J3508,J351C
348D: C6 30          ADD   $30                ; Add to ASCII '0'
348F: FE 3A          CP    $3A                ; Is this a number?
3491: 38 02          JR    C,$3495            ; Yes ... keep what we have
3493: C6 07          ADD   $07                ; Further offset to letters
3495: FD 77 01       LD    (IY+$01),A         ; Put the digit on screen * J3491
3498: DD E9          JP    (IX)               ; Return

PrintHex:
; Print two digit hex value from A to screen at IY and IY+1
;
349A: F5             PUSH  AF                 ; Hold the value * C3459,C356C,C3574,C357C,C3584
349B: 0F             RRCA                     ; Isolate ...
349C: 0F             RRCA                     ; ... the ...
349D: 0F             RRCA                     ; ... upper ...
349E: 0F             RRCA                     ; ... nibble ...
349F: E6 0F          AND   $0F                ; ... value
34A1: C6 30          ADD   $30                ; ... Add to ASCII '0'
34A3: FE 3A          CP    $3A                ; Is this a number?
34A5: 38 02          JR    C,$34A9            ; Yes ... keep what we have
34A7: C6 07          ADD   $07                ; Further offset to letters
34A9: FD 77 00       LD    (IY+$00),A         ; Put the digit on the screen * J34A5
34AC: F1             POP   AF                 ; Restore value
34AD: E6 0F          AND   $0F                ; Isolate the lower nibble
34AF: C6 30          ADD   $30                ; Add to ASCII '0'
34B1: FE 3A          CP    $3A                ; Is this a number?
34B3: 38 02          JR    C,$34B7            ; Yes ... keep what we have
34B5: C6 07          ADD   $07                ; Further offset to letters
34B7: FD 77 01       LD    (IY+$01),A         ; Put the digit on the screen * J34B3
34BA: C9             RET                      ; Done

BadRAM:
;
; Print "RAM___NG__:hhll:  dd  ee"
; The return to RAM test when START1 is pressed or go to ROM test
; when START2 is pressed.
;
; HL = RAM address
;  D = Value written
;  E = Value read
;
34BB: 08             EX    AF,AF'             ; Hold status where ... * J3321,J336F
34BC: D9             EXX                      ; ... error happened
34BD: DD 21 C4 34    LD    IX,$34C4           ; Return to next code
34C1: C3 B1 35       JP    $35B1              ;{ClearVideo} Clear the video and color RAM
;
34C4: 21 72 3A       LD    HL,$3A72           ; "RAM___NG__:____:" Message
34C7: DD 21 CE 34    LD    IX,$34CE           ; Return to next line (don't trust RAM)
34CB: C3 65 34       JP    $3465              ;{MultiCopy} Print the message
;
34CE: D9             EXX                      ; Restore status of where error happened
34CF: FD 21 8F 80    LD    IY,$808F           ; Screen location for number
34D3: DD 21 DB 34    LD    IX,$34DB           ; Return to next line (don't trust RAM)
34D7: 7C             LD    A,H                ; H=MSB of RAM failure
34D8: C3 78 34       JP    $3478              ;{PrintUpperHex} Print the upper nibble of A
;
34DB: DD 21 E3 34    LD    IX,$34E3           ; Return to next line (don't trust RAM)
34DF: 7C             LD    A,H                ; H=MSB of RAM failure
34E0: C3 8B 34       JP    $348B              ;{PrintLowerHex} Print the lower nibble of A
;
34E3: FD 23          INC   IY                 ; Next digit ...
34E5: FD 23          INC   IY                 ; ... on screen
34E7: DD 21 EF 34    LD    IX,$34EF           ; Return to next line (don't trust RAM)
34EB: 7D             LD    A,L                ; L=LSB of RAM failure
34EC: C3 78 34       JP    $3478              ;{PrintUpperHex} Print the upper nibble of A
;
34EF: DD 21 F7 34    LD    IX,$34F7           ; Return to next line (don't trust RAM)
34F3: 7D             LD    A,L                ; L=LSB of RAM failure
34F4: C3 8B 34       JP    $348B              ;{PrintLowerHex} Print the lower nibble of A
;
34F7: FD 21 95 80    LD    IY,$8095           ; Location on screen
34FB: DD 21 03 35    LD    IX,$3503           ; Return to next line (don't trust RAM)
34FF: 7A             LD    A,D                ; D=Value written
3500: C3 78 34       JP    $3478              ;{PrintUpperHex} Print the upper nibble of A
;
3503: DD 21 0B 35    LD    IX,$350B           ; Return to next line (don't trust RAM)
3507: 7A             LD    A,D                ; D=Value written
3508: C3 8B 34       JP    $348B              ;{PrintLowerHex} Print the lower nibble of A
;
350B: FD 21 99 80    LD    IY,$8099           ; Location on screen
350F: DD 21 17 35    LD    IX,$3517           ; Return to next line (don't trust RAM)
3513: 7B             LD    A,E                ; E=Value read
3514: C3 78 34       JP    $3478              ;{PrintUpperHex} Print the upper nibble of A
;
3517: 7B             LD    A,E                ; E=Value read
3518: DD 21 1F 35    LD    IX,$351F           ; Return to next line (don't trust RAM)
351C: C3 8B 34       JP    $348B              ;{PrintLowerHex} Print the lower nibble of A
;
351F: 3A 00 D0       LD    A,($D000)          ;{-2_IN0} Is START 1 ... * J3529
3522: CB 47          BIT   0,A                ; ... pressed?
3524: CA 2F 35       JP    Z,$352F            ; Yes ... continue RAM test
3527: CB 4F          BIT   1,A                ; Is START 2 pressed?
3529: 20 F4          JR    NZ,$351F           ; No ... wait for one of them
;
352B: 08             EX    AF,AF'             ; Swap back the AF (others already swapped)
352C: C3 F5 33       JP    $33F5              ; Go to ROM test
;
352F: 08             EX    AF,AF'             ; Swap back the AF (others already swapped) * J3524
3530: B7             OR    A                  ; Is A a 00?
3531: CA 72 33       JP    Z,$3372            ; Yes ... return to SET VALUE test
3534: C3 24 33       JP    $3324              ; No ... return to WALKING BIT test

3537: E5             PUSH  HL                 ; Hold RAM pointer * C33D9
3538: D9             EXX                      ; Preserve error state
3539: 18 09          JR    $3544              ; Do error and return when button pressed
;
353B: E5             PUSH  HL                 ; Hold RAM pointer * C3387
353C: D9             EXX                      ; Preserve error state
353D: DD 21 44 35    LD    IX,$3544           ; Return to next line
3541: C3 B1 35       JP    $35B1              ;{ClearVideo} Clear video
;
3544: 21 00 80       LD    HL,$8000           ; From video RAM * J3539
3547: 11 00 E0       LD    DE,$E000           ; To RAM
354A: 01 A0 04       LD    BC,$04A0           ; All of visible screen
354D: ED B0          LDIR                     ; Copy screen to RAM (we must put back to continue later)
354F: 21 00 80       LD    HL,$8000           ; Start of screen
3552: 36 00          LD    (HL),$00           ; Put in a zero
3554: 54             LD    D,H                ; Destination is ...
3555: 5D             LD    E,L                ; ... one ...
3556: 13             INC   DE                 ; ... past
3557: 01 9F 04       LD    BC,$049F           ; Count ... all of visible screen
355A: ED B0          LDIR                     ; Clear the screen
355C: 21 72 3A       LD    HL,$3A72           ; "RAM___NG__:____:" Message
355F: DD 21 66 35    LD    IX,$3566           ; Next line (reuse existing routine)
3563: C3 65 34       JP    $3465              ;{MultiCopy} Print the message
;
3566: D9             EXX                      ; Restore error state
3567: FD 21 8F 80    LD    IY,$808F           ; Screen location
356B: 7C             LD    A,H                ; MSB of RAM fail to A
356C: CD 9A 34       CALL  $349A              ;{PrintHex} Print MSB of RAM fail
356F: FD 23          INC   IY                 ; Next ...
3571: FD 23          INC   IY                 ; ... on screen
3573: 7D             LD    A,L                ; LSB of RAM fail to A
3574: CD 9A 34       CALL  $349A              ;{PrintHex} Print LSB of RAM fail
3577: FD 21 95 80    LD    IY,$8095           ; Screen location
357B: 7A             LD    A,D                ; Expected value
357C: CD 9A 34       CALL  $349A              ;{PrintHex} Print expected value
357F: FD 21 99 80    LD    IY,$8099           ; Screen location
3583: 7B             LD    A,E                ; Actual value
3584: CD 9A 34       CALL  $349A              ;{PrintHex} Print the actual value
3587: E1             POP   HL                 ; Restore HL
3588: 3A 00 D0       LD    A,($D000)          ;{-2_IN0} Read input * J3593
358B: CB 47          BIT   0,A                ; START-1 pressed?
358D: 28 06          JR    Z,$3595            ; Yes ... out
358F: CB 4F          BIT   1,A                ; START-2 pressed?
3591: 28 10          JR    Z,$35A3            ; Yes ... out
3593: 18 F3          JR    $3588              ; Wait for something to be pressed
;
3595: D9             EXX                      ; Hold registers * J358D
3596: 21 00 E0       LD    HL,$E000           ; Copy ...
3599: 11 00 80       LD    DE,$8000           ; ... RAM ...
359C: 01 A0 04       LD    BC,$04A0           ; ... back to ...
359F: ED B0          LDIR                     ; ... screen memory
35A1: D9             EXX                      ; Restore registers
35A2: C9             RET                      ; Done
;
35A3: 21 A0 84       LD    HL,$84A0           ; Clear A4A0 .. 87FF (part of color RAM) * J3591
35A6: 36 00          LD    (HL),$00           ; ...
35A8: 54             LD    D,H                ; ...
35A9: 5D             LD    E,L                ; ...
35AA: 13             INC   DE                 ; ...
35AB: 01 5F 03       LD    BC,$035F           ; ...
35AE: ED B0          LDIR                     ; ...
35B0: C9             RET                      ; Back to vid-ram test

ClearVideo:
; Clear the screen and color RAM. Use IX as the return
; address (don't trust RAM)
35B1: 21 00 84       LD    HL,$8400           ; Clear ... * J33E8,J34C1,J3541
35B4: 01 FF 03       LD    BC,$03FF           ; ... Color ...
35B7: 36 00          LD    (HL),$00           ; ... RAM ...
35B9: 54             LD    D,H                ; ... 8400-87FF
35BA: 5D             LD    E,L                ; ...
35BB: 13             INC   DE                 ; ...
35BC: ED B0          LDIR                     ; ...
35BE: 21 00 80       LD    HL,$8000           ; Clear ...
35C1: 01 FF 03       LD    BC,$03FF           ; ... Video ...
35C4: 36 00          LD    (HL),$00           ; ... RAM ...
35C6: 54             LD    D,H                ; ... 8000-83FF
35C7: 5D             LD    E,L                ; ...
35C8: 13             INC   DE                 ; ...
35C9: ED B0          LDIR                     ; ...
35CB: DD E9          JP    (IX)               ; ... RAM is bad ... use IX as return
```

# Service Menu

```code
ServiceMenu: 
;
; Interactive service menu
; E701 tracks the row number (3 is the top)
;
35CD: CD AD 38       CALL  $38AD              ;{ClearScreen} Clear screen and color memory * J3432,J36AF,J3777,J37BD,J3993,J39A6,J3A63
35D0: 21 BF 3E       LD    HL,$3EBF           ; Print the six rows ...
35D3: CD 08 39       CALL  $3908              ;{MultiCopyToRAM} ... of options
35D6: 3A 01 E7       LD    A,($E701)          ;{-1_menuRow} Current row pointer
35D9: 06 02          LD    B,$02              ; Color value of 2
35DB: CD 1C 39       CALL  $391C              ;{MenuColor} Highlight the selected option
35DE: 3A 00 D0       LD    A,($D000)          ;{-2_IN0} Is start-1 ... * J360E,J361F,J3630
35E1: CB 47          BIT   0,A                ; ... pressed?
35E3: 20 14          JR    NZ,$35F9           ; No ... skip to Left/Right check
;
35E5: 3A 01 E7       LD    A,($E701)          ;{-1_menuRow} Row number (3 is first)
35E8: 07             RLCA                     ; *2
35E9: 4F             LD    C,A                ; rowNumber*2 ...
35EA: 06 00          LD    B,$00              ; ... to BC
35EC: DD 21 96 3A    LD    IX,$3A96           ; Routine table
35F0: DD 09          ADD   IX,BC              ; Point to routine entry
35F2: DD 6E 00       LD    L,(IX+$00)         ; Get ...
35F5: DD 66 01       LD    H,(IX+$01)         ; ... address
35F8: E9             JP    (HL)               ; Jump to routine
;
35F9: DD 21 02 E7    LD    IX,$E702           ; Scratch area for menu motion * J35E3
35FD: CD DD 38       CALL  $38DD              ; Get L/R and long debounce (can hold down)
3600: 47             LD    B,A                ; Hold the value for later use
3601: E6 55          AND   $55                ; 01010101 ... only left bit
3603: FE 55          CP    $55                ; Down (left) held down 4 times?
3605: 28 09          JR    Z,$3610            ; Yes ... do menu down
3607: 78             LD    A,B                ; Get original value back
3608: E6 AA          AND   $AA                ; 10101010 ... only right bit
360A: FE AA          CP    $AA                ; Up (right) held down 4 times?
360C: 28 13          JR    Z,$3621            ; Yes ... do menu up
360E: 18 CE          JR    $35DE              ; Back to top to wait on button
;
; Down the menu
3610: DD 36 00 55    LD    (IX+$00),$55       ; Button mask * J3605
3614: DD 36 01 08    LD    (IX+$01),$08       ; Stop at row 8 ... bottom of menu
3618: DD 36 02 01    LD    (IX+$02),$01       ; Row offset (+1 ... down)
361C: CD 32 36       CALL  $3632              ; Increment row and handle shorter held-down rate
361F: 18 BD          JR    $35DE              ; Back to top to wait on button
;
; Up the menu
3621: DD 36 00 AA    LD    (IX+$00),$AA       ; Button mask * J360C
3625: DD 36 01 03    LD    (IX+$01),$03       ; Stop at row 3 ... top of menu
3629: DD 36 02 FF    LD    (IX+$02),$FF       ; Row offset (-1 ... up)
362D: CD 32 36       CALL  $3632              ; Decrement row and handle shorter held-down rate
3630: 18 AC          JR    $35DE              ; Back to top to wait on button
;
; Bump menu up or down with a shorter held-down
; advance rate.
3632: DD 56 00       LD    D,(IX+$00)         ; Button mask * C361C,C362D
3635: 1E 02          LD    E,$02              ; Wait count (outer loop)
3637: CD C8 38       CALL  $38C8              ; Wait for button to be released
363A: 28 0E          JR    Z,$364A            ; Released: Bump row (if we can) and highlight and out
363C: CD 4E 36       CALL  $364E              ; Not released: Bump row (if we can) and highlight * J3647
363F: DD 56 00       LD    D,(IX+$00)         ; Button mask
3642: 1E 01          LD    E,$01              ; Wait count (shorter for held-down repeats)
3644: CD C8 38       CALL  $38C8              ; Wait for button to be released
3647: 20 F3          JR    NZ,$363C           ; Not released ... keep bumping while held down
3649: C9             RET                      ; Done
;
364A: CD 4E 36       CALL  $364E              ; Bump row (and highlight) ... * J363A
364D: C9             RET                      ; ... if not at edge of menu
;
364E: 3A 01 E7       LD    A,($E701)          ;{-1_menuRow} Current menu row * C363C,C364A
3651: DD BE 01       CP    (IX+$01)           ; Are we at the end for this direction?
3654: C8             RET   Z                  ; Yes ... don't delta
3655: 06 00          LD    B,$00              ; Un-highlight ...
3657: CD 1C 39       CALL  $391C              ;{MenuColor} ... the current selection
365A: DD 86 02       ADD   A,(IX+$02)         ; Bump row number up or down
365D: 32 01 E7       LD    ($E701),A          ;{-1_menuRow} Store new current menu row
3660: 06 02          LD    B,$02              ; Highlight ...
3662: CD 1C 39       CALL  $391C              ;{MenuColor} ... the selection
3665: C9             RET                      ; Done

ServiceDIP:
; Service routine for "DIP SWITCH"
;
3666: CD AD 38       CALL  $38AD              ;{ClearScreen} Clear tiles and colors
3669: 21 10 3B       LD    HL,$3B10           ; DIP Switch background text
366C: CD 08 39       CALL  $3908              ;{MultiCopyToRAM} Multi copy the indicator text
366F: 3A 03 D0       LD    A,($D003)          ;{-2_DSW1} Read DIP switch 1 (lives per coin) * J36AD
3672: 21 CB 80       LD    HL,$80CB           ; Screen location
3675: CD B2 36       CALL  $36B2              ;{PrintBits} Print 8 bit status
3678: 3A 04 D0       LD    A,($D004)          ;{-2_DSW2} Read DIP switch 2 (coins, service mode)
367B: 21 0B 81       LD    HL,$810B           ; Screen location
367E: CD B2 36       CALL  $36B2              ;{PrintBits} Print 8 bit status
;
3681: DD 21 AC 3A    LD    IX,$3AAC           ; String table for ...
3685: FD 21 A8 3A    LD    IY,$3AA8           ; ... "cars" and "extend points"
3689: 3A 03 D0       LD    A,($D003)          ;{-2_DSW1} Read DIP switch 1
368C: EE FF          XOR   $FF                ; Flip to active high
368E: 06 02          LD    B,$02              ; Two bit fieds
3690: CD C6 36       CALL  $36C6              ; Print "cars" and "extended points"
;
3693: DD 21 F8 3A    LD    IX,$3AF8           ; String table for ...
3697: FD 21 F4 3A    LD    IY,$3AF4           ; ... "table" or "upright"
369B: 3A 04 D0       LD    A,($D004)          ;{-2_DSW2} Read DIP switch 2
369E: EE FF          XOR   $FF                ; Flip to active high
36A0: 06 01          LD    B,$01              ; One bit field
36A2: CD C5 36       CALL  $36C5              ; Skip bit-1 and print field
36A5: CD EC 36       CALL  $36EC              ; Print coin-mode (complicated)
;
36A8: 3A 00 D0       LD    A,($D000)          ;{-2_IN0} Start-2 button ...
36AB: CB 4F          BIT   1,A                ; ... pressed?
36AD: 20 C0          JR    NZ,$366F           ; No ... refresh DIP display
36AF: C3 CD 35       JP    $35CD              ;{ServiceMenu} Return to interactive menu
;
PrintBits:
; Print 1's or 0's for 8 bits in A to screen at HL.
36B2: EE FF          XOR   $FF                ; Reverse TTL inputs (now 1=on) * C3675,C367E,C3739,C3742,C374B
36B4: 06 08          LD    B,$08              ; 8 bits to show
36B6: 0F             RRCA                     ; Next bit to carry * J36C1
36B7: 38 04          JR    C,$36BD            ; Bit a one? Go print a one
36B9: 36 30          LD    (HL),$30           ; Print a zero
36BB: 18 02          JR    $36BF              ; Skip printing one
36BD: 36 31          LD    (HL),$31           ; Print the one * J36B7
36BF: 23             INC   HL                 ; Next ... * J36BB
36C0: 23             INC   HL                 ; ... screen location
36C1: 10 F3          DJNZ  $36B6              ; Do all 8 bits
36C3: C9             RET                      ; Done

; This method prints a string for each value of a bit-field. If the bit fields are
; two-bits then multiple fields can be printed.
;
; IY points to the string-table descriptor (pointer offset, pointer to strings)
; IX points to the mask/offset for each field
;  A the value (will be masked)
;  B number of 2-bit fields to print
;
36C4: 0F             RRCA                     ; Skip to next ... * J36E9,C371D
;
36C5: 0F             RRCA                     ; ... two-bit field * C36A2
;
36C6: 4F             LD    C,A                ; Hold value in C * C3690
36C7: C5             PUSH  BC                 ; Hold field count and value
36C8: DD A6 00       AND   (IX+$00)           ; Keep only target field
36CB: DD 86 01       ADD   A,(IX+$01)         ; Get string number
36CE: DD 23          INC   IX                 ; Next mask and ...
36D0: DD 23          INC   IX                 ; ... offset for next print (if any)
36D2: 4F             LD    C,A                ; String number A ...
36D3: 06 00          LD    B,$00              ; ... to BC
36D5: FD 6E 00       LD    L,(IY+$00)         ; Get pointer to ...
36D8: FD 66 01       LD    H,(IY+$01)         ; ... string offsets
36DB: 09             ADD   HL,BC              ; Point to the string table offset
36DC: 4E             LD    C,(HL)             ; Get the string table offset
36DD: FD 6E 02       LD    L,(IY+$02)         ; Get the ...
36E0: FD 66 03       LD    H,(IY+$03)         ; ... string table
36E3: 09             ADD   HL,BC              ; Point to the string
36E4: CD 11 39       CALL  $3911              ;{CopyToRAM} Print to screen
36E7: C1             POP   BC                 ; Restore field count
36E8: 79             LD    A,C                ; Restore value
36E9: 10 D9          DJNZ  $36C4              ; Do all fields
36EB: C9             RET                      ; Done

36EC: 3A 04 D0       LD    A,($D004)          ;{-2_DSW2} DIP switch 2 * C36A5
36EF: CB 57          BIT   2,A                ; Coin-mode bit is 0 (coin-mode B)?
36F1: CA 06 37       JP    Z,$3706            ; Yes ... go describe that
36F4: 21 77 3B       LD    HL,$3B77           ; Blank out ...
36F7: CD 08 39       CALL  $3908              ;{MultiCopyToRAM} ... the character ("COIN MODE" with no " A" on the end)
36FA: DD 21 99 3B    LD    IX,$3B99           ; Coins ...
36FE: FD 21 9B 3B    LD    IY,$3B9B           ; ... per play
3702: 06 01          LD    B,$01              ; One field
3704: 18 10          JR    $3716              ; Print coins per play
;
3706: 21 7F 3C       LD    HL,$3C7F           ; Put the "A" on the end of "COIN MODE" and then ... * J36F1
3709: CD 08 39       CALL  $3908              ;{MultiCopyToRAM} ... print "COIN MODE B" on next line.
370C: DD 21 92 3C    LD    IX,$3C92           ; Two-field table for slot A ...
3710: FD 21 96 3C    LD    IY,$3C96           ; ... and slot B
3714: 06 02          LD    B,$02              ; Two fields to print
3716: 3A 03 D0       LD    A,($D003)          ;{-2_DSW1} Get the value * J3704
3719: EE FF          XOR   $FF                ; Flip it active high
371B: 0F             RRCA                     ; Ship first ...
371C: 0F             RRCA                     ; ... two bits
371D: CD C4 36       CALL  $36C4              ; Print the coin modes (skip 2nd two bits first)
3720: C9             RET                      ; Done

ServiceIO:
; Service routine for "I_O"
; This routine displays all the bits of IN0, IN1, and IN2.
; It counts ISR ticks and bumps a 4 digit decimal counter
; every 1.1 seconds (almost once a second). Press START-1
; and START-2 to return to main menu.
;
3721: AF             XOR   A                  ; Fast 0
3722: 32 0F E7       LD    ($E70F),A          ;{-1_isrCVal} Clear ...
3725: 67             LD    H,A                ; ... the ISR BCD ...
3726: 6F             LD    L,A                ; ... counter and ...
3727: 22 0D E7       LD    ($E70D),HL         ;{-1_isrCntM} ... current timer value
;
372A: CD AD 38       CALL  $38AD              ;{ClearScreen} Clear screen tiles and colors
372D: 21 22 3D       LD    HL,$3D22           ; Print background ...
3730: CD 08 39       CALL  $3908              ;{MultiCopyToRAM} ... text for I/O display
3733: 3A 00 D0       LD    A,($D000)          ;{-2_IN0} Read IN0 (coins and starts) * J3766,J376D
3736: 21 CB 80       LD    HL,$80CB           ; Screen coordinates
3739: CD B2 36       CALL  $36B2              ;{PrintBits} Print the IN0 bits
373C: 3A 01 D0       LD    A,($D001)          ;{-2_IN1} Read IN1 (buttons, joystick)
373F: 21 0B 81       LD    HL,$810B           ; Screen coordinates
3742: CD B2 36       CALL  $36B2              ;{PrintBits} Print the IN1 bits
3745: 3A 02 D0       LD    A,($D002)          ;{-2_IN2} Read IN2 (2nd buttons, joystick in cocktail cabinet)
3748: 21 4B 81       LD    HL,$814B           ; Screen coordinates
374B: CD B2 36       CALL  $36B2              ;{PrintBits} Print the IN2 bits
;
374E: CD 8C 37       CALL  $378C              ; Bump the ISR count every 1.1 seconds.
3751: 3A 0D E7       LD    A,($E70D)          ;{-1_isrCntM} Get the MSB (2 digits) of the BCD counter
3754: 21 8C 81       LD    HL,$818C           ; Screen coordinates
3757: CD 7A 37       CALL  $377A              ;{PrintBCD2} Print BCD value
375A: 23             INC   HL                 ; Next on screen
375B: 3A 0E E7       LD    A,($E70E)          ;{-1_isrCntL} Get the LSB (2 digits) of the BCD counter
375E: CD 7A 37       CALL  $377A              ;{PrintBCD2} Print BCD value
3761: 3A 00 D0       LD    A,($D000)          ;{-2_IN0} Wait ...
3764: CB 4F          BIT   1,A                ; ... for ...
3766: 20 CB          JR    NZ,$3733           ; ... START-1 ...
3768: 3A 01 D0       LD    A,($D001)          ;{-2_IN1} ... and ...
376B: CB 4F          BIT   1,A                ; ... START-2 ...
376D: 20 C4          JR    NZ,$3733           ; ... to be down
376F: CD AD 38       CALL  $38AD              ;{ClearScreen} Clear the screen tiles and colors
3772: 3E 01          LD    A,$01              ; Do a ...
3774: CD 3C 39       CALL  $393C              ;{Pause} ... pause
3777: C3 CD 35       JP    $35CD              ;{ServiceMenu} Top of interactive service routine
;
PrintBCD2:
; Print 2-digit BCD value in A to screen at HL and HL+1
377A: F5             PUSH  AF                 ; Hold the value * C3757,C375E
377B: 0F             RRCA                     ; Get ...
377C: 0F             RRCA                     ; ... the ...
377D: 0F             RRCA                     ; ... upper ...
377E: 0F             RRCA                     ; ... decimal ...
377F: E6 0F          AND   $0F                ; ... value
3781: C6 30          ADD   $30                ; Offset to ASCII for tile number
3783: 77             LD    (HL),A             ; Put digit on screen
3784: 23             INC   HL                 ; Next screen coordinate
3785: F1             POP   AF                 ; Restore the value
3786: E6 0F          AND   $0F                ; Get the lower decimal value
3788: C6 30          ADD   $30                ; Offset to ASCII for tile number
378A: 77             LD    (HL),A             ; Put digit on screen
378B: C9             RET                      ; Done

; Bump the 4-digit BCD count of ISRs every 64 ISR ticks. The IRQ ticks at 56.74Hz. This is roughly
; every 1.1 seconds. Almost once a second. 
;
378C: 21 0F E7       LD    HL,$E70F           ; Point to last counter value (upper 2 bits) * C374E
378F: 3A 4E E0       LD    A,($E04E)          ;{-1_isrCNT_1} Bumped every ISR
3792: E6 C0          AND   $C0                ; Keep top 2 bits of count (change every 64 ticks)
3794: BE             CP    (HL)               ; Have the upper 2 bits changed since we last looked?
3795: C8             RET   Z                  ; No ... do nothing
3796: 32 0F E7       LD    ($E70F),A          ;{-1_isrCVal} Remember new counter value (upper 2 bits)
;
; Count has changed ... bump the 4-digit BCD count of ISRs
3799: 3A 0E E7       LD    A,($E70E)          ;{-1_isrCntL} LSB of BCD counter
379C: C6 01          ADD   $01                ; Bump the low nibble
379E: 27             DAA                      ; Adjust carry into high nibble
379F: 32 0E E7       LD    ($E70E),A          ;{-1_isrCntL} Possibly new LSB of BCD counter
37A2: D0             RET   NC                 ; Didn't carry ... out
37A3: 3A 0D E7       LD    A,($E70D)          ;{-1_isrCntM} MSB of BCD counter
37A6: C6 01          ADD   $01                ; Bump the low nibble (carry)
37A8: 27             DAA                      ; Adjust carry into high nibble
37A9: 32 0D E7       LD    ($E70D),A          ;{-1_isrCntM} Possibly new MSB of BCD counter
37AC: C9             RET                      ; Done

ServiceSOUNDS:
; Service routine for "SOUNDS"
;
37AD: 2A 53 3D       LD    HL,($3D53)         ; 
37B0: 22 06 E7       LD    ($E706),HL         ;{-1_sndLastRow} 
37B3: 21 68 3D       LD    HL,$3D68           ; Screen text for sound list
37B6: FD 21 57 3D    LD    IY,$3D57           ; Sound table ... command number for each menu entry
37BA: CD C0 37       CALL  $37C0              ; Do the sound input loop
37BD: C3 CD 35       JP    $35CD              ;{ServiceMenu} Back to service routine
;
37C0: FD 22 0B E7    LD    ($E70B),IY         ;{-1_sndTable} Hold pointer to the sound command table * C37BA
37C4: E5             PUSH  HL                 ; Hold pointer to multi-copy
37C5: CD AD 38       CALL  $38AD              ;{ClearScreen} Clear screen (tiles and color)
37C8: E1             POP   HL                 ; Restore multi-copy
37C9: CD 08 39       CALL  $3908              ;{MultiCopyToRAM} Print the screen description
37CC: DD 21 08 E7    LD    IX,$E708           ; 3 byte area for menu-change handling
37D0: 3E 01          LD    A,$01              ; Start with row one ...
37D2: 32 05 E7       LD    ($E705),A          ;{-1_sndNumber} ... selected
;
37D5: 06 02          LD    B,$02              ; Color selected with ...
37D7: CD 23 39       CALL  $3923              ;{MenuColor2} ... color 2
37DA: 3E 01          LD    A,$01              ; Do ...
37DC: 0E 40          LD    C,$40              ; ... a ...
37DE: CD 3E 39       CALL  $393E              ; ... pause
37E1: CD 72 38       CALL  $3872              ; Diable sounds
37E4: CD 7D 38       CALL  $387D              ; Play current menu selection
37E7: 3E FF          LD    A,$FF              ; Set starting status bits ...
37E9: 32 11 E7       LD    ($E711),A          ;{-1_startButtons} ... for start-button polling
37EC: 3A 00 D0       LD    A,($D000)          ;{-2_IN0} Start-2 ... * J380D,J3815,J3828,J383B,J384C
37EF: CB 4F          BIT   1,A                ; ... pressed?
37F1: 28 4A          JR    Z,$383D            ; Yes ..
37F3: CD F2 38       CALL  $38F2              ;{GetStarts} Get starts
37F6: E6 AA          AND   $AA                ; Only interested in start-1
37F8: FE 2A          CP    $2A                ; Start-1 transition from off to on?
37FA: 28 13          JR    Z,$380F            ; Yes ... restart sound and back to top of loop
;
37FC: CD DD 38       CALL  $38DD              ; Get L/R status
37FF: 47             LD    B,A                ; Hold it
3800: E6 55          AND   $55                ; Only left bits
3802: FE 55          CP    $55                ; Left been down awhile?
3804: 28 11          JR    Z,$3817            ; Yes ... go do "down"
3806: 78             LD    A,B                ; Restore bits
3807: E6 AA          AND   $AA                ; Only right bits
3809: FE AA          CP    $AA                ; Right been down awhile?
380B: 28 1D          JR    Z,$382A            ; Yes ... go do "up"
380D: 18 DD          JR    $37EC              ; Neither ... back to start of sound loop
;
380F: CD 72 38       CALL  $3872              ; Turn sounds off * J37FA
3812: CD 7D 38       CALL  $387D              ; Play current selection again
3815: 18 D5          JR    $37EC              ; Back to sound menu loop
;
3817: DD 36 00 55    LD    (IX+$00),$55       ; Last value was left-held-down * J3804
381B: 3A 06 E7       LD    A,($E706)          ;{-1_sndLastRow} Bottom row number in menu
381E: DD 77 01       LD    (IX+$01),A         ; Store bottom row number (14)
3821: DD 36 02 01    LD    (IX+$02),$01       ; Down means add 1
3825: CD 4F 38       CALL  $384F              ; Do delta if possible
3828: 18 C2          JR    $37EC              ; Back to sound loop
;
382A: DD 36 00 AA    LD    (IX+$00),$AA       ; Last value was right-held-down * J380B
382E: 3A 07 E7       LD    A,($E707)          ;{-1_sndFirstRow} Top row number in menu
3831: DD 77 01       LD    (IX+$01),A         ; Store top row number (1)
3834: DD 36 02 FF    LD    (IX+$02),$FF       ; Up means subtract 1
3838: CD 4F 38       CALL  $384F              ; Do delta if possible
383B: 18 AF          JR    $37EC              ; Back to sound loop
;
; Exit sound
383D: CD 72 38       CALL  $3872              ; All sounds off * J37F1
3840: 3E 01          LD    A,$01              ; Do ...
3842: 0E 20          LD    C,$20              ; ... a ...
3844: CD 3E 39       CALL  $393E              ; ... pause
3847: 3A 00 D0       LD    A,($D000)          ;{-2_IN0} Start-2 ...
384A: CB 4F          BIT   1,A                ; ... pressed?
384C: 20 9E          JR    NZ,$37EC           ; No ... just turning off sound. Back to loop.
384E: C9             RET                      ; It is held down ... out

; Bump sound menu up or down with a shorter held-down advance rate.
384F: CD 72 38       CALL  $3872              ; All sounds off * C3825,C3838
3852: DD 56 00       LD    D,(IX+$00)         ; Button mask
3855: 1E 02          LD    E,$02              ; Wait count (outer loop)
3857: CD C8 38       CALL  $38C8              ; Wait for button to be released
385A: 28 0F          JR    Z,$386B            ; Released: Bump row, hightlight, and out
385C: CD 95 38       CALL  $3895              ; Not released: Bump row and hightlight * J3867
385F: DD 56 00       LD    D,(IX+$00)         ; Button mask
3862: 1E 01          LD    E,$01              ; Wait count (shorter for held-down repeats)
3864: CD C8 38       CALL  $38C8              ; Wait for button to be released
3867: 20 F3          JR    NZ,$385C           ; Not released ... keep bumping while held down
3869: 18 03          JR    $386E              ; Done
;
386B: CD 95 38       CALL  $3895              ; Bump selection if possible * J385A
386E: CD 7D 38       CALL  $387D              ; Play sound * J3869
3871: C9             RET                      ; Done

; Turn off all sounds
3872: 3E 00          LD    A,$00              ; Reset sound processor and ... * C37E1,C380F,C383D,C384F
3874: 32 00 D0       LD    ($D000),A          ; ... disable all sound
3877: CB FF          SET   7,A                ; Latch ...
3879: 32 00 D0       LD    ($D000),A          ; ... sound command
387C: C9             RET                      ; Done

; Play current sound menu selection
387D: 3A 05 E7       LD    A,($E705)          ;{-1_sndNumber} Current sound menu selection * C37E4,C3812,C386E
3880: 4F             LD    C,A                ; To ...
3881: 06 00          LD    B,$00              ; ... BC
3883: FD 2A 0B E7    LD    IY,($E70B)         ;{-1_sndTable} Get sound offset table
3887: FD 09          ADD   IY,BC              ; Offset to the desired sound
3889: FD 7E 00       LD    A,(IY+$00)         ; Get the sound command
388C: 32 00 D0       LD    ($D000),A          ; Send sound command
388F: CB FF          SET   7,A                ; Latch ...
3891: 32 00 D0       LD    ($D000),A          ; ... sound command
3894: C9             RET                      ; Done

; Bump sound menu selection if possible
3895: 3A 05 E7       LD    A,($E705)          ;{-1_sndNumber} Current row number * C385C,C386B
3898: DD BE 01       CP    (IX+$01)           ; Are we at the limit?
389B: C8             RET   Z                  ; Yes ... leave it
389C: 06 00          LD    B,$00              ; Unhighlight ...
389E: CD 23 39       CALL  $3923              ;{MenuColor2} ... current selection
38A1: DD 86 02       ADD   A,(IX+$02)         ; Add offset
38A4: 32 05 E7       LD    ($E705),A          ;{-1_sndNumber} New row number
38A7: 06 02          LD    B,$02              ; Highlight ...
38A9: CD 23 39       CALL  $3923              ;{MenuColor2} ... current selection
38AC: C9             RET                      ; Done

ClearScreen:
;
; Clear tiles and colors ... 8000-87FF.
;
38AD: 21 00 80       LD    HL,$8000           ; Tile video memory  * C35CD,C3666,C372A,C376F,C37C5,C3966,C39CB,C3A32
38B0: 01 FF 03       LD    BC,$03FF           ; Count (32x32 tiles)
38B3: 36 00          LD    (HL),$00           ; Clear first byte
38B5: 54             LD    D,H                ; Copy source ...
38B6: 5D             LD    E,L                ; ... to destination
38B7: 13             INC   DE                 ; Start block copy at 8001
38B8: ED B0          LDIR                     ; Walk the 00 through memory
;
38BA: 21 00 84       LD    HL,$8400           ; Color memory * C39E8
38BD: 01 FF 03       LD    BC,$03FF           ; Count (32x32 tiles)
38C0: 36 00          LD    (HL),$00           ; Clear first byte
38C2: 54             LD    D,H                ; Copy source ...
38C3: 5D             LD    E,L                ; ... to destination
38C4: 13             INC   DE                 ; Start block copy at 8401
38C5: ED B0          LDIR                     ; Walk the 00 through memory
38C7: C9             RET                      ; Done

; Wait for button (left or right) to be released for 4 polling passes.
; D contains button mask (55 or AA)
; E contains the outer count time
; Return A=0 (released) or mask if still held
38C8: 0E 00          LD    C,$00              ; Roll around DJNZ count of 256 * C3637,C3644,C3857,C3864,J38D7
38CA: 06 0C          LD    B,$0C              ; Inner count of 12 * J38D4
38CC: CD E2 38       CALL  $38E2              ;{GetLRs} Get L/R status and long debounce delay * J38D1
38CF: A2             AND   D                  ; Only keep L or R value
38D0: C8             RET   Z                  ; Return if L or R has been released 4 passes (long time)
38D1: 10 F9          DJNZ  $38CC              ; Long ...
38D3: 0D             DEC   C                  ; ... wait ...
38D4: 20 F4          JR    NZ,$38CA           ; ... for ...
38D6: 1D             DEC   E                  ; ... button ...
38D7: 20 EF          JR    NZ,$38C8           ; ... to be released
38D9: 3E FF          LD    A,$FF              ; Button not released ...
38DB: A2             AND   D                  ; ... return held down 4 times
38DC: C9             RET                      ; Done
;
38DD: CD E2 38       CALL  $38E2              ;{GetLRs} Get L/R status * C35FD,C37FC
38E0: 18 1F          JR    $3901              ; Long debounce delay and out

GetLRs:
; This method returns the history of the left/right bits shifted into E710. Bits 0 and 1
; contain the current value and bits 2 and 3 contain the previous value. The returned bits
; are active 1 (1 means pressed).
;
38E2: 21 10 E7       LD    HL,$E710           ; Point to LR status bits * C38CC,C38DD
38E5: 3A 01 D0       LD    A,($D001)          ;{-2_IN1} Read left/right buttons (bits 0 and 1)
38E8: 1F             RRA                      ; Rotate ...
38E9: CB 16          RL    (HL)               ; ... LR button ...
38EB: 1F             RRA                      ; ... status ...
38EC: CB 16          RL    (HL)               ; ... into E710 (shift over last status)
38EE: 7E             LD    A,(HL)             ; Compliment so ...
38EF: EE FF          XOR   $FF                ; ... 1 means pressed
38F1: C9             RET                      ; Return (no delay debounce as in 38F2)

GetStarts:
; This method returns the history of the start bits shifted into E711. Bits 0 and 1
; contain the current value and bits 2 and 3 contain the previous value. The returned bits
; are active 1 (1 means pressed).
;
38F2: 21 11 E7       LD    HL,$E711           ; Point to start-button status bits * C37F3,C39A9
38F5: 3A 00 D0       LD    A,($D000)          ;{-2_IN0} Read start buttons (bits 0 and 1)
38F8: 1F             RRA                      ; Rotate ...
38F9: CB 16          RL    (HL)               ; ... start button ...
38FB: 1F             RRA                      ; ... status ...
38FC: CB 16          RL    (HL)               ; ... into E711 (shift over last status)
38FE: 7E             LD    A,(HL)             ; Compliment so ...
38FF: EE FF          XOR   $FF                ; ... 1 means pressed
;
3901: F5             PUSH  AF                 ; Hold status * J38E0
3902: AF             XOR   A                  ; Fast zero
3903: 3D             DEC   A                  ; Kill time ... * J3904
3904: 20 FD          JR    NZ,$3903           ; ... for debounce
3906: F1             POP   AF                 ; Restore result
3907: C9             RET                      ; Return result

MultiCopyToRAM:
; Multiple CopyToRAM from HL calls. Each copy of the form:
; LL DD DD NN... LL DD DD NN... 00
; LL is byte count, DDDD is destination, NN is data. A count of 00
; ends the multiple sets.
3908: 7E             LD    A,(HL)             ; Is the count ... * C35D3,C366C,C36F7,C3709,C3730,C37C9,J390F
3909: FE 00          CP    $00                ; .. an end marker?
390B: C8             RET   Z                  ; Yes ... out
390C: CD 11 39       CALL  $3911              ;{CopyToRAM} Do the copy to RAM
390F: 18 F7          JR    $3908              ;{MultiCopyToRAM} Do next set

CopyToRAM:
; Copy data pointed to by HL to memory.
; First byte of data is length.
; 2nd and 3rd byte of data is destination.
;
3911: 4E             LD    C,(HL)             ; Get BC count ... * C36E4,C390C
3912: 06 00          LD    B,$00              ; ... (MSB = 00)
3914: 23             INC   HL                 ; Next
3915: 5E             LD    E,(HL)             ; Get DE ...
3916: 23             INC   HL                 ; ... ...
3917: 56             LD    D,(HL)             ; ... destination
3918: 23             INC   HL                 ; Next
3919: ED B0          LDIR                     ; Copy DE to HL (BC bytes)
391B: C9             RET                      ; Done

MenuColor:
; Mark a two-byte color value corresponding to chosen option.
; Row number is in A, which seems to be numbered starting at 3 for first.
; Color value is in B.
; There are two entry points here. One corrects the start-with-3 value and the
; other uses C as the row number without adjustment
;
391C: 4F             LD    C,A                ; Hold row number in C * C35DB,C3657,C3662
391D: D6 03          SUB   $03                ; First row is numbered 3 ... make it 0 based
391F: 07             RLCA                     ; Two lines per option
3920: 3C             INC   A                  ; Skip a line at the top
3921: 18 01          JR    $3924              ; Mark the color
;
MenuColor2:
3923: 4F             LD    C,A                ; Use the row number given * C37D7,C389E,C38A9
;
3924: C5             PUSH  BC                 ; Hold color and row number * J3921
3925: 0E 64          LD    C,$64              ; BC = 0064 ...
3927: 06 00          LD    B,$00              ; ... flat offset in color RAM
3929: 60             LD    H,B                ; MSB of HL to 0
392A: 07             RLCA                     ; Row number ...
392B: 07             RLCA                     ; ... times ...
392C: 07             RLCA                     ; ... 8
392D: 6F             LD    L,A                ; HL is now rowNumber*8
392E: 29             ADD   HL,HL              ; rowNumber*16
392F: 29             ADD   HL,HL              ; rowNumber*32
3930: 09             ADD   HL,BC              ; Flat offset
3931: EB             EX    DE,HL              ; Complete offset to DE
3932: 21 00 84       LD    HL,$8400           ; Start of color RAM
3935: 19             ADD   HL,DE              ; Offset to correct space
3936: C1             POP   BC                 ; Restore color (B) and row number (C)
3937: 70             LD    (HL),B             ; Set two ...
3938: 23             INC   HL                 ; ... adjacent color ...
3939: 70             LD    (HL),B             ; ... values
393A: 79             LD    A,C                ; Restore row number to A
393B: C9             RET                      ; Done

Pause:
; Do a counted pause ... a 16 bit count down
; that rolls A times.
393C: 0E 00          LD    C,$00              ; MSB 0 * C3774,J3946
393E: 06 00          LD    B,$00              ; 256 step ... * C37DE,C3844,J3943
3940: 10 FE          DJNZ  $3940              ; ... countdown * J3940
3942: 0D             DEC   C                  ; 256*256 step ...
3943: 20 F9          JR    NZ,$393E           ; ... countdown
3945: 3D             DEC   A                  ; All done?
3946: 20 F4          JR    NZ,$393C           ;{Pause} No keep pausing
3948: C9             RET                      ; Done

PauseStart:
; Wait for A number of 16-bit countdowns but abort if the start-2
; button is pressed. If the start-2 aborts the wait then
; B is set to 1. Otherwise B is left alone.
;
3949: C5             PUSH  BC                 ; Preserve BC
394A: 0E 00          LD    C,$00              ; Set 16-bit count ... * J395D
394C: 06 00          LD    B,$00              ; ... to 0000 * J395A
394E: 10 FE          DJNZ  $394E              ; ... 256 step countdown * J394E
3950: F5             PUSH  AF                 ; Hold count (A)
3951: 3A 00 D0       LD    A,($D000)          ;{-2_IN0} Start-2 ...
3954: CB 4F          BIT   1,A                ; ... pressed
3956: 28 09          JR    Z,$3961            ; Yes ... note it and out
3958: F1             POP   AF                 ; Restore count
3959: 0D             DEC   C                  ; Do 16-bit ...
395A: 20 F0          JR    NZ,$394C           ; ... count rollover
395C: 3D             DEC   A                  ; All waiting done?
395D: 20 EB          JR    NZ,$394A           ; No ... do it all
395F: C1             POP   BC                 ; Restore BC
3960: C9             RET                      ; Return with B unaltered
;
3961: F1             POP   AF                 ; Drop stacked count * J3956
3962: C1             POP   BC                 ; Restore BC
3963: 06 01          LD    B,$01              ; Return with B=1
3965: C9             RET                      ; Done

ServiceCHARACTER:
; Service routine for "CHARACTER"
; Two blocks of 8 sprites (the small tank picture) drawn in
; all four flip configurations. The bottom block is the same
; as the top:
;
;   T T       (Tank, Tank flipped horizontally)
;   T T       (Tank flipped vertically, Tank flipped both)
;
;   T T       (Tank, Tank flipped horizontally)
;   T T       (Tank flipped vertically, Tank flipped both)
;
3966: CD AD 38       CALL  $38AD              ;{ClearScreen} Clear the screen
3969: 11 00 E1       LD    DE,$E100           ; Copy 4 ...
396C: 21 6D 3E       LD    HL,$3E6D           ; ... sprite ...
396F: 01 10 00       LD    BC,$0010           ; ... descriptors ...
3972: ED B0          LDIR                     ; ... to RAM (ISR moves to hardware)
3974: 11 60 E1       LD    DE,$E160           ; Copy 4 ...
3977: 21 7D 3E       LD    HL,$3E7D           ; ... sprite ...
397A: 01 10 00       LD    BC,$0010           ; ... descriptors ...
397D: ED B0          LDIR                     ; ... to RAM (ISR moves to hardware)
397F: 3A 00 D0       LD    A,($D000)          ;{-2_IN0} Start-2 ... * J3984
3982: CB 4F          BIT   1,A                ; ... pressed?
3984: 20 F9          JR    NZ,$397F           ; No ... wait
3986: 21 00 E1       LD    HL,$E100           ; Clear ...
3989: 36 00          LD    (HL),$00           ; ... sprite ...
398B: 54             LD    D,H                ; ... copy ...
398C: 5D             LD    E,L                ; ... ...
398D: 13             INC   DE                 ; ... ...
398E: 01 BF 00       LD    BC,$00BF           ; ... ...
3991: ED B0          LDIR                     ; ... memory
3993: C3 CD 35       JP    $35CD              ;{ServiceMenu} Back to root of interactive service

ServiceCOLOR:
; Service routine for "COLOR"
;
3996: 3E 01          LD    A,$01              ; Start with ...
3998: 32 12 E7       LD    ($E712),A          ;{-1_colorScreen} ... color screen 1 (letters/numbers)
399B: AF             XOR   A                  ; Clear ...
399C: 32 11 E7       LD    ($E711),A          ;{-1_startButtons} ... start bit history
399F: 18 2A          JR    $39CB              ; Jump right into color screen 1 (letters/numbers)
;
39A1: 3A 00 D0       LD    A,($D000)          ;{-2_IN0} Start-2 ... * J39B0,J39E6,J3A10,J3A20
39A4: CB 4F          BIT   1,A                ; ... pressed?
39A6: CA CD 35       JP    Z,$35CD            ;{ServiceMenu} Yes ... back to service routine
39A9: CD F2 38       CALL  $38F2              ;{GetStarts} Get the start bit status history
39AC: E6 AA          AND   $AA                ; Only care about the start-1
39AE: FE 2A          CP    $2A                ; 00101010 Wait for upper nibble to show 0 to 1 transition 0x1x
39B0: 20 EF          JR    NZ,$39A1           ; Loop back until start-1 goes from off to on
39B2: 3A 12 E7       LD    A,($E712)          ;{-1_colorScreen} Get current color screen number
39B5: 3C             INC   A                  ; Bump to next ...
39B6: 32 12 E7       LD    ($E712),A          ;{-1_colorScreen} ... color screen * J39C9
39B9: FE 01          CP    $01                ; Screen 1 ...
39BB: 28 0E          JR    Z,$39CB            ; ... letters and numbers
39BD: FE 02          CP    $02                ; Screen 2 ...
39BF: CA E8 39       JP    Z,$39E8            ; ... color blocks
39C2: FE 03          CP    $03                ; Screen 3 ...
39C4: CA 13 3A       JP    Z,$3A13            ; ... all red
39C7: D6 03          SUB   $03                ; Roll back if overflow
39C9: 18 EB          JR    $39B6              ; Loop back to handle overflow
;
; Draw line of letters and numbers on screen. 
; With clear color ram, letters are in blue, numbers in white.
39CB: CD AD 38       CALL  $38AD              ;{ClearScreen} Clear screen and color ram * J399F,J39BB
39CE: 21 1C 81       LD    HL,$811C           ; Screen location for Z
39D1: 06 1A          LD    B,$1A              ; 26 letters
39D3: 3E 5A          LD    A,$5A              ; Tile 90 (Letter Z)
39D5: 77             LD    (HL),A             ; Put letter on screen * J39D8
39D6: 2B             DEC   HL                 ; Back up screen pointer
39D7: 3D             DEC   A                  ; Back up letter
39D8: 10 FB          DJNZ  $39D5              ; Do all letters
39DA: 21 0C 82       LD    HL,$820C           ; Screen location for 9
39DD: 06 0A          LD    B,$0A              ; 10 numbers to do
39DF: 3E 39          LD    A,$39              ; Tile 57 (Number 9)
39E1: 77             LD    (HL),A             ; Put number on screen * J39E4
39E2: 2B             DEC   HL                 ; Back up screen pointer
39E3: 3D             DEC   A                  ; Back up number
39E4: 10 FB          DJNZ  $39E1              ; Do all numbers
39E6: 18 B9          JR    $39A1              ; Back to wait on button
;
39E8: CD BA 38       CALL  $38BA              ; Clear color memory * J39BF
39EB: 21 20 80       LD    HL,$8020           ; Start of first visible row
39EE: 36 F3          LD    (HL),$F3           ; Tile 243 (a blank tile)
39F0: 54             LD    D,H                ; Fill ...
39F1: 5D             LD    E,L                ; ... screen ...
39F2: 13             INC   DE                 ; ... with ...
39F3: 01 BF 03       LD    BC,$03BF           ; ... blank ...
39F6: ED B0          LDIR                     ; ... tile
;
39F8: 21 8D 3E       LD    HL,$3E8D           ; Describes blocks
39FB: 06 0A          LD    B,$0A              ; 10 blocks of color to draw
39FD: C5             PUSH  BC                 ; Hold block count * J3A0E
39FE: 5E             LD    E,(HL)             ; Read ...
39FF: 23             INC   HL                 ; ... screen ...
3A00: 56             LD    D,(HL)             ; ... pointer
3A01: 23             INC   HL                 ; Next
3A02: 46             LD    B,(HL)             ; Read column count
3A03: 23             INC   HL                 ; Next
3A04: 4E             LD    C,(HL)             ; Read row count
3A05: 23             INC   HL                 ; Next
3A06: 7E             LD    A,(HL)             ; Read tile color value
3A07: 23             INC   HL                 ; Next
3A08: EB             EX    DE,HL              ; Pointer to DE and screen to HL
3A09: CD 23 3A       CALL  $3A23              ;{TileColorBlock} Draw the block of color
3A0C: EB             EX    DE,HL              ; Pointer back to HL
3A0D: C1             POP   BC                 ; Restore block count
3A0E: 10 ED          DJNZ  $39FD              ; Do all blocks
3A10: C3 A1 39       JP    $39A1              ; Back to wait on button
;
3A13: 21 20 84       LD    HL,$8420           ; Start of first visible color row * J39C4
3A16: 36 0C          LD    (HL),$0C           ; Color value "0C" (a red)
3A18: 54             LD    D,H                ; Destination is ...
3A19: 5D             LD    E,L                ; ... source ...
3A1A: 13             INC   DE                 ; ... plus one
3A1B: 01 BF 03       LD    BC,$03BF           ; All of color memory
3A1E: ED B0          LDIR                     ; Fill the color memory with "0C"
3A20: C3 A1 39       JP    $39A1              ; Back to wait on button
;
TileColorBlock:
; Draw a tile color block at HL.
; A = tile color value
; B = number of columns
; C = number of rows
3A23: C5             PUSH  BC                 ; Hold counts * C3A09,J3A2F
3A24: E5             PUSH  HL                 ; Hold screen position
3A25: 77             LD    (HL),A             ; Store tile color number to screen * J3A27
3A26: 23             INC   HL                 ; Next on row
3A27: 10 FC          DJNZ  $3A25              ; Do all columns on this row
3A29: E1             POP   HL                 ; Restore screen position
3A2A: 0E 20          LD    C,$20              ; Drop down ...
3A2C: 09             ADD   HL,BC              ; ... one row
3A2D: C1             POP   BC                 ; Restore counts
3A2E: 0D             DEC   C                  ; All rows done?
3A2F: 20 F2          JR    NZ,$3A23           ;{TileColorBlock} No ... do all rows
3A31: C9             RET                      ; Done

ServiceBEAM:
; Service routine for "BEAM ADJUST"
; Draws a square grid for visual beam adjustment.
;
3A32: CD AD 38       CALL  $38AD              ;{ClearScreen} Clear screen and colors
3A35: 21 20 80       LD    HL,$8020           ; Tile memory (first visible row)
3A38: 0E 1E          LD    C,$1E              ; 30 visible columns
3A3A: 06 0F          LD    B,$0F              ; 15 double rows (first row invisible, last blank)
3A3C: C5             PUSH  BC                 ; Hold the double row count * J3A5A
3A3D: 06 00          LD    B,$00              ; BC = 001E
3A3F: 36 94          LD    (HL),$94           ; Tile 148 ... top and right grid lines. This is NOT visible.
3A41: 54             LD    D,H                ; Hold this ...
3A42: 5D             LD    E,L                ; ... pointer
3A43: 23             INC   HL                 ; Next on screen
3A44: 36 93          LD    (HL),$93           ; Tile 147 ... top and left grid lines. This IS visible.
3A46: 23             INC   HL                 ; Next screen pointer
3A47: EB             EX    DE,HL              ; HL is now source, DE is destination
3A48: ED B0          LDIR                     ; Copy one row all the way across to make the top part of boxes
3A4A: EB             EX    DE,HL              ; Restore screen pointer
3A4B: 0E 1E          LD    C,$1E              ; 30 visible columns
3A4D: 36 96          LD    (HL),$96           ; Tile 150 ... bottom and right grid lines. This is NOT visible.
3A4F: 54             LD    D,H                ; Hold this ...
3A50: 5D             LD    E,L                ; ... pointer
3A51: 23             INC   HL                 ; Next on screen
3A52: 36 95          LD    (HL),$95           ; Tile 149 ... bottom and left grid lines. This IS visible.
3A54: 23             INC   HL                 ; Next on screen
3A55: EB             EX    DE,HL              ; HL is now source, DE is destination
3A56: ED B0          LDIR                     ; Copy one row all the way across to make the bottom part of boxes
3A58: EB             EX    DE,HL              ; Restore screen pointer
3A59: C1             POP   BC                 ; Restore double-row count
3A5A: 10 E0          DJNZ  $3A3C              ; Do all double rows
3A5C: 3A 00 D0       LD    A,($D000)          ;{-2_IN0} Wait on ... * J3A61
3A5F: CB 4F          BIT   1,A                ; ... start-2 ...
3A61: 20 F9          JR    NZ,$3A5C           ; ... button
3A63: C3 CD 35       JP    $35CD              ;{ServiceMenu} Return to interactive service mode

; RAM OK Message
3A66: 08 84 80 ; Copy 8 bytes to 8084
3A69: 52 41 4D 00 00 00 4F 4B                              ; RAM___OK
3A71: 00  ; End of copy sequence

; RAM NG (Not Good) Message
3A72: 10 84 80 ; Copy 16 bytes to 8084 (screen tiles)
3A75: 52 41 4D 00 00 00 4E 47 00 00 5D 00 00 00 00 5D      ; RAM___NG__:____:
3A85: 00  ; End of copy sequence

; ROM Good and bad
3A86: 52 4F 4D 00 00 00 4F 4B ; ROM___OK
3A8E: 52 4F 4D 00 00 00 4E 47 ; ROM___NG

; Addresses of interactive service routine functions
3A96: 00 00 ; Unused option (row starts with 3)  
3A98: 00 00 ; Unused option (row starts with 3) 
3A9A: 00 00 ; Unused option (row starts with 3)
3A9C: 66 36 ; 3666 : "DIP SWITCH"
3A9E: 21 37 ; 3721 : "I_O"
3AA0: AD 37 ; 37AD : "SOUNDS"
3AA2: 66 39 ; 3966 : "CHARACTER"
3AA4: 96 39 ; 3996 : "COLOR"
3AA6: 32 3A ; 3A32 : "BEAM ADJUST"

3AA8: B0 3A ; Pointer to string offsets (3AB0)
3AAA: B8 3A ; Pointer to strings (3AB8)

3AAC: 03 00 ; First print ... string[value]
3AAE: 03 04 ; Second print ... string[value+4]

; Value-to-string-address offsets
3AB0: 00 04 08 0C 10 1B 26 31

3AB8: 01 73 81 ; Copy 1 byte to screen at 8173
3ABB: 35 ;  "5" String 0 (value 11)
;
3ABC: 01 73 81 ; Copy 1 byte to screen at 8173
3ABF: 33 ;  "3" String 1 (value 10)
;
3AC0: 01 73 81 ; Copy 1 byte to screen at 8173
3AC3: 32 ;  "2" String 2 (value 01)
;
3AC4: 01 73 81 ; Copy 1 byte to screen at 8173
3AC7: 31 ;  "1" String 3 (value 00)
;
3AC8: 08 ED 81 ; Copy 8 bytes to screen at 81ED
3ACB: 31 30 00 33 30 00 35 30   ;"10_30_50" String 4 (value 11)
;
3AD3: 08 ED 81 ; Copy 8 bytes to screen at 81ED
3AD6: 32 30 00 34 30 00 36 30   ;"20_40_60" String 5 (value 10)
;
3ADE: 08 ED 81 ; Copy 8 bytes to screen at 81ED 
3AE1: 00 00 00 00 00 00 31 30   ;"______10" String 6 (value 01)
;
3AE9: 08 ED 81 ; Copy 8 bytes to screen at 81ED
3AEC: 00 00 00 00 00 00 4E 4F   ;"______NO" String 7 (value 00)

3AF4: FA 3A ; Pointer to string offsets (3AFA)
3AF6: FC 3A ; Pointer to strings (3AFC)

3AF8: 01 00 ; One bit ... no offset

3AFA: 00 0A ; Value-to-string-address offsets

3AFC: 07 B1 82 ; Copy 7 bytes to screen at 82B1
3AFF: 54 41 42 4C 45 00 00   ;"TABLE__"
;
3B06: 07 B1 82 ; Copy 7 bytes to screen at 82B1
3B09: 55 50 52 49 47 48 54   ;"UPRIGHT"

; Switch setting background text
;
3B10: 16 84 80 ; Copy 22 bytes to screen at 8084
3B13: 44 49 50 00 53 57 00 31 00 32 00 33 00 34 00 35 00 36 00 37 00 38 ;  "DIP_SW_1_2_3_4_5_6_7_8"
3B29: 03 C6 80 ; Copy 3 bytes to screen at 80C6
3B2C: 53 57 31   ;"SW1"
3B2F: 03 06 81 ; Copy 3 bytes to screen at 8106
3B32: 53 57 32   ;"SW2"
3B35: 0B 64 81 ; Copy 11 bytes to screen at 8164
3B38: 50 41 54 52 4F 4C 00 43 41 52 53  ; "PATROL_CARS"
3B43: 0D A4 81 ; Copy 13 bytes to screen at 81A4
3B46: 45 58 54 45 4E 44 00 50 4F 49 4E 54 53 ;  "EXTEND_POINTS"
3B53: 08 F6 81 ; Copy 8 bytes to screen at 81F6
3B56: 54 48 4F 55 53 41 4E 44;   "THOUSAND"
3B5E: 09 24 82 ; Copy 9 bytes to screen at 8224
3B61: 43 4F 49 4E 00 4D 4F 44 45 ;  "COIN_MODE"
3B6A: 09 A4 82 ; Copy 9 bytes to screen at 82A4
3B6D: 42 4F 44 59 00 54 59 50 45  ; "BODY_TYPE"
3B76: 00 ; End of multi-copy

3B77: 01 2E 82 ; Copy 1 bytes to screen at 822E
3B7A: 00 ;  "_"
3B7B: 1A 64 82 ; Copy 26 bytes to screen at 8264
3B7E: 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 ;  "__________________________"
3B98: 00 ; End of multi-copy


3B99: 0F 00  ; Lower 4 bits, no offset 
;
3B9B: 9F 3B  ; Pointer to offsets
3B9D: AF 3B  ; Pointer to strings
;
3B9F: 00 10 20 30 40 50 60 60 70 80 90 A0 B0 60 60 C0
;
; Coin mode A:
;   15:1C-1P, 14:2C-1P, 13:3C-1P, 12:4C-1P, 11:5C-1P, 10:6C-1P, 9:NA, 8:NA, 
;   7:1C-2P, 6:1C-3P, 5:1C-4P, 4:1C-5P, 3:1C-6P, 2:NA, 1:NA, 0:FREE
;
;   Even though the service mode doesn't show it, the game treats:
;   9 is 7C-1P, 8 is NA, 2 is 1C-7P, 1 is 1C-8P
;
3BAF: 0D 31 82 ; Copy 13 bytes to screen at 8231
3BB2: 31 43 4F 49 4E 00 00 31 50 4C 41 59 00 ;  "1COIN__1PLAY_"
3BBF: 0D 31 82 ; Copy 13 bytes to screen at 8231
3BC2: 32 43 4F 49 4E 53 00 31 50 4C 41 59 00  ; "2COINS_1PLAY_"
3BCF: 0D 31 82 ; Copy 13 bytes to screen at 8231
3BD2: 33 43 4F 49 4E 53 00 31 50 4C 41 59 00  ; "3COINS_1PLAY_"
3BDF: 0D 31 82 ; Copy 13 bytes to screen at 8231
3BE2: 34 43 4F 49 4E 53 00 31 50 4C 41 59 00  ; "4COINS_1PLAY_"
3BEF: 0D 31 82 ; Copy 13 bytes to screen at 8231
3BF2: 35 43 4F 49 4E 53 00 31 50 4C 41 59 00  ; "5COINS_1PLAY_"
3BFF: 0D 31 82 ; Copy 13 bytes to screen at 8231
3C02: 36 43 4F 49 4E 53 00 31 50 4C 41 59 00  ; "6COINS_1PLAY_"
3C0F: 0D 31 82 ; Copy 13 bytes to screen at 8231
3C12: 00 00 00 00 00 00 00 00 00 00 00 00 00  ; "_____________"
3C1F: 0D 31 82 ; Copy 13 bytes to screen at 8231
3C22: 31 43 4F 49 4E 00 00 32 50 4C 41 59 53  ; "1COIN__2PLAYS"
3C2F: 0D 31 82 ; Copy 13 bytes to screen at 8231
3C32: 31 43 4F 49 4E 00 00 33 50 4C 41 59 53  ; "1COIN__3PLAYS"
3C3F: 0D 31 82 ; Copy 13 bytes to screen at 8231
3C42: 31 43 4F 49 4E 00 00 34 50 4C 41 59 53  ; "1COIN__4PLAYS"
3C4F: 0D 31 82 ; Copy 13 bytes to screen at 8231
3C52: 31 43 4F 49 4E 00 00 35 50 4C 41 59 53  ; "1COIN__5PLAYS"
3C5F: 0D 31 82 ; Copy 13 bytes to screen at 8231
3C62: 31 43 4F 49 4E 00 00 36 50 4C 41 59 53  ; "1COIN__6PLAYS"
3C6F: 0D 31 82 ; Copy 13 bytes to screen at 8231
3C72: 00 46 52 45 45 00 00 00 00 00 00 00 00  ; "_FREE________"

3C7F: 01 2E 82 ; Copy 1 bytes to screen at 822E
3C82: 41 ;  "A"
3C83: 0B 64 82 ; Copy 11 bytes to screen at 8264
3C86: 43 4F 49 4E 00 4D 4F 44 45 00 42 ;  "COIN_MODE_B"
3C91: 00 ; End of multi-copy

3C92: 03 00 03 04  ; First field, 2 bits. Second field, 2 bits and add 4 strings.
3C96: 9A 3C        ; 4C9A ... Offset table
3C98: A2 3C        ; 3CA2 ... String table

3C9A: 00 10 20 30 40 50 60 70
;
; Coin mode B
;   Coin A: 3=FREE, 2=3C-1P, 1=2C-1P, 0=1C-1P
;   Coin B: 3=1C-6P, 2=1C-5P, 1=1C-3P, 0=1C-2P 
;
3CA2: 0D 31 82 ; Copy 13 bytes to screen at 8231
3CA5: 31 43 4F 49 4E 00 00 31 50 4C 41 59 00  ; "1COIN__1PLAY_"
3CB2: 0D 31 82 ; Copy 13 bytes to screen at 8231
3CB5: 32 43 4F 49 4E 53 00 31 50 4C 41 59 00  ; "2COINS_1PLAY_"
3CC2: 0D 31 82 ; Copy 13 bytes to screen at 8231
3CC5: 33 43 4F 49 4E 53 00 31 50 4C 41 59 00  ; "3COINS_1PLAY_"
3CD2: 0D 31 82 ; Copy 13 bytes to screen at 8231
3CD5: 00 46 52 45 45 00 00 00 00 00 00 00 00  ; "_FREE________"
;
3CE2: 0D 71 82 ; Copy 13 bytes to screen at 8271
3CE5: 31 43 4F 49 4E 00 00 32 50 4C 41 59 53  ; "1COIN__2PLAYS"
3CF2: 0D 71 82 ; Copy 13 bytes to screen at 8271
3CF5: 31 43 4F 49 4E 00 00 33 50 4C 41 59 53  ; "1COIN__3PLAYS"
3D02: 0D 71 82 ; Copy 13 bytes to screen at 8271
3D05: 31 43 4F 49 4E 00 00 35 50 4C 41 59 53  ; "1COIN__5PLAYS"
3D12: 0D 71 82 ; Copy 13 bytes to screen at 8271
3D15: 31 43 4F 49 4E 00 00 36 50 4C 41 59 53  ; "1COIN__6PLAYS"

3D22: 0F 8B 80 ; Copy 15 bytes to screen at 808B
3D25: 31 00 32 00 33 00 34 00 35 00 36 00 37 00 38 ;  "1_2_3_4_5_6_7_8"
3D34: 04 C4 80 ; Copy 4 bytes to screen at 80C4
3D37: 4B 45 59 30  ; "KEY0"
3D3B: 04 04 81 ; Copy 4 bytes to screen at 8104
3D3E: 4B 45 59 31  ; "KEY1"
3D42: 04 44 81 ; Copy 4 bytes to screen at 8144
3D45: 4B 45 59 32  ; "KEY2"
3D49: 06 84 81 ; Copy 6 bytes to screen at 8184
3D4C: 54 49 4D 49 4E 47 ;  "TIMING"
3D52: 00 ; End of multi-copy
            
; Sound menu data        
3D53: 0E ; Row 14 is the bottom row of the menu
3D54: 01 ; Row 1 is the top row of the menu
   
3D55: 00 00 ; Unused   
   
; This table keeps the sound command for each row in the menu.
3D57: 00 ; Row 0 not used (menu begins with row 1)
3D58: 01 ; "01_EXPLOSION"
3D59: 10 ; "02_POINT_PASSAGE"
3D5A: 11 ; "03_UFO_EXPLOSION"
3D5B: 12 ; "04_CAR_MISSILE"
3D5C: 13 ; "05_COIN
3D5D: 14 ; "06_CAR_JUMP"
3D5E: 16 ; "07_SPACE_PLANT"
3D5F: 17 ; "08_UFO_FLYING"
3D60: 18 ; "09_BACK_GROUND_MUSIC"
3D61: 1B ; "10_ENDING_MUSIC"
3D62: 1C ; "11_OPENING_MUSIC"
3D63: 1D ; "12_STEP_PASSAGE"
3D64: 1E ; "13_CONGRATULATION"
3D65: 1F ; "14_CAR_EXPLOSION"   
 
3D66: 00 00 ; Unused
 
3D68: 0B 27 80 ; Copy 11 bytes to screen at 8027
3D6B: 53 00 4F 00 55 00 4E 00 44 00 53                             ; "S O U N D S"
3D76: 0E 44 81 ; Copy 14 bytes to screen at 8144
3D79: 30 37 00 53 50 41 43 45 00 50 4C 41 4E 54                    ; "07_SPACE_PLANT"
3D87: 0D 64 81 ; Copy 13 bytes to screen at 8164
3D8A: 30 38 00 55 46 4F 00 46 4C 59 49 4E 47                       ; "08_UFO_FLYING"
3D97: 0C 84 80 ; Copy 12 bytes to screen at 8084
3D9A: 30 31 00 45 58 50 4C 4F 53 49 4F 4E                         ;  "01_EXPLOSION"
3DA6: 0E E4 80 ; Copy 14 bytes to screen at 80E4
3DA9: 30 34 00 43 41 52 00 4D 49 53 53 49 4C 45                    ; "04_CAR_MISSILE"
3DB7: 10 C4 80 ; Copy 16 bytes to screen at 80C4
3DBA: 30 33 00 55 46 4F 00 45 58 50 4C 4F 53 49 4F 4E             ;  "03_UFO_EXPLOSION"
3DCA: 10 A4 80 ; Copy 16 bytes to screen at 80A4
3DCD: 30 32 00 50 4F 49 4E 54 00 50 41 53 53 41 47 45              ; "02_POINT_PASSAGE"
3DDD: 07 04 81 ; Copy 7 bytes to screen at 8104
3DE0: 30 35 00 43 4F 49 4E                                         ; "05_COIN"
3DE7: 0B 24 81 ; Copy 11 bytes to screen at 8124
3DEA: 30 36 00 43 41 52 00 4A 55 4D 50                             ; "06_CAR_JUMP"
3DF5: 14 84 81 ; Copy 20 bytes to screen at 8184
3DF8: 30 39 00 42 41 43 4B 00 47 52 4F 55 4E 44 00 4D 55 53 49 43  ; "09_BACK_GROUND_MUSIC"
3E0C: 0F A4 81 ; Copy 15 bytes to screen at 81A4
3E0F: 31 30 00 45 4E 44 49 4E 47 00 4D 55 53 49 43                 ; "10_ENDING_MUSIC"
3E1E: 10 C4 81 ; Copy 16 bytes to screen at 81C4
3E21: 31 31 00 4F 50 45 4E 49 4E 47 00 4D 55 53 49 43             ;  "11_OPENING_MUSIC"
3E31: 0F E4 81 ; Copy 15 bytes to screen at 81E4
3E34: 31 32 00 53 54 45 50 00 50 41 53 53 41 47 45                 ; "12_STEP_PASSAGE"
3E43: 11 04 82 ; Copy 17 bytes to screen at 8204
3E46: 31 33 00 43 4F 4E 47 52 41 54 55 4C 41 54 49 4F 4E       ;     "13_CONGRATULATION"
3E57: 10 24 82 ; Copy 16 bytes to screen at 8224
3E5A: 31 34 00 43 41 52 00 45 58 50 4C 4F 53 49 4F 4E           ;    "14_CAR_EXPLOSION"
3E6A: 00 ; End of multi-copy

3E6B: 00 00 ; Unused

; Sprite data 1
;
; YY is Y coordinate. 0 is bottom of the screen (all showing). EB is top of screen all showing. EC-FF clips off top of sprite.
; XX is X coordinate. 0 is left of the screen half clipped. F0 is right of the screen half clipped. F1-FF clips off right of sprite.
; HV_CCCCCC C=color set from 0 to F. H=1 horizontal flip V=1 vertical flip
; SS=image number from graphics set
;
;     YY MC SS XX
3E6D: A8 01 38 60 
3E71: A8 41 38 98 
3E75: 90 81 38 60   
3E79: 90 C1 38 98  
;
; Sprite data 2
3E7D: 68 01 38 60  
3E81: 68 41 38 98     
3E85: 50 81 38 60    
3E89: 50 C1 38 98       

; Blocks of color used in the color-test.
3E8D: 20 84 20 07 00 ; 32x7 block of color 0 starting at  8420
3E92: 00 87 20 07 08 ; 32x7 block of color 8 starting at  8700
3E97: 00 85 20 08 02 ; 32x8 block of color 2 starting at  8500
3E9C: 00 86 05 08 05 ;  5x8 block of color 5 starting at  8600
3EA1: 05 86 04 08 0C ;  4x8 block of color 12 starting at 8605
3EA6: 09 86 05 08 06 ;  5x8 block of color 6 starting at  8609
3EAB: 0E 86 04 08 04 ;  4x8 block of color 4 starting at  860E
3EB0: 12 86 05 08 03 ;  5x8 block of color 3 starting at  8612
3EB5: 17 86 04 08 00 ;  4x8 block of color 0 starting at  8617
3EBA: 1B 86 05 08 08 ;  5x8 block of color 8 starting at  861B

3EBF: 0E 84 80                                       ; 0E bytes to 8084
3EC2: 30 31 00 00 44 49 50 00 53 57 49 54 43 48      ; "01__DIP_SWITCH"
;
3ED0: 0C C4 80                                       ; 0C bytes to 80C4 
3ED3: 30 32 00 00 49 3F 4F 00 50 4F 52 54            ; "02__I_O"
;
3EDF: 0A 04 81                                       ; 0A bytes to 8104
3EE2: 30 33 00 00 53 4F 55 4E 44 53                  ; "03__SOUNDS"
;
3EEC: 0D 44 81                                       ; 0D bytes to 8144
3EEF: 30 34 00 00 43 48 41 52 41 43 54 45 52         ; "04__CHARACTER"
;
3EFC: 09 84 81                                       ; 09 bytes to 8184
3EFF: 30 35 00 00 43 4F 4C 4F 52                     ; "05__COLOR"  
;
3F08: 0F C4 81                                       ; 0F bytes to 81C4
3F0B: 30 36 00 00 42 45 41 4D 00 41 44 4A 55 53 54   ; "06__BEAM_ADJUST"  
;
3F1A: 00                                             ; End of copies 

; Unused end of ROM
;
3F1B: 00 00 00 00 00
3F20: 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
3F30: 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
3F40: 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
3F50: 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
3F60: 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
3F70: 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
3F80: 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
3F90: 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
3FA0: 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
3FB0: 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
3FC0: 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
3FD0: 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
3FE0: 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
3FF0: 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
;
3FFF: 03 ; Bring ROM chip 3 check value to FF
