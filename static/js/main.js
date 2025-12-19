(function(){
  function el(id){ return document.getElementById(id); }
  function renderTable(targetId, rows){
    const target = el(targetId); if(!target) return;
    if(!rows || !rows.length){ target.innerHTML = '<div class="empty">No data available.</div>'; return; }
    const cols = Object.keys(rows[0]);
    let html = '<table><thead><tr>' + cols.map(c=>`<th>${c}</th>`).join('') + '</tr></thead><tbody>';
    for(const r of rows){ html += '<tr>' + cols.map(c=>`<td>${r[c] ?? ''}</td>`).join('') + '</tr>'; }
    html += '</tbody></table>'; target.innerHTML = html;
  }
  function renderGraphs(targetId, graphs){
    const target = el(targetId); if(!target) return;
    if(!graphs || Object.keys(graphs).length===0){ target.innerHTML = '<div class="empty">No graphs to display.</div>'; return; }
    let html='';
    for(const [name, payload] of Object.entries(graphs)){
      html += `<div style="margin-bottom:12px"><span class="pill">${name}</span>`;
      html += '<pre style="white-space:pre-wrap; background:#f9fbfe; border:1px solid #eef3f9; padding:8px; border-radius:6px;">'+
              JSON.stringify(payload, null, 2)+'</pre></div>';
    }
    target.innerHTML = html;
  }
  renderTable('summary-table', window.SUMMARY);
  renderTable('observations-table', window.OBSERVATIONS);
  renderTable('dbhits-table', window.DBHITS);
  renderGraphs('graphs-container', window.GRAPHS);
})();