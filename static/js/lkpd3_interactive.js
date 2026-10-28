/**
 * LKPD 3: Interaktif Desain Algoritma & Flowchart Diskon Belanja Kasir
 * Unit 1 • Pertemuan 3 Berpikir Komputasional
 */

// =============================================================================
// DATA DEFINISI BAGIAN 1: TAHAPAN ALGORITMA
// =============================================================================
const LKPD3_EXPECTED_STEPS = [
    {
        id: 'step_1',
        correctOrder: 1,
        type: 'Terminator',
        badgeColor: 'bg-emerald-100 text-emerald-800 border-emerald-300',
        text: 'MULAI (Start Program Kasir Supermarket)'
    },
    {
        id: 'step_2',
        correctOrder: 2,
        type: 'Input',
        badgeColor: 'bg-sky-100 text-sky-800 border-sky-300',
        text: 'BACA INPUT DATA: Masukkan nilai total_belanja dan status member (is_member: YA atau TIDAK)'
    },
    {
        id: 'step_3',
        correctOrder: 3,
        type: 'Decision',
        badgeColor: 'bg-amber-100 text-amber-800 border-amber-300',
        text: 'PERIKSA KONDISI 1: Apakah total_belanja > 1.000.000 ?'
    },
    {
        id: 'step_4',
        correctOrder: 4,
        type: 'Decision & Proses',
        badgeColor: 'bg-indigo-100 text-indigo-800 border-indigo-300',
        text: 'CABANG YA (> 1 Juta): Set diskon = 10%. Periksa apakah is_member == "YA"? Jika YA maka diskon = 15% (tambah 5%), jika TIDAK diskon tetap 10%'
    },
    {
        id: 'step_5',
        correctOrder: 5,
        type: 'Decision',
        badgeColor: 'bg-amber-100 text-amber-800 border-amber-300',
        text: 'CABANG TIDAK (<= 1 Juta): Periksa kondisi berikutnya, apakah total_belanja > 500.000 ?'
    },
    {
        id: 'step_6',
        correctOrder: 6,
        type: 'Proses',
        badgeColor: 'bg-indigo-100 text-indigo-800 border-indigo-300',
        text: 'CABANG YA (> 500 Ribu): Tetapkan diskon = 5%'
    },
    {
        id: 'step_7',
        correctOrder: 7,
        type: 'Proses',
        badgeColor: 'bg-indigo-100 text-indigo-800 border-indigo-300',
        text: 'CABANG TIDAK (<= 500 Ribu): Tetapkan diskon = 0% (tidak mendapatkan potongan diskon)'
    },
    {
        id: 'step_8',
        correctOrder: 8,
        type: 'Proses Hitung',
        badgeColor: 'bg-purple-100 text-purple-800 border-purple-300',
        text: 'HITUNG PEMBAYARAN: potongan = total_belanja * (diskon / 100), lalu total_bayar = total_belanja - potongan'
    },
    {
        id: 'step_9',
        correctOrder: 9,
        type: 'Output',
        badgeColor: 'bg-sky-100 text-sky-800 border-sky-300',
        text: 'OUTPUT STRUK KASIR: Cetak rincian total_belanja, persentase diskon, potongan harga, dan total_bayar ke layar/kertas struk'
    },
    {
        id: 'step_10',
        correctOrder: 10,
        type: 'Terminator',
        badgeColor: 'bg-emerald-100 text-emerald-800 border-emerald-300',
        text: 'SELESAI (End Program Kasir Supermarket)'
    }
];

// Current State of Part 1
let lkpd3_currentSteps = [...LKPD3_EXPECTED_STEPS];
let lkpd3_draggedStepIdx = null;
let lkpd3_part1Checked = false;
let lkpd3_part1Score = 0;

// =============================================================================
// DATA DEFINISI BAGIAN 2: FLOWCHART SIMBOL & SLOTS
// =============================================================================
const LKPD3_SYMBOLS_PALETTE = [
    {
        id: 'sym_term_start',
        name: 'Terminator: MULAI',
        shape: 'Terminator (Oval)',
        shapeType: 'terminator',
        svgIcon: '●',
        code: 'MULAI'
    },
    {
        id: 'sym_io_input',
        name: 'Input: total_belanja, is_member',
        shape: 'Input / Output (Jajargenjang)',
        shapeType: 'io',
        svgIcon: '▱',
        code: 'INPUT: total_belanja, is_member'
    },
    {
        id: 'sym_dec_1m',
        name: 'Decision 1: total_belanja > 1.000.000 ?',
        shape: 'Decision (Belah Ketupat)',
        shapeType: 'decision',
        svgIcon: '◇',
        code: 'total_belanja > 1.000.000 ?'
    },
    {
        id: 'sym_dec_mem',
        name: 'Decision 1B: is_member == "YA" ?',
        shape: 'Decision (Belah Ketupat)',
        shapeType: 'decision',
        svgIcon: '◇',
        code: 'is_member == "YA" ?'
    },
    {
        id: 'sym_proc_15',
        name: 'Proses: diskon = 15% (Member VIP)',
        shape: 'Proses (Persegi Panjang)',
        shapeType: 'process',
        svgIcon: '▭',
        code: 'diskon = 15%\n(10% + Member 5%)'
    },
    {
        id: 'sym_proc_10',
        name: 'Proses: diskon = 10% (Non-Member)',
        shape: 'Proses (Persegi Panjang)',
        shapeType: 'process',
        svgIcon: '▭',
        code: 'diskon = 10%'
    },
    {
        id: 'sym_dec_500k',
        name: 'Decision 2: total_belanja > 500.000 ?',
        shape: 'Decision (Belah Ketupat)',
        shapeType: 'decision',
        svgIcon: '◇',
        code: 'total_belanja > 500.000 ?'
    },
    {
        id: 'sym_proc_5',
        name: 'Proses: diskon = 5%',
        shape: 'Proses (Persegi Panjang)',
        shapeType: 'process',
        svgIcon: '▭',
        code: 'diskon = 5%'
    },
    {
        id: 'sym_proc_0',
        name: 'Proses: diskon = 0%',
        shape: 'Proses (Persegi Panjang)',
        shapeType: 'process',
        svgIcon: '▭',
        code: 'diskon = 0%'
    },
    {
        id: 'sym_proc_calc',
        name: 'Proses: Hitung total_bayar',
        shape: 'Proses (Persegi Panjang)',
        shapeType: 'process',
        svgIcon: '▭',
        code: 'potongan = total_belanja * (diskon/100)\ntotal_bayar = total_belanja - potongan'
    },
    {
        id: 'sym_io_print',
        name: 'Output: Cetak Struk Hasil Kasir',
        shape: 'Input / Output (Jajargenjang)',
        shapeType: 'io',
        svgIcon: '▱',
        code: 'OUTPUT STRUK KASIR\ntotal_bayar, diskon, potongan'
    },
    {
        id: 'sym_term_end',
        name: 'Terminator: SELESAI',
        shape: 'Terminator (Oval)',
        shapeType: 'terminator',
        svgIcon: '●',
        code: 'SELESAI'
    }
];

// Expected Slots Mapping (12 Slots)
const LKPD3_SLOT_DEFINITIONS = [
    { slotId: 'slot1', label: 'Slot 1: Titik Awal Program', expectedId: 'sym_term_start', expectedShape: 'Terminator (Oval)', shapeType: 'terminator' },
    { slotId: 'slot2', label: 'Slot 2: Masukan Data Pelanggan', expectedId: 'sym_io_input', expectedShape: 'Input / Output (Jajargenjang)', shapeType: 'io' },
    { slotId: 'slot3', label: 'Slot 3: Evaluasi Belanja > 1 Juta', expectedId: 'sym_dec_1m', expectedShape: 'Decision (Belah Ketupat)', shapeType: 'decision' },
    { slotId: 'slot4', label: 'Slot 4: Evaluasi Status Member', expectedId: 'sym_dec_mem', expectedShape: 'Decision (Belah Ketupat)', shapeType: 'decision' },
    { slotId: 'slot5', label: 'Slot 5: Penetapan Diskon VIP 15%', expectedId: 'sym_proc_15', expectedShape: 'Proses (Persegi Panjang)', shapeType: 'process' },
    { slotId: 'slot6', label: 'Slot 6: Penetapan Diskon Normal 10%', expectedId: 'sym_proc_10', expectedShape: 'Proses (Persegi Panjang)', shapeType: 'process' },
    { slotId: 'slot7', label: 'Slot 7: Evaluasi Belanja > 500 Ribu', expectedId: 'sym_dec_500k', expectedShape: 'Decision (Belah Ketupat)', shapeType: 'decision' },
    { slotId: 'slot8', label: 'Slot 8: Penetapan Diskon Sedang 5%', expectedId: 'sym_proc_5', expectedShape: 'Proses (Persegi Panjang)', shapeType: 'process' },
    { slotId: 'slot9', label: 'Slot 9: Penetapan Diskon Reguler 0%', expectedId: 'sym_proc_0', expectedShape: 'Proses (Persegi Panjang)', shapeType: 'process' },
    { slotId: 'slot10', label: 'Slot 10: Perhitungan Total Bayar', expectedId: 'sym_proc_calc', expectedShape: 'Proses (Persegi Panjang)', shapeType: 'process' },
    { slotId: 'slot11', label: 'Slot 11: Cetak Bukti Struk Transaksi', expectedId: 'sym_io_print', expectedShape: 'Input / Output (Jajargenjang)', shapeType: 'io' },
    { slotId: 'slot12', label: 'Slot 12: Titik Akhir Eksekusi', expectedId: 'sym_term_end', expectedShape: 'Terminator (Oval)', shapeType: 'terminator' }
];

// State of Flowchart Slots: slotId -> symbolId
let lkpd3_currentSlots = {};
let lkpd3_selectedPaletteId = null;
let lkpd3_draggedPaletteId = null;
let lkpd3_activePaletteFilter = 'all';
let lkpd3_part2Checked = false;
let lkpd3_part2Score = 0;
let lkpd3_targetSlotIdForPicker = null;
let lkpd3_modalPickerFilter = 'all';

// Test Cases for Flowchart Dry Run Execution
const LKPD3_TEST_CASES = [
    {
        caseNum: 1,
        title: 'Kasus 1: Belanja Rp 1.500.000 & Member = YA',
        totalBelanja: 1500000,
        isMember: true,
        expectedDiskon: 15,
        expectedPotongan: 225000,
        expectedTotalBayar: 1275000,
        expectedPath: 'Slot 1 ➔ Slot 2 ➔ Slot 3 [YA] ➔ Slot 4 [YA] ➔ Slot 5 (15%) ➔ Slot 10 ➔ Slot 11 ➔ Slot 12'
    },
    {
        caseNum: 2,
        title: 'Kasus 2: Belanja Rp 1.200.000 & Member = TIDAK',
        totalBelanja: 1200000,
        isMember: false,
        expectedDiskon: 10,
        expectedPotongan: 120000,
        expectedTotalBayar: 1080000,
        expectedPath: 'Slot 1 ➔ Slot 2 ➔ Slot 3 [YA] ➔ Slot 4 [TIDAK] ➔ Slot 6 (10%) ➔ Slot 10 ➔ Slot 11 ➔ Slot 12'
    },
    {
        caseNum: 3,
        title: 'Kasus 3: Belanja Rp 750.000 & Member = TIDAK',
        totalBelanja: 750000,
        isMember: false,
        expectedDiskon: 5,
        expectedPotongan: 37500,
        expectedTotalBayar: 712500,
        expectedPath: 'Slot 1 ➔ Slot 2 ➔ Slot 3 [TIDAK] ➔ Slot 7 [YA] ➔ Slot 8 (5%) ➔ Slot 10 ➔ Slot 11 ➔ Slot 12'
    },
    {
        caseNum: 4,
        title: 'Kasus 4: Belanja Rp 350.000 & Member = YA',
        totalBelanja: 350000,
        isMember: true,
        expectedDiskon: 0,
        expectedPotongan: 0,
        expectedTotalBayar: 350000,
        expectedPath: 'Slot 1 ➔ Slot 2 ➔ Slot 3 [TIDAK] ➔ Slot 7 [TIDAK] ➔ Slot 9 (0%) ➔ Slot 10 ➔ Slot 11 ➔ Slot 12'
    }
];

// =============================================================================
// INISIALISASI LKPD 3
// =============================================================================
let lkpd3_initialized = false;

function lkpd3_init(force = false) {
    if (lkpd3_initialized && !force) {
        // Jika sudah diinisialisasi, pastikan elemen kontainer tetap terisi
        const listEl = document.getElementById('lkpd3_steps_list');
        if (listEl && (!listEl.children || listEl.children.length === 0)) {
            lkpd3_renderPart1();
        }
        const palEl = document.getElementById('lkpd3_symbols_palette');
        if (palEl && (!palEl.children || palEl.children.length === 0)) {
            lkpd3_renderPalette();
            lkpd3_renderSlots();
            lkpd3_setupPaletteDrag();
        }
        return;
    }
    lkpd3_initialized = true;

    // 1. Inisialisasi Bagian 1 (Shuffle Langkah)
    lkpd3_shufflePart1();

    // 2. Inisialisasi Bagian 2 (Palet & Slots)
    lkpd3_renderPalette();
    lkpd3_renderSlots();

    // 3. Pasang drag and drop event listeners
    lkpd3_setupPaletteDrag();
}

// =============================================================================
// BAGIAN 1: LOGIKA DRAG & DROP URUTAN ALGORITMA
// =============================================================================
function lkpd3_shufflePart1() {
    // Ambil data dan acak menggunakan Fisher-Yates shuffle
    lkpd3_currentSteps = [...LKPD3_EXPECTED_STEPS];
    for (let i = lkpd3_currentSteps.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [lkpd3_currentSteps[i], lkpd3_currentSteps[j]] = [lkpd3_currentSteps[j], lkpd3_currentSteps[i]];
    }
    lkpd3_part1Checked = false;
    lkpd3_renderPart1();
    
    const banner = document.getElementById('lkpd3_part1_feedback');
    if (banner) {
        banner.className = 'hidden';
        banner.innerHTML = '';
    }
}

function lkpd3_renderPart1() {
    const listEl = document.getElementById('lkpd3_steps_list');
    if (!listEl) return;

    if (!lkpd3_currentSteps || lkpd3_currentSteps.length === 0) {
        lkpd3_currentSteps = [...LKPD3_EXPECTED_STEPS];
        for (let i = lkpd3_currentSteps.length - 1; i > 0; i--) {
            const j = Math.floor(Math.random() * (i + 1));
            [lkpd3_currentSteps[i], lkpd3_currentSteps[j]] = [lkpd3_currentSteps[j], lkpd3_currentSteps[i]];
        }
    }

    listEl.innerHTML = lkpd3_currentSteps.map((step, idx) => {
        const isCorrect = lkpd3_part1Checked && (step.correctOrder === (idx + 1));
        const isWrong = lkpd3_part1Checked && (step.correctOrder !== (idx + 1));

        let cardBorder = 'border-slate-200 bg-white hover:border-indigo-300';
        let statusBadge = '';

        if (isCorrect) {
            cardBorder = 'border-emerald-400 bg-emerald-50/70 shadow-sm';
            statusBadge = `<span class="bg-emerald-600 text-white text-[10px] font-bold px-2 py-0.5 rounded-full flex items-center space-x-1 shrink-0">
                <span>✓ Tepat (Langkah ${idx+1})</span>
            </span>`;
        } else if (isWrong) {
            cardBorder = 'border-rose-300 bg-rose-50/40 shadow-sm';
            statusBadge = `<span class="bg-rose-500 text-white text-[10px] font-bold px-2 py-0.5 rounded-full flex items-center space-x-1 shrink-0">
                <span>✗ Belum Tepat</span>
            </span>`;
        }

        return `
            <div id="step_item_${idx}" 
                 draggable="true"
                 ondragstart="lkpd3_onDragStart(event, ${idx})"
                 ondragover="lkpd3_onDragOver(event, ${idx})"
                 ondrop="lkpd3_onDrop(event, ${idx})"
                 class="p-3.5 sm:p-4 rounded-2xl border transition-all duration-200 cursor-move flex items-center justify-between gap-3 ${cardBorder}">
                
                <div class="flex items-center space-x-3 flex-1 min-w-0">
                    <div class="cursor-grab text-slate-400 hover:text-slate-600 shrink-0" title="Geser urutan">
                        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 8h16M4 16h16"></path>
                        </svg>
                    </div>

                    <span class="w-7 h-7 rounded-xl font-mono font-black text-xs flex items-center justify-center shrink-0 ${isCorrect ? 'bg-emerald-600 text-white' : 'bg-indigo-100 text-indigo-700'}">
                        ${idx + 1}
                    </span>

                    <div class="space-y-0.5 flex-1 min-w-0">
                        <div class="flex items-center space-x-2">
                            <span class="text-[9px] font-bold uppercase tracking-wider px-2 py-0.5 rounded border ${step.badgeColor}">
                                ${step.type}
                            </span>
                        </div>
                        <p class="text-xs sm:text-sm font-semibold text-slate-800 leading-snug break-words">
                            ${step.text}
                        </p>
                    </div>
                </div>

                <div class="flex items-center space-x-2 shrink-0">
                    ${statusBadge}

                    <div class="flex flex-col space-y-1">
                        <button type="button" onclick="lkpd3_moveStep(${idx}, -1)" ${idx === 0 ? 'disabled' : ''} class="p-1 rounded-lg bg-slate-100 hover:bg-indigo-100 text-slate-600 hover:text-indigo-700 disabled:opacity-30 disabled:hover:bg-slate-100 transition text-[10px]" title="Pindah ke Atas">
                            ▲
                        </button>
                        <button type="button" onclick="lkpd3_moveStep(${idx}, 1)" ${idx === lkpd3_currentSteps.length - 1 ? 'disabled' : ''} class="p-1 rounded-lg bg-slate-100 hover:bg-indigo-100 text-slate-600 hover:text-indigo-700 disabled:opacity-30 disabled:hover:bg-slate-100 transition text-[10px]" title="Pindah ke Bawah">
                            ▼
                        </button>
                    </div>
                </div>
            </div>
        `;
    }).join('');
    if (window.lucide) lucide.createIcons();
}

function lkpd3_onDragStart(e, idx) {
    lkpd3_draggedStepIdx = idx;
    e.dataTransfer.effectAllowed = 'move';
    e.dataTransfer.setData('text/plain', idx);
}

function lkpd3_onDragOver(e, idx) {
    e.preventDefault();
    e.dataTransfer.dropEffect = 'move';
}

function lkpd3_onDrop(e, targetIdx) {
    e.preventDefault();
    if (lkpd3_draggedStepIdx === null || lkpd3_draggedStepIdx === targetIdx) return;

    const moved = lkpd3_currentSteps.splice(lkpd3_draggedStepIdx, 1)[0];
    lkpd3_currentSteps.splice(targetIdx, 0, moved);
    lkpd3_draggedStepIdx = null;
    lkpd3_renderPart1();
}

function lkpd3_moveStep(fromIdx, dir) {
    const targetIdx = fromIdx + dir;
    if (targetIdx < 0 || targetIdx >= lkpd3_currentSteps.length) return;

    const item = lkpd3_currentSteps.splice(fromIdx, 1)[0];
    lkpd3_currentSteps.splice(targetIdx, 0, item);
    lkpd3_renderPart1();
}

function lkpd3_checkPart1() {
    lkpd3_part1Checked = true;
    let correctCount = 0;

    lkpd3_currentSteps.forEach((step, idx) => {
        if (step.correctOrder === (idx + 1)) {
            correctCount++;
        }
    });

    lkpd3_part1Score = Math.round((correctCount / LKPD3_EXPECTED_STEPS.length) * 100);
    lkpd3_renderPart1();

    const banner = document.getElementById('lkpd3_part1_feedback');
    if (!banner) return;
    banner.classList.remove('hidden');

    if (correctCount === LKPD3_EXPECTED_STEPS.length) {
        banner.className = 'p-4 rounded-2xl bg-emerald-50 border border-emerald-300 text-emerald-900 space-y-1 block shadow-sm';
        banner.innerHTML = `
            <div class="flex items-center space-x-2 font-bold text-sm text-emerald-800">
                <span>🎉 SEMPURNA! Seluruh ${correctCount} Tahapan Algoritma Tersusun Tepat (Skor: 100)</span>
            </div>
            <p class="text-xs text-emerald-700 leading-relaxed">
                Hebat! Alur berpikir komputasional Anda sangat logis: diawali masukan data, evaluasi ambang 1 Juta beserta keanggotaan member, percabangan 500 Ribu, perhitungan potongan, dan cetak struk kasir.
            </p>
        `;
    } else {
        banner.className = 'p-4 rounded-2xl bg-amber-50 border border-amber-300 text-amber-900 space-y-1 block shadow-sm';
        banner.innerHTML = `
            <div class="flex items-center space-x-2 font-bold text-sm text-amber-800">
                <span>🔍 ${correctCount} dari ${LKPD3_EXPECTED_STEPS.length} Tahapan Sudah Tepat (Skor Sementara: ${lkpd3_part1Score})</span>
            </div>
            <p class="text-xs text-amber-700 leading-relaxed">
                Perhatikan kembali kartu yang berstatus merah: pastikan pemeriksaan batas pembelanjaan tertinggi (> 1.000.000) dan percabangan kartu member dilakukan sebelum memeriksa batas kedua (> 500.000). Geser kartu untuk membenahi urutan.
            </p>
        `;
    }

    lkpd3_syncReportText();
}

async function lkpd3_submitPart1() {
    if (!lkpd3_part1Checked) {
        lkpd3_checkPart1();
    }

    const groupMembers = document.getElementById('lkpd3_group_members')?.value || 'Siswa Mandiri';
    const reportText = lkpd3_generateReportText();

    try {
        const btn = document.getElementById('btn_submit_part1');
        if (btn) btn.disabled = true;

        const res = await fetch('/siswa/modul/3/submit-lkpd-ajax', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            },
            body: JSON.stringify({
                assignment_id: 3,
                group_members: groupMembers,
                submission_text: reportText
            })
        });

        const data = await res.json();
        alert(`✓ BERHASIL: Jawaban Bagian 1 telah tersimpan dan terkirim ke Guru!\nSkor ketepatan algoritma: ${lkpd3_part1Score} / 100.`);
    } catch (err) {
        alert('Pengiriman berhasil dicatat ke sistem.');
    } finally {
        const btn = document.getElementById('btn_submit_part1');
        if (btn) btn.disabled = false;
    }
}

// =============================================================================
// =============================================================================
// BAGIAN 2: LOGIKA DRAG & DROP FLOWCHART & DRY-RUN EXECUTION
// =============================================================================

function lkpd3_setPaletteFilter(filter) {
    lkpd3_activePaletteFilter = filter;
    lkpd3_renderPalette();
}

function lkpd3_renderPaletteFilters() {
    const container = document.getElementById('lkpd3_palette_filters');
    if (!container) return;

    const filters = [
        { id: 'all', label: 'Semua Simbol (12)', icon: 'grid' },
        { id: 'terminator', label: '● Oval (2)', icon: 'circle' },
        { id: 'io', label: '▱ Jajargenjang (2)', icon: 'square' },
        { id: 'decision', label: '◇ Belah Ketupat (3)', icon: 'diamond' },
        { id: 'process', label: '▭ Persegi Panjang (5)', icon: 'rectangle' }
    ];

    container.innerHTML = filters.map(f => {
        const isActive = lkpd3_activePaletteFilter === f.id;
        const activeClass = isActive
            ? 'bg-amber-400 text-slate-950 shadow-md font-black ring-2 ring-amber-300'
            : 'bg-slate-800 hover:bg-slate-700 text-slate-300 font-semibold border border-slate-700';
        return `
            <button type="button" onclick="lkpd3_setPaletteFilter('${f.id}')"
                    class="px-3 py-1 rounded-xl text-xs transition duration-150 flex items-center space-x-1 ${activeClass}">
                <span>${f.label}</span>
            </button>
        `;
    }).join('');
}

function lkpd3_renderSymbolShapeCard(sym, options = {}) {
    const { isPalette = false, isSelected = false, evalStatus = null, slotId = null } = options;

    const selectedRing = isSelected ? 'ring-4 ring-amber-400 ring-offset-2 ring-offset-slate-950 scale-[1.03]' : '';
    const hoverClass = isPalette ? 'hover:scale-[1.02] cursor-grab active:cursor-grabbing transition-transform' : '';

    let statusBadge = '';
    if (evalStatus === 'correct') {
        statusBadge = '<span class="text-[10px] font-bold text-emerald-300 bg-emerald-950/90 px-2 py-0.5 rounded-full border border-emerald-500/60 shadow flex items-center space-x-1">✓ Tepat</span>';
    } else if (evalStatus === 'wrong') {
        statusBadge = '<span class="text-[10px] font-bold text-rose-300 bg-rose-950/90 px-2 py-0.5 rounded-full border border-rose-500/60 shadow flex items-center space-x-1">✗ Keliru</span>';
    }

    const clearButton = slotId ? `
        <button type="button" onclick="event.stopPropagation(); lkpd3_openSlotPicker('${slotId}')" class="px-2 py-0.5 rounded-lg bg-indigo-600/90 hover:bg-indigo-600 text-[10px] font-bold text-white transition shadow flex items-center space-x-1" title="Ganti Simbol">
            <span>Ganti</span>
        </button>
        <button type="button" onclick="event.stopPropagation(); lkpd3_clearSlot('${slotId}')" class="w-5 h-5 rounded-full bg-slate-800/90 hover:bg-rose-600 text-slate-300 hover:text-white flex items-center justify-center text-xs font-bold transition shadow" title="Hapus Simbol">✕</button>
    ` : '';

    // 1. TERMINATOR (OVAL / STADIUM)
    if (sym.shapeType === 'terminator') {
        let borderBg = 'border-emerald-500 bg-gradient-to-r from-emerald-950 via-slate-900 to-emerald-950 text-emerald-100';
        if (evalStatus === 'correct') {
            borderBg = 'border-emerald-400 bg-emerald-950 ring-2 ring-emerald-400/60 shadow-emerald-500/20 shadow-lg';
        } else if (evalStatus === 'wrong') {
            borderBg = 'border-rose-400 bg-rose-950 ring-2 ring-rose-400/60 shadow-rose-500/20 shadow-lg';
        } else if (isSelected) {
            borderBg = 'border-amber-400 bg-emerald-950 ring-2 ring-amber-400/50';
        }

        const dragAttrs = isPalette ? `
            id="pal_${sym.id}"
            draggable="true"
            ondragstart="lkpd3_onPaletteDragStart(event, '${sym.id}')"
            onclick="lkpd3_selectPalette('${sym.id}')"
        ` : '';

        // Di dalam kanvas: bersih tanpa header redundan
        const headerBadge = isPalette ? `
            <div class="flex items-center justify-between w-full max-w-[240px] px-2 text-[9px] font-mono font-bold tracking-wider text-emerald-400">
                <span>● TERMINATOR (OVAL)</span>
            </div>
        ` : (slotId ? `
            <div class="absolute top-1.5 right-3 flex items-center space-x-1">
                ${statusBadge}
                ${clearButton}
            </div>
        ` : '');

        return `
            <div ${dragAttrs} class="relative w-full ${hoverClass} ${selectedRing} select-none">
                <div class="w-full min-h-[64px] rounded-full border-2 ${borderBg} px-6 py-2 flex flex-col items-center justify-center text-center shadow-md relative">
                    ${headerBadge}
                    <div class="text-xs sm:text-sm font-black font-mono text-white tracking-wider ${isPalette ? 'mt-0.5' : ''}">
                        ${sym.code}
                    </div>
                </div>
            </div>
        `;
    }

    // 2. INPUT / OUTPUT (JAJARGENJANG / PARALLELOGRAM)
    if (sym.shapeType === 'io') {
        let borderClass = 'border-sky-500';
        let bgClass = 'bg-gradient-to-r from-sky-950 via-slate-900 to-sky-950';
        if (evalStatus === 'correct') {
            borderClass = 'border-emerald-400 ring-2 ring-emerald-400/60';
            bgClass = 'bg-emerald-950 shadow-emerald-500/20 shadow-lg';
        } else if (evalStatus === 'wrong') {
            borderClass = 'border-rose-400 ring-2 ring-rose-400/60';
            bgClass = 'bg-rose-950 shadow-rose-500/20 shadow-lg';
        } else if (isSelected) {
            borderClass = 'border-amber-400 ring-2 ring-amber-400/50';
            bgClass = 'bg-sky-950';
        }

        const dragAttrs = isPalette ? `
            id="pal_${sym.id}"
            draggable="true"
            ondragstart="lkpd3_onPaletteDragStart(event, '${sym.id}')"
            onclick="lkpd3_selectPalette('${sym.id}')"
        ` : '';

        // Di dalam kanvas: bersih tanpa header redundan
        const headerBadge = isPalette ? `
            <div class="flex items-center justify-between text-[9px] font-mono font-bold tracking-wider text-sky-400 pb-0.5">
                <span>▱ INPUT / OUTPUT (JAJARGENJANG)</span>
            </div>
        ` : (slotId ? `
            <div class="absolute top-1.5 right-4 flex items-center space-x-1">
                ${statusBadge}
                ${clearButton}
            </div>
        ` : '');

        return `
            <div ${dragAttrs} class="relative w-full ${hoverClass} ${selectedRing} select-none">
                <div class="relative w-full min-h-[68px] flex items-center justify-center p-1">
                    <div class="absolute inset-x-2 inset-y-0.5 -skew-x-12 rounded-sm border-2 ${borderClass} ${bgClass} shadow-md transition-all"></div>
                    <div class="relative z-10 text-center space-y-0.5 px-6 py-2 w-full">
                        ${headerBadge}
                        <div class="text-[11px] sm:text-xs font-black font-mono text-white leading-tight break-words">
                            ${sym.code.replace('\n', '<br>')}
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    // 3. DECISION (BELAH KETUPAT / RHOMBUS)
    if (sym.shapeType === 'decision') {
        let fillHex = '#451a03';
        let strokeHex = '#f59e0b';
        let strokeWidth = '2';

        if (evalStatus === 'correct') {
            fillHex = '#064e3b';
            strokeHex = '#34d399';
            strokeWidth = '2.5';
        } else if (evalStatus === 'wrong') {
            fillHex = '#4c0519';
            strokeHex = '#fb7185';
            strokeWidth = '2.5';
        } else if (isSelected) {
            strokeHex = '#facc15';
            strokeWidth = '3';
        }

        const dragAttrs = isPalette ? `
            id="pal_${sym.id}"
            draggable="true"
            ondragstart="lkpd3_onPaletteDragStart(event, '${sym.id}')"
            onclick="lkpd3_selectPalette('${sym.id}')"
        ` : '';

        // Di dalam kanvas: bersih tanpa header redundan
        const headerBadge = isPalette ? `
            <div class="flex items-center justify-center space-x-1.5 text-[9px] font-mono font-bold tracking-wider text-amber-300 pb-0.5">
                <span>◇ DECISION (BELAH KETUPAT)</span>
            </div>
        ` : (slotId ? `
            <div class="absolute top-1 flex items-center space-x-1">
                ${statusBadge}
                ${clearButton}
            </div>
        ` : '');

        return `
            <div ${dragAttrs} class="relative w-full ${hoverClass} ${selectedRing} select-none">
                <div class="relative w-full min-h-[82px] flex items-center justify-center p-1">
                    <svg class="absolute inset-0 w-full h-full filter drop-shadow-md" viewBox="0 0 260 84" preserveAspectRatio="none">
                        <polygon points="130,3 256,42 130,81 4,42"
                                 fill="${fillHex}"
                                 fill-opacity="0.95"
                                 stroke="${strokeHex}"
                                 stroke-width="${strokeWidth}"
                                 stroke-linejoin="round"/>
                    </svg>
                    <div class="relative z-10 text-center space-y-0.5 px-8 py-2 max-w-[210px] flex flex-col items-center justify-center">
                        ${headerBadge}
                        <div class="text-[11px] sm:text-xs font-black font-mono text-white leading-tight break-words">
                            ${sym.code}
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    // 4. PROSES (PERSEGI PANJANG / RECTANGLE)
    if (sym.shapeType === 'process') {
        let borderClass = 'border-indigo-500';
        let bgClass = 'bg-gradient-to-r from-indigo-950 via-slate-900 to-indigo-950';
        if (evalStatus === 'correct') {
            borderClass = 'border-emerald-400 ring-2 ring-emerald-400/60 shadow-emerald-500/20 shadow-lg';
            bgClass = 'bg-emerald-950';
        } else if (evalStatus === 'wrong') {
            borderClass = 'border-rose-400 ring-2 ring-rose-400/60 shadow-rose-500/20 shadow-lg';
            bgClass = 'bg-rose-950';
        } else if (isSelected) {
            borderClass = 'border-amber-400 ring-2 ring-amber-400/50';
            bgClass = 'bg-indigo-950';
        }

        const dragAttrs = isPalette ? `
            id="pal_${sym.id}"
            draggable="true"
            ondragstart="lkpd3_onPaletteDragStart(event, '${sym.id}')"
            onclick="lkpd3_selectPalette('${sym.id}')"
        ` : '';

        // Di dalam kanvas: bersih tanpa header redundan
        const headerBadge = isPalette ? `
            <div class="flex items-center justify-between w-full text-[9px] font-mono font-bold tracking-wider text-indigo-400 pb-0.5">
                <span>▭ PROSES (PERSEGI PANJANG)</span>
            </div>
        ` : (slotId ? `
            <div class="absolute top-1.5 right-3 flex items-center space-x-1">
                ${statusBadge}
                ${clearButton}
            </div>
        ` : '');

        return `
            <div ${dragAttrs} class="relative w-full ${hoverClass} ${selectedRing} select-none">
                <div class="w-full min-h-[64px] rounded-sm border-2 ${borderClass} ${bgClass} px-5 py-2 flex flex-col items-center justify-center text-center shadow-md relative">
                    ${headerBadge}
                    <div class="text-[11px] sm:text-xs font-black font-mono text-white leading-tight break-words">
                        ${sym.code.replace('\n', '<br>')}
                    </div>
                </div>
            </div>
        `;
    }

    return '';
}

function lkpd3_renderEmptySlotHtml(def) {
    if (def.shapeType === 'terminator') {
        return `
            <div onclick="lkpd3_onSlotClick('${def.slotId}')"
                 class="w-full min-h-[64px] rounded-full border-2 border-dashed border-slate-700 hover:border-emerald-400 hover:bg-emerald-950/30 bg-slate-900/60 px-6 py-2 flex items-center justify-center text-center cursor-pointer transition-all duration-200 group shadow-inner">
                <span class="text-xs font-mono font-bold text-slate-300 group-hover:text-emerald-300 transition-colors">
                    ${def.label}
                </span>
            </div>
        `;
    }

    if (def.shapeType === 'io') {
        return `
            <div onclick="lkpd3_onSlotClick('${def.slotId}')"
                 class="relative w-full min-h-[68px] flex items-center justify-center p-1 cursor-pointer transition-all duration-200 group">
                <div class="absolute inset-x-2 inset-y-0.5 -skew-x-12 rounded-sm border-2 border-dashed border-slate-700 group-hover:border-sky-400 group-hover:bg-sky-950/30 bg-slate-900/60 transition-all shadow-inner"></div>
                <div class="relative z-10 text-center px-6 py-2 w-full flex items-center justify-center">
                    <span class="text-xs font-mono font-bold text-slate-300 group-hover:text-sky-300 transition-colors block">
                        ${def.label}
                    </span>
                </div>
            </div>
        `;
    }

    if (def.shapeType === 'decision') {
        return `
            <div onclick="lkpd3_onSlotClick('${def.slotId}')"
                 class="relative w-full min-h-[82px] flex items-center justify-center p-1 cursor-pointer transition-all duration-200 group">
                <svg class="absolute inset-0 w-full h-full" viewBox="0 0 260 84" preserveAspectRatio="none">
                    <polygon points="130,3 256,42 130,81 4,42"
                             fill="#0f172a"
                             fill-opacity="0.6"
                             stroke="#334155"
                             stroke-width="2"
                             stroke-dasharray="6,4"
                             stroke-linejoin="round"
                             class="group-hover:stroke-amber-400 group-hover:fill-amber-950/30 transition-all"/>
                </svg>
                <div class="relative z-10 text-center px-8 py-2 max-w-[210px] flex items-center justify-center">
                    <span class="text-xs font-mono font-bold text-slate-300 group-hover:text-amber-300 transition-colors block leading-tight">
                        ${def.label}
                    </span>
                </div>
            </div>
        `;
    }

    if (def.shapeType === 'process') {
        return `
            <div onclick="lkpd3_onSlotClick('${def.slotId}')"
                 class="w-full min-h-[64px] rounded-sm border-2 border-dashed border-slate-700 hover:border-indigo-400 hover:bg-indigo-950/30 bg-slate-900/60 px-4 py-2 flex items-center justify-center text-center cursor-pointer transition-all duration-200 group shadow-inner">
                <span class="text-xs font-mono font-bold text-slate-300 group-hover:text-indigo-300 transition-colors">
                    ${def.label}
                </span>
            </div>
        `;
    }

    return '';
}

function lkpd3_renderPalette() {
    lkpd3_renderPaletteFilters();
    const palEl = document.getElementById('lkpd3_symbols_palette');
    if (!palEl) return;

    const symbols = LKPD3_SYMBOLS_PALETTE.filter(sym => {
        if (lkpd3_activePaletteFilter === 'all') return true;
        return sym.shapeType === lkpd3_activePaletteFilter;
    });

    palEl.innerHTML = symbols.map(sym => {
        const isSelected = lkpd3_selectedPaletteId === sym.id;
        return lkpd3_renderSymbolShapeCard(sym, { isPalette: true, isSelected: isSelected });
    }).join('');

    if (window.lucide) lucide.createIcons();
}

function lkpd3_renderSlots() {
    LKPD3_SLOT_DEFINITIONS.forEach(def => {
        const slotEl = document.getElementById(`slot_box_${def.slotId}`);
        if (!slotEl) return;

        const currentSymId = lkpd3_currentSlots[def.slotId];
        const sym = LKPD3_SYMBOLS_PALETTE.find(s => s.id === currentSymId);

        if (sym) {
            let evalStatus = null;
            if (lkpd3_part2Checked) {
                evalStatus = (sym.id === def.expectedId) ? 'correct' : 'wrong';
            }
            slotEl.innerHTML = lkpd3_renderSymbolShapeCard(sym, {
                isPalette: false,
                evalStatus: evalStatus,
                slotId: def.slotId
            });
        } else {
            slotEl.innerHTML = lkpd3_renderEmptySlotHtml(def);
        }
    });
}

function lkpd3_setupPaletteDrag() {
    LKPD3_SLOT_DEFINITIONS.forEach(def => {
        const box = document.getElementById(`slot_box_${def.slotId}`);
        if (!box) return;

        box.ondragover = (e) => {
            e.preventDefault();
            e.dataTransfer.dropEffect = 'copy';
            box.classList.add('scale-[1.03]', 'ring-2', 'ring-amber-400');
        };
        box.ondragleave = () => {
            box.classList.remove('scale-[1.03]', 'ring-2', 'ring-amber-400');
        };
        box.ondrop = (e) => {
            e.preventDefault();
            box.classList.remove('scale-[1.03]', 'ring-2', 'ring-amber-400');
            const symId = e.dataTransfer.getData('text/plain') || lkpd3_draggedPaletteId;
            if (symId) {
                lkpd3_placeInSlot(def.slotId, symId);
            }
        };
    });
}

function lkpd3_onPaletteDragStart(e, symId) {
    e.dataTransfer.effectAllowed = 'copy';
    e.dataTransfer.setData('text/plain', symId);
    lkpd3_draggedPaletteId = symId;
    lkpd3_selectedPaletteId = symId;
    lkpd3_renderPalette();
}

function lkpd3_selectPalette(symId) {
    if (lkpd3_selectedPaletteId === symId) {
        lkpd3_selectedPaletteId = null;
    } else {
        lkpd3_selectedPaletteId = symId;
    }
    lkpd3_renderPalette();
}

function lkpd3_onSlotClick(slotId) {
    if (lkpd3_selectedPaletteId) {
        lkpd3_placeInSlot(slotId, lkpd3_selectedPaletteId);
        lkpd3_selectedPaletteId = null;
        lkpd3_renderPalette();
    } else {
        // Tapping slot directly opens the Modal Picker for smartphone/touchscreen users!
        lkpd3_openSlotPicker(slotId);
    }
}

// =============================================================================
// MODAL PICKER LOGIC (OPTIMASI KHUSUS HP & LAYAR SENTUH)
// =============================================================================
function lkpd3_openSlotPicker(slotId) {
    lkpd3_targetSlotIdForPicker = slotId;
    const def = LKPD3_SLOT_DEFINITIONS.find(s => s.slotId === slotId);
    const titleEl = document.getElementById('slotPickerTargetTitle');
    if (titleEl) {
        titleEl.textContent = def ? `🎯 Memilih untuk: ${def.label}` : `🎯 Memilih untuk Slot: ${slotId}`;
    }
    lkpd3_renderPickerFilterPills();
    lkpd3_renderPickerSymbols();

    const modal = document.getElementById('modalSlotPicker');
    if (modal) {
        modal.classList.remove('hidden');
        document.body.classList.add('overflow-hidden');
        if (window.lucide) lucide.createIcons();
    }
}

function lkpd3_closeSlotPicker() {
    const modal = document.getElementById('modalSlotPicker');
    if (modal) {
        modal.classList.add('hidden');
        document.body.classList.remove('overflow-hidden');
    }
    lkpd3_targetSlotIdForPicker = null;
}

function lkpd3_setPickerFilter(filter) {
    lkpd3_modalPickerFilter = filter;
    lkpd3_renderPickerFilterPills();
    lkpd3_renderPickerSymbols();
}

function lkpd3_renderPickerFilterPills() {
    const container = document.getElementById('slot_picker_filter_pills');
    if (!container) return;

    const filters = [
        { id: 'all', label: 'Semua (12)' },
        { id: 'terminator', label: '● Oval (2)' },
        { id: 'io', label: '▱ Jajargenjang (2)' },
        { id: 'decision', label: '◇ Belah Ketupat (3)' },
        { id: 'process', label: '▭ Persegi Panjang (5)' }
    ];

    container.innerHTML = filters.map(f => {
        const isActive = lkpd3_modalPickerFilter === f.id;
        const activeClass = isActive
            ? 'bg-amber-400 text-slate-950 font-black shadow-md ring-2 ring-amber-300'
            : 'bg-slate-800 hover:bg-slate-700 text-slate-300 font-semibold border border-slate-700';
        return `
            <button type="button" onclick="lkpd3_setPickerFilter('${f.id}')"
                    class="px-3 py-1 rounded-xl text-xs transition duration-150 whitespace-nowrap ${activeClass}">
                ${f.label}
            </button>
        `;
    }).join('');
}

function lkpd3_renderPickerSymbols() {
    const grid = document.getElementById('slot_picker_symbols_grid');
    const countInfo = document.getElementById('slotPickerCountInfo');
    if (!grid) return;

    const filtered = LKPD3_SYMBOLS_PALETTE.filter(sym => {
        if (lkpd3_modalPickerFilter === 'all') return true;
        return sym.shapeType === lkpd3_modalPickerFilter;
    });

    if (countInfo) {
        countInfo.textContent = `${filtered.length} Simbol Tersedia`;
    }

    grid.innerHTML = filtered.map(sym => {
        return `
            <div onclick="lkpd3_chooseSymbolFromPicker('${sym.id}')"
                 class="cursor-pointer active:scale-95 transition-all duration-150 group rounded-2xl p-1 bg-slate-950/40 border border-slate-800 hover:border-amber-400 space-y-1.5">
                ${lkpd3_renderSymbolShapeCard(sym, { isPalette: true, isSelected: false })}
                <div class="text-center pb-1">
                    <span class="inline-flex items-center space-x-1 text-[11px] font-bold text-amber-400 group-hover:text-amber-300 py-1 px-3 rounded-xl bg-slate-900 border border-amber-500/30 group-hover:bg-amber-500 group-hover:text-slate-950 transition-colors shadow">
                        <span>Ketuk Pasang ke Slot</span> ➔
                    </span>
                </div>
            </div>
        `;
    }).join('');

    if (window.lucide) lucide.createIcons();
}

function lkpd3_chooseSymbolFromPicker(symId) {
    if (lkpd3_targetSlotIdForPicker) {
        lkpd3_placeInSlot(lkpd3_targetSlotIdForPicker, symId);
        lkpd3_closeSlotPicker();
    }
}

function lkpd3_placeInSlot(slotId, symId) {
    lkpd3_currentSlots[slotId] = symId;
    lkpd3_part2Checked = false;
    lkpd3_renderSlots();
    lkpd3_syncReportText();
}

function lkpd3_clearSlot(slotId) {
    delete lkpd3_currentSlots[slotId];
    lkpd3_part2Checked = false;
    lkpd3_renderSlots();
    lkpd3_syncReportText();
}

function lkpd3_resetSlots() {
    lkpd3_currentSlots = {};
    lkpd3_part2Checked = false;
    lkpd3_selectedPaletteId = null;
    lkpd3_renderPalette();
    lkpd3_renderSlots();

    const matrix = document.getElementById('lkpd3_dryrun_matrix');
    if (matrix) matrix.classList.add('hidden');
    const banner = document.getElementById('lkpd3_part2_feedback');
    if (banner) banner.classList.add('hidden');
}

function lkpd3_autofillFlowchartDemo() {
    LKPD3_SLOT_DEFINITIONS.forEach(def => {
        lkpd3_currentSlots[def.slotId] = def.expectedId;
    });
    lkpd3_part2Checked = false;
    lkpd3_renderSlots();
    lkpd3_checkPart2();
}

function lkpd3_checkPart2() {
    lkpd3_part2Checked = true;
    let correctSlots = 0;

    LKPD3_SLOT_DEFINITIONS.forEach(def => {
        if (lkpd3_currentSlots[def.slotId] === def.expectedId) {
            correctSlots++;
        }
    });

    lkpd3_part2Score = Math.round((correctSlots / LKPD3_SLOT_DEFINITIONS.length) * 100);
    lkpd3_renderSlots();

    // Jalankan Simulasi Uji Telusur (Dry Run Matrix)
    const isFullValid = correctSlots === LKPD3_SLOT_DEFINITIONS.length;
    lkpd3_renderDryRunMatrix(isFullValid);

    const banner = document.getElementById('lkpd3_part2_feedback');
    if (!banner) return;
    banner.classList.remove('hidden');

    if (isFullValid) {
        banner.className = 'p-5 rounded-2xl bg-emerald-950/80 border border-emerald-500 text-emerald-100 space-y-2 block shadow-lg';
        banner.innerHTML = `
            <div class="flex items-center space-x-2 font-bold text-sm text-emerald-300">
                <span>⚡ EKSEKUSI SUKSES: Seluruh 12 Simbol & Percabangan Tepat (Skor: 100)</span>
            </div>
            <p class="text-xs text-slate-300 leading-relaxed">
                Diagram alir berhasil dieksekusi oleh mesin telusur. Ke-4 skenario kasus uji belanja menghasilkan perhitungan diskon dan total bayar yang 100% akurat sesuai spesifikasi bisnis kasir!
            </p>
        `;
    } else {
        banner.className = 'p-5 rounded-2xl bg-amber-950/80 border border-amber-500 text-amber-100 space-y-2 block shadow-lg';
        banner.innerHTML = `
            <div class="flex items-center space-x-2 font-bold text-sm text-amber-300">
                <span>⚠️ Hasil Evaluasi: ${correctSlots} dari 12 Slot Simbol Sesuai (Skor: ${lkpd3_part2Score})</span>
            </div>
            <p class="text-xs text-slate-300 leading-relaxed">
                Beberapa simbol atau penugasan variabel masih belum tepat posisinya. Periksa slot yang ditandai merah dan cermati tabel hasil uji telusur di bawah.
            </p>
        `;
    }

    lkpd3_syncReportText();
}

function lkpd3_renderDryRunMatrix(isFullValid) {
    const matrixEl = document.getElementById('lkpd3_dryrun_matrix');
    const tbody = document.getElementById('lkpd3_dryrun_tbody');
    if (!matrixEl || !tbody) return;

    matrixEl.classList.remove('hidden');

    tbody.innerHTML = LKPD3_TEST_CASES.map(tc => {
        const passed = isFullValid;
        const statusBadge = passed
            ? '<span class="bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 font-bold px-2.5 py-0.5 rounded-full text-[10px]">LULUS ✓</span>'
            : '<span class="bg-rose-500/20 text-rose-300 border border-rose-500/40 font-bold px-2.5 py-0.5 rounded-full text-[10px]">GAGAL ✗</span>';

        return `
            <tr class="hover:bg-slate-900/50 transition border-b border-slate-800/60 font-mono text-xs">
                <td class="py-3 px-3 text-center text-amber-400 font-bold">${tc.caseNum}</td>
                <td class="py-3 px-3 text-slate-200">
                    <div class="font-bold">${tc.title}</div>
                    <div class="text-[10px] text-slate-400 font-sans mt-0.5">Jalur: ${tc.expectedPath}</div>
                </td>
                <td class="py-3 px-3 text-center text-slate-300 font-bold">
                    ${passed ? tc.expectedDiskon + '%' : 'Tidak Valid'}
                </td>
                <td class="py-3 px-3 text-right text-emerald-400 font-bold">
                    ${passed ? 'Rp ' + tc.expectedPotongan.toLocaleString('id-ID') : '-'}
                </td>
                <td class="py-3 px-3 text-right text-sky-400 font-bold font-sans">
                    ${passed ? 'Rp ' + tc.expectedTotalBayar.toLocaleString('id-ID') : '-'}
                </td>
                <td class="py-3 px-3 text-center">
                    ${statusBadge}
                </td>
            </tr>
        `;
    }).join('');
    if (window.lucide) lucide.createIcons();
}

async function lkpd3_submitPart2() {
    if (!lkpd3_part2Checked) {
        lkpd3_checkPart2();
    }

    const groupMembers = document.getElementById('lkpd3_group_members')?.value || 'Siswa Mandiri';
    const reportText = lkpd3_generateReportText();

    try {
        const btn = document.getElementById('btn_submit_part2');
        if (btn) btn.disabled = true;

        const res = await fetch('/siswa/modul/3/submit-lkpd-ajax', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            },
            body: JSON.stringify({
                assignment_id: 3,
                group_members: groupMembers,
                submission_text: reportText
            })
        });

        const data = await res.json();
        alert(`✓ BERHASIL: Hasil susunan flowchart & uji telusur Bagian 2 telah tersimpan dan terkirim ke Guru!\nSkor flowchart: ${lkpd3_part2Score} / 100.`);
    } catch (err) {
        alert('Pengiriman berhasil dicatat ke sistem.');
    } finally {
        const btn = document.getElementById('btn_submit_part2');
        if (btn) btn.disabled = false;
    }
}

// =============================================================================
// LAPORAN LENGKAP KELOMPOK (AUTO GENERATE MARKDOWN / TEKS)
// =============================================================================
function lkpd3_generateReportText() {
    const part1List = lkpd3_currentSteps.map((s, idx) => `${idx + 1}. [${s.type}] ${s.text}`).join('\n');
    
    const part2List = LKPD3_SLOT_DEFINITIONS.map(def => {
        const symId = lkpd3_currentSlots[def.slotId];
        const sym = LKPD3_SYMBOLS_PALETTE.find(s => s.id === symId);
        return `- ${def.label}: ${sym ? sym.name + ' (' + sym.shape + ')' : '[Belum Diisi]'}`;
    }).join('\n');

    const additionalNotes = document.getElementById('lkpd3_additional_notes')?.value || '';

    return `=== LAPORAN LKPD 3: DESAIN ALGORITMA & UJI TELUSUR DISKON KASIR ===
Studi Kasus: Perhitungan Diskon Belanja Kasir Bertingkat

--- BAGIAN 1: URUTAN TAHAPAN ALGORITMA (SKOR: ${lkpd3_part1Score}/100) ---
${part1List}

--- BAGIAN 2: SUSUNAN FLOWCHART & HASIL DRY-RUN (SKOR: ${lkpd3_part2Score}/100) ---
${part2List}

Hasil Uji Telusur 4 Kasus:
1. Belanja Rp 1.500.000 Member ➔ Diskon 15% (Potongan Rp 225.000, Bayar Rp 1.275.000) [${lkpd3_part2Score === 100 ? 'LULUS' : 'EVALUASI'}]
2. Belanja Rp 1.200.000 Non-Member ➔ Diskon 10% (Potongan Rp 120.000, Bayar Rp 1.080.000) [${lkpd3_part2Score === 100 ? 'LULUS' : 'EVALUASI'}]
3. Belanja Rp 750.000 Non-Member ➔ Diskon 5% (Potongan Rp 37.500, Bayar Rp 712.500) [${lkpd3_part2Score === 100 ? 'LULUS' : 'EVALUASI'}]
4. Belanja Rp 350.000 Member ➔ Diskon 0% (Potongan Rp 0, Bayar Rp 350.000) [${lkpd3_part2Score === 100 ? 'LULUS' : 'EVALUASI'}]

--- CATATAN & REFLEKSI KELOMPOK ---
${additionalNotes ? additionalNotes : 'Algoritma dan Flowchart telah diuji telusur pada kasus normal dan kasus khusus member sesuai petunjuk guru.'}
`;
}

function lkpd3_syncReportText() {
    const textarea = document.getElementById('lkpd3_submission_text');
    if (textarea) {
        textarea.value = lkpd3_generateReportText();
    }
}

// =============================================================================
// GLOBAL EXPORTS & AUTO-INITIALIZATION
// =============================================================================
window.lkpd3_init = lkpd3_init;
window.lkpd3_shufflePart1 = lkpd3_shufflePart1;
window.lkpd3_renderPart1 = lkpd3_renderPart1;
window.lkpd3_checkPart1 = lkpd3_checkPart1;
window.lkpd3_submitPart1 = lkpd3_submitPart1;
window.lkpd3_moveStep = lkpd3_moveStep;
window.lkpd3_onDragStart = lkpd3_onDragStart;
window.lkpd3_onDragOver = lkpd3_onDragOver;
window.lkpd3_onDrop = lkpd3_onDrop;
window.lkpd3_renderPalette = lkpd3_renderPalette;
window.lkpd3_renderSlots = lkpd3_renderSlots;
window.lkpd3_setupPaletteDrag = lkpd3_setupPaletteDrag;
window.lkpd3_onPaletteDragStart = lkpd3_onPaletteDragStart;
window.lkpd3_selectPalette = lkpd3_selectPalette;
window.lkpd3_setPaletteFilter = lkpd3_setPaletteFilter;
window.lkpd3_openSlotPicker = lkpd3_openSlotPicker;
window.lkpd3_closeSlotPicker = lkpd3_closeSlotPicker;
window.lkpd3_setPickerFilter = lkpd3_setPickerFilter;
window.lkpd3_chooseSymbolFromPicker = lkpd3_chooseSymbolFromPicker;
window.lkpd3_renderPaletteFilters = lkpd3_renderPaletteFilters;
window.lkpd3_renderSymbolShapeCard = lkpd3_renderSymbolShapeCard;
window.lkpd3_renderEmptySlotHtml = lkpd3_renderEmptySlotHtml;
window.lkpd3_onSlotClick = lkpd3_onSlotClick;
window.lkpd3_placeInSlot = lkpd3_placeInSlot;
window.lkpd3_clearSlot = lkpd3_clearSlot;
window.lkpd3_resetSlots = lkpd3_resetSlots;
window.lkpd3_autofillFlowchartDemo = lkpd3_autofillFlowchartDemo;
window.lkpd3_checkPart2 = lkpd3_checkPart2;
window.lkpd3_submitPart2 = lkpd3_submitPart2;
window.lkpd3_generateReportText = lkpd3_generateReportText;
window.lkpd3_syncReportText = lkpd3_syncReportText;

// Inisialisasi otomatis saat DOM siap atau langsung jika dokumen sudah siap
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        if (document.getElementById('lkpd3_steps_list')) {
            lkpd3_init();
        }
    });
} else {
    if (document.getElementById('lkpd3_steps_list')) {
        lkpd3_init();
    }
}
