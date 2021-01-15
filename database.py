import os
import shutil

from tkinter import messagebox
from tkinter import filedialog
from enums import Status, Permissions

# Database class for storage & manipulation of data
class Database:
    def __init__(self, dbName='DB', directory=os.getcwd(), debug=False):
        self.dbName = dbName
        self.users = {}

        self.rootDir = directory
        self.debug = debug

        # Constant values used for encryption
        self.u_c = 17
        self.p_c = 23

        # Create/Restore DB file structure
        if not os.path.exists(dbName):
            os.mkdir(dbName)

        if not os.path.exists(f'{dbName}/UserData.txt'):
            file = open(f'{dbName}/UserData.txt', "x")
            file.close()

        if not os.path.exists(f'{dbName}/Users'):
            os.mkdir(f'{dbName}/Users')

        if not os.path.exists(f'{dbName}/Public'):
            os.mkdir(f'{dbName}/Public')

        self.readExistingUsers()

    # Encrypt usernames and passwords
    # This can be used to be store encypted account data textfiles or to encrpyt directory names (which helps keep user files somewhat 
    # since they are not stored in a folder with the same name as the user's username)
    def encrypt(self, encryptType, dataType, data):
        # Stores each character of the encrypted name
        newData = []

        # Constant used for encryption
        const = None

        # Set the constant depending on whether the data to be encypted is a username or password
        if dataType == "username":
            const = self.u_c
        elif dataType == "password":
            const = self.p_c

        # If the data to be encrypted is for a textfile, then use this encryption method
        if encryptType == "txt":
            # For every character in the data, find the new character by adding the constant
            for char in data:
                newNum = ord(char) + const

                # If the new character goes outside of the ascii table, loop it back around from ascii 33 (so add 32) since the first 32 
                # are control characters and NOT printable characters
                if newNum > 126:
                    newNum = (newNum-126)+32
                
                # Convert new new ascii number to a character
                newChar = chr(newNum)
                # Add this new character to the list storing each new encrypted character
                newData.append(newChar)

            # Join the encrypted characters and return them as a string
            return ''.join(newData)
        
        # If the data to be encrypted is for a directory, use this method since it has to be alphanumeric
        elif encryptType == "dir":
            # All alphanumeric characters will be mapped to a new set of values called "Cypher" as seen below:
            #
            #    Char:  A   B  ... Y   Z  | 0   1  ... 8   9  | a   b  ... y   z
            #   ASCII:  65  66 ... 89  90 | 48  49 ... 56  57 | 97  98 ... 121 122
            # ----------------------------|-------------------|----------------------
            #  Cypher:  0   1  ... 24  25 | 26  27 ... 34  35 | 36  37 ... 60  61


            # For every character in the data...
            for char in data:
                num = ord(char)     # Store cypher value of original character
                cypherNum = None    # Store encrypted cypher value number that corresponds with the given character
                encodedNum = None   # Store ascii value of encrypted character

                # Convert ascii value for the character (num) into its corresponding number on the cypher
                if char >= 'A' and char <= 'Z':
                    num = ord(char) - 65
                elif char >= '0' and char <= '9':
                    num = ord(char) - 48 + 26
                elif char >= 'a' and char <= 'z':
                    num = ord(char) - 97 + 36


                # Now, since the cypher is all properly space unlike the ascii values of the alphanumeric characters, add the constant
                cypherNum = num + const

                # If adding constants exceeds the length of the cypher, wrap it around back to the start
                if cypherNum > 61:
                    #62 items in cypher, so it has to be 61+1 since cypher starts at 0.
                    cypherNum -= (61+1)

                # Convert from the encrypted cypher value back into ascii
                if cypherNum >= 0 and cypherNum <= 25:
                    encodedNum = cypherNum + 65
                elif cypherNum >= 26 and cypherNum <= 35:
                    encodedNum = cypherNum + (48 - 26)
                elif cypherNum >= 36 and cypherNum <= 61:
                    encodedNum = cypherNum + (97 - 36)
                
                # Save the charater corresponding with the ascii value
                newChar = chr(encodedNum)
                # Append this character to the list of encrypted characters
                newData.append(newChar)

            # Join the encrypted characters and return them as a string
            return ''.join(newData)


    # Decrypt usernames and passwords
    def decrypt(self, decryptType, dataType, data):
        # NOTE: This is basically the reverse of the "Encrypt" method above

        newData = []

        const = None

        if dataType == "username":
            const = self.u_c
        elif dataType == "password":
            const = self.p_c

        if decryptType == "txt":
            for char in data:
                newNum = ord(char) - const
                if newNum < 33:
                    newNum = (newNum+126)-32
                newChar = chr(newNum)
                newData.append(newChar)
            return ''.join(newData)
        
        elif decryptType == "dir":
            #    Char:  A   B  ... Y   Z  | 0   1  ... 8   9  | a   b  ... y   z
            #   ASCII:  65  66 ... 89  90 | 48  49 ... 56  57 | 97  98 ... 121 122
            # ----------------------------|-------------------|----------------------
            #  Cypher:  0   1  ... 24  25 | 26  27 ... 34  35 | 36  37 ... 60  61

            for char in data:
                num = None
                cypherNum = None
                decodedNum = None

                if char >= 'A' and char <= 'Z':
                    num = ord(char) - 65
                elif char >= '0' and char <= '9':
                    num = ord(char) - 48 + 26
                elif char >= 'a' and char <= 'z':
                    num = ord(char) - 97 + (26+10)

                cypherNum = num - const
                if cypherNum < 0:
                    #62 items in cypher, so it has to be 61+1 since cypher starts at 0.
                    cypherNum += (61+1)

                if cypherNum >= 0 and cypherNum <= 25:
                    decodedNum = cypherNum + 65
                elif cypherNum >= 26 and cypherNum <= 35:
                    decodedNum = cypherNum + (48 - 26)
                elif cypherNum >= 36 and cypherNum <= 61:
                    decodedNum = cypherNum + (97 - 36)
                
                newChar = chr(decodedNum)

                newData.append(newChar)

            return ''.join(newData)

    # Reading existing users in the database
    def readExistingUsers(self):
        # Open file
        file = open(f'{self.dbName}/UserData.txt', "r")

        # Read all lines and store them in a list
        lines = file.readlines()

        if self.debug:
            print('Existing User Info (in the form "username: password"):')

        # Read each line and add the decrypted usernames and passwords to the dictonary of users
        for i in range(0, len(lines), 2):
            encryptedUsername = lines[i].rstrip('\n')
            encryptedPassword = lines[i+1].rstrip('\n')

            username = self.decrypt("txt", "username", encryptedUsername)
            password = self.decrypt("txt", "password", encryptedPassword)

            self.users[username] = password

            if self.debug:
                print("  " + username + ": " + password)

        # Close file
        file.close()

    # Create a new user and check to see if the username is unique
    def createUser(self, username, password):
        os.chdir(self.rootDir)
        if username not in self.users:
            self.users[username] = password

            os.mkdir(f'{self.dbName}/Users/{self.encrypt("dir", "username", username)}')

            file = open(f'{self.dbName}/UserData.txt', "a")
            file.write(f'{self.encrypt("txt", "username", username)}\n')
            file.write(f'{self.encrypt("txt", "password", password)}\n')
            file.close()

            return Status.SUCCESS

        return Status.ERROR

    # Checks username and password
    def validateUser(self, username, password):
        for key, value in self.users.items():
            if key == username:
                if value == password:
                    return Status.SUCCESS
        return Status.ERROR

    # Navigates to requested image directory
    def openImageDir(self, imagePermission, username=None):
        os.chdir(self.rootDir)

        if imagePermission == Permissions.PUBLIC:
            os.chdir(self.dbName)
            os.chdir('Public')
        elif imagePermission == Permissions.PRIVATE and username != None:
            os.chdir(self.dbName)
            os.chdir('Users')
            os.chdir(self.encrypt("dir", "username", username))
        else:
            return Status.ERROR

        return Status.SUCCESS

    # Closes requested image directory
    def closeImageDir(self, imagePerimssion, username=None):
        if imagePerimssion == Permissions.PUBLIC:
            if 'Public' == os.path.basename(os.getcwd()):
                os.chdir(self.rootDir)
        elif imagePerimssion == Permissions.PRIVATE and username != None:
            if self.decrypt("dir", "username", username) == os.path.basename(os.getcwd()):
                os.chdir(self.rootDir)
        else:
            return Status.ERROR

        return Status.SUCCESS

    # Iterates over images and stores them
    def iterateImages(self, imgFiles):
        for file in os.listdir(os.getcwd()):
            tmpName = file.lower()
            if tmpName.endswith(".jpg") or tmpName.endswith(".jpeg") or tmpName.endswith(".png") or tmpName.endswith(".gif"):
                imgFiles.append(file)

    # Gets list of images from public or private albums
    def getImages(self, albumType, username=None):
        imgFiles = []

        if albumType == Permissions.PUBLIC:
            self.openImageDir(Permissions.PUBLIC)
            self.iterateImages(imgFiles)
            self.closeImageDir(Permissions.PUBLIC)
        elif albumType == Permissions.PRIVATE and username != None:
            self.openImageDir(Permissions.PRIVATE, username)
            self.iterateImages(imgFiles)
            self.closeImageDir(Permissions.PRIVATE, username)
        else:
            return Status.ERROR
        
        return imgFiles

    # Upload images to requested album
    def uploadImages(self, albumType, username=None):   
        if albumType == Permissions.PUBLIC:
            fileDirectories = filedialog.askopenfilenames(initialdir="/", title = "Select image(s) to publicly upload...", filetypes =[("Image files (.jpg, .jpeg, .png, and .gif)","*.jpg *.jpeg *.png *.gif")])
            self.openImageDir(Permissions.PUBLIC)
        else:
            fileDirectories = filedialog.askopenfilenames(initialdir="/", title = "Select image(s) to privately upload...", filetypes =[("Image files (.jpg, .jpeg, .png, and .gif)","*.jpg *.jpeg *.png *.gif")])
            self.openImageDir(Permissions.PRIVATE, username)

        # Copy selected files into database
        for fileDir in fileDirectories:  
            imgName = os.path.basename(fileDir)

            # Ask to overwrite if already exists
            if os.path.exists(imgName):
                answer = messagebox.askquestion("Attention: File already exists", f"The file {imgName} already exists in this album.\n\nWould you like to override the existing image in the repository?")
                if answer == 'yes':
                    shutil.copy(fileDir, os.getcwd())
                    if self.debug:
                        print(imgName + " was uploaded!")
            else:
                shutil.copy(fileDir, os.getcwd())

        # Close the directory
        if albumType == Permissions.PUBLIC:
            self.closeImageDir(Permissions.PUBLIC)
        else:
            self.closeImageDir(Permissions.PRIVATE, username)

    # Delete images from requested album
    def deleteImages(self, albumType, imageList, deletionIndices, username=None):
        if albumType == Permissions.PUBLIC:
            self.openImageDir(Permissions.PUBLIC)
        else:
            self.openImageDir(Permissions.PRIVATE, username)

        # Get the corresponding image name in the imageList
        for index in deletionIndices:
            imgName = imageList[index]

            try:
                os.remove(imgName)
                if self.debug:
                    print (imgName + " was deleted!")
            except:
                messagebox.showerror("Attention: Unable to Delete File", f"There was an error when try to delete {imgName} from the repository.")

        # Close directory
        if albumType == Permissions.PUBLIC:
            self.closeImageDir(Permissions.PUBLIC)
        else:
            self.closeImageDir(Permissions.PRIVATE, username)


    # Download images from requested album
    def downloadImages(self, albumType, imageList, downloadIndices, username=None):
        targetDirectory = filedialog.askdirectory(initialdir="/", title = "Select download location...")

        if albumType == Permissions.PUBLIC:
            self.openImageDir(Permissions.PUBLIC)
        else:
            self.openImageDir(Permissions.PRIVATE, username)

        # Download the corresponding item in imgList
        for index in downloadIndices:  
            imgName = imageList[index]
            
            # Ask to overwrite if already exists
            if os.path.exists(targetDirectory + "/" + imgName):
                answer = messagebox.askquestion("Attention: File already exist", f"The file {imgName} already exist in this folder.\n\nWould you like to override your existing image with the repository download?")
                if answer == 'yes':
                    shutil.copy(imgName, targetDirectory)
                    if self.debug:
                        print(imgName + " was downloaded to " + targetDirectory)
            else:
                shutil.copy(imgName, targetDirectory)

        if albumType == Permissions.PUBLIC:
            self.closeImageDir(Permissions.PUBLIC)
        elif albumType == Permissions.PRIVATE:
            self.closeImageDir(Permissions.PRIVATE, username)

        messagebox.showinfo("Success", "The download has been completed! You can find your downloaded images here:\n\n" + targetDirectory)
