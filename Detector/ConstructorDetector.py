import cv2
import numpy as np
from numpy.typing import ArrayLike
from Calibration import Calibration
from Tags import FoundTag, field, MegaTag
from math_stuff.math_stuff import Transform3d
from dashboard import SmartDashboard
from math_stuff.rotation3d import Rotation3d
from math_stuff.translation3d import Translation3d
from multiprocessing import Pool
from Detector.Detector import Detector
from Detector.IndividualDetector import IndividualDetector
import time
from Detector.Utils import Point, Line, LinePair

def process_tag(arg: list[LinePair, LinePair, Calibration]) -> list[FoundTag]:
    line1 = arg[0]
    line2 = arg[1]
    calibration = arg[2]
    height = line1.real_line.top.y - line1.real_line.bot.y
    width = line2.real_line.bot.x - line1.real_line.bot.x
    if(width == 0): return
    if(line1.parent.z != line2.parent.z): return
    success, rotation_vectors, translation_vectors, _ = cv2.solvePnPGeneric(
        np.array([
            [-width/2, height/2, 0.0],
            [width/2, height/2, 0.0],
            [width/2, -height/2, 0.0],
            [-width/2, -height/2, 0.0],
        ], dtype=np.float64),
        np.array([
            line1.image_line.top.arr2d,
            line2.image_line.top.arr2d,
            line2.image_line.bot.arr2d,
            line1.image_line.bot.arr2d
        ],
            dtype=np.float64),
        calibration.mtx,
        calibration.dist,
        flags=cv2.SOLVEPNP_IPPE)
    if not success: return
    tag_x = (line1.real_line.top.x + line2.real_line.top.x)/2
    tag_y = (line1.real_line.top.y + line1.real_line.bot.y)/2
    known_tag = MegaTag(tag_x, tag_y, line1.parent.z, 180)

    to_append = []
    for (r, t) in zip(rotation_vectors,translation_vectors):
        rotation_matrix = cv2.Rodrigues(r)[0]
        found_tag = FoundTag(known_tag, t, rotation_matrix,99)
        to_append.append(found_tag)
    return to_append

class ConstructorDetector(Detector):
    """Used to find Apriltags in an image and return a position on the field
    MegaTagDetector: Uses corners of tags to create new tags, and find positions of those fake tags"""
    def create_tags(self, tags) -> list[list[FoundTag]]:
        """
        Finds edges of the tag, finds out their real-world position.
        Then it reconstructs the tags, and uses SolvePNP to find the real-world distance from the camera to the tags.
        Because there is ambiguit across the x axis on SolvePNP's position, this function returns a list pairs of tags, one of them correct, and another one on the wrong side of the tag
        To throw out the incorrect tags, use a function such as "trimmed_tags"
        :param tags: List of Detections to find the corners of
        :return: List of tag pairs
        """
        if len(tags) == 0: return []
        if len(tags) == 1:
            return IndividualDetector.create_tags(self, tags)

        lines = []

        for item in tags:
            image_points = item.corners

            tag = field[item.tag_id]

            lines.append(LinePair.create_from_info("LEFT", self.object_points, image_points, tag))
            lines.append(LinePair.create_from_info("RIGHT", self.object_points, image_points, tag))


        lines = sorted(lines, key=lambda l : l.real_line.top.x)
        args = []
        for i in range(len(lines)-1):
            for k in range(len(lines) - (i+1)):
                j = i + k + 1
                args.append([lines[i], lines[j], self.calibration])
        pool = Pool(4)
        detected = pool.map(process_tag, args)

        if detected is None: return []
        return detected