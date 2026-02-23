import FreeCAD
import FreeCADGui
import ImportGui
import TechDraw
import TechDrawGui
import os
import sys

# -----------------------------
# USER INPUT
# -----------------------------
IGES_FILE = r"C:\Users\CuttechPC-1\Downloads\test\test.igs"
PDF_FILE  = r"C:\Users\CuttechPC-1\Downloads\test\output.pdf"

# -----------------------------
# START GUI (REQUIRED)
# -----------------------------
FreeCADGui.showMainWindow()

# -----------------------------
# CREATE DOCUMENT
# -----------------------------
doc = FreeCAD.newDocument("IGES_TO_PDF")
FreeCAD.setActiveDocument(doc.Name)

# -----------------------------
# IMPORT IGES
# -----------------------------
ImportGui.insert(IGES_FILE, doc.Name)
doc.recompute()

# -----------------------------
# FIND FIRST VALID SHAPE
# -----------------------------
shape_obj = None
for obj in doc.Objects:
    if hasattr(obj, "Shape") and not obj.Shape.isNull():
        shape_obj = obj
        break

if not shape_obj:
    raise RuntimeError("No valid shape found in IGES file")

# -----------------------------
# CREATE TECHDRAW PAGE
# -----------------------------
page = doc.addObject("TechDraw::DrawPage", "Page")
template = doc.addObject("TechDraw::DrawSVGTemplate", "Template")
template.Template = TechDraw.getStandardTemplate("A4_Landscape.svg")
page.Template = template
doc.recompute()

# -----------------------------
# CREATE VIEW
# -----------------------------
view = doc.addObject("TechDraw::DrawViewPart", "MainView")
view.Source = [shape_obj]
view.Direction = (0, 0, 1)   # Top view
view.Scale = 1.0
page.addView(view)

doc.recompute()

# -----------------------------
# EXPORT TO PDF
# -----------------------------
TechDrawGui.exportPageAsPdf(page, PDF_FILE)

print("✅ PDF created successfully:")
print(PDF_FILE)
