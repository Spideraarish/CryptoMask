// ── DOM refs ──────────────────────────────────────────────────
const trace       = document.getElementById('trace');
const dropzone    = document.getElementById('dropzone');
const fileInput   = document.getElementById('file-input');
const ctxSelect   = document.getElementById('ctx-select');
const verdictIcon = document.getElementById('verdict-icon');
const kmsBox      = document.getElementById('kms-box');
const pkt1        = document.getElementById('pkt1');
const pkt2        = document.getElementById('pkt2');

// ── SVG strings ───────────────────────────────────────────────
// Skull (ransomware blocked)
const SKULL = `<svg viewBox="0 0 64 64" fill="none" stroke="currentColor" stroke-width="2.5">
  <circle cx="32" cy="26" r="18" stroke-width="2.5"/>
  <path d="M22 44v10h20V44" stroke-width="2.5"/>
  <line x1="28" y1="44" x2="28" y2="54" stroke-width="2.5"/>
  <line x1="36" y1="44" x2="36" y2="54" stroke-width="2.5"/>
  <circle cx="24" cy="24" r="4.5" fill="currentColor" stroke="none"/>
  <circle cx="40" cy="24" r="4.5" fill="currentColor" stroke="none"/>
  <path d="M27 35 Q32 39.5 37 35" stroke-linecap="round" stroke-width="2.5"/>
</svg>`;

// Checkmark (access granted)
const CHECK = `<svg viewBox="0 0 64 64" fill="none" stroke="currentColor" stroke-width="3">
  <circle cx="32" cy="32" r="27" stroke-width="2.5"/>
  <path d="M18 33 L28 44 L47 20" stroke-linecap="round" stroke-linejoin="round"/>
</svg>`;

// ── Helpers ───────────────────────────────────────────────────
const sleep = ms => new Promise(r => setTimeout(r, ms));

function log(html) {
  const s = document.createElement('span');
  s.className = 'log';
  s.innerHTML = html;
  trace.appendChild(s);
  trace.scrollTop = trace.scrollHeight;
}

function clearTrace() {
  trace.innerHTML = '';
}

function resetDiagram() {
  // Reset packets (force reflow to allow re-animation)
  pkt1.className = 'packet'; void pkt1.offsetWidth;
  pkt2.className = 'packet'; void pkt2.offsetWidth;

  // Reset KMS node
  kmsBox.className = 'node-box kms-box idle';

  // Reset verdict icon — remove classes so CSS animation re-triggers
  verdictIcon.className = 'verdict-icon';
  verdictIcon.innerHTML = '';
}

// ── Dropzone ──────────────────────────────────────────────────
['dragenter','dragover','dragleave','drop'].forEach(e => {
  dropzone.addEventListener(e, ev => ev.preventDefault());
});
dropzone.addEventListener('dragover',  () => dropzone.classList.add('over'));
dropzone.addEventListener('dragleave', () => dropzone.classList.remove('over'));
dropzone.addEventListener('drop', e => {
  dropzone.classList.remove('over');
  const f = e.dataTransfer.files[0];
  if (f) processFile(f, ctxSelect.value);
});
dropzone.addEventListener('click', e => {
  if (e.target.tagName !== 'SELECT') fileInput.click();
});
fileInput.addEventListener('change', e => {
  if (e.target.files[0]) processFile(e.target.files[0], ctxSelect.value);
});

// ── Public: called from HTML buttons ─────────────────────────
function runDemo(context) { processFile(null, context); }

// ── Core flow ─────────────────────────────────────────────────
async function processFile(file, context) {
  const isRansom = context === 'ransomware';
  clearTrace();
  resetDiagram();

  const fd = new FormData();
  fd.append('context', context);
  if (file) fd.append('file', file);

  const fname = file ? file.name : 'demo_document.txt';
  const fsize = file ? file.size : 53;

  // Step 1 — ingestion
  log(`<span class="c-m">$</span> interceptor caught incoming write request`);
  log(`  file     : <span class="c-w">${fname}</span>`);
  log(`  size     : ${fsize} bytes`);
  log(`  process  : <span class="${isRansom ? 'c-r' : 'c-g'}">${isRansom ? 'RANSOM_CRYPT.exe' : 'Authorized_Backup.exe'}</span>`);
  log(``);

  await sleep(400);

  // Animate packet → KMS
  pkt1.className = 'packet'; void pkt1.offsetWidth;
  pkt1.classList.add(isRansom ? 'go-red' : 'go-green');

  // Step 2 — KMS key lookup
  log(`<span class="c-b">[KMS]</span> master key lookup...`);
  if (isRansom) {
    log(`<span class="c-r">[KMS]</span> DENIED — process not authorised. rogue AES key detected.`);
  } else {
    log(`<span class="c-g">[KMS]</span> master key retrieved from secure store.`);
  }
  log(``);

  await sleep(950);

  // Step 3 — call backend
  let data;
  try {
    const res = await fetch('/api/process', { method: 'POST', body: fd });
    data = await res.json();
  } catch (err) {
    log(`<span class="c-r">[ERROR]</span> ${err.message}`);
    return;
  }

  // Step 4 — HMAC calculation
  log(`<span class="c-p">[HMAC]</span> computing signature...`);
  log(`  formula  : <span class="c-m">HMAC-SHA256( Key ‖ File_ID ‖ Op ‖ Ts )</span>`);
  log(`  op       : ${data.operation}`);
  log(`  ts       : ${data.timestamp}`);
  log(``);

  await sleep(550);

  const eMac = data.expected_mac;
  const pMac = data.mac_provided;
  const match = eMac === pMac;

  log(`  expected : <span class="c-hash">${eMac.slice(0,28)}…</span>`);
  log(`  provided : <span class="${match ? 'c-hash' : 'c-r'}">${pMac.slice(0,28)}…</span>`);
  log(``);

  await sleep(450);

  // Step 5 — Verdict
  if (match) {
    kmsBox.className = 'node-box kms-box success';

    // Inject check SVG and trigger animation
    verdictIcon.innerHTML = CHECK;
    verdictIcon.className = 'verdict-icon v-check visible';

    log(`<span class="c-g">✔  MATCH — write ALLOWED. forwarding to secure storage.</span>`);

    await sleep(750);
    pkt2.className = 'packet'; void pkt2.offsetWidth;
    pkt2.classList.add('go-green');

  } else {
    kmsBox.className = 'node-box kms-box danger';

    // Shake the KMS node
    kmsBox.classList.add('shake');
    setTimeout(() => kmsBox.classList.remove('shake'), 500);

    // Inject skull SVG and trigger animation
    verdictIcon.innerHTML = SKULL;
    verdictIcon.className = 'verdict-icon v-skull visible';

    log(`<span class="c-r">✖  MISMATCH — RANSOMWARE BLOCKED. payload destroyed.</span>`);
    log(`<span class="c-r">   ${data.message}</span>`);
  }

  log(``);
  log(`<span class="c-m">$ _</span>`);
}
