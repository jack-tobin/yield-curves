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
    path("analysis/<int:analysis_id>/add_scatter/", views.add_bond_scatter, name="add_bond_scatter"),
    path("analysis/<int:analysis_id>/scatter/<int:scatter_id>/delete/", views.delete_bond_scatter, name="delete_bond_scatter"),
    path("analysis/<int:analysis_id>/scatter/<int:scatter_id>/data/", views.get_bond_scatter_data, name="get_bond_scatter_data"),
    path("analysis/<int:analysis_id>/all_scatters_data/", views.get_all_scatters_data, name="get_all_scatters_data"),
]
