"""Philips TV support"""
import logging
from datetime import timedelta

import json
import requests

import voluptuous as vol

import homeassistant.util as util
from homeassistant.components.media_player import (
    PLATFORM_SCHEMA,
    SUPPORT_TURN_ON,
    SUPPORT_TURN_OFF,
    # SUPPORT_SELECT_SOURCE,
    SUPPORT_PREVIOUS_TRACK,
    SUPPORT_NEXT_TRACK,
    SUPPORT_VOLUME_MUTE,
    SUPPORT_VOLUME_STEP,
    MediaPlayerDevice
)
from homeassistant.const import (
    STATE_UNKNOWN,
    STATE_OFF,
    STATE_ON,
    CONF_NAME,
    CONF_HOST,
    CONF_ACCESS_TOKEN
)
from homeassistant.helpers import config_validation as cv

_LOGGER = logging.getLogger(__name__)

ICON = 'mdi:television'
DEFAULT_NAME = 'Philips TV'
DEVICE_NAME = 'Philips TV Control'
DEVICE_ID = 'philips_tv'
MIN_TIME_BETWEEN_SCANS = timedelta(seconds=10)
MIN_TIME_BETWEEN_FORCED_SCANS = timedelta(seconds=1)
SUPPORTED_COMMANDS = SUPPORT_TURN_ON | SUPPORT_TURN_OFF \
                     | SUPPORT_NEXT_TRACK | SUPPORT_PREVIOUS_TRACK \
                     | SUPPORT_VOLUME_MUTE | SUPPORT_VOLUME_STEP

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_HOST): cv.string,
    vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
})


def setup_platform(hass, config, add_devices, discovery_info=None):
    host = config.get(CONF_HOST)
    if host is None:
        _LOGGER.error('No host info')
        return False
    name = config.get(CONF_NAME)

    add_devices([PhilipsTV(host, name)], True)

def get_command(host, path):
    try:
        r = requests.get("http://" + host + ":1925/" + path, verify=False, timeout=3)
        # print(r)
        # print(r.url)
        # print(r.text)
        r.raise_for_status()

        return r.json()

    except requests.exceptions.HTTPError as errh:
        return {"error": "HTTPError"}
    except requests.exceptions.ConnectionError as errc:
        return {"error": "ConnectionError"}
    except requests.exceptions.Timeout as errt:
        return {"error": "Timeout"}
    except requests.exceptions.RequestException as err:
        return {"error": "RequestException"}

def post_command(host, path, body):
    try:
        r = requests.post("http://" + host + ":1925/" + path, json=body, verify=False, timeout=3)
        r.raise_for_status()
    except requests.exceptions.HTTPError as errh:
        return {"error": "HTTPError"}
    except requests.exceptions.ConnectionError as errc:
        return {"error": "ConnectionError"}
    except requests.exceptions.Timeout as errt:
        return {"error": "Timeout"}
    except requests.exceptions.RequestException as err:
        return {"error": "RequestException"}
    # print(r)

def post_key(host, key):
	post_command(host, "6/input/key", { "key" : key })

class PhilipsTV(MediaPlayerDevice):
    def __init__(self, host, name):
        import pyvizio
        self._host = host
        self._device = None
        self._name = name
        self._state = STATE_UNKNOWN
        self._volume_level = None
        self._current_input = None
        self._available_inputs = None

    @util.Throttle(MIN_TIME_BETWEEN_SCANS, MIN_TIME_BETWEEN_FORCED_SCANS)
    def update(self):

    	if( 'error' in get_command(self._host, '6/powerstate')):
    		self._state = STATE_UNKNOWN
    		return
    	else:
            # powerstate = 
            is_on = True if get_command(self._host, '6/powerstate')['powerstate'] == "On" else False
            if is_on is None:
                self._state = STATE_UNKNOWN
                return
            elif is_on is False:
                self._state = STATE_OFF
            else:
                self._state = STATE_ON

            # volume = True if get_command(self._host, '6/powerstate')['powerstate'] == "On" else False
            self._volume_level = get_command(self._host, '6/audio/volume')['current']
            # input_ = self._device.get_current_input()
            # if input_ is not None:
            #     self._current_input = input_.meta_name
            # inputs = self._device.get_inputs()
            # if inputs is not None:
            #     self._available_inputs = []
            #     for input_ in inputs:
            #         self._available_inputs.append(input_.name)

    @property
    def state(self):
        return self._state

    @property
    def name(self):
        return self._name

    @property
    def volume_level(self):
        return self._volume_level

    @property
    def source(self):
        return self._current_input

    @property
    def source_list(self):
        return self._available_inputs

    @property
    def supported_features(self):
        return SUPPORTED_COMMANDS

    def turn_on(self):
        # self._device.pow_on()
        post_key(self._host, "Standby")

    def turn_off(self):
    	post_key(self._host, "Standby")
        # self._device.pow_off()

    def mute_volume(self, mute):
        post_key(self._host, "Mute")
        if mute:
        	mute = False
        	# post_key(self.host, "Mute")
            # self._device.mute_on()
        else:
        	mute = True
        	# post_key(self.host, "Standby")
            # self._device.mute_off()

    def media_previous_track(self):
        # self._device.ch_down()
        post_key(self._host, "Previous")

    def media_next_track(self):
        # self._device.ch_up()
        post_key(self._host, "Next")

    # def select_source(self, source):
    #     self._device.input_switch(source)

    def volume_up(self):
    	post_key(self._host, "VolumeUp")
        # self._device.vol_up()

    def volume_down(self):
    	post_key(self._host, "VolumeDown")
        # self._device.vol_down()