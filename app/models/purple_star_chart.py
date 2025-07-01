from typing import Optional

class PurpleStarChart:
    def find_star_palace(self, target_star: str) -> Optional[str]:
        """
        找到指定星曜所在的宮位
        
        Args:
            target_star: 要查找的星曜名稱
            
        Returns:
            宮位名稱，如果找不到則返回 None
        """
        for palace_name, palace_info in self.palaces.items():
            for star in palace_info.stars:
                # 提取星曜名稱（去除狀態描述和四化標記）
                clean_star_name = star.split("（")[0] if "（" in star else star
                clean_star_name = clean_star_name.replace("化祿", "").replace("化權", "").replace("化科", "").replace("化忌", "")
                
                if clean_star_name == target_star:
                    return palace_name
        
        return None 