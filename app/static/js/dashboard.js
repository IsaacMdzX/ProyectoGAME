// Dashboard Analytics - Chart.js Implementation

let salesChartInstance = null
let topProductsChartInstance = null

document.addEventListener("DOMContentLoaded", () => {
  if (typeof Chart === "undefined") {
    console.error("Chart.js no está cargado")
    return
  }

  cargarResumen()
  cargarVentas(document.getElementById("salesPeriod")?.value || "month")
  cargarTopProductos()
  cargarActividad()
  cargarPedidosRecientes()

  const periodSelect = document.getElementById("salesPeriod")
  if (periodSelect) {
    periodSelect.addEventListener("change", (e) => {
      cargarVentas(e.target.value)
    })
  }
})

async function cargarResumen() {
  try {
    const response = await fetch("/api/admin/dashboard/summary")
    const data = await response.json()
    if (!data.success) throw new Error(data.error || "Error cargando resumen")

    setStat("daily-sales", formatCurrency(data.summary.daily_sales))
    setStat("pending-orders", data.summary.pending_orders)
    setStat("low-stock", data.summary.low_stock)
    setStat("active-customers", data.summary.active_customers)
  } catch (error) {
    console.error("Error cargando resumen:", error)
  }
}

async function cargarVentas(period) {
  try {
    const response = await fetch(`/api/admin/dashboard/sales?period=${period}`)
    const data = await response.json()
    if (!data.success) throw new Error(data.error || "Error cargando ventas")

    renderSalesChart(data.chart.labels, data.chart.data)
  } catch (error) {
    console.error("Error cargando ventas:", error)
  }
}

async function cargarTopProductos() {
  try {
    const response = await fetch("/api/admin/dashboard/top-products")
    const data = await response.json()
    if (!data.success) throw new Error(data.error || "Error cargando top productos")

    renderTopProductsChart(data.chart.labels, data.chart.data)
  } catch (error) {
    console.error("Error cargando top productos:", error)
  }
}

async function cargarActividad() {
  try {
    const response = await fetch("/api/admin/dashboard/recent-activity")
    const data = await response.json()
    if (!data.success) throw new Error(data.error || "Error cargando actividad")

    const container = document.getElementById("activity-grid")
    if (!container) return

    if (!data.activity.length) {
      container.innerHTML = `<div class="no-data">No hay actividad reciente</div>`
      return
    }

    container.innerHTML = data.activity
      .map(
        (item) => `
        <div class="activity-card">
          <div class="activity-icon ${item.icon_class}">${item.icon}</div>
          <div class="activity-content">
            <div class="activity-title">${item.title}</div>
            <div class="activity-description">${item.description}</div>
            <div class="activity-time">${formatTimeAgo(item.timestamp)}</div>
          </div>
        </div>
      `
      )
      .join("")
  } catch (error) {
    console.error("Error cargando actividad:", error)
  }
}

async function cargarPedidosRecientes() {
  try {
    const response = await fetch("/api/admin/dashboard/recent-orders")
    const data = await response.json()
    if (!data.success) throw new Error(data.error || "Error cargando pedidos recientes")

    const tbody = document.getElementById("recent-orders-body")
    if (!tbody) return

    if (!data.orders.length) {
      tbody.innerHTML = `
        <tr>
          <td colspan="7" class="no-data">No hay pedidos recientes</td>
        </tr>
      `
      return
    }

    tbody.innerHTML = data.orders
      .map(
        (pedido) => `
        <tr>
          <td>${pedido.numero_pedido}</td>
          <td>${pedido.cliente}</td>
          <td>${pedido.productos}</td>
          <td>${formatCurrency(pedido.total)}</td>
          <td><span class="status-badge ${pedido.estado}">${pedido.estado_label}</span></td>
          <td>${pedido.fecha}</td>
          <td>
            <div class="action-buttons">
              <button class="btn-icon" title="Ver" onclick="window.location.href='/admin/pedidos'">👁️</button>
              <button class="btn-icon" title="Editar" onclick="window.location.href='/admin/pedidos'">✏️</button>
            </div>
          </td>
        </tr>
      `
      )
      .join("")
  } catch (error) {
    console.error("Error cargando pedidos recientes:", error)
  }
}

function renderSalesChart(labels, data) {
  const ctx = document.getElementById("salesChart")
  if (!ctx) return

  if (salesChartInstance) salesChartInstance.destroy()

  salesChartInstance = new Chart(ctx, {
    type: "line",
    data: {
      labels,
      datasets: [
        {
          label: "Ventas",
          data,
          borderColor: "#a21caf",
          backgroundColor: "rgba(162, 28, 175, 0.1)",
          tension: 0.4,
          fill: true,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          display: false,
        },
      },
      scales: {
        y: {
          beginAtZero: true,
          ticks: {
            callback: (value) => "$" + Number(value).toLocaleString(),
          },
        },
      },
    },
  })
}

function renderTopProductsChart(labels, data) {
  const ctx = document.getElementById("topProductsChart")
  if (!ctx) return

  if (topProductsChartInstance) topProductsChartInstance.destroy()

  topProductsChartInstance = new Chart(ctx, {
    type: "bar",
    data: {
      labels,
      datasets: [
        {
          label: "Unidades Vendidas",
          data,
          backgroundColor: ["#a21caf", "#c026d3", "#d946ef", "#e879f9", "#f0abfc"],
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          display: false,
        },
      },
      scales: {
        y: {
          beginAtZero: true,
        },
      },
    },
  })
}

function setStat(statName, value) {
  const element = document.querySelector(`[data-stat="${statName}"]`)
  if (element) element.textContent = value
}

function formatCurrency(value) {
  const numberValue = Number(value || 0)
  return `$${numberValue.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`
}

function formatTimeAgo(timestamp) {
  if (!timestamp) return ""
  const date = new Date(timestamp)
  const diffMs = Date.now() - date.getTime()
  const diffMin = Math.round(diffMs / 60000)

  if (diffMin < 1) return "Hace unos segundos"
  if (diffMin < 60) return `Hace ${diffMin} minuto${diffMin !== 1 ? "s" : ""}`

  const diffHours = Math.round(diffMin / 60)
  if (diffHours < 24) return `Hace ${diffHours} hora${diffHours !== 1 ? "s" : ""}`

  const diffDays = Math.round(diffHours / 24)
  return `Hace ${diffDays} día${diffDays !== 1 ? "s" : ""}`
}
