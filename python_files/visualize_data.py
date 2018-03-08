import matplotlib.pyplot as plt
import sqlite3

conn = sqlite3.connect("test_db")
curs = conn.cursor()

tick_lst = ['INSY']

cnt = 0
while cnt < 2:
    curs.execute("SELECT * FROM data WHERE ticker=?", (tick_lst[cnt],))

    rows = curs.fetchall()

    # print(thing) for thing in rows
    opn = []
    high = []
    date = []

    for thing in rows:
        date.append(thing[1])
        opn.append(thing[2])
    # high.append(thing[3])
    # print(thing)

    plt.scatter(date, opn)
    plt.show()
    cnt += 1
