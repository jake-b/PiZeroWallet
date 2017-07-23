# PiZeroWallet
This repository contains some tools and information I used to build a pseudo-airgapped offline hardware wallet for cryptocurrency using a Raspberry Pi Zero 1.3

This is in support of a blog post you can find here:

    http://www.allaboutjake.com/pi-offline-crypto-wallet/

## Introudction
For various reasons, I have been experimenting with the Bitcoin and Etherium currencies. While I do not have a vast fortune, I still wanted to generate and store my private keys in a safe and secure manner.

What I really wanted was a Leger Nano S.  These at the time, however, are backorered for months.  So I started to explore methods for generating and storing keys.

I decided the Raspberry Pi Zero 1.3 was an good platform for this endevor:

- It has no onboard networking hardware, making it easy to maintain separation by simply never connecting a network interface.
- It is small, so when done, you can store the thing in a safe place, such as a safety deposit box.
- The serial gadget makes it possible to connect the Pi Zero to a host machine and login to the command line.  This is what I mean by "pseudo-airgapped".  Yes I am connecting the machine to another via USB... but in theory, only via a simple  serial connection.  I'm sure there are state-level hackers that could do something malicious with this connection, but I'm pretty satisfied that it is somewhat secure for my purposes.

The challenge was to build a Pi with all the necessary software while never connecting the Pi Zero to the internet.  What follows are my instructions on how I did this.

## Disclaimer

I am doing this to explore the world of cryptocurrency, not as an investment.  I currently hold TENS of US dollars in cryptocurrency.  This is secure enough for my purpose.   I am not an expert, so evaluate the risks before you put any significant investment in cryptocurrency at risk on some random person's solution to the wallet problem.  I am not responsible if your coins are lost or stolen.

## What's here

Some python scripts to support building a cold wallet:

 - **vendorize.py** - a tool to download a list of dependencies and tar/gz them into a single file, for transferrring to the Raspberry Pi Zero that has no internet connection
 - **seedwallet.py** - a tool to generate an HTML printable wallet of an Electrum seed phrase for printing.  Opens the generated wallet in a browser.