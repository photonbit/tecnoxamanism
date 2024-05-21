import FreeCAD as App
import Part



def add_crenels_to_edge(shape, crenel_width, crenel_height, crenel_depth, total_length, start_with_crenel=True):
    """
    Adds crenels to an edge of the given shape, with an option to start with a crenel or a gap.

    Parameters:
    - shape: The shape to modify
    - crenel_width: The width of each crenel
    - crenel_height: The height of each crenel
    - crenel_depth: The depth of each crenel into the shape
    - total_length: The total length of the edge to be modified with crenels
    - start_with_crenel: Boolean indicating whether to start with a crenel (True) or a gap (False)

    Returns:
    - Modified shape with crenels along one edge
    """
    num_crenels = int(total_length / (2 * crenel_width))
    for i in range(num_crenels):
        # Calculate position for each crenel
        pos_x = i * 2 * crenel_width
        # Adjust behavior based on whether to start with a crenel or gap
        if (i % 2 == 0 and start_with_crenel) or (i % 2 != 0 and not start_with_crenel):
            # Create crenel shape and add it to the main shape
            crenel_shape = Part.makeBox(crenel_width, crenel_depth, crenel_height, App.Vector(pos_x, 0, 0))
            shape = shape.fuse(crenel_shape)
        else:
            # Create gap shape and subtract it from the main shape
            gap_shape = Part.makeBox(crenel_width, crenel_depth, crenel_height, App.Vector(pos_x, 0, 0))
            shape = shape.cut(gap_shape)
    return shape


def create_box_shape(width, height, depth, thickness):
    """
    Create the shape of the box without positioning it in the document.

    Parameters:
    - width, height, depth: Internal dimensions of the box
    - thickness: Thickness of the material

    Returns:
    - The shape of the box (Part::Box)
    """
    # Calculate external dimensions
    ext_width = width + 2 * thickness
    ext_depth = depth + 2 * thickness
    ext_height = height + thickness  # No thickness on top for the lid

    # Create box shape
    box_shape = Part.makeBox(ext_width, ext_depth, ext_height)
    inner_shape = Part.makeBox(width, depth, height, App.Vector(thickness, thickness, thickness))
    box_with_hole = box_shape.cut(inner_shape)

    creneled_box = add_crenels_to_edge(box_with_hole, 10, 10, 5, width, start_with_crenel=True)

    return creneled_box

def create_lid_shape(width, depth, thickness):
    """
    Create the shape of the lid without positioning it in the document.

    Parameters:
    - width, depth: Internal dimensions of the box (the lid will match the box's external dimensions)
    - thickness: Thickness of the lid material

    Returns:
    - The shape of the lid (Part::Box)
    """
    # Adjust dimensions to match the box's external dimensions
    lid_width = width + 2 * thickness
    lid_depth = depth + 2 * thickness

    # Create lid shape
    lid_shape = Part.makeBox(lid_width, lid_depth, thickness)

    return lid_shape

def add_shape_to_document(shape, name):
    """
    Adds a given shape to the FreeCAD document with the specified name.

    Parameters:
    - shape: The shape to add (created by Part.makeBox or similar)
    - name: Name of the object in the document

    Returns:
    - The FreeCAD document object added
    """
    doc = App.activeDocument()
    obj = doc.addObject("Part::Feature", name)
    obj.Shape = shape
    return obj

def set_placement(obj, position, rotation=(0, 0, 0, 1)):
    """
    Set the placement of an object in the document.

    Parameters:
    - obj: The object to place
    - position: A tuple (x, y, z) for the object's position
    - rotation: A tuple (x, y, z, w) for the object's rotation (quaternion), default is no rotation
    """
    obj.Placement = App.Placement(App.Vector(*position), App.Rotation(*rotation))


def create_lid_with_walls_shape(width, depth, thickness, wall_height):
    """
    Create the shape of the lid with short walls, without positioning it in the document.

    Parameters:
    - width, depth: Internal dimensions of the box
    - thickness: Thickness of the material for the lid and its walls
    - wall_height: Height of the walls of the lid

    Returns:
    - The shape of the lid with walls
    """
    # Adjust dimensions to match the box's external dimensions plus walls
    lid_ext_width = width + 2 * thickness
    lid_ext_depth = depth + 2 * thickness
    lid_ext_height = wall_height  # Total height of the lid including its short walls

    # Create outer shape of the lid
    lid_shape = Part.makeBox(lid_ext_width, lid_ext_depth, lid_ext_height)

    # Create inner cutout to form the walls
    if wall_height > thickness:  # Ensure there's enough height for inner cutout
        inner_cutout = Part.makeBox(width, depth, wall_height - thickness,
                                    App.Vector(thickness, thickness, thickness))
        lid_with_walls_shape = lid_shape.cut(inner_cutout)
    else:
        lid_with_walls_shape = lid_shape

    creneled_lid = add_crenels_to_edge(lid_with_walls_shape, 10, 10, 5, width, start_with_crenel=False)

    return creneled_lid


# Parameters for the box
width, height, depth, thickness = 100, 50, 100, 5

# Create document if not already present
if App.activeDocument() is None:
    doc = App.newDocument("BoxDesign")
else:
    doc = App.activeDocument()

# Create and add box shape to the document
box_shape = create_box_shape(width, height, depth, thickness)
box_obj = add_shape_to_document(box_shape, "WoodenBox")
set_placement(box_obj, (0, 0, 0))

# Create and add lid shape to the document
# Adjusted function call for the lid with short walls
wall_height = 10  # Example wall height for the lid
lid_shape_with_walls = create_lid_with_walls_shape(width, depth, thickness, wall_height)

# Add the modified lid shape to the document
lid_with_walls_obj = add_shape_to_document(lid_shape_with_walls, "LidWithWalls")
set_placement(lid_with_walls_obj, (0, depth +thickness+thickness, height + thickness + wall_height), rotation=(1, 0, 0, 0))

# Recompute the document to apply changes
doc.recompute()

