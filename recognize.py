from src.resources.manager import resource_path, writable_path
from PIL import Image, ImageGrab, ImageOps
from src.constants import TOTAL_SLOTS_ALL
from keras.models import load_model
from keras import Model
import numpy as np
import random
import os



# * Private functions
def _crop_image(img: Image.Image, dx: int, dy: int, randomName: bool = False):
    _, h = img.size                                                                     # Ignore the width since it's currently unused during cropping 

    for i in range(1, int(h-h%dy+1), int(dy)):
        box = (
            0, 
            i + (2 * int((i-1)/dy)),                                                    # ? We add 2 pixels for every new image we crop since there is a 2 pixel border between the images on the leaderboard
            dx, 
            i+dy + (2 * int((i-1)/dy))
        )
        img.crop(box).save(
            writable_path("out", "state", 
                f"e{int((i-1)/dy)}.png"                                                 # Default name
                if not randomName                                                       # Check to see if we should provide a random name 
                else str(random.random())[2:] + ".png"                                  # Generate a random name
            )
        )


def _determine_leaderboard_x1() -> int:
    # * Constants
    # List of X coordinates where the white bar starts at the different upgrade levels  
    WHITE_BAR_STARTS_AT_X = (
        320,                                                                            # X coordinate of the left edge at 0 upgrades
        300,                                                                            # X coordinate of the left edge at 1 upgrade
        270                                                                             # X coordinate of the left edge at 2 upgrades
    )
    
    # Region of the white bar at the top of your own team's leaderboard
    WHITE_BAR_REGION = (WHITE_BAR_STARTS_AT_X[2], 160, 665, 190)                        # ? We do max upgrades for x1 to be able to check all upgrade levels
    WHITE_BAR_PIXEL_COLOR = (215, 219, 224)                                             # The color of the white bar pixels


    # * Process
    # Grab the image of the white bar region
    whiteBarImage = ImageGrab.grab(WHITE_BAR_REGION)
    currentStartX = WHITE_BAR_STARTS_AT_X[0]                                            # ? Start by assuming that there are 0 upgrades

    # Check which upgrade level is active by checking the color of the pixel at the different X coordinates
    for i, x in enumerate(WHITE_BAR_STARTS_AT_X[1:]):                                   # ? Start checking from 1 upgrade since we already assume 0 upgrades at the start
        # Coordinates of the pixel we check
        checkX = x - (                                                                  # ? We start by using the current X coordinate we want to check
            WHITE_BAR_REGION[0]                                                         # ? Then we subtract the coordinate where the region starts since we are checking the pixel relative to the region
            - 5                                                                         # ? Finally, we subtract 5 pixels to not be on the exact edge of the white bar, since the increments are pretty big, and we don't want any potential anti-aliasing to mess with our color check
        ) 
        checkY = 15                                                                     # ? Just half the width of the white bar region (we check the middle of the white bar for consistency - same as the "- 5" for the X coordinate)

        # Get the color of the pixel at the coordinates
        color = whiteBarImage.getpixel((checkX, checkY))

        # Check if the color matches the white bar pixel color
        if not color == WHITE_BAR_PIXEL_COLOR:
            break                                                                       # ? If the color doesn't match, we break out of the loop since we found the current upgrade level
        
        # If the color matches, we update the current start X coordinate to the current X coordinate
        currentStartX = x

    # If we found an upgrade level, or finished checking all upgrade levels, we return the current start X coordinate
    print(f"[§] Leaderboard x1 currently at: {currentStartX}")
    return currentStartX



# * Public functions
def capture_image(persistPortraits: bool = False):
    """
    Captures the enemy leaderboard in game

    ---

    ### Process
    1. Determine, at most, where the x1 of the leaderboard is based on how many upgrades are active for the most progressed person
    2. (WIP) Determine how many players per team 
    3. Grab screenshot based on the number of upgrades and team size
    4. Split image into one image per enemy and save them
    5. Save full leaderboard

    """
    # * 1) Determine, where the x1 of the leeaderboard is based on how many upgrades are active for the most progressed person
    leaderboardX1 = _determine_leaderboard_x1()


    # * 2) Determine how many players per team
    # (WIP)


    # * 3) Grab screenshot based on the number of upgrades and team size
    # // region = (310, 610, 1160, 920)
    region = (leaderboardX1, 595, 1100, 925)
    enemyLeaderboardImage = ImageGrab.grab(region)    

    print("[§] Image captured")

    # Create output directory if it doesn't exist
    os.makedirs(writable_path("out", "state"), exist_ok=True)                           # ! NO STORED IMAGE READING CAN HAPPEN BEFORE THIS
    

    # * 4) Split image into one image per enemy and save them
    # Character image size is: 64x64
    # Role icon image size is: 27x64
    # Border size is: 2x2
    _crop_image(enemyLeaderboardImage, 93, 64, randomName=persistPortraits)


    # * 5) Save full leaderboard
    enemyLeaderboardImage.save(writable_path("out", "state", "enemyLeaderboard.png"))
    
    return 0
 
 
def recognize() -> list[tuple[str, float]]:
    np.set_printoptions(suppress=True)

    model: Model = load_model(resource_path("model", "keras_model.h5"), compile=False)
    classNames = open(resource_path("model", "labels.txt"), 'r').readlines()

    data = np.ndarray(shape=(1, 224, 224, 3), dtype=np.float32)
    size = (224, 224)

    classesReturned = []

    for i in range(TOTAL_SLOTS_ALL):
        image = Image.open(writable_path("out", "state", f"e{i}.png")).convert('RGB')
        image = ImageOps.fit(image, size, Image.Resampling.LANCZOS)

        imageArray = np.asarray(image)

        normalizedImageArray = (imageArray.astype(np.float32) / 127.0) - 1
        data[0] = normalizedImageArray

        prediction = model.predict(data, verbose=0)
        index = np.argmax(prediction)
        className = classNames[index]
        confidenceScore = prediction[0][index]

        print('[§] Class:', className, end='')
        print('[§] Confidence score:', confidenceScore)

        classesReturned.append([className.strip(), confidenceScore])
    
    return classesReturned


if __name__ == "__main__":
    print("[!] This file is not ment to be run!\n\n")
    input("Press \"Enter\" to exit . . .")
