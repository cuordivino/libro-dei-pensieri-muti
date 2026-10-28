/**
 * IL LIBRO DEI PENSIERI MUTI — OMBRE DI LUCE & CHIAROSCURO
 * Logica Applicativa, Audio Engine, Galleria e Personalizzazione
 * Autore: @refuso_di.verso (Cuordivino)
 */

(function () {
  'use strict';

  // --- STATE ---
  let currentIndex = 0;
  let activeMoodFilter = 'all';
  let isPlayingAudio = false;
  let customPhotos = {}; // id -> base64
  let customAudios = {}; // id -> objectURL / base64
  let userCustomPoems = []; // user added poems
  let currentCardStyle = 'chiaroscuro_noir';

  // --- MODALITÀ PUBBLICA / MODIFICA ---
  // I visitatori vedono solo il libro. I controlli per aggiungere poesie, foto e audio
  // (salvati solo nel browser di chi li usa) compaiono aprendo il sito con ?edit=1
  // (per disattivarli di nuovo: ?edit=0).
  try {
    const q = new URLSearchParams(location.search).get('edit');
    if (q === '1') localStorage.setItem('refuso_edit_mode', '1');
    if (q === '0') localStorage.removeItem('refuso_edit_mode');
    if (localStorage.getItem('refuso_edit_mode') === '1') document.body.classList.add('edit-mode');
  } catch (e) {}

  // Load custom data from localStorage
  try {
    const savedPhotos = localStorage.getItem('refuso_custom_photos');
    if (savedPhotos) customPhotos = JSON.parse(savedPhotos);

    const savedPoems = localStorage.getItem('refuso_custom_poems');
    if (savedPoems) userCustomPoems = JSON.parse(savedPoems);
  } catch (e) {
    console.warn('LocalStorage error:', e);
  }

  // Combine default poems with user added poems
  let allPoems = [...BOOK_DATA.poems, ...userCustomPoems];

  // --- AUDIO SYNTHESIS & REAL AUDIO PLAYBACK ---
  let audioCtx = null;
  let synthInterval = null;
  let realAudioEl = null;

  function getAudioContext() {
    if (!audioCtx) {
      const AudioCtx = window.AudioContext || window.webkitAudioContext;
      audioCtx = new AudioCtx();
    }
    if (audioCtx.state === 'suspended') {
      audioCtx.resume();
    }
    return audioCtx;
  }

  // Play realistic neoclassical piano chord note
  function playSynthNote(freq, time, duration = 2.5, volume = 0.15) {
    try {
      const ctx = getAudioContext();
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();

      // Triangle / warm sine hybrid for upright piano sound
      osc.type = 'triangle';
      osc.frequency.setValueAtTime(freq, time);

      // Low pass filter for soft melancholic tone
      const filter = ctx.createBiquadFilter();
      filter.type = 'lowpass';
      filter.frequency.setValueAtTime(1400, time);
      filter.frequency.exponentialRampToValueAtTime(300, time + duration);

      gain.gain.setValueAtTime(0.001, time);
      gain.gain.linearRampToValueAtTime(volume, time + 0.05);
      gain.gain.exponentialRampToValueAtTime(0.0001, time + duration);

      osc.connect(filter);
      filter.connect(gain);
      gain.connect(ctx.destination);

      osc.start(time);
      osc.stop(time + duration);
    } catch (e) {}
  }

  // Chiaroscuro arpeggio patterns based on mood
  const chordProgressions = [
    [220.00, 261.63, 329.63, 392.00], // Am7
    [174.61, 220.00, 261.63, 329.63], // Fmaj7
    [196.00, 246.94, 293.66, 392.00], // G
    [164.81, 196.00, 246.94, 329.63]  // Em
  ];

  function startAtmosphericSoundtrack() {
    stopAtmosphericSoundtrack();
    isPlayingAudio = true;
    updatePlayerUI(true);

    const ctx = getAudioContext();
    let chordIdx = 0;
    let step = 0;

    function playArpeggioStep() {
      if (!isPlayingAudio) return;
      const now = ctx.currentTime;
      const chord = chordProgressions[chordIdx];
      const noteFreq = chord[step % chord.length];

      playSynthNote(noteFreq, now, 3.2, 0.14);

      // Bass note on root
      if (step === 0) {
        playSynthNote(chord[0] / 2, now, 4.0, 0.18);
      }

      step++;
      if (step >= chord.length) {
        step = 0;
        chordIdx = (chordIdx + 1) % chordProgressions.length;
      }
    }

    playArpeggioStep();
    synthInterval = setInterval(playArpeggioStep, 750);
  }

  function stopAtmosphericSoundtrack() {
    isPlayingAudio = false;
    if (synthInterval) {
      clearInterval(synthInterval);
      synthInterval = null;
    }
    if (realAudioEl) {
      realAudioEl.pause();
    }
    updatePlayerUI(false);
  }

  function togglePlayCurrentTrack() {
    const poem = allPoems[currentIndex];
    const customAudio = customAudios[poem.id];

    if (isPlayingAudio) {
      stopAtmosphericSoundtrack();
    } else {
      if (customAudio) {
        realAudioEl.src = customAudio;
        realAudioEl.play().then(() => {
          isPlayingAudio = true;
          updatePlayerUI(true);
        }).catch(() => {
          startAtmosphericSoundtrack();
        });
      } else {
        startAtmosphericSoundtrack();
      }
    }
  }

  function updatePlayerUI(playing) {
    const playerEl = document.getElementById('poem-music-player');
    const playIcon = document.getElementById('play-track-icon');
    const globalBtn = document.getElementById('btn-global-sound');

    if (playerEl) {
      playerEl.classList.toggle('playing', playing);
    }
    if (playIcon) {
      playIcon.textContent = playing ? '❚❚' : '▶';
    }
    if (globalBtn) {
      globalBtn.classList.toggle('playing', playing);
      document.getElementById('global-sound-icon').textContent = playing ? '🔊' : '🔈';
    }
  }

  // --- SPREAD VIEW CONTROLLER ---
  function renderBookPage(index) {
    if (index < 0) index = 0;
    if (index >= allPoems.length) index = allPoems.length - 1;

    currentIndex = index;
    const poem = allPoems[currentIndex];
    if (currentViewName === 'book') setHash('poesia-' + (currentIndex + 1));
    document.title = `${poem.title} · IL LIBRO DEI PENSIERI MUTI`;

    // Left Page: Photo & Music
    const photoImg = document.getElementById('pl-photo-img');
    const photoSrc = customPhotos[poem.id] || poem.image || `images/poesia_${(poem.id % 48) + 1}.jpg`;
    photoImg.src = photoSrc;

    document.getElementById('pl-photo-index').textContent = `FOTOGRAFIA ${currentIndex + 1} / ${allPoems.length}`;
    document.getElementById('pl-track-title').textContent = poem.musicTrack || 'On the Nature of Daylight';
    document.getElementById('pl-track-artist').textContent = poem.musicArtist || 'Max Richter';
    document.getElementById('pl-mood-sense').textContent = poem.moodSense || '';

    // Right Page: Poem
    document.getElementById('pr-section').textContent = `${poem.section} · ${poem.sectionTitle}`;
    document.getElementById('pr-page-num').textContent = (currentIndex + 1);

    const macroObj = BOOK_DATA.meta.macroMoods.find(m => m.key === poem.macroMoodKey) || BOOK_DATA.meta.macroMoods[1];
    document.getElementById('pr-mood-icon').textContent = macroObj.icon;
    document.getElementById('pr-mood-text').textContent = poem.moodPrimary;
    document.getElementById('pr-poem-title').textContent = `${poem.number && poem.number !== '—' ? poem.number + '. ' : ''}${poem.title}`;

    const versesEl = document.getElementById('pr-poem-verses');
    versesEl.textContent = poem.text;
    document.getElementById('pr-sheet-scroll').scrollTop = 0;

    document.getElementById('pr-index-counter').textContent = `Pensiero Muto ${currentIndex + 1} di ${allPoems.length}`;

    // Scrubber
    document.getElementById('scrubber-counter').textContent = `${currentIndex + 1} / ${allPoems.length}`;
    document.getElementById('book-slider').value = currentIndex + 1;
    document.getElementById('book-slider').max = allPoems.length;

    // Mood pills active state
    document.querySelectorAll('#book-mood-pills .mood-filter-pill').forEach(pill => {
      pill.classList.toggle('active', pill.dataset.mood === activeMoodFilter);
    });

    // If audio was playing, keep playing or restart for new atmosphere
    if (isPlayingAudio) {
      updatePlayerUI(true);
    }
  }

  function goToNextPoem() {
    if (currentIndex < allPoems.length - 1) {
      renderBookPage(currentIndex + 1);
    } else {
      showToast('Hai raggiunto l\'ultimo pensiero muto.');
    }
  }

  function goToPreviousPoem() {
    if (currentIndex > 0) {
      renderBookPage(currentIndex - 1);
    } else {
      showToast('Sei alla prima pagina.');
    }
  }

  // --- PHOTO & AUDIO REPLACEMENT HANDLERS ---
  function setupMediaReplacers() {
    const inputPhoto = document.getElementById('input-replace-photo');
    inputPhoto.addEventListener('change', (e) => {
      const file = e.target.files[0];
      if (file) {
        const reader = new FileReader();
        reader.onload = (event) => {
          const base64 = event.target.result;
          const poem = allPoems[currentIndex];
          customPhotos[poem.id] = base64;
          try {
            localStorage.setItem('refuso_custom_photos', JSON.stringify(customPhotos));
          } catch(err) {}
          document.getElementById('pl-photo-img').src = base64;
          showToast('Fotografia sostituita e salvata per questa poesia!');
        };
        reader.readAsDataURL(file);
      }
    });

    const inputAudio = document.getElementById('input-replace-audio');
    inputAudio.addEventListener('change', (e) => {
      const file = e.target.files[0];
      if (file) {
        const poem = allPoems[currentIndex];
        const audioUrl = URL.createObjectURL(file);
        customAudios[poem.id] = audioUrl;
        poem.musicTrack = file.name.replace(/\.[^/.]+$/, "");
        poem.musicArtist = "File Audio Locale";
        document.getElementById('pl-track-title').textContent = poem.musicTrack;
        document.getElementById('pl-track-artist').textContent = poem.musicArtist;

        if (isPlayingAudio) {
          togglePlayCurrentTrack();
          togglePlayCurrentTrack();
        }
        showToast('Traccia audio locale caricata!');
      }
    });

    document.getElementById('btn-play-poem-track').addEventListener('click', togglePlayCurrentTrack);
    document.getElementById('btn-global-sound').addEventListener('click', togglePlayCurrentTrack);
  }

  // --- VIEW SWITCHING ---
  const views = {
    cover: document.getElementById('view-cover'),
    book: document.getElementById('view-book'),
    gallery: document.getElementById('view-gallery'),
    moods: document.getElementById('view-moods'),
    index: document.getElementById('view-index')
  };

  const navBtns = {
    book: document.getElementById('btn-view-book'),
    gallery: document.getElementById('btn-view-gallery'),
    moods: document.getElementById('btn-view-moods'),
    index: document.getElementById('btn-view-index')
  };

  // --- LINK DIRETTI (#poesia-12, #galleria, #stati, #indice, #copertina) ---
  const VIEW_HASH = { cover: 'copertina', gallery: 'galleria', moods: 'stati', index: 'indice' };
  let currentViewName = 'book';

  function setHash(h) {
    try { history.replaceState(null, '', h ? '#' + h : location.pathname + location.search); } catch (e) {}
  }

  function applyHash() {
    const h = decodeURIComponent((location.hash || '').replace(/^#/, ''));
    const m = h.match(/^poesia-(\d+)$/);
    if (m) {
      switchView('book', true);
      renderBookPage(parseInt(m[1], 10) - 1);
      return true;
    }
    const entry = Object.entries(VIEW_HASH).find(([, v]) => v === h);
    if (entry) { switchView(entry[0], true); return true; }
    return false;
  }

  function switchView(viewName, fromHash) {
    Object.values(views).forEach(v => v.classList.remove('active'));
    Object.values(navBtns).forEach(b => b.classList.remove('active'));

    if (views[viewName]) views[viewName].classList.add('active');
    if (navBtns[viewName]) navBtns[viewName].classList.add('active');
    currentViewName = viewName;
    if (!fromHash) setHash(viewName === 'book' ? 'poesia-' + (currentIndex + 1) : VIEW_HASH[viewName]);

    window.scrollTo({ top: 0, behavior: 'smooth' });
  }

  // --- GALLERIA & MUSICA VIEW (INSTAGRAM GRID) ---
  function renderGallery() {
    const grid = document.getElementById('gallery-grid');
    grid.innerHTML = '';

    allPoems.forEach((poem, idx) => {
      const card = document.createElement('div');
      card.className = 'gallery-card';

      const photoSrc = customPhotos[poem.id] || poem.image || `images/poesia_${(poem.id % 48) + 1}.jpg`;

      card.innerHTML = `
        <div class="gc-photo-wrap">
          <img src="${photoSrc}" alt="${poem.title}" loading="lazy">
          <div class="gc-play-overlay">
            <div class="gc-play-btn">▶</div>
          </div>
        </div>
        <div class="gc-info">
          <div class="gc-top">
            <span>#${idx + 1}</span>
            <span class="gc-mood">${poem.moodPrimary}</span>
          </div>
          <h4 class="gc-title">${poem.title}</h4>
          <div class="gc-music">
            <span>🎵</span>
            <span>${poem.musicTrack} — ${poem.musicArtist}</span>
          </div>
        </div>
      `;

      card.addEventListener('click', () => {
        renderBookPage(idx);
        switchView('book');
        if (!isPlayingAudio) {
          togglePlayCurrentTrack();
        }
      });

      grid.appendChild(card);
    });
  }

  // --- STATI D'ANIMO VIEW ---
  function setupMoodsView() {
    const macroGrid = document.getElementById('macro-cards-grid');
    macroGrid.innerHTML = '';

    BOOK_DATA.meta.macroMoods.forEach(mood => {
      const count = mood.key === 'all'
        ? allPoems.length
        : allPoems.filter(p => p.macroMoodKey === mood.key).length;

      const card = document.createElement('div');
      card.className = `macro-card ${mood.key === activeMoodFilter ? 'active' : ''}`;
      card.dataset.mood = mood.key;
      card.innerHTML = `
        <span class="macro-card-icon">${mood.icon}</span>
        <h4 class="macro-card-title">${mood.name}</h4>
        <span class="macro-card-count">${count} Poesie</span>
        <p class="macro-card-desc">${mood.desc}</p>
      `;

      card.addEventListener('click', () => {
        document.querySelectorAll('.macro-card').forEach(c => c.classList.remove('active'));
        card.classList.add('active');
        activeMoodFilter = mood.key;
        renderMoodPoemsGrid(mood.key);
      });

      macroGrid.appendChild(card);
    });

    document.getElementById('btn-clear-filter').addEventListener('click', () => {
      activeMoodFilter = 'all';
      document.querySelectorAll('.macro-card').forEach(c => c.classList.toggle('active', c.dataset.mood === 'all'));
      renderMoodPoemsGrid('all');
    });

    renderMoodPoemsGrid('all');
  }

  function renderMoodPoemsGrid(moodKey) {
    const grid = document.getElementById('mood-poems-grid');
    grid.innerHTML = '';

    const list = moodKey === 'all'
      ? allPoems
      : allPoems.filter(p => p.macroMoodKey === moodKey);

    const bannerTitle = document.getElementById('filter-banner-title');
    const bannerCount = document.getElementById('filter-banner-count');
    const clearBtn = document.getElementById('btn-clear-filter');

    const currentMacro = BOOK_DATA.meta.macroMoods.find(m => m.key === moodKey) || BOOK_DATA.meta.macroMoods[0];
    bannerTitle.textContent = currentMacro.name;
    bannerCount.textContent = `${list.length} componimenti`;
    clearBtn.classList.toggle('hidden', moodKey === 'all');

    list.forEach(poem => {
      const card = document.createElement('div');
      card.className = 'mood-poem-card';

      const previewLines = poem.text.split('\n').filter(l => l.trim().length > 0).slice(0, 3).join('\n');

      card.innerHTML = `
        <div class="mpc-header">
          <span>${poem.section}</span>
          <span class="mpc-mood-tag">${poem.moodPrimary}</span>
        </div>
        <h4 class="mpc-title">${poem.title}</h4>
        <p class="mpc-sense">${poem.moodSense}</p>
        <div class="mpc-preview">${previewLines}...</div>
        <div class="mpc-footer">
          <span>🎵 ${poem.musicTrack}</span>
          <span>Apri →</span>
        </div>
      `;

      card.addEventListener('click', () => {
        const targetIndex = allPoems.findIndex(p => p.id === poem.id);
        renderBookPage(targetIndex);
        switchView('book');
      });

      grid.appendChild(card);
    });
  }

  // --- INDICE VIEW & RICERCA ---
  function setupIndexView() {
    renderIndexSections(allPoems);

    const searchInput = document.getElementById('index-search-input');
    const clearSearchBtn = document.getElementById('btn-clear-search');

    searchInput.addEventListener('input', (e) => {
      const query = e.target.value.trim().toLowerCase();
      clearSearchBtn.classList.toggle('hidden', query.length === 0);

      if (query.length === 0) {
        renderIndexSections(allPoems);
        return;
      }

      const results = allPoems.filter(p => {
        return p.title.toLowerCase().includes(query) ||
               (p.moodPrimary && p.moodPrimary.toLowerCase().includes(query)) ||
               (p.moodSense && p.moodSense.toLowerCase().includes(query)) ||
               (p.musicTrack && p.musicTrack.toLowerCase().includes(query)) ||
               (p.musicArtist && p.musicArtist.toLowerCase().includes(query)) ||
               p.text.toLowerCase().includes(query);
      });

      renderIndexSections(results, query);
    });

    clearSearchBtn.addEventListener('click', () => {
      searchInput.value = '';
      clearSearchBtn.classList.add('hidden');
      renderIndexSections(allPoems);
    });
  }

  function renderIndexSections(poemList, searchQuery = '') {
    const container = document.getElementById('toc-container');
    container.innerHTML = '';

    if (poemList.length === 0) {
      container.innerHTML = `
        <div style="text-align:center; padding: 3rem 1rem; color: #a89f92;">
          <p style="font-size: 1.2rem; font-family: var(--font-serif-body);">Nessun verso trovato per "<em>${searchQuery}</em>".</p>
        </div>
      `;
      return;
    }

    const sections = {};
    poemList.forEach(p => {
      const key = `${p.section}: ${p.sectionTitle}`;
      if (!sections[key]) sections[key] = [];
      sections[key].push(p);
    });

    Object.entries(sections).forEach(([secTitle, pList]) => {
      const block = document.createElement('div');
      block.className = 'toc-section-block';

      const header = document.createElement('div');
      header.className = 'toc-section-header';
      header.innerHTML = `
        <span class="toc-section-title">${secTitle}</span>
        <span style="font-family: var(--font-sans); font-size: 0.72rem; color: #a0a0a0;">${pList.length} poesie</span>
      `;
      block.appendChild(header);

      const listDiv = document.createElement('div');
      listDiv.className = 'toc-poem-list';

      pList.forEach(poem => {
        const item = document.createElement('div');
        item.className = 'toc-item';
        item.innerHTML = `
          <div style="display:flex; align-items:center; gap:0.5rem;">
            <span class="toc-item-num">${poem.id}</span>
            <span class="toc-item-title">${poem.title}</span>
          </div>
          <span class="toc-item-mood">${poem.moodPrimary}</span>
        `;

        item.addEventListener('click', () => {
          const targetIndex = allPoems.findIndex(p => p.id === poem.id);
          renderBookPage(targetIndex);
          switchView('book');
        });

        listDiv.appendChild(item);
      });

      block.appendChild(listDiv);
      container.appendChild(block);
    });
  }

  // --- MODAL: AGGIUNGI NUOVA POESIA DA INSTAGRAM ---
  function setupAddPoemModal() {
    const modal = document.getElementById('modal-add-poem');
    const openBtn = document.getElementById('btn-open-add-modal');
    const closeBtn = document.getElementById('btn-close-add-modal');
    const cancelBtn = document.getElementById('btn-cancel-add');
    const form = document.getElementById('form-add-poem');

    openBtn.addEventListener('click', () => modal.classList.remove('hidden'));
    closeBtn.addEventListener('click', () => modal.classList.add('hidden'));
    cancelBtn.addEventListener('click', () => modal.classList.add('hidden'));

    form.addEventListener('submit', (e) => {
      e.preventDefault();

      const newId = allPoems.length + 1;
      const title = document.getElementById('add-title').value.trim();
      const mood = document.getElementById('add-mood').value.trim();
      const macroKey = document.getElementById('add-macro-mood').value;
      const sense = document.getElementById('add-sense').value.trim();
      const verses = document.getElementById('add-verses').value.trim();
      const trackTitle = document.getElementById('add-track-title').value.trim();
      const trackArtist = document.getElementById('add-track-artist').value.trim();
      const fileInput = document.getElementById('add-photo-file');

      function savePoem(photoData) {
        const newPoem = {
          id: newId,
          number: `${newId}`,
          title: title,
          section: "ARCHIVIO INSTAGRAM",
          sectionTitle: "@refuso_di.verso",
          macroMoodKey: macroKey,
          moodPrimary: mood,
          moodSense: sense,
          text: verses,
          image: photoData || `images/poesia_${((newId - 1) % 48) + 1}.jpg`,
          musicTrack: trackTitle,
          musicArtist: trackArtist,
          audioFile: ""
        };

        userCustomPoems.push(newPoem);
        allPoems.push(newPoem);

        try {
          localStorage.setItem('refuso_custom_poems', JSON.stringify(userCustomPoems));
        } catch(err) {}

        form.reset();
        modal.classList.add('hidden');
        renderBookPage(allPoems.length - 1);
        renderGallery();
        setupMoodsView();
        setupIndexView();
        switchView('book');
        showToast(`Poesia "${title}" aggiunta con successo al libro!`);
      }

      if (fileInput.files && fileInput.files[0]) {
        const reader = new FileReader();
        reader.onload = (ev) => savePoem(ev.target.result);
        reader.readAsDataURL(fileInput.files[0]);
      } else {
        savePoem(null);
      }
    });
  }

  // --- MODAL: INSTAGRAM CARD GENERATOR ---
  function setupCardModal() {
    const modal = document.getElementById('modal-card');
    const closeBtn = document.getElementById('btn-close-modal');
    const stylePills = modal.querySelectorAll('.style-pill');
    const downloadBtn = document.getElementById('btn-download-card');
    const copyCaptionBtn = document.getElementById('btn-copy-ig-caption');

    closeBtn.addEventListener('click', () => modal.classList.add('hidden'));

    stylePills.forEach(pill => {
      pill.addEventListener('click', () => {
        stylePills.forEach(p => p.classList.remove('active'));
        pill.classList.add('active');
        currentCardStyle = pill.dataset.style;
        drawInstagramCanvas(currentIndex, currentCardStyle);
      });
    });

    downloadBtn.addEventListener('click', () => {
      const canvas = document.getElementById('ig-canvas');
      const poem = allPoems[currentIndex];
      const link = document.createElement('a');
      link.download = `refuso_di_verso_${poem.title.toLowerCase().replace(/\s+/g, '_')}.png`;
      link.href = canvas.toDataURL('image/png');
      link.click();
      showToast('Card Instagram in Chiaroscuro scaricata!');
    });

    copyCaptionBtn.addEventListener('click', () => {
      const poem = allPoems[currentIndex];
      const caption = `« ${poem.title} »\n\n${poem.text}\n\nStato d'animo: ${poem.moodPrimary}\n${poem.moodSense}\n\n🎵 Colonna sonora: ${poem.musicTrack} — ${poem.musicArtist}\n\nDa: IL LIBRO DEI PENSIERI MUTI\nAutore: @refuso_di.verso (Cuordivino)\n\n#refusodiverso #pensierimuti #cuordivino #chiaroscuro #fotografiadautore #poesiaitaliana #versi #letteraturacontemporanea`;
      navigator.clipboard.writeText(caption).then(() => {
        showToast('Didascalia con musica e hashtag copiata!');
      });
    });
  }

  function openCardModal(index) {
    const modal = document.getElementById('modal-card');
    const poem = allPoems[index];
    document.getElementById('modal-track-info').textContent = `${poem.musicTrack} — ${poem.musicArtist}`;
    modal.classList.remove('hidden');
    drawInstagramCanvas(index, currentCardStyle);
  }

  function drawInstagramCanvas(index, style) {
    const canvas = document.getElementById('ig-canvas');
    const ctx = canvas.getContext('2d');
    const poem = allPoems[index];

    const W = canvas.width;
    const H = canvas.height;

    // Palette Chiaroscuro
    let bg = '#09090b';
    let text = '#f4f3ee';
    let sub = '#9e9c96';
    let border = 'rgba(255,255,255,0.2)';

    if (style === 'chiaroscuro_silver') {
      bg = '#16161c';
      text = '#ffffff';
      sub = '#b8b8c2';
      border = 'rgba(255,255,255,0.3)';
    } else if (style === 'chiaroscuro_candle') {
      bg = '#110e0c';
      text = '#f7eedb';
      sub = '#c2b39f';
      border = 'rgba(235,210,170,0.25)';
    }

    ctx.fillStyle = bg;
    ctx.fillRect(0, 0, W, H);

    // Subtle grain effect
    for (let i = 0; i < 4000; i++) {
      const gx = Math.random() * W;
      const gy = Math.random() * H;
      ctx.fillStyle = `rgba(255, 255, 255, ${Math.random() * 0.04})`;
      ctx.fillRect(gx, gy, 1.5, 1.5);
    }

    // Outer double frame
    ctx.strokeStyle = border;
    ctx.lineWidth = 2;
    ctx.strokeRect(50, 50, W - 100, H - 100);

    ctx.strokeStyle = 'rgba(255,255,255,0.08)';
    ctx.lineWidth = 1;
    ctx.strokeRect(65, 65, W - 130, H - 130);

    // Top Brand & Symbol
    ctx.textAlign = 'center';
    ctx.font = '36px "Cinzel", serif';
    ctx.fillStyle = text;
    ctx.fillText('☩', W / 2, 130);

    ctx.font = '500 22px "Montserrat", sans-serif';
    ctx.fillStyle = sub;
    ctx.fillText('IL LIBRO DEI PENSIERI MUTI', W / 2, 175);

    ctx.font = 'italic 24px "Cormorant Garamond", Georgia, serif';
    ctx.fillStyle = text;
    ctx.fillText(`— ${poem.moodPrimary} —`, W / 2, 220);

    // Title
    ctx.font = 'bold 44px "Cinzel", serif';
    ctx.fillStyle = text;
    ctx.fillText(poem.title, W / 2, 295);

    // Divider line
    ctx.strokeStyle = 'rgba(255,255,255,0.4)';
    ctx.beginPath();
    ctx.moveTo(W / 2 - 70, 320);
    ctx.lineTo(W / 2 + 70, 320);
    ctx.stroke();

    // Stanzas
    const lines = poem.text.split('\n');
    const displayLines = lines.length > 17 ? lines.slice(0, 17).concat(['...']) : lines;

    ctx.font = '30px "Cormorant Garamond", Georgia, serif';
    ctx.fillStyle = text;

    const startY = 390;
    const lineHeight = 42;
    displayLines.forEach((l, i) => {
      ctx.fillText(l, W / 2, startY + (i * lineHeight));
    });

    // Soundtrack watermark
    ctx.font = 'italic 22px "Montserrat", sans-serif';
    ctx.fillStyle = sub;
    ctx.fillText(`🎵 ${poem.musicTrack} — ${poem.musicArtist}`, W / 2, H - 170);

    // Instagram Tag
    ctx.font = '600 26px "Montserrat", sans-serif';
    ctx.fillStyle = text;
    ctx.fillText('@refuso_di.verso', W / 2, H - 120);

    ctx.font = '18px "Montserrat", sans-serif';
    ctx.fillStyle = sub;
    ctx.fillText('Cuordivino', W / 2, H - 90);
  }

  // --- INITIALIZATION ---
  function init() {
    realAudioEl = document.getElementById('real-audio-player');

    // Navigation buttons
    document.getElementById('btn-go-cover').addEventListener('click', () => switchView('cover'));
    document.getElementById('btn-start-reading').addEventListener('click', () => switchView('book'));
    document.getElementById('btn-explore-gallery-cover').addEventListener('click', () => switchView('gallery'));

    navBtns.book.addEventListener('click', () => switchView('book'));
    navBtns.gallery.addEventListener('click', () => switchView('gallery'));
    navBtns.moods.addEventListener('click', () => switchView('moods'));
    navBtns.index.addEventListener('click', () => switchView('index'));

    // Book View buttons
    document.getElementById('btn-prev-page').addEventListener('click', goToPreviousPoem);
    document.getElementById('btn-next-page').addEventListener('click', goToNextPoem);

    const slider = document.getElementById('book-slider');
    slider.addEventListener('input', (e) => {
      const idx = parseInt(e.target.value, 10) - 1;
      renderBookPage(idx);
    });

    document.getElementById('btn-copy-verses').addEventListener('click', () => {
      const poem = allPoems[currentIndex];
      const textToCopy = `«${poem.title}»\nStato d'animo: ${poem.moodPrimary}\n\n${poem.text}\n\n— @refuso_di.verso (Cuordivino)\nIL LIBRO DEI PENSIERI MUTI`;
      navigator.clipboard.writeText(textToCopy).then(() => {
        showToast('Poesia copiata negli appunti!');
      });
    });

    document.getElementById('btn-copy-link').addEventListener('click', () => {
      const url = location.origin + location.pathname + '#poesia-' + (currentIndex + 1);
      const done = () => showToast('Link alla poesia copiato!');
      if (navigator.clipboard && window.isSecureContext) navigator.clipboard.writeText(url).then(done, () => window.prompt('Copia il link:', url));
      else window.prompt('Copia il link:', url);
    });

    document.getElementById('btn-share-card').addEventListener('click', () => {
      openCardModal(currentIndex);
    });

    // Quick Mood Pills in Book View
    const pillsContainer = document.getElementById('book-mood-pills');
    pillsContainer.innerHTML = '';
    BOOK_DATA.meta.macroMoods.forEach(mood => {
      const pill = document.createElement('button');
      pill.className = `mood-filter-pill ${mood.key === activeMoodFilter ? 'active' : ''}`;
      pill.dataset.mood = mood.key;
      pill.innerHTML = `<span>${mood.icon}</span> <span>${mood.name}</span>`;
      pill.addEventListener('click', () => {
        activeMoodFilter = mood.key;
        document.querySelectorAll('#book-mood-pills .mood-filter-pill').forEach(p => {
          p.classList.toggle('active', p.dataset.mood === mood.key);
        });
        const matched = allPoems.find(p => mood.key === 'all' || p.macroMoodKey === mood.key);
        if (matched) {
          const idx = allPoems.findIndex(p => p.id === matched.id);
          renderBookPage(idx);
        }
      });
      pillsContainer.appendChild(pill);
    });

    // Keyboard navigation
    window.addEventListener('keydown', (e) => {
      if (document.getElementById('modal-card').classList.contains('hidden') &&
          document.getElementById('modal-add-poem').classList.contains('hidden')) {
        if (e.key === 'ArrowRight' || e.key === 'PageDown') goToNextPoem();
        else if (e.key === 'ArrowLeft' || e.key === 'PageUp') goToPreviousPoem();
        else if (e.key === ' ') {
          e.preventDefault();
          togglePlayCurrentTrack();
        }
      } else if (e.key === 'Escape') {
        document.getElementById('modal-card').classList.add('hidden');
        document.getElementById('modal-add-poem').classList.add('hidden');
      }
    });

    setupMediaReplacers();
    setupAddPoemModal();
    setupCardModal();
    setupMoodsView();
    setupIndexView();
    renderGallery();
    if (!applyHash()) renderBookPage(0);
    window.addEventListener('hashchange', applyHash);
  }

  function showToast(msg) {
    const toast = document.getElementById('toast-notification');
    document.getElementById('toast-text').textContent = msg;
    toast.classList.remove('hidden');
    clearTimeout(toast._timeout);
    toast._timeout = setTimeout(() => toast.classList.add('hidden'), 3200);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
