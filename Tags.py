from dataclasses import dataclass
from math_stuff import Transform3d, Translation3d, Pose3d, Rotation3d
from pyquaternion import Quaternion
import numpy as np
from numpy.typing import ArrayLike
import math
from constants import _robotToCamera

@dataclass
class KnownTag:
    """Contains the position and rotation of the tag on the field"""
    @staticmethod
    def from_inches(x_inches: float, z_inches: float, y_inches: float, rotation_degrees: float):
        return KnownTag(x_inches * 0.0254, y_inches * 0.0254, z_inches * 0.0254,rotation_degrees)
    def __init__(self, x: float, y: float, z: float, rotation_degrees: float):
        self.x: float = x
        """X position of the tag relative to a corner of the field in meters"""
        self.y: float = y
        """Y position of the tag relative to a corner of the field in meters"""
        self.z: float = z
        """Z position of the tag relative to a corner of the field in meters"""
        self.rotation: float = math.radians(rotation_degrees)
        """Rotation of the tag relative to the center of the field in radians."""
        self.pose = Pose3d(
            Translation3d(x,y,z),
            #Rotation3d.zero()
            #Translation3d.zero(),
            Rotation3d(Quaternion(axis=[1.0, 0.0, 0.0], radians=self.rotation))
        )


class FoundTag:
    def __init__(self, parent_tag: KnownTag, translation: ArrayLike, rotation: ArrayLike):
        self.parent_tag: KnownTag = parent_tag
        """The ID of the apriltag"""
        translation: Translation3d = Translation3d.from_matrix(translation)
        """Translation of the camera from the apriltag"""
        rotation3d: Rotation3d = Rotation3d.from_matrix(rotation)
        """Rotation matrix of the apriltag from the matrix"""
        self.tag_transform: Transform3d = Transform3d(translation, rotation3d)

    def get_robot_location(self):
        object_to_camera = self.tag_transform.inverse()
        camera_to_robot = _robotToCamera.inverse()
        return self.parent_tag.pose.transform_by(object_to_camera).transform_by(camera_to_robot)

"""field = (
    None,                                   # 0
    KnownTag.from_inches(42.19, 610.77, 18.22, 180),    # 1
    KnownTag.from_inches(108.19, 610.77, 18.22, 180),   # 2
    KnownTag.from_inches(147.19, 610.77, 18.22, 180),   # 3
    KnownTag.from_inches(265.74, 636.96, 27.38, 180),   # 4
    KnownTag.from_inches(265.74,  14.25, 27.38, 0),     # 5
    KnownTag.from_inches(147.19,  40.45, 18.22, 0),     # 6
    KnownTag.from_inches(108.19,  40.45, 18.22, 0),     # 7
    KnownTag.from_inches(42.19,  40.45, 18.22, 0)       # 8
)"""
field = (
    None,
    KnownTag(-1.2318, 0, 12, 180),
    KnownTag(1.65, 0, 12, 180)
)

