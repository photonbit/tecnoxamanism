import FreeCAD, Part


def create_box_with_hinge_space(box_length, box_width, box_height, lid_height, wall_thickness, hinge_space_width,
                                hinge_space_depth, hinge_space_height):
    doc = FreeCAD.newDocument('WoodenBoxWithHinges')

    # Create the box base
    outer_box = Part.makeBox(box_length, box_width, box_height)
    inner_box = Part.makeBox(box_length - 2 * wall_thickness,
                             box_width - 2 * wall_thickness,
                             box_height - wall_thickness,
                             FreeCAD.Vector(wall_thickness, wall_thickness, wall_thickness))
    box_base = outer_box.cut(inner_box)

    # Modify the box to add hinge spaces at the back
    hinge_space = Part.makeBox(hinge_space_width, hinge_space_depth, hinge_space_height,
                               FreeCAD.Vector(0, box_width - hinge_space_depth, box_height - hinge_space_height))
    box_with_hinge_space = box_base.cut(hinge_space)

    # Create the lid
    lid = Part.makeBox(box_length, box_width, lid_height)

    # Modify the lid to accommodate hinge mechanism
    lid_hinge_space = Part.makeBox(hinge_space_width, hinge_space_depth, lid_height,
                                   FreeCAD.Vector(0, box_width - hinge_space_depth, 0))
    lid_with_hinge_space = lid.cut(lid_hinge_space)

    # Add the modified box and lid to the document
    box_object = doc.addObject("Part::Feature", "BoxWithHingeSpace")
    box_object.Shape = box_with_hinge_space

    lid_object = doc.addObject("Part::Feature", "LidWithHingeSpace")
    lid_object.Shape = lid_with_hinge_space

    # Reposition the lid on top of the box
    lid_object.Placement = FreeCAD.Placement(FreeCAD.Vector(0, 0, box_height),
                                             FreeCAD.Rotation(FreeCAD.Vector(0, 0, 1), 0))

    # Recompute the document to apply changes
    doc.recompute()


# Example dimensions
box_length = 100  # Length of the box in mm
box_width = 60  # Width of the box in mm
box_height = 40  # Height of the box in mm
lid_height = 5  # Height of the lid in mm
wall_thickness = 2  # Thickness of the box walls in mm
hinge_space_width = 10  # Width of the space for each hinge in mm
hinge_space_depth = 5  # Depth of the space for the hinge into the box/lid in mm
hinge_space_height = 10  # Height of the space for the hinge in mm

create_box_with_hinge_space(box_length, box_width, box_height, lid_height, wall_thickness, hinge_space_width,
                            hinge_space_depth, hinge_space_height)
