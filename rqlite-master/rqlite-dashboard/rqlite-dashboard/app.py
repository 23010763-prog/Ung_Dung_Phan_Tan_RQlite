<!DOCTYPE html>
<html lang="vi">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>RQLite Cluster Dashboard</title>
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }

    body {
      font-family: 'Segoe UI', sans-serif;
      background: #0f1117;
      color: #e2e8f0;
      min-height: 100vh;
    }

    header {
      background: #1a1d2e;
      border-bottom: 1px solid #2d3748;
      padding: 16px 32px;
      display: flex;
      align-items: center;
      justify-content: space-between;
    }

    header h1 {
      font-size: 20px;
      font-weight: 600;
      color: #63b3ed;
      letter-spacing: 0.5px;
    }

    .badge {
      font-size: 12px;
      padding: 4px 12px;
      border-radius: 20px;
      background: #2d3748;
      color: #a0aec0;
    }

    .badge.live {
      background: #1a2e1a;
      color: #68d391;
      animation: pulse 2s infinite;
    }

    @keyframes pulse {
      0%, 100% { opacity: 1; }
      50% { opacity: 0.6; }
    }

    .container { max-width: 1100px; margin: 0 auto; padding: 28px 24px; }

    /* Summary cards */
    .summary {
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 16px;
      margin-bottom: 28px;
    }

    .card {
      background: #1a1d2e;
      border: 1px solid #2d3748;
      border-radius: 12px;
      padding: 20px;
    }

    .card-label {
      font-size: 12px;
      color: #718096;
      text-transform: uppercase;
      letter-spacing: 0.8px;
      margin-bottom: 8px;
    }

    .card-value {
      font-size: 32px;
      font-weight: 700;
      color: #e2e8f0;
    }

    .card-value.green { color: #68d391; }
    .card-value.blue  { color: #63b3ed; }
    .card-value.amber { color: #f6ad55; }

    /* Node grid */
    .section-title {
      font-size: 14px;
      font-weight: 600;
      color: #a0aec0;
      text-transform: uppercase;
      letter-spacing: 0.8px;
      margin-bottom: 14px;
    }

    .nodes {
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 16px;
      margin-bottom: 28px;
    }

    .node-card {
      background: #1a1d2e;
      border: 1px solid #2d3748;
      border-radius: 12px;
      padding: 20px;
      transition: border-color 0.3s;
      position: relative;
      overflow: hidden;
    }

    .node-card.online  { border-color: #2f855a; }
    .node-card.offline { border-color: #742a2a; opacity: 0.6; }
    .node-card.leader  { border-color: #2b6cb0; background: #1a2035; }

    .node-card::before {
      content: '';
      position: absolute;
      top: 0; left: 0; right: 0;
      height: 3px;
      border-radius: 12px 12px 0 0;
    }

    .node-card.online::before  { background: #48bb78; }
    .node-card.offline::before { background: #fc8181; }
    .node-card.leader::before  { background: #63b3ed; }

    .node-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      margin-bottom: 12px;
    }

    .node-name {
      font-size: 16px;
      font-weight: 600;
    }

    .node-status {
      font-size: 11px;
      padding: 3px 10px;
      border-radius: 20px;
      font-weight: 600;
    }

    .status-online  { background: #1a2e1a; color: #68d391; }
    .status-offline { background: #2d1a1a; color: #fc8181; }
    .status-leader  { background: #1a2040; color: #63b3ed; }

    .node-url {
      font-size: 12px;
      color: #4a5568;
      font-family: monospace;
      margin-bottom: 10px;
    }

    .node-dot {
      width: 8px; height: 8px;
      border-radius: 50%;
      display: inline-block;
      margin-right: 6px;
    }

    .dot-online  { background: #48bb78; box-shadow: 0 0 6px #48bb78; }
    .dot-offline { background: #fc8181; }
    .dot-leader  { background: #63b3ed; box-shadow: 0 0 6px #63b3ed; }

    /* Bottom panels */
    .panels {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 16px;
      margin-bottom: 28px;
    }

    .panel {
      background: #1a1d2e;
      border: 1px solid #2d3748;
      border-radius: 12px;
      padding: 20px;
    }

    .panel-title {
      font-size: 13px;
      font-weight: 600;
      color: #a0aec0;
      margin-bottom: 14px;
      padding-bottom: 10px;
      border-bottom: 1px solid #2d3748;
    }

    table { width: 100%; border-collapse: collapse; }
    th {
      text-align: left;
      font-size: 11px;
      color: #4a5568;
      text-transform: uppercase;
      padding: 6px 8px;
    }
    td {
      padding: 8px;
      font-size: 13px;
      border-top: 1px solid #1e2533;
    }

    /* Log */
    .log-box {
      background: #0d1117;
      border-radius: 8px;
      padding: 14px;
      font-family: monospace;
      font-size: 12px;
      max-height: 180px;
      overflow-y: auto;
    }

    .log-entry {
      margin-bottom: 4px;
      display: flex;
      gap: 10px;
    }

    .log-time { color: #4a5568; min-width: 60px; }
    .log-msg.ok  { color: #68d391; }
    .log-msg.err { color: #fc8181; }
    .log-msg.info { color: #63b3ed; }

    /* Button */
    .btn-row { display: flex; gap: 10px; margin-bottom: 24px; }

    .btn {
      padding: 9px 20px;
      border-radius: 8px;
      border: none;
      font-size: 13px;
      font-weight: 600;
      cursor: pointer;
      transition: opacity 0.2s;
    }

    .btn:hover { opacity: 0.85; }
    .btn-blue  { background: #2b6cb0; color: #fff; }
    .btn-green { background: #276749; color: #fff; }
    .btn-gray  { background: #2d3748; color: #a0aec0; }

    .refresh-info {
      font-size: 12px;
      color: #4a5568;
      align-self: center;
      margin-left: auto;
    }

    /* Spinner */
    .spinner {
      display: inline-block;
      width: 10px; height: 10px;
      border: 2px solid #4a5568;
      border-top-color: #63b3ed;
      border-radius: 50%;
      animation: spin 0.8s linear infinite;
      margin-right: 6px;
      vertical-align: middle;
    }

    @keyframes spin { to { transform: rotate(360deg); } }

    #countdown {
      font-size: 12px;
      color: #4a5568;
    }
  </style>
</head>
<body>

<header>
  <h1>⚡ RQLite Cluster Dashboard</h1>
  <div style="display:flex;gap:10px;align-items:center">
    <span id="countdown">Refresh sau 3s</span>
    <span class="badge live">● LIVE</span>
  </div>
</header>

<div class="container">

  <!-- Summary cards -->
  <div class="summary">
    <div class="card">
      <div class="card-label">Node Online</div>
      <div class="card-value green" id="online-count">--</div>
    </div>
    <div class="card">
      <div class="card-label">Tổng node</div>
      <div class="card-value blue" id="total-nodes">3</div>
    </div>
    <div class="card">
      <div class="card-label">Leader</div>
      <div class="card-value amber" id="leader-name">--</div>
    </div>
    <div class="card">
      <div class="card-label">API Calls</div>
      <div class="card-value" id="query-count">--</div>
    </div>
  </div>

  <!-- Buttons -->
  <div class="btn-row">
    <button class="btn btn-green" onclick="demoWrite()">+ Thêm dữ liệu demo</button>
    <button class="btn btn-blue" onclick="fetchAll()">↻ Refresh ngay</button>
    <button class="btn btn-gray" onclick="loadDbInfo()">📋 Xem bảng dữ liệu</button>
    <span class="refresh-info">Tự động refresh mỗi 3 giây</span>
  </div>

  <!-- Node cards -->
  <div class="section-title">Trạng thái từng node</div>
  <div class="nodes" id="nodes-container">
    <div class="node-card"><div class="card-label">Đang tải...</div></div>
    <div class="node-card"><div class="card-label">Đang tải...</div></div>
    <div class="node-card"><div class="card-label">Đang tải...</div></div>
  </div>

  <!-- Bottom panels -->
  <div class="panels">
    <div class="panel">
      <div class="panel-title">📋 Bảng dữ liệu trong SQLite</div>
      <div id="db-info-content">
        <span style="color:#4a5568;font-size:13px">Nhấn "Xem bảng dữ liệu" để tải...</span>
      </div>
    </div>

    <div class="panel">
      <div class="panel-title">📜 Activity Log</div>
      <div class="log-box" id="log-box">
        <div class="log-entry">
          <span class="log-time">--:--:--</span>
          <span class="log-msg info">Dashboard khởi động...</span>
        </div>
      </div>
    </div>
  </div>

</div>

<script>
  let countdown = 3;
  let logEntries = [];

  function addLog(msg, type = 'info') {
    const now = new Date().toLocaleTimeString('vi-VN');
    logEntries.unshift({ time: now, msg, type });
    if (logEntries.length > 30) logEntries.pop();
    renderLog();
  }

  function renderLog() {
    const box = document.getElementById('log-box');
    box.innerHTML = logEntries.map(e =>
      `<div class="log-entry">
        <span class="log-time">${e.time}</span>
        <span class="log-msg ${e.type}">${e.msg}</span>
       </div>`
    ).join('');
  }

  function renderNodes(nodes, leader) {
    const container = document.getElementById('nodes-container');
    container.innerHTML = nodes.map(node => {
      const isLeader = node.id === leader;
      const cls = node.status === 'offline' ? 'offline' : (isLeader ? 'leader' : 'online');
      const dotCls = node.status === 'offline' ? 'dot-offline' : (isLeader ? 'dot-leader' : 'dot-online');
      const statusCls = node.status === 'offline' ? 'status-offline' : (isLeader ? 'status-leader' : 'status-online');
      const statusText = node.status === 'offline' ? 'OFFLINE' : (isLeader ? 'LEADER' : 'FOLLOWER');

      return `
        <div class="node-card ${cls}">
          <div class="node-header">
            <div class="node-name">
              <span class="node-dot ${dotCls}"></span>
              ${node.id.toUpperCase()}
            </div>
            <span class="node-status ${statusCls}">${statusText}</span>
          </div>
          <div class="node-url">${node.url}</div>
          <div style="font-size:12px;color:#4a5568;margin-top:6px">
            ${node.status === 'online'
              ? `<span style="color:#68d391">✓ Đang hoạt động</span>`
              : `<span style="color:#fc8181">✗ Không phản hồi</span>`}
          </div>
        </div>`;
    }).join('');
  }

  async function fetchAll() {
    try {
      const res = await fetch('/api/status');
      const data = await res.json();

      document.getElementById('online-count').textContent = data.online_count;
      document.getElementById('total-nodes').textContent = data.total_nodes;
      document.getElementById('leader-name').textContent = data.leader ? data.leader.toUpperCase() : 'Không rõ';
      document.getElementById('query-count').textContent = data.query_count;

      renderNodes(data.nodes, data.leader);

      const offlineNodes = data.nodes.filter(n => n.status === 'offline');
      if (offlineNodes.length > 0) {
        offlineNodes.forEach(n => addLog(`⚠ ${n.id} OFFLINE — cluster vẫn hoạt động`, 'err'));
      } else {
        addLog(`✓ Cluster OK — ${data.online_count}/${data.total_nodes} node online`, 'ok');
      }

      if (data.leader) {
        addLog(`Leader: ${data.leader.toUpperCase()}`, 'info');
      }
    } catch (e) {
      addLog('Lỗi kết nối tới Flask server', 'err');
    }
  }

  async function loadDbInfo() {
    const el = document.getElementById('db-info-content');
    el.innerHTML = '<span class="spinner"></span> Đang tải...';
    try {
      const res = await fetch('/api/db-info');
      const data = await res.json();
      if (data.tables.length === 0) {
        el.innerHTML = '<span style="color:#4a5568;font-size:13px">Chưa có bảng nào. Nhấn "Thêm dữ liệu demo" để tạo.</span>';
        return;
      }
      el.innerHTML = `
        <table>
          <thead><tr><th>Tên bảng</th><th>Số bản ghi</th></tr></thead>
          <tbody>
            ${data.tables.map(t => `
              <tr>
                <td style="color:#63b3ed;font-family:monospace">${t.name}</td>
                <td style="color:#68d391;font-weight:600">${t.rows}</td>
              </tr>`).join('')}
          </tbody>
        </table>
        <div style="margin-top:10px;font-size:11px;color:#4a5568">Nguồn: ${data.source_node}</div>`;
      addLog(`Đã tải thông tin DB từ ${data.source_node}`, 'info');
    } catch (e) {
      el.innerHTML = '<span style="color:#fc8181">Lỗi tải dữ liệu</span>';
    }
  }

  async function demoWrite() {
    try {
      const res = await fetch('/api/demo-write');
      const data = await res.json();
      if (data.success) {
        addLog(`✓ ${data.message}`, 'ok');
        await loadDbInfo();
      } else {
        addLog(`✗ ${data.message}`, 'err');
      }
    } catch (e) {
      addLog('Lỗi khi ghi dữ liệu', 'err');
    }
  }

  // Countdown + auto refresh
  setInterval(() => {
    countdown--;
    document.getElementById('countdown').textContent = `Refresh sau ${countdown}s`;
    if (countdown <= 0) {
      countdown = 3;
      fetchAll();
    }
  }, 1000);

  // Chay ngay khi load trang
  fetchAll();
  loadDbInfo();
</script>
</body>
</html>