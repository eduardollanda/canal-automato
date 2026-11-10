let player = null;
let currentVideoId = null;
let ending = false;
let ytReady = false;

function loadYouTubeApi() {
  return new Promise((resolve) => {
    if (window.YT && window.YT.Player) {
      ytReady = true;
      resolve();
      return;
    }
    const tag = document.createElement("script");
    tag.src = "https://www.youtube.com/iframe_api";
    document.head.appendChild(tag);
    window.onYouTubeIframeAPIReady = () => {
      ytReady = true;
      resolve();
    };
  });
}

function ensurePlayer(videoId) {
  if (player) {
    if (videoId !== currentVideoId) {
      ending = false;
      currentVideoId = videoId;
      player.loadVideoById(videoId);
    }
    return;
  }
  currentVideoId = videoId;
  player = new YT.Player("player", {
    videoId,
    playerVars: {
      autoplay: 1,
      controls: 1,
      rel: 0,
      modestbranding: 1,
      playsinline: 1,
    },
    events: {
      onReady: (e) => e.target.playVideo(),
      onStateChange: onStateChange,
      onError: async () => {
        ending = true;
        await fetch("/api/ended", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ watched_sec: 0, completed: false }),
        });
        ending = false;
        await refreshState(true);
      },
    },
  });
}

async function onStateChange(event) {
  if (!player) return;
  if (event.data === YT.PlayerState.ENDED && !ending) {
    ending = true;
    const duration = player.getDuration?.() || 0;
    await fetch("/api/ended", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        watched_sec: duration,
        duration_sec: duration,
        completed: true,
      }),
    });
    ending = false;
    await refreshState(true);
  }
}

async function heartbeat() {
  if (!player || typeof player.getCurrentTime !== "function") return;
  try {
    const watched = player.getCurrentTime() || 0;
    const duration = player.getDuration() || 0;
    if (duration > 0) {
      await fetch("/api/progress", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ watched_sec: watched, duration_sec: duration }),
      });
    }
  } catch (_) {}
}

function renderAffinity(affinity) {
  const el = document.getElementById("affinityBars");
  const entries = Object.entries(affinity || {}).sort((a, b) => b[1] - a[1]).slice(0, 8);
  el.innerHTML = entries
    .map(
      ([k, v]) => `
      <div class="bar-row">
        <span>${k}</span>
        <div class="bar-track"><div class="bar-fill" style="width:${(v * 100).toFixed(1)}%"></div></div>
        <span>${(v * 100).toFixed(1)}%</span>
      </div>`
    )
    .join("");
}

function renderQueue(queue) {
  const el = document.getElementById("queueList");
  if (!queue?.length) {
    el.innerHTML = "<li>fila vazia — engine buscando…</li>";
    return;
  }
  el.innerHTML = queue
    .map((item) => {
      const tag = item.kind === "ad" ? "ad" : "content";
      const type = item.kind === "ad" ? item.ad_type : item.content_type;
      return `<li><span class="tag ${tag}">${item.kind}</span><strong>${item.status}</strong> · ${type || "—"} · ${item.title}</li>`;
    })
    .join("");
}

function renderLogs(logs) {
  const el = document.getElementById("logList");
  el.innerHTML = (logs || []).slice().reverse().map((l) => `<li>${l}</li>`).join("") || "<li>—</li>";
}

function renderAsRun(rows) {
  const el = document.getElementById("asrunList");
  el.innerHTML =
    (rows || [])
      .slice()
      .reverse()
      .map((r) => {
        const tag = r.kind === "ad" ? "ad" : "content";
        const type = r.kind === "ad" ? r.ad_type : r.content_type;
        return `<li><span class="tag ${tag}">${r.kind}</span>${type || "—"} · ${r.title} · view ${(r.watched_ratio * 100).toFixed(0)}%</li>`;
      })
      .join("") || "<li>—</li>";
}

async function refreshState(forcePlay = false) {
  const res = await fetch("/api/state");
  const state = await res.json();
  const cur = state.current;

  document.getElementById("cacheStat").textContent = `${state.cache_pct}% de 2GB`;
  document.getElementById("statusStat").textContent = state.status;
  document.getElementById("historyStat").textContent = `${state.history_count ?? 0} vídeos`;

  if (cur) {
    const badge = document.getElementById("kindBadge");
    badge.textContent = cur.kind === "ad" ? `propaganda · ${cur.ad_type || ""}` : `conteúdo · ${cur.content_type || ""}`;
    badge.className = `badge ${cur.kind === "ad" ? "ad" : "live"}`;
    document.getElementById("nowTitle").textContent = cur.title;
    document.getElementById("nowSub").textContent = `${cur.video_id} · ${Math.round(cur.duration_sec || 0)}s · ${cur.status}`;
    if (ytReady && cur.video_id && (forcePlay || cur.video_id !== currentVideoId)) {
      ensurePlayer(cur.video_id);
    }
  }

  renderAffinity(state.affinity);
  renderQueue(state.queue);
  renderLogs(state.algorithm_log);
  renderAsRun(state.recent_as_run);
}

async function boot() {
  await loadYouTubeApi();
  await refreshState(true);
  setInterval(() => refreshState(false), 2500);
  setInterval(heartbeat, 5000);
}

boot();
