What this program does
----------------------
This program serves as an automatic scouting system for finding  emerging talents in football leagues 
all around the world to help in playing `SoccerManger <https://www.soccermanager.com>`_.

==============
Instructions
==============
1. Download the repo
        - Click the "Download as ZIP" from the right side
        -  or if you have git you can use the "git pull" command to copy it directly to your machine
2. Get Python
        Install python 2.7 if you don't already have it. It doesn't work with python 3, yet.
3. Unzip the file
4. Open terminal
5. Move to ``SmScout`` folder 
6. Run the ``start.py`` script by typing ``python start.py``
7. Browse the saved data
    - Use your favourite sql viewer
    - or run ``python browser.py -l "league_name"``. Replace league name by the name of the league for which data was downloaded.
    - The data is stored in ``SmScout/SWdata/databases``

Use ``-h`` option to get help for any of the two modules.
More detailed instructions are available in `instructions.rst <https://github.com/gpalsingh/SmScout/blob/master/instructions.rst>`_