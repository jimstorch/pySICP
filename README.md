# pySICP
Example of using Python to send **Serial Interface Communications Protocol** (SICP) commands
to Philips Digital Signage.  The newer versions have the backcronymn **Serial/Ethernet Interface
Communications Protocol**.

This is not a full-featured library but rather a couple of scripts to turn the display on and
off but should give anyone familar with Python a helpful start to controlling their signage.

## Background
I use a Raspberry Pi as a network status montitor connected to a Philips BDL4771V 47" Display.
Rather than hunt for the remote, I wanted it to turn on and off automatically with the work
day.

I noticed that it had a 9 pin serial port and dug into how to control it.

## Physical Serial Interface
You may see two DB9 connectors -- one labeled **RS232C In** and the other labelled **RS232C Out**.
We want the **In** connector.  The other one is used to chain the next display in a wall of them
so everything can be controlled by the same serial connection.

We only need three wires; *transmit* (TX), *receive* (RX), and *ground* (GND).  This is a male 
connector which typically (but not always) indicated **Data Terminal Equipment** (DTE) as 
opposed to something like a dial-up modem which is **Data Carrier Equipment** (DCE). There
are conflicting definitions for what DTE/DCE stand for but they are all pretty close.

The important thing to understand is that when you wire a DTE to a DCE using a 1-for-1 pintout, 
the DTE's *transmit* connects to the DCE's *receive* and the vice versa.

I'm going to assume you are using a common *USB serial adapter*.
<img src="https://github.com/jimstorch/pySICP/blob/main/usb_serial_adapter.jpg" width=256p>

But here we run into our first complication; the *USB serial adapter* you're using is *also a male DTE*
connector.  This means we need to fix a couple issues;
* The physical connectors don't fit as both are male pins.
* Pin 3 is Transmit on both.
* Pin 2 is Receive on both. 

<img src="https://raw.githubusercontent.com/jimstorch/pySICP/main/f2f_null_modem.jpg" width=256px>
You need a combination *gender adapter* and [Null Modem](https://en.wikipedia.org/wiki/Null_modem).
You can buy these on Amazon as tiny wedges or you can get two female DB9 connectors and
wire your own like so;
* Pin 5 to Pin 5
* Pin 3 to Pin 2
* Pin 2 to Pin 3

## Data Settings
All the Philips appear to use the same port settings;
* 9600 baud
* 8 data bits
* no parity
* 1 stop bit
* flow control none

## The Protocol
Oh boy.  I was expecting something like the old [AT modem controls](https://en.wikipedia.org/wiki/Hayes_command_set)
where I could connect to the port and just type commands. Yeah no.
* SICP is a *binary* protocol.
* Commands are sent as packets with *length* and *checksum* bytes.
* There are multiple, incompatible versions.  This bit me.

I'm including PDFs of all the versions I could find.

### Finding the SICP version
This is how I did it, your display may vary.  It's possible the versions for each model are documented somewhere...
1. Connected the display to a network with DCHP at least temporarily.
2. Use the remote to open *Menu*, *Configuration 1*, *Network Settings* and note the IP address.
3. While you're there, got to *Advanced Option*, and get the *Monitor ID* as you may need it. Probably **1**.
4. Open a web browser and go to http://[Step 2 IP Address]/html
5. Log in as *admin* with the password *000000*
6. The first tab was *Power Settings* and the first box was *SICP version*.  Mine was 1.7.

### Talking to the Display
This thing did not want to give me anything to indicate I had a connection. I tried cold starts hoping it would
send a boot message to the port like a like of gear -- nope.  I sent packets based on a PDF for SICP version 1.99
I found on the Internet but nothing.

My set reported itself as SICP version 1.7.  I kept hunting and eventually found a PDF for version 1.6 and finally
got a reply;
```python
b'\x05\x01\x00\x06\x02'
```
Five bytes?  According to the docs, this was *"Command is well executed."**

So while most of the protocol versions worked on 6+ byte packets, mine wanted 5:

| Index | Byte Field          | Description |
| ----  | -----               | ----------- |
|  0    | Packet Length       | Packet Size.  This is the length of the entire packet, including this byte and the checksum  |
|  1    | Monitor ID          | This should be the number from step 3 above. |
|  2    | Command             | Given as hex codes in the docs 
|  *3+* | Possible arguments  | Optional depending on the command | 
| Final | Checksum            | Sum of *Exclusive OR*'ing all preceding bytes in the packet |

For newer displays, there will be an additional **Group** field after the **Monitor ID**:

| Index | Byte Field          | Description |
| ----  | -----               | ----------- |
|  0    | Packet Length       | Packet Size.  This is the length of the entire packet, including this byte and the checksum  |
|  1    | Monitor ID          | This should be the number from step 3 above. |
| **2** | **Group ID**        | **I'm guessing this is for controlling part of a display matrix, i.e. giant TV wall** |
|  3    | Command             | Given as hex codes in the docs 
|  *4+* | Possible arguments  | Optional depending on the command | 
| Final | Checksum            | Sum of *Exclusive OR*'ing all preceding bytes in the packet |

**Note**: The PDFs use index 1 instead of index 0 but we're programmers here.

## Requirements
[pySerial](https://github.com/pyserial/pyserial).  I'm using Python 3 and installed mine with;

```sh
$ pip3 install pyserial
```

I coded this using Python 3 and used the new f-string formatting introduced in Python 3.6 (which is so darn
brilliant) for a couple lines.  Sadly, version of Raspian on my Raspberry Pi was still on 3.5.3 so I had to edit
them.

## Modifying the Code
For newer sets you will probably need to add the **Group**. So line 45 in **on.py** and **off.py** becomes;
```python
cmd = [MONITOR, GROUP, SET_POWER_STATE, PWR_OFF]
```
Don't forget to define *GROUP* as whatever group you need, probably 0x00.  The proper response in line 51 will probably change to;
```python
if resp == b'\x06\x01\x00\x00\x06\x01':
```
These are my best guesses as I don't have another set to test.
