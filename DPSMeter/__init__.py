from unrealsdk import *
from Mods import ModMenu

from time import time
from typing import Sequence, Any

import locale
locale.setlocale(locale.LC_ALL, '')


_state: int = 0
_start_epoch: float = 0.0
_tick_epoch: float = 0.0
_total_damage: float = 0.0


def _show_hud(message: Any) -> None:
    PC = GetEngine().GamePlayers[0].Actor
    HUD = PC.GetHUDMovie()
    if HUD is None:
        RemoveHook("WillowGame.WillowPawn.AdjustDamage", "DPSMeter")
        RemoveHook("WillowGame.WillowPlayerController.PlayerTick", "DPSMeter")
        global _state
        _state = 0

    else: HUD.AddTrainingText(
        MessageString = str(message),
        TitleString = "DPS Meter",
        Duration = float('inf'),
        DrawColor = (),
        HUDInitializationFrame = "",
        PausesGame = False,
        PauseContinueDelay = 0,
        Related_PRI1 = PC.PlayerReplicationInfo,
        bIsntActuallyATrainingMessage = True
    )

def _hide_hud() -> None:
    GetEngine().GamePlayers[0].Actor.GetHUDMovie().ClearTrainingText()


def _update_hud() -> None:
    global _tick_epoch
    _tick_epoch = time()

    dps = _total_damage / (_tick_epoch - _start_epoch)

    _show_hud(f"Tracking DPS: {round(dps):n}")


def _player_tick(caller: UObject, function: UFunction, params: FStruct) -> bool:
    # global _tick_epoch

    # current_time = time()
    # if (current_time - _tick_epoch) >= 1:
    #     _tick_epoch = current_time
    #     _update_hud()

    _update_hud()
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

    _update_hud()

    return True


class DPSMeter(ModMenu.SDKMod):
    Name: str = "DPS Meter"
    Version: str = "1.0"
    Description: str = "Provides means of estimating damage dealt per second."
    Author: str = "mopioid"
    Types: ModMenu.ModTypes = ModMenu.ModTypes.Utility

    SaveEnabledState: ModMenu.EnabledSaveType = ModMenu.EnabledSaveType.LoadOnMainMenu


    Keybinds: Sequence[ModMenu.Keybind] = [ModMenu.Keybind("Start/Stop Acculmulator")]

    def GameInputPressed(self, keybind: ModMenu.Keybind) -> None:
        global _state, _start_epoch, _tick_epoch, _total_damage

        if _state == 0:
            _start_epoch = _tick_epoch = time()
            _total_damage = 0.0
            _show_hud(0)

            RunHook("WillowGame.WillowPawn.AdjustDamage", "DPSMeter", _adjust_damage)
            RunHook("WillowGame.WillowPlayerController.PlayerTick", "DPSMeter", _player_tick)

            _state = 1

        elif _state == 1:
            RemoveHook("WillowGame.WillowPawn.AdjustDamage", "DPSMeter")
            RemoveHook("WillowGame.WillowPlayerController.PlayerTick", "DPSMeter")

            elapsed_seconds = time() - _start_epoch
            dps = _total_damage / elapsed_seconds

            _show_hud(
                f"Dealt {round(_total_damage):n} damage "
                f"over {round(elapsed_seconds):n} seconds "
                f"(average {round(dps):n} DPS)"
            )

            _state = 2

        else:
            _hide_hud()

            _state = 0


    def Enable(self) -> None:
        super().Enable()

        global _state, _start_epoch, _tick_epoch, _total_damage
        _state = 0
        _start_epoch = 0.0
        _tick_epoch = 0.0
        _total_damage = 0.0

 
    def Disable(self) -> None:
        super().Disable()

        RemoveHook("WillowGame.WillowPawn.AdjustDamage", "DPSMeter")
        RemoveHook("WillowGame.WillowPlayerController.PlayerTick", "DPSMeter")


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
