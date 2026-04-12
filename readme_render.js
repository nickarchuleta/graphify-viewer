/**
 * README → readable panel: strip leading logo/badge HTML, then render Markdown.
 * Used by graph_unified.html and github_stars_mirror.html
 */
(function (global) {
  'use strict';

  function stripLeadNoise(text) {
    if (!text || typeof text !== 'string') return text;
    var s = text.replace(/\r\n/g, '\n');
    s = s.replace(/^(<!--[\s\S]*?-->\s*)+/g, '');
    var prev = '';
    for (var guard = 0; guard < 40 && s !== prev; guard++) {
      prev = s;
      s = s.replace(/^\s*<p[^>]*align\s*=\s*["']?center["']?[^>]*>[\s\S]*?<\/p>\s*/i, '');
      s = s.replace(/^\s*<div[^>]*align\s*=\s*["']?center["']?[^>]*>[\s\S]*?<\/div>\s*/i, '');
      s = s.replace(/^\s*<h[1-6][^>]*align\s*=\s*["']?center["']?[^>]*>[\s\S]*?<\/h[1-6]>\s*/i, '');
      s = s.replace(/^\s*<picture>[\s\S]*?<\/picture>\s*/i, '');
      s = s.replace(/^\s*<p[^>]*>\s*<a[^>]*>[\s\S]*?<\/a>\s*<\/p>\s*/i, '');
    }
    var lines = s.split('\n');
    var i = 0;
    while (i < lines.length) {
      var line = lines[i];
      var t = line.trim();
      if (!t) {
        i++;
        continue;
      }
      if (/^\[!\[/.test(t)) {
        i++;
        continue;
      }
      if (/^\[!\[.*\]\(http.*shield/i.test(t)) {
        i++;
        continue;
      }
      if (/^\s*<a\s+[^>]*href[^>]*>\s*<img/i.test(t)) {
        i++;
        continue;
      }
      if (/^\s*<img\s/i.test(t)) {
        i++;
        continue;
      }
      if (/^\s*<\/(p|div|a)>\s*$/i.test(t)) {
        i++;
        continue;
      }
      if (/^#{1,3}\s+\S/.test(t)) break;
      if (t.startsWith('```')) break;
      if (t.length > 120 && !/^</.test(t)) break;
      if (/^Lux is a Python library/i.test(t)) break;
      if (/^OpenViking/i.test(t)) break;
      if (/^To (start|get started|install)/i.test(t)) break;
      if (t.length > 60 && /^[A-Za-z]/.test(t) && !/^</.test(t)) break;
      i++;
    }
    return lines.slice(i).join('\n').replace(/^\s+/, '');
  }

  function cleanupRendered(root) {
    if (!root || !root.querySelectorAll) return;
    root.querySelectorAll('p[align="center"], p[align=center]').forEach(function (p) {
      var imgs = p.querySelectorAll('img');
      if (imgs.length >= 1 && (p.textContent || '').trim().length < 30) p.remove();
    });
    root.querySelectorAll('div[align="center"], div[align=center]').forEach(function (d) {
      if (d.querySelector('img, picture') && (d.textContent || '').trim().length < 40) d.remove();
    });
    var firstPs = root.querySelectorAll('p');
    firstPs.forEach(function (p) {
      var onlyBadges = p.querySelectorAll('a > img').length >= 2 && (p.textContent || '').trim().length < 15;
      if (onlyBadges) p.remove();
    });
  }

  function render(md, container, marked) {
    if (!container || !md) return;
    var cleaned = stripLeadNoise(md);
    var html;
    try {
      html = marked.parse(cleaned, { mangle: false, headerIds: false, breaks: true });
    } catch (e) {
      container.innerHTML = '<pre class="readme-fallback">' + escapeHtml(md) + '</pre>';
      return;
    }
    container.innerHTML = html;
    container.classList.add('readme-prose');
    cleanupRendered(container);
  }

  function escapeHtml(s) {
    var d = document.createElement('div');
    d.textContent = s;
    return d.innerHTML;
  }

  global.ReadmeSkin = { stripLeadNoise: stripLeadNoise, cleanupRendered: cleanupRendered, render: render, escapeHtml: escapeHtml };
})(typeof window !== 'undefined' ? window : globalThis);
