shiny-ninja
===========

Requirements
------------

Requires Python 2.7 and Pygame 1.9.

Compatibility
-------------

Everything works on Mac OS X Yosemite, and the matchmaking server definitely works on Windows 7. The only problem noticed
with Windows 7 is that it crashed when trying to use the Man-in-the-Middle script (mitm.py).



Quick Start
-----------

In order to play a simple two-player game, open up a command prompt or terminal and run

  cd ShinyNinja
  python server.py

to start up the matchmaking server. The terminal should print as the first line an IP address; this is the IPv4 address
of the matchmaking server.

NOTE: this IP address may not be the correct one on Windows, although it seems to work on Mac
OS X just fine. In order to get the accurate LAN IP address in Windows, use the `ipconfig` command line program.

Then, on two terminals connected to the same LAN as the matchmaking server (or even
both on the same machine as the matchmaking server), run

  cd ShinyNinja
  python client.py x.x.x.x 2
  
where x.x.x.x is the IP address of the matchmaking server. Once both client terminals have connected to the server, the game
should start! The controls are:

MOVE:   Arrow keys
ATTACK: Space bar

Cheating
--------

Note: A player cheating with mitm.py must be on a different machine than the matchmaking server due to port conflicts.

If playing a 4-player game, three of the players should connect normally to the matchmaking server, but the cheating one
first must run

  cd ShinyNinja
  python mitm.py x.x.x.x
  
where x.x.x.x is the IP address of the matchmaking server. Then, once the Man-in-the-Middle is listening, the cheater must
open another terminal and run the command

  cd ShinyNinja
  python client.py y.y.y.y 4

where y.y.y.y is the IP address of the machine running the mitm.py (printed out in the mitm.py terminal). The game should
start and the cheating player should win in about a second.

Advanced
--------

In order to use a different protocol, simply add the appropriate argument when running the client program. Lockstep is

  python client.py x.x.x.x n lockstep
  
and Asynchronous Synchronization is

  python client.py x.x.x.x n as
  
where x.x.x.x is the matchmaking server IP address and n is the desired number of players. All clients should use the same
protocol in order for the game to run properly.
