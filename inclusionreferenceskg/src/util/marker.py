"""
Unrefined GUI to quickly mark parts of a text and store the locations of the marks.
"""
from __future__ import annotations

import dataclasses
import tkinter
import uuid
from pathlib import Path
from tkinter.constants import DISABLED
from typing import Any, Optional

import _tkinter


@dataclasses.dataclass
class Mark:
    id: str
    tag_start: str
    tag_end: str
    start: int
    end: int
    selection: str

    @staticmethod
    def from_line(line: str) -> Optional["Mark"]:
        if not line:
            return None
        id_, tag_start, tag_end, start, end, *selection = line.split(" ")
        return Mark(id_, tag_start, tag_end, int(start), int(end), " ".join(selection))

    def to_line(self) -> str:
        return f"{self.id} {self.tag_start} {self.tag_end} {self.start} {self.end} {self.selection}"


def main():
    with open("./resources/eu_documents/gdpr.txt", "r", encoding="utf-8") as f:
        t = f.read()

    output_file_name = "./resources/eu_documents/gdpr_marks.txt"

    marked = []
    Path(output_file_name).touch(exist_ok=True)

    font = ("Courier", 14)

    root = tkinter.Tk()
    text = tkinter.Text(root, width=120, height=30, font=font)
    text.insert(1.0, t)
    text.config(state=DISABLED)

    listbox = tkinter.Listbox(root, font=font, height=30, width=60)

    def place_mark(*_, mark: Mark = None):
        if mark is None:
            try:
                selection = text.selection_get()
            except _tkinter.TclError:
                return
            mark = Mark(str(uuid.uuid4()),
                        text.index(tkinter.SEL_FIRST), text.index(tkinter.SEL_LAST),
                        text.count("1.0", tkinter.SEL_FIRST)[0], text.count("1.0", tkinter.SEL_LAST)[0],
                        selection.replace("\n", " "))

        marked.insert(0, mark)
        listbox.insert(0, mark.selection)
        text.tag_add(mark.id, mark.tag_start, mark.tag_end)
        text.tag_config(mark.id, background="purple", foreground="white")

    def delete_mark(*_, index: tuple[Any, ...] | tuple):
        if not index:
            return
        if not marked:
            return
        for ind in index:
            if ind < 0 or ind >= len(marked):
                return
            text.tag_delete(marked[ind].id)
            del marked[ind]
            listbox.delete(ind)

    def select_mark(*_, index: tuple[Any, ...] | tuple):
        if not marked:
            return
        for mark in marked:
            text.tag_config(mark.id, background="purple", foreground="white")

        if not index:
            return
        if not marked:
            return
        for ind in index:
            if ind < 0 or ind >= len(marked):
                return
            text.tag_config(marked[ind].id, background="green")
        text.see(marked[index[0]].tag_start)

    def save(*_):
        with open(output_file_name, "w+", encoding="utf-8") as of:
            of.write("\n".join(m.to_line() for m in marked))

    with open(output_file_name, "r", encoding="utf-8") as output_file:
        for line in output_file.read().splitlines():
            if marK := Mark.from_line(line):
                place_mark(mark=marK)

    button_frame = tkinter.Frame()
    mark_button = tkinter.Button(button_frame, text="Mark [SPACE]", command=place_mark)
    save_button = tkinter.Button(button_frame, text="Save [CTRL-S]", command=save)
    mark_button.pack(side=tkinter.LEFT, expand=True)
    save_button.pack(side=tkinter.LEFT, expand=True)

    text.grid(row=0, column=0)
    button_frame.grid(row=1, column=0, columnspan=2)
    listbox.grid(row=0, column=1)

    root.bind("<space>", place_mark)
    root.bind("<Control-z>", lambda *_: delete_mark(index=(0,)))
    root.bind("<Control-s>", save)
    listbox.bind("<Delete>", lambda *_: delete_mark(index=listbox.curselection()))
    listbox.bind("<<ListboxSelect>>", lambda *_: select_mark(index=listbox.curselection()))

    root.mainloop()
    save()


if __name__ == "__main__":
    main()
