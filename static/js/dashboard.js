// dashboard.js — external JS (bundle_v3_1)
(function(){
  // Tabs
  Array.prototype.forEach.call(document.querySelectorAll('.tab'), function(tab){
    tab.addEventListener('click', function(){
      Array.prototype.forEach.call(document.querySelectorAll('.tab'), function(t){ t.classList.remove('active'); });
      Array.prototype.forEach.call(document.querySelectorAll('.panel'), function(p){ p.classList.remove('active'); });
      tab.classList.add('active');
      var target = tab.getAttribute('data-target');
      document.querySelector(target).classList.add('active');
    });
  });

  // Single-chart toggle
  var singleToggle = document.getElementById('singleChart');
  if (singleToggle) {
    singleToggle.addEventListener('change', function(e){
      var enabled = e.target.checked;
      var cards = Array.prototype.slice.call(document.querySelectorAll('.chart-card'));
      if (!enabled) {
        cards.forEach(function(c){ c.style.display = ''; });
        return;
      }
      cards.forEach(function(c, idx){ c.style.display = (idx === 0) ? '' : 'none'; });
      cards.forEach(function(c){
        c.addEventListener('click', function(){
          cards.forEach(function(cc){ cc.style.display = 'none'; });
          c.style.display = '';
        });
      });
    });
  }

  // Metrics
  var METRICS = window.METRICS || {};

  // Helper: common yaxis
  var yAxisResp = { title: 'Seconds', range: [0,12], dticks: 3 };

  // Chart 1: Success vs Fail (Overall)
  (function(){
    var pass = METRICS.overall_pass || 0;
    var fail = METRICS.overall_fail || 0;
    var data = [{ values: [pass, fail], labels: ['Pass','Fail'], type: 'pie', textinfo: 'label+percent', hole: 0.4 }];
    var layout = { margin: {t:20,l:10,r:10,b:10}, height: 320 };
    Plotly.newPlot('chart_success_fail', data, layout, {displayModeBar: false});
  })();

  // Chart 2: Response Code Pie
  (function(){
    var rc = METRICS.response_code_counts || [];
    var labels = rc.map(function(x){ return x.code; });
    var values = rc.map(function(x){ return x.count; });
    var data = [{ values: values.length ? values : [1], labels: labels.length ? labels : ['No data'], type: 'pie', textinfo: 'label+percent' }];
    var layout = { margin: {t:20,l:10,r:10,b:10}, height: 320 };
    Plotly.newPlot('chart_response_code', data, layout, {displayModeBar: false});
  })();

  // Chart 3: Throughput stacked (Transaction vs Pass/Fail)
  (function(){
    var rows = METRICS.per_txn_pass_fail || [];
    var names = rows.map(function(r){ return r.name; });
    var pass = rows.map(function(r){ return r.pass; });
    var fail = rows.map(function(r){ return r.fail; });
    var data = [
      { x: names, y: pass, type: 'bar', name: 'Pass' },
      { x: names, y: fail, type: 'bar', name: 'Fail' }
    ];
    var layout = { barmode: 'stack', margin: {t:20,l:30,r:10,b:80}, height: 360, xaxis: { automargin: true } };
    Plotly.newPlot('chart_throughput', data, layout, {displayModeBar: false});
  })();

  // Chart 4: Average response time per transaction (0–12, dticks=3)
  (function(){
    var rows = METRICS.avg_by_txn || [];
    var names = rows.map(function(r){ return r.name; });
    var values = rows.map(function(r){ return r.average; });
    var data = [{ x: names, y: values, type: 'bar', marker: {color: '#42a5f5'} }];
    var layout = { margin: {t:20,l:50,r:10,b:120}, height: 380, xaxis: { automargin: true, tickangle: -45 }, yaxis: yAxisResp };
    Plotly.newPlot('chart_avg_by_txn', data, layout, {displayModeBar: false});
  })();

  // Chart 5: 90th percentile response time per transaction (0–12, dticks=3)
  (function(){
    var rows = METRICS.p90_by_txn || [];
    var names = rows.map(function(r){ return r.name; });
    var values = rows.map(function(r){ return r.p90; });
    var data = [{ x: names, y: values, type: 'bar', marker: {color: '#ef5350'} }];
    var layout = { margin: {t:20,l:50,r:10,b:120}, height: 380, xaxis: { automargin: true, tickangle: -45 }, yaxis: yAxisResp };
    Plotly.newPlot('chart_p90_by_txn', data, layout, {displayModeBar: false});
  })();

  // Chart 6: Maximum response time per transaction (keep scale same for consistency)
  (function(){
    var rows = METRICS.max_by_txn || [];
    var names = rows.map(function(r){ return r.name; });
    var values = rows.map(function(r){ return r.max; });
    var data = [{ x: names, y: values, type: 'bar', marker: {color: '#ab47bc'} }];
    var layout = { margin: {t:20,l:50,r:10,b:120}, height: 380, xaxis: { automargin: true, tickangle: -45 }, yaxis: yAxisResp };
    Plotly.newPlot('chart_max_by_txn', data, layout, {displayModeBar: false});
  })();
})();
