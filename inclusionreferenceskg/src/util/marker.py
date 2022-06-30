import tkinter
from tkinter.constants import DISABLED


def main():
    with open("./resources/eu_documents/gdpr.txt", encoding="utf-8") as f:
        t = f.read()

    root = tkinter.Tk()
    root.geometry("800x600")
    text = tkinter.Text(root)
    text.insert(1.0, t)
    text.config(state=DISABLED)

    listbox = tkinter.Listbox(None)

    def print_selection():
        text.edit()
        print(text.selection_get())

    button = tkinter.Button(root, text="Click", command=print_selection)

    text.pack()
    button.pack()

    root.bind("<KeyPress>", print)

    root.mainloop()

if __name__ == "__main__":
    main()
