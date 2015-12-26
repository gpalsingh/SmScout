from Tkinter import *
from API import swApi as api


def populateNationsList(li):
    home = api.HomePage()
    nation_and_link = home.get_leagues_list()

    n = nation_and_link.keys()
    for i, x in enumerate(sorted(n)):
        li.insert(i, x)

def nationScreen(root, sw=3):

    heading = Label(root, text='Select Nation')
    heading.grid(row=0, column=0, columnspan=sw)

    search = Entry(root)
    search.grid(row=1, column=0, columnspan=sw-1)
    search_b = Button(root, text='Search')
    search_b.grid(row=1, column=sw-1)

    scrollbar = Scrollbar(root, orient=VERTICAL)
    nations = Listbox(root, height=max(10, sw-2), yscrollcommand=scrollbar.set)
    populateNationsList(nations)
    nations.grid(row=3, column=0, columnspan=sw-1)
    scrollbar.config(command=nations.yview)
    scrollbar.grid(row=3, column=sw-1, rowspan=sw)

    start = Button(root, text='Start')
    start.grid(row=4, column=0, columnspan=sw)



root = Tk()
nationScreen(root)
root.mainloop()