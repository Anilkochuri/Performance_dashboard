
function plotlyOrEmpty(elId, fig){
  const el = document.getElementById(elId);
  if (!el) return;
  if (fig && fig.data && fig.layout){
    Plotly.newPlot(el, fig.data, fig.layout, {displayModeBar: true, responsive: true});
  } else {
    el.innerHTML = '<div class="alert alert-info">Chart data not available.</div>';
  }
}

window.renderFigures = function(){
  const figs = window.figures || {};
  plotlyOrEmpty('plt_latency', figs.latency);
  plotlyOrEmpty('plt_topn', figs.topn);
  plotlyOrEmpty('plt_passfail', figs.passfail);
  plotlyOrEmpty('plt_successpie', figs.successpie);
  plotlyOrEmpty('plt_codepie', figs.codepie);
  plotlyOrEmpty('plt_rttrend', figs.rttrend);
  plotlyOrEmpty('plt_throughput', figs.throughput);
};
