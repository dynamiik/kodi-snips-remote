import json
import requests
import re
kodi_url = ''
debuglevel =0
playlist_size =20
def ausgabe(text,mode):
    '''
    main function name -mode= 1
    debugs -mode= >=2
     - kodi function -mode= 1
       -- snips subscription -mode= 0
    '''
    ausgabe=""
    if mode < 2:
        ausgabe = " - "
    if mode >= debuglevel:
        print(ausgabe + str(text))
    return
def send(g_data,isfilter=0,all_data=""):
    headers = {
            'Content-type': 'application/json',
        }
    if all_data =="":
        data_head = '{"id":"160","jsonrpc":"2.0",'
        data_end = '}'
        data = data_head + g_data + data_end
    else:
        data = all_data
    try:
        response = requests.post(kodi_url, headers=headers, data=data)
        json_obj= response.text
        #ausgabe(json_obj,2)
        json_data = json.loads(json_obj)
        #ausgabe(json_data,2)
        for item in json_data:
            if item == 'result':
                #ausgabe('send is good',2)
                json_data = json_data['result']
                if isfilter == 0:
                    filter_dict(json_data)
                return(json_data)
            elif item == 'error':
                ausgabe('send is bad',2)
                ausgabe('data: '+data,2)
                ausgabe(json_data,2)
                return
    except: 
        ausgabe('server nicht erreichbar',2)
        return
    
    """except errorMeldung:
        ausgabe('es kam ein fehler zurueck',2)
        raise"""
    return
def check_connectivity():
    ausgabe('check_connectivity',1)
    data_method= '"method":"JSONRPC.Ping"'
    data_prop = ',"params":{}'
    data = data_method + data_prop
    json_data=send(data,1)
    return json_data

def filter_dict(d):
    #cause snips get confused with special characters this will replace all special chars with ' '
    #ausgabe('filter_dict',1)
    for key, value in d.items():
        if isinstance(value, dict):
            d[key] = filter_dict(value)
        elif isinstance(value, list):
            d[key] = [filter_dict(l) for l in value]
        else:
            d[key]=re.sub('[^A-Za-z0-9 ]+', ' ', str(value))
    return d

def get_movies():
    ausgabe('get_movies',1)
    data_method= '"method":"VideoLibrary.GetMovies"'
    data_prop = ',"params":{"properties":["title"],"sort":{"method":"none","order":"ascending"}}'
    data = data_method + data_prop
    json_data=send(data)
    return(json_data['movies'])

def get_shows():
    ausgabe('get_shows',1)
    data_method= '"method":"VideoLibrary.GetTVShows"'
    data_prop = ',"params":{"properties":["title","file","lastplayed"],"sort":{"method":"none","order":"ascending"}}'
    data = data_method + data_prop
    json_data=send(data)
    return(json_data['tvshows'])

def get_genre():
    ausgabe('get_genre',1)
    data_method= '"method":"AudioLibrary.GetGenres"'
    data_prop = ',"params":{"properties":["title"],"sort":{"method":"none","order":"ascending"}}'
    data = data_method + data_prop
    json_data=send(data)
    return(json_data['genres'])
def get_artists():
    ausgabe('get_artists',1)
    data_method= '"method":"AudioLibrary.GetArtists"'
    data_prop = ',"params":{"albumartistsonly":false,"properties":[],"limits":{"start":0},"sort":{"method":"label","order":"ascending","ignorearticle":true}}'
    data = data_method + data_prop
    json_data=send(data)
    return(json_data['artists'])
def get_songtitles():
    ausgabe('get_songtitles',1)
    data_method= '"method":"AudioLibrary.GetSongs"'
    data_prop = ',"params":{"properties":["title"],"limits":{"start":0},"sort":{"method":"title","order":"ascending","ignorearticle":true}}'
    data = data_method + data_prop
    json_data=send(data)
    return(json_data['songs'])
def get_albums():
    ausgabe('get_albums',1)
    data_method= '"method":"AudioLibrary.GetAlbums"'
    data_prop = ',"params":{"properties":["title"],"limits":{"start":0},"sort":{"method":"title","order":"ascending","ignorearticle":true}}'
    data = data_method + data_prop
    json_data=send(data)
    return(json_data['albums'])
def get_songs_by(filterkey,filtervalue):
    ausgabe('get_songs_by',1)
    data_method= '"method":"AudioLibrary.GetSongs"'
    data_prop = ',"params":{"properties":["title","albumid"],'\
                '"limits":{"start":0},"sort":{"method":"track","order":"ascending","ignorearticle":true},'\
                '"filter":{"'+filterkey+'":'+filtervalue+'}}'
    data = data_method + data_prop
    json_data=send(data)
    return(json_data['songs'])

def find_title_id(titlename,searchkey,id_slot_name,json_data):
    ausgabe('find_title_id',1)
    titleid=0
    for item in json_data:
        if item[searchkey].lower()==titlename.lower():
            titleid = item[id_slot_name]
            break
    return(titleid)

def find_title(titlename,json_data):
    ausgabe('find_title',1)
    title_found =[]
    for item in json_data:
        if titlename.lower() in item['label'].lower():
            title_found = title_found+ [item['label']]
    return(title_found)

def get_episodes_unseen(id):
    ausgabe('get_episodes_unseen',1)
    data_method= '"method":"VideoLibrary.GetEpisodes"'
    data_prop = ',"params":{"tvshowid":'+str(id)+',' \
                '"filter": {"field": "playcount", "operator": "lessthan", "value": "1"},' \
                '"properties":["title","file","lastplayed","season","playcount"], ' \
                '"sort": { "order": "ascending", "method": "label" }'\
                '}'
    data = data_method + data_prop
    json_data=send(data,1)
    return(json_data)

def get_episodes_all(id):
    ausgabe('add_episodes_all',1)
    data_method= '"method":"VideoLibrary.GetEpisodes"'
    data_prop = ',"params":{"tvshowid":'+str(id)+','\
                '"properties":["title","file","lastplayed","season","playcount"],'\
                '"sort": { "order": "ascending", "method": "label" }'\
                '}'
    data = data_method + data_prop
    json_data=send(data,1)
    return(json_data)

def insert_playlist(tupel,types, playlistid):
    ausgabe('insert_playlist',1)
    data_method= '"method":"Playlist.Clear"'
    data_prop = ',"params":{"playlistid":1}'
    data = data_method + data_prop
    send(data,1)
    num=0    
    data = "["
    
    for item in tupel:
        data_head = '{"id":"'+str(num+100)+'","jsonrpc":"2.0",'
        data_method= '"method":"Playlist.Insert"'
        data_prop = ',"params":['+str(playlistid)+','+str(num)+',{"'+types+'":'+str(item)+'}]}'
        data = data + data_head + data_method + data_prop
        if num+1 == playlist_size:
            break
        if num+1 < len(tupel):
            data = data + ', '
        num =num+1
    data = data + "]"    
    send("",1,data)
    return
def get_active_player():
    ausgabe('get_active_player',1)
    data_method= '"method":"Player.GetActivePlayers"'
    data_prop = ',"params":{}'
    data = data_method + data_prop
    active_json = send(data,1)
    
    if active_json != [] and active_json:
        return(active_json[0])
    else:
        return(active_json)

def get_properties():
    ausgabe('get_properties',1)
    player_id = get_active_player()
    if player_id:
        data = '{"jsonrpc":"2.0",'\
               '"method":"Player.GetProperties",'\
               '"params":['+str(player_id['playerid'])+',["playlistid","speed","position","totaltime",'\
               '"time","percentage","shuffled","repeat","canrepeat","canshuffle",'\
               '"canseek","partymode"]],'\
               '"id":1387}'
        json = send("",1,data)
        return(json)
    return
def get_running_state():
    ausgabe('get_running_state',1)
    state = 0
    json_state = get_properties()
    if json_state:
        if json_state['speed'] == 1:
            state=1
    return state
def start_play(playlistid):
    ausgabe('play',1)
    data_method = '"method":"Player.Open"'
    data_prop = ',"params":{"item":{"position":0,"playlistid":'+str(playlistid)+'}}'
    data = data_method + data_prop
    send(data,1)
    return
def play_pause():
    ausgabe('play_pause',1)
    json_data = get_active_player()
    if json_data != [] and json_data:
        data_method= '"method":"Player.PlayPause"'
        data_prop = ',"params":['+str(json_data['playerid'])+',"toggle"]'
        data = data_method + data_prop
        send(data,1)
    return
def resume():
    ausgabe('resume',1)
    json_data = get_active_player()
    if json_data != [] and json_data:
        data_method= '"method":"Player.PlayPause"'
        data_prop = ',"params":['+str(json_data['playerid'])+',true]'
        data = data_method + data_prop
        send(data,1)
    return
def pause():
    ausgabe('pause',1)
    json_data = get_active_player()
    if json_data != [] and json_data:
        data_method= '"method":"Player.PlayPause"'
        data_prop = ',"params":['+str(json_data['playerid'])+',false]'
        data = data_method + data_prop
        send(data,1)
    return
def stop():
    ausgabe('stop',1)
    json_data = get_active_player()
    if json_data != [] and json_data:
        data_method= '"method":"Player.Stop"'
        data_prop = ',"params":['+str(json_data['playerid'])+']'
        data = data_method + data_prop
        send(data,1)
    return
def subtitles(state):
    ausgabe('subtitles',1)
    data_method= '"method":"Player.SetSubtitle"'
    data_prop = ',"params":[1,"'+state+'"]'
    data = data_method + data_prop
    send(data,1)
    return
def next_media():
    ausgabe('next_media',1)
    json_data = get_active_player()
    if json_data != [] and json_data:
        data_method= '"method":"Player.GoTo"'
        data_prop = ',"params":['+str(json_data['playerid'])+',"next"]'
        data = data_method + data_prop
        send(data,1)
    return
def previous_media():
    ausgabe('previous_media',1)
    json_data = get_active_player()
    if json_data != [] and json_data:
        data_method= '"method":"Player.GoTo"'
        data_prop = ',"params":['+str(json_data['playerid'])+',"previous"]'
        data = data_method + data_prop
        send(data,1)
    return
def shuffle_on(playlistid=5):
    ausgabe('shuffle_on',1)
    if playlistid == 5:
        json_data = get_active_player()
        if json_data != [] and json_data:
            playlistid = json_data['playerid']
    data_method= '"method":"Player.SetShuffle"'
    data_prop = ',"params":['+str(playlistid)+',true]'
    data = data_method + data_prop
    send(data,1)
    return
def shuffle_off(playlistid=5):
    ausgabe('shuffle_off',1)
    if playlistid == 5:
        json_data = get_active_player()
        if json_data != [] and json_data:
            playlistid = json_data['playerid']
    data_method= '"method":"Player.SetShuffle"'
    data_prop = ',"params":['+str(playlistid)+',false]'
    data = data_method + data_prop
    send(data,1)
    return

def get_gui():
    data_method= '"method":"GUI.GetProperties"'
    data_prop = ',"params":{"properties":["currentwindow","currentcontrol"]}'
    data = data_method + data_prop
    ausgabe(send(data,1),3)
    return
def introspect():
    data_method= '"method":"JSONRPC.Introspect"'
    data_prop = ''
    data = data_method + data_prop
    ausgabe(send(data,1),3)
    return
def open_gui(window="",mediatype="", filtervalue="",isfilter=0):
    ausgabe('open_gui',1)
    parameter=""
    if isfilter:
        if mediatype == 'movies' or mediatype == 'tvshows':
            window = 'videos'
            filterkey = 'title'
            if mediatype == 'movies':
                destination = "videodb://movies/titles/"
            else:
                destination = "videodb://tvshows/titles/"
        else:
            window = 'music'
            if mediatype == 'artists':
                destination = "musicdb://artists/"
                filterkey = "artist"
            else:
                destination = "musicdb://albums/"
                filterkey = "album"
        parameter = ',"parameters":["'\
                    +destination+\
                    '?filter=%7b%22rules%22%3a%7b%22and%22%3a%5b%7b'\
                    '%22field%22%3a%22'\
                    +filterkey+\
                    '%22%2c%22operator%22%3a%22contains%22%2c%22value%22%3a%5b%22'\
                    +filtervalue+\
                    '%22%5d%7d%5d%7d%2c%22type%22%3a%22'\
                    +mediatype+\
                    '%22%7d"]'
        
    elif filtervalue != "":
        parameter = ',"parameters":["'+filtervalue+'"]'
        
    data_method= '"method":"GUI.ActivateWindow"'
    data_prop = ',"params":{"window": "'+window+'"'\
                +parameter+ '}'
    data = data_method + data_prop
    send(data,1)
    return
def send_input(slotvalue):
    data_method= '"method":"Input.ExecuteAction"'
    data_prop = ',"params":["'+slotvalue+'"]'
    data = data_method + data_prop
    ausgabe(send(data,1),3)
    return
def init(kodi_user,kodi_pw,kodi_ip,kodi_port,_debuglevel):
    global kodi_url
    global debuglevel
    kodi_url = 'http://'+kodi_user+':'+kodi_pw+'@'+kodi_ip+':'+kodi_port+'/jsonrpc'
    debuglevel = _debuglevel
    if check_connectivity():
        print("Kodi connected at {0}:{1}".format(kodi_ip, kodi_port))
    else:
        print("Kodi not found at {0}:{1}".format(kodi_ip, kodi_port))

