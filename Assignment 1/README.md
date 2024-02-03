# YouTube Application using RabbitMQ

This program simulates a simplified version of a YouTube application using RabbitMQ.

## Instructions

1. Run YoutubeServer.py to start the server.
   $ python3 YoutubeServer.py
2. Run Youtuber.py and User.py in any sequence multiple times and simultaneously. Multiple users can be logged in simultaneously and should receive notifications simultaneously.

   1. For subscribing to a channel:
      $ python3 User.py Nishaant s MKBHD
   2. For unsubscribing from a channel:
      $ python3 User.py Nishaant u LoganPaul
   3. For logging in/receiving notifications:
      $ python3 User.py Nishaant
