const ctx = document.getElementById('graph');

new Chart(ctx, {
  type: 'line',
  data: {
    labels: document.getElementById('dates').value.split(','),
    datasets: [{
      label: 'Price',
      data: document.getElementById('prices').value.split(','),
      borderWidth: 2
    }]
  },
  options: {
    responsive: true,
    plugins: {
        title: {
            display: true,
            text: 'Price history chart',
            font: {
              size: 28
            }
        }
    },
    scales: {
      y: {
        beginAtZero: true
      }
    }
  }
});