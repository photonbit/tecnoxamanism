import FreeCAD as App
import Part


def create_shape_with_crenels(width, height, depth, thickness, crenel_params, start_with_crenel):
    """
    Creates a box or lid shape with crenels for interlocking.

    Parameters:
    - width, height, depth: Internal dimensions of the box or lid
    - thickness: Thickness of the material
    - crenel_params: Dictionary with crenel dimensions (width, height, depth)
    - start_with_crenel: Boolean indicating if the crenel pattern should start with a crenel

    Returns:
    - A Part object with the shape of the box or lid, including crenels
    """
    # Create base shape
    shape = Part.makeBox(width + 2 * thickness, depth + 2 * thickness, height + thickness)

    # Add crenels to the top edge
    shape = add_complementary_crenels(shape, width + 2 * thickness, crenel_params, start_with_crenel)

    return shape


def add_complementary_crenels(shape, edge_length, crenel_params, start_with_crenel):
    """
    Adds complementary crenels along one edge of the shape.

    Parameters:
    - shape: The shape to modify
    - edge_length: Length of the edge where crenels are added
    - crenel_params: Dictionary with crenel dimensions (width, height, depth)
    - start_with_crenel: Boolean indicating if the crenel pattern should start with a crenel

    Returns:
    - Modified shape with crenels
    """
    crenel_width = crenel_params['width']
    crenel_height = crenel_params['height']
    crenel_depth = crenel_params['depth']
    num_pairs = int(edge_length / (2 * crenel_width))
    modified_shape = shape

    for i in range(num_pairs):
        pos_x = i * 2 * crenel_width
        if not start_with_crenel:
            pos_x += crenel_width

        crenel_shape = Part.makeBox(crenel_width, crenel_depth, crenel_height,
                                    App.Vector(pos_x, 0, shape.Height - crenel_height))
        if (i % 2 == 0 and start_with_crenel) or (i % 2 != 0 and not start_with_crenel):
            modified_shape = modified_shape.fuse(crenel_shape)
        else:
            modified_shape = modified_shape.cut(crenel_shape)

    return modified_shape


def add_shape_to_document(shape, name):
    """
    Adds a given shape to the FreeCAD document with the specified name.

    Parameters:
    - shape: The shape to add
    - name: Name of the object in the document
    """
    doc = App.activeDocument()
    obj = doc.addObject("Part::Feature", name)
    obj.Shape = shape


def set_placement(obj, position, rotation=(0, 0, 0, 1)):
    """
    Set the placement of an object in the document.

    Parameters:
    - obj: The object to place
    - position: A tuple (x, y, z) for the object's position
    - rotation: A quaternion (x, y, z, w) for the object's rotation
    """
    obj.Placement = App.Placement(App.Vector(*position), App.Rotation(*rotation))


# Box and lid parameters
width, height, depth, thickness = 100, 50, 100, 5
crenel_params = {'width': 10, 'height': 10, 'depth': 5}

# Create document if not already present
if App.activeDocument() is None:
    doc = App.newDocument("BoxWithCrenels")
else:
    doc = App.activeDocument()

# Create box with crenels
box_shape = create_shape_with_crenels(width, height, depth, thickness, crenel_params, start_with_crenel=True)
box_obj = add_shape_to_document(box_shape, "Box")
set_placement(box_obj, (0, 0, 0))

# Create lid with complementary crenels
lid_shape = create_shape_with_crenels(width, 5, depth, thickness, crenel_params,
                                      start_with_crenel=False)  # Assuming a shorter height for the lid
lid_obj = add_shape_to_document(lid_shape, "Lid")
set_placement(lid_obj, (0, 0, height + thickness))

doc.recompute()
