import numpy
import cv2
import praw
import os
import requests

import credentials


# Create directory if it doesn't exist to save images
def create_folder(image_path):
    _check_folder = os.path.isdir(image_path)
    # If folder doesn't exist, then create it.
    if not _check_folder:
        os.makedirs(image_path)


# Path to save images
dir_path = os.path.dirname(os.path.realpath(__file__))
image_path = os.path.join(dir_path, "images/")
ignore_path = os.path.join(dir_path, "ignore_images/")
create_folder(image_path)

# file_with_path = ""

reddit = praw.Reddit(
    client_id=credentials.CLIENT_ID,
    client_secret=credentials.SECRET_KEY,
    user_agent="Wallpaper-Bot"
)

subreddit = reddit.subreddit("Wimmelbilder")
POST_SEARCH_AMOUNT = 1


def scrap_for_image():
    f_final = open("sub_list.csv", "r")
    img_notfound = cv2.imread(f'{ignore_path}imageNF.png')
    for line in f_final:
        sub = line.strip()
        subreddit = reddit.subreddit(sub)

        print(f"Starting {sub}!")
        count = 0

    for submission in subreddit.hot(limit=POST_SEARCH_AMOUNT):
        _sub_url = submission.url.lower()
        if "jpg" in _sub_url or "png" in _sub_url:
            try:
                resp = requests.get(submission.url.lower(), stream=True).raw
                image = numpy.asarray(bytearray(resp.read()), dtype="uint8")
                image = cv2.imdecode(image, cv2.IMREAD_COLOR)

                # Could do transforms on images like resize!
                compare_image = cv2.resize(image, (224, 224))

                # Get all images to ignore
                for (dirpath, dirnames, filenames) in os.walk(ignore_path):
                    ignore_paths = [os.path.join(dirpath, file) for file in filenames]
                ignore_flag = False

                for ignore in ignore_paths:
                    ignore = cv2.imread(ignore)
                    difference = cv2.subtract(ignore, compare_image)
                    b, g, r = cv2.split(difference)
                    total_difference = cv2.countNonZero(b) + cv2.countNonZero(g) + cv2.countNonZero(r)
                    if total_difference == 0:
                        ignore_flag = True

                # scraped image
                if not ignore_flag:
                    cv2.imwrite(f"{image_path}{sub}-{submission.id}.png", image)
                    count += 1
                    file_with_path = f"{image_path}{sub}-{submission.id}.png"
                    return file_with_path


            except Exception as e:
                print(f"Image failed. {submission.url.lower()}")
                print(e)
