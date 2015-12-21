What this program does
----------------------
This program serves as an automatic scouting system for finding  emerging talents in football leagues 
all around the world to help in playing `SoccerManger <https://www.soccermanager.com>`_.

==============
Instructions
==============
Linux
-----
1. Download the repo
        - Click the "Download as ZIP" from the right side
        - Or if you have git you can use the "git pull" command to copy it directly to your machine
2. Install Python
        Install python 2.* if you don't already have it or using python 3.*
3. Move to ``SmScout`` folder (terminal)
        It is important that you run it from the same folder because data saving is done relatively and 
        will be saved at wrong place if you run it from outside. This I plan to remove by makin it a installable
        program. 
4. Enter the following command:
        - ``python swDownloader.py``
        - Select the leagues
5. Browse the saved data
    - Use your favourite sql viewer
    - or run ``python browsertest.py`` 
    - The data is stored in ``/SmScout/SWdata/logs.db``

Use ``-h`` option to get help for any of the two modules.
More detailed instructions are available in `instructions.rst <https://github.com/gpalsingh/SmScout/blob/master/instructions.rst>`_

Windows
-------
I will reccommend not to run this on Windows, although you could. Dos shell doesn't support the CSI sequences I use for
colored text. Moreover I have encountered several other bugs too. You are free to fork and change it for Windows. I can
then create a new branch from pull request.

I'll be updating regularly so look out for changes.
Feel free to join, give suggestions, use, anything...
