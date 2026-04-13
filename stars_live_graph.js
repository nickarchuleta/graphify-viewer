/**
 * Live GitHub starred repos → vis-network node/edge payloads.
 * Sensible groups (This Mac, AI coding, …) + optional token: localStorage SPELLBOOK_GH_TOKEN
 */
(function (global) {
  'use strict';

  /** Ordered rules — first match wins. Last entry is fallback. */
  var STARS_GROUPS = [
    { id: 'mac', label: 'This Mac & Apple', color: '#4E79A7', kws: ['swift', 'mlx', 'macos', 'darwin', 'xcode', 'ios', 'appkit', 'catalyst', 'apple-silicon', 'metal', 'swiftui', 'cocoa', 'foundation', 'objc', 'watchos', 'tvos'] },
    { id: 'ai_code', label: 'AI coding stack', color: '#F28E2B', kws: ['claude', 'mcp', 'cursor', 'copilot', 'codex', 'openclaw', 'aider', 'windsurf', 'opencode', 'gemini-cli', 'cline', 'continue.dev'] },
    { id: 'agents', label: 'Agents & orchestration', color: '#EDC948', kws: ['agent', 'multi-agent', 'autogen', 'crewai', 'langgraph', 'orchestr', 'swarm', 'droid'] },
    { id: 'local_ai', label: 'Local / edge inference', color: '#E15759', kws: ['ollama', 'llama.cpp', 'gguf', 'vllm', 'onnx', 'tensorrt', 'quantization', 'mlx', 'inference', 'ggml'] },
    { id: 'graphs', label: 'Graphs & RAG', color: '#59A14F', kws: ['graph', 'rag', 'vector', 'embedding', 'neo4j', 'chromadb', 'graphrag', 'lancedb'] },
    { id: 'browser', label: 'Browser automation', color: '#76B7B2', kws: ['playwright', 'puppeteer', 'browser-use', 'selenium', 'cdp', 'headless'] },
    { id: 'data', label: 'Data & ML', color: '#FF9DA7', kws: ['dataset', 'pandas', 'spark', 'pytorch', 'jupyter', 'notebook', 'huggingface', 'keras'] },
    { id: 'sec', label: 'Security & OSINT', color: '#9C755F', kws: ['security', 'osint', 'pentest', 'cve', 'malware', 'forensic'] },
    { id: 'misc', label: 'Everything else', color: '#BAB0AC', kws: [] },
  ];
  /** Explicit per-repo fixes for ambiguous keyword overlaps. */
  var DEFAULT_STARS_GROUP_OVERRIDES = {
    'e2b-dev/awesome-ai-agents': 'agents',
    'addyosmani/agent-skills': 'agents',
    'alirezarezvani/claude-skills': 'agents',
    'mozilla-ai/any-agent': 'agents',
    'superagent-ai/grok-cli': 'agents',
    'langchain-ai/open-swe': 'agents',
    'huggingface/skills': 'data',
    'financial-datasets/mcp-server': 'data',
    'ml-explore/mlx': 'mac',
    'ml-explore/mlx-lm': 'mac',
    'ml-explore/mlx-swift': 'mac',
    'trevin-creator/autoresearch-mlx': 'mac',
    'Blaizzy/mlx-audio': 'mac',
    'ARahim3/mlx-tune': 'mac',
    'browser-use/browser-use': 'browser',
    'microsoft/playwright': 'browser',
    'puppeteer/puppeteer': 'browser',
    'neo4j/neo4j': 'graphs',
    'langchain-ai/langgraph': 'agents',
    'ComposioHQ/awesome-claude-plugins': 'ai_code'
  };
  var STARS_GROUP_OVERRIDES = Object.assign({}, DEFAULT_STARS_GROUP_OVERRIDES);
  var __starsOverrideLoaded = false;
  function groupById(id) {
    for (var i = 0; i < STARS_GROUPS.length; i++) {
      if (STARS_GROUPS[i].id === id) return STARS_GROUPS[i];
    }
    return STARS_GROUPS[STARS_GROUPS.length - 1];
  }

  async function loadOverrideFile() {
    if (__starsOverrideLoaded) return;
    __starsOverrideLoaded = true;
    try {
      var r = await fetch('./stars_group_overrides.json', { cache: 'no-store' });
      if (!r.ok) return;
      var j = await r.json();
      if (!j || typeof j !== 'object') return;
      Object.keys(j).forEach(function (k) {
        var key = String(k || '').toLowerCase().trim();
        var gid = String(j[k] || '').trim();
        if (!key || !gid) return;
        STARS_GROUP_OVERRIDES[key] = gid;
      });
    } catch (e) {}
  }

  function inferStarGroup(repo) {
    var fn = (repo.full_name || '').toLowerCase();
    if (fn && STARS_GROUP_OVERRIDES[fn]) return groupById(STARS_GROUP_OVERRIDES[fn]);
    var desc = (repo.description || '').toLowerCase();
    var topics = (repo.topics || []).map(function (t) { return String(t).toLowerCase(); }).join(' ');
    var lang = (repo.language || '').toLowerCase();
    var blob = fn + ' ' + desc + ' ' + topics + ' ' + lang;
    var best = STARS_GROUPS[STARS_GROUPS.length - 1];
    var bestScore = 0;
    for (var i = 0; i < STARS_GROUPS.length - 1; i++) {
      var g = STARS_GROUPS[i];
      var score = 0;
      for (var j = 0; j < g.kws.length; j++) {
        if (blob.indexOf(g.kws[j]) !== -1) score += 1;
      }
      if (g.id === 'agents' && (fn.indexOf('agent') !== -1 || topics.indexOf('agent') !== -1)) score += 2;
      if (g.id === 'mac' && (fn.indexOf('mlx') !== -1 || fn.indexOf('swift') !== -1)) score += 2;
      if (g.id === 'browser' && (fn.indexOf('playwright') !== -1 || fn.indexOf('browser') !== -1)) score += 2;
      if (score > bestScore) {
        bestScore = score;
        best = g;
      }
    }
    return bestScore > 0 ? best : STARS_GROUPS[STARS_GROUPS.length - 1];
  }

  function escTitle(s) {
    return String(s == null ? '' : s)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }

  function getGithubHeaders() {
    var h = {
      Accept: 'application/vnd.github+json',
      'X-GitHub-Api-Version': '2022-11-28',
    };
    try {
      var tok = localStorage.getItem('SPELLBOOK_GH_TOKEN') || '';
      if (tok) h.Authorization = 'Bearer ' + tok;
    } catch (e) {}
    return h;
  }

  async function fetchAllStarred(login) {
    var headers = getGithubHeaders();
    var out = [];
    var page = 1;
    var perPage = 100;
    for (;;) {
      var url =
        'https://api.github.com/users/' +
        encodeURIComponent(login) +
        '/starred?per_page=' +
        perPage +
        '&page=' +
        page;
      var r = await fetch(url, { headers: headers });
      if (r.status === 403 || r.status === 429) {
        var err = new Error('GitHub rate limit — set localStorage SPELLBOOK_GH_TOKEN or wait.');
        err.code = 'rate_limit';
        throw err;
      }
      if (!r.ok) throw new Error('GitHub API ' + r.status);
      var batch = await r.json();
      if (!batch || !batch.length) break;
      for (var i = 0; i < batch.length; i++) out.push(batch[i]);
      if (batch.length < perPage) break;
      page++;
    }
    return out;
  }

  async function buildNodesEdges(apiRepos) {
    await loadOverrideFile();
    var hubId = '_github_stars_hub';
    var hubTitle =
      'Hub — ' +
      apiRepos.length +
      ' repos (live from GitHub). Click a node for GitHub.';
    var nodes = [
      {
        id: hubId,
        label: '★ GitHub stars',
        color: { background: '#f59e0b', border: '#d97706' },
        size: 28,
        font: { size: 14, color: '#fff' },
        title: escTitle(hubTitle),
        _star_group: 'hub',
      },
    ];
    var edges = [];
    for (var i = 0; i < apiRepos.length; i++) {
      var r = apiRepos[i];
      var fn = r.full_name || '';
      if (!fn) continue;
      var gid = 'star_' + fn.replace(/\//g, '_').replace(/\./g, '_');
      var url = r.html_url || 'https://github.com/' + fn;
      var parts = fn.split('/');
      var label = (parts[parts.length - 1] || fn).slice(0, 40);
      var desc = String(r.description || '').slice(0, 180);
      var stars = r.stargazers_count || 0;
      var lang = r.language || '—';
      var grp = inferStarGroup(r);
      var title = fn + '\n' + stars + '★ · ' + lang + '\n' + desc + '\n— ' + grp.label;
      var col = grp.color;
      var size = 10 + Math.min(18, stars ? Math.pow(stars, 0.33) : 8);
      nodes.push({
        id: gid,
        label: label,
        full_name: fn,
        color: { background: col, border: col },
        size: size,
        font: { size: 0 },
        title: escTitle(title),
        url: url,
        _star_group: grp.id,
      });
      edges.push({ from: hubId, to: gid });
    }
    return { nodes: nodes, edges: edges };
  }

  global.StarsLive = {
    STARS_GROUPS: STARS_GROUPS,
    inferStarGroup: inferStarGroup,
    fetchAllStarred: fetchAllStarred,
    buildNodesEdges: buildNodesEdges,
    loadOverrideFile: loadOverrideFile,
  };
})(typeof window !== 'undefined' ? window : this);
