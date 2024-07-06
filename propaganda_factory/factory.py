import os
from dotenv import load_dotenv
import argparse
import json
import cv2


def emotion_and_situation_to_picture(emotion, situation, materials):
    for item in materials["pic_path"]:
        if item["emotion"] == emotion and item["situation"] == situation:
            return cv2.imread(item["text"]) 

def emotion_and_situation_to_top_text(emotion, situation, materials):
    for item in materials["top_text"]:
        if item["emotion"] == emotion and item["situation"] == situation: 
            return item["text"]

def emotion_and_situation_to_bottom_text(emotion, situation, materials):
    for item in materials["bottom_text"]:
        if item["emotion"] == emotion and item["situation"] == situation: 
            return item["text"]


def emotion_to_situation(emotion, emotion_to_situation_mapping):
    return emotion_to_situation_mapping[emotion]

def situation_to_emotion(situation, situation_to_emotion_mapping):
    return situation_to_emotion_mapping[situation]


def main(args):
    load_dotenv()
    CURRENT_PATH = os.getenv('CURRENT_PATH')
    with open(CURRENT_PATH + "/factory/context/on_chain_security/materials.json", "r") as f:
        materials = json.load(f)
        print(materials)

    pic = emotion_and_situation_to_picture(args.emotion, args.situation, materials)
    top_text = emotion_and_situation_to_top_text(args.emotion, args.situation, materials)
    bottom_text = emotion_and_situation_to_bottom_text(args.emotion, args.situation, materials)

    # TODO :top text -> add it to background
    # TODO: bottom text -> add it to background
    # TODO: background generator -> grab color from the pic that's on the background and create pic of a particular size
    # -> approach 1. find the most common color combinations and cross ref with positioning (take top 1 or 2 and cross ref with corners)
    # -> 

    pass
# TODO: factory has 3 Components - 
# 1) the picture part (queried via emotions and situation)
# 2) the fregrt gtr trg rtg r
# 3) the fref rgrt 



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-e", "--emotion", type=str)
    parser.add_argument("-s", "--situation", type=str)

    main(parser.parse_args())


# DESIGN