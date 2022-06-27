import tkinter


def main():
    with open("./resources/eu_documents/gdpr.txt", encoding="utf-8") as f:
        t = f.read()



    root = tkinter.Tk()
    text = tkinter.Text(root)
    text.insert(1.0, t)

    def print_selection():
        print(text.selection_get())

    button = tkinter.Button(root, text="Click", command=print_selection)

    text.pack()
    button.pack()

    root.mainloop()

if __name__ == "__main__":
    main()
