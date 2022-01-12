import math
from threading import Timer
from tkinter import Frame, Canvas, Label, LAST, Scale, HORIZONTAL, StringVar, DoubleVar, Spinbox


def wavelength_to_rgb(wavelength, gamma=0.8):
    wavelength = float(wavelength)
    if 380 <= wavelength <= 440:
        attenuation = 0.3 + 0.7 * (wavelength - 380) / (440 - 380)
        R = ((-(wavelength - 440) / (440 - 380)) * attenuation) ** gamma
        G = 0.0
        B = (1.0 * attenuation) ** gamma
    elif 440 <= wavelength <= 490:
        R = 0.0
        G = ((wavelength - 440) / (490 - 440)) ** gamma
        B = 1.0
    elif 490 <= wavelength <= 510:
        R = 0.0
        G = 1.0
        B = (-(wavelength - 510) / (510 - 490)) ** gamma
    elif 510 <= wavelength <= 580:
        R = ((wavelength - 510) / (580 - 510)) ** gamma
        G = 1.0
        B = 0.0
    elif 580 <= wavelength <= 645:
        R = 1.0
        G = (-(wavelength - 645) / (645 - 580)) ** gamma
        B = 0.0
    elif 645 <= wavelength <= 750:
        attenuation = 0.3 + 0.7 * (750 - wavelength) / (750 - 645)
        R = (1.0 * attenuation) ** gamma
        G = 0.0
        B = 0.0
    else:
        R = 0.0
        G = 0.0
        B = 0.0
    R *= 255
    G *= 255
    B *= 255
    return int(R), int(G), int(B)


def rgbToHex(rgb):
    return "#%02x%02x%02x" % rgb


def opacity(rgb, opacity=1.0):
    r, g, b = rgb
    return int(r * opacity), int(g * opacity), int(b * opacity)


class Window(Frame):

    def __init__(self, root):
        super().__init__()
        # controls
        self.t = None
        self.systemButton = None
        self.brightnessLabel = None
        self.concentrationLabel = None
        self.concentrationRange = None
        self.lengthOfBottleLabel = None
        self.lengthOfBottleInput = None
        self.absorptionInput = None
        self.absorptionLabel = None
        self.waveLengthLabel = None
        self.waveLengthInput = None

        # size setup
        self.root = root

        w = root.winfo_screenwidth()
        h = root.winfo_screenheight()
        self.width = 1200
        self.height = 350
        w = w // 2
        h = h // 2
        w = w - self.width // 2
        h = h - self.height // 2

        i0Initial = 50

        # model variables connected to controls
        self.eps = StringVar(root, value="0.55")
        self.L = DoubleVar(root, value=2)
        self.waveLength = DoubleVar(root, value=652)
        self.i0 = DoubleVar(root, value=i0Initial)
        self.c = StringVar(root, value="0.24")

        # output model variables

        self.A = 0
        self.i1 = 0
        self.i1Opacity = 1
        self.i0Opacity = i0Initial / 100

        # ui init
        self.inited = False
        self.root.geometry('{}x{}+{}+{}'.format(self.width, self.height - 30, w, h))
        self.root.resizable(False, False)
        self.root.configure(background='#fff')
        self.canvas = None
        self.initUI()

    def initUI(self):
        self.master.title("Sensors")

        # Brightness (I0)
        self.brightnessLabel = Label(text="Яркость света (I₀, %): ")
        self.brightnessLabel.grid(row=0, column=1)
        self.absorptionInput = Scale(self.root, from_=0, to=100, orient=HORIZONTAL, variable=self.i0,
                                     command=self.updateModel)
        self.absorptionInput.grid(row=1, column=1)

        # Concentration (c)
        self.concentrationLabel = Label(text="Концентрация растворённого вещества (c, моль/литр): ")
        self.concentrationLabel.grid(row=0, column=2)
        self.concentrationRange = Spinbox(self.root, textvariable=self.c, validatecommand=self.inputsUpdated,
                                          validate="all")
        self.concentrationRange.grid(row=1, column=2)

        # Length of bottle (L)
        self.lengthOfBottleLabel = Label(text="Длина кюветы L (см): ")
        self.lengthOfBottleLabel.grid(row=0, column=3)
        self.lengthOfBottleInput = Scale(self.root, from_=1, to=8, orient=HORIZONTAL, variable=self.L,
                                         command=self.updateModel)
        self.lengthOfBottleInput.grid(row=1, column=3)

        # Absorption (ε)
        self.absorptionLabel = Label(text="Молярный коэф-т поглощения ε")
        self.absorptionLabel.grid(row=0, column=5)
        self.absorptionInput = Spinbox(self.root, textvariable=self.eps, validatecommand=self.inputsUpdated,
                                       validate="all")
        self.absorptionInput.grid(row=1, column=5)

        # Wave length
        self.waveLengthLabel = Label(text="Длина волны монохроматора")
        self.waveLengthLabel.grid(row=0, column=6)
        self.waveLengthInput = Scale(self.root, from_=380, to=750, orient=HORIZONTAL, variable=self.waveLength,
                                     command=self.updateModel)
        self.waveLengthInput.grid(row=1, column=6)

        self.initCanvas()

    def inputsUpdated(self, *args):
        if (self.t):
            self.t.cancel()
            self.t = None

        self.t = Timer(0.001, self.updateModel)
        self.t.start()

        return True

    def updateModel(self, *args):
        # A = εLc

        try:
            transmited = 1

            if self.i0.get() == 0:
                self.A = 0
            else:
                if (
                        len(self.eps.get()) != 0 and
                        len(self.c.get()) != 0
                ):
                    self.A = float(self.eps.get()) * self.L.get() * float(self.c.get())
                    transmited = 1 / math.exp(self.A)
                else:
                    self.A = 0
                    transmited = 1

            self.i0Opacity = self.i0.get() / 100
            self.i1Opacity = self.i0Opacity * transmited

            self.drawModel()

        except:
            pass

    def drawModel(self):
        if not self.inited:
            return

        self.canvas.delete("all")
        self.drawStraightLightRays()
        self.drawDiaglonalLightRays()
        self.drawBulb()
        self.drawLens()
        self.drawMonochromator()
        self.drawMonoLight()
        self.drawBottle()
        self.drawDetector()

    def initCanvas(self):
        if self.canvas:
            self.canvas.destroy()
        self.canvas = Canvas(self.root, width=self.width, height=self.height - 100, highlightthickness=0)
        self.canvas.configure(background='black')
        self.canvas.grid(row=2, columnspan=7, pady=10)
        self.inited = True

    def drawBulb(self):
        startX = 50
        startY = 50
        width = 100
        height = 200
        lightColor = self.getLightColor()
        self.canvas.create_oval(startX, startY, startX + width, startX + height,
                                fill=lightColor,
                                outline='yellow',
                                width=1,
                                )
        self.createRoundRect(startX + 10, startY + height - 30, startX + width - 10, startY + height + 30,
                             fill='#1d1d1d')

    def drawStraightLightRays(self):
        startX = 50
        startY = 50
        width = 100
        lightColor = self.getLightColor()
        self.canvas.create_line(startX + width // 2, startY + 50, startX + width + 128, startY + 50, arrow=LAST,
                                fill=lightColor, width=5)
        self.canvas.create_line(startX + width // 2, startY + 100, startX + width + 128, startY + 100, arrow=LAST,
                                fill=lightColor, width=5)
        self.canvas.create_line(startX + width // 2, startY + 150, startX + width + 128, startY + 150, arrow=LAST,
                                fill=lightColor, width=5)

    def drawDiaglonalLightRays(self):
        startX = 320
        startY = 50
        width = 80
        lightColor = self.getLightColor()
        self.canvas.create_line(startX - 20, startY + 50, startX + width, 140, arrow=LAST,
                                fill=lightColor, width=5)
        self.canvas.create_line(startX, startY + 100, startX + width, 150, arrow=LAST,
                                fill=lightColor, width=5)
        self.canvas.create_line(startX - 20, startY + 150, startX + width, 160, arrow=LAST,
                                fill=lightColor, width=5)

    def drawMonochromator(self):
        self.createRoundRect(400, 100, 550, 200, fill='#1d1d1d')
        self.canvas.create_text(475, 150, fill="#c3c3c3", font="Arial 16 bold",
                                text="Монохроматор")

    def getLightColor(self):
        return rgbToHex(opacity((255, 255, 0), self.i0Opacity))

    def drawLens(self):
        off = 30
        self.canvas.create_polygon([
            310 - off, 150,
            305 - off, 50,
            370 - off, 150,
            305 - off, 250,
            310 - off, 150,
        ], smooth=True, fill='blue')
        self.canvas.create_polygon([
            310 - off, 150,
            305 - off, 50,
            330 - off, 150,
            305 - off, 250,
            310 - off, 150,
        ], smooth=True, fill='DarkBlue')

    def drawMonoLight(self):
        rgb = wavelength_to_rgb(self.waveLength.get())

        self.createRect(550, 145, 140, 10, rgbToHex(opacity(rgb, self.i0Opacity)))
        self.createRect(720, 145, 110, 10, rgbToHex(opacity(rgb, self.i1Opacity)))

    def drawBottle(self):
        c = self.c.get()
        cnum = 0
        if (len(c) == 0):
            cnum = 0
        else:
            cnum = 1 - float(c)

        cnum = max(cnum, 0.3)

        start = 690 - (self.L.get() // 2) * 30
        width = self.L.get() * 30

        self.canvas.create_rectangle(start, 60, start + width, 200, fill=rgbToHex((210, 226, 241)))
        self.canvas.create_rectangle(start, 120, start + width, 200, fill=rgbToHex(opacity((86, 135, 225), cnum)))
        self.canvas.create_oval(start, 50, start + width, 74, fill=rgbToHex((228, 237, 246)))
        self.canvas.create_oval(start, 110, start + width, 134, fill=rgbToHex(opacity((152, 182, 236), cnum)))
        self.canvas.create_oval(start, 190, start + width, 214, fill=rgbToHex(opacity((86, 135, 225), cnum)))

    def drawDetector(self):
        self.createRect(830, 120, 50, 60, '#1d1d1d')
        self.canvas.create_rectangle(880, 120 + 5, 1175, 180 - 5, outline="#1d1d1d", width=10)
        self.canvas.create_text(1020, 150, fill="red", font="Arial 30 bold",
                                text="{}".format(round(self.A, 15)),
                                justify="left"
                                )

    def createCircle(self, x, y, r):
        x0 = x - r
        y0 = y - r
        x1 = x + r
        y1 = y + r
        self.canvas.create_oval(x0, y0, x1, y1, fill="yellow", width=0)

    def createRect(self, x, y, w, h, fill):
        self.canvas.create_rectangle(x, y, x + w, y + h, fill=fill, width=0)

    def createRoundRect(self, x1, y1, x2, y2, radius=25, **kwargs):
        points = [x1 + radius, y1,
                  x1 + radius, y1,
                  x2 - radius, y1,
                  x2 - radius, y1,
                  x2, y1,
                  x2, y1 + radius,
                  x2, y1 + radius,
                  x2, y2 - radius,
                  x2, y2 - radius,
                  x2, y2,
                  x2 - radius, y2,
                  x2 - radius, y2,
                  x1 + radius, y2,
                  x1 + radius, y2,
                  x1, y2,
                  x1, y2 - radius,
                  x1, y2 - radius,
                  x1, y1 + radius,
                  x1, y1 + radius,
                  x1, y1]

        return self.canvas.create_polygon(points, **kwargs, smooth=True)
