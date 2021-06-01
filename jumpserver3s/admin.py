from django.contrib import admin
from .models import CommandsSequence,Log

class LogAdmin(admin.ModelAdmin):
    list_display = ('log', 'id','user','server','start_time', 'end_time', 'is_finished')
    list_filter = ('user', 'server','is_finished',)
    fieldsets = [
        ('Log Description', {'fields': ('log', 'user', 'server','channel',)}),
        ('Time', {'fields': ('start_time', 'end_time', 'is_finished',)}),
        ('Extra information', {'fields': ('gucamole_client_id',)}),
        ('Dimensions', {'fields': ('width','height',)}),
    ]
    readonly_fields = ('start_time','end_time', 'channel','log', 'gucamole_client_id',)
    search_fields = ['log',]
    ordering = ('log',)
    filter_horizontal = ()

admin.site.register(Log,LogAdmin)

class CommandsSequenceAdmin(admin.ModelAdmin):
    list_display = ('name','commands',)
    list_filter = ('commands', 'group',)
    fieldsets = [
        ('Commands Sequence Description', {'fields': ('name', 'group',)}),
        ('Commands', {'fields': ('commands',)}),
    ]
    search_fields = ['group','commands',]
    ordering = ('name',)
    filter_horizontal = ()

admin.site.register(CommandsSequence,CommandsSequenceAdmin)
