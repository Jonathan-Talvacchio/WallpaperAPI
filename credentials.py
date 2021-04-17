
import numpy
import cv2
import praw
import os
import requests

CLIENT_ID = "2nLO-3HsCYSvnA"
SECRET_KEY = "nvL4z-THuNsikRjDPi6N4hKYxGtgMg"

POST_SEARCH_AMOUNT = 5


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

reddit = praw.Reddit(
    client_id=CLIENT_ID,
    client_secret=SECRET_KEY,
    user_agent="Wallpaper-Bot"
)

subreddit = reddit.subreddit("Wimmelbilder")

f_final = open("sub_list.csv", "r")
img_notfound = cv2.imread('imageNF.png')
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

            if not ignore_flag:
                cv2.imwrite(f"{image_path}{sub}-{submission.id}.png", image)
                count += 1

        except Exception as e:
            print(f"Image failed. {submission.url.lower()}")
            print(e)

os.system("gsettings set org.gnome.desktop.background picture-uri file:////home/jonathan/Projects/Python/WallpaperAPI/images/Wimmelbilder-ml9ou2.png")
