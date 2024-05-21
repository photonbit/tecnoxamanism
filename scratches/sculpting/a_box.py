import FreeCAD, Part


def create_box_with_lid(box_length, box_width, box_height, lid_height, wall_thickness):
    doc = FreeCAD.newDocument('WoodenBoxWithLid')

    # Create the box base
    outer_box = Part.makeBox(box_length, box_width, box_height)
    inner_box = Part.makeBox(box_length - 2 * wall_thickness,
                             box_width - 2 * wall_thickness,
                             box_height - wall_thickness,
                             FreeCAD.Vector(wall_thickness, wall_thickness, wall_thickness))
    box_base = outer_box.cut(inner_box)

    # Create the lid
    lid = Part.makeBox(box_length, box_width, lid_height)

    # Add the box and the lid to the document
    box_base_object = doc.addObject("Part::Feature", "BoxBase")
    box_base_object.Shape = box_base

    lid_object = doc.addObject("Part::Feature", "Lid")
    lid_object.Shape = lid

    # Reposition the lid on top of the box
    lid_object.Placement = FreeCAD.Placement(FreeCAD.Vector(0, 0, box_height),
                                             FreeCAD.Rotation(FreeCAD.Vector(0, 0, 1), 0))

    # Recompute the document to apply changes
    doc.recompute()

    # Optionally, save the document
    # doc.saveAs('path/to/save/your/file.FCStd')


# Example dimensions
box_length = 100  # Length of the box in mm
box_width = 60  # Width of the box in mm
box_height = 40  # Height of the box in mm
lid_height = 5  # Height of the lid in mm
wall_thickness = 2  # Thickness of the box walls in mm

create_box_with_lid(box_length, box_width, box_height, lid_height, wall_thickness)
