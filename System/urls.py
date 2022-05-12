from django.urls import path
from System import views

urlpatterns = [
    path('', views.index),
    path('about/', views.about),
    path('online/', views.online),
    path('online/GA', views.online_GA_train),
    path('online/TA', views.online_TA_train),
    path('online/train', views.online_train),
    path('upload/', views.upload),
    path('statistics/', views.statistics),
    path('history/', views.history),
    path('DA/<int:task_id>', views.data_show),
    path('GA/<int:task_id>', views.GA_algorthm),
    path('TA/<int:task_id>', views.TA_algorthm),
    path('RE/<int:record_id>', views.Result),
    path('DR/<int:record_id>', views.delete_record),
    path('DT/<int:task_id>', views.delete_task),
]
