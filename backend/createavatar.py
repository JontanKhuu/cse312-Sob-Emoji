# Using the Pillow library
# > https://pillow.readthedocs.io/en/stable/handbook/tutorial.html
##########
import PIL
import PIL.Image

# Important constants for generating sprites
AVATAR_RESIZE    = (56,56)          # Scale for the avatar in order to fit within the base sprite.
SPRITE_DIMENSION = (128,128)        # Dimensions of the base sprite.
AVATAR_PASTE_LOC = (36,30)          # X/Y coordinates for the top-left pixel of the resized avatar.

# create_avatar()
####################################
# Creates an avatar sprite for user using the given file.
# username - The name to write in the filename
# filename - The file containing the user's original avatar
####################################
def create_avatar(username, filename):
    base_sprite = PIL.Image.open("../frontend/public/sprites/player_base.png")

    # Resize the Avatar to the correct dimensions to merge into the sprite.
    myavatar = PIL.Image.open(filename)
    myavatar = myavatar.resize(AVATAR_RESIZE)

    # Create a new image, and combine both sprites into it.
    new = PIL.Image.new("RGBA",SPRITE_DIMENSION)
    new.paste(base_sprite)                      # Paste the base sprite first.
    new.paste(myavatar, AVATAR_PASTE_LOC)       # Paste the avatar on top of the base, in the correct position.

    # Save the file.
    out_path = "../frontend/public/avatars/avsprite_" + username + ".png"
    new.save(out_path,"PNG")
    return


# DEBUGGING
if __name__ == '__main__':
    create_avatar("Liandra", "../frontend/public/avatars/lia_avatar.png")