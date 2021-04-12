from unrealsdk import *
from Mods import ModMenu

import enum
from math import inf
from collections import deque
from typing import Any, Deque, List, Sequence

import locale
locale.setlocale(locale.LC_ALL, '')


class _State(enum.Enum):
    OFF = enum.auto()
    CONTINUOUS = enum.auto()
    ACCULMULATOR_STARTED = enum.auto()
    ACCULMULATOR_STOPPED = enum.auto()

_state: _State = _State.OFF


_start_epoch: float
_total_damage: float
_tick_epochs: Deque[float]
_tick_totals: Deque[float]


def _reset() -> None:
    global _start_epoch, _total_damage, _tick_epochs, _tick_totals
    _start_epoch = GetEngine().GetCurrentWorldInfo().TimeSeconds
    _total_damage = 0.0
    _tick_epochs = deque()
    _tick_totals = deque()

    RemoveHook("WillowGame.WillowPawn.AdjustDamage", "DPSMeter")
    RemoveHook("WillowGame.WillowPlayerController.PlayerTick", "DPSMeter")


def _show_hud(message: str) -> None:
    PC = GetEngine().GamePlayers[0].Actor

    HUD = PC.GetHUDMovie()
    if HUD is None:
        _reset()

        global _state
        _state = _State.OFF

    else: HUD.AddTrainingText(
        MessageString = message,
        TitleString = "DPS Meter",
        Duration = inf,
        DrawColor = (),
        HUDInitializationFrame = "",
        PausesGame = False,
        PauseContinueDelay = 0,
        Related_PRI1 = PC.PlayerReplicationInfo,
        bIsntActuallyATrainingMessage = True
    )


def _player_tick_continuous(caller: UObject, function: UFunction, params: FStruct) -> bool:
    global _total_damage

    current_time = GetEngine().GetCurrentWorldInfo().TimeSeconds
    _tick_epochs.append(current_time)

    _tick_totals.append(_total_damage)
    _total_damage = 0.0

    while (current_time - _tick_epochs[0]) > _continuous_option.CurrentValue:
        _tick_epochs.popleft()
        _tick_totals.popleft()

    elapsed_seconds = current_time - _tick_epochs[0] or inf

    dps = sum(_tick_totals) / elapsed_seconds
    _show_hud(f" {round(dps):n}")

    return True


def _player_tick_accumulator(caller: UObject, function: UFunction, params: FStruct) -> bool:
    elapsed_seconds = GetEngine().GetCurrentWorldInfo().TimeSeconds - _start_epoch
    _show_hud(
        f" Time: {elapsed_seconds:n} seconds\n"
        f" Damage Dealt: {round(_total_damage):n}\n"
        f" Average DPS: {round(_total_damage / elapsed_seconds):n}"
    )
    return True


def _adjust_damage(caller: UObject, function: UFunction, params: FStruct) -> bool:
    if params.InstigatedBy is not GetEngine().GamePlayers[0].Actor:
        return True

    damage, *_ = caller.AdjustDamage(
        InDamage = params.InDamage,
        DamageSeverityPercent = params.DamageSeverityPercent,
        Momentum = (
            params.Momentum.X,
            params.Momentum.Y,
            params.Momentum.Z
        ),
        InstigatedBy = params.InstigatedBy,
        HitLocation = (
            params.HitLocation.X,
            params.HitLocation.Y,
            params.HitLocation.Z
        ),
        DamageType = params.DamageType,
        HitInfo = (
            params.HitInfo.Material,
            params.HitInfo.PhysMaterial,
            params.HitInfo.Item,
            params.HitInfo.LevelIndex,
            params.HitInfo.BoneName,
            params.HitInfo.HitComponent
        ),
        DamageCauser = (
            None if params.DamageCauser is None
            else params.DamageCauser.ObjectPointer
        ),
        Pipeline = params.Pipeline
    )

    global _total_damage
    _total_damage += damage

    return True


_continuous_option = ModMenu.Options.Slider(
    Caption = "Continuous Time Window",
    Description = "The number of seconds over which DPS should be averaged in continuous mode",
    StartingValue = 3.0, MinValue = 0.5, MaxValue = 12, Increment = 0.5
)

_continuous_keybind = ModMenu.Keybind("Show/Hide Continuous Average")
_accumulator_keybind = ModMenu.Keybind("Start/Stop/Clear Accumulator")

class DPSMeter(ModMenu.SDKMod):
    Name: str = "DPS Meter"
    Version: str = "1.0"
    Description: str = "Provides means of estimating damage dealt per second."
    Author: str = "mopioid"
    Types: ModMenu.ModTypes = ModMenu.ModTypes.Utility

    SaveEnabledState: ModMenu.EnabledSaveType = ModMenu.EnabledSaveType.LoadOnMainMenu

    Options: Sequence[ModMenu.Options.Base] = [_continuous_option]

    Keybinds: Sequence[ModMenu.Keybind] = [_continuous_keybind, _accumulator_keybind]

    def GameInputPressed(self, keybind: ModMenu.Keybind) -> None:
        global _state

        if keybind is _continuous_keybind:
            if _state is _State.CONTINUOUS:
                _reset()
                GetEngine().GamePlayers[0].Actor.GetHUDMovie().ClearTrainingText()
                _state = _State.OFF

            else:
                _reset()
                RunHook("WillowGame.WillowPawn.AdjustDamage", "DPSMeter", _adjust_damage)
                RunHook("WillowGame.WillowPlayerController.PlayerTick", "DPSMeter", _player_tick_continuous)
                _state = _State.CONTINUOUS

        elif keybind is _accumulator_keybind:
            if _state is _State.ACCULMULATOR_STARTED:
                _reset()
                _state = _State.ACCULMULATOR_STOPPED

            elif _state is _State.ACCULMULATOR_STOPPED:
                GetEngine().GamePlayers[0].Actor.GetHUDMovie().ClearTrainingText()
                _state = _State.OFF

            else:
                _reset()
                RunHook("WillowGame.WillowPawn.AdjustDamage", "DPSMeter", _adjust_damage)
                RunHook("WillowGame.WillowPlayerController.PlayerTick", "DPSMeter", _player_tick_accumulator)
                _state = _State.ACCULMULATOR_STARTED


    def Enable(self) -> None:
        super().Enable()
        _reset()
 
    def Disable(self) -> None:
        super().Disable()
        _reset()


_mod_instance = DPSMeter()

if __name__ == "__main__":
    for mod in Mods:
        if mod.Name == _mod_instance.Name:
            if mod.IsEnabled:
                mod.Disable()
            Mods.remove(mod)
            _mod_instance.__class__.__module__ = mod.__class__.__module__
            break

ModMenu.RegisterMod(_mod_instance)
