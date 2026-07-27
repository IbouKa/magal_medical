/* ============================================================
   Saisie — Logique interactive (fichier externe)
   ============================================================ */

var hasChanges = false;
var showFilledOnly = false;

// ---- Mobile sticky bar padding ----
function updateStickyPadding() {
  if (window.innerWidth < 768) {
    document.body.classList.add('has-sticky-bar');
  } else {
    document.body.classList.remove('has-sticky-bar');
  }
}
updateStickyPadding();
window.addEventListener('resize', updateStickyPadding);

// ---- Select all on focus ----
document.querySelectorAll('.saisie-input').forEach(function(inp) {
  inp.addEventListener('focus', function() { this.select(); });
});

// ---- Calcul total par ligne ----
function updateTotal(id) {
  var s = parseInt(document.getElementById('s_' + id).value) || 0;
  var h = parseInt(document.getElementById('h_' + id).value) || 0;
  var e = parseInt(document.getElementById('e_' + id).value) || 0;
  var d = parseInt(document.getElementById('d_' + id).value) || 0;
  var t = s + h + e;
  document.getElementById('tot_' + id).textContent = t;
  var row = document.getElementById('row_' + id);
  if (s > 0 || h > 0 || e > 0 || d > 0) {
    row.classList.add('saisie-row-filled');
  } else {
    row.classList.remove('saisie-row-filled');
  }
  updateGrandTotals();
  updateMPECounter();
  if (showFilledOnly) {
    if (t === 0 && d === 0) row.classList.add('row-hidden');
    else row.classList.remove('row-hidden');
  }
}

// ---- Totaux generaux ----
function updateGrandTotals() {
  var sumS = 0, sumH = 0, sumE = 0, sumD = 0;
  document.querySelectorAll('.saisie-data-row').forEach(function(row) {
    var id = row.id.replace('row_', '');
    sumS += parseInt(document.getElementById('s_' + id).value) || 0;
    sumH += parseInt(document.getElementById('h_' + id).value) || 0;
    sumE += parseInt(document.getElementById('e_' + id).value) || 0;
    sumD += parseInt(document.getElementById('d_' + id).value) || 0;
  });
  document.getElementById('sumSimples').textContent = sumS;
  document.getElementById('sumHospit').textContent = sumH;
  document.getElementById('sumEvacues').textContent = sumE;
  document.getElementById('sumDecedes').textContent = sumD;
  document.getElementById('sumTotal').textContent = sumS + sumH + sumE;
}

// ---- Compteur MPE ----
function updateMPECounter() {
  var mpeTotal = 0;
  document.querySelectorAll('.saisie-data-row[data-mpe="1"]').forEach(function(row) {
    var id = row.id.replace('row_', '');
    mpeTotal += (parseInt(document.getElementById('s_' + id).value) || 0)
              + (parseInt(document.getElementById('h_' + id).value) || 0)
              + (parseInt(document.getElementById('e_' + id).value) || 0);
  });
  var counter = document.getElementById('mpeCounter');
  if (mpeTotal > 0) {
    document.getElementById('mpeCount').textContent = mpeTotal;
    counter.classList.remove('d-none');
  } else {
    counter.classList.add('d-none');
  }
}

// ---- Marquer les modifications ----
function markChanged(inp) {
  hasChanges = true;
  document.getElementById('draftBadge').classList.add('visible');
  if ((parseInt(inp.value) || 0) > 0) inp.classList.add('changed');
  else inp.classList.remove('changed');
}

// ---- Reinitialiser tout ----
function clearAll() {
  if (!confirm('Effacer toutes les valeurs ?')) return;
  document.querySelectorAll('.saisie-input').forEach(function(inp) {
    inp.value = 0; inp.classList.remove('changed');
  });
  document.querySelectorAll('[id^="tot_"]').forEach(function(el) { el.textContent = '0'; });
  document.querySelectorAll('.saisie-data-row').forEach(function(r) { r.classList.remove('saisie-row-filled'); });
  updateGrandTotals(); updateMPECounter();
  hasChanges = true;
  document.getElementById('draftBadge').classList.add('visible');
}

// ---- Toggle sections ----
function toggleSection(secId, headerRow) {
  var isCollapsed = headerRow.classList.toggle('section-collapsed');
  document.querySelectorAll('.saisie-data-row[data-sec="' + secId + '"]').forEach(function(r) {
    if (isCollapsed) { r.dataset.sectionHidden = '1'; r.classList.add('row-hidden'); }
    else { delete r.dataset.sectionHidden; if (!showFilledOnly || r.classList.contains('saisie-row-filled')) r.classList.remove('row-hidden'); }
  });
}

// ---- Filtre remplies ----
function toggleFilledOnly() {
  showFilledOnly = !showFilledOnly;
  var btn = document.getElementById('toggleFilledBtn');
  if (showFilledOnly) { btn.classList.replace('btn-light', 'btn-success'); btn.title = 'Afficher toutes les lignes'; }
  else { btn.classList.replace('btn-success', 'btn-light'); btn.title = 'Lignes remplies seulement'; }
  document.querySelectorAll('.saisie-data-row').forEach(function(row) {
    if (row.dataset.sectionHidden === '1') return;
    if (showFilledOnly && !row.classList.contains('saisie-row-filled')) row.classList.add('row-hidden');
    else row.classList.remove('row-hidden');
  });
}

// ---- Recherche ----
document.getElementById('searchInput').addEventListener('input', function() {
  var q = this.value.toLowerCase().trim();
  var any = false;
  document.querySelectorAll('.saisie-data-row').forEach(function(row) {
    if ((row.dataset.label || '').indexOf(q) !== -1) { row.classList.remove('row-hidden'); any = true; }
    else row.classList.add('row-hidden');
  });
  document.querySelectorAll('.saisie-section-header').forEach(function(h) {
    var vis = false;
    document.querySelectorAll('.saisie-data-row[data-sec="' + h.dataset.sec + '"]').forEach(function(r) { if (!r.classList.contains('row-hidden')) vis = true; });
    h.style.display = vis ? '' : 'none';
  });
  var nr = document.getElementById('noResultsRow');
  if (q && !any) nr.classList.add('visible'); else nr.classList.remove('visible');
  if (!q) {
    document.querySelectorAll('.saisie-section-header').forEach(function(h) { h.style.display = ''; });
    document.querySelectorAll('.saisie-data-row').forEach(function(row) {
      if (row.dataset.sectionHidden === '1') row.classList.add('row-hidden');
      else if (showFilledOnly && !row.classList.contains('saisie-row-filled')) row.classList.add('row-hidden');
      else row.classList.remove('row-hidden');
    });
  }
});

// ---- Init ----
updateGrandTotals();
updateMPECounter();

// ---- Avertissement depart ----
window.addEventListener('beforeunload', function(e) { if (hasChanges) { e.preventDefault(); e.returnValue = ''; } });
document.getElementById('saisieFrm').addEventListener('submit', function() { hasChanges = false; });