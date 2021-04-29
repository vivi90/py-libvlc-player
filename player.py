#!/usr/bin/env python3
from typing import Callable
from vlc import Instance as vlcInstance, MediaList, MediaListPlayer, Event, EventType, State
from datetime import timedelta
from time import sleep

class MusicPlayer:
    """Simple LibVLC based music player

    :Author: Vivien Richter <vivien-richter@outlook.de>
    :Version: 2.0.0
    :License: `Creative Commons Attribution 4.0 International <https://creativecommons.org/licenses/by/4.0>`_
    :Repository: `GitHub <https://github.com/vivi90/py-libvlc-player.git>`_
    """

    def __init__(self, mrls: tuple[str, ...] = None, options: str = "", trackChangedEventCallback: Callable[[str, str, str, str, str], None] = None, positionChangedEventCallback: Callable[[float], None] = None) -> None:
        """Constructor

        :param mrls: Media ressource locators
        :param trackChangedEventCallback: User defined callback, that's called at an track changed event and expects five parameters
        :param positionChangedEventCallback: User defined callback, that's called at an position changed event and expects one parameter
        """
        self.player = MediaListPlayer(vlcInstance(options))
        self.player.event_manager().event_attach(
            EventType.MediaListPlayerNextItemSet,
            self.trackChanged
        )
        self.player.get_media_player().event_manager().event_attach(
            EventType.MediaPlayerTimeChanged,
            self.positionChanged
        )
        self.trackChangedEventCallback = trackChangedEventCallback
        self.positionChangedEventCallback = positionChangedEventCallback
        self.mrls = mrls

    def trackChanged(self, event):
        '''Track changed event'''
        media = self.player.get_media_player().get_media()
        if media.get_meta(1) is not None and self.trackChangedEventCallback is not None:
            self.trackChangedEventCallback(
                media.get_meta(0),  # Title
                media.get_meta(1),  # Artist
                media.get_meta(6),  # Description
                media.get_meta(10), # URL
                media.get_meta(15)  # Artlink
            )

    def positionChanged(self, event):
        '''Position changed event'''
        if self.positionChangedEventCallback is not None:
            self.positionChangedEventCallback(
                self.player.get_media_player().get_time() # Current position in ms
            )

    @property
    def mrls(self) -> tuple[str, ...]:
        '''Media ressource locators of the current playlist'''
        return self._mrls

    @mrls.setter
    def mrls(self, mrls: tuple[str, ...] = None) -> None:
        '''Loads a new playlist'''
        self._mrls = mrls
        self.player.set_media_list(MediaList(self._mrls))

    @property
    def isPlaying(self) -> bool:
        '''Playing state'''
        return True if self.player.get_state() == State.Playing else False

    @property
    def isBusy(self) -> bool:
        '''Busy state'''
        currentState = self.player.get_state()
        return True if currentState == State.Opening or currentState == State.Buffering else False

    @property
    def isFailed(self) -> bool:
        '''Failing state'''
        return True if self.player.get_state() == State.Error else False

    def play(self) -> None:
        '''Play action'''
        self.player.play()

    def pause(self) -> None:
        '''Pause action'''
        self.player.pause()

    def stop(self) -> None:
        '''Stop action'''
        self.player.stop()

    def nextTrack(self) -> None:
        '''Next track action'''
        self.player.next()

    def previousTrack(self) -> None:
        '''Previous track action'''
        self.player.previous()

# Usage example

playlist = [
    "https://www.youtube.com/watch?v=6qEzh3wKVJc",
    "https://www.youtube.com/watch?v=UfVF3NWzeAY"
]

def onTrackChanged(title: str, artist: str, description: str, URL: str, artURL: str) -> None:
    '''Print track infos'''
    print(artist, " - ", title)
    print(description)
    print(artURL)
    print(URL)

def onPositionChanged(currentPosition: float) -> None:
    '''Print current position'''
    print(
        str(timedelta(
            seconds=currentPosition / 1000
        )).split(".")[0]
    )

musicPlayer = MusicPlayer(
    None,
    "--no-ts-trust-pcr --ts-seek-percent --no-video -q",
    onTrackChanged,
    onPositionChanged
)
musicPlayer.mrls = playlist
musicPlayer.play()

while musicPlayer.isPlaying or musicPlayer.isBusy:
    sleep(1) # Keeps this thread waiting until the music ends
