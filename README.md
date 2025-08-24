DecodePMTSDReq_FD: Decode the request from the W100 for a PMTSD command to be sent from the coordinator to the W100.  
DecodePMTSD_FD: Decode the PMTSD commands sent from the W100 to the coordinator.  
DecodePMTSD_TD: Decode the PMTSD commands sent from the coordinator to the W100.  
GenerateHVACOff_TD: Generate the command to disable HVAC mode on the W100.  
GenerateHVACOn_TD: Generate the command to enable HVAC mode on the W100.  
GeneratePMTSD_TD: Generate the command to update the PMTSD values on the W100.  

In the context of what may be hardcoded into these very crappy scripts, the IEEE addresses are as follows:  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;W100 (TH-S04D): 54:EF:44:10:01:2D:D6:31  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Coordinator/Hub: 54:EF:44:80:71:1A  

I have not seen any issue with reusing the IEEE address above. It was the IEEE of the Aqara hub I did testing with. Using that IEEE to send commands from my SLZB worked just fine. YMMV.

"u16_onoff: %llu, u16_mode:%llu, u16_temp:%llu, u16_wind_speed:%llu, u16_wind_mode:%llu"

P: Power  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;P=0 (Thermostat On)  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;P=1 (Thermostat Off)  
M: Mode  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;M=0 (Cooling)  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;M=1 (Heating)  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;M=2 (Auto)  
T: Temperature (Set Point)  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Values are in Celsius. Despite the display showing 0.5 degree increments, I have only seen it reported as a whole number.  
S: Speed (Fan Speed)  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;S=0 (Fan Auto)  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;S=1 (Fan Low)  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;S=2 (Fan Medium)  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;S=3 (Fan High)  
D: "Wind Mode" I assume this is something like swing mode. I saw no change when I messed with that setting the Aqara app, but there isn't an indicator for this on the W100 anyway so it doesn't affect much.   
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;D=0  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;D=1  

To Use With Home Assistant:  
These files allow you to use the W100 in thermostat mode via zigbee2mqtt and Home Assistant. Note: I manually created the input helpers, automations and scripts. Hopefully I didn't make any errors when transposing them to combined YAMLs. The individual YAML files are located in their respective folders.  

   1. Place lumi.sensor_ht.agl001.js in your /zigbee2mqtt/external_converters folder.
   2. Place pmtsd.yaml into HA's config folder and add the following line to configuration.yaml input_number: !include pmtsd_helpers.yaml
   3. Place w100_automatons.yaml into HA's config folder and add the following line to configuration.yaml automation: !include w100_automations.yaml
   4. Place w100_scripts.yaml into HA's config folder and add the following line to configuration.yaml scripts: !inclue w100_scripts.yaml
   5. Make some edits to w100_automations and w100_scripts to enter in your entity names, etc. I will write this up better later.
   6. Reboot HA
   7. Use the W100. I will write this up better later as well.


