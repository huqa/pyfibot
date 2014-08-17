# -*- coding: utf-8 -*-
'''
Created on 17.8.2013

@author: Hukka
'''

import time
from math import ceil
#from datetime import timedelta
#from datetime import datetime
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw

def generate_kivatietaa(nick,text):
    #print len(text)
    if not text:
        return False
    if len(text) < 10 or len(text) > 133:
        return False
    IMAGE_LOCATION = "images/kivat_med_template.png"
    OUTPUT_LOCATION = "~/public_html/kiva_tietaa/"
    #MDX = 120
    font_size = 14
    nick_size = 9
    
    rivit = ceil(len(text) / 36.0)
    #print rivit
    
    img = Image.open(IMAGE_LOCATION)
    #img = img.convert("RGBA")
    txt_img = Image.new("RGBA", (300, 255))
    font = ImageFont.truetype('fonts/arial.ttf', font_size)
    font2 = ImageFont.truetype('fonts/arial.ttf', nick_size)
    draw = ImageDraw.Draw(img)
    draw_txt = ImageDraw.Draw(txt_img)

    start_m = 0
    end_m = 0
    merkit = 36
    x_pos = 6
    y_pos = 6
    #text = "Aku-set‰! " + text
    for rivi in range(1,int(rivit)+1):
        end_m = merkit * rivi 
        teksti = text[start_m:end_m]
        start_m = end_m
        draw.text((x_pos,y_pos), teksti.strip(), (2,2,2), font=font)
        y_pos = y_pos + 18 

    #draw_txt.text((4,188), str(nick), (2,2,2), font=font2)
    draw_txt.text((192,245), str(nick), (2,2,2), font=font2)
    txt_img = txt_img.rotate(270)
    img.paste(txt_img, None, txt_img)
    #draw.text((x_pos,88), text, (2,2,2), font=font)
    stamp = int(time.time())
    filename = "kt_" + str(stamp) + ".png"
    img.save(OUTPUT_LOCATION + filename)
    #set scheduler
    return filename
    #return url


def destroy_image(image):
    import os 
    folder = '~/public_html/kiva_tietaa'
    file_path = os.path.join(folder, image)
    try:
        if os.path.isfile(file_path):
            os.unlink(file_path)
    except:
        pass
        
def handle_kivatietaa(bot, user, channel, args):
    if not args:
        return
    nick = getNick(user)
    file = generate_kivatietaa(nick,args)
    if file is False:
        return bot.say(channel, "MATHO FUCKIN ERROR")
    #aika = datetime.now()+timedelta(minutes=20)
    #bot.scheduler.add_date_job(destroy_image, aika, [file])
    return bot.say(channel, "http://server.tld/kiva_tietaa/%s" % file)

#if __name__ == "__main__":
#    generate_kivatietaa("mcherwanta","Nyt kyll‰ n‰in niin ison hirven ett‰ rupes oikeen hirvitt‰‰n! T‰m‰ on tarinani!")