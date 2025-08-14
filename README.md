DecodePMTSDReq_FD: Decode the request from the W100 for a PMTSD command to be sent from the coordinator to the W100.
DecodePMTSD_FD: Decode the PMTSD commands sent from the W100 to the coordinator.
DecodePMTSD_TD: Decode the PMTSD commands sent from the coordinator to the W100.
GenerateHVACOff_TD: Generate the command to disable HVAC mode on the W100.
GenerateHVACOn_TD: Generate the command to enable HVAC mode on the W100.
GeneratePMTSD_TD: Generate the command to update the PMTSD values on the W100.

In the context of what may be hardcoded into these very crappy scripts, the IEEE addresses are as follows:
    W100 (TH-S04D): 54:EF:44:10:01:2D:D6:31
    Coordinator/Hub: 54:EF:44:80:71:1A

I have not seen any issue with reusing the IEEE address above. It was the IEEE of the Aqara hub I did testing with. Using that IEEE to send commands from my SLZB worked just fine. YMMV.

P: Power
    P=0 (Thermostat On)
    P=1 (Thermostat Off)
M: Mode
    M=0 (Cooling)
    M=1 (Heating)
    M=2 (Auto)
T: Temperature (Set Point)
    Values are in Celsius. Despite the display showing 0.5 degree increments, I have only seen it reported as a whole number.
S: Speed (Fan Speed)
    S=0 (Fan Auto)
    S=1 (Fan Low)
    S=2 (Fan Medium)
    S=3 (Fan High)
D: Unknown. Values below have been observed with no obvious changes in behvior. Will eventually see if I can figure this out, but it doesn't seem to be breaking.
    D=0
    D=1

To Use With Home Assistant:
These files allow you to use the W100 in thermostat mode via zigbee2mqtt and Home Assistant. Note: I manually created the input helpers, automations and scripts. Hopefully I didn't make any errors when transposing them to combined YAMLs. The individual YAML files are located in their respective folders.

   1. Place lumi.sensor_ht.agl001.js in your /zigbee2mqtt/external_converters folder.
   2. Place pmtsd.yaml into HA's config folder and add the following line to configuration.yaml input_number: !include pmtsd_helpers.yaml
   3. Place w100_automatons.yaml into HA's config folder and add the following line to configuration.yaml automation: !include w100_automations.yaml
   4. Place w100_scripts.yaml into HA's config folder and add the following line to configuration.yaml scripts: !inclue w100_scripts.yaml
   5. Make some edits to w100_automations and w100_scripts to enter in your entity names, etc. I will write this up better later.
   6. Reboot HA
   7. Use the W100. I will write this up better later as well.


