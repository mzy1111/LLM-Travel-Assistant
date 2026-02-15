"""日志工具模块，提供清晰的日志格式"""
import datetime
from typing import Optional


class AgentLogger:
    """智能体日志记录器"""
    
    def __init__(self, verbose: bool = True):
        self.verbose = verbose
        self.separator = "=" * 80
        self.sub_separator = "-" * 80
    
    def log_agent_call_start(self, agent_name: str, query: Optional[str] = None):
        """记录智能体调用开始"""
        if not self.verbose:
            return
        
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"\n{self.separator}", flush=True)
        print(f"[AGENT] [{timestamp}] 调用智能体: {agent_name}", flush=True)
        print(f"{self.sub_separator}", flush=True)
        if query:
            # 限制查询长度，避免日志过长
            query_preview = query[:200] + "..." if len(query) > 200 else query
            print(f"[QUERY] 查询内容: {query_preview}", flush=True)
            print(f"{self.sub_separator}", flush=True)
    
    def log_agent_call_end(self, agent_name: str, success: bool = True, 
                          response_length: Optional[int] = None, 
                          error: Optional[str] = None):
        """记录智能体调用结束"""
        if not self.verbose:
            return
        
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        status = "[OK] 成功" if success else "[ERROR] 失败"
        print(f"{self.sub_separator}", flush=True)
        print(f"{status} [{timestamp}] {agent_name} 执行完成", flush=True)
        if response_length is not None:
            print(f"[STATS] 响应长度: {response_length} 字符", flush=True)
        if error:
            print(f"[ERROR] 错误信息: {error}", flush=True)
        print(f"{self.separator}\n", flush=True)
    
    def log_info(self, message: str):
        """记录一般信息"""
        if not self.verbose:
            return
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[INFO] [{timestamp}] {message}", flush=True)
    
    def log_warning(self, message: str):
        """记录警告信息"""
        if not self.verbose:
            return
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[WARN] [{timestamp}] {message}", flush=True)
    
    def log_error(self, message: str, error: Optional[Exception] = None):
        """记录错误信息"""
        if not self.verbose:
            return
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[ERROR] [{timestamp}] {message}", flush=True)
        if error:
            print(f"   错误详情: {str(error)}", flush=True)
    
    def log_section(self, title: str):
        """记录章节标题"""
        if not self.verbose:
            return
        print(f"\n{self.sub_separator}", flush=True)
        print(f"[SECTION] {title}", flush=True)
        print(f"{self.sub_separator}", flush=True)
    
    def log_api_call(self, api_name: str, status: str, details: Optional[str] = None):
        """记录第三方API调用状态"""
        if not self.verbose:
            return
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        status_icon = "[OK]" if status == "成功" else "[ERROR]" if status == "失败" else "[WARN]"
        print(f"  {status_icon} [{timestamp}] {api_name}: {status}", flush=True)
        if details:
            print(f"     详情: {details}", flush=True)
    
    def log_fallback(self, service_name: str, reason: str):
        """记录使用兜底方案"""
        if not self.verbose:
            return
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"  [FALLBACK] [{timestamp}] 使用兜底方案: {service_name}", flush=True)
        print(f"     原因: {reason}", flush=True)
    
    def log_weather_result(self, city: str, date: str, result: str):
        """记录天气查询结果到终端日志"""
        if not self.verbose:
            return
        
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"  [RESULT] [{timestamp}] 天气查询结果:", flush=True)
        print(f"     城市: {city}", flush=True)
        print(f"     日期: {date}", flush=True)
        print(f"     结果: {result}", flush=True)

