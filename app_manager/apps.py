# -*- coding: utf-8 -*-
from django.apps import AppConfig

class AppManagerConfig(AppConfig):
    name = 'app_manager'

    def ready(self):
        # everytime server restarts
        import app_manager.signals
