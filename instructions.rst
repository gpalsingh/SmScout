Downloader
----------
The swDownloader is the main file which is responsible for fetching all the data. To run it use the command
``python swDownloader.py``. After that select the Nation, then league. You will be prompted to continue
incomplete session if you had previously started a download for the same league and it wasn't completed.
The options for the league will be saved automatically in a file with the name of the country in which the league
is played. The data downloaded will be according to the league standings( Higher teams first ).

Options available are:

- To continue data download for latest english league : ``python swDownloader.py < england.txt``. 
- ``-m`` or ``--mins``
    To get data for only for players with minutes more than 500 : ``python swDownloader.py - m 500``
- ``-a`` or ``--age``
    To set minimum age bar of 20 : ``python swDownloader.py -a 20``
- ``-g`` or ``--goals``
    To set minimum goals bar of 6 : ``python swDownloader.py -g 6``
- ``-v`` or ``--verbose``
    To turn on extra text : ``python swDownloader.py -v``
- ``-q`` or ``--quiet``
    To turn off almost every text : ``python swDownloader.py -q``
- ``-n`` or ``--new-session``
    To start from begining even if incomplete session( in case
    matches have been played in between) : ``python swDownloader.py -n``    

Build / Update Database
-------------------------
The downloader automatically builds the tables data once whole data has been downloaded but you have to do it yourself
if the download is not complete. This is ideal for cases when you don't want to wait for the data for teams 
in the lower parts of the table. The data written by buildTables is placed in SWdata/logs.db 

Options available are:

- ``-l`` or ``--leagues``
    To make tables for all leagues with "pro" or "prim" in their names : ``python tablesBuilder.py -l "pro" "prim"``
- ``-v`` or ``--verbose``
    To allow extra text : ``python tablesBuilder.py -v``
- ``-q`` or ``--quiet``
    To suppress extra text : ``python tablesBuilder.py -q``
- ``-o`` or ``--overwrite``
    To force overwrite by default : ``python tablesBuilder.py -o``

See downloaded data
-------------------
You can use some sql viewer of your choice or the ``browser.py`` module for this task.

Options available are:

- ``-l`` or ``--leagues``
    To get data of players in all leagues with 
    "liga" or "serie" in their names : ``python tablesBuilder.py "liga" "serie"``
- ``-A`` or ``--all``
    To show data for all leagues : ``python tablesBuilder.py -A``
- ``-g`` or ``--goals``
    To sort players by goals : ``python tablesBuilder.py -g``
- ``-m`` or ``--mins``
    To sort players by minutes played : ``python tablesBuilder.py -m``
- ``-a`` or ``--age``
    To sort players by age : ``python tablesBuilder.py -a``

By default the sorting variable is minutes. Each player's data will be shown one by one. If you want to skip
rest of the players of the league and skip to the next league, just enter any character or word.
If you want to terminate the program altogether just press ``Ctrl + D``





























