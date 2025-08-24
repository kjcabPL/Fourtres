
Fourtres PK is an offline password generator and keeper app from Bitknvs Studio. 

You can record your users and their respective sites and passwords into the app. You can also retrieve them by searching the website they belong to and opening the needed username that appears in the dropdown list.

This app was written in Python and compiled via Nuitka.

## Usage

Run the executable named Fourtres.exe.

To add a username and password:
1. Add the website in the "website" field
2. Add the needed username or email address in the username/email field
3. Add the password you want in the password field. You can also generate your own password using the "Generate Password" which has its own options. Check the Generate Password section for more information.
4. Click on "Add Record". If the user already exists for that website, you will be prompted to update or replace the current password it already has.

## Generating Passwords

The app has 2 methods of generating randomized passwords. Both methods will show their own respective settings for generating a password

- Generating a password using random characters
1. Choose the characters to be added into the password.
2. Add the length of the password to be added. Defaults to 8 characters minimum
3. Click on "Generate Password" to create the randomized password

- Generating a password by forming a random passphrase using selected words
1. Add a word to be included in the passphrase. Populate your list as many words as you want
2. Choose the number of words to be included from the passphrase.
3. Click on "Generate Password" to create the randomized phrase from the current set of words. You can view this set of words via "Open Word List".
  
Optionally, you can choose to remove a word from the wordlist by clicking on "Open Word List". This will open the word list dialog, and selecting a word will let you "remove" that word using the Remove button.

## Building The Repository

To build the repo, just run the build script included in the repo, using

```js
./build
```

This will build the main python file along with the img folder into a "dist" folder. Use this folder as the compiled version of the program, and open it using the "Fourtres.exe" file in it.



