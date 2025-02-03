from pynput import keyboard
from pynput.keyboard import Controller, Key
import pystray
from PIL import Image
import sys
import tkinter as tk
from tkinter import messagebox
import json
import os

script_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
dictionary_path = os.path.join(script_dir, "dictionary.json")

if not os.path.exists(dictionary_path):
    defaultData = {
    "in": "∈",
    "forall": "∀",
    "thereexists": "∃",
    "or": "∨",
    "and": "∧",
    "implies": "⇒",
    "iff": "⇔",
    "emptyset": "∅",
    "epsilon": "ε",
    "notin": "∉",
    "natural": "ℕ",
    "integers": "ℤ",
    "real": "ℝ",
    "subset": "⊆"
    }

    with open(dictionary_path, "w", encoding="utf-8") as file:
        json.dump(defaultData, file)  # Initialize with the default data required

keyboardPresser = Controller()
typingCombo = False
currentCombo = ""

allLetters = [
    'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z',
    'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z',
    '0', '1', '2', '3', '4', '5', '6', '7', '8', '9',
    '!', '@', '#', '$', '%', '^', '&', '*', '(', ')', '-', '_', '=', '+',
    '[', ']', '{', '}', '|', '\\', ';', ':', "'", '"', ',', '.', '/', '?', '`', '~'
]

# Dictionary for all available superscripts
SUPERSCRIPT_MAP = str.maketrans(
    "0123456789abdefghijklmnoprstuvwxyzABDEGHIJKLMNOPRTUVW+-=()",
    "⁰¹²³⁴⁵⁶⁷⁸⁹ᵃᵇᵈᵉᶠᵍʰⁱʲᵏˡᵐⁿᵒᵖʳˢᵗᵘᵛʷˣʸᶻᴬᴮᴰᴱᴳᴴᴵᴶᴷᴸᴹᴺᴼᴾᴿᵀᵁⱽᵂ⁺⁻⁼⁽⁾"
)

# Dictionary for all available subscripts
SUBSCRIPT_MAP = str.maketrans(
    "0123456789aehlmnopst+-=()",
    "₀₁₂₃₄₅₆₇₈₉ₐₑₕₗₘₙₒₚₛₜ₊₋₌₍₎"
)

def getSpecialCharacter(combo):
    def formatString(string):
        allowedChars = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789+-=()")
        filteredString = ''.join(char for char in string if char in allowedChars).lower()  # Allow letters, numbers, and allowed punctuation. convert to lowercase
        print(filteredString)

        if "power" in string:
            filteredString = filteredString.replace("power", "")

        elif "sub" in string:
            filteredString = filteredString.replace("sub", "")

        return filteredString

    # Types the powers separately from regular characters because they use a different dictionary
    if "power" in combo:
        filteredString = formatString(combo)

        specialCharacter = filteredString.translate(SUPERSCRIPT_MAP)
        if filteredString == specialCharacter:
            print("Not in map")
        else:
            keyboardPresser.type('\b' * (len(combo) + 2))  # type backspaces to remove what the user typed
            keyboardPresser.type(specialCharacter)

    # Types the subsets separately from regular characters because they use a different dictionary
    elif "sub" in combo:
        filteredString = formatString(combo)

        specialCharacter = filteredString.translate(SUBSCRIPT_MAP)
        if filteredString == specialCharacter:
            print("Not in map")
        else:
            keyboardPresser.type('\b' * (len(combo) + 2))  # type backspaces to remove what the user typed
            keyboardPresser.type(specialCharacter)

    else:
        try:
            with open("dictionary.json", encoding="utf-8") as file:
                dictionary = json.load(file)
                specialCharacter = dictionary[formatString(combo)]

            print(specialCharacter)

            keyboardPresser.type('\b' * (len(combo) + 2)) # type backspaces to remove what the user typed
            keyboardPresser.type(specialCharacter)

        except KeyError:
            print("invalid character: " + combo)


def onPress(key):
    global typingCombo, currentCombo

    if key == keyboard.Key.backspace and len(currentCombo) > 0:
        currentCombo = currentCombo[:-1] # Remove the last typed character if the user clicks backspace

    if key == keyboard.Key.space and typingCombo:
        currentCombo += " " # Adds a space if the user types one (required because space is not a char, it is keyboard.Key.space)

    try:
        if key.char == '<' and not typingCombo:
            typingCombo = True # detect the start of a special character

        elif key.char == '<' and typingCombo:
            currentCombo += ' ' # if the user accidentally clicks it again, add a placeholder
                                # character so the correct amount of backspaces are typed

        elif key.char == '>' and typingCombo:
            typingCombo = False
            getSpecialCharacter(currentCombo)
            currentCombo = "" # detect end of special character, type it, and then reset the currentCombo

        elif key.char in allLetters and typingCombo:
            if len(currentCombo) > 15:
                currentCombo = ""
                typingCombo = False # reset the combo if it's too long (user just wanted a <, not to start a combo)

            else:
                currentCombo = currentCombo + key.char # add the character to the combo

    except AttributeError:
        pass

def onRelease(key):
    pass

image = Image.open("logo.png")
listener = None

def after_click(icon, query):
    if str(query) == "Exit":
        icon.stop()
        if listener and listener.running:
            listener.stop()  # Stop the keyboard listener if it is running
        sys.exit(0)

    def submit():
        phrase = phrase_var.get()
        char = char_var.get()

        with open("dictionary.json", encoding="utf-8") as file:
            dictionary = json.load(file)

        # Validation checks

        if not (phrase.isalpha() and phrase.islower()):
            messagebox.showerror("Invalid Input", "Phrase must only contain lowercase letters.")
            return

        if '<' in phrase or '>' in phrase or '<' in char or '>' in char:
            messagebox.showerror("Invalid Input", "Inputs must not contain '<' or '>'.")
            return

        if len(phrase) < 1:
            messagebox.showerror("Invalid Input", "Phrase must be at least 1 character long.")
            return

        if len(char) != 1:
            messagebox.showerror("Invalid Input", "Character must be exactly 1 character long.")
            return

        if phrase in dictionary:
            messagebox.showerror("Invalid Input", f"{phrase} already exists!")
            return

        # Add to the dictionary

        dictionary[phrase] = char

        with open("dictionary.json", "w", encoding="utf-8") as file:
            json.dump(dictionary, file, ensure_ascii=False, indent=4)

        messagebox.showinfo("Success", f"Added: {phrase} ⇒ {char}")
        window.destroy()

    # Create the GUI

    window = tk.Tk()
    window.title("Add New Character")

    tk.Label(window, text="Phrase").grid(row=0, column=0, padx=10, pady=5)
    phrase_var = tk.StringVar()
    tk.Entry(window, textvariable=phrase_var).grid(row=0, column=1, padx=10, pady=5)

    tk.Label(window, text="Character").grid(row=1, column=0, padx=10, pady=5)
    char_var = tk.StringVar()
    tk.Entry(window, textvariable=char_var).grid(row=1, column=1, padx=10, pady=5)

    tk.Button(window, text="Submit", command=submit).grid(row=2, column=0, columnspan=2, pady=10)

    # Run the Tkinter event loop

    window.mainloop()

icon = pystray.Icon("Chars", image, "Special Characters", menu = pystray.Menu(
    pystray.MenuItem("Exit", after_click),
    pystray.MenuItem("Add character", after_click)
    )
)

listener = keyboard.Listener(on_press=onPress, on_release=onRelease)
listener.start()

icon.run()

