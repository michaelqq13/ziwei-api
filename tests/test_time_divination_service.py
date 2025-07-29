"""
指定時間占卜服務單元測試
確保重構後的穩定性
"""
import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

from app.services.time_divination_service import (
    TimeDivinationService,
    TimeDivinationRequest,
    TimeDivinationResponse
)
from app.utils.timezone_helper import TimezoneHelper


class TestTimeDivinationService:
    """指定時間占卜服務測試"""
    
    def test_parse_line_bot_data_success(self):
        """測試 LINE Bot 數據解析成功"""
        # 測試標準格式
        data = "time_gender=M&time=2025-07-28T19:32"
        gender, time_value = TimeDivinationService.parse_line_bot_data(data)
        
        assert gender == "M"
        assert time_value == "2025-07-28T19:32"
    
    def test_parse_line_bot_data_with_now(self):
        """測試解析現在時間"""
        data = "time_gender=F&time=now"
        gender, time_value = TimeDivinationService.parse_line_bot_data(data)
        
        assert gender == "F"
        assert time_value == "now"
    
    def test_parse_line_bot_data_invalid_format(self):
        """測試無效數據格式"""
        with pytest.raises(ValueError):
            TimeDivinationService.parse_line_bot_data("invalid_data")
    
    def test_parse_line_bot_data_invalid_gender(self):
        """測試無效性別"""
        with pytest.raises(ValueError):
            TimeDivinationService.parse_line_bot_data("time_gender=X&time=now")
    
    def test_validate_user_permission_admin(self):
        """測試管理員權限驗證"""
        # Mock 用戶和數據庫
        mock_user = Mock()
        mock_db = Mock()
        
        # Mock permission_manager
        with patch('app.services.time_divination_service.permission_manager') as mock_pm:
            mock_pm.get_user_stats.return_value = {
                "user_info": {"is_admin": True}
            }
            
            result = TimeDivinationService.validate_user_permission(mock_user, mock_db)
            assert result is True
    
    def test_validate_user_permission_non_admin(self):
        """測試非管理員權限驗證"""
        mock_user = Mock()
        mock_db = Mock()
        
        with patch('app.services.time_divination_service.permission_manager') as mock_pm:
            mock_pm.get_user_stats.return_value = {
                "user_info": {"is_admin": False}
            }
            
            result = TimeDivinationService.validate_user_permission(mock_user, mock_db)
            assert result is False


class TestTimeDivinationRequest:
    """請求模型測試"""
    
    def test_valid_request(self):
        """測試有效請求"""
        current_time = TimezoneHelper.get_current_taipei_time()
        target_time = (current_time + timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M")
        
        request = TimeDivinationRequest(
            gender="m",  # 測試小寫轉換
            target_time=target_time,
            purpose="測試占卜"
        )
        
        assert request.gender == "M"  # 應該轉換為大寫
        assert request.target_time == target_time
        assert request.purpose == "測試占卜"
    
    def test_invalid_gender(self):
        """測試無效性別"""
        with pytest.raises(ValueError):
            TimeDivinationRequest(
                gender="X",
                target_time="2025-07-28T19:32",
                purpose="測試"
            )
    
    def test_invalid_time_format(self):
        """測試無效時間格式"""
        with pytest.raises(ValueError):
            TimeDivinationRequest(
                gender="M",
                target_time="invalid_time",
                purpose="測試"
            )
    
    def test_time_too_far_past(self):
        """測試時間太久遠的過去"""
        current_time = TimezoneHelper.get_current_taipei_time()
        past_time = (current_time - timedelta(days=35)).strftime("%Y-%m-%dT%H:%M")
        
        with pytest.raises(ValueError, match="目標時間不能超過 30 天前"):
            TimeDivinationRequest(
                gender="M",
                target_time=past_time,
                purpose="測試"
            )
    
    def test_time_too_far_future(self):
        """測試時間太久遠的未來"""
        current_time = TimezoneHelper.get_current_taipei_time()
        future_time = (current_time + timedelta(days=10)).strftime("%Y-%m-%dT%H:%M")
        
        with pytest.raises(ValueError, match="目標時間不能超過 7 天後"):
            TimeDivinationRequest(
                gender="M",
                target_time=future_time,
                purpose="測試"
            )
    
    def test_purpose_too_long(self):
        """測試占卜目的太長"""
        with pytest.raises(ValueError, match="占卜目的不能超過 100 字符"):
            TimeDivinationRequest(
                gender="M",
                target_time="2025-07-28T19:32",
                purpose="x" * 101  # 101 個字符
            )


class TestTimeDivinationResponse:
    """回應模型測試"""
    
    def test_successful_response(self):
        """測試成功回應"""
        response = TimeDivinationResponse(
            success=True,
            divination_id="123",
            target_time="2025-07-28T19:32:00+08:00",
            current_time="2025-07-29T10:30:00+08:00",
            gender="M",
            taichi_palace="寅宮",
            minute_dizhi="寅",
            palace_tiangan="甲",
            sihua_results=[],
            purpose="測試占卜",
            message="占卜完成"
        )
        
        assert response.success is True
        assert response.divination_id == "123"
        assert response.error is None
    
    def test_error_response(self):
        """測試錯誤回應"""
        response = TimeDivinationResponse(
            success=False,
            target_time="2025-07-28T19:32:00+08:00",
            current_time="2025-07-29T10:30:00+08:00",
            gender="M",
            taichi_palace="",
            minute_dizhi="",
            palace_tiangan="",
            sihua_results=[],
            purpose="測試占卜",
            message="占卜失敗",
            error="權限不足"
        )
        
        assert response.success is False
        assert response.error == "權限不足"
        assert response.divination_id is None


# Pytest fixtures
@pytest.fixture
def mock_user():
    """Mock 用戶對象"""
    user = Mock()
    user.line_user_id = "test_user_123"
    user.id = 1
    user.is_admin.return_value = True
    user.is_premium.return_value = True
    return user

@pytest.fixture
def mock_db():
    """Mock 數據庫會話"""
    return Mock()

# 集成測試（需要實際的數據庫和服務）
@pytest.mark.integration
class TestTimeDivinationServiceIntegration:
    """集成測試"""
    
    @patch('app.services.time_divination_service.get_divination_result')
    def test_execute_time_divination_success(self, mock_get_result, mock_user, mock_db):
        """測試完整的占卜執行流程"""
        # Mock 占卜結果
        mock_get_result.return_value = {
            "success": True,
            "divination_id": 123,
            "taichi_palace": "寅宮",
            "minute_dizhi": "寅",
            "palace_tiangan": "甲",
            "sihua_results": []
        }
        
        # Mock 權限檢查
        with patch.object(TimeDivinationService, 'validate_user_permission', return_value=True):
            result = TimeDivinationService.execute_time_divination(
                user=mock_user,
                gender="M",
                target_time="now",
                db=mock_db,
                purpose="集成測試"
            )
        
        assert result.success is True
        assert result.divination_id == "123"
        assert result.gender == "M"
        assert result.purpose == "集成測試"

# 如果直接運行此文件
if __name__ == "__main__":
    pytest.main([__file__]) 