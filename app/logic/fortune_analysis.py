"""
個人運勢分析邏輯模組
包含流年、流月、流日運勢計算功能
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session

from app.logic.purple_star_chart import PurpleStarChart
from app.logic.user_binding import UserBindingManager
from app.models.user_birth_info import UserBirthInfo

logger = logging.getLogger(__name__)

class FortuneAnalyzer:
    """個人運勢分析器"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_user_birth_chart(self, user_id: str) -> Optional[PurpleStarChart]:
        """獲取用戶的本命盤"""
        try:
            birth_info = UserBindingManager.get_user_birth_info(user_id, self.db)
            if not birth_info:
                return None
            
            chart = PurpleStarChart(
                year=birth_info['year'],
                month=birth_info['month'],
                day=birth_info['day'],
                hour=birth_info['hour'],
                minute=birth_info['minute'],
                gender=birth_info['gender'],
                db=self.db
            )
            
            return chart
            
        except Exception as e:
            logger.error(f"獲取用戶命盤失敗 {user_id}: {e}")
            return None
    
    def analyze_annual_fortune(self, user_id: str, target_year: Optional[int] = None) -> Dict[str, Any]:
        """分析流年運勢"""
        try:
            if target_year is None:
                target_year = datetime.now().year
            
            base_chart = self.get_user_birth_chart(user_id)
            if not base_chart:
                return {"error": "未找到用戶命盤資訊"}
            
            # 計算流年盤
            annual_chart = self._calculate_annual_chart(base_chart, target_year)
            
            # 分析流年運勢
            fortune_analysis = self._analyze_annual_aspects(base_chart, annual_chart, target_year)
            
            return {
                "type": "annual_fortune",
                "target_year": target_year,
                "analysis": fortune_analysis,
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"流年運勢分析失敗 {user_id}: {e}")
            return {"error": "流年運勢分析失敗"}
    
    def analyze_monthly_fortune(self, user_id: str, target_year: Optional[int] = None, 
                               target_month: Optional[int] = None) -> Dict[str, Any]:
        """分析流月運勢"""
        try:
            now = datetime.now()
            if target_year is None:
                target_year = now.year
            if target_month is None:
                target_month = now.month
            
            base_chart = self.get_user_birth_chart(user_id)
            if not base_chart:
                return {"error": "未找到用戶命盤資訊"}
            
            # 計算流月盤
            monthly_chart = self._calculate_monthly_chart(base_chart, target_year, target_month)
            
            # 分析流月運勢
            fortune_analysis = self._analyze_monthly_aspects(base_chart, monthly_chart, target_year, target_month)
            
            return {
                "type": "monthly_fortune",
                "target_year": target_year,
                "target_month": target_month,
                "analysis": fortune_analysis,
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"流月運勢分析失敗 {user_id}: {e}")
            return {"error": "流月運勢分析失敗"}
    
    def analyze_daily_fortune(self, user_id: str, target_date: Optional[datetime] = None) -> Dict[str, Any]:
        """分析流日運勢"""
        try:
            if target_date is None:
                target_date = datetime.now()
            
            base_chart = self.get_user_birth_chart(user_id)
            if not base_chart:
                return {"error": "未找到用戶命盤資訊"}
            
            # 計算流日盤
            daily_chart = self._calculate_daily_chart(base_chart, target_date)
            
            # 分析流日運勢
            fortune_analysis = self._analyze_daily_aspects(base_chart, daily_chart, target_date)
            
            return {
                "type": "daily_fortune",
                "target_date": target_date.strftime("%Y-%m-%d"),
                "analysis": fortune_analysis,
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"流日運勢分析失敗 {user_id}: {e}")
            return {"error": "流日運勢分析失敗"}
    
    def _calculate_annual_chart(self, base_chart: PurpleStarChart, target_year: int) -> Dict[str, Any]:
        """計算流年盤"""
        # 這裡實現流年盤的計算邏輯
        # 基於本命盤和目標年份計算流年星曜分佈
        
        annual_data = {
            "year": target_year,
            "annual_stars": self._get_annual_stars(target_year),
            "four_transformations": self._get_annual_four_transformations(target_year),
            "major_aspects": self._get_annual_major_aspects(base_chart, target_year)
        }
        
        return annual_data
    
    def _calculate_monthly_chart(self, base_chart: PurpleStarChart, target_year: int, 
                                target_month: int) -> Dict[str, Any]:
        """計算流月盤"""
        monthly_data = {
            "year": target_year,
            "month": target_month,
            "monthly_stars": self._get_monthly_stars(target_year, target_month),
            "four_transformations": self._get_monthly_four_transformations(target_year, target_month),
            "major_aspects": self._get_monthly_major_aspects(base_chart, target_year, target_month)
        }
        
        return monthly_data
    
    def _calculate_daily_chart(self, base_chart: PurpleStarChart, target_date: datetime) -> Dict[str, Any]:
        """計算流日盤"""
        daily_data = {
            "date": target_date.strftime("%Y-%m-%d"),
            "daily_stars": self._get_daily_stars(target_date),
            "four_transformations": self._get_daily_four_transformations(target_date),
            "major_aspects": self._get_daily_major_aspects(base_chart, target_date)
        }
        
        return daily_data
    
    def _analyze_annual_aspects(self, base_chart: PurpleStarChart, annual_chart: Dict[str, Any], 
                               target_year: int) -> Dict[str, Any]:
        """分析流年運勢各個面向"""
        analysis = {
            "overall_fortune": self._get_annual_overall_fortune(target_year),
            "career_fortune": self._get_annual_career_fortune(base_chart, annual_chart),
            "wealth_fortune": self._get_annual_wealth_fortune(base_chart, annual_chart),
            "relationship_fortune": self._get_annual_relationship_fortune(base_chart, annual_chart),
            "health_fortune": self._get_annual_health_fortune(base_chart, annual_chart),
            "key_months": self._get_annual_key_months(target_year),
            "suggestions": self._get_annual_suggestions(base_chart, annual_chart)
        }
        
        return analysis
    
    def _analyze_monthly_aspects(self, base_chart: PurpleStarChart, monthly_chart: Dict[str, Any],
                                target_year: int, target_month: int) -> Dict[str, Any]:
        """分析流月運勢各個面向"""
        analysis = {
            "overall_fortune": self._get_monthly_overall_fortune(target_year, target_month),
            "career_fortune": self._get_monthly_career_fortune(base_chart, monthly_chart),
            "wealth_fortune": self._get_monthly_wealth_fortune(base_chart, monthly_chart),
            "relationship_fortune": self._get_monthly_relationship_fortune(base_chart, monthly_chart),
            "health_fortune": self._get_monthly_health_fortune(base_chart, monthly_chart),
            "key_days": self._get_monthly_key_days(target_year, target_month),
            "suggestions": self._get_monthly_suggestions(base_chart, monthly_chart)
        }
        
        return analysis
    
    def _analyze_daily_aspects(self, base_chart: PurpleStarChart, daily_chart: Dict[str, Any],
                              target_date: datetime) -> Dict[str, Any]:
        """分析流日運勢各個面向"""
        analysis = {
            "overall_fortune": self._get_daily_overall_fortune(target_date),
            "career_fortune": self._get_daily_career_fortune(base_chart, daily_chart),
            "wealth_fortune": self._get_daily_wealth_fortune(base_chart, daily_chart),
            "relationship_fortune": self._get_daily_relationship_fortune(base_chart, daily_chart),
            "health_fortune": self._get_daily_health_fortune(base_chart, daily_chart),
            "lucky_hours": self._get_daily_lucky_hours(target_date),
            "suggestions": self._get_daily_suggestions(base_chart, daily_chart)
        }
        
        return analysis
    
    # 以下是具體的運勢計算方法，這裡提供簡化版實現
    
    def _get_annual_stars(self, year: int) -> Dict[str, Any]:
        """獲取流年星曜"""
        # 簡化實現，實際應該根據紫微斗數規則計算
        return {"annual_stars": f"{year}年流年星曜配置"}
    
    def _get_annual_four_transformations(self, year: int) -> Dict[str, Any]:
        """獲取流年四化"""
        return {"four_transformations": f"{year}年四化配置"}
    
    def _get_annual_major_aspects(self, base_chart: PurpleStarChart, year: int) -> List[str]:
        """獲取流年重要相位"""
        return [f"{year}年重要相位1", f"{year}年重要相位2"]
    
    def _get_annual_overall_fortune(self, year: int) -> str:
        """獲取流年整體運勢"""
        fortunes = [
            f"{year}年整體運勢平穩，適合穩健發展。",
            f"{year}年變化較多，需要靈活應對。",
            f"{year}年機會良多，宜積極把握。",
            f"{year}年需要謹慎行事，避免衝動。",
            f"{year}年財運亨通，事業有成。"
        ]
        return fortunes[year % len(fortunes)]
    
    def _get_annual_career_fortune(self, base_chart: PurpleStarChart, annual_chart: Dict[str, Any]) -> str:
        """獲取流年事業運勢"""
        return "事業運勢穩定，有升遷機會。建議把握貴人相助的時機。"
    
    def _get_annual_wealth_fortune(self, base_chart: PurpleStarChart, annual_chart: Dict[str, Any]) -> str:
        """獲取流年財運"""
        return "財運尚佳，正財穩定，偏財小有收穫。投資需謹慎。"
    
    def _get_annual_relationship_fortune(self, base_chart: PurpleStarChart, annual_chart: Dict[str, Any]) -> str:
        """獲取流年感情運勢"""
        return "感情運勢平穩，單身者有機會遇到合適對象。"
    
    def _get_annual_health_fortune(self, base_chart: PurpleStarChart, annual_chart: Dict[str, Any]) -> str:
        """獲取流年健康運勢"""
        return "健康狀況良好，注意作息規律，適度運動。"
    
    def _get_annual_key_months(self, year: int) -> List[str]:
        """獲取流年關鍵月份"""
        return [f"{year}年3月", f"{year}年7月", f"{year}年11月"]
    
    def _get_annual_suggestions(self, base_chart: PurpleStarChart, annual_chart: Dict[str, Any]) -> List[str]:
        """獲取流年建議"""
        return [
            "保持積極樂觀的心態",
            "注重人際關係的維護",
            "在重要決策前多方諮詢",
            "定期檢視目標進度"
        ]
    
    # 流月相關方法（簡化實現）
    def _get_monthly_stars(self, year: int, month: int) -> Dict[str, Any]:
        return {"monthly_stars": f"{year}年{month}月流月星曜"}
    
    def _get_monthly_four_transformations(self, year: int, month: int) -> Dict[str, Any]:
        return {"four_transformations": f"{year}年{month}月四化"}
    
    def _get_monthly_major_aspects(self, base_chart: PurpleStarChart, year: int, month: int) -> List[str]:
        return [f"{year}年{month}月重要相位"]
    
    def _get_monthly_overall_fortune(self, year: int, month: int) -> str:
        fortunes = [
            "本月運勢平穩，適合按部就班。",
            "本月變化較多，需要靈活應對。",
            "本月機會良多，宜積極行動。",
            "本月需要低調行事，避免衝突。"
        ]
        return fortunes[month % len(fortunes)]
    
    def _get_monthly_career_fortune(self, base_chart: PurpleStarChart, monthly_chart: Dict[str, Any]) -> str:
        return "本月工作順利，有機會展現才能。"
    
    def _get_monthly_wealth_fortune(self, base_chart: PurpleStarChart, monthly_chart: Dict[str, Any]) -> str:
        return "本月財運平穩，收支平衡。"
    
    def _get_monthly_relationship_fortune(self, base_chart: PurpleStarChart, monthly_chart: Dict[str, Any]) -> str:
        return "本月人際關係和諧，感情穩定。"
    
    def _get_monthly_health_fortune(self, base_chart: PurpleStarChart, monthly_chart: Dict[str, Any]) -> str:
        return "本月身體健康，精神狀態佳。"
    
    def _get_monthly_key_days(self, year: int, month: int) -> List[str]:
        return [f"{month}月8日", f"{month}月15日", f"{month}月23日"]
    
    def _get_monthly_suggestions(self, base_chart: PurpleStarChart, monthly_chart: Dict[str, Any]) -> List[str]:
        return [
            "保持工作與生活的平衡",
            "注意與同事的溝通協調",
            "適時放鬆心情"
        ]
    
    # 流日相關方法（簡化實現）
    def _get_daily_stars(self, date: datetime) -> Dict[str, Any]:
        return {"daily_stars": f"{date.strftime('%Y-%m-%d')}流日星曜"}
    
    def _get_daily_four_transformations(self, date: datetime) -> Dict[str, Any]:
        return {"four_transformations": f"{date.strftime('%Y-%m-%d')}四化"}
    
    def _get_daily_major_aspects(self, base_chart: PurpleStarChart, date: datetime) -> List[str]:
        return [f"{date.strftime('%Y-%m-%d')}重要相位"]
    
    def _get_daily_overall_fortune(self, date: datetime) -> str:
        fortunes = [
            "今日運勢平穩，適合處理日常事務。",
            "今日活力充沛，適合積極行動。",
            "今日需要謹慎，避免重大決策。",
            "今日貴人運佳，適合尋求協助。"
        ]
        return fortunes[date.day % len(fortunes)]
    
    def _get_daily_career_fortune(self, base_chart: PurpleStarChart, daily_chart: Dict[str, Any]) -> str:
        return "今日工作效率高，適合處理重要任務。"
    
    def _get_daily_wealth_fortune(self, base_chart: PurpleStarChart, daily_chart: Dict[str, Any]) -> str:
        return "今日財運平穩，適合理財規劃。"
    
    def _get_daily_relationship_fortune(self, base_chart: PurpleStarChart, daily_chart: Dict[str, Any]) -> str:
        return "今日人際和諧，適合社交活動。"
    
    def _get_daily_health_fortune(self, base_chart: PurpleStarChart, daily_chart: Dict[str, Any]) -> str:
        return "今日身體狀況良好，精神飽滿。"
    
    def _get_daily_lucky_hours(self, date: datetime) -> List[str]:
        return ["9-11時", "14-16時", "19-21時"]
    
    def _get_daily_suggestions(self, base_chart: PurpleStarChart, daily_chart: Dict[str, Any]) -> List[str]:
        return [
            "保持正面思維",
            "注意時間管理",
            "多與他人交流"
        ]

def format_fortune_result(fortune_data: Dict[str, Any]) -> str:
    """格式化運勢結果為可讀文字"""
    if "error" in fortune_data:
        return f"❌ {fortune_data['error']}"
    
    fortune_type = fortune_data.get("type", "unknown")
    analysis = fortune_data.get("analysis", {})
    
    if fortune_type == "annual_fortune":
        year = fortune_data.get("target_year")
        text = f"📈 {year}年流年運勢\n\n"
        text += f"🔮 整體運勢：\n{analysis.get('overall_fortune', '')}\n\n"
        text += f"💼 事業運勢：\n{analysis.get('career_fortune', '')}\n\n"
        text += f"💰 財運：\n{analysis.get('wealth_fortune', '')}\n\n"
        text += f"💕 感情運勢：\n{analysis.get('relationship_fortune', '')}\n\n"
        text += f"🏥 健康運勢：\n{analysis.get('health_fortune', '')}\n\n"
        
        key_months = analysis.get('key_months', [])
        if key_months:
            text += f"📅 關鍵月份：{', '.join(key_months)}\n\n"
        
        suggestions = analysis.get('suggestions', [])
        if suggestions:
            text += f"💡 建議：\n"
            for i, suggestion in enumerate(suggestions, 1):
                text += f"{i}. {suggestion}\n"
    
    elif fortune_type == "monthly_fortune":
        year = fortune_data.get("target_year")
        month = fortune_data.get("target_month")
        text = f"🌙 {year}年{month}月流月運勢\n\n"
        text += f"🔮 整體運勢：\n{analysis.get('overall_fortune', '')}\n\n"
        text += f"💼 事業：{analysis.get('career_fortune', '')}\n\n"
        text += f"💰 財運：{analysis.get('wealth_fortune', '')}\n\n"
        text += f"💕 感情：{analysis.get('relationship_fortune', '')}\n\n"
        text += f"🏥 健康：{analysis.get('health_fortune', '')}\n\n"
        
        key_days = analysis.get('key_days', [])
        if key_days:
            text += f"📅 關鍵日期：{', '.join(key_days)}\n\n"
    
    elif fortune_type == "daily_fortune":
        date = fortune_data.get("target_date")
        text = f"☀️ {date} 流日運勢\n\n"
        text += f"🔮 整體：{analysis.get('overall_fortune', '')}\n\n"
        text += f"💼 事業：{analysis.get('career_fortune', '')}\n\n"
        text += f"💰 財運：{analysis.get('wealth_fortune', '')}\n\n"
        text += f"💕 感情：{analysis.get('relationship_fortune', '')}\n\n"
        text += f"🏥 健康：{analysis.get('health_fortune', '')}\n\n"
        
        lucky_hours = analysis.get('lucky_hours', [])
        if lucky_hours:
            text += f"🍀 吉時：{', '.join(lucky_hours)}\n\n"
    
    else:
        text = "運勢分析結果格式錯誤"
    
    return text 