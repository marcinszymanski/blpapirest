from django.conf.urls import patterns, url
from rest_framework.urlpatterns import format_suffix_patterns
from blpapirest import views

urlpatterns = patterns('',
    url(r'^refdata/$', views.RefDataView.as_view()),
    url(r'^histdata/$', views.HistDataView.as_view()),
)

urlpatterns = format_suffix_patterns(urlpatterns)