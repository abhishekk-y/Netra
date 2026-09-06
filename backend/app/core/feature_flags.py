from app.core.config import settings
from fastapi import HTTPException, status

def is_feature_enabled(feature_name: str) -> bool:
    # E.g., FEATURE_ZEEK
    attr_name = f"FEATURE_{feature_name.upper()}"
    return getattr(settings, attr_name, False)

def require_feature(feature_name: str):
    def feature_checker():
        if not is_feature_enabled(feature_name):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Feature {feature_name} is disabled"
            )
        return True
    return feature_checker
