let chart;
let chartType = "weekly"; // Default chart type

// Function to fetch data from the backend
async function fetchData() {
    try {
        const response = await fetch(`/data/${chartType}`);
        if (!response.ok) {
            throw new Error("Unauthorized or error fetching data");
        }
        const data = await response.json();
        return data;
    } catch (error) {
        console.error("Error fetching data:", error);
    }
}

// Function to update the chart dynamically
async function updateChart() {
    const data = await fetchData();
    
    if (!data || data.length === 0) {
        console.warn("No data available to display.");
        return;
    }

    const labels = data.map(item => item[0]); // X-axis labels (dates/weeks/months)
    const ratings = data.map(item => item[1]); // Y-axis ratings

    if (chart) {
        chart.destroy(); // Destroy the previous chart instance
    }

    const ctx = document.getElementById("ratingChart").getContext("2d");
    chart = new Chart(ctx, {
        type: "line",
        data: {
            labels: labels,
            datasets: [{
                label: `Your ${chartType} Ratings`,
                data: ratings,
                borderColor: "#ffffff",
                backgroundColor: "rgba(255, 255, 255, 0.2)",
                borderWidth: 2,
                fill: true,
                tension: 0.3,
                pointBackgroundColor: "#ffffff",
                pointRadius: 5
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: { display: false }
            },
            scales: {
                x: {
                    ticks: { color: "#ffffff" },
                    grid: { color: "rgba(255, 255, 255, 0.2)" }
                },
                y: {
                    min: 0,
                    max: 10,
                    ticks: { stepSize: 1, color: "#ffffff" },
                    grid: { color: "rgba(255, 255, 255, 0.2)" }
                }
            }
        }
    });
}

// Function to handle rating submission
async function submitRating() {
    const rating = document.getElementById("rating").value;
    
    if (!rating || rating < 1 || rating > 10) {
        alert("Please enter a valid rating between 1 and 10.");
        return;
    }

    try {
        const response = await fetch("/submit", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ rating: rating })
        });

        const result = await response.json();
        if (!response.ok) {
            alert(result.error || "Error submitting rating");
            return;
        }
    } catch (error) {
        console.error("Error submitting rating:", error);
    }
    
    document.getElementById("rating").value = ""; // Clear input field
    updateChart(); // Refresh the chart with new data
}

// Event listener for chart type dropdown change
document.getElementById("chartType").addEventListener("change", function () {
    chartType = this.value;
    updateChart();
});

// Load the chart on page load
document.addEventListener("DOMContentLoaded", updateChart);