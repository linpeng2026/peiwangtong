# 网络设备型号数据库 - 3级联动结构
# 结构: {厂商: {类型: [设备型号列表]}}

DEVICE_MODELS = {
    # ==================== Huawei 华为 ====================
    "Huawei 华为": {
        "交换机": [
            "CloudEngine 16800",
            "CloudEngine 12800",
            "CloudEngine 8800",
            "CloudEngine 6800",
            "CloudEngine 5800",
            "S12700E",
            "S12700",
            "S9700",
            "S8700",
            "S7700",
            "S6700",
            "S5700",
            "S5735",
            "S3700",
            "S2700",
        ],
        "路由器": [
            "AR6000",
            "AR5000",
            "AR3200",
            "AR2200",
            "AR1200",
            "AR650",
            "NE5000E",
            "NE40E",
            "NE20E",
            "NE08E",
            "NetEngine 8000",
            "NetEngine 4000",
            "NetEngine 2000",
        ],
        "防火墙": [
            "USG6000E",
            "USG9500",
        ],
    },
    
    # ==================== H3C 新华三 ====================
    "H3C 新华三": {
        "交换机": [
            "S12500",
            "S9800",
            "S6800",
            "S6520X",
            "S5560S",
            "S5130S",
            "S5000",
            "S3100",
            "S5100",
            "S5800",
            "S7500E",
            "S7500",
            "S6500",
            "S5500",
        ],
        "路由器": [
            "MSR3600",
            "MSR2600",
            "MSR1600",
            "MSR900",
            "SR8800",
            "SR6600",
            "CR16000",
            "CR19000",
        ],
        "防火墙": [
            "SecPath F1000",
            "SecPath F5000",
        ],
    },
    
    # ==================== Ruijie 锐捷 ====================
    "Ruijie 锐捷": {
        "交换机": [
            "RG-S6510",
            "RG-S6520",
            "RG-S6220",
            "RG-S5750",
            "RG-S5700",
            "RG-S2900",
            "RG-S2800",
            "RG-S2600",
            "RG-S6000C",
            "RG-S8600",
            "RG-S7800",
            "RG-S7500",
            "RG-S5200",
            "RG-N18000",
        ],
        "路由器": [
            "RG-RSR7700",
            "RG-RSR50X",
            "RG-RSR30X",
            "RG-RSR20",
            "RG-EG2000",
            "RG-EG1000",
        ],
        "Reyee系列": [
            "Reyee RG-ES200",
            "Reyee RG-ES100",
            "Reyee RG-EG200",
            "Reyee RG-EG100",
            "Reyee RG-RAP200",
            "Reyee RG-RAP100",
        ],
    },
    
    # ==================== Cisco 思科 ====================
    "Cisco 思科": {
        "交换机": [
            "Catalyst 9500",
            "Catalyst 9400",
            "Catalyst 9300",
            "Catalyst 9200",
            "Catalyst 3850",
            "Catalyst 3650",
            "Catalyst 2960-X",
            "Catalyst 2960",
            "Catalyst 4500",
            "Catalyst 6500",
            "Nexus 9000",
            "Nexus 7000",
            "Nexus 5000",
            "Nexus 3000",
            "Nexus 2000",
        ],
        "路由器": [
            "ASR 9000",
            "ASR 1000",
            "ISR 4000",
            "ISR 1000",
            "Cisco 8000",
        ],
        "防火墙": [
            "ASA 5500-X",
            "ASA 5500",
            "Firepower 1000",
            "Firepower 2100",
            "Firepower 4100",
            "Firepower 9300",
        ],
    },
    
    # ==================== Juniper 瞻博 ====================
    "Juniper 瞻博": {
        "交换机": [
            "EX4300",
            "EX4600",
            "EX3400",
            "EX2300",
            "EX2200",
            "QFX5100",
            "QFX5200",
            "QFX10000",
        ],
        "路由器": [
            "MX960",
            "MX480",
            "MX240",
            "MX2000",
            "MX5000",
            "ACX2100",
            "ACX2200",
            "PTX10000",
            "PTX5000",
        ],
        "防火墙": [
            "SRX1500",
            "SRX5000",
            "SRX300",
            "SRX4100",
            "SRX4600",
        ],
    },
    
    # ==================== Aruba 阿鲁巴 ====================
    "Aruba 阿鲁巴": {
        "交换机": [
            "8320CX",
            "8360CX",
            "8400",
            "6300M",
            "6200F",
            "2930F",
            "2930M",
            "3810M",
            "5400R",
            "2530",
            "2540",
            "2920",
            "6000",
            "8200",
        ],
    },
    
    # ==================== ZTE 中兴 ====================
    "ZTE 中兴": {
        "交换机": [
            "ZXR10 8900E",
            "ZXR10 5900E",
            "ZXR10 5200",
            "ZXR10 2800",
            "ZXR10 2200",
        ],
        "路由器": [
            "ZXR10 GER",
            "ZXR10 M6000",
        ],
    },
    
    # ==================== Maipu 迈普 ====================
    "Maipu 迈普": {
        "交换机": [
            "IS8000",
            "IS6000",
            "IS5000",
            "IS3000",
            "IS2000",
        ],
        "路由器": [
            "MP2800",
            "MP2600",
            "MP1800",
        ],
    },
    
    # ==================== TP-Link ====================
    "TP-Link": {
        "交换机": [
            "JetStream T2600G",
            "JetStream T2500G",
            "JetStream T1600G",
            "JetStream T1500G",
            "JetStream TL-SG3428",
            "JetStream TL-SG3452",
        ],
        "路由器": [
            "Omada ER7206",
            "Omada ER605",
            "Omada ER2260T",
        ],
    },
    
    # ==================== D-Link ====================
    "D-Link": {
        "交换机": [
            "DGS-3620",
            "DGS-3630",
            "DGS-1510",
            "DGS-1210",
            "DXS-1210",
        ],
    },
    
    # ==================== Fortinet 飞塔 ====================
    "Fortinet 飞塔": {
        "防火墙": [
            "FortiGate 600E",
            "FortiGate 400E",
            "FortiGate 200E",
            "FortiGate 100E",
            "FortiGate 90G",
            "FortiGate 80F",
            "FortiGate 60F",
            "FortiGate 40F",
            "FortiGate 30E",
        ],
        "交换机": [
            "FortiSwitch 424E",
            "FortiSwitch 448E",
            "FortiSwitch 448D",
        ],
    },
    
    # ==================== Palo Alto 派拓网络 ====================
    "Palo Alto 派拓网络": {
        "防火墙": [
            "PA-5200",
            "PA-3200",
            "PA-220",
            "PA-7000",
            "VM-Series",
        ],
    },
    
    # ==================== MikroTik ====================
    "MikroTik": {
        "路由器": [
            "CCR2004",
            "CCR1036",
            "CCR1009",
            "RB5009",
            "RB4011",
            "hEX",
            "hAP",
            "CCR2116",
        ],
        "交换机": [
            "CRS328",
            "CRS326",
            "CRS317",
        ],
    },
    
    # ==================== Ubiquiti ====================
    "Ubiquiti": {
        "路由器": [
            "EdgeRouter Infinity",
            "EdgeRouter 12",
            "EdgeRouter X",
            "EdgeRouter 4",
            "UniFi UDM-Pro",
            "UniFi UDM-SE",
        ],
        "交换机": [
            "UniFi USW-Pro-48",
            "UniFi USW-Pro-24",
            "UniFi USW-Enterprise-24",
            "UniFi USW-Aggregation",
        ],
    },
    
    # ==================== Dell 戴尔 ====================
    "Dell 戴尔": {
        "交换机": [
            "PowerSwitch S5248F",
            "PowerSwitch S5224F",
            "PowerSwitch S4148U",
            "PowerSwitch S4128T",
            "PowerSwitch S3048",
            "PowerSwitch S4048",
            "PowerConnect 8024",
            "PowerConnect 6248",
        ],
    },
    
    # ==================== Extreme Networks ====================
    "Extreme Networks": {
        "交换机": [
            "X465",
            "X440",
            "X330",
            "X150",
            "SLX 9140",
            "VSP 7200",
            "VSP 8200",
            "VSP 8400",
        ],
    },
    
    # ==================== Brocade ====================
    "Brocade": {
        "交换机": [
            "ICX 7850",
            "ICX 7650",
            "ICX 7450",
            "ICX 7250",
            "ICX 7150",
            "MLXe",
            "NetIron MLX",
        ],
    },
    
    # ==================== Allied Telesis ====================
    "Allied Telesis": {
        "交换机": [
            "x950",
            "x510",
            "x310",
            "x230",
            "x220",
        ],
    },
    
    # ==================== Netgear ====================
    "Netgear": {
        "交换机": [
            "M4300-52G",
            "M4300-28G",
            "M4250-12G",
            "M4250-24G",
            "GSM4248P",
        ],
    },
    
    # ==================== Lenovo 联想 ====================
    "Lenovo 联想": {
        "交换机": [
            "NE1032",
            "NE1032T",
            "NE0152T",
            "G8264",
            "G8124",
        ],
    },
    
    # ==================== Inspur 浪潮 ====================
    "Inspur 浪潮": {
        "交换机": [
            "CN6024G",
            "CN6024S",
            "CN6016Q",
            "CN6012Q",
        ],
    },
    
    # ==================== DCN 神州数码 ====================
    "DCN 神州数码": {
        "交换机": [
            "DCN-S6200",
            "DCN-S6000",
            "DCN-S5000",
            "DCN-S3700",
        ],
        "路由器": [
            "DCN-RSR7800",
            "DCN-RSR5900",
            "DCN-RSR3200",
        ],
    },
    
    # ==================== FiberHome 烽火 ====================
    "FiberHome 烽火": {
        "交换机": [
            "S6800",
            "S6600",
            "S5500",
            "S3500",
        ],
        "路由器": [
            "AN5516",
        ],
    },
    
    # ==================== Raisecom 瑞斯康达 ====================
    "Raisecom 瑞斯康达": {
        "路由器": [
            "RC8000",
            "RC5000",
            "ISCOM2600",
            "ISCOM2100",
        ],
    },
    
    # ==================== Ciena ====================
    "Ciena": {
        "传输设备": [
            "6500",
            "5430",
            "5160",
            "5140",
        ],
    },
    
    # ==================== Calix ====================
    "Calix": {
        "接入设备": [
            "E7-2",
            "E7-16",
            "RAX 500",
        ],
    },
}

# 设备型号到系统类型的映射
MODEL_TO_SYSTEM = {
    # Cisco
    "Catalyst 9500": "Cisco IOS-XE",
    "Catalyst 9400": "Cisco IOS-XE",
    "Catalyst 9300": "Cisco IOS-XE",
    "Catalyst 9200": "Cisco IOS-XE",
    "Catalyst 3850": "Cisco IOS-XE",
    "Catalyst 3650": "Cisco IOS-XE",
    "Catalyst 2960-X": "Cisco IOS",
    "Catalyst 2960": "Cisco IOS",
    "Catalyst 4500": "Cisco IOS",
    "Catalyst 6500": "Cisco IOS",
    "Nexus 9000": "Cisco NX-OS",
    "Nexus 7000": "Cisco NX-OS",
    "Nexus 5000": "Cisco NX-OS",
    "Nexus 3000": "Cisco NX-OS",
    "Nexus 2000": "Cisco NX-OS",
    "ASR 9000": "Cisco IOS-XR",
    "ASR 1000": "Cisco IOS-XE",
    "ISR 4000": "Cisco IOS-XE",
    "ISR 1000": "Cisco IOS-XE",
    "Cisco 8000": "Cisco IOS-XR",
    "ASA 5500-X": "Cisco ASA",
    "ASA 5500": "Cisco ASA",
    "Firepower 1000": "Cisco ASA",
    "Firepower 2100": "Cisco ASA",
    "Firepower 4100": "Cisco ASA",
    "Firepower 9300": "Cisco ASA",
    
    # Huawei
    "CloudEngine 16800": "Huawei CloudEngine",
    "CloudEngine 12800": "Huawei CloudEngine",
    "CloudEngine 8800": "Huawei CloudEngine",
    "CloudEngine 6800": "Huawei CloudEngine",
    "CloudEngine 5800": "Huawei CloudEngine",
    "S12700E": "Huawei VRP V8",
    "S12700": "Huawei VRP",
    "S9700": "Huawei VRP",
    "S8700": "Huawei VRP V8",
    "S7700": "Huawei VRP",
    "S6700": "Huawei VRP",
    "S5700": "Huawei VRP",
    "S5735": "Huawei VRP",
    "S3700": "Huawei VRP",
    "S2700": "Huawei VRP",
    "AR6000": "Huawei VRP V8",
    "AR5000": "Huawei VRP",
    "AR3200": "Huawei VRP",
    "AR2200": "Huawei VRP",
    "AR1200": "Huawei VRP",
    "AR650": "Huawei VRP",
    "NE5000E": "Huawei VRP",
    "NE40E": "Huawei VRP",
    "NE20E": "Huawei VRP",
    "NE08E": "Huawei VRP",
    "NetEngine 8000": "Huawei VRP V8",
    "NetEngine 4000": "Huawei VRP V8",
    "NetEngine 2000": "Huawei VRP V8",
    "USG6000E": "Huawei VRP",
    "USG9500": "Huawei VRP",
    
    # H3C
    "S12500": "H3C Comware V7",
    "S9800": "H3C Comware V7",
    "S6800": "H3C Comware V7",
    "S6520X": "H3C Comware V7",
    "S5560S": "H3C Comware V7",
    "S5130S": "H3C Comware V7",
    "S5000": "H3C Comware V7",
    "S3100": "H3C Comware V5",
    "S5100": "H3C Comware V5",
    "S5800": "H3C Comware V5",
    "S7500E": "H3C Comware V7",
    "S7500": "H3C Comware V5",
    "S6500": "H3C Comware V5",
    "S5500": "H3C Comware V5",
    "MSR3600": "H3C Comware V7",
    "MSR2600": "H3C Comware V7",
    "MSR1600": "H3C Comware V7",
    "MSR900": "H3C Comware V7",
    "SR8800": "H3C Comware V7",
    "SR6600": "H3C Comware V7",
    "CR16000": "H3C Comware V7",
    "CR19000": "H3C Comware V9",
    "SecPath F1000": "H3C Comware V7",
    "SecPath F5000": "H3C Comware V7",
    
    # Ruijie
    "RG-S6510": "Ruijie RGOS",
    "RG-S6520": "Ruijie RGOS",
    "RG-S6220": "Ruijie RGOS",
    "RG-S5750": "Ruijie RGOS",
    "RG-S5700": "Ruijie RGOS",
    "RG-S2900": "Ruijie RGOS",
    "RG-S2800": "Ruijie RGOS",
    "RG-S2600": "Ruijie RGOS",
    "RG-S6000C": "Ruijie RGOS",
    "RG-S8600": "Ruijie RGOS",
    "RG-S7800": "Ruijie RGOS",
    "RG-S7500": "Ruijie RGOS",
    "RG-S5200": "Ruijie RGOS",
    "RG-N18000": "Ruijie RGOS",
    "RG-RSR7700": "Ruijie RGOS",
    "RG-RSR50X": "Ruijie RGOS",
    "RG-RSR30X": "Ruijie RGOS",
    "RG-RSR20": "Ruijie RGOS",
    "RG-EG2000": "Ruijie RGOS",
    "RG-EG1000": "Ruijie RGOS",
    "Reyee RG-ES200": "Ruijie Reyee",
    "Reyee RG-ES100": "Ruijie Reyee",
    "Reyee RG-EG200": "Ruijie Reyee",
    "Reyee RG-EG100": "Ruijie Reyee",
    "Reyee RG-RAP200": "Ruijie Reyee",
    "Reyee RG-RAP100": "Ruijie Reyee",
    
    # Juniper
    "EX4300": "Juniper JunOS",
    "EX4600": "Juniper JunOS",
    "EX3400": "Juniper JunOS",
    "EX2300": "Juniper JunOS",
    "EX2200": "Juniper JunOS",
    "QFX5100": "Juniper JunOS",
    "QFX5200": "Juniper JunOS",
    "QFX10000": "Juniper JunOS",
    "MX960": "Juniper JunOS",
    "MX480": "Juniper JunOS",
    "MX240": "Juniper JunOS",
    "MX2000": "Juniper JunOS",
    "MX5000": "Juniper JunOS",
    "SRX1500": "Juniper JunOS",
    "SRX5000": "Juniper JunOS",
    "SRX300": "Juniper JunOS",
    "SRX4100": "Juniper JunOS",
    "SRX4600": "Juniper JunOS",
    "ACX2100": "Juniper JunOS",
    "ACX2200": "Juniper JunOS",
    "PTX10000": "Juniper JunOS",
    "PTX5000": "Juniper JunOS",
    
    # Aruba
    "8320CX": "Aruba AOS-CX",
    "8360CX": "Aruba AOS-CX",
    "8400": "Aruba AOS-CX",
    "6300M": "Aruba AOS-CX",
    "6200F": "Aruba AOS-CX",
    "2930F": "Aruba AOS-Switch",
    "2930M": "Aruba AOS-Switch",
    "3810M": "Aruba AOS-Switch",
    "5400R": "Aruba AOS-Switch",
    "2530": "Aruba AOS-Switch",
    "2540": "Aruba AOS-Switch",
    "2920": "Aruba AOS-Switch",
    "6000": "Aruba AOS-Switch",
    "8200": "Aruba AOS-Switch",
    
    # ZTE
    "ZXR10 8900E": "ZTE ZXR10",
    "ZXR10 5900E": "ZTE ZXR10",
    "ZXR10 5200": "ZTE ZXR10",
    "ZXR10 2800": "ZTE ZXR10",
    "ZXR10 2200": "ZTE ZXR10",
    "ZXR10 GER": "ZTE Router",
    "ZXR10 M6000": "ZTE Router",
    
    # Maipu
    "IS8000": "Maipu MPS",
    "IS6000": "Maipu MPS",
    "IS5000": "Maipu MPS",
    "IS3000": "Maipu MPS",
    "IS2000": "Maipu MPS",
    "MP2800": "Maipu Router",
    "MP2600": "Maipu Router",
    "MP1800": "Maipu Router",
    
    # TP-Link
    "JetStream T2600G": "TP-Link JetStream",
    "JetStream T2500G": "TP-Link JetStream",
    "JetStream T1600G": "TP-Link JetStream",
    "JetStream T1500G": "TP-Link JetStream",
    "JetStream TL-SG3428": "TP-Link JetStream",
    "JetStream TL-SG3452": "TP-Link JetStream",
    "Omada ER7206": "TP-Link Omada",
    "Omada ER605": "TP-Link Omada",
    "Omada ER2260T": "TP-Link Omada",
    
    # D-Link
    "DGS-3620": "D-Link DGS",
    "DGS-3630": "D-Link DGS",
    "DGS-1510": "D-Link DGS",
    "DGS-1210": "D-Link DGS",
    "DXS-1210": "D-Link DGS",
    
    # Fortinet
    "FortiGate 600E": "Fortinet FortiOS",
    "FortiGate 400E": "Fortinet FortiOS",
    "FortiGate 200E": "Fortinet FortiOS",
    "FortiGate 100E": "Fortinet FortiOS",
    "FortiGate 90G": "Fortinet FortiOS",
    "FortiGate 80F": "Fortinet FortiOS",
    "FortiGate 60F": "Fortinet FortiOS",
    "FortiGate 40F": "Fortinet FortiOS",
    "FortiGate 30E": "Fortinet FortiOS",
    "FortiSwitch 424E": "Fortinet FortiSwitch",
    "FortiSwitch 448E": "Fortinet FortiSwitch",
    "FortiSwitch 448D": "Fortinet FortiSwitch",
    
    # Palo Alto
    "PA-5200": "Palo Alto PAN-OS",
    "PA-3200": "Palo Alto PAN-OS",
    "PA-220": "Palo Alto PAN-OS",
    "PA-7000": "Palo Alto PAN-OS",
    "VM-Series": "Palo Alto PAN-OS",
    
    # MikroTik
    "CCR2004": "MikroTik RouterOS",
    "CCR1036": "MikroTik RouterOS",
    "CCR1009": "MikroTik RouterOS",
    "CRS328": "MikroTik RouterOS",
    "CRS326": "MikroTik RouterOS",
    "CRS317": "MikroTik RouterOS",
    "RB5009": "MikroTik RouterOS",
    "RB4011": "MikroTik RouterOS",
    "hEX": "MikroTik RouterOS",
    "hAP": "MikroTik RouterOS",
    "CCR2116": "MikroTik RouterOS",
    
    # Ubiquiti
    "EdgeRouter Infinity": "Ubiquiti EdgeOS",
    "EdgeRouter 12": "Ubiquiti EdgeOS",
    "EdgeRouter X": "Ubiquiti EdgeOS",
    "EdgeRouter 4": "Ubiquiti EdgeOS",
    "UniFi USW-Pro-48": "Ubiquiti UniFi",
    "UniFi USW-Pro-24": "Ubiquiti UniFi",
    "UniFi USW-Enterprise-24": "Ubiquiti UniFi",
    "UniFi USW-Aggregation": "Ubiquiti UniFi",
    "UniFi UDM-Pro": "Ubiquiti UniFi",
    "UniFi UDM-SE": "Ubiquiti UniFi",
    
    # Dell
    "PowerSwitch S5248F": "Dell OS10",
    "PowerSwitch S5224F": "Dell OS10",
    "PowerSwitch S4148U": "Dell OS10",
    "PowerSwitch S4128T": "Dell OS10",
    "PowerSwitch S3048": "Dell OS9",
    "PowerSwitch S4048": "Dell OS9",
    "PowerConnect 8024": "Dell PowerConnect",
    "PowerConnect 6248": "Dell PowerConnect",
    
    # Extreme
    "X465": "Extreme EXOS",
    "X440": "Extreme EXOS",
    "X330": "Extreme EXOS",
    "X150": "Extreme EXOS",
    "SLX 9140": "Extreme SLX",
    "VSP 7200": "Extreme VOSS",
    "VSP 8200": "Extreme VOSS",
    "VSP 8400": "Extreme VOSS",
    
    # Brocade
    "ICX 7850": "Brocade ICX",
    "ICX 7650": "Brocade ICX",
    "ICX 7450": "Brocade ICX",
    "ICX 7250": "Brocade ICX",
    "ICX 7150": "Brocade ICX",
    "MLXe": "Brocade MLX",
    "NetIron MLX": "Brocade MLX",
    
    # Allied Telesis
    "x950": "Allied Telesis AlliedWare Plus",
    "x510": "Allied Telesis AlliedWare Plus",
    "x310": "Allied Telesis AlliedWare Plus",
    "x230": "Allied Telesis AlliedWare Plus",
    "x220": "Allied Telesis AlliedWare Plus",
    
    # Netgear
    "M4300-52G": "Netgear M4300",
    "M4300-28G": "Netgear M4300",
    "M4250-12G": "Netgear M4250",
    "M4250-24G": "Netgear M4250",
    "GSM4248P": "Netgear M4250",
    
    # Lenovo
    "NE1032": "Lenovo CNOS",
    "NE1032T": "Lenovo CNOS",
    "NE0152T": "Lenovo CNOS",
    "G8264": "Lenovo ENOS",
    "G8124": "Lenovo ENOS",
    
    # Inspur
    "CN6024G": "Inspur Switch OS",
    "CN6024S": "Inspur Switch OS",
    "CN6016Q": "Inspur Switch OS",
    "CN6012Q": "Inspur Switch OS",
    
    # DCN
    "DCN-S6200": "DCN DCNOS",
    "DCN-S6000": "DCN DCNOS",
    "DCN-S5000": "DCN DCNOS",
    "DCN-S3700": "DCN DCNOS",
    "DCN-RSR7800": "DCN DCNOS",
    "DCN-RSR5900": "DCN DCNOS",
    "DCN-RSR3200": "DCN DCNOS",
    
    # FiberHome
    "S6800": "FiberHome Switch",
    "S6600": "FiberHome Switch",
    "S5500": "FiberHome Switch",
    "S3500": "FiberHome Switch",
    "AN5516": "FiberHome Router",
    
    # Raisecom
    "RC8000": "Raisecom Router",
    "RC5000": "Raisecom Router",
    "ISCOM2600": "Raisecom Router",
    "ISCOM2100": "Raisecom Router",
    
    # Ciena
    "6500": "Ciena SAOS",
    "5430": "Ciena SAOS",
    "5160": "Ciena SAOS",
    "5140": "Ciena SAOS",
    
    # Calix
    "E7-2": "Calix AXOS",
    "E7-16": "Calix AXOS",
    "RAX 500": "Calix AXOS",
}


def get_vendors():
    """获取所有厂商列表"""
    return list(DEVICE_MODELS.keys())


def get_types(vendor):
    """获取指定厂商的设备类型列表"""
    if vendor in DEVICE_MODELS:
        return list(DEVICE_MODELS[vendor].keys())
    return []


def get_models(vendor, device_type):
    """获取指定厂商和类型的设备型号列表"""
    if vendor in DEVICE_MODELS and device_type in DEVICE_MODELS[vendor]:
        return DEVICE_MODELS[vendor][device_type]
    return []


def get_system_type(model):
    """根据设备型号获取系统类型"""
    return MODEL_TO_SYSTEM.get(model, model)


def get_full_device_name(vendor, model):
    """获取完整的设备名称（厂商 + 型号）"""
    return f"{vendor} {model}"
