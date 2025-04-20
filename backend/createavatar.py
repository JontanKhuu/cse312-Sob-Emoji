import PIL
import PIL.Image





def create_avatar(username, filename):
    myimage = PIL.Image.open("../frontend/public/sprites/player_base.png")

    # Avatar to resize 56x56
    myavatar = PIL.Image.open(filename)
    myavatar = myavatar.resize((56,56))

    #print(myimage.format, myimage.size, myimage.mode)

    new = PIL.Image.new("RGBA",(128,128))

    #region = (36,30,91,85)

    new.paste(myimage)
    new.paste(myavatar, (36,30))

    #new.show()

    out_path = "../frontend/public/avatars/avsprite_" + username + ".png"

    new.save(out_path,"PNG")
    return


# DEBUGGING
if __name__ == '__main__':
    create_avatar("Liandra", "../frontend/public/avatars/lia_avatar.png")