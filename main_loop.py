import time

from Detector import Detector
from camera import getImage


def start(tag_finder: Detector) -> None:
    """Starts the main loop, putting value to smart dashboard"""
    while True:
        tag_finder.get_world_pos_from_image(getImage()).to_smart_dashboard()


def debug(tag_finder: Detector) -> None:
    """Starts the main loop, and prints values for FPS """
    frames = 0

    while True:
        img = getImage()
        #location = info[0]
        #print(location)
        #location1 = tag_finder.get_world_pos_from_image_single_tag_strats(img)
        location2 = tag_finder.get_world_pos_from_image(img)
        print(location2)
        #print(location1)
        #location.to_smart_dashboard()
        """frames += 1
        if frames >= 100:
            now = time.perf_counter()
            print(f"avg fps: {frames / (now - start)}")
            start = now
            frames = 0
        """
        print("---+===-{ New Frame }-===+---")