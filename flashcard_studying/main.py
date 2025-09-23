import tkinter as tk
import pandas as pd


class DataLoader:
    def __init__(self, size):
        self.size = size
        sheet_url = "chinese_char_dataset.xlsx"
        self.df = pd.read_excel(sheet_url, sheet_name="All Words (HSK 3.0)", usecols="C:E", skiprows=4)
        
    def get_set(self):
        self.sample_set = self.df.sample(n=self.size)
        return self.sample_set
    
class FlashcardApp:
    def __init__(self, root, dataLoader):
        self.root = root
        self.root.title("Chinese Flashcards")
        
        self.dataLoader = dataLoader
        self.dataset = self.dataLoader.get_set()
        self.index = 0
        self.flipped = False
        self.repeat = False
        self.correct_count = 0
        self.repeat_count = 0

        self.revisit = set()
        self.current_set = set(range(len(self.dataset))) #initialize with all cards in current set

        self.card_frame = tk.Frame(root, width=600, height=400, bg="white", relief="raised", borderwidth=2)
        self.card_frame.pack(padx=20, pady=20)

        self.card_text = tk.Label(self.card_frame, text="", font=("Arial", 24), wraplength=280)
        self.card_text.place(relx=0.5, rely=0.5, anchor="center")

        self.card_frame.bind("<Button-1>", self.flip_card)
        self.card_text.bind("<Button-1>", self.flip_card)

        # Navigation
        btn_frame = tk.Frame(root)
        btn_frame.pack(pady=10)

        self.correct_cnt = tk.Label(btn_frame, text=f"Correct: {self.index - self.repeat_count}") 
        self.correct_cnt.grid(row=0, column=1, padx=5)
        self.repeat_cnt = tk.Label(btn_frame, text=f"Repeated: {self.repeat_count}") 
        self.repeat_cnt.grid(row=0, column=3, padx=5)

        correct_btn = tk.Button(btn_frame, text="Continue", command=self.next_card)
        correct_btn.grid(row=1, column=0, padx=5)

        repeat_btn = tk.Button(btn_frame, text="Repeat", command=self.repeat_card)
        repeat_btn.grid(row=1, column=1, padx=5)

        new_btn = tk.Button(btn_frame, text="New set", command=self.get_new_set)
        new_btn.grid(row=1, column=2, padx=5)

        self.repeat_label = tk.Label(btn_frame, text=f"Repeat: {str(self.repeat)}")
        self.repeat_label.grid(row=1, column=3, padx=5)

        self.counter_label = tk.Label(btn_frame, text=f"{self.index} / {len(self.current_set)}")
        self.counter_label.grid(row=1, column=4, padx=10)

        self.show_front()

    def show_front(self):
        self.flipped = False
        word = self.dataset.iloc[self.index, 0]
        self.card_text.config(text=word)
        self.update_labels()


    def show_back(self):
        self.flipped = True
        pinyin = self.dataset.iloc[self.index, 1]
        english = self.dataset.iloc[self.index, 2]
        self.card_text.config(text=f"{pinyin}\n{english}")

    def update_labels(self):
        self.repeat_label.config(text=f"Repeat: {str(self.repeat)}")
        self.counter_label.config(text=f"{self.index + 1} / {len(self.current_set)}")
        self.correct_cnt.config(text=f"Correct: {self.index - self.repeat_count}")
        self.repeat_cnt.config(text=f"Repeated: {self.repeat_count}")

    def flip_card(self, event=None):
        if self.flipped:
            self.show_front()
        else:
            self.show_back()

    def next_card(self):
        if self.index == len(self.current_set) - 1: # finished the current set
            if self.revisit:
                self.current_set = self.revisit
                self.revisit = set()
                self.index = 0
                self.repeat = True
            else:
                print("Reached the end")
                # self.root.destroy()
                self.get_new_set()
        else:
            self.index += 1

        self.show_front()

    def repeat_card(self):
        self.revisit.add(self.index)
        self.repeat_count += 1
        self.next_card()

    def get_new_set(self):
        self.dataset = self.dataLoader.get_set()
        self.index = 0
        self.repeat = False
        self.show_front()

if __name__ == "__main__":
    num_cards = 30
    dataLoader = DataLoader(num_cards)
    print("Dataset Loaded")
    root = tk.Tk()
    app = FlashcardApp(root, dataLoader)
    root.mainloop()
