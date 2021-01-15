import sys
import webbrowser

from tkinter import *
from tkinter import messagebox
from PIL import Image, ImageTk
from enums import Status, Permissions

# Store default values for colours
bgColour = "light sky blue"
txtColour = "gray5"

butColour = "steel blue"
butTxtColour = "gray5"

# Application class for GUI
class App:
    def __init__(self, db, debug=False):
        self.db = db
        self.debug = debug

        self.currUser = None
        self.currAlbum = None
        self.currImage = None
        self.imgListBoxWidget = None

        self.listOfPriorSelections = []

        # Root window setup
        self.rootWindow = Tk()
        self.rootWindow.title("Image Repository")
        self.rootWindow.geometry("1200x720")
        self.rootWindow.minsize(1200, 720)
        self.rootWindow.configure(bg=bgColour)


        # Menu bar setup
        self.menuBar = Menu(self.rootWindow)
        self.fileMenu = Menu(self.menuBar, tearoff=0)
        self.editMenu = Menu(self.menuBar, tearoff=0)
        self.viewMenu = Menu(self.menuBar, tearoff=0)
        self.helpMenu = Menu(self.menuBar, tearoff=0)
        self.createMenu()

        # Title test setup
        self.title = Label(self.rootWindow, text="Image Repository", font=("Copperplate Gothic Bold", 50), fg=txtColour, bg=bgColour)
        self.title.pack(padx=10, pady=(30,0))

        self.currFrame = self.startFrame()

    # Starts the application
    def Run(self):
        self.rootWindow.mainloop()

    # Sets up the menu bar system
    def createMenu(self):
        # Setting up "File" menu button with options to upload/download photos, logout, and exit
        self.fileMenu.add_command(label="Upload Image(s)", command=self.upload)
        self.fileMenu.add_command(label="Download Image(s)", command=lambda:self.switchFrame(self.homeFrame(self.currAlbum, "download")))
        self.fileMenu.add_separator()
        self.fileMenu.add_command(label="Log Out", command=lambda:self.switchFrame(self.startFrame()))
        self.fileMenu.add_separator()
        self.fileMenu.add_command(label="Exit", command=sys.exit)
        self.menuBar.add_cascade(label="File", menu=self.fileMenu)

        # Setting up "Edit" menu with option to delete photos
        self.editMenu.add_command(label="Delete Photo(s)", command=lambda:self.switchFrame(self.homeFrame(self.currAlbum, "delete")))
        self.editMenu.add_separator()
        self.editMenu.add_command(label="Select All", state=DISABLED, command=self.selectAll)
        self.menuBar.add_cascade(label="Edit", menu=self.editMenu)

        # Setting up "View" menu button with options to view public or private photos
        self.viewMenu.add_command(label="Private Photos", command=lambda:self.switchFrame(self.homeFrame(Permissions.PRIVATE)))
        self.viewMenu.add_command(label="Public Photos", command=lambda:self.switchFrame(self.homeFrame(Permissions.PUBLIC)))
        self.menuBar.add_cascade(label="View", menu=self.viewMenu)

        # Setting up "Help" menu button with options to see documentation to get help and to get info about author
        self.helpMenu.add_command(label="About", command=lambda:webbrowser.open("https://github.com/SciortinoR"))
        self.menuBar.add_cascade(label="Help", menu=self.helpMenu)

    # Displays menu bar in the root window.
    def showMenuBar(self, showOrHide, editMode=None):
        if showOrHide == False:
            emptyMenu = Menu(self.rootWindow)
            self.rootWindow.config(menu=emptyMenu)
        else:
            if editMode == "edit":
                self.editMenu.entryconfig("Select All", state=NORMAL)
                self.rootWindow.config(menu=self.menuBar)
            else:
                self.editMenu.entryconfig("Select All", state=DISABLED)
                self.rootWindow.config(menu=self.menuBar)

    # Switches from current frame to next requested frame
    def switchFrame(self, nextFrame):
        self.currFrame.destroy()
        nextFrame.pack
        self.currFrame = nextFrame
    
    # Start login frame
    def startFrame(self):
        self.showMenuBar(False)

        frame = Frame(self.rootWindow, bg=bgColour)

        loginBut = Button(frame, text="Login", font=("Copperplate Gothic Bold", 25), fg=butTxtColour, bg=butColour, command=lambda:self.switchFrame(self.loginFrame()))
        loginBut.pack(pady=50)

        createAccBut = Button(frame, text="Register", font=("Copperplate Gothic Bold", 25), fg=butTxtColour, bg=butColour, command=lambda:self.switchFrame(self.createUserFrame()))
        createAccBut.pack(pady=20)

        frame.pack(pady=80)

        # Must always return the frame
        return frame
    
    # Existing user login frame
    def loginFrame(self):
        self.showMenuBar(False)

        frame = Frame(self.rootWindow, bg=bgColour)

        frameUsername = Frame(frame, bg=bgColour)
        framePassword = Frame(frame, bg=bgColour)
        frameBut = Frame(frame, bg=bgColour)

        usernameLabel = Label(frameUsername, text="Username: ", fg=butTxtColour, bg=butColour, width=10, anchor=E)
        usernameEntry = Entry(frameUsername)
        usernameLabel.pack(side=LEFT)
        usernameEntry.pack(side=RIGHT)

        passwordLabel = Label(framePassword, text="Password: ", fg=butTxtColour, bg=butColour, width=10, anchor=E)
        passwordEntry = Entry(framePassword, show='*')
        passwordLabel.pack(side=LEFT)
        passwordEntry.pack(side=RIGHT)
        

        def dialog():
            username = (usernameEntry.get()).upper()
            password = passwordEntry.get()

            userLogin = self.db.validateUser(username, password)
            if userLogin == Status.SUCCESS:
                self.currUser = username
                self.switchFrame(self.homeFrame(Permissions.PRIVATE))
            else:
                messagebox.showerror("Attention: Invalid Combination", "Incorrect username and password combination!\n\nNote: Passwords are case-sensitive.")

        submitBut = Button(frameBut, text="Submit", font=("Copperplate Gothic Light", 20), fg=butTxtColour, bg=butColour, command=dialog)
        submitBut.pack(pady=50)

        backBut = Button(frameBut, text="Back", font=("Copperplate Gothic Light", 20), fg=butTxtColour, bg=butColour, command=lambda:self.switchFrame(self.startFrame()))
        backBut.pack(pady=10)

        frameUsername.pack()
        framePassword.pack()
        frameBut.pack()

        frame.pack(pady=85)

        return frame

    # New user account creation frame
    def createUserFrame(self):
        self.showMenuBar(False)

        frame = Frame(self.rootWindow, bg=bgColour)

        frameUsername = Frame(frame, bg=bgColour)
        framePassword = Frame(frame, bg=bgColour)
        framePasswordConfirm = Frame(frame, bg=bgColour)
        frameBut = Frame(frame, bg=bgColour)

        usernameLabel = Label(frameUsername, text="Username: ", fg=butTxtColour, bg=butColour, width=15, anchor=E)
        usernameEntry = Entry(frameUsername)
        usernameLabel.pack(side=LEFT)
        usernameEntry.pack(side=RIGHT)

        passwordLabel = Label(framePassword, text="Password: ", fg=butTxtColour, bg=butColour, width=15, anchor=E)
        passwordEntry = Entry(framePassword, show='*')
        passwordLabel.pack(side=LEFT)
        passwordEntry.pack(side=RIGHT)

        passwordConfirmLabel = Label(framePasswordConfirm, text="Confirm Password: ", fg=butTxtColour, bg=butColour, width=15, anchor=E)
        passwordConfirmEntry = Entry(framePasswordConfirm, show='*')
        passwordConfirmLabel.pack(side=LEFT)
        passwordConfirmEntry.pack(side=RIGHT)
        
        submitBut = Button(frameBut, text="SUBMIT", font=("Copperplate Gothic Light", 20), fg=butTxtColour, bg=butColour, command=lambda:self.createUser(usernameEntry.get(), passwordEntry.get(), passwordConfirmEntry.get()))
        submitBut.pack(pady=50)

        backBut = Button(frameBut, text="Back", font=("Copperplate Gothic Light", 20), fg=butTxtColour, bg=butColour, command=lambda:self.switchFrame(self.startFrame()))
        backBut.pack(pady=10)

        frameUsername.pack(pady=15)
        framePassword.pack()
        framePasswordConfirm.pack()
        frameBut.pack()

        frame.pack(pady=60)

        return frame

    # User Dashboard / Home screen
    def homeFrame(self, albumType, mode="view"):
        if mode == "view":
            self.showMenuBar(True) 
        else:
            self.showMenuBar(True, "edit")

        self.currAlbum = albumType
        self.currImage = None
        self.listOfPriorSelections = []
        self.imgListBoxWidget = None

        frame = Frame(self.rootWindow, bg=bgColour)

        frameSelectionBox = Frame(frame, bg=bgColour)
        frameImgViewer = Frame(frame, bg=butColour)  

        # If we are in delete mode, create approporiate instructions for the user and create a delete button
        if mode == "delete":
            subtitle = Label(frame, text='Select the desired image(s) and press the "DELETE" button.\n\nTo go back, select "View" and choose the desired album.', font=("Verdana", 10), fg=txtColour, bg=bgColour)
            subtitle.pack(pady=(15,0))

            button = Button(frame, text="DELETE", font=("Copperplate Gothic Light", 10), fg=butTxtColour, bg=butColour, command=lambda:self.delete(listOfImages, self.imgListBoxWidget.curselection()))
            button.pack(anchor=W, padx=25, pady=(15, 3))

        # If we are in download mode, create approporiate instructions for the user and create a download button
        elif mode == "download":
            subtitle = Label(frame, text='Select the desired image(s) and press the "DOWNLOAD" button.\nThen, select a download location.\n\nTo go back, select "View" and choose the desired album.', font=("Verdana", 10), fg=txtColour, bg=bgColour)
            subtitle.pack(pady=(15,0))

            button = Button(frame, text="DOWNLOAD", font=("Copperplate Gothic Light", 10), fg=butTxtColour, bg=butColour, command=lambda:self.download(listOfImages, self.imgListBoxWidget.curselection()))
            button.pack(anchor=W, padx=25, pady=(15,3))
        # If we are in view mode (which is the default), tell the user what album they are currently viewing
        else:
            if albumType == Permissions.PRIVATE:
                subtitle = Label(frame, text="Private Images", font=("Copperplate Gothic Light", 15), fg=txtColour, bg=bgColour)
                subtitle.pack(pady=15)
            elif albumType == Permissions.PUBLIC:
                subtitle = Label(frame, text="Public Images", font=("Copperplate Gothic Light", 15), fg=txtColour, bg=bgColour)
                subtitle.pack(pady=15)

        # Setting up the scroll bars for the image selection box
        yDirScrollBar = Scrollbar(frameSelectionBox)
        yDirScrollBar.pack(side=RIGHT, fill=Y)

        xDirScrollBar = Scrollbar(frameSelectionBox, orient=HORIZONTAL)
        xDirScrollBar.pack(side=BOTTOM, fill=X)
        
        self.imgListBoxWidget = Listbox(frameSelectionBox, selectmode=EXTENDED, yscrollcommand=yDirScrollBar.set, xscrollcommand=xDirScrollBar.set, bg=butColour, fg=butTxtColour, font = ("Copperplate Gothic Light", 20))
        # Enable multi-select if we are in delete or download mode
        if mode == "delete" or mode == "download":
            self.imgListBoxWidget.configure(selectmode=MULTIPLE)
        else:
            self.imgListBoxWidget.configure(selectmode=SINGLE)

        # Configuring the scoll bars to control the image selection box
        yDirScrollBar.config(command=self.imgListBoxWidget.yview)
        xDirScrollBar.config(command=self.imgListBoxWidget.xview)

        # Get ist of images from current album
        listOfImages = None
        if self.currAlbum == Permissions.PRIVATE:
            listOfImages = self.db.getImages(Permissions.PRIVATE, self.currUser)
            if self.debug : print(self.currUser + " Images:")
        else:
            listOfImages = self.db.getImages(Permissions.PUBLIC)
            if self.debug : print("Public Images:")

        for image in listOfImages:
            if self.debug : print("  " + image)
            self.imgListBoxWidget.insert(END, image)

        # Setting up the image viewer box and configuing it
        imgViewer = Label(frameImgViewer, text="Select a photo to view it.\n\n\nIf there is nothing listed on the left, then no images have been uploaded yet.", font=("Copperplate Gothic Bold", 10), fg=txtColour, image=self.currImage, bg=butColour)
        imgViewer.configure(wraplength=imgViewer.winfo_width(), justify=CENTER)
        imgViewer.bind('<Configure>', lambda e: imgViewer.config(wraplength=imgViewer.winfo_width()))
        imgViewer.pack(padx=25, pady=25, fill=BOTH, expand=True)

        # Binding the image selection box to the image handler whenever an item is selected
        if mode == "delete" or mode == "download":
            self.imgListBoxWidget.bind('<<ListboxSelect>>', lambda event:self.imageHandler(event, "multiple", listOfImages, imgViewer))
        # If we are in view mode (the default mode), then we are using a single-selection box (so the list box is of type "single")
        else:
            self.imgListBoxWidget.bind('<<ListboxSelect>>', lambda event:self.imageHandler(event, "single", listOfImages, imgViewer))
        # Packing the image selection box
        self.imgListBoxWidget.pack(fill=BOTH, expand=True)

        frameSelectionBox.pack(fill=Y, side=LEFT, padx=25)
        frameImgViewer.pack(fill=BOTH, expand=True, side=LEFT, padx=25)

        frame.pack(fill=BOTH, expand=True, pady=(0,25))

        return frame

    # Validate new user
    def createUser(self, username, password, passwordConfirm):
        username = username.upper()

        if username.isalnum() == True:
            if password == passwordConfirm:
                newUniqueUser = self.db.createUser(username, password)
                if newUniqueUser == Status.SUCCESS:
                    messagebox.showinfo("Success", f"Welcome, {username}!\nYour account was successfully created.\n\n")
                    self.switchFrame(self.startFrame())
                else:
                    messagebox.showerror("Attention: Username Taken", "That username is already taken!")
            else:
                messagebox.showerror("Attention: Invaild Password", "The passwords do not match!\n\nNote: Passwords are case-sensitive.")
        else:
            messagebox.showerror("Attention: Invaild Username", "This username is not allowed!\n\nNote: Usernames can only contain letters and numbers. Spaces and special charaters (such as !, $, #, @) are NOT allowed.")

    # Handles the image viewer to ensure it displays the currently selected image
    def imageHandler(self, event, selectionType, listOfImages, imgViewerWidget):
        indexOfSelection = None

        if selectionType == "single":
            indexOfSelection = int(self.imgListBoxWidget.curselection()[0])
        else:
            listOfSelections = self.imgListBoxWidget.curselection()

            # Find what image is different in the two list (which indicates it was either the last selected or it was just unselected)
            lastSelectedItem = set(listOfSelections).symmetric_difference(set(self.listOfPriorSelections))
            indexOfSelection = int(list(lastSelectedItem)[0])

            self.listOfPriorSelections = listOfSelections

        imgName = listOfImages[indexOfSelection]
        self.db.openImageDir(self.currAlbum, self.currUser)
        img = Image.open(imgName)
        sizeOfImg = img.size

        # Find the largest side of the image. If "largestSideOfImg" is none, both sides are equal and its a square. If it
        # is zero, the largest side is the width. If it is one, the largest side is the height
        largestSideOfImg = None
        if sizeOfImg[0] != sizeOfImg[1]:
            largestSideOfImg = sizeOfImg.index(max(sizeOfImg))
        
        # Calculate the image ratio of the width to the height
        ratio = sizeOfImg[0]/sizeOfImg[1]

        # Stores the size of the image viewer widget in the form [width, height]
        sizeOfImgViewer = [imgViewerWidget.winfo_width(), imgViewerWidget.winfo_height()]

        # *** DETERMING THE HEIGHT AND WIDTH OF THE IMAGE TO FIT WITHIN THE IMAGE VIWER ***
        #If width is largest side of image, adjust the width to fill the image viewer frame completely
        if largestSideOfImg == 0:
            imgWidth = int(imgViewerWidget.winfo_width())
            imgHeight = int(imgWidth*(1/ratio))
            #If the new height of the image is larger than the height of the frame, then it won't fit properly vertically so size it down 
            if imgHeight > sizeOfImgViewer[1]:
                #New image height is calculated by subtracting different between the current height and the image viewer height
                imgHeight = int(imgHeight - (imgHeight - sizeOfImgViewer[1]))
                imgWidth = int(imgHeight*ratio)

        #Else, if height of image is largest, adjust image height to fill the image viewer frame completely
        elif largestSideOfImg == 1:
            imgHeight = int(imgViewerWidget.winfo_height())
            imgWidth = int(imgHeight*ratio)

            #If the new width of the image is larger than the width of the frame, then it won't fit properly horizontally so size it down 
            if imgWidth > sizeOfImgViewer[0]:
                #New image width is calculated by subtracting different between the current width and the image viewer width
                imgWidth = int(imgWidth - (imgWidth - sizeOfImgViewer[0]))
                imgHeight = int(imgWidth*(1/ratio))
        
        #Else, if image is a square, then size it up to fill the smallest side of the image viewer frame
        elif largestSideOfImg == None:
            #If width of image viewer is smaller than its height, make the width of the image itself as large as the image viewer frame width
            if sizeOfImgViewer[0] < sizeOfImgViewer[1]:
                imgWidth = int(imgViewerWidget.winfo_width())
                imgHeight = int(imgWidth*(1/ratio))
            #If height of image viewer is smaller than (or equal to) its height, make the height of the image itself as large as the image viewer frame height
            else:
                imgHeight = int(imgViewerWidget.winfo_height())
                imgWidth = int(imgHeight*ratio)

        # Reszie image to fit within the image viewer frame
        img = img.resize((imgWidth, imgHeight), Image.ANTIALIAS)

        # Update the global object variable that stores a reference to the current image being displayed
        self.currImage = ImageTk.PhotoImage(img)

        # Reconfigure the image viewer to display the current image
        imgViewerWidget.configure(image=self.currImage)
        
        # Close the directory of photos for the current album and return to the top level application directory
        self.db.closeImageDir(self.currAlbum, self.currUser)

    # Upload images to the database
    def upload(self):
        self.db.uploadImages(self.currAlbum, self.currUser)
        self.switchFrame(self.homeFrame(self.currAlbum))

    # Delete a given list of images from the database
    def delete(self, imgList, deletionIndices):
        self.db.deleteImages(self.currAlbum, imgList, deletionIndices, self.currUser)
        self.switchFrame(self.homeFrame(self.currAlbum))

    # Download a given list of images from the database
    def download(self, imgList, downloadIndices):
        self.db.downloadImages(self.currAlbum, imgList, downloadIndices, self.currUser)
        self.switchFrame(self.homeFrame(self.currAlbum))

    # Selects all images in the image selection list box widget
    def selectAll(self):
        self.imgListBoxWidget.select_set(0,END)