from django.urls import path
from . import views

app_name = "yield_curves"

urlpatterns = [
    path("analyses_list/", views.analyses_list, name="analyses_list"),
    path("analysis/<int:analysis_id>/", views.analysis_detail, name="analysis_detail"),
    path("create_analysis/", views.create_analysis, name="create_analysis"),
    path("delete_analysis/<int:analysis_id>/", views.delete_analysis, name="delete_analysis"),
    path(
        "undo_delete_analysis/<int:analysis_id>/",
        views.undo_delete_analysis,
        name="undo_delete_analysis",
    ),
]
