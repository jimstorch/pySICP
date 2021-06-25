# pySICP
Example of using Python to send **Serial Interface Communications Protocol** (SICP) commands
to Philips Digital Signage.  The newer versions have the backcronymn **Serial/Ethernet Interface
Communications Protocol**.

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
opposed to something like a dial-up modem which is **Data Carrier Equipment** (DCE).  
Note: there are conflicting definitions for what DTE/DCE stand for but they are all pretty close.

The important thing to understand is that when you wire a DTE to a DCE using a 1-for-1 pintout, 
the DTE's *transmit* connects to the DCE's *receive* and the vice versa.

I'm going to assume you are using a common *USB serial adapter*.

But here we run into our first complication; the *USB serial adapter* you're using is *also a male DTE*
connector.  This means we need to fix a couple issues;
* The physical connectors don't fit as both are pins.
* Pin 3 is Transmit on both.
* Pin 2 is Receive on both. 

You need a combination *gender adapter* and [Null Modem](https://en.wikipedia.org/wiki/Null_modem).
You can buy these on Amazon in as tiny gold wedges or you can get two female DB9 connectors and
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
* There are multiple, incompatible versions.



To make matters worse, it's a protocol with a lot of changes.  
SICP is a binary protocol that includes a [checksum]



(https://en.wikipedia.org/wiki/Longitudinal_redundancy_check) byte.    
