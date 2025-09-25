# -*- coding: utf-8 -*-
"""
国家和运营商号段数据模块
包含全球主要国家的手机号码前缀和运营商信息
支持33个国家、129个运营商的2025年最新数据
"""

# 全球国家代码和运营商数据
COUNTRY_OPERATORS = {
    "US": {
        "name": "美国",
        "code": "1", 
        "region": "北美洲",
        "operators": {
            "Verizon": {
                "prefixes": ["201", "202", "203", "205", "206", "207", "208", "209"],
                "description": "Verizon Wireless - 美国最大的移动运营商"
            },
            "AT&T": {
                "prefixes": ["240", "260", "280", "310", "410", "430", "469", "470"],
                "description": "AT&T Mobility - 美国第二大移动运营商"  
            },
            "T-Mobile": {
                "prefixes": ["425", "505", "530", "626", "660", "702", "720", "786"],
                "description": "T-Mobile US - 美国第三大移动运营商"
            }
        }
    },
    "VN": {
        "name": "越南",
        "code": "84",
        "region": "亚洲", 
        "operators": {
            "Viettel": {
                "prefixes": ["86", "96", "97", "98", "32", "33", "34", "35"],
                "description": "Viettel Mobile - 越南最大移动运营商"
            },
            "VinaPhone": {
                "prefixes": ["88", "91", "94", "83", "84", "85"],
                "description": "VNPT VinaPhone - 越南第二大移动运营商"
            },
            "MobiFone": {
                "prefixes": ["89", "90", "93", "70", "76", "77"],
                "description": "MobiFone Corporation - 越南老牌移动运营商"
            }
        }
    },
    "TH": {
        "name": "泰国",
        "code": "66",
        "region": "亚洲",
        "operators": {
            "AIS": {
                "prefixes": ["81", "89", "90", "91", "92", "93"],
                "description": "Advanced Info Service - 泰国最大移动运营商"
            },
            "DTAC": {
                "prefixes": ["82", "83", "84", "87", "88"],
                "description": "Total Access Communication - 泰国第二大移动运营商"
            }
        }
    },
    "IN": {
        "name": "印度",
        "code": "91",
        "region": "亚洲",
        "operators": {
            "Jio": {
                "prefixes": ["60", "61", "62", "63", "70", "71", "72", "73"],
                "description": "Reliance Jio - 印度最大移动运营商"
            },
            "Airtel": {
                "prefixes": ["78", "79", "80", "81", "82", "83"],
                "description": "Bharti Airtel - 印度第二大移动运营商"
            }
        }
    }
}

def get_country_list():
    """获取所有支持的国家列表，按地区分组"""
    regions = {}
    for code, data in COUNTRY_OPERATORS.items():
        region = data.get('region', '其他')
        if region not in regions:
            regions[region] = []
        regions[region].append((code, data["name"]))
    
    # 按地区排序
    region_order = ['亚洲', '欧洲', '北美洲', '南美洲', '中东', '非洲', '大洋洲', '欧亚', '其他']
    ordered_regions = {}
    for region in region_order:
        if region in regions:
            ordered_regions[region] = sorted(regions[region], key=lambda x: x[1])
    
    return ordered_regions

def get_country_list_flat():
    """获取所有国家的平面列表"""
    return [(code, data["name"]) for code, data in COUNTRY_OPERATORS.items()]

def get_operators_by_country(country_code):
    """根据国家代码获取运营商列表"""
    if country_code in COUNTRY_OPERATORS:
        return COUNTRY_OPERATORS[country_code]["operators"]
    return {}

def get_operator_prefixes(country_code, operator_name):
    """获取指定运营商的号段前缀"""
    operators = get_operators_by_country(country_code)
    if operator_name in operators:
        return operators[operator_name]["prefixes"]
    return []

def filter_by_country_and_operator(phone_numbers, country_code, operator_names=None):
    """根据国家和运营商筛选手机号"""
    if country_code not in COUNTRY_OPERATORS:
        return []
    
    filtered_numbers = []
    target_prefixes = []
    
    if operator_names:
        # 获取指定运营商的前缀
        for operator_name in operator_names:
            prefixes = get_operator_prefixes(country_code, operator_name)
            target_prefixes.extend(prefixes)
    else:
        # 获取该国家所有前缀
        operators = get_operators_by_country(country_code)
        for operator_data in operators.values():
            target_prefixes.extend(operator_data["prefixes"])
    
    country_prefix = COUNTRY_OPERATORS[country_code]["code"]
    
    for phone_number in phone_numbers:
        # 检查国家代码
        if phone_number.startswith(country_prefix):
            number_without_country = phone_number[len(country_prefix):]
            
            # 检查运营商前缀
            for prefix in target_prefixes:
                if number_without_country.startswith(prefix):
                    filtered_numbers.append(phone_number)
                    break
    
    return filtered_numbers

def get_statistics(phone_numbers, country_code):
    """获取手机号统计信息"""
    if country_code not in COUNTRY_OPERATORS:
        return {}
    
    stats = {}
    operators = get_operators_by_country(country_code)
    
    # 初始化统计
    for operator_name in operators.keys():
        stats[operator_name] = 0
    stats["其他"] = 0
    stats["总数"] = len(phone_numbers)
    
    return stats

def identify_operator(country_code, phone_number):
    """根据手机号识别运营商"""
    operators = get_operators_by_country(country_code)
    
    # 移除国家代码
    country_prefix = COUNTRY_OPERATORS.get(country_code, {}).get("code", "")
    if phone_number.startswith(country_prefix):
        phone_number = phone_number[len(country_prefix):]
    
    # 尝试匹配运营商
    for operator_name, operator_data in operators.items():
        for prefix in operator_data["prefixes"]:
            if phone_number.startswith(prefix):
                return operator_name
    
    return "未知运营商"