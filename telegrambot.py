import telebot
import os
from requests import get
import json
import youtube_dl
from datetime import timedelta

print('start')
head = {'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:82.0) Gecko/20100101 Firefox/82.0',
        'Accept': '*/*'}

bot = telebot.TeleBot(os.environ.get('bottok'))
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, 'Добро пожаловать.\n'
                                      'Это бот тырелка из Инстаграма 🤖\n'
                                      'Можешь присылать ссылки на картинки, видосы и профиль.\n'
                                      'Так же есть закачка песен с ютуба\n'
                                      'А если напишешь любое английское слово, то я найду картинку по нему )')


@bot.message_handler(content_types=['text'])
def incomingmess(message):
    if message.text.find('https://www.instagram.com/p/') > -1 or message.text.find('https://www.instagram.com/reel/') > -1:
        print('media')
        html = get(message.text, headers=head).text
        html = html[html.find('_sharedData = ') + 14:html.find(';</script>')]
        js = json.loads(html)
        if js['entry_data'].get('PostPage', None):
            typ = js['entry_data']['PostPage'][0]['graphql']['shortcode_media']['__typename']
            if typ == 'GraphImage':
                url = js['entry_data']['PostPage'][0]['graphql']['shortcode_media']['display_url']
            elif typ == 'GraphVideo':
                url = js['entry_data']['PostPage'][0]['graphql']['shortcode_media']['video_url']
            elif typ == 'GraphSidecar':
                countimg = js['entry_data']['PostPage'][0]['graphql']['shortcode_media']['edge_sidecar_to_children']['edges']
                url = ''
                for js in countimg:
                    typ = js['node']['__typename']
                    if typ == 'GraphImage':
                        url = js['node']['display_url']
                    elif typ == 'GraphVideo':
                        url = js['node']['video_url']
                    bot.send_message(message.chat.id, url)
                exit()
        else:
            url = 'Меня не впустили\nЭто закрытый аккаунт ('
        bot.send_message(message.chat.id, url)
    elif message.text.find('https://instagram.com/') > -1:
        print('prof')
        html = get(message.text, headers=head).text
        html = html[html.find('_sharedData = ') + 14:html.find(';</script>')]
        print(len(html))
        #print(html)
        js = json.loads(html)
        try:
            url = js['entry_data']['ProfilePage'][0]['graphql']['user']['profile_pic_url_hd']
        except Exception:
            url = 'Непредвиденная ошибка ('
        bot.send_message(message.chat.id, url)
    elif message.text.find('www.youtube.com/watch?v=') > -1 or message.text.find('https://youtu.be/') > -1:
        bot.send_message(message.chat.id, 'Щас подумаю...')
        ydl = youtube_dl.YoutubeDL({'format': '140'})#{'outtmpl': '%(id)s%(ext)s'})
        with ydl:
            result = ydl.extract_info(message.text, download=True)
        vname = f"{result['title']}-{result['id']}.m4a"
        vid = open(vname, 'rb')
        bot.send_audio(message.chat.id, vid)
        vid.close()
        os.remove(vname)
            # for i in result['formats']:
            #     if i['format_id'] == '140':
            #         url = i['url']
            #         markup = telebot.types.InlineKeyboardMarkup()
            #         btn_my_site = telebot.types.InlineKeyboardButton(text='Скачать', url=url)
            #         markup.add(btn_my_site)
            #         bot.send_message(message.chat.id, f"{result['title']}\n"
            #                                           f"🕒 {str(timedelta(seconds=result['duration']))}"
            #                                           f"  👁 {result['view_count']}\n"
            #                                           f"{result['thumbnails'][-1]['url']}", reply_markup=markup)
    else:
        print(message.text)
        bot.send_message(message.chat.id, 'Щас подумаю...')
        t = get('https://source.unsplash.com/300x500/?' + message.text, headers=head).content
        #t = get('https://picsum.photos/300/500', headers=head).content
        bot.send_photo(message.chat.id, t, caption='Вот чё нашел.')


bot.polling(none_stop=True)
