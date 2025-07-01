from dataclasses import dataclass
from typing import List, Dict, Optional

@dataclass
class Star:
    name: str  # 星曜名稱
    element: str  # 五行屬性
    category: str  # 分類（主星、輔星等）
    transformations: List[str]  # 四化（化祿、化權、化科、化忌）
    description: str  # 星曜描述
    strength: Dict[str, int]  # 在不同宮位的強度

class StarRegistry:
    """星曜註冊表，用於管理所有星曜"""
    
    def __init__(self):
        self.stars: Dict[str, Star] = {}
        
    def register_star(self, star: Star):
        """註冊星曜"""
        self.stars[star.name] = star
        
    def get_star(self, name: str) -> Optional[Star]:
        """獲取星曜"""
        return self.stars.get(name)
        
    def get_stars_by_category(self, category: str) -> List[Star]:
        """根據分類獲取星曜"""
        return [star for star in self.stars.values() if star.category == category]
        
    def get_stars_by_element(self, element: str) -> List[Star]:
        """根據五行獲取星曜"""
        return [star for star in self.stars.values() if star.element == element]

# 創建全局星曜註冊表
star_registry = StarRegistry()

# 預留主星定義位置
# 等待安星規則提供後再添加具體的星曜定義 