# kodi-snips-remote
# Controll kodi via snips
With this script you can control Kodi via Snips. It is possible to start a Kodi navigaton loop. This will start a Snips session automaticaly when the old session ends. The Snips hotword is now not necessary for a faster navigation through the Kodi gui.

# Functions:
* Entities Injection to get the titles from Kodi media-library in the Snips assistant
* Play show
* Play (random) episodes of show
* Play movie
* Play songs from artist
* Play songs of specific genre
* Play album
* Search for shows and display results in gui 
* Search for movies and display results in gui
* Search for album and display results in gui
* Search for songs from artists and display results in gui
* Set subtitles on/off
* Set shuffle on/off
* Play/pause
* Stop
* Next/previous
* Open gui window:
  * Videos
  * Shows
  * Music
  * Addon
  * Useraddon
  * Videoaddon
  * Audiaddon
  * Executableaddon
  * Home
  * Videoplaylist
  * Musicplaylist
  * Fullscreenvideo
* Kodi navigation loop
* Navigate through the gui (only while Kodi navigation loop)
  * Left
  * Right
  * Up
  * Down
  * Pageup
  * Pagedown
  * Select
  * Back
  * Info
  * Playlist
  * Queue
  * Close
  * Togglewatched
  * Parentdir
  * Scrollup
  * Scrolldown
  
# Snips config
For the script the following Snips-apps with slots are used:
* datenbank:
  * hey Snips synchronise library
* play_movie:
  * hey Snips start the movie iron man(slot)
  * add the select_movie intent in case multiple titles will be found e.g. iron man 1, iron man 2, iron man 3
  * slotname: movies
  * slotvalue:  -filled from injection
* select_movie:
  * iron man 3(slot)
  * this intent will only work if the session is keept alive with the customData "media_selected" when multiple    sessions are found. so it is possible to only say the movie name without hey Snips...
  * slotname: movies
  * slotvalue:  -filled from injection
* play_show:
  * hey Snips play the show marvels iron fist(slot), hey Snips play a random(slot) episode of futurama(slot)
  * slotname: shows
  * slotvalue:  -filled from injection
  * slotname: random
  * slotvalue: random +synonyms
* select_show:
  * marvels iron fist, marvels luke cake....
  * slotname: shows
  * slotvalue:  -filled from injection
* play_genre:
  * hey Snips play pop(slot) music
  * slotname: genre
  * slotvalue:  -filled from injection
* play_artist:
  * hey Snips play songs by lady gaga(slot)
  * slotname: artist
  * slotvalue:  -filled from injection
* play_album:
  * hey Snips play album(slot) ...
  * slotname: albums
  * slotvalue:  -filled from injection
* kodiNavigator:
  * hey Snips start(slot) navigator
  * slotname: startstop
  * slotvalue: start, stop +synonyms
* kodiInputNavigation:
  * up, left, okay, back
  * this intent only works if the navigator loop started
  * slotname: kodiinput
  * slotvalue: (value, synonyms)
    * left, links, nach links
    * right, rechts, nach rechts
    * up, hoch, nach oben
    * down, runter, nach unten
    * pageup, eine seite hoch, eine seite nach oben
    * pagedown, eine seite runter, eine seite nach unten
    * select, okay, öffnen
    * back, zurück
    * info, information
    * playlist, öffne wiedergabe liste
    * queue, in playlist einreihen, zur playlist hinzufügen, zur wiedergabeliste hinzufügen
    * close, schließen
    * togglewatched, wechsel gesehen status
    * parentdir, ein ordner nach oben
    * scrollup, scroll hoch, hoch scrollen, nach oben scrollen
    * scrolldown, sroll runter, runter scrollen, nach unten scrollen
* kodiWindowNavigation:
  * hey Snips open movies(slot)
  * slotname: windows
  * slotvalues: (value, synonyms)
    * videos, Filme
    * shows, Serien
    * music, Musik
    * addon, Add ons
    * useraddon, benutzer addon
    * videoaddon, video addon
    * audiaddon, musik addon
    * executableaddon, programm addon
    * home, hauptmenü
    * videoplaylist, video playlist, video wiedergabeliste
    * musicplaylist, musik playlist, musik wiedergabeliste
    * fullscreenvideo, zurück zum video, zurück zur wiedergabe, zurück zum film, zurück zur serie, zurück zur folge
* KodiPause:
  * hey Snips papuse
* KodiResume:
  * hey Snips resume
* KodiStop:
  * hey Snips stop player
* KodiNext:
  * hey Snips play next song/episode
* KodiPrevious:
  * hey Snips play previous
* KodiShuffleON:
  * hey Snips set suffle on
* KodiShuffleOFF:
  * hey Snips set suffle off
* subtitles:
  * hey Snips set subtitles off(slot)
  * slotname: on_off
  * slotvalue: on, off +synonyms
* search_show:
  * hey Snips search show marvel(slot)
  * slotname: shows
  * slotvalue:  -filled from injection
* search_movie:
  * hey Snips search movie spider(slot)
  * slotname: movies
  * slotvalue:  -filled from injection
* search_artist:
  * hey Snips search artist eminem(slot)
  * slotname: artist
  * slotvalue:  -filled from injection
* search_album:
  * hey Snips search album relapse(slot)
  * slotname: albums
  * slotvalue:  -filled from injection
# install
The script uses the Eclipse's paho.mqtt library. https://github.com/eclipse/paho.mqtt.python

The Snips entities injection must be installed. https://docs.snips.ai/articles/advanced/dynamic-vocabulary

In kodi you must enable HTTP control: Settings/Services/Control > Allow remote control via HTTP must be enabled. Choose a 
Username, Password and Port

Change following values in the snips_remote.py:
* Kodi Username, Password, IP, Port
* MQTT server IP and Port
* Snips username 

To start the scrip run the snips_remote.py
