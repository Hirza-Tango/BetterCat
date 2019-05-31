# BetterCat - Like a NetCat shell but Better

## Description

Have you ever tried to use a netcat shell and thought, "I wish there was a better way"?
Well now there is!
BetterCat will connect to the shell and do the following:
- Disable saving of the session's history
- Enumerate the operating system, shell and supported terminal interfaces
- Spawn a TTY shell for programs that need them, like `sudo`
- Integrate the shell with your terminal!
  + You want colour? You got colour! (Yes, it's spelled with a _u_)
  + You want TAB completion? You got TAB completion!
  + Tired of trying to kill a command with *Control-C* only for it to kill your shell? No more!
  + Any other default control sequence for your terminal _should_ "Just work"
  + Even `vim` and `emacs` work just fine!

## Installation

`pip3 install -r requirements.txt`

## Usage

### Listening
Instead of `nc -lp <port>`, use `./BetterCat.py l <port>` to listen for incoming reverse shells.

### Connecting
Instead of `nc <host> <port>`, use `./Bettercat.py c <host> <port>` to connect to bind shells.

## Development
This was hacked together in about 2 days. I'll try to keep working on it, but if you'd like any features or fixes, feel free to ask!

### Upcoming features
- Support for more shells, terminals and operating systems
- Better teminal support enumeration
- Support for shells which are already TTYs
- Custom per-shell prompts
- More netcat-like features
- Support for resized terminals
- Methods for spawning a TTY that don't rely on python
- More reconnaisance
- Code cleanup

© Dylan Slogrove, 2019

