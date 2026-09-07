# Kevin Corporate Goblin — Production Rig

1. Extract the ZIP into a new folder.
2. Install Python from python.org and enable **Add Python to PATH** if it is not already installed.
3. Double-click `START-KEVIN.bat`.
4. In the control page, click **Enable microphone**, approve access, and calibrate the layers. Changes save automatically.
5. In OBS, add a Browser source using `http://localhost:8877/?obs=1` at 1280 by 1280.
6. Add a Chroma Key filter using custom color `#FF00FF`.

## Improvements in this build

- Clean five-file artwork set: base, eyes, typing hand, resting mouse-hand, and visibly pressed mouse-hand.
- Event-driven typing: the hand remains completely still at rest, performs one short anchored tap for each keyboard event, and immediately returns to its exact resting pose.
- Windows uses direct operating-system input polling. Typing and clicking are controlled only by physical input counters; neither animation has an idle timer.
- The control page shows the active input backend plus live key and click counts for immediate troubleshooting.
- Redesigned compact, low-profile charcoal office keyboard with cleaner desk perspective and open mouse space.
- Smooth mouse acceleration, deceleration, and directional movement, with a dedicated pressed-finger frame for clicks.
- Closed, slight, and wide microphone-driven mouth states.
- Microphone analysis runs on the browser audio thread, so switching focus to OBS or a game no longer throttles mouth capture.
- Voice packets include a heartbeat and expire safely; a disconnected control page cannot leave the mouth stuck open.
- Mouth hysteresis and a short 150 ms syllable hold prevent dropped consonants and rapid open/closed flicker.
- Smooth four-stage blinking.
- Saved X/Y/size controls for the hands and mouth, plus typing tap distance, voice sensitivity, and mouse range.
- Calibration is a selectable on/off mode; its sliders, individual test buttons, typing tap distance, and reset button stay hidden when calibration is off.
- Calibration changes are relayed through the local server so the OBS source updates live even though OBS and Chrome use separate browser storage.
- Calibration settings are saved in `settings.json`, so they survive server and browser restarts.
- Real mouse-button input and the click test use the same pronounced mouse-hand press animation.
- Mouse clicks now swap to a dedicated pressed-finger artwork frame instead of relying on a barely visible scale effect.
- The keyboard is oriented from Kevin's side: its long spacebar faces him, while the keyboard itself sits forward toward the viewer.
- The magenta background fills the complete OBS browser canvas while Kevin remains proportionally aligned inside his square rig.
- No wife or children background animations.
- No input text or audio is recorded.

Keep the normal control page open after enabling the microphone so it can relay voice levels to the OBS page. The live status line should change from `voice waiting` to `voice linked`.

This production build intentionally uses port `8877`, not the older overlay's port `8765`. This prevents an old Kevin command window from serving the wrong interface. The correct control page is titled **Kevin Rig Controls** and does not contain family-interruption settings.

## Input check

The control page displays the input backend and live `keys` and `clicks` counters. Those counters should increase only when you physically type or click. If a game is running as administrator and its input is not detected, close Kevin and run `START-KEVIN.bat` at the same privilege level as the game.

The buttons inside calibration mode are deliberate visual tests. They do not indicate captured computer input and cannot run while calibration is hidden.
