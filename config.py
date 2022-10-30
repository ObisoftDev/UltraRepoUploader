import os
import ProxyCloud

BOT_TOKEN =  os.environ.get('bot_token','5754595072:AAHl5S_uEJglSaMZV5zqA-C81tntHww4W10')
API_ID =  os.environ.get('api_id','18641760')
API_HASH = os.environ.get('api_hash','b7b026ce9d1d36400c02dc21d8df53a3')
SPLIT_FILE = 1024 * 1024 * int(os.environ.get('split_file','99'))
ROOT_PATH = 'root/'
ACCES_USERS = os.environ.get('tl_admin_user','obisoftt').split(';')
PROXY = ProxyCloud.parse(os.environ.get('proxy_enc','http://KHGHJHYHJHLHFHYHDHGHYHJHHHCHRHDHLHDHLH'))

if PROXY:
  print(f'Proxy {PROXY.as_dict_proxy()}')
