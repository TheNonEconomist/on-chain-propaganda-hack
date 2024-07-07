import cv2
import numpy as np

def concatenate_images_paths(image_paths, horizontal=True):
    images = [cv2.imread(img_path) for img_path in image_paths]
    
    if horizontal:
        concatenated_image = np.hstack(images)
    else:
        concatenated_image = np.vstack(images)
    
    return concatenated_image

def concatenate_images_inline(images, horizontal=True):
    if horizontal:
        concatenated_image = np.hstack(images)
    else:
        concatenated_image = np.vstack(images)
    
    return concatenated_image


def add_text_alignment_check(
        image_path: list, image: np.array, inline: bool,
        text: str, 
        position: tuple, alignment: str,
        font, font_scale: int, font_color: tuple, font_thickness: int
        ):
    """
    add text as well as where it's aligned. By default it's left aligned from the position
    """
    if alignment == "right":
        (text_w, text_h), _ = cv2.getTextSize(text, font, font_scale, font_thickness)
        position = (position[0]-text_w, position[1]+text_h)
    elif alignment == "center":
        (text_w, text_h), _ = cv2.getTextSize(text, font, font_scale, font_thickness)
        position = (position[0]-text_w//2, position[1]+text_h//2)

    if inline is True:
        return __add_text_to_image_inline(image, text, position, font, font_scale, font_color, font_thickness)
    else:
        return __add_text_to_image_path(image_path, text, position, font, font_scale, font_color, font_thickness)


def __font_size_and_thickness_scaling(text, h, w, side_pad):
    # For referencem at font_scale= 0.5, each letter takes about 10 pixels and seems to scale linearly?

    # TODO: font size and thickness scaling based off picture size
    w_usage = w
    if type(side_pad) == int:
        w_usage -= 2*side_pad
    elif type(side_pad) == float:
        w_usage = w_usage - int(2*w*side_pad)

    pixel_width_usage_per_letter = w_usage//len(text)
    font_scale = pixel_width_usage_per_letter/20
    
    return font_scale

def __add_text_to_image_inline(image, text, position, font, font_scale, font_color, font_thickness):
    # Add text to the image
    # print(text, position, font, font_scale, font_color, font_thickness)
    cv2.putText(image, text, position, font, font_scale, font_color, font_thickness)

    return image

def __add_text_to_image_path(image_path, text, position, font, font_scale, font_color, font_thickness):
    # Read the image
    image = cv2.imread(image_path)

    # Add text to the image
    # print(text, position, font, font_scale, font_color, font_thickness)
    cv2.putText(image, text, position, font, font_scale, font_color, font_thickness)

    return image

def grab_background_color(image, approach="corners_and_edges"):
    h, w, _ = image.shape
    majority_vote = dict()
    if approach == "corners_and_edges":
        for i in range(h):
            try:
                majority_vote[tuple(image[i, 0, :])] += 1
            except KeyError:
                majority_vote[tuple(image[i, 0, :])] = 1

            try:
                majority_vote[tuple(image[i, -1, :])] += 1
            except KeyError:
                majority_vote[tuple(image[i, -1, :])] = 1
                 
        for j in range(1, w-1):
            try:
                majority_vote[tuple(image[0, j, :])] += 1
            except KeyError:
                majority_vote[tuple(image[0, j, :])] = 1

            try:
                majority_vote[tuple(image[-1, j, :])] += 1
            except KeyError:
                majority_vote[tuple(image[-1, j, :])] = 1
    
    max_count, max_combi = 0, None
    for color_combination, count in majority_vote.items():
        if count > max_count: 
            max_count= count
            max_combi = color_combination
    return max_combi


def create_pad(color, height, width, depth=3):
    return np.ones((height, width, depth))*color

def create_pad_and_text(
        color, height, width, depth, 
        text, text_position, alignment,
        font, font_scale, font_color, font_thickness):
    pad = create_pad(color, height, width, depth)
    return add_text_alignment_check(
        image_path=None, image=pad, inline=True,
        text=text, 
        position=text_position, alignment=alignment,
        font=font, font_scale=font_scale, font_color=font_color, font_thickness=font_thickness
        )

def __opposite_RGB(color):
    r, g, b = color
    return int(255 - r), int(255 - g), int(255 - b)


def create_pad_and_text_wif_font_scaling(
        color, height, width, depth, 
        text, text_position, alignment, font
    ):
    font_scale = __font_size_and_thickness_scaling(text, height, width, side_pad=0.1)
    font_color = __opposite_RGB(color)
    return create_pad_and_text(
        color, height, width, depth, 
        text, text_position, alignment,
        font=font, font_scale=font_scale, font_color=font_color, font_thickness=1
    )
    

### Replacing background
def separate_mask_from_image(image_path, pipe):
    """
    image_path: 
    pipe: pipeline for hugging face interface - should input image background separation model
    """
    pillow_mask = pipe(image_path, return_mask = True) # outputs a pillow mask
    pillow_image = pipe(image_path) # applies mask on input and returns a pillow image
    return np.asarray(pillow_mask.convert("RGB")), np.asarray(pillow_image.convert("RGB"))


def change_background_color(mask, image, new_background_color):
    # Convert all non-background space in Mask to W
    
    mask2 = np.asarray(mask)/255
    mask2 = (np.round(mask2)*255).astype(np.uint8)
    original_background_color = grab_background_color(mask2)
    new_background = ((mask2 == original_background_color)*new_background_color).astype(np.uint8)

    result = cv2.add(new_background, image)
    
    return result