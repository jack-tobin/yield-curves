import { Utils } from "../core/utils.js";

/**
 * Chart management functionality using Chart.js
 */
export class ChartManager {
  constructor() {
    this.bondChart = null;
    this.zeroCurveData = new Map(); // Store zero curve data by scatter ID
    this.colors = [
      "rgba(54, 162, 235, 0.8)", // Blue
      "rgba(255, 99, 132, 0.8)", // Red
      "rgba(75, 192, 192, 0.8)", // Teal
      "rgba(255, 206, 86, 0.8)", // Yellow
      "rgba(153, 102, 255, 0.8)", // Purple
      "rgba(255, 159, 64, 0.8)", // Orange
      "rgba(199, 199, 199, 0.8)", // Grey
      "rgba(83, 102, 255, 0.8)", // Indigo
      "rgba(255, 99, 255, 0.8)", // Pink
      "rgba(99, 255, 132, 0.8)", // Green
    ];
  }

  async loadAllSelectedScatters() {
    const selectedScatters = Array.from(
      document.querySelectorAll('.scatter-chip[data-visible="true"]'),
    ).map((chip) => chip.dataset.scatterId);

    if (selectedScatters.length === 0) {
      this.initializeEmptyChart();
      document.getElementById("chart-info").innerHTML = "";
      return;
    }

    try {
      const response = await fetch(
        `/yield-curves/analysis/${window.ANALYSIS_ID}/scatter/data/`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": Utils.getCsrfToken(),
          },
          body: JSON.stringify({ scatter_ids: selectedScatters }),
        },
      );

      const selectedData = await response.json();

      if (selectedData.length > 0) {
        this.createMultiScatterChart(selectedData);
      } else {
        this.initializeEmptyChart();
        document.getElementById("chart-info").innerHTML = "";
      }
    } catch (error) {
      console.error("Error loading scatter data:", error);
      this.initializeEmptyChart();
    }
  }

  async loadZeroCurveData(scatterId) {
    try {
      const response = await fetch(
        `/yield-curves/analysis/${window.ANALYSIS_ID}/scatter/${scatterId}/zero-curve/`,
        {
          method: "GET",
          headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": Utils.getCsrfToken(),
          },
        },
      );

      const zeroCurveData = await response.json();

      if (zeroCurveData.success) {
        this.zeroCurveData.set(scatterId, zeroCurveData);
      } else {
        throw new Error(
          zeroCurveData.error || "Failed to load zero curve data",
        );
      }
    } catch (error) {
      console.error("Error loading zero curve data:", error);
      throw error;
    }
  }

  removeZeroCurveData(scatterId) {
    this.zeroCurveData.delete(scatterId);
  }

  createMultiScatterChart(scatterData) {
    const ctx = document.getElementById("bond-scatter-chart").getContext("2d");

    // Destroy existing chart if it exists
    if (this.bondChart) {
      this.bondChart.destroy();
    }

    const datasets = [];

    // Add scatter plot datasets
    scatterData.forEach((scatter) => {
      // Use scatter ID for consistent color assignment
      const colorIndex = scatter.scatter.id % this.colors.length;
      const chartData = scatter.data.map((bond) => ({
        x: bond.ttm_years,
        y: bond.yield,
        isin: bond.isin,
        coupon: bond.coupon,
        maturityDate: bond.maturity_date,
        description: bond.description,
      }));

      datasets.push({
        label: scatter.scatter.display_name,
        data: chartData,
        backgroundColor: this.colors[colorIndex % this.colors.length],
        borderColor: this.colors[colorIndex].replace("0.8", "1"),
        borderWidth: 1,
        pointRadius: 6,
        pointHoverRadius: 8,
        type: "scatter",
      });

      // Add zero curve dataset if enabled
      const scatterId = scatter.scatter.id.toString();
      const chip = document.querySelector(`[data-scatter-id="${scatterId}"]`);
      const isZeroCurveEnabled = chip && chip.dataset.zeroCurve === "true";

      if (isZeroCurveEnabled && this.zeroCurveData.has(scatterId)) {
        const zeroCurve = this.zeroCurveData.get(scatterId);
        const zeroCurveChartData = zeroCurve.data.map((point) => ({
          x: point.ttm_years,
          y: point.zero_rate,
        }));

        datasets.push({
          label: zeroCurve.scatter.display_name,
          data: zeroCurveChartData,
          backgroundColor: "transparent",
          borderColor: this.colors[colorIndex].replace("0.8", "1"),
          borderWidth: 2,
          pointRadius: 0,
          pointHoverRadius: 4,
          type: "line",
          tension: 0.1,
          fill: false,
        });
      }
    });

    this.bondChart = new Chart(ctx, {
      type: "scatter",
      data: { datasets },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        animation: false, // Disable animations as requested
        scales: {
          x: {
            title: {
              display: true,
              text: "Time to Maturity (Years)",
            },
            beginAtZero: false,
          },
          y: {
            title: {
              display: true,
              text: "Yield (%)",
            },
          },
        },
        plugins: {
          title: {
            display: true,
            text: "Bond Yield vs Time to Maturity - Multi-Scatter Analysis",
          },
          legend: {
            display: true,
            position: "top",
          },
          tooltip: {
            callbacks: {
              title: function (context) {
                const point = context[0];
                if (point.raw.isin) {
                  return `ISIN: ${point.raw.isin}`;
                } else {
                  return `Zero Curve Point`;
                }
              },
              label: function (context) {
                const point = context.raw;
                if (point.isin) {
                  // Bond scatter point
                  return [
                    `Dataset: ${context.dataset.label}`,
                    `TTM: ${point.x} years`,
                    `Yield: ${point.y}%`,
                    `Coupon: ${point.coupon}%`,
                    `Maturity: ${point.maturityDate}`,
                    `Description: ${point.description.substring(0, 50)}...`,
                  ];
                } else {
                  // Zero curve point
                  return [
                    `Dataset: ${context.dataset.label}`,
                    `TTM: ${point.x} years`,
                    `Zero Rate: ${point.y}%`,
                  ];
                }
              },
            },
          },
        },
      },
    });
  }

  initializeEmptyChart() {
    const ctx = document.getElementById("bond-scatter-chart").getContext("2d");

    // Destroy existing chart if it exists
    if (this.bondChart) {
      this.bondChart.destroy();
    }

    this.bondChart = new Chart(ctx, {
      type: "scatter",
      data: { datasets: [] },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        animation: false, // Disable animations as requested
        scales: {
          x: {
            title: {
              display: true,
              text: "Time to Maturity (Years)",
            },
            beginAtZero: false,
          },
          y: {
            title: {
              display: true,
              text: "Yield (%)",
            },
          },
        },
        plugins: {
          title: {
            display: true,
            text: "Bond Yield vs Time to Maturity",
          },
          legend: {
            display: false,
          },
        },
      },
    });
  }
  destroy() {
    if (this.bondChart) {
      this.bondChart.destroy();
      this.bondChart = null;
    }
    this.zeroCurveData.clear();
  }
}
