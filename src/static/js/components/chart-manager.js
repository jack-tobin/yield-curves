import { API } from "../core/api.js";
import { Utils } from "../core/utils.js";

/**
 * Chart management functionality using Chart.js
 */
export class ChartManager {
  constructor() {
    this.bondChart = null;
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

  createMultiScatterChart(scatterData) {
    const ctx = document.getElementById("bond-scatter-chart").getContext("2d");

    // Destroy existing chart if it exists
    if (this.bondChart) {
      this.bondChart.destroy();
    }

    const datasets = scatterData.map((scatter, index) => {
      const chartData = scatter.data.map((bond) => ({
        x: bond.ttm_years,
        y: bond.yield,
        isin: bond.isin,
        coupon: bond.coupon,
        maturityDate: bond.maturity_date,
        description: bond.description,
      }));

      return {
        label: scatter.scatter.display_name,
        data: chartData,
        backgroundColor: this.colors[index % this.colors.length],
        borderColor: this.colors[index % this.colors.length].replace(
          "0.8",
          "1",
        ),
        borderWidth: 1,
        pointRadius: 6,
        pointHoverRadius: 8,
      };
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
                return `ISIN: ${point.raw.isin}`;
              },
              label: function (context) {
                const point = context.raw;
                return [
                  `Dataset: ${context.dataset.label}`,
                  `TTM: ${point.x} years`,
                  `Yield: ${point.y}%`,
                  `Coupon: ${point.coupon}%`,
                  `Maturity: ${point.maturityDate}`,
                  `Description: ${point.description.substring(0, 50)}...`,
                ];
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
  }
}
