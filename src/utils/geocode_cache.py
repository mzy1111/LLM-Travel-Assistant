"""地理编码缓存模块 - 减少重复API调用"""
from typing import Optional, Dict
import time


class GeocodeCache:
    """地理编码缓存类"""
    
    def __init__(self, ttl_seconds: int = 3600):
        """
        初始化缓存
        
        Args:
            ttl_seconds: 缓存过期时间（秒），默认1小时
        """
        self._cache: Dict[str, dict] = {}
        self._ttl = ttl_seconds
        self._stats = {
            'hits': 0,
            'misses': 0,
            'total_requests': 0
        }
    
    def get(self, city: str) -> Optional[dict]:
        """
        从缓存获取地理编码
        
        Args:
            city: 城市名称
            
        Returns:
            地理编码数据，如果不存在或已过期则返回None
        """
        self._stats['total_requests'] += 1
        
        if city not in self._cache:
            self._stats['misses'] += 1
            return None
        
        cache_entry = self._cache[city]
        
        # 检查是否过期
        if time.time() - cache_entry['timestamp'] > self._ttl:
            del self._cache[city]
            self._stats['misses'] += 1
            return None
        
        self._stats['hits'] += 1
        return cache_entry['data']
    
    def set(self, city: str, data: dict):
        """
        设置缓存
        
        Args:
            city: 城市名称
            data: 地理编码数据
        """
        self._cache[city] = {
            'data': data,
            'timestamp': time.time()
        }
    
    def clear(self):
        """清空缓存"""
        self._cache.clear()
        self._stats = {
            'hits': 0,
            'misses': 0,
            'total_requests': 0
        }
    
    def get_stats(self) -> dict:
        """
        获取缓存统计信息
        
        Returns:
            包含命中率等统计信息的字典
        """
        total = self._stats['total_requests']
        hit_rate = (self._stats['hits'] / total * 100) if total > 0 else 0
        
        return {
            'total_requests': total,
            'hits': self._stats['hits'],
            'misses': self._stats['misses'],
            'hit_rate': f"{hit_rate:.2f}%",
            'cache_size': len(self._cache)
        }
    
    def __len__(self):
        """返回缓存大小"""
        return len(self._cache)


# 全局缓存实例
_geocode_cache = GeocodeCache(ttl_seconds=3600)  # 1小时过期


def get_geocode_cache() -> GeocodeCache:
    """获取全局地理编码缓存实例"""
    return _geocode_cache
