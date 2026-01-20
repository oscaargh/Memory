"""
Memory By Oscar Fonsati.

GUI program for a memory game. Running the code opens a tkinter window and the user has to find
matching pairs of words (which the buttons represent). When all of the pairs are found, a new window appears where
the user is now instructed to enter their name. The name which the user entered is combined with the number of
wrong attempts required for the user to finish the game, and are then added to a scoreboard which can be opened in a
drop down options menu.

"""

import tkinter as tk
import random
from tkinter import messagebox


class Window(object):
    """Class for all methods that open a tkinter window or add something new to tkinter window."""

    def __init__(self):
        self.logic = MemoryLogic()
        self.root = tk.Tk()  # Main window for game.
        self.root.title("OSCARS MEMORY 2000")
        self.root.geometry("480x550")
        self.buttonList = []
        self.currentButtonPicked = []
        self.button_creator(self.root)
        self.drop_down_menu()
        self.wrong_attempts_count()
        self.root.mainloop()

    def drop_down_menu(self):
        """Creates drop down menu in main window. Pressing the drop down menu will allow you to access the
        scoreboard."""

        drop_down_menu = tk.Menu(self.root)
        self.root.config(menu=drop_down_menu)

        option_menu = tk.Menu(drop_down_menu)
        drop_down_menu.add_cascade(label="Options", menu=option_menu)
        option_menu.add_command(label="Scoreboard", command=self.scoreboard)

    def wrong_attempts_count(self):
        """Counts number of wrong picks in memory (picking buttons that do not match) and display them in main window.
         The number of wrong attempts are counted at bottom of main window."""

        self.label = tk.Label(text="Antal fel: " + str(self.logic.attempts), font=20)
        self.label.grid(row=10, column=0, columnspan=9)

    def button_creator(self, root):
        """Creates 6x6 grid with all buttons for memory."""

        counter = 0
        for row in range(6):
            for column in range(6):
                button = tk.Button(root, text="", height=5, width=10,
                                   command=lambda index=counter: self.button_click(index))
                self.buttonList.append(button)
                button.grid(row=row, column=column)
                counter += 1

    def button_click(self, index):
        """Method for what should happen after a button is pressed. When two buttons are pressed one after the other
         the assigned word for each button is compared. If the assigned word is the same for both buttons and the
         user has not pressed the same button twice, the two buttons which have been pressed are disabled. Once all
         pairs are found the method self.win() is initiated. If the user has pressed the same button twice or pressed
         two buttons that represent different words, the number of wrong attempts is increased with one."""

        button_pressed = self.buttonList[index]
        button_pressed.config(text=self.logic.wordsWithPairs[index])
        self.currentButtonPicked.append(button_pressed)
        self.logic.currentPickedWords.append(self.logic.wordsWithPairs[index])

        currently_pressed_buttons = len(self.logic.currentPickedWords)

        if currently_pressed_buttons == 2:
            if self.currentButtonPicked[0] != self.currentButtonPicked[1]:
                if self.logic.are_words_same():

                    for key in self.currentButtonPicked:
                        key["state"] = "disabled"

                    self.logic.nrOfCorrectPicks += 1
                    messagebox.showinfo("Matchning!", "Matching!")
                    self.logic.currentPickedWords.clear()
                    self.currentButtonPicked.clear()

                else:
                    messagebox.showinfo("Fel", "Fel!")
                    self.logic.attempts += 1
                    self.label.config(text="Antal fel: " + str(self.logic.attempts))

                    for key in self.currentButtonPicked:
                        key["text"] = " "

                    self.currentButtonPicked.clear()
                    self.logic.currentPickedWords.clear()
            else:
                messagebox.showinfo("HALLÅ?!", "TRYCK INTE PÅ SAMMA KNAPP!")
                self.logic.attempts += 1
                self.label.config(text="Försök: " + str(self.logic.attempts))
                for key in self.currentButtonPicked:
                    key["text"] = " "

                self.currentButtonPicked.clear()
                self.logic.currentPickedWords.clear()

        if self.logic.nrOfCorrectPicks == 18:
            self.win()

    def win(self):
        """Opens new window once you have won. The new window allows the user to type their name in a
        text box, the name is then added to an external text file along with their number of wrong guesses."""

        scoreboard_window = tk.Tk()
        scoreboard_window.title("Grattis du vann!")
        scoreboard_window.geometry("400x40")

        scoreboard_label = tk.Label(scoreboard_window, text="Skriv in ditt namn för plats på topplistan:")
        scoreboard_label.grid(column=0, row=0)

        input_text_box = tk.Text(scoreboard_window, height=0, width=15)
        input_text_box.grid(column=4, row=0)

        input_button = tk.Button(scoreboard_window, text="OK",
                                 command=lambda: self.logic.save_to_scoreboard_file(input_text_box, scoreboard_window))
        input_button.grid(column=5, row=0)

        scoreboard_window.mainloop()

    def scoreboard(self):
        """Opens a window to view the scoreboard with result from other players. In the scoreboard
         window you can see how many wrong guesses each player has and their name."""

        scoreboard_window = tk.Tk()
        scoreboard_window.title("Topplista")
        scoreboard_window.geometry("400x400")
        scoreboard_list = self.logic.create_list_from_file("topplista.txt")

        self.logic.sort_scoreboard_list(scoreboard_list)

        for i in range(len(scoreboard_list)):
            scoreboard_name_and_result = tk.Label(scoreboard_window, text=str(i + 1) + "   Namn: " +
                                                                          str(scoreboard_list[i].split(":")[1]) +
                                                                          "    Antal fel: " +
                                                                          str(scoreboard_list[i].split(":")[0]))
            scoreboard_name_and_result.grid(column=0, row=i)

        scoreboard_window.mainloop()


class MemoryLogic(object):
    """Class for everything that is running the memory and not visible to user."""

    def __init__(self):
        self.wordList = self.create_list_from_file("memo.txt")  # +700 words
        self.wordsWithPairs = []  # 36 words
        self.currentPickedWords = []
        self.nrOfCorrectPicks = 0
        self.word_to_button_assigner()
        self.attempts = 0

    def word_to_button_assigner(self):
        """Assigns a word to each button in the buttons grid that is the memory."""

        random.shuffle(self.wordList)
        for i in range(2):
            for j in range(18):
                self.wordsWithPairs.append(self.wordList[j])

        random.shuffle(self.wordsWithPairs)

    def create_list_from_file(self, filename):
        """Opens file with all words necessary for the memory and append them to a list."""

        list_from_file = []
        with open(filename, encoding="UTF-8") as file:
            for word in file:
                word = word.strip()
                list_from_file.append(str(word))
        return list_from_file

    def are_words_same(self):
        """Evaluates if two currently selected buttons have same words assigned to them."""

        is_same = self.currentPickedWords[0] == self.currentPickedWords[1]
        return is_same

    def save_to_scoreboard_file(self, input_text_box, scoreboard_window):
        """Saves input from a tkinter text box and write them to an external text file."""

        input_from_tkinter_textbox = input_text_box.get(1.0, "end-1c")
        file_to_write_results_to = open("topplista.txt", "a", encoding="UTF-8")
        file_to_write_results_to.write(str(self.attempts) + ":" + input_from_tkinter_textbox + "\n")
        file_to_write_results_to.close()
        scoreboard_window.destroy()  # Closes scoreboard_window

    def sort_scoreboard_list(self, list_to_sort):
        """Sorts list with numbers and names split with ':' by the value of the numbers which are split with ':'."""

        for i in range(len(list_to_sort)):
            for j in range(i + 1, len(list_to_sort)):
                if int(list_to_sort[i].split(":")[0]) > int(list_to_sort[j].split(":")[0]):
                    temporary_value_to_switch_elements_in_list = list_to_sort[i]
                    list_to_sort[i] = list_to_sort[j]
                    list_to_sort[j] = temporary_value_to_switch_elements_in_list


def main():
    Window()


if __name__ == "__main__":
    main()
