"""预算可行性检查模块"""
from datetime import datetime
from typing import Tuple, Dict


class BudgetChecker:
    """预算检查器"""
    
    # 最低费用标准（元）
    MIN_TRANSPORT_LOCAL = 100      # 本地交通最低费用
    MIN_TRANSPORT_NEARBY = 200     # 邻近城市交通最低费用
    MIN_TRANSPORT_FAR = 500        # 远距离交通最低费用
    MIN_HOTEL_ECONOMY = 100        # 经济型酒店最低价格/晚
    MIN_HOTEL_COMFORT = 150        # 舒适型酒店最低价格/晚
    MIN_HOTEL_LUXURY = 300         # 豪华型酒店最低价格/晚
    MIN_FOOD_PER_DAY = 80          # 每日最低餐饮费用
    MIN_ATTRACTION_PER_DAY = 50    # 每日最低景点费用
    
    @staticmethod
    def calculate_days(departure_date: str, return_date: str) -> int:
        """计算旅行天数"""
        try:
            start = datetime.strptime(departure_date, "%Y-%m-%d")
            end = datetime.strptime(return_date, "%Y-%m-%d")
            days = (end - start).days + 1  # 包含出发和返回当天
            return max(1, days)
        except:
            return 1
    
    @staticmethod
    def estimate_min_transport(origin: str, destination: str) -> int:
        """估算最低交通费用"""
        # 简化版：根据城市名称判断距离
        if not origin or not destination:
            return BudgetChecker.MIN_TRANSPORT_NEARBY
        
        if origin == destination:
            return BudgetChecker.MIN_TRANSPORT_LOCAL
        
        # 一线城市间的距离
        tier1_cities = ["北京", "上海", "广州", "深圳"]
        origin_tier1 = any(city in origin for city in tier1_cities)
        dest_tier1 = any(city in destination for city in tier1_cities)
        
        if origin_tier1 and dest_tier1:
            return BudgetChecker.MIN_TRANSPORT_FAR
        
        # 默认邻近城市
        return BudgetChecker.MIN_TRANSPORT_NEARBY
    
    @staticmethod
    def estimate_min_hotel(hotel_type: str) -> int:
        """估算最低酒店费用/晚"""
        hotel_map = {
            "经济型": BudgetChecker.MIN_HOTEL_ECONOMY,
            "舒适型": BudgetChecker.MIN_HOTEL_COMFORT,
            "豪华型": BudgetChecker.MIN_HOTEL_LUXURY,
            "民宿": BudgetChecker.MIN_HOTEL_ECONOMY,
            "青旅": 50
        }
        return hotel_map.get(hotel_type, BudgetChecker.MIN_HOTEL_COMFORT)
    
    @classmethod
    def check_budget_feasibility(cls, travel_info: Dict, actual_costs: Dict = None) -> Tuple[bool, str, Dict]:
        """
        检查预算是否可行
        
        Args:
            travel_info: 旅行信息字典
            actual_costs: 实际费用信息（可选），包含：
                - transport: 实际交通费用
                - hotel_per_night: 实际酒店单价
                - attraction_total: 实际景点门票总费用
            
        Returns:
            (是否可行, 提示信息, 费用明细)
        """
        try:
            budget = float(travel_info.get('budget', 0))
            if budget <= 0:
                return True, "", {}
            
            departure_date = travel_info.get('departureDate', '')
            return_date = travel_info.get('returnDate', '')
            origin = travel_info.get('departureCity', '')
            destination = travel_info.get('destination', '')
            hotel_type = travel_info.get('hotelPreference', '舒适型')
            
            # 计算天数
            days = cls.calculate_days(departure_date, return_date)
            
            # 使用实际费用或估算最低费用
            if actual_costs:
                min_transport = actual_costs.get('transport', cls.estimate_min_transport(origin, destination))
                min_hotel_per_night = actual_costs.get('hotel_per_night', cls.estimate_min_hotel(hotel_type))
                min_attraction = actual_costs.get('attraction_total', cls.MIN_ATTRACTION_PER_DAY * days)
            else:
                min_transport = cls.estimate_min_transport(origin, destination)
                min_hotel_per_night = cls.estimate_min_hotel(hotel_type)
                min_attraction = cls.MIN_ATTRACTION_PER_DAY * days
            
            min_hotel_total = min_hotel_per_night * max(0, days - 1)  # 最后一天不住酒店
            min_food = cls.MIN_FOOD_PER_DAY * days
            
            min_total = min_transport + min_hotel_total + min_food + min_attraction
            
            # 费用明细
            breakdown = {
                'days': days,
                'transport': min_transport,
                'hotel': min_hotel_total,
                'food': min_food,
                'attraction': min_attraction,
                'total': min_total,
                'budget': budget,
                'surplus': budget - min_total,
                'using_actual_costs': bool(actual_costs)  # 标记是否使用了实际费用
            }
            
            # 判断是否可行（预留20%缓冲）
            recommended_budget = min_total * 1.2
            
            # 构建费用说明（区分估算和实际）
            cost_type = "实际查询" if actual_costs else "最低估算"
            
            if budget < min_total:
                message = (
                    f"⚠️ 预算不足警告\n\n"
                    f"您的预算：{budget:.0f}元\n"
                    f"最低预算：{min_total:.0f}元\n"
                    f"预算缺口：{min_total - budget:.0f}元\n\n"
                    f"费用明细（{cost_type}）：\n"
                    f"- 交通费用：{min_transport:.0f}元\n"
                    f"- 住宿费用：{min_hotel_total:.0f}元（{max(0, days-1)}晚 × {min_hotel_per_night:.0f}元）\n"
                    f"- 餐饮费用：{min_food:.0f}元（{days}天 × {cls.MIN_FOOD_PER_DAY}元）\n"
                    f"- 景点费用：{min_attraction:.0f}元（{days}天）\n\n"
                    f"建议：\n"
                    f"1. 增加预算至 {recommended_budget:.0f}元 以上\n"
                    f"2. 选择更近的目的地以降低交通费用\n"
                    f"3. 缩短旅行天数\n"
                    f"4. 选择更经济的住宿类型"
                )
                return False, message, breakdown
            
            elif budget < recommended_budget:
                message = (
                    f"💡 预算提示\n\n"
                    f"您的预算：{budget:.0f}元\n"
                    f"最低预算：{min_total:.0f}元（{cost_type}）\n"
                    f"建议预算：{recommended_budget:.0f}元\n\n"
                    f"您的预算刚好够用，但建议增加预算以获得更好的旅行体验。"
                )
                return True, message, breakdown
            
            else:
                message = f"✅ 预算充足（预算：{budget:.0f}元，最低需求：{min_total:.0f}元，{cost_type}）"
                return True, message, breakdown
                
        except Exception as e:
            return True, f"预算检查失败：{str(e)}", {}


def check_budget(travel_info: Dict, actual_costs: Dict = None) -> Tuple[bool, str, Dict]:
    """
    便捷函数：检查预算是否可行
    
    Args:
        travel_info: 旅行信息字典
        actual_costs: 实际费用信息（可选），包含：
            - transport: 实际交通费用
            - hotel_per_night: 实际酒店单价
            - attraction_total: 实际景点门票总费用
        
    Returns:
        (是否可行, 提示信息, 费用明细)
    """
    return BudgetChecker.check_budget_feasibility(travel_info, actual_costs)

