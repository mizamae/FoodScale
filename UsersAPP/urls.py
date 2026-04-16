from django.urls import path
from . import views

urlpatterns = [
    path("firstlogin/<uuid:user_uuid>", views.firstLogin, name="UsersAPP_firstLogin"),
    path("permissiondenied", views.permissionDenied, name="UsersAPP_permissionDenied"),
    path("myplace/", views.myplace , name="UserAPP_myPlace"),
    path("addweight/<negint:dayOffset>", views.addWeight , name="UsersAPP_addWeight"),
    path("changepassword/", views.changePassword , name="UsersAPP_changePassword"),
    path("changepasswordfirsttime/<uuid:user_uuid>", views.changePasswordFirstTime , name="UsersAPP_changePasswordFirstTime"),
]

