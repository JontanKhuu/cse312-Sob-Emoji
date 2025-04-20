import PIL
import PIL.Image





def create_avatar():
    myimage = PIL.Image.open("../frontend/public/sprites/player_base.png")

    # Avatar to resize 56x56
    myavatar = PIL.Image.open("../frontend/public/sprites/lia_avatar.png")
    myavatar = myavatar.resize((56,56))

    #print(myimage.format, myimage.size, myimage.mode)

    new = PIL.Image.new("RGBA",(128,128))

    #region = (36,30,91,85)

    new.paste(myimage)
    new.paste(myavatar, (36,30))

    #new.show()

    myoutput = ("hybridized.png","wb")
    new.save("hybridized.png","PNG")


    return
