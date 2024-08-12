"""Constants for the Hitachi Projector integration."""

from libhitachiprojector.hitachiprojector import Command, InputSource, PowerStatus

from homeassistant.components.media_player.const import MediaPlayerState

DOMAIN = "hitachiprojector"

POWER_STATUS_TO_MEDIA_PLAYER_STATE = {
    PowerStatus.On: MediaPlayerState.ON,
    PowerStatus.Off: MediaPlayerState.OFF,
    PowerStatus.CoolDown: MediaPlayerState.OFF,
}

SOURCE_TO_SET_COMMAND = {
    InputSource.ComputerIn1.name: Command.InputSourceComputerIn1,
    InputSource.ComputerIn2.name: Command.InputSourceComputerIn2,
    InputSource.HDMI.name: Command.InputSourceHDMI,
    InputSource.Component.name: Command.InputSourceComponent,
    InputSource.SVideo.name: Command.InputSourceSVideo,
    InputSource.Video.name: Command.InputSourceVideo,
    InputSource.USBTypeA.name: Command.InputSourceUSBTypeA,
    InputSource.LAN.name: Command.InputSourceLAN,
    InputSource.USBTypeA.name: Command.InputSourceUSBTypeA,
}
