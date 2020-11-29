import os
import vk_api
import random
import requests
import config as c
from PIL import Image
from PIL import ImageOps
from PIL import ImageFont
from PIL import ImageDraw
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType

vk = vk_api.VkApi(token=c.TOKEN)
vk._auth_token()
vk.get_api()
longpoll = VkBotLongPoll(vk, c.GROUP_ID)


while True:
    try:
        for event in longpoll.listen():
            if event.type == VkBotEventType.MESSAGE_NEW:

                split_text = event.object.text.split(' \n')

                if split_text[0] in c.DEMOTIVATOR and len(split_text) == 3:

                    if len(event.object['attachments']) >= 1:
                        if 'photo' in event.object['attachments'][0]['type']:

                            photos = event.object['attachments'][0]['photo']['sizes']
                            max_photo = photos[len(photos)-1]['url']

                            img = Image.new('RGB', (1280, 1024), color=('#000000'))
                            img_border = Image.new('RGB', (1060, 720), color=('#000000'))
                            border = ImageOps.expand(img_border, border=2, fill='#ffffff')

                            user_photo_raw = requests.get(f'{max_photo}', stream=True).raw
                            user_img = Image.open(user_photo_raw).convert("RGBA").resize((1050, 710))

                            img.paste(border, (111, 96))
                            img.paste(user_img, (118, 103))

                            drawer = ImageDraw.Draw(img)

                            font_1 = ImageFont.truetype(font='files/font/times-new-roman.ttf', size=60, encoding='UTF-8')
                            font_2 = ImageFont.truetype(font='files/font/times-new-roman.ttf', size=30, encoding='UTF-8')

                            size_1 = drawer.textsize(f'{split_text[1]}', font=font_1)
                            drawer.text(((1280 - size_1[0]) / 2, 850), f'{split_text[1]}', fill=(240, 230, 210), font=font_1)

                            size_2 = drawer.textsize(f'{split_text[2]}', font=font_2)
                            drawer.text(((1280 - size_2[0]) / 2, 950), f'{split_text[2]}', fill=(240, 230, 210), font=font_2)

                            name = f'{event.object.from_id}-{random.randint(1, 999999999)}'

                            img.save(f'files/{name}.png')

                            server = vk.method("photos.getMessagesUploadServer")
                            upload = requests.post(server['upload_url'], files={'photo': open(f'files/{name}.png', 'rb')}).json()
                            save = vk.method('photos.saveMessagesPhoto', {'photo': upload['photo'], 'server': upload['server'], 'hash': upload['hash']})[0]
                            photo = "photo{}_{}".format(save["owner_id"], save["id"])

                            vk.method("messages.send", {"peer_id": event.object.peer_id, "attachment": photo, "random_id": 0})

                            os.remove(f'files/{name}.png')

    except Exception as e:
        print(repr(e))
