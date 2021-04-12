# Borderlands DPS Meter

Provides means of estimating damage dealt per second in Borderlands 2 and Borderlands: The Pre-Sequel.

![DPS Meter](https://i.imgur.com/3Rdo98V.png)

Borderlands DPS Meter offers two modes of estimating DPS. Each can be activated via a hotkey, configured via OPTIONS > KEYBOARD/MOUSE > MODDED KEY BINDINGS > DPS Meter.

In "continuous" mode, a simple widget is displayed in the HUD that shows the average DPS over the last three seconds (or a different number of seconds configured via OPTIONS > MODS > DPS Meter > Continuous Time Window).

In "accumulator" mode, DPS Meter starts recording all damage done until it is told to stop. It displays a widget featuring the running time, the total damage dealt, and the resulting average DPS.

### Installation

1. Begin by [downloading the latest version of Borderlands DPS Meter.](https://github.com/mopioid/Borderlands-DPS-Meter/archive/main.zip)

2. [Install UnrealEngine PythonSDK](https://github.com/bl-sdk/PythonSDK#installation) if you have not already.

3. Locate the SDK's `Mods` folder (located in the `Win32` folder of the `Binaries` folder of your BL2/TPS installation).

4. Copy the `DPSMeter` folder from `Borderlands-DPS-Meter-main.zip` to the SDK's `Mods` folder.

5. Launch the game, select "Mods" from the main menu, then select "DPS Meter" to enable it.

6. From the main menu, navigate to OPTIONS > KEYBOARD/MOUSE > MODDED KEY BINDINGS, and configure keybindings for Continuous and Accumulator mode as desired.
