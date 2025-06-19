import datetime as dt
import json

import numpy as np
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Max, Min
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_http_methods

from src.apps.yield_curves.models import Analysis, BondMetric, BondScatter
from src.constants import DAYS_IN_YEAR
from src.curve_engine.curve_engine import YieldCurveCalibrator


@login_required
def analysis_list(request):
    analyses = Analysis.objects.filter(
        user=request.user,
    ).order_by("-updated_at")
    context = {"analyses": analyses}
    return render(request, "yield_curves/analysis_list.html", context)


@login_required
def analysis_detail(request, analysis_id):
    """Detail view for a specific yield curve analysis."""
    analysis = get_object_or_404(Analysis, id=analysis_id, user=request.user)
    bond_scatters = analysis.bond_scatters.all()
    context = {
        "analysis": analysis,
        "bond_scatters": bond_scatters,
    }
    return render(request, "yield_curves/analysis_detail.html", context)


@login_required
def create_analysis(request):
    """Create a new analysis."""
    try:
        data = json.loads(request.body.decode("utf-8"))
        name = data.get("name", "").strip()

        if not name:
            return JsonResponse({"success": False, "error": "Analysis name is required"})

        # Create the analysis
        analysis = Analysis.objects.create(name=name, user=request.user)

        return JsonResponse(
            {
                "success": True,
                "redirect_url": reverse("yield_curves:analysis_detail", args=[analysis.id]),
            }
        )

    except json.JSONDecodeError as e:
        return JsonResponse({"success": False, "error": f"Invalid JSON: {str(e)}"})
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)})


@login_required
def delete_analysis(request, analysis_id):
    """Hard delete a specific analysis."""
    analysis = get_object_or_404(Analysis, id=analysis_id, user=request.user)
    analysis.delete()
    messages.success(request, f"Analysis '{analysis.name}' has been deleted.")
    return redirect("yield_curves:analysis_list")


@login_required
@require_http_methods(["POST"])
def add_bond_scatter(request, analysis_id):
    """Add a new bond scatter to an analysis."""
    analysis = get_object_or_404(Analysis, id=analysis_id, user=request.user)

    try:
        data = json.loads(request.body)
        country = data.get("country", "").upper()
        date_str = data.get("date", "")

        if not country or not date_str:
            return JsonResponse({"error": "Both country and date are required"}, status=400)

        try:
            date = dt.datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            return JsonResponse({"error": "Invalid date format. Use YYYY-MM-DD"}, status=400)

        # Check if this scatter already exists
        if BondScatter.objects.filter(analysis=analysis, country=country, date=date).exists():
            return JsonResponse(
                {"error": f"Scatter for {country} on {date_str} already exists"}, status=400
            )

        # Create the bond scatter
        bond_scatter = BondScatter.objects.create(analysis=analysis, country=country, date=date)

        return JsonResponse(
            {
                "success": True,
                "scatter": {
                    "id": bond_scatter.id,
                    "country": bond_scatter.country,
                    "date": bond_scatter.date.isoformat(),
                    "display_name": f"{bond_scatter.country} {bond_scatter.date.strftime('%b %d, %Y')}",
                },
            }
        )

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON data"}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@login_required
@require_http_methods(["DELETE"])
def delete_bond_scatter(request, analysis_id, scatter_id):
    """Delete a bond scatter from an analysis."""
    analysis = get_object_or_404(Analysis, id=analysis_id, user=request.user)
    bond_scatter = get_object_or_404(BondScatter, id=scatter_id, analysis=analysis)

    bond_scatter.delete()

    return JsonResponse({"success": True})


@login_required
def get_selected_scatters_data(request, analysis_id):
    """Get bond data for selected scatters in an analysis."""
    if request.method != "POST":
        return JsonResponse({"error": "POST request required"}, status=405)

    try:
        data = json.loads(request.body)
        scatter_ids = data.get("scatter_ids", [])

        if not scatter_ids:
            return JsonResponse([])

        analysis = get_object_or_404(Analysis, id=analysis_id, user=request.user)
        bond_scatters = analysis.bond_scatters.filter(id__in=scatter_ids)

        selected_data = []
        for bond_scatter in bond_scatters:
            bond_metrics = bond_scatter.get_bond_data()

            scatter_data = []
            for metric in bond_metrics:
                if metric.ttm < 0:
                    continue  # Exclude bonds with negative time to maturity

                scatter_data.append(
                    {
                        "isin": metric.bond.isin,
                        "ttm_years": round(metric.ttm, 2),
                        "ttm_days": metric.ttm * DAYS_IN_YEAR,
                        "yield": float(metric._yield),
                        "maturity_date": metric.bond.maturity_date.isoformat(),
                        "coupon": float(metric.bond.coupon),
                        "description": metric.bond.description,
                    }
                )

            selected_data.append(
                {
                    "scatter": {
                        "id": bond_scatter.id,
                        "country": bond_scatter.country,
                        "date": bond_scatter.date.isoformat(),
                        "display_name": f"{bond_scatter.country} {bond_scatter.date.strftime('%b %d, %Y')}",
                    },
                    "data": scatter_data,
                    "count": len(scatter_data),
                }
            )

        return JsonResponse(selected_data, safe=False)

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@login_required
def get_zero_curve_data(request, analysis_id, scatter_id):
    """Generate zero curve data for a specific scatter."""
    analysis = get_object_or_404(Analysis, id=analysis_id, user=request.user)
    bond_scatter = get_object_or_404(BondScatter, id=scatter_id, analysis=analysis)

    try:
        # Get bond metrics for this scatter
        bond_metrics = list(bond_scatter.get_bond_data())

        if len(bond_metrics) < 3:
            return JsonResponse({"error": "Need at least 3 bonds to calibrate curve"}, status=400)

        calibrator = YieldCurveCalibrator(bond_metrics, bond_scatter.date)
        calibrator.calibrate()

        # Find max TTM
        max_ttm = max(metric.ttm for metric in bond_metrics)

        all_ttms = np.arange(0.1, max_ttm + 0.1, 0.1)
        zero_curve_data = []
        errors = []
        for ttm in all_ttms:
            try:
                zero_rate = calibrator.zero_rate(ttm) * 100.0  # Convert to percentage
            except RuntimeError as e:
                errors.append(f"Failed to calculate zero rate for TTM {ttm}: {e}")
            else:
                zero_curve_data.append(
                    {"ttm_years": round(ttm, 1), "zero_rate": round(zero_rate, 4)}
                )

        if not zero_curve_data:
            return JsonResponse({"error": f"Failed to generate zero curve:\n{errors}"}, status=500)

        return JsonResponse(
            {
                "success": True,
                "scatter": {
                    "id": bond_scatter.id,
                    "country": bond_scatter.country,
                    "date": bond_scatter.date.isoformat(),
                    "display_name": f"{bond_scatter.country} {bond_scatter.date.strftime('%b %d, %Y')} - Zero Curve",
                },
                "data": zero_curve_data,
                "count": len(zero_curve_data),
            }
        )

    except Exception as e:
        import traceback

        error_msg = traceback.format_exc()
        return JsonResponse(
            {"error": f"Failed to generate zero curve: {str(e)}", "details": error_msg}, status=500
        )


@login_required
def get_bond_date_range(request):
    """Get the available date range for bond data."""
    try:
        date_range = BondMetric.objects.aggregate(min_date=Min("date"), max_date=Max("date"))

        min_date = date_range["min_date"]
        max_date = date_range["max_date"]

        if not min_date or not max_date:
            return JsonResponse({"error": "No bond data available"}, status=404)

        return JsonResponse(
            {
                "min_date": min_date.isoformat(),
                "max_date": max_date.isoformat(),
                "default_date": max_date.isoformat(),  # Default to the most recent date
            }
        )

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
