from tkinter import Frame, Canvas, Entry, Label, Button, Scale, HORIZONTAL


class Window(Frame):

    def __init__(self, root):
        super().__init__()
        self.root = root
        w = root.winfo_screenwidth()
        h = root.winfo_screenheight()
        self.width = 1200
        self.height = 400
        w = w // 2
        h = h // 2
        w = w - self.width // 2
        h = h - self.height // 2

        self.root.geometry('{}x{}+{}+{}'.format(self.width, self.height, w, h))
        # self.root.resizable(False, False)
        # self.root.configure(background='#ccc')
        self.canvas = None
        self.initUI()

    def initUI(self):
        self.master.title("Sensors")

        # System button
        systemButton = Button(text="Питание")
        systemButton.grid(row=0, column=0, pady=10)

        # Brightness
        brightnessLabel = Label(text="Яркость света (I₀): ")
        brightnessLabel.grid(row=0, column=1)
        brightnessInput = Entry(self.root)
        brightnessInput.grid(row=1, column=1)

        # Concentration
        concentrationLabel = Label(text="Концентрация растворённого вещества (c, %): ")
        concentrationLabel.grid(row=0, column=2)
        concentrationRange = Scale(self.root, from_=0, to=100, orient=HORIZONTAL)
        concentrationRange.grid(row=1, column=2)

        self.initCanvas()

    def initCanvas(self):
        if self.canvas:
            self.canvas.destroy()
        self.canvas = Canvas(self.root, width=self.width, height=self.height - 100)
        self.canvas.configure(background='yellow')
        self.canvas.grid(row=2, columnspan=7, pady=10)
