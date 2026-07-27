/* ============================================================
   Offline Saisie — Sauvegarde automatique localStorage
   + synchronisation automatique au retour de connexion
   ============================================================ */
(function () {
  'use strict';

  /* ---------- Clés localStorage ---------- */
  var DRAFT_PREFIX = 'saisie_draft:';
  var PENDING_KEY  = 'saisie_pending';

  /* ---------- Helpers ---------- */
  function getPeriode() {
    var el = document.querySelector('input[name="periode"]');
    return el ? el.value : 'default';
  }

  function draftKey() {
    return DRAFT_PREFIX + window.location.pathname + ':' + getPeriode();
  }

  /* ---------- Brouillon (draft) ---------- */
  function saveDraft() {
    var inputs = {};
    document.querySelectorAll('.saisie-input').forEach(function (inp) {
      var v = parseInt(inp.value) || 0;
      if (v > 0) inputs[inp.name] = v;
    });
    var obsEl = document.querySelector('textarea[name="observations"]');
    try {
      localStorage.setItem(draftKey(), JSON.stringify({
        data: inputs,
        observations: obsEl ? obsEl.value : '',
        savedAt: new Date().toISOString()
      }));
    } catch (e) { /* stockage plein */ }
  }

  function clearDraft() {
    try { localStorage.removeItem(draftKey()); } catch (e) {}
  }

  function restoreDraft() {
    try {
      var raw = localStorage.getItem(draftKey());
      if (!raw) return;
      var draft = JSON.parse(raw);

      /* Ne pas écraser des données déjà remplies par le serveur */
      var hasServerData = false;
      document.querySelectorAll('.saisie-input').forEach(function (inp) {
        if ((parseInt(inp.value) || 0) > 0) hasServerData = true;
      });
      if (hasServerData) { clearDraft(); return; }

      var restored = 0;
      Object.keys(draft.data || {}).forEach(function (name) {
        var inp = document.querySelector('input[name="' + name + '"]');
        if (inp && inp.classList.contains('saisie-input')) {
          inp.value = draft.data[name];
          inp.classList.add('changed');
          restored++;
          /* Recalculer le total de la ligne */
          var idPart = name.replace(/^[shed]_/, '');
          if (typeof updateTotal === 'function') {
            try { updateTotal(idPart); } catch (ex) {}
          }
        }
      });

      var obsEl = document.querySelector('textarea[name="observations"]');
      if (obsEl && draft.observations) obsEl.value = draft.observations;

      if (restored > 0) {
        if (typeof updateGrandTotals === 'function') updateGrandTotals();
        if (typeof updateMPECounter  === 'function') updateMPECounter();
        showToast(
          '<i class="bi bi-cloud-download-fill me-1"></i> Brouillon restauré (' +
          new Date(draft.savedAt).toLocaleTimeString('fr-FR') + ')',
          'info'
        );
        /* Marquer comme modifié */
        if (typeof hasChanges !== 'undefined') {
          // eslint-disable-next-line no-global-assign
          hasChanges = true;
          var badge = document.getElementById('draftBadge');
          if (badge) badge.classList.add('visible');
        }
      }
    } catch (e) {}
  }

  /* ---------- File d'attente (pending queue) ---------- */
  function getPending() {
    try { return JSON.parse(localStorage.getItem(PENDING_KEY) || '[]'); } catch (e) { return []; }
  }

  function savePending(queue) {
    try { localStorage.setItem(PENDING_KEY, JSON.stringify(queue)); } catch (e) {}
  }

  function enqueueSubmission(frm) {
    var data = {};
    var fd = new FormData(frm);
    fd.forEach(function (val, key) { data[key] = val; });
    var queue = getPending();
    queue.push({
      url: window.location.href,
      data: data,
      ts: Date.now()
    });
    savePending(queue);
  }

  function flushPending() {
    var queue = getPending();
    if (!queue.length) return;
    var remaining = [];

    var promises = queue.map(function (item) {
      var body = Object.keys(item.data)
        .map(function (k) {
          return encodeURIComponent(k) + '=' + encodeURIComponent(item.data[k]);
        }).join('&');

      return fetch(item.url, {
        method: 'POST',
        credentials: 'same-origin',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: body
      }).then(function (resp) {
        if (resp.ok || resp.redirected) {
          clearDraft();
          showToast(
            '<i class="bi bi-check-circle-fill me-1"></i> Fiche soumise avec succès !',
            'success'
          );
        } else {
          remaining.push(item);
        }
      }).catch(function () {
        remaining.push(item);
      });
    });

    Promise.all(promises).then(function () { savePending(remaining); });
  }

  /* ---------- Bannière offline ---------- */
  var _banner = null;

  function getBanner() {
    if (_banner) return _banner;
    _banner = document.getElementById('offlineBanner');
    if (!_banner) {
      _banner = document.createElement('div');
      _banner.id = 'offlineBanner';
      _banner.className = 'offline-banner';
      document.body.insertBefore(_banner, document.body.firstChild);
    }
    return _banner;
  }

  function updateBanner(isOnline) {
    var b = getBanner();
    if (!isOnline) {
      b.innerHTML =
        '<i class="bi bi-wifi-off me-2"></i>' +
        'Mode hors ligne — saisie sauvegardée localement &nbsp;' +
        '<span class="offline-dot"></span>';
      b.classList.add('visible');
    } else {
      b.innerHTML =
        '<i class="bi bi-wifi me-2"></i>' +
        'Connexion rétablie — synchronisation en cours…';
      b.classList.add('visible', 'online');
      setTimeout(function () { b.classList.remove('visible', 'online'); }, 3500);
    }
  }

  /* ---------- Toast ---------- */
  function showToast(html, type) {
    var t = document.createElement('div');
    t.className = 'saisie-toast saisie-toast-' + (type || 'info');
    t.innerHTML = html;
    document.body.appendChild(t);
    requestAnimationFrame(function () {
      requestAnimationFrame(function () { t.classList.add('visible'); });
    });
    setTimeout(function () {
      t.classList.remove('visible');
      setTimeout(function () { if (t.parentNode) t.parentNode.removeChild(t); }, 400);
    }, 4000);
  }

  /* ---------- Bouton "Soumettre en attente" ---------- */
  function checkPendingOnLoad() {
    var queue = getPending();
    if (!queue.length) return;
    if (navigator.onLine) {
      showToast(
        '<i class="bi bi-cloud-arrow-up-fill me-1"></i> ' +
        queue.length + ' fiche(s) en attente — soumission en cours…',
        'info'
      );
      flushPending();
    } else {
      showToast(
        '<i class="bi bi-cloud-slash me-1"></i> ' +
        queue.length + ' fiche(s) sauvegardée(s) — en attente de connexion',
        'warning'
      );
    }
  }

  /* ---------- Branchement sur le formulaire ---------- */
  var frm = document.getElementById('saisieFrm');

  if (frm) {
    /* Auto-save à chaque modification */
    frm.addEventListener('input', function () {
      saveDraft();
    });

    /* Interception du submit si offline */
    frm.addEventListener('submit', function (e) {
      if (!navigator.onLine) {
        e.preventDefault();
        e.stopImmediatePropagation();
        enqueueSubmission(frm);
        saveDraft();

        var badge = document.getElementById('draftBadge');
        if (badge) {
          badge.className = 'draft-badge badge bg-danger text-white visible';
          badge.innerHTML = '<i class="bi bi-cloud-slash"></i> En attente de connexion';
        }

        showToast(
          '<i class="bi bi-wifi-off me-1"></i> Hors ligne : fiche sauvegardée. ' +
          'Soumission automatique à la reconnexion.',
          'info'
        );
      } else {
        /* Online : nettoyer le brouillon après soumission réussie */
        clearDraft();
      }
    }, true); /* capture phase = avant le handler de saisie.js */

    /* Restaurer le brouillon au chargement */
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', restoreDraft);
    } else {
      restoreDraft();
    }
  }

  /* ---------- Événements réseau ---------- */
  window.addEventListener('offline', function () {
    updateBanner(false);
    showToast('<i class="bi bi-wifi-off me-1"></i> Connexion perdue — mode hors ligne activé', 'warning');
  });

  window.addEventListener('online', function () {
    updateBanner(true);
    flushPending();
  });

  /* ---------- État initial ---------- */
  if (!navigator.onLine) {
    updateBanner(false);
  }

  /* Vérifier fiches en attente au chargement */
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', checkPendingOnLoad);
  } else {
    checkPendingOnLoad();
  }

})();