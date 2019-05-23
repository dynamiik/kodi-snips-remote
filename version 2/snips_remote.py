import paho.mqtt.client as mqtt
import json
import kodi
from random import shuffle
playing_state_old = 0
is_in_session=0
is_injecting=0

#MQTT host and port
HOST = '127.0.0.1'
PORT = 1883

#snips username with ':' or '__' at the end
snipsuser = ""

#kodi  login data
kodi_ip = ''
kodi_user = ''
kodi_pw = ''
kodi_port = '8080'


debuglevel = 1 # 0= snips subscriptions; 1= function call; 2= debugs; 3=higher debug

def ausgabe(text,mode=3):
    # 0= snips subscriptions; 1= function call; 2= debugs; 3=higher debug
    '''
    function name -mode= 1
    debugs -mode= >=2
     - kodi function -mode= 1
       -- snips subscription -mode= 0
    '''
    ausgabe=""
    if mode < 1:
        ausgabe = "   -- "
    if mode >= debuglevel:
        print(ausgabe + str(text))
    return
def build_tupel(json, filtervalue):
    #Build tupels and lists of json
    ausgabe('build_tupel',1)
    json_data = json
    tupel = []
    for item in json_data:
        if item[filtervalue] != '' and item[filtervalue] != ' ':
            tupel = tupel + [item[filtervalue]]
    return tupel

def inject():
    #makes an injection for snpips from the kodi library. Entities Injection musst be installed
    #replaces all special chars with ' ' bevor inject.
    global is_injecting
    is_injecting = 1
    ausgabe('inject',1)
    send={"operations": [["addFromVanilla",{"shows":[],"movies":[],"genre":[],"artist":[],"albums":[]}]]} #"shows":[],"movies":[],... are entitie names from snips
    tupel = build_tupel(kodi.get_movies(),'title')
    send['operations'][0][1]['movies'] = send['operations'][0][1]['movies']+tupel
    tupel = build_tupel(kodi.get_shows(),'title')
    send['operations'][0][1]['shows'] = send['operations'][0][1]['shows']+tupel
    tupel = build_tupel(kodi.get_genre(),'title')
    send['operations'][0][1]['genre'] = send['operations'][0][1]['genre']+tupel
    tupel = build_tupel(kodi.get_artists(),'artist')
    send['operations'][0][1]['artist'] = send['operations'][0][1]['artist']+tupel
    tupel = build_tupel(kodi.get_albums(),'title')
    send['operations'][0][1]['albums'] = send['operations'][0][1]['albums']+tupel
    client.publish("hermes/injection/perform",json.dumps(send))
    return

def start_navigator(session_id):
    #start a snips session loop so that the hotword is not necessary. this is for controll the kodi menue. 
    ausgabe('start_navigator',1)
    global is_in_session
    is_in_session = 1
    client.publish("hermes/feedback/sound/toggleOff",'{"siteId":"default"}')
    end_session(session_id,text="navigator gestartet")
    return
def end_navigator(session_id=""):
    #ends the session loop
    ausgabe('end_navigator',1)
    global is_in_session
    is_in_session = 0
    if session_id == "":
        start_session(session_type="notification",text="Navigator gestoppt")
    else:
        end_session(session_id,text="Navigator gestoppt")
    client.publish("hermes/feedback/sound/toggleOn",'{"siteId":"default"}')
    return
def kodi_navigation_input(slotvalue,session_id):
    #for the kodi Input.ExecuteAction while in session loop.
    ausgabe('kodi_navigation_input',1)
    kodi.send_input(slotvalue)
    end_session(session_id)
    return
def kodi_navigation_gui(slotvalue,session_id=""):
    #for the kodi GUI.ActivateWindow. prepares values before send
    ausgabe('kodi_navigation_gui',1)
    window=""
    filtervalue=""
    if slotvalue == 'home':
        window='home'
    elif slotvalue == 'music':
        window='music'
        filtervalue="musicdb://"
    elif slotvalue == 'videos':
        window='videos'
        filtervalue="videodb://movies/titles/"
    elif slotvalue == 'shows':
        window='videos'
        filtervalue="videodb://tvshows/titles/"
    elif slotvalue == 'videoaddon':
        window='programs'
        filtervalue="addons://sources/video/"
    elif slotvalue == 'audiaddon':
        window='programs'
        filtervalue="addons://sources/audio/"
    elif slotvalue == 'executableaddon':
        window='programs'
        filtervalue="addons://sources/executable/"
    elif slotvalue == 'useraddon':
        window='programs'
        filtervalue="addons://user/"
    else:
        window = slotvalue
    kodi.open_gui(window=window,filtervalue=filtervalue)
    if session_id != "":
        end_session(session_id)
    return
def start_session(session_type="action",text="",intent_filter="",customData=""):
    #starts a snips session as notification or as action. also adds custom data to session
    ausgabe("start_session",1)
    data = ""
    cdata =""
    data = data + ',"text":"'+text+'"'
    if intent_filter!="":
        data = data + ',"intentFilter":['+intent_filter+']'
    else:
        data = data + ',"intentFilter":null'
    if customData!="":
        cdata = ',"customData":"'+customData+'"'
    client.publish("hermes/dialogueManager/startSession",'{"sideId": "default","init":'\
                   '{"type":"'+session_type+'","canBeEnqueued":true'+data+'}'+cdata+'}')
    return

def keep_session_alive(session_id,text="",intent_filter="",customData=""):
    #keeps the snips session running with or without tts. also adds custom data to session
    ausgabe('keep_session_alive',1)
    data = ""
    data = data + ',"text":"'+text+'"'
    if intent_filter!="":
        data = data + ',"intentFilter":['+intent_filter+']'
    if customData!="":
        data = data + ',"customData":"'+customData+'"'
    client.publish("hermes/dialogueManager/continueSession",\
                                '{"sessionId":"'+session_id+'"'+data+'}')
    return

def end_session(session_id,text=""):
    #ends a snips session with or without tts
    ausgabe('end_session',1)
    if text!="":
        text = ',"text":"'+text+'"'
    client.publish("hermes/dialogueManager/endSession",'{"sessionId":"'+session_id+'"'+text+'}')
    return

def search(slotvalue,slotname,json_d):
    #check if word is in titles of the kodi library. e.g. marvel will be in more than 1 title. if found it will display it in kodi
    ausgabe("search",1)
    titles = kodi.find_title(slotvalue,json_d)
    if len(titles) ==0:
        start_session(session_type="notification", text="keine medien gefunden")
    elif len(titles) >=1:
        ausgabe('slotname: '+slotname,2)
        if slotname == 'shows':
            mediatype = 'tvshows'
        elif slotname =='movies':
            mediatype = 'movies'
        elif slotname == 'artist': #or slotname == 'albums':
            mediatype = 'artists'
        elif slotname == 'albums':
            mediatype ='albums'
        kodi.open_gui("", mediatype, slotvalue,isfilter=1)
    return(titles)
def start_tv():
    ausgabe("start_tv",1)
    kodi.stop()
    kodi_navigation_gui("videoplaylist")
    showsid_tupel= build_tupel(kodi.get_tv_shows("tv"),"tvshowid")
    ausgabe(len(showsid_tupel))
    #kodi.show_notification(len(showsid_tupel)+" Serien gefunden. Episoden werden gesucht")
    id_tupel =[]    
    kodi.show_notification("Programm wird geladen")
    kodi.clear_playlist("1")
    json_data = kodi.get_tv_shows_episodeids(showsid_tupel)
    for item in json_data:
        if item['result']['limits']['total'] != 0:
            id_tupel_temp = build_tupel(item['result']['episodes'], "episodeid")
            shuffle(id_tupel_temp)
            id_tupel = id_tupel + [id_tupel_temp[0]]+ [id_tupel_temp[1]]+ [id_tupel_temp[2]]+ [id_tupel_temp[3]]
    ausgabe(len(id_tupel))
    shuffle(id_tupel)
    kodi.insert_playlist(id_tupel,'episodeid', '1')
    kodi.start_play('1')    
    return
def start_playlist(playlist, playlistid):
    ausgabe("start_playlist",1)
    kodi.stop()
    kodi_navigation_gui("videoplaylist")
    kodi.add_playlist(playlist,playlistid)
    kodi.start_play(playlistid)
    return
def start_partymode():
    kodi.stop()
    kodi_navigation_gui("musicplaylist")
    kodi.partymode()
    return
def main_controller(slotvalue,slotname,id_slot_name,json_d,session_id,intent_filter,israndom,playlistid):
    
    '''
    serch id of title in json from kodi library. if id is found get episodes/songs ids, stop kodi, insert playlist, (shuffle playlist), play.
    if id not found: search(). if search finds only one(search "big bang" find "the big bang theroy"): main_controller with slotvalue=search() return.
    if found multiple (search "iron" find "iron man 1, iron man 2..." keep session alive and add media_selected to custom_data. 
    playlist size is limited to 20 items cause kodi keeps crashing while adding to much items
    
    slotvalue: the media title from snips e.g. Iron Man
    slotname: the name of the slot of the snips intent e.g. movies
    id_slot_name: the key value name of the media id from the kodi library json
    session_id: the snips session id
    intent_filter: the intents for new or keep alive snips sessions
    israndom: from snips if the media should played in random order e.g. hey snips play seinfeld in random order
    playlistid: the playlist id for kodi. 0=Music; 1=Movies; 2=Pictures
    '''
    global playing_state_old
    ausgabe('main_controller',1)
    media_id_of_title_found = kodi.find_title_id(slotvalue,'label',id_slot_name,json_d)
    if media_id_of_title_found != 0:
        intent_filter=""
        if slotname =='shows':
            id_slot_name='episodeid'
            if str(israndom) == "random":
                json_episodes = kodi.get_episodes_all(media_id_of_title_found)
            else:
                json_episodes = kodi.get_episodes_unseen(media_id_of_title_found)
            if json_episodes['limits']['total'] != 0:
                id_tupel = build_tupel(json_episodes['episodes'], id_slot_name)
            else:
                start_session(session_type="notification", text="keine episoden gefunden")
        elif slotname=='movies':
            id_tupel = [media_id_of_title_found]
        elif slotname=='genre':
            id_tupel = [media_id_of_title_found]
            #json_songs = kodi.get_songs_by(id_slot_name,media_id_of_title_found)
            #id_slot_name="songid"
            #id_tupel = build_tupel(json_songs, id_slot_name)
        elif slotname=='artist':
            id_tupel = [media_id_of_title_found]
            #json_songs = kodi.get_songs_by(id_salot_name,media_id_of_title_found)
            #id_slot_name="songid"
            #id_tupel = build_tupel(json_songs, id_slot_name)
        elif slotname=='albums':
            id_tupel = [media_id_of_title_found]
            #json_songs = kodi.get_songs_by(id_slot_name,media_id_of_title_found)
            #id_slot_name="songid"
            #id_tupel = build_tupel(json_songs, id_slot_name)
        playing_state_old = 0
        if israndom == "random":
            shuffle(id_tupel)
        end_session(session_id, text="")
        kodi.stop()
        if playlistid == 1:
            kodi_navigation_gui("videoplaylist")
        elif playlistid == 0:
            kodi_navigation_gui("musicplaylist")
        kodi.insert_playlist(id_tupel,id_slot_name, playlistid)
        kodi.start_play(playlistid)
    else:
        titles = search(slotvalue,slotname,json_d)
        #ausgabe(titles)
        if len(titles) == 1:
            end_session(session_id, text="")
            main_controller(titles[0],slotname,id_slot_name,json_d,session_id,intent_filter,israndom,playlistid)
            return
        elif len(titles) > 1:
            keep_session_alive(session_id,text="okay. was?",intent_filter=intent_filter,customData="media_selected")            
    return

def on_connect(client, userdata, flags, rc):
    print("Connected to {0} with result code {1}".format(HOST, rc))
    client.subscribe("hermes/hotword/default/detected")
    client.subscribe('hermes/intent/#')
    client.subscribe('hermes/tts/sayFinished')
    #client.subscribe('hermes/asr/textCaptured')
    client.subscribe('hermes/dialogueManager/#')
    client.subscribe('hermes/asr/textCaptured')
    kodi.init(kodi_user,kodi_pw,kodi_ip,kodi_port,debuglevel)
    
def on_message(client, userdata, msg):
    global playing_state_old
    global is_in_session
    if msg.topic != 'hermes/audioServer/default/audioFrame':
        ausgabe(''+msg.topic,0)
    if msg.topic == 'hermes/hotword/default/detected':
        #when hotword is detected pause kodi player for better understanding. check if kodi is online, kodi is playing, not in kodi navigator session
        ausgabe('silent_mediaplay',1)
        if kodi.check_connectivity() and kodi.get_running_state() and not is_in_session:
            kodi.pause()
            playing_state_old = 1
    elif msg.topic == 'hermes/dialogueManager/sessionEnded':
        '''
        if session ended return to kodi playing state. check if not in kodi navigator session so kodi keeps on pause while navigating.
        also check current playing state so kodi wont return to play when "hey snips kodi pause"
        check for is_in_session to end kodi navigator when asked or start a new session for navigator session loop
        '''
        if kodi.check_connectivity() and not is_in_session:
            ausgabe('reset_mediaplay',1)
            playing_state_current = kodi.get_running_state() 
            if playing_state_old == 1 and playing_state_current == 0:
                kodi.resume()
            playing_state_old = 0
        elif kodi.check_connectivity() and is_in_session:
            if kodi.get_running_state():
                end_navigator()
            else:
                start_session(intent_filter='"'+snipsuser+'kodiNavigator","'+snipsuser+'kodiInputNavigation",'\
                              '"'+snipsuser+'kodiWindowNavigation", "'+snipsuser+'search_album",'\
                              '"'+snipsuser+'search_artist","'+snipsuser+'search_movie",'\
                              '"'+snipsuser+'search_show"'\
                              ,customData="kodi_navigation")
                
    elif msg.topic == 'hermes/asr/textCaptured':
        #checks for captured text to end session immediately if it is empty 
        payload = json.loads(msg.payload.decode())
        session_id= payload['sessionId']
        if payload['text'] == '':
            end_session(session_id,text="")
            
    elif 'intent' in msg.topic:
        ausgabe("Intent detected!",1)
        payload = json.loads(msg.payload.decode())
        slotvalue = ""
        slotname = ""
        slotisrandom = ""
        playlistid = 1
        if len(payload['slots']) > 1:
            #check if besides the mediatitle name the random slot is given 
            for item in payload['slots']:
                if item['slotName'] == 'random':
                    slotisrandom = "random"
                else:
                    slotvalue = item["value"]["value"]
                    slotname = item["slotName"]
        elif payload["slots"] != []:
            slotvalue = payload["slots"][0]["value"]["value"]
            slotname = payload["slots"][0]["slotName"]   
        name = payload["intent"]["intentName"]
        session_id= payload['sessionId']
        custom_data = payload['customData']
        ausgabe('"{0}" \n   -- "{1}":"{2}"\n   -- "customData":"{3}\n   -- "{4}" wiedergabe \n   -- "sessionId: {5} '\
            .format(name, slotname, slotvalue, custom_data, slotisrandom,session_id),0)
        if kodi.check_connectivity():
            #check if kodi is online else end session
            #first check for intents which can require the session to keep alive or start a new session with tts
            if msg.topic == 'hermes/intent/'+snipsuser+'datenbank':
                #hey snips synchronise library
                inject()
            elif msg.topic == 'hermes/intent/'+snipsuser+'play_movie':
                '''
                hey snips start the movie iron man
                add the select_movie intent in case multiple titles will be found e.g. iron man 1, iron man 2, iron man 3
                slotname: movies
                slotvalue:  -filled from injection
                '''
                intent_filter = '"'+snipsuser+'select_movie","'+snipsuser+'play_movie"'
                main_controller(slotvalue,slotname,'movieid',kodi.get_movies(),session_id,intent_filter,slotisrandom, playlistid)
            elif msg.topic == 'hermes/intent/'+snipsuser+'select_movie':
                '''
                iron man 3
                this intent will only work if the session is keept alive with the customData "media_selected" when multiple sessions are found. so it is possible to only say the movie name without hey snips...
                slotname: movies
                slotvalue:  -filled from injection
                '''
                
                if payload['customData']=="media_selected":
                    intent_filter = '"'+snipsuser+'select_movie","'+snipsuser+'play_movie"'
                    main_controller(slotvalue,slotname,'movieid',kodi.get_movies(),session_id,intent_filter,slotisrandom,playlistid)
                else:
                    end_session(session_id,text="")
            elif msg.topic == 'hermes/intent/'+snipsuser+'play_show':
                '''
                hey snips play the show marvels iron fist, hey snips play a random episode of futurama
                slotname: shows
                slotvalue:  -filled from injection
                slotname: random
                slotvalue: random +synonyms
                '''
                intent_filter = '"'+snipsuser+'play_show","'+snipsuser+'select_show"'
                main_controller(slotvalue,slotname,'tvshowid',kodi.get_shows(),session_id,intent_filter,slotisrandom,playlistid)
            elif msg.topic == 'hermes/intent/'+snipsuser+'select_show':
                '''
                if multiple shows are found e.g hey snips play the show marvels - marvels iron fist, marvels luke cake....
                slotname: shows
                slotvalue:  -filled from injection
                '''
                if payload['customData']=="media_selected":
                    intent_filter = '"'+snipsuser+'play_show","'+snipsuser+'select_show"'
                    main_controller(slotvalue,slotname,'tvshowid',kodi.get_shows(),session_id,intent_filter,slotisrandom,playlistid)
                else:
                    end_session(session_id,text="")
            elif msg.topic == 'hermes/intent/'+snipsuser+'play_genre':
                '''
                hey snips play pop music
                slotname: genre
                slotvalue:  -filled from injection
                '''
                intent_filter = '"'+snipsuser+'play_genre",'+'"'+snipsuser+'select_genre"'
                main_controller(slotvalue,slotname,'genreid',kodi.get_genre(),session_id,intent_filter,slotisrandom,0)
            elif msg.topic == 'hermes/intent/'+snipsuser+'select_genre':
                '''
                if multiple shows are found e.g hey snips play the show marvels - marvels iron fist, marvels luke cake....
                slotname: shows
                slotvalue:  -filled from injection
                '''
                if payload['customData']=="media_selected":
                    intent_filter = '"'+snipsuser+'play_genre",'+'"'+snipsuser+'select_genre"'
                    main_controller(slotvalue,slotname,'genreid',kodi.get_genre(),session_id,intent_filter,slotisrandom,0)
                else:
                    end_session(session_id,text="")
            elif msg.topic == 'hermes/intent/'+snipsuser+'play_artist':
                '''
                hey snips play songs by lady gaga
                slotname: artist
                slotvalue:  -filled from injection
                '''
                intent_filter = '"'+snipsuser+'play_artist",'+'"'+snipsuser+'select_artist"'
                main_controller(slotvalue,slotname,'artistid',kodi.get_artists(),session_id,intent_filter,slotisrandom,0)
            elif msg.topic == 'hermes/intent/'+snipsuser+'select_artist':
                '''
                if multiple shows are found e.g hey snips play the show marvels - marvels iron fist, marvels luke cake....
                slotname: shows
                slotvalue:  -filled from injection
                '''
                if payload['customData']=="media_selected":
                    intent_filter = '"'+snipsuser+'play_artist",'+'"'+snipsuser+'select_artist"'
                    main_controller(slotvalue,slotname,'artistid',kodi.get_artists(),session_id,intent_filter,slotisrandom,0)
                else:
                    end_session(session_id,text="")
            elif msg.topic == 'hermes/intent/'+snipsuser+'play_album':
                '''
                hey snips play album ...
                slotname: albums
                slotvalue:  -filled from injection
                '''
                intent_filter = '"'+snipsuser+'play_album",'+'"'+snipsuser+'select_album"'
                main_controller(slotvalue,slotname,'albumid',kodi.get_albums(),session_id,intent_filter,slotisrandom,0)
            elif msg.topic == 'hermes/intent/'+snipsuser+'select_album':
                '''
                if multiple shows are found e.g hey snips play the show marvels - marvels iron fist, marvels luke cake....
                slotname: shows
                slotvalue:  -filled from injection
                '''
                if payload['customData']=="media_selected":
                    intent_filter = '"'+snipsuser+'play_album",'+'"'+snipsuser+'select_album"'
                    main_controller(slotvalue,slotname,'albumid',kodi.get_albums(),session_id,intent_filter,slotisrandom,0)
                else:
                    end_session(session_id,text="")
            elif msg.topic == 'hermes/intent/'+snipsuser+'kodiNavigator':
                '''
                hey snips start navigator
                slotname: startstop
                slotvalue: start, stop +synonyms
                '''
                if slotvalue =='start':
                    start_navigator(session_id)    
                if slotvalue == 'stop':
                    end_navigator(session_id)
            elif msg.topic == 'hermes/intent/'+snipsuser+'kodiInputNavigation':
                '''
                up, left, okay, back, search for movies with marvels
                this intent only works if the navigator loop started
                slotname: kodiinput
                slotvalue: (value, synonyms)
                    left, links, nach links
                    right, rechts, nach rechts
                    up, hoch, nach oben
                    down, runter, nach unten
                    pageup, eine seite hoch, eine seite nach oben
                    pagedown, eine seite runter, eine seite nach unten
                    select, okay, öffnen
                    back, zurück
                    info, information
                    playlist, öffne wiedergabe liste
                    queue, in playlist einreihen, zur playlist hinzufügen, zur wiedergabeliste hinzufügen
                    close, schließen
                    togglewatched, wechsel gesehen status
                    parentdir, ein ordner nach oben
                    scrollup, scroll hoch, hoch scrollen, nach oben scrollen
                    scrolldown, sroll runter, runter scrollen, nach unten scrollen

                '''
                if payload['customData']=="kodi_navigation":
                    kodi_navigation_input(slotvalue,session_id)
                else:
                    end_session(session_id)
            elif msg.topic == 'hermes/intent/'+snipsuser+'kodiWindowNavigation':
                '''
                hey snips open movies, home, addons
                slotname: windows
                slotvalues: (value, synonyms)
                    videos, Filme
                    shows, Serien
                    music, Musik
                    addon, Add ons
                    useraddon, benutzer addon
                    videoaddon, video addon
                    audiaddon, musik addon
                    executableaddon, programm addon
                    home, hauptmenü
                    videoplaylist, video playlist, video wiedergabeliste
                    musicplaylist, musik playlist, musik wiedergabeliste
                    fullscreenvideo, zurück zum video, zurück zur wiedergabe, zurück zum film, zurück zur serie, zurück zur folge

                '''
                kodi_navigation_gui(slotvalue,session_id)
            
            else:
                #these intent will end the session after the function is called
                if msg.topic == 'hermes/intent/'+snipsuser+'KodiPause':
                    #hey snips papuse
                    playing_state_old = 0
                    kodi.pause()
                    ausgabe('pause',1)
                elif msg.topic == 'hermes/intent/'+snipsuser+'KodiResume':
                    #hey snips resume
                    playing_state_old = 0
                    kodi.resume()
                    ausgabe('resume',1)
                elif msg.topic == 'hermes/intent/'+snipsuser+'KodiStop':
                    #hey snips stop player
                    playing_state_old = 0
                    kodi.stop()
                    ausgabe('stop',1)
                elif msg.topic == 'hermes/intent/'+snipsuser+'KodiNext':
                    #hey snips play next song/episode
                    kodi.next_media()
                    ausgabe('next_media',1)
                elif msg.topic == 'hermes/intent/'+snipsuser+'KodiPrevious':
                    #hey snips play previous
                    kodi.previous_media()
                    ausgabe('previous_media',1)
                elif msg.topic == 'hermes/intent/'+snipsuser+'KodiShuffle':
                    '''
                    hey snips set shuffle off
                    slotname: on_off
                    slotvalue: on, off +synonyms
                    '''
                    kodi.shuffle(slotvalue)
                    ausgabe('shuffle_on',1)
                elif msg.topic == 'hermes/intent/'+snipsuser+'kodiSubtitles':
											 
												
											
																		 
                    '''
                    hey snips set subtitles off
                    slotname: on_off
                    slotvalue: on, off +synonyms
                    '''
                    kodi.subtitles(slotvalue)
                    ausgabe('set_subtitles',1)
                elif msg.topic == 'hermes/intent/'+snipsuser+'search_show':
                    '''
                    hey snips search show marvel
                    slotname: shows
                    slotvalue:  -filled from injection
                    '''
                    search(slotvalue,slotname,kodi.get_shows())
                elif msg.topic == 'hermes/intent/'+snipsuser+'search_movie':
                    '''
                    hey snips search movie spider
                    slotname: movies
                    slotvalue:  -filled from injection
                    '''
                    search(slotvalue,slotname,kodi.get_movies())
                elif msg.topic == 'hermes/intent/'+snipsuser+'search_artist':
                    '''
                    hey snips search artist eminem
                    slotname: artist
                    slotvalue:  -filled from injection
                    '''
                    search(slotvalue,slotname,kodi.get_artists())
                elif msg.topic == 'hermes/intent/'+snipsuser+'search_album':
                    '''
                    hey snips search album relapse
                    slotname: albums
                    slotvalue:  -filled from injection
                    '''
                    search(slotvalue,slotname,kodi.get_albums())
                elif msg.topic == 'hermes/intent/'+snipsuser+'play_music':
                    '''
                    
                    '''
                    start_partymode()
                elif msg.topic == 'hermes/intent/'+snipsuser+'play_tv':
                    #start_tv()
                    start_playlist("video/tv.xsp", 1)
                elif msg.topic == 'hermes/intent/'+snipsuser+'kodi_wakeup':
                    if str(kodi.get_gui()['id']) == '13003':
                        kodi.send_input("up")
                end_session(session_id,text="")
        else:
            end_session(session_id,text="")


client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect(HOST, PORT, 60)
client.loop_forever()
