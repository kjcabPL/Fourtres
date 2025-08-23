import tkinter
import pyperclip
import json
import os
import webbrowser
from json import JSONDecodeError
from tkinter.ttk import Combobox
from math import ceil
from tkinter import *
from tkinter import messagebox
from random import randint, choice, shuffle
from datetime import datetime

IS_OPEN = True
GEN_PW = ""
GEN_MAX_CTR = 100
GEN_CALC = False

IMGPATH = "./img"
STOREPATH = "./str"
STOREFILE = STOREPATH + "/stores.json"
WORDFILE = STOREPATH + "/ws.json"
ICONFILE = IMGPATH + "/icon.ico"
STORED_DATA = {}
CUR_USER_DATA = []
CUR_WORD_LIST = []
CUR_WORD_LENGTH = 2
PW_LENGTH = 20

# Variables for Color Manipulation during PW generation
CUR_BG = ""
LOGO_FRAMES = ""
pwGenSources = { "Random Characters": 0, "Pass Phrase": 1}
curGenSource = pwGenSources["Random Characters"]
startColor = (255, 0, 0)
endColor = (255, 240, 136)
incs = ( int((endColor[0] - startColor[0]) / GEN_MAX_CTR), int((endColor[1] - startColor[1]) / GEN_MAX_CTR), int((endColor[2] - startColor[2]) / GEN_MAX_CTR))
placeholderWS = "my.site.com"
placeholderUser = "my_user / dummy@testmail.com"

# Misc Variables
subgrpGenSettings = [ ]

# ---------------------------- PASSWORD GENERATOR ------------------------------- #
def genPassword():
    global GEN_CALC
    global CUR_BG

    GEN_CALC = True
    CUR_BG = startColor

    # reset the logo before animating
    # lblLogo.config(image=LOGO_FRAMES[0])
    if curGenSource == 0: generateFromCharacters()
    elif curGenSource == 1: generateFromWordList()

def generateFromCharacters():
    global GEN_PW

    GEN_CUR_CTR = 0
    disableButtons()
    doGenAnimation(GEN_CUR_CTR)
    tbNewPw.insert(0, str(GEN_PW))

def generateFromWordList():
    global GEN_PW
    global CUR_WORD_LIST
    global CUR_WORD_LENGTH

    try:
        with open(WORDFILE, "r") as file:
            data = json.load(file)
            curWordList = data["words"]
    except FileNotFoundError:
        messagebox.showerror("Password Generation Error", "Cannot find word list file")
        return

    if len(curWordList) == 0:
        messagebox.showerror("Password Generation Error", "Cannot generate passphrase from empty word list")
        return

    CUR_WORD_LIST = curWordList
    CUR_WORD_LENGTH = int(sbWordCount.get())
    GEN_CUR_CTR = 0
    disableButtons()
    doGenAnimation(GEN_CUR_CTR)
    tbNewPw.insert(0, str(GEN_PW))

def doGenAnimation(CTR):
    global GEN_PW
    global GEN_CALC
    global CUR_BG

    if GEN_CALC:
        if CTR < GEN_MAX_CTR:
            CTR += 1
            GEN_PW = CTR
            if curGenSource == 0: newPass = genRandomizedHash()
            elif curGenSource == 1: newPass = genRandomizedPhrase()
            tbNewPw.delete(0, tkinter.END)
            tbNewPw.insert(0, newPass)

            # old canvas animation
                # CUR_BG = ( CUR_BG[0] + incs[0], CUR_BG[1] + incs[1], CUR_BG[2] + incs[2] )
                # bgColor = f"#{CUR_BG[0]:02X}{CUR_BG[1]:02X}{CUR_BG[2]:02X}"
                # canvas.config(bg=bgColor)

            for item in ["n1", "n2", "n3", "n4"]:
                cvLogo.itemconfig(item, image=choice(LOGO_FRAMES))

            main.after(10, doGenAnimation, CTR)
        else:
            GEN_CALC = False
            pyperclip.copy(tbNewPw.get())
            disableButtons(False)

def genRandomizedHash():
    letters = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u',
               'v', 'w', 'x', 'y', 'z', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P',
               'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
    numbers = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
    symbols = ['!', '#', '$', '%', '&', '(', ')', '*', '+']

    # Get password length and character settings. return with an error if none of the checkboxes are enabled
    PW_LENGTH = int(sbCharLength.get())
    hasLetters = charSettings["hasLetters"].get()
    hasNumbers = charSettings["hasNumbers"].get()
    hasSymbols = charSettings["hasSymbols"].get()

    if not hasLetters and not hasNumbers and not hasSymbols:
        messagebox.showerror("Password Generation Error", "You must select at least one character setting for password generation")
        return

    # Separate letter, number and symbol counts
    charCount = numCount = symCount = 0
    lengthRatio = 1
    if hasLetters or hasNumbers or hasSymbols:
        if hasLetters and hasNumbers:
            lengthRatio += 1
            if hasSymbols:
                lengthRatio += 1
        elif hasLetters and hasSymbols:
            lengthRatio += 1
            if hasNumbers:
                lengthRatio += 1
        elif hasSymbols and hasNumbers:
            lengthRatio += 1
            if hasLetters:
                lengthRatio += 1

    if hasLetters: charCount = ceil(PW_LENGTH / lengthRatio)
    if hasNumbers: numCount = ceil(PW_LENGTH / lengthRatio)
    if hasSymbols: symCount = ceil(PW_LENGTH / lengthRatio)

    # Generate a new password from combined list comprehension arithmetic
    newPass = [choice(letters) for _ in range(0, charCount)] + [choice(numbers) for _ in range(0, numCount)] + [choice(symbols) for _ in range(0, symCount)]
    # In case the length of the result is higher than the password length
    if len(newPass) > PW_LENGTH:
        extra = len(newPass) - PW_LENGTH
        newPass = newPass[:-extra]

    # shuffle(newPass)
    newPass = "".join(newPass)
    return newPass

# Generate a password using the wordlist and some character separators
def genRandomizedPhrase():
    global CUR_WORD_LIST

    wordLength = CUR_WORD_LENGTH
    tempPass = ""

    separators = ["-", "_", "&", "*", "%", "^"]
    separators = [char for char in separators if wordSeparators[char].get()]

    for i in range(0, wordLength):
        tempPass += choice(CUR_WORD_LIST)
        if len(separators) and not i == wordLength - 1:
            tempPass += choice(separators)

    newPass = tempPass
    return newPass

# ---------------------------- PASSWORD FUNCTIONS ------------------------------- #
def writeNewStoreFile():
    os.makedirs(STOREPATH, exist_ok=True)
    with open(STOREFILE, mode="w") as file:
        file.write("")

def writeNewWordsetFile():
    os.makedirs(STOREPATH, exist_ok=True)
    with open(WORDFILE, mode="w") as file:
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
        messagebox.showerror("Error Saving Data", "Unable to find store file. ")
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
        tbUser["values"] = tuple(userlist)
        tbUser.set("")
        if len(userlist) > 0:
            tbUser.set(userlist[0])


# ---------------------------- UI FUNCTIONS ------------------------------- #

def aboutFourtres():
    year = str(datetime.now().year)
    img = LOGO_FRAMES[3]

    dg = Toplevel(main, padx = "10", pady = "10")
    dg.title = "About Fourtres"
    dg.resizable(False, False)
    dlbli = Label(dg, image = img)
    dlbl1 = Label(dg, text = "Fourtres Pass Keeper")
    dlbl2 = Label(dg, text = "Ver. 1.0")
    dlbl3 = Label(dg, text = f"Bitknvs Studio © {year}")
    dlbl4 = Label(dg, text = "http:/bitknvs.com", fg = "blue", cursor = "hand2")
    dlbl4.bind("<Button-1>", lambda e: webbrowser.open("http:/bitknvs.com"))

    dlbli.grid(row = 0, column = 0, rowspan = 4, padx = 10)
    dlbl1.grid(row = 0, column = 1, padx = 30)
    dlbl2.grid(row = 1, column = 1, padx = 30)
    dlbl3.grid(row = 2, column = 1, padx = 30)
    dlbl4.grid(row = 3, column = 1, padx = 30)


def closeWindow():
    global IS_OPEN
    if messagebox.askokcancel("Exit", "Exit Fourtres?"):
        IS_OPEN = False
        main.destroy()

def disableButtons(state = True):
    val = tkinter.DISABLED
    if not state:
        val = tkinter.NORMAL

    btGenPW["state"] = val
    btAdd["state"] = val
    btSearch["state"] = val

def openWordList():
    modalWordlist = tkinter.Toplevel(main)
    modalWordlist.title("Word Generation Set")
    modalWordlist.grab_set()
    modalWordlist.config(padx = 10, pady = 10)

    # make this window modal and disabled main window unless closed
    modalWordlist.transient(main)

    # get the position of the main window based on its location and dimensions
    main.update_idletasks()
    x = main.winfo_x()
    y = main.winfo_y()
    w = main.winfo_width()
    h = main.winfo_height()

    # Reposition modal using its window width and height and using geometry()
    mWidth = modalWordlist.winfo_width()
    mHeight = modalWordlist.winfo_height()
    posx = x + ( w // 2 ) - ( mWidth // 2 )
    posy = y + ( h // 2 ) - ( mHeight // 2 )
    geoString = f"{mWidth}x{mHeight}+{posx}+{posy}"
    modalWordlist.geometry(geoString)

    wordlist = []
    try:
        with open(WORDFILE, "r") as file:
            data = json.load(file)
            wordlist = data["words"]
    except FileNotFoundError:
        with open(WORDFILE, "w") as file:
            file.write("")

    # Add components to the modal
    btRemoveWord = Button(modalWordlist, text = "Remove Word", width = 20, pady = 3)
    lbWordlist = Listbox(modalWordlist, height = 8, width = 30)
    lbWordlist.focus()

    # insert word list into wordlist list box
    if len(wordlist) > 0:
        for item in wordlist:
            lbWordlist.insert(wordlist.index(item), item)

    def removeWordFromList():
        try:
            wordToRemove = lbWordlist.get(lbWordlist.curselection())
        except tkinter.TclError:
            print("Unable to delete - no word selected")
        else:
            index = 0
            if wordToRemove in wordlist:
                index = wordlist.index(wordToRemove)
                lbWordlist.delete(index)
                wordlist.remove(wordToRemove)
                newData = {"words": wordlist}
                try:
                    with open(WORDFILE, "w") as file:
                        json.dump(newData, file, indent=2)
                except FileNotFoundError:
                    messagebox.showerror("Error updating word list", "Unable to update word list: file not found")
                    return

    btRemoveWord["command"] = removeWordFromList

    # position the components
    lbWordlist.grid(row = 0, column = 0, pady = 5)
    btRemoveWord.grid(row = 1, column = 0, pady = 5)

def addToWordList():
    newWord = tbWordToAdd.get()
    curWordList = []
    data = { "words": [] }

    def showWordListError(title, message):
        messagebox.showerror("Error adding to word list", message)
        btWordList.focus()

    if newWord == "":
        showWordListError("Error adding to word list", f"Word to be added cannot be an empty string")
        return

    try:
        with open(WORDFILE, "r") as file:
            data = json.load(file)
            curWordList = data["words"]
    except FileNotFoundError:
        with open(WORDFILE, "w") as file:
            file.write("")

    # check if the new word is already in the wordlist to prevent redundancy
    if newWord in curWordList:
        showWordListError("Error adding to word list", f"{newWord} already in the word list.")
        return

    curWordList.append(newWord)
    data = { "words": curWordList }
    try:
        with open(WORDFILE, "w") as file:
            json.dump(data, file, indent=2)
    except FileNotFoundError:
        showWordListError("Error Saving Data", "Unable to find word file. ")
        return
    else:
        messagebox.showinfo("Added to Word List", f"{newWord} added to word list")


# When the searchbox is changed to a different user
def displayPWData(event):
    global CUR_USER_DATA
    curUser = tbUser.get()
    data = [ item["pw"] for item in CUR_USER_DATA if item["user"] == curUser ]
    if len(data) > 0:
        tbUser.delete(0, tkinter.END)
        tbUser.insert(0, curUser)
        tbNewPw.delete(0, tkinter.END)
        tbNewPw.insert(0, data[0])

def changePWGenSource(event):
    global curGenSource
    val = listGenSource.get()
    curGenSource = pwGenSources[val]
    for frame in subgrpGenSettings:
        frame.grid_remove()
    subgrpGenSettings[curGenSource].grid(row=1, column=0, columnspan=3)

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

def validateNumberEntries(val):
    return val.isdigit()

# set up the logo GIF on the main window
def setupLogoGif():
    global LOGO_FRAMES

    # load all frames in the animated GIF
    maxFrames = 10
    LOGO_FRAMES = [tkinter.PhotoImage(file=f"{IMGPATH}/logo{i}.png") for i in range(0, 10)]

    padding = 10
    cvLogo.create_image(50 + padding, 100, image=LOGO_FRAMES[3], tags="n1")
    cvLogo.create_image(150 + padding, 100, image=LOGO_FRAMES[3], tags="n2")
    cvLogo.create_image(250 + padding, 100, image=LOGO_FRAMES[3], tags="n3")
    cvLogo.create_image(350 + padding, 100, image=LOGO_FRAMES[3], tags="n4")

# ---------------------------- UI & WINDOW SETUP ------------------------------- #

main = Tk()
main.config(padx=25, pady=25)
main.title("Fourtres PK")
main.resizable(False, False)
main.iconbitmap(ICONFILE)
readPWData()

# Menubar and help button
menuMain = Menu(main)
main.config(menu=menuMain)

menuhelp = Menu(menuMain, tearoff = 0)
menuMain.add_cascade(label = "Help", menu = menuhelp)
menuhelp.add(label = "About Fourtres", itemType = "command", command = aboutFourtres)

# Panels and component groupings
groupMain = LabelFrame(text = "User Record", padx = 10, pady = 10)
groupGens = LabelFrame(text = "Password Generation", padx = 10, pady = 10)
subgrpGenRandom = LabelFrame(groupGens, text = "", width = 60, borderwidth = 0, highlightthickness = 0, padx = 5, pady = 10)
subgrpGenCBs = LabelFrame(subgrpGenRandom, text = "", borderwidth = 0, highlightthickness = 0, padx = 5, pady = 5)
subgrpGenPhrase = LabelFrame(groupGens, text = "", borderwidth = 0, highlightthickness = 0, padx = 3, pady = 10)
subgrpGenSettings = [ subgrpGenRandom, subgrpGenPhrase ]
subgrpGenSeparators = LabelFrame(subgrpGenPhrase, text = "", borderwidth = 0, highlightthickness = 0, padx = 5)

# labels
lblWebsite = Label(groupMain, text="Website:", width = 15, anchor="e" )
lblUser = Label(groupMain, text="Email/Username:", width = 15, anchor="e")
lblNewPW = Label(groupMain, text="New Password:", width = 15, anchor="e")
lblGenSource = Label(groupGens, text="Generate Using: ", width = 15, anchor="e")
lblGenCharSet = Label(subgrpGenRandom, text="Include Characters: ", width = 15, anchor="e")
lblGenLength = Label(subgrpGenRandom, text="Password Length: ", width = 15, anchor="e")
lblGenCount = Label(subgrpGenPhrase, text=" Word Count: ", width = 16, anchor="e")
lblGenPhrases = Label(subgrpGenPhrase, text="Edit Word List:", width = 16, anchor="e")
lblGenSeps = Label(subgrpGenPhrase, text="Word Separators:", width = 16, anchor="e")

# copyright label
year = str(datetime.now().year)
lblFooter = Label(text=f"Bitknvs Studio © {year}", font=("Arial", 8, "normal"))

# Entry Fields
tbWebsite = Entry(groupMain, width = 27)
tbWebsite.insert(0, placeholderWS)
tbUser = Combobox(groupMain, values=[], width = 47, height = 10)
tbUser.insert(0, placeholderUser)
tbNewPw = Entry(groupMain, width = 50)
tbWordToAdd = Entry(subgrpGenPhrase, width = 15)

# buttons & other components
btAdd = Button(groupMain, text = "Add Record", width = 60, pady = 5)
btSearch = Button(groupMain, text = "Search Website 🔎", width = 17)
btGenPW = Button(groupGens, text = "Generate Password", width = 60, pady = 5)
btAddWord = Button(subgrpGenPhrase, text = "Add To Word List", width = 15)
btWordList = Button(subgrpGenPhrase, text = "Open Word List", width = 50, pady = 3)

listGenSource = Combobox(groupGens, values=[val for val in pwGenSources.keys()], state = "readonly", width = 43 )
listGenSource.set("Random Characters")

charSettings = {"hasLetters": BooleanVar(value=True), "hasNumbers": BooleanVar(value=True), "hasSymbols": BooleanVar(value=True)}
cbChars = Checkbutton(subgrpGenCBs, text="Letters", variable=charSettings["hasLetters"])
cbNumbers = Checkbutton(subgrpGenCBs, text="Numbers", variable=charSettings["hasNumbers"])
cbSymbols = Checkbutton(subgrpGenCBs, text="Symbols", variable=charSettings["hasSymbols"])

# separater checkboxes
wordSeparators = { "-": BooleanVar(value = False), "_": BooleanVar(value = False), "&": BooleanVar(value = False), "*": BooleanVar(value = False) ,"%": BooleanVar(value = False), "^": BooleanVar(value = False) }
cbSep1 = Checkbutton(subgrpGenSeparators, text="-", variable=wordSeparators["-"])
cbSep2 = Checkbutton(subgrpGenSeparators, text="_", variable=wordSeparators["_"])
cbSep3 = Checkbutton(subgrpGenSeparators, text="&", variable=wordSeparators["&"])
cbSep4 = Checkbutton(subgrpGenSeparators, text="*", variable=wordSeparators["*"])
cbSep5 = Checkbutton(subgrpGenSeparators, text="%", variable=wordSeparators["%"])
cbSep6 = Checkbutton(subgrpGenSeparators, text="^", variable=wordSeparators["^"])

sbCharLength = Spinbox(subgrpGenRandom, from_ = 8, to = 50, width = 40, state = "readonly", validatecommand = validateNumberEntries)
sbWordCount = Spinbox(subgrpGenPhrase, from_ = 2, to = 10, width = 38, state = "readonly", validatecommand = validateNumberEntries)

# build the logo
cvLogo = Canvas(width = 415, height = 200, bg="black")
setupLogoGif()

# ---------------------------- WINDOW & COMPONENTS SETUP ------------------------------- #

# function assignments
main.protocol("WM_DELETE_WINDOW", closeWindow)
btGenPW["command"] = genPassword
btAdd["command"] = savePWData
btSearch["command"] = searchPWData
btAddWord["command"] = addToWordList
btWordList["command"] = openWordList

# event binding assignments
tbUser.bind("<<ComboboxSelected>>", displayPWData)
listGenSource.bind("<<ComboboxSelected>>", changePWGenSource)
tbUser.bind("<FocusIn>", entryFocused)
tbUser.bind("<FocusOut>", entryLeaveFocus)
tbWebsite.bind("<FocusIn>", entryFocused)
tbWebsite.bind("<FocusOut>", entryLeaveFocus)

# arrangements
cvLogo.grid(row = 0, column = 0, columnspan = 3, rowspan = 2)

groupMain.grid(row = 2, column = 0, columnspan = 3)
lblWebsite.grid(row = 0, column = 0)
lblUser.grid(row = 1, column = 0)
tbWebsite.grid(row = 0, column = 1, pady = 5)
btSearch.grid(row = 0, column = 2)
tbUser.grid(row = 1, column = 1, columnspan = 2, pady = 5)
lblNewPW.grid(row = 2, column = 0)
tbNewPw.grid(row = 2, column = 1, columnspan = 2, pady = 5)
btAdd.grid(row = 3, column = 0, columnspan = 3, pady = 5)

groupGens.grid(row = 3, column = 0, columnspan = 3)
lblGenSource.grid(row = 0, column = 0, padx = 2)
listGenSource.grid(row = 0, column = 1, columnspan = 2, padx = 15)
subgrpGenRandom.grid(row = 1, column = 0, columnspan = 3, padx = 5)
lblGenCharSet.grid(row = 0, column = 0)
subgrpGenCBs.grid(row = 0, column = 1, columnspan = 2, padx = 23)
cbChars.grid(row = 0, column = 0, padx=5)
cbNumbers.grid(row = 0, column = 1, padx=5)
cbSymbols.grid(row = 0, column = 2, padx=5)
lblGenLength.grid(row = 1, column = 0)
sbCharLength.grid(row = 1, column = 1, columnspan = 2, pady = 3)
subgrpGenPhrase.grid(row = 1, column = 0, columnspan = 3)
lblGenPhrases.grid(row = 0, column = 0)
tbWordToAdd.grid(row = 0, column = 1, padx = (0, 3))
btAddWord.grid(row = 0, column = 2, padx = (5,0), pady = 5)
lblGenCount.grid(row = 1, column = 0, padx = (5,0))
sbWordCount.grid(row = 1, column = 1, columnspan = 2, pady = 5)
lblGenSeps.grid(row = 2, column = 0, padx = (5,0), pady = 2)
subgrpGenSeparators.grid(row = 2, column = 1, columnspan = 2, pady = 5)
cbSep1.grid(row = 0, column = 0, padx = 4)
cbSep2.grid(row = 0, column = 1, padx = 4)
cbSep3.grid(row = 0, column = 2, padx = 4)
cbSep4.grid(row = 0, column = 3, padx = 4)
cbSep5.grid(row = 0, column = 4, padx = 4)
cbSep6.grid(row = 0, column = 5, padx = 4)
btWordList.grid(row = 3, column = 0, columnspan = 3)
btGenPW.grid(row = 2, column = 0, columnspan = 3, pady = 5)

# footer placement
lblFooter.grid(row = 4, column = 0, columnspan = 3, padx = 3)

# hide by default at app start
subgrpGenPhrase.grid_remove()
# ---------------------------- MAIN LOOP ------------------------------- #

# window loop
while IS_OPEN:
    main.mainloop()