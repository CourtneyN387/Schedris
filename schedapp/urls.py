from django.shortcuts import render
from django.urls import path
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('home/', views.home, name='home'),
    path('advisor/', views.AdvisorIndexView.as_view(), name='advisor'),
    path('advisor/schedule-list/', views.AdvisorScheduleListView.as_view(), name='advisor-schedule-list'),
    path('advisor/schedule-detail-<int:pk>/', views.AdvisorScheduleDetailView.as_view(), name='advisor-schedule-detail'),
    path('student/', views.StudentIndexView.as_view(), name='student'),
    path('courses/', views.course_list, name='course_list'),
    path('student/schedule-list/', views.StudentScheduleListView.as_view(), name='student-schedule-list'),
    path('student/schedule-detail-<int:pk>/', views.StudentScheduleDetailView.as_view(), name='student-schedule-detail'),
    path('student/schedule-add-course/', views.student_schedule_add_course, name='student-schedule-add-course'),
    path('student/schedule-remove-course/', views.student_schedule_remove_course, name='student-schedule-remove-course'),
    path('student/schedule-create/', views.ScheduleCreateView.as_view(), name='schedule-create'),
    path('student/schedule-delete-<int:pk>/', views.ScheduleDeleteView.as_view(), name='schedule-delete'),
    path('FAQ/', views.FAQ, name='FAQ'),
    path('About/', views.About, name='About'),
    path('shopping_cart/', views.shopping_cart, name='shopping_cart'),
    path('add_to_cart/<int:class_nbr>/<int:strm>/', views.add_to_cart, name='add_to_cart'),
    path('remove_from_cart/<int:class_nbr>/', views.remove_from_cart, name='remove_from_cart'),
    path('schedule-list/', views.schedule_list, name='schedule-list'),
    path('schedule-detail-<int:pk>/', views.schedule_detail, name='schedule-detail'),
    path('schedule-change-approval-status', views.schedule_change_approval_status, name='schedule-change-approval-status'),
    path('flexible-index/', views.flexible_index, name='flexible-index'),
]
urlpatterns += staticfiles_urlpatterns()