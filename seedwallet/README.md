# Seed Wallet

I wrote this script as part of exploring the world of cryptocurrency.  My holdings in cryptocurrency are meger, and I currently hold TENS of US dollars in cryptocurrency. This is secure enough for my purpose. I am not an expert, so evaluate the risks before you put any significant investment in cryptocurrency at risk on some random person’s solution to the wallet problem. I am not responsible if your coins are lost or stolen.

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details.

# About this python script

This is a quick and dirty python script to generate a printable "paper wallet" from a electrum seed.

It can request the seed directly from Electrum, using the optional -w parameter to point directly to a wallet file other than the default.

If your wallet is encrypted, then it should pass through Electrum's passwrod prompt to the terminal. (Not quite sure why this works)

The wallet will open in chromium-browser (or Safari on Mac OS) for you to print.  Make sure to clear your caches when you're done.

Alternatively, you can use the -e option to enter the seed phrase directly.

Use at your own risk.