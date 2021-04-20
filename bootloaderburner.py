#!/usr/bin/env python3

import serial
import sys

sport = ""
if len(sys.argv) > 1:
    sport = sys.argv[1]

flasherfile = "rzg2-flash-writer/AArch64_output/AArch64_Flash_writer_SCIF_DUMMY_CERT_E6300400_ek874.mot"

flasherwaittext = b"-- Load Program to SystemRAM ---------------\r\nplease send !"
flasherreadytext = b">"
extcsdindextext = b"Please Input EXT_CSD Index"
extcsdvaluetext = b"Please Input Value"
writeareatext = b"Select area"
writesectortext = b"Please Input Start Address in sector"
writeaddresstext = b"Please Input Program Start Address"
sendrequesttext = b"please send"
speeduptext1 = b"Change to 460.8Kbps baud rate setting of the SCIF."
speeduptext2 = b"Please change to 921.6Kbps baud rate setting of the terminal."
speeduptext3 = b"Please change to 460.8Kbps baud rate setting of the terminal."

bootloadermap = [
    {"part": "1", "sector": "0", "address": "E6320000", "file": "arm-trusted-firmware/deploy/g2e-emmc/bootparam_sa0.srec"},
    {"part": "1", "sector": "1E", "address": "E6304000", "file": "arm-trusted-firmware/deploy/g2e-emmc/bl2.srec"},
    {"part": "1", "sector": "180", "address": "E6320000", "file": "arm-trusted-firmware/deploy/g2e-emmc/cert_header_sa6.srec"},
    {"part": "1", "sector": "200", "address": "44000000", "file": "arm-trusted-firmware/deploy/g2e-emmc/bl31.srec"},
    {"part": "2", "sector": "0", "address": "50000000", "file": "renesas-u-boot-cip/deploy/u-boot-elf.srec"},
]

if len(sport) == 0:
    sport = "/dev/ttyUSB0"

print("RZG2 flash burner helper started.")
sp = serial.Serial(sport, 115200, timeout=0.5)
if sp is None:
    print("Failed to open serial port %s!" % sport)
    exit()

print("Open serial port %s successfully." % sport)

print("Waiting for download mode prompt...")
while True:
    rdata = sp.read(8192)
    if flasherwaittext in rdata:
        break

print("Download mode detected, sending flash burner...")

f = open(flasherfile, "rb")
tlen = 0
while True:
    fdata = f.read(4096)
    fdatalen = len(fdata)
    if fdatalen == 0:
        break;
    sp.write(fdata)
    tlen += fdatalen
    print('\r%d bytes completed.' % tlen, end='')
f.close()
sp.write(b'.\r\n')
print('')

while True:
    rdata = sp.read(8192)
    if flasherreadytext in rdata:
        break

sp.write(b'\r\n')
while True:
    rdata = sp.read(8192)
    if flasherreadytext in rdata:
        break

print("Flash burner ready, try to speed up.")

sspeed = 115200

sp.write(b'SUP\r\n')
while True:
    rdata = sp.read(8192)
    if speeduptext2 in rdata:
        sspeed = 921600
        break
    elif speeduptext1 in rdata:
        sspeed = 460800
        break
    elif speeduptext3 in rdata:
        sspeed = 460800
        break

sp.close()
sp = serial.Serial(sport, sspeed, timeout=0.5)

sp.write(b'\r\n')
while True:
    rdata = sp.read(8192)
    if flasherreadytext in rdata:
        break

print("Speed up to %d bps OK, setting eMMC mode..." % sspeed)

sp.write(b'EM_SECSD\r\n')
while True:
    rdata = sp.read(8192)
    if extcsdindextext in rdata:
        break
sp.write(b'b1\r\n')
while True:
    rdata = sp.read(8192)
    if extcsdvaluetext in rdata:
        break
sp.write(b'a\r\n')
print("Set EXT_CSD[B1] = 0x0A")
while True:
    rdata = sp.read(8192)
    if flasherreadytext in rdata:
        break
sp.write(b'EM_SECSD\r\n')
while True:
    rdata = sp.read(8192)
    if extcsdindextext in rdata:
        break
sp.write(b'b3\r\n')
while True:
    rdata = sp.read(8192)
    if extcsdvaluetext in rdata:
        break
sp.write(b'8\r\n')
while True:
    rdata = sp.read(8192)
    if flasherreadytext in rdata:
        break
print("Set EXT_CSD[B3] = 0x08")

print("Sending ARM Trusted Firmware SA0...")
sp.write(b'EM_W\r\n')
while True:
    rdata = sp.read(8192)
    if writeareatext in rdata:
        break
cmd = str("%s\r\n" % bootloadermap[0]['part'])
sp.write(cmd.encode())
while True:
    rdata = sp.read(8192)
    if writesectortext in rdata:
        break
cmd = str("%s\r\n" % bootloadermap[0]['sector'])
sp.write(cmd.encode())
while True:
    rdata = sp.read(8192)
    if writeaddresstext in rdata:
        break
cmd = str("%s\r\n" % bootloadermap[0]['address'])
sp.write(cmd.encode())
while True:
    rdata = sp.read(8192)
    if sendrequesttext in rdata:
        break
f = open(bootloadermap[0]['file'], "rb")
tlen = 0
while True:
    fdata = f.read(4096)
    fdatalen = len(fdata)
    if fdatalen == 0:
        break;
    sp.write(fdata)
    tlen += fdatalen
    print('\r%d bytes completed.' % tlen, end='')
f.close()
sp.write(b'.\r\n')
print('')
while True:
    rdata = sp.read(8192)
    if flasherreadytext in rdata:
        break
print("Send ARM Trusted Firmware SA0 completed.")

print("Sending ARM Trusted Firmware BL2...")
sp.write(b'EM_W\r\n')
while True:
    rdata = sp.read(8192)
    if writeareatext in rdata:
        break
cmd = str("%s\r\n" % bootloadermap[1]['part'])
sp.write(cmd.encode())
while True:
    rdata = sp.read(8192)
    if writesectortext in rdata:
        break
cmd = str("%s\r\n" % bootloadermap[1]['sector'])
sp.write(cmd.encode())
while True:
    rdata = sp.read(8192)
    if writeaddresstext in rdata:
        break
cmd = str("%s\r\n" % bootloadermap[1]['address'])
sp.write(cmd.encode())
while True:
    rdata = sp.read(8192)
    if sendrequesttext in rdata:
        break
f = open(bootloadermap[1]['file'], "rb")
tlen = 0
while True:
    fdata = f.read(4096)
    fdatalen = len(fdata)
    if fdatalen == 0:
        break;
    sp.write(fdata)
    tlen += fdatalen
    print('\r%d bytes completed.' % tlen, end='')
f.close()
sp.write(b'.\r\n')
print('')
while True:
    rdata = sp.read(8192)
    if flasherreadytext in rdata:
        break
print("Send ARM Trusted Firmware BL2 completed.")

print("Sending ARM Trusted Firmware SA6...")
sp.write(b'EM_W\r\n')
while True:
    rdata = sp.read(8192)
    if writeareatext in rdata:
        break
cmd = str("%s\r\n" % bootloadermap[2]['part'])
sp.write(cmd.encode())
while True:
    rdata = sp.read(8192)
    if writesectortext in rdata:
        break
cmd = str("%s\r\n" % bootloadermap[2]['sector'])
sp.write(cmd.encode())
while True:
    rdata = sp.read(8192)
    if writeaddresstext in rdata:
        break
cmd = str("%s\r\n" % bootloadermap[2]['address'])
sp.write(cmd.encode())
while True:
    rdata = sp.read(8192)
    if sendrequesttext in rdata:
        break
f = open(bootloadermap[2]['file'], "rb")
tlen = 0
while True:
    fdata = f.read(4096)
    fdatalen = len(fdata)
    if fdatalen == 0:
        break;
    sp.write(fdata)
    tlen += fdatalen
    print('\r%d bytes completed.' % tlen, end='')
f.close()
sp.write(b'.\r\n')
print('')
while True:
    rdata = sp.read(8192)
    if flasherreadytext in rdata:
        break
print("Send ARM Trusted Firmware SA6 completed.")

print("Sending ARM Trusted Firmware BL31...")
sp.write(b'EM_W\r\n')
while True:
    rdata = sp.read(8192)
    if writeareatext in rdata:
        break
cmd = str("%s\r\n" % bootloadermap[3]['part'])
sp.write(cmd.encode())
while True:
    rdata = sp.read(8192)
    if writesectortext in rdata:
        break
cmd = str("%s\r\n" % bootloadermap[3]['sector'])
sp.write(cmd.encode())
while True:
    rdata = sp.read(8192)
    if writeaddresstext in rdata:
        break
cmd = str("%s\r\n" % bootloadermap[3]['address'])
sp.write(cmd.encode())
while True:
    rdata = sp.read(8192)
    if sendrequesttext in rdata:
        break
f = open(bootloadermap[3]['file'], "rb")
tlen = 0
while True:
    fdata = f.read(4096)
    fdatalen = len(fdata)
    if fdatalen == 0:
        break;
    sp.write(fdata)
    tlen += fdatalen
    print('\r%d bytes completed.' % tlen, end='')
f.close()
sp.write(b'.\r\n')
print('')
while True:
    rdata = sp.read(8192)
    if flasherreadytext in rdata:
        break
print("Send ARM Trusted Firmware BL31 completed.")

print("Sending U-Boot...")
sp.write(b'EM_W\r\n')
while True:
    rdata = sp.read(8192)
    if writeareatext in rdata:
        break
cmd = str("%s\r\n" % bootloadermap[4]['part'])
sp.write(cmd.encode())
while True:
    rdata = sp.read(8192)
    if writesectortext in rdata:
        break
cmd = str("%s\r\n" % bootloadermap[4]['sector'])
sp.write(cmd.encode())
while True:
    rdata = sp.read(8192)
    if writeaddresstext in rdata:
        break
cmd = str("%s\r\n" % bootloadermap[4]['address'])
sp.write(cmd.encode())
while True:
    rdata = sp.read(8192)
    if sendrequesttext in rdata:
        break
f = open(bootloadermap[4]['file'], "rb")
tlen = 0
while True:
    fdata = f.read(4096)
    fdatalen = len(fdata)
    if fdatalen == 0:
        break;
    sp.write(fdata)
    tlen += fdatalen
    print('\r%d bytes completed.' % tlen, end='')
f.close()
sp.write(b'.\r\n')
print('')
while True:
    rdata = sp.read(8192)
    if flasherreadytext in rdata:
        break
print("Send U-Boot completed.")

print("Bootloader burning completed! Please poweroff the board.")
sp.close()
