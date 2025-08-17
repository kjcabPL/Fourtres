import tkinter
from json import JSONDecodeError
from tkinter.ttk import Combobox

import pyperclip
import json
from tkinter import *
from tkinter import messagebox
from random import randint, choice, shuffle

IS_OPEN = True
GEN_PW = ""
GEN_MAX_CTR = 100
GEN_CALC = False
# STOREFILE = "data.txt"
STOREFILE = "stores.json"
STORED_DATA = {}
CUR_USER_DATA = []
PW_LENGTH = 20

# Variables for Color Manipulation during PW generation
CUR_BG = ""
canvasbgStart = "#FF0000"
canvasbgGen = "#FFF088"
startColor = (255, 0, 0)
endColor = (255, 240, 136)
incs = ( int((endColor[0] - startColor[0]) / GEN_MAX_CTR), int((endColor[1] - startColor[1]) / GEN_MAX_CTR), int((endColor[2] - startColor[2]) / GEN_MAX_CTR))
placeholderWS = "my.site.com"
placeholderUser = "my_user / dummy@testmail.com"

# ---------------------------- PASSWORD GENERATOR ------------------------------- #
def genPassword():
    global GEN_PW
    global GEN_CALC
    global CUR_BG

    GEN_CALC = True
    GEN_CUR_CTR = 0
    CUR_BG = startColor
    doGenAnimation(GEN_CUR_CTR)
    tbNewPw.insert(0, str(GEN_PW))
    disableButtons()
    canvas.config(bg=canvasbgStart)

def doGenAnimation(CTR):
    global GEN_PW
    global GEN_CALC
    global CUR_BG

    if GEN_CALC:
        if CTR < GEN_MAX_CTR:
            CTR += 1
            GEN_PW = CTR
            newPass = genRandomizedHash()
            tbNewPw.delete(0, tkinter.END)
            tbNewPw.insert(0, newPass)
            CUR_BG = ( CUR_BG[0] + incs[0], CUR_BG[1] + incs[1], CUR_BG[2] + incs[2] )
            bgColor = f"#{CUR_BG[0]:02X}{CUR_BG[1]:02X}{CUR_BG[2]:02X}"
            canvas.config(bg=bgColor)
            window.after(10, doGenAnimation, CTR)
        else:
            GEN_CALC = False
            pyperclip.copy(tbNewPw.get())
            disableButtons(False)
            canvas.config(bg=canvasbgGen)

def genRandomizedHash():
    letters = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u',
               'v', 'w', 'x', 'y', 'z', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P',
               'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
    numbers = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
    symbols = ['!', '#', '$', '%', '&', '(', ')', '*', '+']

    # Separate the password length to letter, number and symbol variance
    maxChars = PW_LENGTH
    nr_letters = randint(int(maxChars / 4), int(maxChars / 2))
    maxChars -= nr_letters
    nr_numbers = randint(int(maxChars / 3), int(maxChars / 2))
    maxChars -= nr_numbers
    nr_symbols = maxChars

    # Generate a new password from combined list comprehension arithmetic
    newPass = [choice(letters) for _ in range(0, nr_letters)] + [choice(numbers) for _ in range(0, nr_numbers)] + [choice(symbols) for _ in range(0, nr_symbols)]
    shuffle(newPass)
    newPass = "".join(newPass)
    return newPass


# ---------------------------- PASSWORD FUNCTIONS ------------------------------- #
def writeNewStoreFile():
    with open(STOREFILE, mode="w") as file:
        file.write("")

def savePWData():
    newpw = tbNewPw.get()
    website = tbWebsite.get()
    user = tbUser.get()

    if website == "":
        messagebox.showerror("Error Saving Record", "Website should not be empty")
        return
    elif user == "":
        messagebox.showerror("Error Saving Record", "Username should not be empty")
        return
    elif newpw == "":
        if not messagebox.askokcancel("Saving Record", "Password field is empty. Are you sue you want to continue?"):
            tbNewPw.focus()
            return

    # convert to json data
    curIndex = curData = ""
    currentRecord = {}
    isUpdateRecord = False
    msgSuccess = f"User record for {website} added to store file."
    data = {
        website: [{
            user: {
                "pw": newpw
            }
        }]
    }

    # open the contents of the store file
    try:
        with open(STOREFILE, mode="r") as file:
            curData = json.load(file)
    except FileNotFoundError:
            writeNewStoreFile()
            curData = data
    except JSONDecodeError:
        curData = data
    else:
        # curData.update(data)
        # TODO - if a website record already exists, ADD the user/email and its pw to that list instead
        # TODO - if a website already HAS that user/email, PROMPT before replacing the record
        # check if the user is already in the website records and either overwrite or add
        if len(STORED_DATA) > 0 and website in STORED_DATA:
            siteRecords = [data for data in STORED_DATA[website] if website in STORED_DATA]
            if len(siteRecords) > 0:
                for record in siteRecords:
                    if user in record:
                        curIndex = siteRecords.index(record)
                        currentRecord = record
                        isUpdateRecord = True
                        break
                # we found the user's record in the site, now we update and rewrite the full path in curData
                if user in currentRecord:
                    data = { "pw": newpw}
                    curData[website][curIndex][user].update(data)
                # we have a new user for the site, just add it as a new record
                else:
                    data = {
                        user: {
                            "pw": newpw
                        }
                    }
                    curData[website].append(data)
        else:
            curData.update(data)

    # Prompt user before replacing record if it's a record update
    if isUpdateRecord:
        if not messagebox.askokcancel(f"Update website record for {user}", f"A User {user} already exists in {website}, overwrite this record?"):
            return
        else:
            msgSuccess = f"{user}'s record for {website} updated successfully."

    try:
        with open(STOREFILE, mode="w") as file:
             json.dump(curData, file, indent=2)
    except FileNotFoundError:
        messagebox.showerror("Error Saving Data", "Unable to find store file: " + STOREFILE)
    else:
        messagebox.showinfo("New Record Added", msgSuccess)
    finally:
        tbNewPw.delete(0,tkinter.END)
        tbWebsite.delete(0, tkinter.END)
        tbUser.delete(0, tkinter.END)

def readPWData():
    global STORED_DATA
    try:
        with open(STOREFILE, mode="r") as file:
            STORED_DATA = json.load(file)
    except FileNotFoundError:
        writeNewStoreFile()
    except JSONDecodeError:
        STORED_DATA = {}

def searchPWData():
    global CUR_USER_DATA
    userlist = []
    website = tbWebsite.get()
    if website == "":
        messagebox.showerror("Search Error", "No Website Provided")
        return
    try:
        siteRecord = [ data for data in STORED_DATA[website] if website in STORED_DATA ]
    except KeyError:
        messagebox.showerror("Search Error", f"No Users recorded for website: {website}")
        CUR_USER_DATA = []
    else:
        if len(siteRecord) > 0:
            # for items in user_data:
            for record in siteRecord:
                user_data = record.keys()
                for username in user_data:
                    userlist.append(username)
                    pw = record[username]["pw"]
                    CUR_USER_DATA.append({ "user": username, "pw": pw })

    finally:
        listUsers["values"] = tuple(userlist)
        listUsers.set("")
        if len(userlist) > 0:
            listUsers.set(userlist[0])


# ---------------------------- UI FUNCTIONS ------------------------------- #

def closeWindow():
    global IS_OPEN
    if messagebox.askokcancel("Exit", "Exit Fourtres?"):
        IS_OPEN = False
        window.destroy()

def disableButtons(state = True):
    val = tkinter.DISABLED
    if not state:
        val = tkinter.NORMAL

    btGenPW["state"] = val
    btAdd["state"] = val
    btSearch["state"] = val

# When the searchbox is changed to a different user
def displayPWData(event):
    global CUR_USER_DATA
    curUser = listUsers.get()
    data = [ item["pw"] for item in CUR_USER_DATA if item["user"] == curUser ]
    print(data)

    if len(data) > 0:
        tbUser.delete(0, tkinter.END)
        tbUser.insert(0, curUser)
        tbNewPw.delete(0, tkinter.END)
        tbNewPw.insert(0, data[0])

def entryFocused(event):
    component = event.widget
    textItem = component.get()
    if textItem == placeholderUser or textItem == placeholderWS:
        component.delete(0, tkinter.END)

def entryLeaveFocus(event):
    component = event.widget
    textItem = component.get()
    if textItem == "":
        if component == tbWebsite:
            tbWebsite.insert(0, placeholderWS)
        elif component == tbUser:
            tbUser.insert(0, placeholderUser)


# ---------------------------- UI & WINDOW SETUP ------------------------------- #

window = Tk()
window.config(padx=25, pady=25)
window.title("Fourtres Password Builder")
window.resizable(False, False)
readPWData()
canvasbg = window["bg"]

lock_img = PhotoImage(file="logo.png")
canvas = Canvas(width=200, height=200)
canvas.config(bg=canvasbg)
canvas.create_image(100, 100, image=lock_img )

# Panels and component groupings
groupMain = LabelFrame(text = "User Record", padx = 10, pady = 10)
groupGens = LabelFrame(text = "Password Generation", padx = 10, pady = 10)
groupRecords = LabelFrame(text = "Record Search", padx = 10, pady = 10)

# labels
lblWebsite = Label(groupMain, text="Website:", width = 15 )
lblUser = Label(groupMain, text="Email/Username:", width = 15)
lblNewPW = Label(groupMain, text="New Password:", width = 15)

# Entry Fields
tbWebsite = Entry(groupMain, width = 50)
tbWebsite.insert(0, placeholderWS)
tbUser = Entry(groupMain, width = 50)
tbUser.insert(0, placeholderUser)
tbNewPw = Entry(groupMain, width = 50)

# buttons & other components
btAdd = Button(groupMain, text = "Add Record", width = 60, pady = 5)
btGenPW = Button(groupGens, text = "Generate Password", width = 60, pady = 5)
btSearch = Button(groupRecords, text = "Search For Website Records", width = 40, pady = 5)

listUsers = Combobox(groupRecords, values=[], width = 16, height = 10)
listUsers.set("")


# ---------------------------- WINDOW & COMPONENTS SETUP ------------------------------- #

# function assignments
window.protocol("WM_DELETE_WINDOW", closeWindow)
btGenPW["command"] = genPassword
btAdd["command"] = savePWData
btSearch["command"] = searchPWData

# event binding assignments
listUsers.bind("<<ComboboxSelected>>", displayPWData)
tbUser.bind("<FocusIn>", entryFocused)
tbUser.bind("<FocusOut>", entryLeaveFocus)
tbWebsite.bind("<FocusIn>", entryFocused)
tbWebsite.bind("<FocusOut>", entryLeaveFocus)

# arrangements
canvas.grid(row = 0, column = 0, columnspan = 3, rowspan = 2)

groupMain.grid(row = 2, column = 0, columnspan = 3)
lblWebsite.grid(row = 0, column = 0)
lblUser.grid(row = 1, column = 0)
tbWebsite.grid(row = 0, column = 1, columnspan = 2)
tbUser.grid(row = 1, column = 1, columnspan = 2)
lblNewPW.grid(row = 2, column = 0)
tbNewPw.grid(row = 2, column = 1, columnspan = 2)
btAdd.grid(row = 3, column = 0, columnspan = 3, pady = 5)

groupGens.grid(row = 3, column = 0, columnspan = 3)
btGenPW.grid(row = 0, column = 1)

groupRecords.grid(row = 4, column = 0, columnspan = 3)
btSearch.grid(row = 0, column = 0, columnspan = 2, padx = 5)
listUsers.grid(row = 0, column = 2, padx = 5)

# ---------------------------- MAIN LOOP ------------------------------- #

# window loop
while IS_OPEN:
    window.mainloop()