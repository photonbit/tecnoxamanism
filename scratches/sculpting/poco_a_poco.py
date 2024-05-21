import FreeCAD as App
import Part

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

    return box_with_hole

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
lid_shape = create_lid_shape(width, depth, thickness)
lid_obj = add_shape_to_document(lid_shape, "Lid")
set_placement(lid_obj, (0, 0, height + thickness))

# Recompute the document to apply changes
doc.recompute()
