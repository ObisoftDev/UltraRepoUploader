from telethon import TelegramClient, events, sync
from telethon.events import NewMessage

from utils import createID,get_file_size,sizeof_fmt
from threads import ThreadAsync
from worker import async_worker

import asyncio
import base64
import zipfile
import os
import requests
import re
import config
import repouploader
import zipfile
import time
import animate

from repouploader import RepoUploader,RepoUploaderResult
from pydownloader.downloader import Downloader
import shorturl
import xdlink

async def get_root(username):
    if os.path.isdir(config.ROOT_PATH+username)==False:
        os.mkdir(config.ROOT_PATH+username)
    return os.listdir(config.ROOT_PATH+username)

async def send_root(bot,ev,username):
    listdir = await get_root(username)
    reply = f'📄 {username}/ ({len(listdir)} archivos) 📄\n\n'
    i=-1
    for item in listdir:
        i+=1
        fname = item
        fsize = get_file_size(config.ROOT_PATH + username + '/' + item)
        prettyfsize = sizeof_fmt(fsize)
        reply += str(i) + ' - ' + fname + ' [' + prettyfsize + ']\n'
    await bot.send_message(ev.chat.id,reply)

def text_progres(index, max):
            try:
                if max < 1:
                    max += 1
                porcent = index / max
                porcent *= 100
                porcent = round(porcent)
                make_text = ''
                index_make = 1
                make_text += '\n'
                while (index_make < 21):
                    if porcent >= index_make * 5:
                        make_text += '▰'
                    else:
                        make_text += '▱'
                    index_make += 1
                make_text += ''
                return make_text
            except Exception as ex:
                return ''

def porcent(index, max):
    porcent = index / max
    porcent *= 100
    porcent = round(porcent)
    return porcent

async def download_progress(dl, filename, currentBits, totalBits, speed, totaltime, args):
    try:
        bot = args[0]
        ev = args[1]
        message = args[2]

        if True:
            msg = '⬇️ Descargando archivo....\n'
            msg += '📁 Archivo: ' + filename + ''
            msg += '\n' + text_progres(currentBits, totalBits) + ' ' + str(porcent(currentBits, totalBits)) + '%\n' + '\n'
            msg += '☑ Total: ' + sizeof_fmt(totalBits) + '\n'
            msg += '↩️ Descargado: ' + sizeof_fmt(currentBits) + '\n'
            msg += '🚀 Velocidad: ' + sizeof_fmt(speed) + '/s\n'
            msg += '⏱ Tiempo de Descarga: ' + str(time.strftime('%H:%M:%S', time.gmtime(totaltime))) + 's\n\n'
            await bot.edit_message(ev.chat,message,text=msg)

    except Exception as ex:
        print(str(ex))

@async_worker
async def edit_in_loop(bot,ev,message,text):
    await bot.edit_message(message=message,text=msg)

def upload_progress(filename, currentBits, totalBits, speed, totaltime, args):
    try:
        bot = args[0]
        ev = args[1]
        message = args[2]
        loop = args[3]

        if True:
            msg = '⬆️ Subiendo archivo....\n'
            msg += '📁 Archivo: ' + filename + ''
            msg += '\n' + text_progres(currentBits, totalBits) + ' ' + str(porcent(currentBits, totalBits)) + '%\n' + '\n'
            msg += '☑ Total: ' + sizeof_fmt(totalBits) + '\n'
            msg += '⤴️ Subido: ' + sizeof_fmt(currentBits) + '\n'
            msg += '🚀 Velocidad: ' + sizeof_fmt(speed) + '/s\n'
            msg += '⏱ Tiempo de Descarga: ' + str(time.strftime('%H:%M:%S', time.gmtime(totaltime))) + 's\n\n'
            #loop.create_task(edit_in_loop(bot,ev,message,msg))

    except Exception as ex:
        print(str(ex))

async def onmessage(bot:TelegramClient,ev: NewMessage.Event,loop):
    username = ev.message.chat.username
    text = ev.message.text

    if username not in config.ACCES_USERS:
        await bot.send_message(ev.chat.id,'🛑No Tiene Acceso🛑')
        return

    if not os.path.isdir(config.ROOT_PATH + username):
        os.mkdir(config.ROOT_PATH + username)

    if '/start' in text:
        reply = '👋FreeUltraUploader👋\nEs un bot para el manejo de archivos en telegam (descargas/subidas)\n\n'
        reply += '<a href="https://github.com/ObisoftDev">Obisoft Dev Github</a>\n'
        reply += '<a href="https://t.me/obisoftt">Obisoft Dev Telegram</a>'
        message = await bot.send_message(ev.chat.id,reply,parse_mode='html')
        pass

    if 'http' in text:
        message = await bot.send_message(ev.chat.id,'⏳Procesando Enlace...🔗')
        dl = Downloader(config.ROOT_PATH + username + '/')
        file = await dl.download_url(text,progressfunc=download_progress,args=(bot,ev,message))
        if file:
            if file!='':
                await bot.delete_messages(ev.chat,message)
                await send_root(bot,ev,username)
            else:
                await bot.edit_message(ev.chat,message,text='💢Error De Enlace🔗')
        else:
             await bot.edit_message(ev.chat,message,text='💢Error De Enlace🔗')
        return

    if '/ls' in text:
        await send_root(bot,ev,username)
        return

    if '/rm' in text:
        message = await bot.send_message(ev.chat.id,'🗑Empezando...')
        text = str(text).replace('/rm ','')
        index = 0
        range = 1
        try:
            cmdtokens = str(text).split(' ')
            if len(cmdtokens)>0:
                index = int(cmdtokens[0])
            range = index+1
            if len(cmdtokens)>1:
                range = int(cmdtokens[1])+1
        except:
            pass
        listdir = await get_root(username)
        while index < range:
              rmfile = config.ROOT_PATH + username + '/' + listdir[index]
              await bot.edit_message(ev.chat,message,text=f'🗑 {listdir[index]} 🗑...')
              os.unlink(rmfile)
              index += 1
        await bot.delete_messages(ev.chat,message)
        await send_root(bot,ev,username)
        return

    if '/rar' in text:
        message = await bot.send_message(ev.chat.id,'📚Empezando...')
        text = str(text).replace('/rar ','')
        index = 0
        range = 0
        sizemb = 1900
        try:
            cmdtokens = str(text).split(' ')
            if len(cmdtokens)>0:
                index = int(cmdtokens[0])
            range = index+1
            if len(cmdtokens)>1:
                range = int(cmdtokens[1])+1
            if len(cmdtokens)>2:
                sizemb = int(cmdtokens[2])
        except:
            pass
        if index != None:
            listdir = await get_root(username)
            zipsplit = listdir[index].split('.')
            zipname = ''
            i=0
            for item in zipsplit:
                    if i>=len(zipsplit)-1:continue
                    zipname += item
                    i+=1
            totalzipsize=0
            iindex = index
            while iindex<range:
                ffullpath = config.ROOT_PATH + username + '/' + listdir[index]
                totalzipsize+=get_file_size(ffullpath)
                iindex+=1
            zipname = config.ROOT_PATH + username + '/' + zipname
            multifile = zipfile.MultiFile(zipname,config.SPLIT_FILE)
            zip = zipfile.ZipFile(multifile, mode='w', compression=zipfile.ZIP_DEFLATED)
            while index<range:
                ffullpath = config.ROOT_PATH + username + '/' + listdir[index]
                await bot.edit_message(ev.chat,message,text=f'📚 {listdir[index]} 📚...')
                filezise = get_file_size(ffullpath)
                zip.write(ffullpath)
                index+=1
            zip.close()
            multifile.close()
            await bot.delete_messages(ev.chat,message)
            await send_root(bot,ev,username)
            return

    if '/up' in text:
        message = await bot.send_message(ev.chat.id,'⬆️Empezando...')
        text = str(text).replace('/up ','')
        index = 0
        range = 0
        txtname = ''
        try:
            cmdtokens = str(text).split(' ')
            if len(cmdtokens)>0:
                index = int(cmdtokens[0])
            range = index+1
            if len(cmdtokens)>1:
                range = int(cmdtokens[1])+1
            if len(cmdtokens)>2:
                txtname = cmdtokens[2]
        except:
            pass
        listdir = await get_root(username)
        try:
            await bot.edit_message(ev.chat,message,text=f'📯Generando Session...')
            session:RepoUploader = await repouploader.create_session(config.PROXY)
            resultlist = []
            while index<range:
                  ffullpath = config.ROOT_PATH + username + '/' + listdir[index]
                  await bot.edit_message(ev.chat,message,text=f'⬆️Subiendo {listdir[index]}...')
                  result:RepoUploaderResult = await session.upload_file(ffullpath,progress_func=upload_progress,progress_args=(bot,ev,message,loop))
                  if result:
                      resultlist.append(result)
                  index+=1
            txtsendname = f'{username}.txt'
            if txtname!='':
                txtsendname = txtname
            txtfile = open(txtsendname,'w')
            urls = []
            for item in resultlist:
                urls.append(item.url)
            data = xdlink.parse(urls)
            if data:
                txtfile.write(data)
            else:
                txtfile.write('ERROR XDLINK PARSE URLS')
            txtfile.close()
            await bot.delete_messages(ev.chat,message)
            await bot.send_file(ev.chat,txtsendname)
            os.unlink(txtsendname)
        except Exception as ex:
             await bot.send_message(ev.chat.id,str(ex))
    pass



def init():
    try:
        bot = TelegramClient(
            'bot', api_id=config.API_ID, api_hash=config.API_HASH).start(bot_token=config.BOT_TOKEN)

        print('Bot is Started!')

        try:
            loopevent = asyncio.get_runing_loop();
        except:
            try:
                loopevent = asyncio.get_event_loop();
            except:
                loopevent = None

        @bot.on(events.NewMessage()) 
        async def process(ev: events.NewMessage.Event):
           await onmessage(bot,ev,loopevent)
           #await onmessage(bot,ev)
           #loopevent.create_task(onmessage(None,bot,ev))
           #t = ThreadAsync(loop=loopevent,targetfunc=onmessage,args=(loopevent,bot,ev))
           #t.start()


        loopevent.run_forever()
    except Exception as ex:
        init()
        conf.procesing = False

if __name__ == '__main__': 
   init()