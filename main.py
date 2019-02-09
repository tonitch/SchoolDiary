#!/bin/python3
from tkinter import Tk, Frame, Label, Text, Button, Canvas, END
from pathlib import Path
import datetime
import sqlite3

DOTW = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi"]  # Days of the week


class App(Frame):
    def __init__(self, master, db):
        super().__init__(master)
        self.week = 0
        self.db = db
        self.DrawHUD()
        self.UpdateHud()
        self.mainloop()

    def DrawHUD(self):
        CanLine = Canvas(self.master, height=0)
        CanLine.grid(row=2, column=0, columnspan=5)
        self.labelDates = []
        self.TextsDev = []
        self.TextsLec = []
        for i in range(5):
            labelday = Label(self.master, text=DOTW[i])
            labelday.grid(row=0, column=i)

            labelDate = Label(self.master, text="00/00")
            labelDate.grid(row=1, column=i)
            self.labelDates.append(labelDate)

            CBdev = Label(self.master, text="Devoir")
            CBdev.grid(row=3, column=i)

            TextDev = Text(self.master, height=5, width=10)
            TextDev.grid(row=4, column=i)
            self.TextsDev.append(TextDev)

            CBlec = Label(self.master, text="Leçon")
            CBlec.grid(row=5, column=i)

            TextLec = Text(self.master, height=5, width=10)
            TextLec.grid(row=6, column=i)
            self.TextsLec.append(TextLec)

        LeftButton = Button(self.master, text="<--", command=self.PrevWeek)
        LeftButton.grid(row=7, column=0)

        self.DateSel = Label(self.master, text="00/00 - 00/00")
        self.DateSel.grid(row=7, column=1, columnspan=3)

        RightButton = Button(self.master, text="-->", command=self.NextWeek)
        RightButton.grid(row=7, column=4)

        SaveButton = Button(self.master, text="Save", width=50, command=self.Save)
        SaveButton.grid(row=8, column=0, columnspan=5)

    def DetermineDate(self, today=datetime.timedelta()):
        self.today = datetime.date.today() + today
        self.monday = self.today - datetime.timedelta(days=self.today.weekday())
        self.sunday = self.monday + datetime.timedelta(days=4)
        return [self.today, self.monday, self.sunday]

    def UpdateHud(self, week=0):
        dates = self.DetermineDate(datetime.timedelta(weeks=week))
        self.DateSel.config(text="{} - {}".format(dates[1], dates[2]))

        for i in range(5):
            _date = datetime.timedelta(days=i)
            self.labelDates[i].config(text=dates[1] + _date)
            self.UpdateData(i, dates[1] + _date)
            if dates[1] + _date == datetime.date.today():
                self.labelDates[i].config(bg="green")
            else:
                self.labelDates[i].config(bg=self.master.cget("bg"))

    def UpdateData(self, column, date):
        dbData = self.db.GetData(date)
        devData = dbData[1]
        lecData = dbData[2]

        textDev = self.TextsDev[column]
        textDev.delete("1.0", END)
        textDev.insert(END, devData)

        textLec = self.TextsLec[column]
        textLec.delete("1.0", END)
        textLec.insert(END, lecData)

    def Save(self):
        for i in range(5):
            _textdev = self.TextsDev[i].get("1.0", END).strip()
            _textlec = self.TextsLec[i].get("1.0", END).strip()
            _date = datetime.timedelta(days=i)
            if _textdev != "" or _textlec != "":
                self.db.PutData(self.monday + _date, _textdev, _textlec)
            else:
                self.db.deleteData(self.monday + _date)

    def NextWeek(self):
        self.week = self.week + 1
        self.UpdateHud(week=self.week)

    def PrevWeek(self):
        self.week = self.week - 1
        self.UpdateHud(week=self.week)


class bdd():
    def __init__(self):
        home = str(Path.home())
        self.conn = sqlite3.connect(home + "/.jdc.db")
        self.curr = self.conn.cursor()
        self.curr.execute("""CREATE TABLE IF NOT EXISTS jdc (
                            date TEXT NOT NULL,
                            devoir TEXT,
                            Lecon TEXT);""")

    def GetData(self, date):
        self.curr.execute("SELECT * FROM jdc WHERE date='{}'".format(date))
        data = self.curr.fetchone()
        if data is None:
            return ["", "", ""]
        return data

    def PutData(self, date, devoir, lecon):
        self.deleteData(date)
        self.curr.execute(
            "INSERT INTO jdc VALUES (?,?,?);",
            (str(date), devoir, lecon))
        self.conn.commit()

    def deleteData(self, date):
        self.curr.execute("DELETE FROM jdc WHERE date='{}'".format(str(date)))
        self.conn.commit()


def main():
    root = Tk()
    db = bdd()
    App(root, db)


if __name__ == "__main__":
    main()
