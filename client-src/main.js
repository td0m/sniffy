// util functions

function get_all_data() {
  response = fetch("http://10.14.138.32:5000/node", {
    cors: "no-cors"
  }).then(resp => resp.json());
  if (response.data == "no match") {
    return {data: {}};
  }
  return response;
}

function get_all_names(data) {
  return data.map((entry) => entry['name']);
}

function formatDate(date) {
  var hours = date.getHours();
  var minutes = date.getMinutes();
  var ampm = hours >= 12 ? 'pm' : 'am';
  hours = hours % 12;
  hours = hours ? hours : 12; // the hour '0' should be '12'
  minutes = minutes < 10 ? '0'+minutes : minutes;
  var strTime = hours + ':' + minutes + ' ' + ampm;
  return strTime;
}

function reform_to_time_series(data) {
  const occ = {}
  data.forEach(function (entry, index) {
    if (entry.name != "") {
      entry.logs.forEach(function (log, index) {
        let date = new Date(Math.round(log.time * 1000));
        let time = formatDate(date)
        occ[time] = (occ[time] || 0) + 1;
      });
    }
  });
  return Object.keys(occ).map((key) => [key, occ[key]]);
}

// build a list that contains all the unique item's count
function statistic_count(array) {
  const occ = {}
  array.forEach((x) => {
    if (x === "") x = "unknown";
    occ[x] = (occ[x] || 0) + 1;
  });
  return Object.keys(occ).map((key) => [key, occ[key]]);
}

// graph op

function draw_graph(graph_wrapper) {
  let data = graph_wrapper.data;
  let options = graph_wrapper.options;
  graph_wrapper.graph.draw(data, options);
}

// graph generating

function getPieChartData(data_counts)
{
  return google.visualization.arrayToDataTable([
    ['Device names', 'counts'],
    ...data_counts
  ]);
}

function getPieChart()
{
  let options = {
    title: 'Devices Counts',
    // pieHole: 0.4,
    animation:{
      duration: 1000,
      easing: 'out',
    },
    is3D: false,
  };

  let chart = new google.visualization.PieChart(document.getElementById('names_piechart'));
  return {graph: chart, data: undefined, options: options};
}

function getHeatChartData(total) {
  return google.visualization.arrayToDataTable([
    ['Traffic', 'Density', { role: 'style' }],
    ['Traffic', total, '#b87333'],            // RGB value
  ]);
}

function getHeatChart()
{
  let options = {
    title: 'Traffic',
    legend: 'none',
    fontSize: 14,
    animation:{
      duration: 1000,
      easing: 'out',
    },
    pieSliceTextStyle: {
      color: 'black',
    },
    pieSliceText: 'value',
  };

  let chart = new google.visualization.PieChart(document.getElementById('traffic_heatChart'));
  return {graph: chart, data: undefined, options: options};
}

function getLineChartData(time_series_data) {
  return google.visualization.arrayToDataTable([
    ['Date', 'Count'],
    ...time_series_data
  ]);
}

function getLineChart() {
  var options = {
    title: 'New devices time line',
    animation:{
      duration: 1000,
      easing: 'out',
    },
    legend: { position: 'bottom' }
  };

  var chart = new google.visualization.LineChart(document.getElementById('line_chart'));
  return {graph: chart, data: undefined, options: options};
}

var device_count_graph = undefined;
var traffice_graph = undefined;
var line_graph = undefined;

function drawChart() {
  draw_graph(device_count_graph);
  draw_graph(traffice_graph);
  draw_graph(line_graph);
}

function update() {
  data = new_data;
  drawChart();
}

(() => {
  google.charts.load('current', {'packages':['corechart']});

  device_count_graph = getPieChart(counts);
  traffice_graph = getHeatChart(total);
  line_graph = getLineChart(time_series);
})();

(async () => {
  //
  let {data} = await get_all_data();
  let time_series = reform_to_time_series(data);
  let counts = statistic_count(get_all_names(data))
  let total = counts.reduce((acc, x) => x[1] + acc, 0);

  device_count_graph.data = getHeatChartData(total);
  traffice_graph.data = getPieChartData(counts);
  line_graph.data = getLineChartData(time_series);

  console.log(counts);
  console.log(time_series);

  google.charts.setOnLoadCallback(drawChart);
})();
