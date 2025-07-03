// NetFlux5G - Open5GS Subscriber Initialization Script
// This script adds default subscriber data to Open5GS MongoDB database

// Switch to open5gs database
use open5gs;

// Remove existing subscriber with same IMSI (if any)
db.subscribers.deleteMany({"imsi": "999700000000001"});

// Add default subscriber for testing
db.subscribers.insertOne({
    "imsi": "999700000000001",
    "msisdn": [],
    "imeisv": "4370816125816151",
    "mme_host": "",
    "mme_realm": "",
    "purge_flag": [],
    "security": {
        "k": "465B5CE8B199B49FAA5F0A2EE238A6BC",
        "amf": "8000",
        "op": null,
        "opc": "E8ED289DEBA952E4283B54E88E6183CA"
    },
    "ambr": {
        "downlink": {"value": 1, "unit": 3},
        "uplink": {"value": 1, "unit": 3}
    },
    "slice": [
        {
            "sst": 1,
            "sd": "010203",
            "default_indicator": true,
            "session": [
                {
                    "name": "internet",
                    "type": 3,
                    "pcc_rule": [],
                    "ambr": {
                        "downlink": {"value": 1, "unit": 3},
                        "uplink": {"value": 1, "unit": 3}
                    },
                    "qos": {
                        "index": 9,
                        "arp": {
                            "priority_level": 8,
                            "pre_emption_capability": 1,
                            "pre_emption_vulnerability": 1
                        }
                    }
                }
            ]
        }
    ]
});

// Verify subscriber was added
var count = db.subscribers.countDocuments({"imsi": "999700000000001"});
print("Subscribers added: " + count);

// Show the added subscriber
var subscriber = db.subscribers.findOne({"imsi": "999700000000001"});
if (subscriber) {
    print("Subscriber IMSI: " + subscriber.imsi);
    print("Subscriber K: " + subscriber.security.k);
    print("Subscriber OPc: " + subscriber.security.opc);
    print("Default APN: " + subscriber.slice[0].session[0].name);
} else {
    print("ERROR: Subscriber not found after insertion!");
}
