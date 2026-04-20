# admin.py
from django.contrib import admin
from .models import License

admin.site.site_header = "P2i widgets licenses"
admin.site.site_title = "P2i widgets licenses"
admin.site.index_title = "Welcome to P2i widgets licenses dashboard"


admin.site.register(License)