from typing_extensions import get_args
from django.contrib.admin.sites import gettext_lazy
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
import datetime as dt
from django.utils import timezone

from src.apps.yield_curves.models import Analysis


@login_required
def analyses_list(request):
    analyses = Analysis.objects.filter(
        user=request.user,
        is_deleted=False,
    ).order_by("-updated_at")
    context = {"analyses": analyses}
    return render(request, "yield_curves/analyses_list.html", context)


@login_required
def analysis_detail(request, analysis_id):
    """Detail view for a specific yield curve."""
    analysis = get_object_or_404(Analysis, id=analysis_id, user=request.user)
    context = {"analysis": analysis}
    return render(request, "yield_curves/analysis_detail.html", context)


@login_required
def create_analysis(request):
    """Create a new analysis."""
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        country = request.POST.get("country", "").strip()
        analysis_date = request.POST.get("date")

        # Validation
        errors = []
        if not name:
            errors.append("Analysis name is required.")
        if not country:
            errors.append("Country is required.")
        if not analysis_date:
            errors.append("Analysis date is required.")

        if errors:
            for error in errors:
                messages.error(request, error)
        else:
            # Create the analysis
            analysis = Analysis.objects.create(
                user=request.user, name=name, country=country, date=analysis_date
            )
            messages.success(request, f'Analysis "{name}" created successfully!')
            return redirect("yield_curves:analysis_detail", analysis_id=analysis.id)

    # For GET request, provide today's date as default
    context = {"today": dt.date.today().isoformat()}
    return render(request, "yield_curves/create_analysis.html", context)


@login_required
def delete_analysis(request, analysis_id):
    """Soft delete a specific analysis."""
    analysis = get_object_or_404(Analysis, id=analysis_id, user=request.user, is_deleted=False)
    analysis.is_deleted = True
    analysis.save()

    # Create a message with undo link
    undo_url = request.build_absolute_uri(f"/yield-curves/undo_delete_analysis/{analysis.id}/")
    message_html = f'''Analysis "{analysis.name}" has been deleted.
    <a href="{undo_url}" class="alert-link fw-bold text-decoration-underline">Undo</a>'''

    messages.success(request, message_html, extra_tags="safe")
    return redirect("yield_curves:analyses_list")


@login_required
def undo_delete_analysis(request, analysis_id):
    """Undo soft delete of a specific analysis."""
    analysis = get_object_or_404(Analysis, id=analysis_id, user=request.user, is_deleted=True)
    analysis.is_deleted = False
    analysis.save()

    messages.success(request, f'Analysis "{analysis.name}" has been restored.')
    return redirect("yield_curves:analyses_list")
