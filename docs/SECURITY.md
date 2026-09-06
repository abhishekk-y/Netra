# Security Measures

1. **Database Encryption**: Sensitive fields (like passwords) use `pgcrypto`.
2. **API Security**: FastAPI endpoints are protected by JWT Bearer authentication.
3. **RBAC**: Users are assigned roles (`admin`, `analyst`, `viewer`).
4. **Sensor Authentication**: Sensors authenticate via pre-shared TLS certificates or static tokens.
