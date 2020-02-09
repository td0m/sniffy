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

function formatDate(date) {
  const getFrameI = timeUnix => Math.floor(timeUnix / 60 / 10)

  const lastFrame = getFrameI(Date.now() / 1000)
  const frame = getFrameI(date)

  const frameDiff = frame - lastFrame



  return `${frameDiff}`
}

function devices_per_unit_frame(frames) {
  return frames.map((frame) => {
    if (frame.length > 0) {
      return [frame[0].time, frame.length];
    }
    return [-1, 0];
  });
}

// build a list that contains all the unique item's count
function names_count_each_frame(frames) {
  return frames.map((frame) => {
    const occ = {}
    frame.forEach((entry) => {
      if (entry.name === "") entry.name = "unknown";
      occ[entry.name] = (occ[entry.name] || 0) + 1;
    })
    return Object.keys(occ)
      .map((key) => [key, occ[key]])
      .sort((a,b) => a[1] < b[1]);
  });
}

// graph op

function draw_graph(graph_wrapper) {
  let data = graph_wrapper.data;
  let options = graph_wrapper.options;
  console.log("draw", data, options);
  graph_wrapper.graph.draw(data, options);
}

// graph generating

function getPieChartData(data_counts)
{
  console.log(data_counts);
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
  return {graph: chart, data: undefined, options: options, frame_name_counts: undefined};
}

function getHeatChartData(total) {
  console.log("total", total);
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
    // pieSliceTextStyle: {
    //   color: 'black',
    // },
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

var device_count_graph = undefined;
var traffic_graph = undefined;
var line_graph = undefined;

function updatePieChartToMatchLineChart(e) {
  e.row;
}

function getLineChart(device_count_graph) {
  var options = {
    title: 'New devices time line',
    animation:{
      duration: 1000,
      easing: 'out',
    },
    legend: { position: 'bottom' }
  };

  var chart = new google.visualization.LineChart(document.getElementById('line_chart'));

  google.visualization.events.addListener(chart, 'onmouseover', (e) => {
    frame_name_counts = device_count_graph.frame_name_counts;
    device_count_graph.data = getPieChartData(frame_name_counts[e.row]);
    console.log(device_count_graph.data);
    draw_graph(device_count_graph);
  });

  return {graph: chart, data: undefined, options: options};
}

function drawChart() {
  if (!device_count_graph)
    device_count_graph = getPieChart();

  // if (!traffic_graph)
  //   traffic_graph = getHeatChart();

  if (!line_graph)
    line_graph = getLineChart(device_count_graph);

  (async () => {
    //
    let {data} = await get_all_data();
    let time_series = devices_per_unit_frame(data);
    let counts = names_count_each_frame(data);

    device_count_graph.frame_name_counts = counts;

    let total = counts.reduce((acc, x) => x[1] + acc, 0);

    if (counts.length > 0) {
      if (counts[0].length > 0) {
        console.log(counts[0])
        device_count_graph.data = getPieChartData(counts[0]);
        draw_graph(device_count_graph);
      }
    }

    // traffic_graph.data = getHeatChartData(total);
    // draw_graph(traffic_graph);

    line_graph.data = getLineChartData(time_series);
    draw_graph(line_graph);
  })();
}

function test_butn_click() {
  console.log("button clicked");
  drawChart();
}

google.charts.load('current', {'packages':['corechart']});
google.charts.setOnLoadCallback(drawChart);
