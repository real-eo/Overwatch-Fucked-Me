from keras.models import load_model
from PIL import Image, ImageGrab, ImageOps
import numpy as np


def _crop_image_(img, d):
    w, h = img.size

    for i in range(1, h-h%d+1, d):
        box = (0, i, 90, i+d)
        img.crop(box).save(f"sources/ai/e{int((i-1)/62)}.png")


def capture_image():
    region = (310, 610, 1160, 920)
    img = ImageGrab.grab(region)    

    print("[$] Image captured")

    _crop_image_(img, 62)

    img.save("sources/ai/enemyLeaderboard.png")
    
    return 0
 
def recognize():
    np.set_printoptions(suppress=True)

    model = load_model('model/keras_model.h5', compile=False)
    class_names = open('model/labels.txt', 'r').readlines()

    data = np.ndarray(shape=(1, 224, 224, 3), dtype=np.float32)
    size = (224, 224)

    classesReturned = []

    for i in range(5):
        image = Image.open(f'sources/ai/e{i}.png').convert('RGB')

        image = ImageOps.fit(image, size, Image.Resampling.LANCZOS)

        image_array = np.asarray(image)

        normalized_image_array = (image_array.astype(np.float32) / 127.0) - 1

        data[0] = normalized_image_array

        prediction = model.predict(data)
        index = np.argmax(prediction)
        class_name = class_names[index]
        confidence_score = prediction[0][index]

        print('[$] Class:', class_name, end='')
        print('[$] Confidence score:', confidence_score)

        classesReturned.append([class_name, confidence_score])
    
    return classesReturned


if __name__ == "__main__":
    print("[!] This file is not ment to be run!\n\n")
    input("Press \"Enter\" to exit . . .")
