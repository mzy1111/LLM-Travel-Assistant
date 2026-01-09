"""Agent工具定义"""
from typing import Optional
import requests
import os
from datetime import datetime, timedelta
try:
    from langchain.tools import tool
except ImportError:
    from langchain_core.tools import tool

from src.config import config


@tool
def get_weather_info(city: str, date: str) -> str:
    """
    获取指定城市在指定日期的天气信息。用于根据天气情况调整旅行规划建议。
    使用高德地图API获取国内天气数据。
    
    Args:
        city: 城市名称，例如"北京"、"上海"、"广州"
        date: 日期，格式为"YYYY-MM-DD"，例如"2024-01-15"
    
    Returns:
        天气信息字符串，包括温度、天气状况、降雨概率等。如果API不可用，返回提示信息。
    """
    try:
        # 从配置获取API密钥（高德地图，与交通API共用）
        api_key = os.getenv("AMAP_API_KEY") or config.get("transport.api_key", "") or config.get("weather.api_key", "")
        
        if not api_key:
            return f"天气API密钥未配置。假设{city}在{date}的天气为：晴天，温度15-25°C，适合户外活动。"
        
        # 首先通过地理编码API获取城市编码（adcode）
        geo_url = "https://restapi.amap.com/v3/geocode/geo"
        geo_params = {
            "address": city,
            "key": api_key,
            "output": "json"
        }
        
        geo_response = requests.get(geo_url, params=geo_params, timeout=5)
        if geo_response.status_code != 200:
            return f"无法获取{city}的地理位置信息。假设天气为：晴天，温度15-25°C，适合户外活动。"
        
        geo_data = geo_response.json()
        if geo_data.get("status") != "1" or not geo_data.get("geocodes"):
            return f"未找到城市{city}。假设天气为：晴天，温度15-25°C，适合户外活动。"
        
        # 获取城市编码（adcode）
        adcode = geo_data["geocodes"][0].get("adcode", "")
        city_name = geo_data["geocodes"][0].get("formatted_address", city)
        
        if not adcode:
            return f"无法获取{city}的城市编码。假设天气为：晴天，温度15-25°C，适合户外活动。"
        
        # 计算目标日期与今天的天数差
        try:
            target_date = datetime.strptime(date, "%Y-%m-%d")
            today = datetime.now().date()
            target_date_only = target_date.date()
            days_diff = (target_date_only - today).days
        except:
            days_diff = 0
        
        # 如果日期是今天或未来4天内，使用预报天气API（extensions=all返回4天预报）
        if days_diff >= 0 and days_diff <= 4:
            weather_url = "https://restapi.amap.com/v3/weather/weatherInfo"
            weather_params = {
                "city": adcode,
                "key": api_key,
                "extensions": "all",  # all返回4天预报，base返回实况天气
                "output": "json"
            }
            
            weather_response = requests.get(weather_url, params=weather_params, timeout=5)
            if weather_response.status_code == 200:
                weather_data = weather_response.json()
                if weather_data.get("status") == "1":
                    # 如果是今天，优先使用实况天气
                    if days_diff == 0:
                        lives = weather_data.get("lives", [])
                        if lives:
                            live = lives[0]
                            temp = live.get("temperature", "N/A")
                            weather = live.get("weather", "未知")
                            wind_direction = live.get("winddirection", "")
                            wind_power = live.get("windpower", "")
                            humidity = live.get("humidity", "N/A")
                            report_time = live.get("reporttime", "")
                            
                            result = f"{city_name}在{date}的天气：{weather}，温度{temp}°C，湿度{humidity}%"
                            if wind_direction:
                                result += f"，风向{wind_direction}"
                            if wind_power:
                                result += f"，风力{wind_power}"
                            
                            # 添加活动建议
                            if "雨" in weather or "雪" in weather:
                                result += "。建议安排室内活动或准备雨具。"
                            elif int(temp) if temp != "N/A" and temp.isdigit() else 25 > 30:
                                result += "。天气较热，建议安排室内活动或选择早晨/傍晚出行。"
                            elif int(temp) if temp != "N/A" and temp.isdigit() else 15 < 5:
                                result += "。天气较冷，建议多穿衣物，适合室内活动。"
                            else:
                                result += "。天气适宜，适合户外活动和景点游览。"
                            
                            return result
                    
                    # 如果是未来日期，使用预报天气
                    forecasts = weather_data.get("forecasts", [])
                    if forecasts:
                        forecast = forecasts[0]
                        casts = forecast.get("casts", [])
                        
                        # 查找目标日期的预报
                        target_forecast = None
                        for cast in casts:
                            cast_date = cast.get("date", "")
                            if cast_date == date:
                                target_forecast = cast
                                break
                        
                        if target_forecast:
                            dayweather = target_forecast.get("dayweather", "未知")
                            nightweather = target_forecast.get("nightweather", "未知")
                            daytemp = target_forecast.get("daytemp", "N/A")
                            nighttemp = target_forecast.get("nighttemp", "N/A")
                            daywind = target_forecast.get("daywind", "")
                            nightwind = target_forecast.get("nightwind", "")
                            daypower = target_forecast.get("daypower", "")
                            nightpower = target_forecast.get("nightpower", "")
                            
                            result = f"{city_name}在{date}的天气：白天{dayweather}，夜间{nightweather}，温度{nighttemp}-{daytemp}°C"
                            if daywind:
                                result += f"，白天风向{daywind}"
                            if daypower:
                                result += f"风力{daypower}"
                            if nightwind:
                                result += f"，夜间风向{nightwind}"
                            if nightpower:
                                result += f"风力{nightpower}"
                            
                            # 添加活动建议
                            if "雨" in dayweather or "雨" in nightweather:
                                result += "。建议安排室内活动或准备雨具。"
                            elif int(daytemp) if daytemp != "N/A" and daytemp.isdigit() else 25 > 30:
                                result += "。天气较热，建议安排室内活动或选择早晨/傍晚出行。"
                            elif int(nighttemp) if nighttemp != "N/A" and nighttemp.isdigit() else 15 < 5:
                                result += "。天气较冷，建议多穿衣物，适合室内活动。"
                            else:
                                result += "。天气适宜，适合户外活动和景点游览。"
                            
                            return result
        
        # 如果日期超过4天，使用实况天气并给出估算
        if days_diff > 4:
            weather_url = "https://restapi.amap.com/v3/weather/weatherInfo"
            weather_params = {
                "city": adcode,
                "key": api_key,
                "extensions": "base",  # 实况天气
                "output": "json"
            }
            
            weather_response = requests.get(weather_url, params=weather_params, timeout=5)
            if weather_response.status_code == 200:
                weather_data = weather_response.json()
                if weather_data.get("status") == "1":
                    lives = weather_data.get("lives", [])
                    if lives:
                        live = lives[0]
                        temp = live.get("temperature", "N/A")
                        weather = live.get("weather", "未知")
                        
                        result = f"{city_name}在{date}的天气：{weather}，温度约{temp}°C（基于当前天气估算，{date}距离今天{days_diff}天，实际天气可能有所变化）"
                        result += "。建议根据季节准备相应衣物，关注临近天气预报。"
                        return result
        
        return f"天气API无法获取{city_name}在{date}的详细天气信息。建议：根据季节准备相应衣物，关注天气预报。"
        
    except Exception as e:
        return f"获取天气信息时出错: {str(e)}。假设{city}在{date}的天气为：晴天，温度15-25°C，适合户外活动。"


@tool
def get_hotel_prices(
    city: str,
    checkin_date: str,
    checkout_date: str,
    hotel_preference: Optional[str] = None,
    max_price: Optional[float] = None
) -> str:
    """
    获取指定城市在指定日期的酒店价格信息。用于更准确地估算旅行预算。
    注意：由于国内酒店API需要商业合作，当前使用智能估算方案。如需实时价格，可集成携程、去哪儿等平台API。
    
    Args:
        city: 城市名称，例如"北京"、"上海"、"广州"
        checkin_date: 入住日期，格式为"YYYY-MM-DD"
        checkout_date: 退房日期，格式为"YYYY-MM-DD"
        hotel_preference: 酒店偏好，例如"经济型"、"商务型"、"豪华型"、"民宿"
        max_price: 最高价格限制（人民币/晚），可选
    
    Returns:
        酒店价格信息字符串，包括价格范围、推荐类型等。如果API不可用，返回智能估算信息。
    """
    try:
        # 计算住宿天数
        try:
            checkin = datetime.strptime(checkin_date, "%Y-%m-%d")
            checkout = datetime.strptime(checkout_date, "%Y-%m-%d")
            nights = (checkout - checkin).days
            if nights <= 0:
                nights = 1
        except:
            nights = 1
        
        # 尝试使用携程API（如果配置了）
        ctrip_api_key = os.getenv("CTRIP_API_KEY") or config.get("hotel.api_key", "")
        ctrip_api_secret = os.getenv("CTRIP_API_SECRET") or config.get("hotel.api_secret", "")
        
        if ctrip_api_key and ctrip_api_secret:
            try:
                # 携程API调用示例（需要根据实际API文档调整）
                # 这里提供一个框架，实际使用时需要根据携程开放平台的API文档进行实现
                hotel_url = "https://openapi.ctrip.com/hotel/search"
                # 实际调用代码...
                # 如果成功获取数据，返回实时价格信息
            except Exception as e:
                # API调用失败，使用估算
                pass
        
        # 智能估算方案（基于城市、季节、酒店类型）
        # 根据城市调整价格（一线城市更贵）
        city_multiplier = 1.0
        tier1_cities = ["北京", "上海", "广州", "深圳"]
        tier2_cities = ["杭州", "成都", "重庆", "西安", "南京", "武汉", "苏州", "天津", "长沙", "郑州"]
        
        if any(tier1 in city for tier1 in tier1_cities):
            city_multiplier = 1.5  # 一线城市
        elif any(tier2 in city for tier2 in tier2_cities):
            city_multiplier = 1.2  # 二线城市
        
        # 根据季节调整价格（节假日和旺季更贵）
        try:
            checkin_month = checkin.month
            # 旺季：4-5月（春季）、7-8月（暑假）、10月（国庆）
            if checkin_month in [4, 5, 7, 8, 10]:
                season_multiplier = 1.3
            # 淡季：11-2月（冬季，除春节）
            elif checkin_month in [11, 12, 1, 2]:
                season_multiplier = 0.9
            else:
                season_multiplier = 1.0
        except:
            season_multiplier = 1.0
        
        # 根据酒店类型确定基础价格
        base_prices = {
            "经济型": {"min": 120, "max": 250},
            "商务型": {"min": 250, "max": 500},
            "豪华型": {"min": 600, "max": 1200},
            "民宿": {"min": 150, "max": 350},
            "青旅": {"min": 50, "max": 150}
        }
        
        if hotel_preference and hotel_preference in base_prices:
            price_range = base_prices[hotel_preference]
            min_price = int(price_range["min"] * city_multiplier * season_multiplier)
            max_price_est = int(price_range["max"] * city_multiplier * season_multiplier)
        else:
            # 默认使用商务型价格
            min_price = int(250 * city_multiplier * season_multiplier)
            max_price_est = int(500 * city_multiplier * season_multiplier)
        
        # 如果用户指定了最高价格，进行调整
        if max_price:
            if max_price_est > max_price:
                max_price_est = int(max_price)
            if min_price > max_price:
                min_price = int(max_price * 0.6)  # 如果最低价都超过限制，调整为限制的60%
        
        result = f"{city}在{checkin_date}至{checkout_date}期间的酒店价格估算：\n"
        result += f"- 价格范围：{min_price}-{max_price_est}元/晚（基于城市、季节和偏好智能估算）\n"
        result += f"- 住宿{nights}晚总预算：{min_price * nights}-{max_price_est * nights}元\n"
        result += f"- 建议预算：{int((min_price + max_price_est) / 2 * nights)}元\n"
        
        # 添加价格说明
        if season_multiplier > 1.0:
            result += "- 注意：当前为旅游旺季，价格可能较高，建议提前预订\n"
        elif season_multiplier < 1.0:
            result += "- 注意：当前为旅游淡季，价格相对较低，可能有优惠\n"
        
        result += "提示：这是基于城市、季节和酒店类型的智能估算。实际价格可能因位置、预订时间、促销活动等因素有所不同。建议通过携程、去哪儿、美团等平台查询实时价格并提前预订。"
        
        return result
        
    except Exception as e:
        return f"获取酒店价格时出错: {str(e)}。建议根据城市和偏好估算：经济型120-250元/晚，商务型250-500元/晚，豪华型600-1200元/晚。"


@tool
def plan_travel_itinerary(
    destination: str,
    days: int,
    budget: Optional[float] = None,
    preferences: Optional[str] = None,
    departure_date: Optional[str] = None,
    return_date: Optional[str] = None,
    hotel_preference: Optional[str] = None,
    departure_city: Optional[str] = None,
    transport_mode: Optional[str] = None,
    interests: Optional[str] = None,
    session_id: Optional[str] = None
) -> str:
    """
    规划旅行行程。会自动查询天气、酒店价格、交通路线和景点门票信息，提供更准确的规划。
    
    Args:
        destination: 目的地城市或景点
        days: 旅行天数
        budget: 预算（可选）
        preferences: 偏好说明，例如"喜欢历史文化"、"偏好自然风光"（可选）
        departure_date: 出发日期，格式为"YYYY-MM-DD"（可选，用于查询天气）
        return_date: 返回日期，格式为"YYYY-MM-DD"（可选，用于查询天气和酒店）
        hotel_preference: 酒店偏好，例如"经济型"、"商务型"、"豪华型"（可选）
        departure_city: 出发地（可选，用于查询交通路线）
        transport_mode: 出行方式，例如"飞机"、"高铁"、"火车"、"自驾"（可选，用于查询交通路线）
        interests: 兴趣偏好，例如"历史、文化、美食"（可选，用于查询景点门票）
        session_id: 会话ID（可选，用于区分不同用户）
    
    Returns:
        详细的行程规划提示，包含天气、酒店价格、交通路线和景点门票信息
    """
    # 构建行程规划提示
    plan_prompt = f"""请为以下需求规划旅行行程：

目的地：{destination}
天数：{days}天
预算：{budget if budget else '未指定'}
当前偏好：{preferences if preferences else '无特殊偏好'}
"""
    
    # 如果有日期信息，查询天气
    if departure_date:
        try:
            weather_info = get_weather_info.invoke(destination, departure_date)
            plan_prompt += f"\n出发日天气：{weather_info}\n"
        except:
            pass
    
    # 如果有酒店偏好和日期，查询酒店价格
    if hotel_preference and departure_date and return_date:
        try:
            hotel_info = get_hotel_prices.invoke(destination, departure_date, return_date, hotel_preference)
            plan_prompt += f"\n酒店价格信息：\n{hotel_info}\n"
        except:
            pass
    
    # 如果有出发地、目的地和出行方式，查询交通路线
    if departure_city and transport_mode:
        try:
            transport_info = get_transport_route.invoke(departure_city, destination, transport_mode)
            plan_prompt += f"\n交通路线信息：\n{transport_info}\n"
        except:
            pass
    
    # 如果有目的地和兴趣偏好，查询景点门票
    if interests:
        try:
            attraction_info = get_attraction_ticket_prices.invoke(destination, None, interests)
            plan_prompt += f"\n景点门票信息：\n{attraction_info}\n"
        except:
            pass
    
    plan_prompt += """
请提供详细的每日行程安排，包括：
1. 每日游览景点（考虑天气情况和景点门票价格）
2. 推荐路线
3. 餐饮建议
4. 住宿建议（参考酒店价格信息）
5. 交通方式（参考交通路线和费用信息）
6. 预算分配（如提供，参考酒店价格、交通费用、景点门票信息进行合理分配）
7. 根据天气情况的活动建议
"""
    
    return plan_prompt


@tool
def answer_attraction_question(question: str, attraction: Optional[str] = None, session_id: Optional[str] = None) -> str:
    """
    回答关于景点的问题。
    
    Args:
        question: 问题内容，例如"开放时间"、"门票价格"、"最佳游览时间"
        attraction: 景点名称（可选，如果不提供则从问题中推断）
        session_id: 会话ID（可选，用于区分不同用户）
    
    Returns:
        问题的答案
    """
    # 构建答案提示
    answer_prompt = f"""关于"{attraction or question}"的问题：
{question}

请提供详细、准确的回答。"""
    
    return answer_prompt


@tool
def get_personalized_recommendations(
    destination: str,
    interests: str,
    travel_style: Optional[str] = None,
    session_id: Optional[str] = None
) -> str:
    """
    获取个性化旅行推荐。
    
    Args:
        destination: 目的地
        interests: 兴趣偏好，例如"历史、文化、美食"
        travel_style: 旅行风格，例如"深度游"、"休闲游"、"探险游"（可选）
        session_id: 会话ID（可选，用于区分不同用户）
    
    Returns:
        个性化推荐提示
    """
    # 构建推荐提示
    recommendation_prompt = f"""请根据以下信息提供个性化推荐：

目的地：{destination}
当前兴趣：{interests}
旅行风格：{travel_style or '未指定'}

请提供个性化的推荐列表。"""
    
    return recommendation_prompt


@tool
def get_transport_route(
    origin: str,
    destination: str,
    transport_mode: str
) -> str:
    """
    获取从出发地到目的地的交通路线规划信息。包括路线、距离、时间、费用估算等。
    使用高德地图API进行路径规划。
    
    Args:
        origin: 出发地，例如"北京"、"北京天安门"
        destination: 目的地，例如"上海"、"上海外滩"
        transport_mode: 出行方式，例如"飞机"、"高铁"、"火车"、"自驾"、"大巴"
    
    Returns:
        交通路线信息字符串，包括路线、距离、时间、费用估算等。如果API不可用，返回估算信息。
    """
    try:
        # 从配置获取API密钥（高德地图）
        api_key = os.getenv("AMAP_API_KEY") or config.get("transport.api_key", "")
        
        # 根据出行方式选择不同的处理方式
        if transport_mode in ["飞机", "高铁", "火车", "大巴"]:
            # 这些方式需要查询票价，但免费API有限，使用估算
            return _estimate_public_transport(origin, destination, transport_mode)
        elif transport_mode == "自驾":
            # 自驾可以使用高德地图路径规划API
            if api_key:
                return _get_driving_route(origin, destination, api_key)
            else:
                return _estimate_driving_route(origin, destination)
        else:
            return f"出行方式'{transport_mode}'暂不支持路线规划。建议：{origin}到{destination}，请选择合适的出行方式。"
            
    except Exception as e:
        return f"获取交通路线时出错: {str(e)}。建议：{origin}到{destination}，请选择合适的出行方式。"


def _get_driving_route(origin: str, destination: str, api_key: str) -> str:
    """使用高德地图API获取自驾路线"""
    try:
        # 高德地图路径规划API
        route_url = "https://restapi.amap.com/v3/direction/driving"
        route_params = {
            "origin": origin,
            "destination": destination,
            "key": api_key,
            "extensions": "all"  # 返回详细信息，包括过路费
        }
        
        route_response = requests.get(route_url, params=route_params, timeout=5)
        if route_response.status_code == 200:
            route_data = route_response.json()
            if route_data.get("status") == "1" and route_data.get("route"):
                route_info = route_data["route"]
                paths = route_info.get("paths", [])
                
                if paths:
                    # 取第一条路线（通常是最优路线）
                    path = paths[0]
                    distance = path.get("distance", 0)  # 米
                    duration = path.get("duration", 0)  # 秒
                    tolls = path.get("tolls", 0)  # 过路费（元）
                    toll_distance = path.get("toll_distance", 0)  # 收费路段距离（米）
                    
                    # 转换单位
                    distance_km = distance / 1000
                    duration_hour = duration / 3600
                    
                    # 估算油费（假设每公里0.6元）
                    fuel_cost = distance_km * 0.6
                    total_cost = tolls + fuel_cost
                    
                    result = f"{origin}到{destination}的自驾路线：\n"
                    result += f"- 距离：{distance_km:.1f}公里\n"
                    result += f"- 预计时间：{duration_hour:.1f}小时（{int(duration/60)}分钟）\n"
                    result += f"- 过路费：{tolls:.0f}元\n"
                    result += f"- 油费估算：{fuel_cost:.0f}元（按0.6元/公里）\n"
                    result += f"- 总费用估算：{total_cost:.0f}元\n"
                    
                    # 添加路线建议
                    if duration_hour > 8:
                        result += "- 建议：长途驾驶，注意休息，建议中途停留\n"
                    elif duration_hour > 4:
                        result += "- 建议：中长途驾驶，建议准备充足\n"
                    else:
                        result += "- 建议：短途驾驶，适合当日往返\n"
                    
                    return result
        
        # API调用失败，使用估算
        return _estimate_driving_route(origin, destination)
        
    except Exception as e:
        return _estimate_driving_route(origin, destination)


def _estimate_driving_route(origin: str, destination: str) -> str:
    """估算自驾路线（当API不可用时）"""
    # 简单的距离估算（基于城市间距离）
    city_distances = {
        ("北京", "上海"): 1200,
        ("北京", "广州"): 2100,
        ("北京", "深圳"): 2200,
        ("上海", "广州"): 1400,
        ("上海", "深圳"): 1500,
        ("广州", "深圳"): 150,
    }
    
    # 尝试匹配城市对
    distance_km = None
    for (city1, city2), dist in city_distances.items():
        if (city1 in origin and city2 in destination) or (city2 in origin and city1 in destination):
            distance_km = dist
            break
    
    if distance_km is None:
        # 默认估算：假设是中等距离
        distance_km = 800
    
    # 估算时间和费用
    avg_speed = 80  # 平均速度80km/h
    duration_hour = distance_km / avg_speed
    tolls = distance_km * 0.5  # 过路费估算：0.5元/公里
    fuel_cost = distance_km * 0.6  # 油费：0.6元/公里
    total_cost = tolls + fuel_cost
    
    result = f"{origin}到{destination}的自驾路线估算：\n"
    result += f"- 距离估算：{distance_km:.0f}公里\n"
    result += f"- 预计时间：{duration_hour:.1f}小时（{int(duration_hour*60)}分钟）\n"
    result += f"- 过路费估算：{tolls:.0f}元\n"
    result += f"- 油费估算：{fuel_cost:.0f}元\n"
    result += f"- 总费用估算：{total_cost:.0f}元\n"
    result += "注意：这是估算值，实际距离和费用可能因具体路线而异。建议使用导航软件查询准确路线。"
    
    return result


def _estimate_public_transport(origin: str, destination: str, transport_mode: str) -> str:
    """估算公共交通路线和价格"""
    # 城市间距离估算（用于计算时间）
    city_distances = {
        ("北京", "上海"): 1200,
        ("北京", "广州"): 2100,
        ("北京", "深圳"): 2200,
        ("上海", "广州"): 1400,
        ("上海", "深圳"): 1500,
        ("广州", "深圳"): 150,
    }
    
    distance_km = None
    for (city1, city2), dist in city_distances.items():
        if (city1 in origin and city2 in destination) or (city2 in origin and city1 in destination):
            distance_km = dist
            break
    
    if distance_km is None:
        distance_km = 800  # 默认中等距离
    
    result = f"{origin}到{destination}的{transport_mode}路线：\n"
    
    if transport_mode == "飞机":
        # 飞机：时间短，价格高
        duration_hour = distance_km / 800  # 平均速度800km/h
        # 价格估算：根据距离，0.8-1.2元/公里
        price_min = int(distance_km * 0.8)
        price_max = int(distance_km * 1.2)
        result += f"- 距离：约{distance_km:.0f}公里\n"
        result += f"- 飞行时间：约{int(duration_hour*60)}分钟（不含候机时间）\n"
        result += f"- 票价范围：{price_min}-{price_max}元（经济舱，不含税费）\n"
        result += "- 建议：提前预订可获得更好价格，关注航空公司促销活动\n"
        
    elif transport_mode == "高铁":
        # 高铁：速度快，价格中等
        duration_hour = distance_km / 300  # 平均速度300km/h
        # 价格估算：二等座约0.4-0.5元/公里
        price_min = int(distance_km * 0.4)
        price_max = int(distance_km * 0.5)
        result += f"- 距离：约{distance_km:.0f}公里\n"
        result += f"- 运行时间：约{int(duration_hour*60)}分钟\n"
        result += f"- 票价范围：{price_min}-{price_max}元（二等座）\n"
        result += "- 建议：高铁舒适便捷，适合中长途旅行\n"
        
    elif transport_mode == "火车":
        # 普通火车：速度慢，价格低
        duration_hour = distance_km / 100  # 平均速度100km/h
        # 价格估算：硬座约0.15-0.2元/公里，硬卧约0.3-0.4元/公里
        price_min = int(distance_km * 0.15)
        price_max = int(distance_km * 0.4)
        result += f"- 距离：约{distance_km:.0f}公里\n"
        result += f"- 运行时间：约{int(duration_hour)}小时\n"
        result += f"- 票价范围：{price_min}-{price_max}元（硬座-硬卧）\n"
        result += "- 建议：价格实惠，但时间较长，适合预算有限的旅行\n"
        
    elif transport_mode == "大巴":
        # 大巴：速度中等，价格低
        duration_hour = distance_km / 80  # 平均速度80km/h
        # 价格估算：约0.3-0.5元/公里
        price_min = int(distance_km * 0.3)
        price_max = int(distance_km * 0.5)
        result += f"- 距离：约{distance_km:.0f}公里\n"
        result += f"- 运行时间：约{int(duration_hour)}小时\n"
        result += f"- 票价范围：{price_min}-{price_max}元\n"
        result += "- 建议：价格实惠，适合短途旅行\n"
    
    result += "注意：实际票价和时间可能因具体班次、日期、季节等因素有所不同。建议通过12306、携程等平台查询实时信息。"
    
    return result


@tool
def get_attraction_ticket_prices(
    city: str,
    attraction_name: Optional[str] = None,
    interests: Optional[str] = None
) -> str:
    """
    获取指定城市的景点门票价格信息。用于帮助用户了解景点费用，合理规划预算。
    使用天聚数行旅游景区API或高德地图POI API查询景点信息。
    
    Args:
        city: 城市名称，例如"北京"、"上海"、"杭州"
        attraction_name: 景点名称（可选），例如"故宫"、"天坛"、"西湖"
        interests: 兴趣偏好（可选），例如"历史"、"文化"、"自然"、"美食"
    
    Returns:
        景点门票价格信息字符串，包括景点名称、门票价格、开放时间等。如果API不可用，返回估算信息。
    """
    try:
        # 尝试使用天聚数行API
        tianapi_key = os.getenv("TIANAPI_KEY") or config.get("attraction.api_key", "")
        
        if tianapi_key and city:
            try:
                # 天聚数行旅游景区API
                tianapi_url = "http://api.tianapi.com/lvyou/index"
                tianapi_params = {
                    "key": tianapi_key,
                    "word": city
                }
                
                tianapi_response = requests.get(tianapi_url, params=tianapi_params, timeout=5)
                if tianapi_response.status_code == 200:
                    tianapi_data = tianapi_response.json()
                    if tianapi_data.get("code") == 200 and tianapi_data.get("newslist"):
                        attractions = tianapi_data["newslist"]
                        
                        # 如果指定了景点名称，优先匹配
                        if attraction_name:
                            matched = [a for a in attractions if attraction_name in a.get("name", "")]
                            if matched:
                                attractions = matched[:5]  # 取前5个匹配的
                            else:
                                attractions = attractions[:5]  # 如果没有匹配，取前5个
                        else:
                            attractions = attractions[:10]  # 取前10个
                        
                        if attractions:
                            result = f"{city}的景点门票信息：\n\n"
                            for i, attr in enumerate(attractions, 1):
                                name = attr.get("name", "未知景点")
                                level = attr.get("level", "")
                                address = attr.get("address", "")
                                ticket = attr.get("ticket", "")
                                open_time = attr.get("opentime", "")
                                
                                result += f"{i}. {name}"
                                if level:
                                    result += f"（{level}）"
                                result += "\n"
                                
                                if address:
                                    result += f"   地址：{address}\n"
                                if ticket:
                                    result += f"   门票：{ticket}\n"
                                if open_time:
                                    result += f"   开放时间：{open_time}\n"
                                result += "\n"
                            
                            result += "提示：门票价格可能因季节、优惠政策等因素有所变化，建议通过官方渠道或携程、去哪儿等平台查询实时价格。"
                            return result
            except Exception as e:
                # API调用失败，使用估算
                pass
        
        # 尝试使用高德地图POI API
        amap_key = os.getenv("AMAP_API_KEY") or config.get("transport.api_key", "")
        
        if amap_key and city:
            try:
                # 高德地图POI搜索API
                poi_url = "https://restapi.amap.com/v3/place/text"
                poi_params = {
                    "key": amap_key,
                    "keywords": attraction_name if attraction_name else f"{city}景点",
                    "city": city,
                    "types": "110000",  # 风景名胜
                    "offset": 10,
                    "page": 1,
                    "extensions": "all"
                }
                
                poi_response = requests.get(poi_url, params=poi_params, timeout=5)
                if poi_response.status_code == 200:
                    poi_data = poi_response.json()
                    if poi_data.get("status") == "1" and poi_data.get("pois"):
                        pois = poi_data["pois"][:10]  # 取前10个
                        
                        result = f"{city}的景点信息：\n\n"
                        for i, poi in enumerate(pois, 1):
                            name = poi.get("name", "未知景点")
                            address = poi.get("address", "")
                            location = poi.get("location", "")
                            tel = poi.get("tel", "")
                            
                            result += f"{i}. {name}\n"
                            if address:
                                result += f"   地址：{address}\n"
                            if tel:
                                result += f"   电话：{tel}\n"
                            result += "\n"
                        
                        result += "提示：门票价格信息请通过官方渠道或携程、去哪儿等平台查询。"
                        return result
            except Exception as e:
                # API调用失败，使用估算
                pass
        
        # 如果所有API都不可用，使用基于城市和兴趣的估算
        return _estimate_attraction_tickets(city, attraction_name, interests)
        
    except Exception as e:
        return f"获取景点门票信息时出错: {str(e)}。建议：{city}的主要景点门票通常在50-200元之间，具体价格请查询官方渠道。"


def _estimate_attraction_tickets(city: str, attraction_name: Optional[str], interests: Optional[str]) -> str:
    """估算景点门票价格（当API不可用时）"""
    # 常见城市的主要景点门票价格估算
    city_attractions = {
        "北京": [
            ("故宫", "60元", "AAAAA级景区"),
            ("天坛", "15-35元", "AAAAA级景区"),
            ("颐和园", "30-60元", "AAAAA级景区"),
            ("长城", "40-45元", "AAAAA级景区"),
            ("天安门", "免费", "国家标志"),
        ],
        "上海": [
            ("外滩", "免费", "城市地标"),
            ("东方明珠", "180-220元", "AAAAA级景区"),
            ("豫园", "30-40元", "AAAA级景区"),
            ("田子坊", "免费", "文化创意区"),
            ("朱家角", "免费", "古镇"),
        ],
        "杭州": [
            ("西湖", "免费", "AAAAA级景区"),
            ("灵隐寺", "45-75元", "AAAA级景区"),
            ("雷峰塔", "40元", "AAAA级景区"),
            ("千岛湖", "130-195元", "AAAAA级景区"),
            ("宋城", "310元", "AAAA级景区"),
        ],
        "广州": [
            ("广州塔", "150-298元", "AAAA级景区"),
            ("长隆", "250-350元", "AAAAA级景区"),
            ("白云山", "5元", "AAAAA级景区"),
            ("陈家祠", "10元", "AAAA级景区"),
            ("沙面", "免费", "历史街区"),
        ],
    }
    
    result = f"{city}的主要景点门票价格估算：\n\n"
    
    # 查找城市的主要景点
    found_city = False
    for city_name, attractions in city_attractions.items():
        if city_name in city:
            found_city = True
            for name, price, level in attractions:
                # 如果指定了景点名称，优先匹配
                if attraction_name and attraction_name in name:
                    result += f"★ {name}：{price}（{level}）\n"
                elif not attraction_name:
                    result += f"- {name}：{price}（{level}）\n"
            break
    
    if not found_city:
        # 通用估算
        result += "主要景点门票价格参考：\n"
        result += "- 5A级景区：通常100-300元\n"
        result += "- 4A级景区：通常50-150元\n"
        result += "- 3A级及以下：通常20-80元\n"
        result += "- 免费景点：公园、博物馆等\n"
    
    if interests:
        result += f"\n根据您的兴趣偏好（{interests}），推荐关注相关类型的景点。"
    
    result += "\n提示：实际门票价格可能因季节、优惠政策、联票等因素有所变化。建议通过官方渠道或携程、去哪儿等平台查询实时价格并提前预订。"
    
    return result


# 所有工具列表
TRAVEL_TOOLS = [
    get_weather_info,
    get_hotel_prices,
    get_transport_route,
    get_attraction_ticket_prices,
    plan_travel_itinerary,
    answer_attraction_question,
    get_personalized_recommendations,
]
