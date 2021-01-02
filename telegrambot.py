import telebot
import os
from requests import get
import json

head = {'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:82.0) Gecko/20100101 Firefox/82.0',
'Accept': '*/*'}

bot = telebot.TeleBot(os.environ.get('bottok'))
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, 'Добро пожаловать.\n'
                                      'Это бот тырелка из Инстаграма 🤖\n'
                                      'Можешь присылать ссылки на картинки, видосы и профиль.\n'
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
        js = json.loads(html)
        try:
            url = js['entry_data']['ProfilePage'][0]['graphql']['user']['profile_pic_url_hd']
        except Exception:
            url = 'Непредвиденная ошибка ('
        bot.send_message(message.chat.id, url)
    else:
        bot.send_message(message.chat.id, 'Щас подумаю...')
        t = get('https://source.unsplash.com/300x500/?'+ message.text, headers=head).content
        #t = get('https://picsum.photos/300/500', headers=head).content
        bot.send_photo(message.chat.id, t, caption='Вот чё нашел.')


bot.polling(none_stop=True)
