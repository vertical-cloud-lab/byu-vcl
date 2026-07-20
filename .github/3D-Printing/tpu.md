# 3D Printing Using TPU
## Bambu Studio
1. In Bambu Studio, select the three dots next to the TPU filament and edit to the following presets (with the orange reset symbol next to them):
   *    <img width="503" height="350" alt="Screenshot 2026-07-20 151310" src="https://github.com/user-attachments/assets/590b220d-e647-41f3-90ce-f51c2e98be72" />
   
   *    This causes better adhesion when printing small, vertical prints, minimizing 'wobble.'
1. If printing a tall, thin, or small object, make sure to generate a raft in Bambu Studio before slicing or use the Bambu Glue Stick on the print plate for better adhesion.
### Support Settings
1. If necessary, paint manual supports onto each part (MANUAL SUPPORTS VIDEO HERE).
1. If printing a tall object with thin TPU elements, make sure to set support filament to PLA only (this will prevent wobbling during printing).
   Also, DENY any suggested preset adjustments from Bambu Studio that come from this decision:
   *    <img width="503" height="361" alt="Screenshot 2026-07-20 153644" src="https://github.com/user-attachments/assets/5e43e539-7391-4a15-8d03-c649f3a26070" />

1. Additionally, make sure to disable flushing TPU into supports:
   *    <img width="502" height="457" alt="Screenshot 2026-07-20 153945" src="https://github.com/user-attachments/assets/d8b73905-b70e-4154-be7b-97834b1b2476" />

1. Make sure to select 'On build plate only,' so supports are not built on the object being printed unless there is no other option.

## Preparing the 3D Printer
1. If humidity is not below 8%, run a TPU dry cycle at 70-75&deg;C for 12hr or until below 8% humidity.
1. Clean Nozzle(s)
   *    Note: To switch active nozzle, click 'right' or 'left' on 3D printer, then wait for it to switch.
   *    Remove Heat Cover
   *    Heat Nozzle to 180&deg;C
   *    Use razor and paper towels to peel and wipe gummy material off nozzle. CAUTION: The nozzle is HOT; take care to avoid burns.
   *    Cool Nozzle to 0&deg;C
   *    Replace Heat Cover
1. Load the TPU (Make sure to do this step even if the TPU is already loaded; this prevents clogs.)
   *    On the 3D printer, select the roll of TPU and click "Load." Wait for the prompt to push the filament into the extruder.
   *    If TPU not loaded AND using TPU assist module:
        -    Feed the TPU through the loading tube at the back of the TPU AMS system until TPU touches the feed area of the TPU assist module.
        -    Press the right button to automatically feed the TPU down the tube and into the extruder.
   *    If TPU not loaded:
        -    Hand feed the TPU through the hole at the back of the printer labeled for TPU, through the loops where a PTFE tube normally sits, and push into the extruder.
        -    If extruder does not automatically sense filament and begin feeding, select 'Finished, continue."
   *    Else (if TPU is already loaded):
        -    Pass
   *    Follow any remaining instructions on the printer.
1. Brush any leftover filament purge from previous print jobs out of the waste chute.
1. Finally, slice and print the file like normal.

## Notes & Troubleshooting:
1. If the prints have too many bubbles, this is a humidity issue. Try printing at a drier temperature.
2. For thinner prints, if there appears to be 'wobble' in the print when using 100% PLA supports, this can usually be remedied by the TPU filament preset changes.
   When the min and max temperatures are too far apart, there can be 'skipping,' which causes wobble between 3D print layers as the filament takes extra time to adhere and misses the target point of adhesion.



