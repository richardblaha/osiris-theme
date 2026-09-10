/* ============================================================================
   OSIRIS — VS Code Theme Preview
   Interaction layer for the design reference. No dependencies.
   ========================================================================== */
(function () {
  'use strict';

  /* ---- Theme toggle (dark / light) ---------------------------------------- */
  function setTheme(mode) {
    document.documentElement.setAttribute('data-theme', mode);
    document.querySelectorAll('[data-theme-btn]').forEach(function (btn) {
      btn.classList.toggle('active', btn.getAttribute('data-theme-btn') === mode);
    });
    try { localStorage.setItem('osiris-preview-theme', mode); } catch (e) { /* ignore */ }
    if (galleriesRendered) renderGalleries(); // folder icons are theme-tinted
  }

  /* ---- Main tabs: Editor / Aplikační ikony / Ikony souborů --------------- */
  var galleriesRendered = false;

  function setMainTab(name) {
    document.querySelectorAll('.main-tab').forEach(function (t) {
      var on = t.getAttribute('data-main-tab') === name;
      t.classList.toggle('active', on);
      t.setAttribute('aria-selected', on ? 'true' : 'false');
    });
    document.querySelectorAll('[data-main-view]').forEach(function (v) {
      v.hidden = v.getAttribute('data-main-view') !== name;
    });
    if (!galleriesRendered && name !== 'editor') {
      renderGalleries();
      galleriesRendered = true;
    }
  }

  function esc(s) {
    return String(s).replace(/[&<>"]/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c];
    });
  }

  function iconCard(item) {
    var glyphs = (window.OSIRIS_PREVIEW_ICONS && window.OSIRIS_PREVIEW_ICONS.glyphs) || {};
    var glyph = glyphs[item.glyph] || { d: '' };
    var color = item.color;
    if (!color) {
      color = document.documentElement.getAttribute('data-theme') === 'light' ? item.light : item.dark;
    }
    var fr = glyph.e ? ' fill-rule="evenodd" clip-rule="evenodd"' : '';
    return '<div class="icon-card" title="' + esc(item.glyph) + '">' +
      '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="' + glyph.d + '" fill="' + color + '"' + fr + '/></svg>' +
      '<span class="lbl">' + esc(item.label) + '</span></div>';
  }

  function iconGroup(title, items) {
    if (!items || !items.length) return '';
    return '<div class="icon-group"><h3>' + esc(title) + '</h3><div class="icon-grid">' +
      items.map(iconCard).join('') + '</div></div>';
  }

  function renderGalleries() {
    var data = window.OSIRIS_PREVIEW_ICONS;
    var themes = (data && data.themes) || [];
    document.querySelectorAll('.icon-gallery[data-theme-id]').forEach(function (sec) {
      var id = sec.getAttribute('data-theme-id');
      var theme = themes.filter(function (t) { return t.id === id; })[0];
      if (!theme) {
        sec.innerHTML = '<div class="empty">icons.js se nenačetl — spusťte <b>make pages</b>.</div>';
        return;
      }
      sec.innerHTML =
        '<header class="gallery-head">' +
          '<h2>' + esc(theme.name) + '</h2>' +
          '<p class="gallery-target">' + esc(theme.target) + '</p>' +
          '<p>' + esc(theme.note) + '</p>' +
        '</header>' +
        '<div class="gallery-body">' +
          theme.groups.map(function (gr) { return iconGroup(gr.title, gr.items); }).join('') +
        '</div>';
    });
  }

  /* ---- Activity Bar -> Side Bar view switching --------------------------- */
  function setView(el) {
    var view = el.getAttribute('data-view');
    if (!view) return;
    document.querySelectorAll('.activitybar .act-item[data-view]').forEach(function (i) {
      i.classList.toggle('active', i === el);
    });
    document.querySelectorAll('.sidebar-view').forEach(function (v) {
      v.classList.toggle('active', v.getAttribute('data-view') === view);
    });
    closeGear();
  }

  /* ---- Editor tabs -> code / settings view switching -------------------- */
  function setEditorTab(el) {
    document.querySelectorAll('.editor-area .tabs .tab').forEach(function (t) {
      t.classList.toggle('active', t === el);
    });
    var target = el.getAttribute('data-editor');
    document.querySelectorAll('.editor-view').forEach(function (v) {
      v.classList.toggle('active', v.getAttribute('data-editor') === target);
    });
  }

  /* ---- Settings gear menu ---------------------------------------------- */
  function toggleGear(evt, forceClose) {
    if (evt) evt.stopPropagation();
    var menu = document.getElementById('gearMenu');
    if (forceClose) { menu.classList.remove('open'); return; }
    menu.classList.toggle('open');
  }
  function closeGear() {
    var menu = document.getElementById('gearMenu');
    if (menu) menu.classList.remove('open');
  }

  /* ---- Command Palette ------------------------------------------------- */
  function toggleCmdk(open) {
    document.getElementById('cmdkBackdrop').classList.toggle('open', open);
    closeGear();
  }

  /* ---- Wire up -------------------------------------------------------- */
  document.addEventListener('click', function (e) {
    var menu = document.getElementById('gearMenu');
    if (menu && menu.classList.contains('open') && !menu.contains(e.target)) closeGear();
  });

  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') { toggleCmdk(false); closeGear(); }
    if ((e.ctrlKey || e.metaKey) && e.shiftKey && (e.key === 'P' || e.key === 'p')) {
      e.preventDefault();
      toggleCmdk(!document.getElementById('cmdkBackdrop').classList.contains('open'));
    }
  });

  document.addEventListener('DOMContentLoaded', function () {
    // restore persisted theme
    var stored = null;
    try { stored = localStorage.getItem('osiris-preview-theme'); } catch (e) { /* ignore */ }
    if (stored === 'dark' || stored === 'light') setTheme(stored);

    // delegate onclick hooks declared in markup
    document.querySelectorAll('[data-act="theme"]').forEach(function (b) {
      b.addEventListener('click', function () { setTheme(b.getAttribute('data-theme-btn')); });
    });
    document.querySelectorAll('[data-act="view"]').forEach(function (b) {
      b.addEventListener('click', function () { setView(b); });
    });
    document.querySelectorAll('[data-act="editor-tab"]').forEach(function (b) {
      b.addEventListener('click', function () { setEditorTab(b); });
    });
    document.querySelectorAll('[data-act="main-tab"]').forEach(function (b) {
      b.addEventListener('click', function () { setMainTab(b.getAttribute('data-main-tab')); });
    });
    document.querySelectorAll('[data-act="gear"]').forEach(function (b) {
      b.addEventListener('click', function (e) { toggleGear(e); });
    });
    document.querySelectorAll('[data-act="cmdk-open"]').forEach(function (b) {
      b.addEventListener('click', function () { toggleCmdk(true); });
    });
    var backdrop = document.getElementById('cmdkBackdrop');
    if (backdrop) backdrop.addEventListener('click', function (e) { if (e.target === backdrop) toggleCmdk(false); });
    document.querySelectorAll('[data-act="toast-close"]').forEach(function (b) {
      b.addEventListener('click', function () { var t = b.closest('.toast'); if (t) t.hidden = true; });
    });

    // Build gutter line numbers to match code line count
    var code = document.getElementById('code-content');
    var gutter = document.getElementById('gutter');
    if (code && gutter) {
      var lines = code.querySelectorAll('.ln').length;
      var html = '';
      for (var i = 1; i <= lines; i++) {
        html += '<div class="' + (i === 10 ? 'active-line' : '') + '">' + i + '</div>';
      }
      gutter.innerHTML = html;
    }

    // Build a fake minimap made of proportionally tinted bars
    var mm = document.getElementById('minimap');
    if (mm) {
      var pattern = [40, 70, 0, 55, 30, 30, 30, 65, 20, 85, 45, 20, 45, 50, 20, 60, 45, 25, 20, 0, 60];
      var mhtml = '';
      pattern.forEach(function (w, idx) {
        var cls = 'mline';
        if (idx === 9) cls += ' accentA';
        if (idx === 13) cls += ' accentB';
        mhtml += '<div class="' + cls + '" style="width:' + w + '%;' + (w === 0 ? 'visibility:hidden;' : '') + '"></div>';
      });
      mhtml += '<div class="viewport"></div>';
      mm.innerHTML = mhtml;
    }
  });

  // expose for inline handlers still present in markup
  window.setTheme = setTheme;
  window.setView = setView;
  window.setEditorTab = setEditorTab;
  window.setMainTab = setMainTab;
  window.toggleGear = toggleGear;
  window.toggleCmdk = toggleCmdk;
})();
