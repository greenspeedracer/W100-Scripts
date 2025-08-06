DecodePMTSDReq_FD: Decode the request from the W100 for a PMTSD command to be sent from the coordinator to the W100.

DecodePMTSD_FD: Decode the PMTSD commands sent from the W100 to the coordinator.

DecodePMTSD_TD: Decode the PMTSD commands sent from the coordinator to the W100.

GenerateHVACOff_TD: Generate the command to disable HVAC mode on the W100.

GenerateHVACOn_TD: Generate the command to enable HVAC mode on the W100.

GeneratePMTSD_TD: Generate the command to update the PMTSD values on the W100.

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

D: Display? Unknown. (Possibly "Auto Display Off," which is supposed to turn the "middle row" HVAC display off after some set period of time. Values below have been observed with no obvious changes in behvior)
    D=0
    D=1
