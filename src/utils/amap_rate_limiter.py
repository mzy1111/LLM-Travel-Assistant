"""高德地图API并发控制模块"""
import threading
import time
from typing import Callable, Any, List
import requests


class AmapRateLimiter:
    """高德地图API并发限流器，限制每秒最多3次请求，最多3个并发请求"""
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(AmapRateLimiter, cls).__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        # 使用信号量控制并发数，最多3个并发请求
        self._semaphore = threading.Semaphore(3)
        # 记录最近3次请求的时间戳（用于控制每秒最多3次）
        self._request_timestamps: List[float] = []
        # 保护时间戳列表的锁
        self._timestamp_lock = threading.Lock()
        self._initialized = True
    
    def _wait_if_needed(self):
        """
        检查是否需要等待，确保每秒最多3次请求
        如果已经连续调用3次，等待1秒
        """
        with self._timestamp_lock:
            current_time = time.time()
            
            # 清理超过1秒的时间戳（只保留最近1秒内的请求）
            self._request_timestamps = [
                ts for ts in self._request_timestamps 
                if current_time - ts < 1.0
            ]
            
            # 如果已经有3次请求在1秒内，需要等待1秒
            if len(self._request_timestamps) >= 3:
                # 等待1秒，确保不会触发频率限制
                time.sleep(1.0)
                # 等待完成后，清理时间戳列表（保留超过1秒的会被清理）
                current_time = time.time()
                self._request_timestamps = [
                    ts for ts in self._request_timestamps 
                    if current_time - ts < 1.0
                ]
            
            # 记录当前请求的时间戳
            self._request_timestamps.append(time.time())
    
    def execute_request(self, request_func: Callable[[], requests.Response]) -> requests.Response:
        """
        执行高德地图API请求，自动控制并发数和请求频率
        
        Args:
            request_func: 返回 requests.Response 的调用函数
            
        Returns:
            requests.Response: API响应
        """
        # 检查并等待，确保每秒最多3次请求
        self._wait_if_needed()
        
        # 获取信号量，如果当前已有3个并发请求，这里会阻塞等待
        self._semaphore.acquire()
        try:
            # 执行请求
            response = request_func()
            return response
        finally:
            # 释放信号量，允许下一个请求执行
            self._semaphore.release()
    
    def get(self, url: str, params: dict = None, timeout: float = 5, **kwargs) -> requests.Response:
        """
        执行GET请求，自动控制并发数和请求频率
        
        Args:
            url: 请求URL
            params: 请求参数
            timeout: 超时时间
            **kwargs: 其他requests.get参数
            
        Returns:
            requests.Response: API响应
        """
        def _request():
            return requests.get(url, params=params, timeout=timeout, **kwargs)
        
        return self.execute_request(_request)


# 创建全局单例实例
_amap_rate_limiter = AmapRateLimiter()


def get_amap_rate_limiter() -> AmapRateLimiter:
    """获取高德地图API限流器实例"""
    return _amap_rate_limiter

