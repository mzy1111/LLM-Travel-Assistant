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
from src.utils.logger import AgentLogger
from src.utils.amap_rate_limiter import get_amap_rate_limiter

# 创建全局日志记录器（工具函数使用）
_tool_logger = AgentLogger(verbose=True)

# 获取高德地图API限流器实例
_amap_limiter = get_amap_rate_limiter()


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
            _tool_logger.log_api_call("高德地图天气API", "跳过", "API密钥未配置")
            _tool_logger.log_fallback("天气信息", "API密钥未配置，使用默认估算")
            return f"天气API密钥未配置。假设{city}在{date}的天气为：晴天，温度15-25°C，适合户外活动。"
        
        # 首先通过地理编码API获取城市编码（adcode）
        geo_url = "https://restapi.amap.com/v3/geocode/geo"
        geo_params = {
            "address": city,
            "key": api_key,
            "output": "json"
        }
        
        geo_response = _amap_limiter.get(geo_url, params=geo_params, timeout=5)
        if geo_response.status_code != 200:
            _tool_logger.log_api_call("高德地图地理编码API", "失败", f"HTTP {geo_response.status_code}")
            _tool_logger.log_fallback("天气信息", f"地理编码失败，使用默认估算")
            return f"无法获取{city}的地理位置信息。假设天气为：晴天，温度15-25°C，适合户外活动。"
        
        geo_data = geo_response.json()
        if geo_data.get("status") != "1" or not geo_data.get("geocodes"):
            _tool_logger.log_api_call("高德地图地理编码API", "失败", f"未找到城市: {city}")
            _tool_logger.log_fallback("天气信息", f"未找到城市，使用默认估算")
            return f"未找到城市{city}。假设天气为：晴天，温度15-25°C，适合户外活动。"
        
        # 获取城市编码（adcode）
        adcode = geo_data["geocodes"][0].get("adcode", "")
        city_name = geo_data["geocodes"][0].get("formatted_address", city)
        _tool_logger.log_api_call("高德地图地理编码API", "成功", f"获取{city}的地理编码: {adcode}")
        
        if not adcode:
            _tool_logger.log_api_call("高德地图地理编码API", "失败", "无法获取城市编码")
            _tool_logger.log_fallback("天气信息", "无法获取城市编码，使用默认估算")
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
            
            weather_response = _amap_limiter.get(weather_url, params=weather_params, timeout=5)
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
                            
                            _tool_logger.log_api_call("高德地图天气API", "成功", f"获取{city}当天实况天气")
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
                            
                            _tool_logger.log_api_call("高德地图天气API", "成功", f"获取{city}在{date}的预报天气")
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
            
            weather_response = _amap_limiter.get(weather_url, params=weather_params, timeout=5)
            if weather_response.status_code == 200:
                weather_data = weather_response.json()
                if weather_data.get("status") == "1":
                    lives = weather_data.get("lives", [])
                    if lives:
                        live = lives[0]
                        temp = live.get("temperature", "N/A")
                        weather = live.get("weather", "未知")
                        
                        _tool_logger.log_api_call("高德地图天气API", "成功", f"获取{city}当前实况天气用于估算")
                        result = f"{city_name}在{date}的天气：{weather}，温度约{temp}°C（基于当前天气估算，{date}距离今天{days_diff}天，实际天气可能有所变化）"
                        result += "。建议根据季节准备相应衣物，关注临近天气预报。"
                        return result
                    else:
                        _tool_logger.log_api_call("高德地图天气API", "失败", "无法获取实况天气")
        _tool_logger.log_fallback("天气信息", "所有API调用失败，使用默认估算")
        return f"天气API无法获取{city_name}在{date}的详细天气信息。建议：根据季节准备相应衣物，关注天气预报。"
        
    except Exception as e:
        _tool_logger.log_api_call("高德地图天气API", "异常", str(e)[:100])
        _tool_logger.log_fallback("天气信息", f"异常错误: {str(e)[:100]}")
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
    使用智能估算方案，基于城市、季节、酒店类型等因素进行价格估算。
    
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
        
        # 使用智能估算方案（基于城市、季节、酒店类型）
        _tool_logger.log_info(f"使用智能估算方案获取{city}酒店价格")
        
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
        
        result += "提示：这是基于城市、季节和酒店类型的智能估算。实际价格可能因位置、预订时间、促销活动等因素有所不同。建议通过飞猪、携程、去哪儿、美团等平台查询实时价格并提前预订。"
        
        _tool_logger.log_info(f"酒店价格估算完成: {city}, {hotel_preference}, 价格范围: {min_price}-{max_price_est}元/晚")
        return result
        
    except Exception as e:
        _tool_logger.log_api_call("酒店价格工具", "异常", str(e)[:100])
        _tool_logger.log_fallback("酒店价格", f"异常错误: {str(e)[:100]}")
        return f"获取酒店价格时出错: {str(e)}。建议根据城市和偏好估算：经济型120-250元/晚，商务型250-500元/晚，豪华型600-1200元/晚。"


@tool
def plan_travel_itinerary(
    days: int,
    destination: Optional[str] = None,
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
    规划旅行行程。会自动查询交通路线、天气、酒店价格和景点门票信息，提供更准确的规划。
    注意：此工具会优先查询交通路线以获取准确的距离和时间信息，这是规划行程的基础。
    目的地和出发地都是可选的，如果没有提供，将进行通用旅行规划。
    
    Args:
        destination: 目的地城市或景点（可选）
        days: 旅行天数
        budget: 预算（可选）
        preferences: 偏好说明，例如"喜欢历史文化"、"偏好自然风光"（可选）
        departure_date: 出发日期，格式为"YYYY-MM-DD"（可选，用于查询天气）
        return_date: 返回日期，格式为"YYYY-MM-DD"（可选，用于查询天气和酒店）
        hotel_preference: 酒店偏好，例如"经济型"、"商务型"、"豪华型"（可选）
        departure_city: 出发地（可选，用于查询自驾路线）
        transport_mode: 出行方式，仅支持"自驾"（可选，用于查询自驾路线）
        interests: 兴趣偏好，例如"历史、文化、美食"（可选，用于查询景点门票）
        session_id: 会话ID（可选，用于区分不同用户）
    
    Returns:
        详细的行程规划提示，包含交通路线（距离、时间、费用）、天气、酒店价格和景点门票信息
    """
    # 构建行程规划提示
    plan_prompt = f"""请为以下需求规划旅行行程：

{"目的地：" + destination if destination else "目的地：未指定（请根据用户偏好推荐合适的目的地）"}
天数：{days}天
预算：{budget if budget else '未指定'}
当前偏好：{preferences if preferences else '无特殊偏好'}
"""
    
    # **优先查询自驾路线**：这是规划行程的基础，必须获取准确的距离和时间
    if departure_city and destination:
        # 默认使用自驾方式
        transport_mode_to_use = transport_mode if transport_mode == "自驾" else "自驾"
        try:
            transport_info = get_transport_route.invoke({
                "origin": departure_city,
                "destination": destination,
                "transport_mode": transport_mode_to_use
            })
            plan_prompt += f"\n【重要】自驾路线信息（距离、时间、费用）：\n{transport_info}\n"
            plan_prompt += "\n注意：请基于上述实际距离和时间来安排行程，而不是估算。\n"
        except Exception as e:
            plan_prompt += f"\n警告：无法获取自驾路线信息（{str(e)}），将使用估算值。\n"
    elif departure_city or destination:
        plan_prompt += "\n提示：缺少出发地或目的地，无法查询准确的自驾路线和距离。建议询问用户完整信息或提供通用建议。\n"
    
    # 如果有目的地和日期信息，查询天气
    if destination and departure_date:
        try:
            weather_info = get_weather_info.invoke({"city": destination, "date": departure_date})
            plan_prompt += f"\n出发日天气：{weather_info}\n"
        except:
            pass
    elif departure_date and not destination:
        plan_prompt += "\n提示：已提供出发日期，但缺少目的地，无法查询具体天气。建议根据出发日期和季节提供一般性天气建议。\n"
    
    # 如果有目的地、酒店偏好和日期，查询酒店价格
    if destination and hotel_preference and departure_date and return_date:
        try:
            hotel_info = get_hotel_prices.invoke({
                "city": destination,
                "checkin_date": departure_date,
                "checkout_date": return_date,
                "hotel_preference": hotel_preference
            })
            plan_prompt += f"\n酒店价格信息：\n{hotel_info}\n"
        except:
            pass
    elif hotel_preference and departure_date and return_date and not destination:
        plan_prompt += "\n提示：已提供酒店偏好和日期，但缺少目的地，无法查询具体酒店价格。建议根据酒店偏好提供一般性价格参考。\n"
    
    # 如果有目的地和兴趣偏好，查询景点门票
    if destination and interests:
        try:
            attraction_info = get_attraction_ticket_prices.invoke({
                "city": destination,
                "attraction_name": None,
                "interests": interests
            })
            plan_prompt += f"\n景点门票信息：\n{attraction_info}\n"
        except:
            pass
    elif interests and not destination:
        plan_prompt += "\n提示：已提供兴趣偏好，但缺少目的地，无法查询具体景点门票。建议根据兴趣偏好推荐相关类型的景点。\n"
    
    plan_prompt += """
请提供详细的每日行程安排，包括：
1. **目的地推荐**：如果用户未指定目的地，请根据用户的偏好、预算和旅行天数推荐合适的目的地
2. **交通安排**：如果提供了出发地和目的地，基于上述查询到的实际距离、时间和费用，合理安排出发和返回的交通方式；如果未提供，请提供交通建议
3. 每日游览景点（考虑天气情况和景点门票价格）
4. 推荐路线（如果查询到了交通路线，考虑实际距离）
5. 餐饮建议
6. 住宿建议（参考酒店价格信息）
7. 预算分配（如提供，参考交通费用、酒店价格、景点门票信息进行合理分配）
8. 根据天气情况的活动建议

**重要**：如果查询到了实际交通距离和时间，所有行程安排必须基于这些实际数据，而不是估算值。如果未查询到，请提供合理的估算和建议。
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
    获取从出发地到目的地的自驾路线规划信息。包括路线、距离、时间、费用估算等。
    使用高德地图API进行精确计算（包括地理编码和路径规划），确保距离和时间准确。
    
    Args:
        origin: 出发地，例如"北京"、"北京天安门"、"河北省廊坊市"
        destination: 目的地，例如"上海"、"上海外滩"、"广东省深圳市"
        transport_mode: 出行方式，仅支持"自驾"
    
    Returns:
        自驾路线信息字符串，包括路线、距离、时间、过路费等。
        使用高德地图API精确计算实际距离、时间、过路费等。
    """
    try:
        # 仅支持自驾方式
        if transport_mode != "自驾":
            return f"当前仅支持自驾方式。请将出行方式设置为'自驾'。"
        
        # 从配置获取API密钥（高德地图）
        api_key = os.getenv("AMAP_API_KEY") or config.get("transport.api_key", "")
        
        # 使用高德地图路径规划API获取自驾路线
        if api_key:
            return _get_driving_route(origin, destination, api_key)
        else:
            return _estimate_driving_route(origin, destination)
            
    except Exception as e:
        _tool_logger.log_api_call("交通路线工具", "异常", str(e)[:100])
        _tool_logger.log_fallback("交通路线", f"异常错误: {str(e)[:100]}")
        return f"获取交通路线时出错: {str(e)}。建议：{origin}到{destination}，请使用自驾方式。"


def _get_driving_route(origin: str, destination: str, api_key: str) -> str:
    """使用高德地图API获取自驾路线（优先使用坐标进行精确计算）"""
    try:
        # 第一步：对出发地和目的地进行地理编码，获取精确坐标
        origin_coord = None
        destination_coord = None
        origin_name = origin
        destination_name = destination
        
        # 地理编码API
        geo_url = "https://restapi.amap.com/v3/geocode/geo"
        
        # 获取出发地坐标
        try:
            _tool_logger.log_info(f"请求出发地地理编码: {origin}")
            geo_params_origin = {
                "address": origin,
                "key": api_key,
                "output": "json"
            }
            geo_response_origin = _amap_limiter.get(geo_url, params=geo_params_origin, timeout=5)
            if geo_response_origin.status_code == 200:
                geo_data_origin = geo_response_origin.json()
                api_status = geo_data_origin.get("status")
                api_info = geo_data_origin.get("info", "")
                
                # 检查是否是频率限制错误
                if api_status != "1":
                    if "QPS" in api_info or "LIMIT" in api_info:
                        _tool_logger.log_api_call("高德地图地理编码API", "失败", f"API调用频率超限: {api_info}")
                        _tool_logger.log_warning(f"出发地地理编码因API频率限制失败，将使用地址字符串进行路径规划")
                    else:
                        _tool_logger.log_api_call("高德地图地理编码API", "失败", f"未找到出发地: {origin} (API返回: {api_info})")
                elif api_status == "1" and geo_data_origin.get("geocodes"):
                    location = geo_data_origin["geocodes"][0].get("location", "")
                    if location:
                        origin_coord = location  # 格式：经度,纬度
                        origin_name = geo_data_origin["geocodes"][0].get("formatted_address", origin)
                        _tool_logger.log_api_call("高德地图地理编码API", "成功", f"获取{origin}坐标: {origin_coord}")
                else:
                    _tool_logger.log_api_call("高德地图地理编码API", "失败", f"未找到出发地: {origin} (无geocodes)")
            else:
                _tool_logger.log_api_call("高德地图地理编码API", "失败", f"HTTP {geo_response_origin.status_code}")
        except Exception as e:
            # 地理编码失败，继续尝试使用地址字符串
            _tool_logger.log_api_call("高德地图地理编码API", "异常", f"{origin}: {str(e)[:100]}")
        
        # 获取目的地坐标
        try:
            _tool_logger.log_info(f"请求目的地地理编码: {destination}")
            geo_params_dest = {
                "address": destination,
                "key": api_key,
                "output": "json"
            }
            geo_response_dest = _amap_limiter.get(geo_url, params=geo_params_dest, timeout=5)
            if geo_response_dest.status_code == 200:
                geo_data_dest = geo_response_dest.json()
                api_status = geo_data_dest.get("status")
                api_info = geo_data_dest.get("info", "")
                
                # 检查是否是频率限制错误
                if api_status != "1":
                    if "QPS" in api_info or "LIMIT" in api_info:
                        _tool_logger.log_api_call("高德地图地理编码API", "失败", f"API调用频率超限: {api_info}")
                        _tool_logger.log_warning(f"目的地地理编码因API频率限制失败，将使用地址字符串进行路径规划")
                    else:
                        _tool_logger.log_api_call("高德地图地理编码API", "失败", f"未找到目的地: {destination} (API返回: {api_info})")
                elif api_status == "1" and geo_data_dest.get("geocodes"):
                    location = geo_data_dest["geocodes"][0].get("location", "")
                    if location:
                        destination_coord = location  # 格式：经度,纬度
                        destination_name = geo_data_dest["geocodes"][0].get("formatted_address", destination)
                        _tool_logger.log_api_call("高德地图地理编码API", "成功", f"获取{destination}坐标: {destination_coord}")
                else:
                    _tool_logger.log_api_call("高德地图地理编码API", "失败", f"未找到目的地: {destination} (无geocodes)")
            else:
                _tool_logger.log_api_call("高德地图地理编码API", "失败", f"HTTP {geo_response_dest.status_code}")
        except Exception as e:
            # 地理编码失败，继续尝试使用地址字符串
            _tool_logger.log_api_call("高德地图地理编码API", "异常", f"{destination}: {str(e)[:100]}")
        
        # 第二步：使用高德地图路径规划API
        route_url = "https://restapi.amap.com/v3/direction/driving"
        
        # 优先使用坐标，如果坐标不可用则使用地址字符串
        route_origin = origin_coord if origin_coord else origin
        route_destination = destination_coord if destination_coord else destination
        
        route_params = {
            "origin": route_origin,
            "destination": route_destination,
            "key": api_key,
            "extensions": "all"  # 返回详细信息，包括过路费
        }
        
        _tool_logger.log_info(f"请求路径规划: {route_origin} -> {route_destination}")
        route_response = _amap_limiter.get(route_url, params=route_params, timeout=10)
        if route_response.status_code == 200:
            route_data = route_response.json()
            
            # 检查API返回状态
            if route_data.get("status") == "1" and route_data.get("route"):
                route_info = route_data["route"]
                paths = route_info.get("paths", [])
                
                if paths:
                    # 取第一条路线（通常是最优路线）
                    path = paths[0]
                    # 确保所有数值都是数字类型，API可能返回字符串
                    distance = float(path.get("distance", 0) or 0)  # 米
                    duration = float(path.get("duration", 0) or 0)  # 秒
                    tolls = float(path.get("tolls", 0) or 0)  # 过路费（元）
                    toll_distance = float(path.get("toll_distance", 0) or 0)  # 收费路段距离（米）
                    
                    # 转换单位
                    distance_km = distance / 1000
                    duration_hour = duration / 3600
                    
                    # 估算油费（假设每公里0.6元）
                    fuel_cost = distance_km * 0.6
                    total_cost = tolls + fuel_cost
                    
                    # 构建结果，使用格式化后的地址名称
                    result = f"{origin_name}到{destination_name}的自驾路线（高德地图API精确计算）：\n"
                    result += f"- 实际距离：{distance_km:.1f}公里（{distance:.0f}米）\n"
                    result += f"- 预计时间：{duration_hour:.1f}小时（{int(duration/60)}分钟）\n"
                    result += f"- 过路费：{tolls:.0f}元\n"
                    result += f"- 收费路段距离：{toll_distance/1000:.1f}公里\n"
                    result += f"- 油费估算：{fuel_cost:.0f}元（按0.6元/公里）\n"
                    result += f"- 总费用估算：{total_cost:.0f}元\n"
                    
                    # 添加路线建议
                    if duration_hour > 8:
                        result += "- 建议：长途驾驶，注意休息，建议中途停留\n"
                    elif duration_hour > 4:
                        result += "- 建议：中长途驾驶，建议准备充足\n"
                    else:
                        result += "- 建议：短途驾驶，适合当日往返\n"
                    
                    _tool_logger.log_api_call("高德地图路径规划API", "成功", f"获取{origin}到{destination}的精确路线")
                    return result
            else:
                # API返回错误，记录错误信息
                error_info = route_data.get("info", "未知错误")
                _tool_logger.log_api_call("高德地图路径规划API", "失败", error_info)
                _tool_logger.log_fallback("交通路线", f"API返回错误: {error_info}")
                error_msg = f"高德地图API返回错误：{error_info}"
                # 如果API返回错误，尝试使用估算
                estimate_result = _estimate_driving_route(origin, destination)
                return f"{error_msg}\n\n{estimate_result}"
        else:
            # HTTP请求失败
            _tool_logger.log_api_call("高德地图路径规划API", "失败", f"HTTP {route_response.status_code}")
            _tool_logger.log_fallback("交通路线", f"HTTP请求失败: {route_response.status_code}")
            error_msg = f"高德地图API请求失败（HTTP {route_response.status_code}）"
            estimate_result = _estimate_driving_route(origin, destination)
            return f"{error_msg}\n\n{estimate_result}"
        
    except requests.exceptions.Timeout:
        error_msg = "高德地图API请求超时"
        estimate_result = _estimate_driving_route(origin, destination)
        return f"{error_msg}\n\n{estimate_result}"
    except requests.exceptions.RequestException as e:
        error_msg = f"高德地图API网络错误：{str(e)}"
        estimate_result = _estimate_driving_route(origin, destination)
        return f"{error_msg}\n\n{estimate_result}"
    except Exception as e:
        # 其他异常
        error_msg = f"获取自驾路线时出错：{str(e)}"
        estimate_result = _estimate_driving_route(origin, destination)
        return f"{error_msg}\n\n{estimate_result}"


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
    使用高德地图POI API查询景点信息。
    
    Args:
        city: 城市名称，例如"北京"、"上海"、"杭州"
        attraction_name: 景点名称（可选），例如"故宫"、"天坛"、"西湖"
        interests: 兴趣偏好（可选），例如"历史"、"文化"、"自然"、"美食"
    
    Returns:
        景点门票价格信息字符串，包括景点名称、地址、电话等。如果API不可用，返回估算信息。
    """
    try:
        # 使用高德地图POI API
        amap_key = os.getenv("AMAP_API_KEY") or config.get("transport.api_key", "")
        
        if amap_key and city:
            try:
                # 高德地图POI搜索API - 优化关键字搜索策略
                poi_url = "https://restapi.amap.com/v3/place/text"
                
                # 构建搜索关键词：如果指定了景点名称，使用精确搜索；否则结合兴趣偏好
                if attraction_name:
                    # 精确搜索指定景点
                    search_keywords = f"{city}{attraction_name}"
                else:
                    # 根据兴趣偏好构建关键词
                    if interests:
                        interest_keywords = {
                            "历史": "历史景点",
                            "文化": "文化景点",
                            "自然": "自然风景",
                            "美食": "美食街",
                            "娱乐": "主题公园",
                            "博物馆": "博物馆"
                        }
                        interest_word = interest_keywords.get(interests, "景点")
                        search_keywords = f"{city}{interest_word}"
                    else:
                        search_keywords = f"{city}景点"
                
                poi_params = {
                    "key": amap_key,
                    "keywords": search_keywords,
                    "city": city,
                    "citylimit": "true",  # 限制在指定城市内搜索，提高精度
                    "types": "110000",  # 风景名胜
                    "offset": 10,
                    "page": 1,
                    "extensions": "all"  # 返回详细信息
                }
                
                poi_response = _amap_limiter.get(poi_url, params=poi_params, timeout=5)
                if poi_response.status_code == 200:
                    poi_data = poi_response.json()
                    if poi_data.get("status") == "1" and poi_data.get("pois"):
                        pois = poi_data["pois"][:10]  # 取前10个
                        _tool_logger.log_api_call("高德地图POI API", "成功", f"关键字'{search_keywords}'，获取{city}景点信息，共{len(pois)}个")
                        
                        result = f"{city}的景点信息"
                        if attraction_name:
                            result += f"（搜索：{attraction_name}）"
                        result += "：\n\n"
                        
                        for i, poi in enumerate(pois, 1):
                            name = poi.get("name", "未知景点")
                            address = poi.get("address", "")
                            tel = poi.get("tel", "")
                            business_area = poi.get("business_area", "")  # 商圈/区域
                            
                            result += f"{i}. {name}\n"
                            if address:
                                result += f"   地址：{address}\n"
                            if business_area:
                                result += f"   区域：{business_area}\n"
                            if tel:
                                result += f"   电话：{tel}\n"
                            result += "\n"
                        
                        result += "提示：门票价格信息请通过官方渠道或携程、去哪儿等平台查询实时价格。"
                        return result
            except Exception as e:
                # API调用失败，使用估算
                _tool_logger.log_api_call("高德地图POI API", "失败", str(e)[:100])
                _tool_logger.log_fallback("景点信息", "高德地图POI API调用失败，使用智能估算")
        else:
            _tool_logger.log_api_call("高德地图POI API", "跳过", "API密钥未配置")
            _tool_logger.log_fallback("景点信息", "高德地图POI API密钥未配置，使用智能估算")
        
        # 如果API不可用，使用基于城市和兴趣的估算
        return _estimate_attraction_tickets(city, attraction_name, interests)
        
    except Exception as e:
        _tool_logger.log_api_call("景点门票工具", "异常", str(e)[:100])
        _tool_logger.log_fallback("景点信息", f"异常错误: {str(e)[:100]}")
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
