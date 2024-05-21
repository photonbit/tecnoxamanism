import FreeCAD, Part


def create_crenelated_box_with_magnets(box_length, box_width, box_height, lid_height, wall_thickness, magnet_diameter,
                                       magnet_thickness, crenel_size, crenel_depth):
    doc = FreeCAD.newDocument('CrenelatedBoxWithMagnets')

    # Create the basic box shape
    outer_box = Part.makeBox(box_length, box_width, box_height)
    inner_box = Part.makeBox(box_length - 2 * wall_thickness, box_width - 2 * wall_thickness,
                             box_height - wall_thickness,
                             FreeCAD.Vector(wall_thickness, wall_thickness, wall_thickness))
    box_base = outer_box.cut(inner_box)

    # Function to add crenels to the box
    def add_crenels_to_edge(shape, z_height):
        crenel_pattern = []
        for x in range(0, int(box_length / crenel_size) + 1, 2):
            crenel = Part.makeBox(crenel_size, wall_thickness, crenel_depth,
                                  FreeCAD.Vector(x * crenel_size, 0, z_height))
            crenel_pattern.append(crenel)
        for x in range(0, int(box_width / crenel_size) + 1, 2):
            crenel = Part.makeBox(wall_thickness, crenel_size, crenel_depth,
                                  FreeCAD.Vector(0, x * crenel_size, z_height))
            crenel_pattern.append(crenel)
        for crenel in crenel_pattern:
            shape = shape.fuse(crenel)
        return shape

    # Add crenels to the box
    box_with_crenels = add_crenels_to_edge(box_base, box_height - crenel_depth)

    # Create the lid with notches to fit the crenels
    lid = Part.makeBox(box_length, box_width, lid_height)
    lid_with_notches = add_crenels_to_edge(lid, -crenel_depth)  # Negative depth to cut notches instead of adding

    # Function to create magnet recesses
    def create_magnet_recesses(shape, z_offset):
        for i in range(4):  # Four corners
            x_offset = 0 if i % 2 == 0 else box_length - magnet_diameter
            y_offset = 0 if i < 2 else box_width - magnet_diameter
            magnet_recess = Part.makeCylinder(magnet_diameter / 2, magnet_thickness,
                                              FreeCAD.Vector(x_offset, y_offset, z_offset), FreeCAD.Vector(0, 0, 1))
            shape = shape.cut(magnet_recess)
        return shape

    # Add magnet recesses to the box and lid
    box_ready = create_magnet_recesses(box_with_crenels, box_height - magnet_thickness)
    lid_ready = create_magnet_recesses(lid_with_notches, 0)

    # Add the modified box and lid to the document
    box_object = doc.addObject("Part::Feature", "BoxReady")
    box_object.Shape = box_ready

    lid_object = doc.addObject("Part::Feature", "LidReady")
    lid_object.Shape = lid_ready

    # Recompute the document to apply changes
    doc.recompute()


# Example dimensions and parameters
box_length = 100  # Length of the box in mm
box_width = 60  # Width of the box in mm
box_height = 40  # Height of the box in mm
lid_height = 5  # Height of the lid in mm
wall_thickness = 2  # Thickness of the box walls in mm
magnet_diameter = 3  # Diameter of the neodymium magnets in mm
magnet_thickness = 1  # Thickness of the neodymium magnets in mm
crenel_size = 10  # Length of each crenel/notch in mm
crenel_depth = 5  # How deep the crenels/notches extend in mm

create_crenelated_box_with_magnets(box_length, box_width, box_height, lid_height, wall_thickness, magnet_diameter,
                                   magnet_thickness, crenel_size, crenel_depth)
