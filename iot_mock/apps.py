from django.apps import AppConfig


class IotMockConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'iot_mock'
    verbose_name = 'IoT Cold Chain Monitoring'
    
    def ready(self):
        """Initialize app when Django starts"""
        pass