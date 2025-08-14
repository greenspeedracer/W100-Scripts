const {Zcl} = require("zigbee-herdsman");
const fz = require("zigbee-herdsman-converters/converters/fromZigbee");
const tz = require("zigbee-herdsman-converters/converters/toZigbee");
const exposes = require("zigbee-herdsman-converters/lib/exposes");
const { logger } = require("zigbee-herdsman-converters/lib/logger");
const lumi = require("zigbee-herdsman-converters/lib/lumi");
const m = require("zigbee-herdsman-converters/lib/modernExtend");

const e = exposes.presets;
const ea = exposes.access;

const {
    lumiAction,
    lumiZigbeeOTA,
    lumiExternalSensor,
} = lumi.modernExtend;

const NS = "zhc:lumi";
const manufacturerCode = lumi.manufacturerCode;

const W100_0844_req = {
    cluster: 'manuSpecificLumi',
    type: ['attributeReport', 'readResponse'],
    convert: (model, msg, publish, options, meta) => {
        const attr = msg.data[65522];
        if (!attr || !Buffer.isBuffer(attr)) return;

        const endsWith = Buffer.from([0x08, 0x00, 0x08, 0x44]);
        if (attr.slice(-4).equals(endsWith)) {
            meta.logger.info(`Detected PMTSD request from device ${meta.device.ieeeAddr}`);
            return { action: 'W100_PMTSD_request' };
        }
    },
};

const PMTSD_to_W100 = {
        key: ['PMTSD_to_W100'],
        convertSet: async (entity, key, value, meta) => {
            const { P, M, T, S, D } = value;

            const pmtsdStr = `P${P}_M${M}_T${T}_S${S}_D${D}`;
            const pmtsdBytes = Array.from(pmtsdStr).map(c => c.charCodeAt(0));
            const pmtsdLen = pmtsdBytes.length;

            const fixedHeader = [
                0xAA, 0x71, 0x1F, 0x44,
                0x00, 0x00, 0x05, 0x41, 0x1C,
                0x00, 0x00,
                0x54, 0xEF, 0x44, 0x80, 0x71, 0x1A,
                0x08, 0x00, 0x08, 0x44, pmtsdLen,
            ];

            const counter = Math.floor(Math.random() * 256);
            fixedHeader[4] = counter;

            const fullPayload = [...fixedHeader, ...pmtsdBytes];

            const checksum = fullPayload.reduce((sum, b) => sum + b, 0) & 0xFF;
            fullPayload[5] = checksum;

            await entity.write(
                64704,
                { 65522: { value: Buffer.from(fullPayload), type: 65 } },
                { manufacturerCode: 4447, disableDefaultResponse: true },
            );

            logger.info(`PMTSD frame sent: ${pmtsdStr} (Counter: ${counter}, Checksum: ${checksum})`);
            return{};
        },
};

const PMTSD_from_W100 = {
    cluster: 'manuSpecificLumi',
    type: ['attributeReport', 'readResponse'],
    convert: (model, msg, publish, options, meta) => {
        const data = msg.data[65522];
        if (!data || !Buffer.isBuffer(data)) return;

        const endsWith = Buffer.from([0x08, 0x44]);
        const idx = data.indexOf(endsWith);
        if (idx === -1 || idx + 2 >= data.length) return;

        const payloadLen = data[idx + 2];
        const payloadStart = idx + 3;
        const payloadEnd = payloadStart + payloadLen;

        if (payloadEnd > data.length) return;

        const payloadBytes = data.slice(payloadStart, payloadEnd);
        let payloadAscii;
        try {
            payloadAscii = payloadBytes.toString('ascii');
        } catch {
            return;
        }

        const result = {};
        const partsForCombined = [];
        const pairs = payloadAscii.split('_');
        pairs.forEach(p => {
            if (p.length >= 2) {
                const key = p[0];
                const value = p.slice(1);
                let newKey;
                switch(key) {
                    case 'p': newKey = 'PW'; break;
                    case 'm': newKey = 'MW'; break;
                    case 't': newKey = 'TW'; break;
                    case 's': newKey = 'SW'; break;
                    case 'd': newKey = 'DW'; break;
                    default: newKey = key.toUpperCase() + 'W';
            }
            result[newKey] = value;
            partsForCombined.push(`${newKey}${value}`);
            }
        });
        const ts = Date.now();
        const combinedString = partsForCombined.length
            ? `${ts}_${partsForCombined.join('_')}`
            : `${ts}`;

        meta.logger.info(`Decoded PMTSD: ${JSON.stringify(result)} from ${meta.device.ieeeAddr}`);
        return { 
                ...result,
                PMTSD_from_W100_Data: combinedString
        };
    },
};

const Thermostat_Mode = {
    key: ['Thermostat_Mode'],
    convertSet: async (entity, key, value, meta) => {
        const deviceMac = meta.device.ieeeAddr.replace(/^0x/, '').toLowerCase();
        const hubMac = '54ef4480711a';
        function cleanMac(mac, expectedLen) {
            const cleaned = mac.replace(/[:\-]/g, '');
            if (cleaned.length !== expectedLen) {
                throw new Error(`MAC must be ${expectedLen} hex digits`);
            }
            return cleaned;
        }

        const dev = Buffer.from(cleanMac(deviceMac, 16), 'hex');
        const hub = Buffer.from(cleanMac(hubMac, 12), 'hex');

        let frame;

        if (value === 'ON') {
            const prefix = Buffer.concat([
                Buffer.from('aa713244', 'hex'),
                Buffer.from([Math.floor(Math.random() * 256), Math.floor(Math.random() * 256)])
            ]);
            const zigbeeHeader = Buffer.from('02412f6891', 'hex');
            const messageId = Buffer.from([Math.floor(Math.random() * 256), Math.floor(Math.random() * 256)]);
            const control = Buffer.from([0x18]);
            const payloadMacs = Buffer.concat([dev, Buffer.from('0000', 'hex'), hub]);
            const payloadTail = Buffer.from('08000844150a0109e7a9bae8b083e58a9f000000000001012a40', 'hex');

            frame = Buffer.concat([prefix, zigbeeHeader, messageId, control, payloadMacs, payloadTail]);

        } else {
            const prefix = Buffer.from([
                0xaa, 0x71, 0x1c, 0x44, 0x69, 0x1c,
                0x04, 0x41, 0x19, 0x68, 0x91
            ]);
            const frameId = Buffer.from([Math.floor(Math.random() * 256)]);
            const seq    = Buffer.from([Math.floor(Math.random() * 256)]);
            const control = Buffer.from([0x18]);

            frame = Buffer.concat([prefix, frameId, seq, control, dev]);
            if (frame.length < 34) {
                frame = Buffer.concat([frame, Buffer.alloc(34 - frame.length, 0x00)]);
            }
        }
        await entity.write(
            64704,
            { 65522: { value: frame, type: 0x41 } },
            { manufacturerCode: 4447, disableDefaultResponse: true },
        );

        logger.info(`Thermostat_Mode=${value} payload=${frame.toString('hex')}`);
        return {};
    },
};

module.exports = {
    zigbeeModel: ["lumi.sensor_ht.agl001"],
    model: "TH-S04D",
    vendor: "Aqara",
    description: "Climate Sensor W100",
    fromZigbee: [W100_0844_req, PMTSD_from_W100],
    toZigbee: [PMTSD_to_W100, Thermostat_Mode],
    exposes: [ e.action(['W100_PMTSD_request']).withDescription('W100 Requesting PMTSD Data via 08000844 Request'),
               e.text('PMTSD_from_W100_Data', ea.STATE).withDescription('Timestamp+Most Recent PMTSD Values Sent by W100'),
               e.binary('Thermostat_Mode', ea.ALL, 'ON', 'OFF').withDescription('On: Enable thermostat mode. Buttons send encrypted payloads and middle line is enabled. Off: Disable thermostat mode. Buttons send actions and middle line is disabled.')],
    extend: [
        lumiZigbeeOTA(),
        m.temperature(),
        m.humidity(),
        lumiExternalSensor(),
        m.deviceEndpoints({endpoints: {plus: 1, center: 2, minus: 3}}),
        lumiAction({
            actionLookup: {hold: 0, single: 1, double: 2, release: 255},
            endpointNames: ["plus", "center", "minus"],
        }),
        m.binary({
            name: "Auto_Hide_Middle_Line",
            cluster: "manuSpecificLumi",
            attribute: {ID: 0x0173, type: Zcl.DataType.BOOLEAN},
            valueOn: [true, 0],
            valueOff: [false, 1],
            description: "Only applies when thermostat mode is enabled. True: Hides middle line after 30 seconds of inactivity. False: Always displays middle line.",
            access: "ALL",
            entityCategory: "config",
            zigbeeCommandOptions: {manufacturerCode},
            reporting: false,
        }),
        m.numeric({
            name: "high_temperature",
            valueMin: 26,
            valueMax: 60,
            valueStep: 0.5,
            scale: 100,
            unit: "°C",
            cluster: "manuSpecificLumi",
            attribute: {ID: 0x0167, type: Zcl.DataType.INT16},
            description: "High temperature alert",
            zigbeeCommandOptions: {manufacturerCode},
        }),
        m.numeric({
            name: "low_temperature",
            valueMin: -20,
            valueMax: 20,
            valueStep: 0.5,
            scale: 100,
            unit: "°C",
            cluster: "manuSpecificLumi",
            attribute: {ID: 0x0166, type: Zcl.DataType.INT16},
            description: "Low temperature alert",
            zigbeeCommandOptions: {manufacturerCode},
        }),
        m.numeric({
            name: "high_humidity",
            valueMin: 65,
            valueMax: 100,
            valueStep: 1,
            scale: 100,
            unit: "%",
            cluster: "manuSpecificLumi",
            attribute: {ID: 0x016e, type: Zcl.DataType.INT16},
            description: "High humidity alert",
            zigbeeCommandOptions: {manufacturerCode},
        }),
        m.numeric({
            name: "low_humidity",
            valueMin: 0,
            valueMax: 30,
            valueStep: 1,
            scale: 100,
            unit: "%",
            cluster: "manuSpecificLumi",
            attribute: {ID: 0x016d, type: Zcl.DataType.INT16},
            description: "Low humidity alert",
            zigbeeCommandOptions: {manufacturerCode},
        }),
        m.enumLookup({
            name: "sampling",
            lookup: {low: 1, standard: 2, high: 3, custom: 4},
            cluster: "manuSpecificLumi",
            attribute: {ID: 0x0170, type: Zcl.DataType.UINT8},
            description: "Temperature and Humidity sampling settings",
            zigbeeCommandOptions: {manufacturerCode},
        }),
        m.numeric({
            name: "period",
            valueMin: 0.5,
            valueMax: 600,
            valueStep: 0.5,
            scale: 1000,
            unit: "sec",
            cluster: "manuSpecificLumi",
            attribute: {ID: 0x0162, type: Zcl.DataType.UINT32},
            description: "Sampling period",
            zigbeeCommandOptions: {manufacturerCode},
        }),
        m.enumLookup({
            name: "temp_report_mode",
            lookup: {no: 0, threshold: 1, period: 2, threshold_period: 3},
            cluster: "manuSpecificLumi",
            attribute: {ID: 0x0165, type: Zcl.DataType.UINT8},
            description: "Temperature reporting mode",
            zigbeeCommandOptions: {manufacturerCode},
        }),
        m.numeric({
            name: "temp_period",
            valueMin: 1,
            valueMax: 10,
            valueStep: 1,
            scale: 1000,
            unit: "sec",
            cluster: "manuSpecificLumi",
            attribute: {ID: 0x0163, type: Zcl.DataType.UINT32},
            description: "Temperature reporting period",
            zigbeeCommandOptions: {manufacturerCode},
        }),
        m.numeric({
            name: "temp_threshold",
            valueMin: 0.2,
            valueMax: 3,
            valueStep: 0.1,
            scale: 100,
            unit: "°C",
            cluster: "manuSpecificLumi",
            attribute: {ID: 0x0164, type: Zcl.DataType.UINT16},
            description: "Temperature reporting threshold",
            zigbeeCommandOptions: {manufacturerCode},
        }),
        m.enumLookup({
            name: "humi_report_mode",
            lookup: {no: 0, threshold: 1, period: 2, threshold_period: 3},
            cluster: "manuSpecificLumi",
            attribute: {ID: 0x016c, type: Zcl.DataType.UINT8},
            description: "Humidity reporting mode",
            zigbeeCommandOptions: {manufacturerCode},
        }),
        m.numeric({
            name: "humi_period",
            valueMin: 1,
            valueMax: 10,
            valueStep: 1,
            scale: 1000,
            unit: "sec",
            cluster: "manuSpecificLumi",
            attribute: {ID: 0x016a, type: Zcl.DataType.UINT32},
            description: "Humidity reporting period",
            zigbeeCommandOptions: {manufacturerCode},
        }),
        m.numeric({
            name: "humi_threshold",
            valueMin: 2,
            valueMax: 10,
            valueStep: 0.5,
            scale: 100,
            unit: "%",
            cluster: "manuSpecificLumi",
            attribute: {ID: 0x016b, type: Zcl.DataType.UINT16},
            description: "Humidity reporting threshold",
            zigbeeCommandOptions: {manufacturerCode},
        }),
        m.identify(),
    ],
};
