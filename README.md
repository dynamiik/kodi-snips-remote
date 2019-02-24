# kodi-snips-remote
# Controll kodi via snips
With this script it is possible to control kodi via snips. The snips entities injection must be installed. The IP and login data for kodi must be insert in the mqtt script. HTTP control in Kodi must be enabled. It is possible to start a kodi navigaton loop. This will start a snips session loop. The hotword is now not necessary for a better navigation through the kodi gui. To start the scrip run the mqtt.py.
# Functions:
* Entities Injection to get the titles from kodi library in the snips assistant
* Play show
* Play (random) episodes of show
* Play movie
* Play songs from artist
* Play songs of specific genre
* Play album
* Search for shows and display results in gui 
* Search for movies and display results in gui
* Search for album and display results in gui
* Search for song artists and display results in gui
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
* Navigate through the gui (only while kodi navigation loop)
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
For the Script the following apps with slots are used:
* datenbank:
  * hey snips synchronise library
* play_movie:
  * hey snips start the movie iron man(slot)
  * add the select_movie intent in case multiple titles will be found e.g. iron man 1, iron man 2, iron man 3
  * slotname: movies
  * slotvalue:  -filled from injection
* select_movie:
  * iron man 3(slot)
  * this intent will only work if the session is keept alive with the customData "media_selected" when multiple    sessions are found. so it is possible to only say the movie name without hey snips...
  * slotname: movies
  * slotvalue:  -filled from injection
* play_show:
  * hey snips play the show marvels iron fist(slot), hey snips play a random(slot) episode of futurama(slot)
  * slotname: shows
  * slotvalue:  -filled from injection
  * slotname: random
  * slotvalue: random +synonyms
* select_show:
  * marvels iron fist, marvels luke cake....
  * slotname: shows
  * slotvalue:  -filled from injection
* play_genre:
  * hey snips play pop(slot) music
  * slotname: genre
  * slotvalue:  -filled from injection
* play_artist:
  * hey snips play songs by lady gaga(slot)
  * slotname: artist
  * slotvalue:  -filled from injection
* play_album:
  * hey snips play album(slot) ...
  * slotname: albums
  * slotvalue:  -filled from injection
* kodiNavigator:
  * hey snips start(slot) navigator
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
  * hey snips open movies(slot)
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
  * hey snips papuse
* KodiResume:
  * hey snips resume
* KodiStop:
  * hey snips stop player
* KodiNext:
  * hey snips play next song/episode
* KodiPrevious:
  * hey snips play previous
* KodiShuffleON:
  * hey snips set suffle on
* KodiShuffleOFF:
  * hey snips set suffle off
* subtitles:
  * hey snips set subtitles off(slot)
  * slotname: on_off
  * slotvalue: on, off +synonyms
* search_show:
  * hey snips search show marvel(slot)
  * slotname: shows
  * slotvalue:  -filled from injection
* search_movie:
  * hey snips search movie spider(slot)
  * slotname: movies
  * slotvalue:  -filled from injection
* search_artist:
  * hey snips search artist eminem(slot)
  * slotname: artist
  * slotvalue:  -filled from injection
* search_album:
  * hey snips search album relapse(slot)
  * slotname: albums
  * slotvalue:  -filled from injection

