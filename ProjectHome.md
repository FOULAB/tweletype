Tweletype is a python program that will connect to Twitter, receive tweets from users that it is following, and transmit them as ASCII or Baudot characters to a serial port. It will also take a line of input from the serial port and send it to Twitter.

This allows you to use a Baudot or ASCII terminal, either printer or CRT based, as a Twitter interface.

Other useful features:
  * Prints any @replies directed at itself, even from people it is not following. Neat party trick!
  * Automatically stops accepting input at 140 characters and rings the terminal bell.
  * Ctrl-c cancels message if you make a mistake.
  * Kind of works with oauth.

Notes:
  * Baudot functionality depends on setserial to set custom baud rates, so Baudot may not work on Windows or other non-`*`nix environments. ASCII should work everywhere.