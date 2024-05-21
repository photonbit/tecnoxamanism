import FreeCAD, Part


def create_box_with_magnets_and_crenels(box_length, box_width, box_height, lid_height, wall_thickness, magnet_diameter,
                                        magnet_thickness):
    doc = FreeCAD.newDocument('WoodenBoxWithMagnets')

    # Basic dimensions for crenels and magnet recesses
    crenel_depth = magnet_thickness + 0.5  # Slightly deeper than the magnet thickness for a flush fit
    crenel_width = magnet_diameter + 0.5  # Slightly wider than the magnet to ensure easy placement

    # Create the box base
    outer_box = Part.makeBox(box_length, box_width, box_height)
    inner_box = Part.makeBox(box_length - 2 * wall_thickness,
                             box_width - 2 * wall_thickness,
                             box_height - wall_thickness,
                             FreeCAD.Vector(wall_thickness, wall_thickness, wall_thickness))
    box_base = outer_box.cut(inner_box)

    # Function to create magnet recesses
    def create_magnet_recesses(shape, height_offset):
        for x in [wall_thickness - crenel_depth, box_length - wall_thickness]:
            for y in [wall_thickness - crenel_depth, box_width - wall_thickness]:
                recess = Part.makeCylinder(magnet_diameter / 2, magnet_thickness,
                                           FreeCAD.Vector(x, y, height_offset),
                                           FreeCAD.Vector(0, 0, 1))
                shape = shape.cut(recess)
        return shape

    # Add magnet recesses to the box
    box_with_magnets = create_magnet_recesses(box_base, box_height - magnet_thickness)

    # Create the lid
    lid = Part.makeBox(box_length, box_width, lid_height)

    # Add magnet recesses to the lid
    lid_with_magnets = create_magnet_recesses(lid, 0)

    # Add the modified box and lid to the document
    box_object = doc.addObject("Part::Feature", "BoxWithMagnets")
    box_object.Shape = box_with_magnets

    lid_object = doc.addObject("Part::Feature", "LidWithMagnets")
    lid_object.Shape = lid_with_magnets

    # Recompute the document to apply changes
    doc.recompute()


# Example dimensions
box_length = 100  # Length of the box in mm
box_width = 60  # Width of the box in mm
box_height = 40  # Height of the box in mm
lid_height = 5  # Height of the lid in mm
wall_thickness = 2  # Thickness of the box walls in mm
magnet_diameter = 3  # Diameter of the neodymium magnets in mm
magnet_thickness = 1  # Thickness of the neodymium magnets in mm

create_box_with_magnets_and_crenels(box_length, box_width, box_height, lid_height, wall_thickness, magnet_diameter,
                                    magnet_thickness)
