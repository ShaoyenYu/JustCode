import os
from reportlab.pdfgen import canvas

DEFAULT_PATH = os.path.join(os.path.expanduser("~"), "Desktop", "")


# A pdfgen program is essentially a sequence of instructions for "painting" a document onto a sequence of pages.
# `canvas` is the interface object which provides the painting operation.


def hello(c: canvas.Canvas):
    c.drawString(100, 100, "Hello World")


c = canvas.Canvas("hello.pdf")
hello(c)
c.showPage()
c.save()

# Most common page sizes are found in the library module

from reportlab.lib.pagesizes import letter, A4


def hello(c: canvas.Canvas = None):
    c = canvas.Canvas("hello.pdf")

    from reportlab.lib.units import inch
    c.translate(inch, inch)

    c.setFont("Helvetica", 20)

    c.setStrokeColorRGB(0.2, 0.5, 0.3)
    c.setFillColorRGB(1, 0, 1)

    c.line(0, 0, 0, 1.7 * inch)
    c.line(0, 0, 1 * inch, 0)

    c.rotate(30)
    c.rect(0.2 * inch, 0.2 * inch, inch, 1.5 * inch, fill=1)

    c.rotate(-30)
    c.setFillColorRGB(0, 0.15, 0.03)
    c.setFillColorRGB(0.31, 0.15, 0.64)
    c.drawString(20, 20, "Hello World from Reportlab")

    c.showPage()
    c.save()


hello(1)
