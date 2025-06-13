from django.urls import path
from . import views

app_name = "yield_curves"

urlpatterns = [
    path("analysis/", views.analysis_list, name="analysis_list"),
    path("analysis/<int:analysis_id>/", views.analysis_detail, name="analysis_detail"),
    path("analysis/create", views.create_analysis, name="create_analysis"),
    path("analysis/<int:analysis_id>/delete", views.delete_analysis, name="delete_analysis"),
    path("analysis/<int:analysis_id>/undo_delete", views.undo_delete_analysis, name="undo_delete_analysis"),
    path("analysis/<int:analysis_id>/scatter/add", views.add_bond_scatter, name="add_bond_scatter"),
    path("analysis/<int:analysis_id>/scatter/<int:scatter_id>/delete/", views.delete_bond_scatter, name="delete_bond_scatter"),
    path("analysis/<int:analysis_id>/scatter/data/", views.get_selected_scatters_data, name="get_selected_scatters_data"),
]
