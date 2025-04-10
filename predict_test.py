from datetime import datetime
from app.models.model_utils import predict

result = predict(32, "2025-04-10", "09:00:00")
print("✅ Prediction Result:", result)
