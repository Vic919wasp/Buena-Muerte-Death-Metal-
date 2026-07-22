/* ============================================================
   CONTEXTO: JS compartido del sitio multi-page de Buena Muerte.
             Nav mobile toggle, scroll-header shadow, active nav
             link en scroll, smooth-scroll con offset, uptime
             clock opcional, form handlers fake (newsletter/contact),
             carga lazy de Spotify embeds y render de fechas FECHAS[].
   ============================================================
   ÍNDICE DE SECCIONES
   [01] Helpers               - línea 8
   [02] Datos editables       - línea 18
   [03] Nav / toggle mobile   - línea 35
   [04] Active link scroll    - línea 60
   [05] Smooth scroll anchor  - línea 80
   [06] Tour render           - línea 95
   [07] Spotify lazy load     - línea 130
   [08] Newsletter / contact  - línea 145
   ============================================================ */

/* EDITAR acá para cargar fechas. Vacío = estado cero visible. */
var FECHAS = [
  // { dia:'02', mes:'AGO', anio:'2026', lugar:'Reventados Bar', ciudad:'Quilmes, GBA', link:'#' }
];

/* ============================================================
   [01] Helpers
   ============================================================ */
function qs(s, ctx) { return (ctx || document).querySelector(s); }
function qsa(s, ctx) { return Array.prototype.slice.call((ctx || document).querySelectorAll(s)); }
function pad(n) { return n < 10 ? '0' + n : '' + n; }

/* ============================================================
   [02] Datos editables
   ============================================================ */
var SPOTIFY_EMBEDS = {
  catalepsia: 'https://open.spotify.com/embed/album/0nX9lEtTJa4RyqgMglpKzX?theme=0',
  diosEsSadico: 'https://open.spotify.com/embed/album/1j8MNMHY4KHASmOtpKXXCT?theme=0'
};

/* ============================================================
   [03] Nav / toggle mobile
   ============================================================ */
function initNav() {
  var nav = qs('.site-nav');
  var toggle = qs('.site-nav__toggle');
  if (!toggle || !nav) { return; }
  toggle.addEventListener('click', function () { nav.classList.toggle('is-open'); });
  qsa('.site-nav a').forEach(function (a) {
    a.addEventListener('click', function () { nav.classList.remove('is-open'); });
  });
}

/* ============================================================
   [04] Active link en scroll (IntersectionObserver)
   ============================================================ */
function initActiveLink() {
  var links = qsa('.site-nav a');
  if (!links.length || !('IntersectionObserver' in window)) { return; }
  var map = {};
  links.forEach(function (l) {
    var href = l.getAttribute('href');
    if (href && href.indexOf('#') === 0 && href !== '#') {
      var target = document.querySelector(href);
      if (target) { map[href] = l; }
    }
  });
  var io = new IntersectionObserver(function (entries) {
    entries.forEach(function (e) {
      var l = map['#' + e.target.id];
      if (!l) { return; }
      if (e.isIntersecting) {
        links.forEach(function (x) { x.classList.remove('is-active'); });
        l.classList.add('is-active');
      }
    });
  }, { rootMargin: '-30% 0px -60% 0px' });
  Object.keys(map).forEach(function (k) { io.observe(document.querySelector(k)); });
}

/* ============================================================
   [05] Smooth scroll con offset (respeta header sticky)
   ============================================================ */
function initSmoothScroll() {
  qsa('a[href^="#"]').forEach(function (a) {
    a.addEventListener('click', function (ev) {
      var href = a.getAttribute('href');
      if (href === '#' || href === '#top') {
        ev.preventDefault();
        window.scrollTo({ top: 0, behavior: 'smooth' });
        return;
      }
      var target = document.querySelector(href);
      if (!target) { return; }
      ev.preventDefault();
      var top = target.getBoundingClientRect().top + window.scrollY - 70;
      window.scrollTo({ top: top, behavior: 'smooth' });
    });
  });
}

/* ============================================================
   [06] Tour render
   ============================================================ */
function renderFechas() {
  var empty = qs('#tourEmpty');
  var table = qs('#tourTable');
  var body  = qs('#tourBody');
  var head  = qs('#tourHeader');
  if (!empty || !table) { return; }
  if (!FECHAS.length) { return; }
  empty.style.display = 'none';
  table.style.display = 'table';
  if (head) { head.textContent = FECHAS.length + ' fecha' + (FECHAS.length === 1 ? '' : 's') + ' confirmada' + (FECHAS.length === 1 ? '' : 's'); }
  body.innerHTML = FECHAS.map(function (f) {
    return '<tr><td class="dia">' + f.dia + '<br><span style="font-size:.55rem;letter-spacing:.25em;color:var(--bronce);">' + (f.mes || '') + ' ' + (f.anio || '') + '</span></td>' +
           '<td class="lugar">' + f.lugar + '<span>' + (f.ciudad || '') + '</span></td>' +
           '<td class="btt"><a href="' + (f.link || '#') + '" target="_blank" rel="noopener">ENTRADAS ›</a></td></tr>';
  }).join('');
}

/* ============================================================
   [07] Spotify lazy load (carga src al hacer visible el disco)
   ============================================================ */
function initSpotifyLazy() {
  var embeds = qsa('[data-spotify]');
  if (!embeds.length || !('IntersectionObserver' in window)) {
    embeds.forEach(function (el) {
      var key = el.getAttribute('data-spotify');
      if (SPOTIFY_EMBEDS[key]) { el.src = SPOTIFY_EMBEDS[key]; }
    });
    return;
  }
  var io = new IntersectionObserver(function (entries) {
    entries.forEach(function (e) {
      if (e.isIntersecting) {
        var key = e.target.getAttribute('data-spotify');
        if (SPOTIFY_EMBEDS[key] && !e.target.src) { e.target.src = SPOTIFY_EMBEDS[key]; }
        io.unobserve(e.target);
      }
    });
  }, { rootMargin: '200px 0px' });
  embeds.forEach(function (el) { io.observe(el); });
}

/* ============================================================
   [08] Newsletter / Contact
   ============================================================ */
function copyToClipboard(text) {
  if (navigator.clipboard && navigator.clipboard.writeText) {
    navigator.clipboard.writeText(text).catch(function () { fallbackCopy(text); });
  } else {
    fallbackCopy(text);
  }
}
function fallbackCopy(text) {
  var ta = document.createElement('textarea');
  ta.value = text;
  ta.style.cssText = 'position:fixed;left:-9999px;top:-9999px';
  document.body.appendChild(ta);
  ta.select();
  try { document.execCommand('copy'); } catch (e) {}
  document.body.removeChild(ta);
}
function getSubscribers() {
  try { return JSON.parse(localStorage.getItem('bm_subscribers') || '[]'); }
  catch (e) { return []; }
}

function saveSubscribers(list) {
  localStorage.setItem('bm_subscribers', JSON.stringify(list));
}

function initNewsletter() {
  var form = qs('#newsletterForm');
  if (!form) return;
  form.addEventListener('submit', function (ev) {
    ev.preventDefault();
    var input = qs('input[name="email"]', form);
    var note = qs('.newsletter-form__note', form);
    var email = (input.value || '').trim().toLowerCase();
    if (!email || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      if (note) { note.textContent = 'Ingresá un email válido.'; note.style.color = '#c00'; }
      return;
    }
    var subs = getSubscribers();
    var exists = subs.some(function (s) { return s.email === email; });
    if (exists) {
      if (note) { note.textContent = 'Este email ya está suscrito.'; note.style.color = 'var(--bronce)'; }
      form.reset();
      return;
    }
    subs.push({ email: email, date: new Date().toISOString().split('T')[0] });
    saveSubscribers(subs);
    if (note) {
      note.textContent = '✔ Suscripto. Próximamente recibirás novedades de la banda. †';
      note.style.color = '#4a0f0d';
      note.classList.add('form-success');
    }
    form.reset();
  });
}

function initContact() {
  var form = qs('#contactForm');
  if (!form) return;
  form.addEventListener('submit', function (ev) {
    ev.preventDefault();
    var note = qs('.form-success', form) || qs('.newsletter-form__note');
    if (note) {
      note.textContent = '✔ Recibido. La banda confirmará su respuesta a la brevedad. †';
      note.classList.add('form-success');
    }
    form.reset();
  });
}

/* ============================================================
   [10] Share buttons — copy URL to clipboard
   ============================================================ */
function initShareButtons() {
  document.querySelectorAll('[data-share-url]').forEach(function (btn) {
    btn.addEventListener('click', function () {
      var url = btn.getAttribute('data-share-url');
      var title = btn.getAttribute('data-share-title') || 'Buena Muerte';
      if (navigator.share) {
        navigator.share({ title: title, url: url }).catch(function () {});
      } else if (navigator.clipboard) {
        navigator.clipboard.writeText(url).then(function () {
          var label = btn.querySelector('[data-i18n="video_share"]');
          var original = label ? label.textContent : '';
          if (label) label.textContent = '¡Link copiado!';
          btn.classList.add('is-copied');
          setTimeout(function () {
            if (label) label.textContent = original;
            btn.classList.remove('is-copied');
          }, 2000);
        });
      }
    });
  });
}

/* ============================================================
   Inicialización global
   ============================================================ */
// Video shuffle — reordena los 9 videos cada 15s
function initVideoShuffle() {
  var container = document.getElementById('videoGrid');
  if (!container) return;
  var slides = Array.prototype.slice.call(container.querySelectorAll('.video-slide'));

  function shuffle() {
    for (var i = slides.length - 1; i > 0; i--) {
      var j = Math.floor(Math.random() * (i + 1));
      var temp = slides[i];
      slides[i] = slides[j];
      slides[j] = temp;
    }
    slides.forEach(function (slide) { container.appendChild(slide); });
  }

  setInterval(shuffle, 15000);
}

// Video modal
function initVideoModal() {
  var modal = document.getElementById('videoModal');
  var player = document.getElementById('modalPlayer');
  if (!modal || !player) return;

  function openModal(videoId) {
    player.innerHTML = '<iframe src="https://www.youtube.com/embed/' + videoId + '?autoplay=1" allow="autoplay; encrypted-media" allowfullscreen></iframe>';
    modal.classList.add('is-open');
    modal.setAttribute('aria-hidden', 'false');
    document.body.style.overflow = 'hidden';
  }

  function closeModal() {
    player.innerHTML = '';
    modal.classList.remove('is-open');
    modal.setAttribute('aria-hidden', 'true');
    document.body.style.overflow = '';
  }

  document.querySelectorAll('[data-video]').forEach(function (el) {
    el.addEventListener('click', function () { openModal(el.dataset.video); });
    el.addEventListener('keydown', function (e) { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); openModal(el.dataset.video); } });
  });

  modal.querySelectorAll('[data-close-modal]').forEach(function (el) {
    el.addEventListener('click', closeModal);
  });

  document.addEventListener('keydown', function (e) { if (e.key === 'Escape' && modal.classList.contains('is-open')) closeModal(); });
}

/* ============================================================
   [09] Fog — niebla borravino sutil cubriendo ~35% del sitio
   ============================================================ */
function initFog() {
  var canvas = document.getElementById('sparkles');
  if (!canvas) return;
  var ctx = canvas.getContext('2d');
  var patches = [];
  var MAX = window.innerWidth <= 880 ? 3 : 6;

  function resize() {
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
    MAX = window.innerWidth <= 880 ? 3 : 6;
  }
  resize();
  window.addEventListener('resize', resize);

  function createPatch() {
    return {
      x: Math.random() * canvas.width,
      y: Math.random() * canvas.height,
      radius: Math.random() * 300 + 150,
      alpha: 0,
      targetAlpha: Math.random() * 0.4 + 0.3,
      alphaSpeed: Math.random() * 0.003 + 0.001,
      life: 0,
      maxLife: Math.random() * 300 + 150,
      driftX: (Math.random() - 0.5) * 1.2,
      driftY: (Math.random() - 0.5) * 0.6
    };
  }

  for (var i = 0; i < MAX; i++) {
    var p = createPatch();
    p.life = Math.random() * p.maxLife;
    patches.push(p);
  }

  function draw() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    for (var i = 0; i < patches.length; i++) {
      var p = patches[i];
      p.life++;
      p.x += p.driftX;
      p.y += p.driftY;
      if (p.life > p.maxLife) {
        patches[i] = createPatch();
        continue;
      }
      var progress = p.life / p.maxLife;
      var fade = progress < 0.2 ? progress / 0.2 : progress > 0.8 ? (1 - progress) / 0.2 : 1;
      p.alpha = fade * p.targetAlpha;
      var grad = ctx.createRadialGradient(p.x, p.y, 0, p.x, p.y, p.radius);
      grad.addColorStop(0, 'rgba(100,15,25,' + p.alpha + ')');
      grad.addColorStop(0.5, 'rgba(80,10,20,' + (p.alpha * 0.5) + ')');
      grad.addColorStop(1, 'rgba(60,5,15,0)');
      ctx.fillStyle = grad;
      ctx.fillRect(p.x - p.radius, p.y - p.radius, p.radius * 2, p.radius * 2);
    }
    requestAnimationFrame(draw);
  }
  draw();
}

/* ============================================================
   [10] Nav scroll infinito mobile + touch + mouse drag
   ============================================================ */
function initNavScroll() {
  var track = document.querySelector('.nav-track');
  if (!track) return;
  if (window.innerWidth > 880) return;

  var html = track.innerHTML;
  track.innerHTML = html + html;

  var pos = 0;
  var speed = 0.4;
  var paused = false;
  var dragStart = 0;
  var dragPos = 0;
  var dragging = false;
  var resumeTimer = null;

  // Animación continua con JS
  function autoScroll() {
    if (!paused) {
      pos -= speed;
      var half = track.scrollWidth / 2;
      if (Math.abs(pos) >= half) pos = 0;
      track.style.transform = 'translateX(' + pos + 'px)';
    }
    requestAnimationFrame(autoScroll);
  }
  requestAnimationFrame(autoScroll);

  // Touch
  track.addEventListener('touchstart', function (e) {
    paused = true;
    dragging = true;
    dragStart = e.touches[0].pageX;
    dragPos = pos;
    clearTimeout(resumeTimer);
  }, { passive: true });

  track.addEventListener('touchmove', function (e) {
    if (!dragging) return;
    var x = e.touches[0].pageX;
    pos = dragPos + (x - dragStart);
    track.style.transform = 'translateX(' + pos + 'px)';
  }, { passive: true });

  track.addEventListener('touchend', function () {
    dragging = false;
    resumeTimer = setTimeout(function () { paused = false; }, 3000);
  });

  // Mouse drag (desktop)
  track.addEventListener('mousedown', function (e) {
    paused = true;
    dragging = true;
    dragStart = e.pageX;
    dragPos = pos;
    e.preventDefault();
    clearTimeout(resumeTimer);
  });

  document.addEventListener('mousemove', function (e) {
    if (!dragging) return;
    pos = dragPos + (e.pageX - dragStart);
    track.style.transform = 'translateX(' + pos + 'px)';
  });

  document.addEventListener('mouseup', function () {
    if (!dragging) return;
    dragging = false;
    resumeTimer = setTimeout(function () { paused = false; }, 3000);
  });
}

/* ============================================================
   [11] Mini Player — playlist Catalepsia, 10s preview,
        spectrum analyzer borravino+blanco
   ============================================================ */
function initMiniPlayer() {
  var tracks = [
    { name: 'Catalepsia I', src: 'assets/audio/catalepsia-01.mp3' },
    { name: 'Catalepsia II', src: 'assets/audio/catalepsia-02.mp3' },
    { name: 'Catalepsia III', src: 'assets/audio/catalepsia-03.mp3' },
    { name: 'Catalepsia IV', src: 'assets/audio/catalepsia-04.mp3' },
    { name: 'Catalepsia V', src: 'assets/audio/catalepsia-05.mp3' },
    { name: 'Catalepsia VI', src: 'assets/audio/catalepsia-06.mp3' },
    { name: 'Catalepsia VII', src: 'assets/audio/catalepsia-07.mp3' },
    { name: 'Catalepsia VIII', src: 'assets/audio/catalepsia-08.mp3' },
    { name: 'Catalepsia IX', src: 'assets/audio/catalepsia-09.mp3' },
    { name: 'Catalepsia X', src: 'assets/audio/catalepsia-10.mp3' }
  ];
  var cur = 0, playing = false, muted = false;
  var audio, actx, analyser, srcNode;
  var cvs, cx, animId;

  var el = document.createElement('div');
  el.className = 'mini-player';
  el.innerHTML =
    '<div class="mini-player__info">' +
      '<span class="mini-player__track">' + tracks[0].name + '</span>' +
      '<span class="mini-player__time">0:00</span>' +
    '</div>' +
    '<canvas class="mini-player__spectrum" width="204" height="50"></canvas>' +
    '<div class="mini-player__controls">' +
      '<button class="mini-player__btn mp-play" title="Play">▶</button>' +
      '<button class="mini-player__btn mp-stop" title="Stop">■</button>' +
      '<button class="mini-player__btn mp-mute" title="Silenciar">🔊</button>' +
    '</div>';
  document.body.appendChild(el);

  cvs = el.querySelector('.mini-player__spectrum');
  cx = cvs.getContext('2d');
  var nameEl = el.querySelector('.mini-player__track');
  var timeEl = el.querySelector('.mini-player__time');
  var playBtn = el.querySelector('.mp-play');
  var stopBtn = el.querySelector('.mp-stop');
  var muteBtn = el.querySelector('.mp-mute');

  function setup() {
    if (audio) return;
    audio = new Audio();
    audio.volume = 0.25;
    audio.crossOrigin = 'anonymous';
    actx = new (window.AudioContext || window.webkitAudioContext)();
    analyser = actx.createAnalyser();
    analyser.fftSize = 128;
    srcNode = actx.createMediaElementSource(audio);
    srcNode.connect(analyser);
    analyser.connect(actx.destination);
    audio.addEventListener('timeupdate', tick);
    audio.addEventListener('ended', next);
    audio.addEventListener('error', next);
  }

  function load(i) {
    cur = i % tracks.length;
    audio.src = tracks[cur].src;
    nameEl.textContent = tracks[cur].name;
    timeEl.textContent = '0:00';
  }

  function tick() {
    if (audio.currentTime >= 10) { next(); return; }
    var s = Math.floor(audio.currentTime);
    timeEl.textContent = '0:' + (s < 10 ? '0' : '') + s;
  }

  function next() {
    load(cur + 1);
    if (playing) audio.play();
  }

  function draw() {
    animId = requestAnimationFrame(draw);
    var buf = new Uint8Array(analyser.frequencyBinCount);
    analyser.getByteFrequencyData(buf);
    cx.clearRect(0, 0, cvs.width, cvs.height);
    var w = cvs.width / buf.length;
    for (var i = 0; i < buf.length; i++) {
      var h = (buf[i] / 255) * cvs.height;
      var x = i * w;
      var g = cx.createLinearGradient(0, cvs.height, 0, cvs.height - h);
      g.addColorStop(0, 'rgba(74,15,13,.2)');
      g.addColorStop(0.6, 'rgba(74,15,13,.7)');
      g.addColorStop(1, 'rgba(200,204,208,.9)');
      cx.fillStyle = g;
      cx.fillRect(x, cvs.height - h, w - 1, h);
    }
  }

  playBtn.onclick = function () {
    setup();
    if (actx.state === 'suspended') actx.resume();
    if (playing) {
      audio.pause();
      playBtn.textContent = '▶';
      cancelAnimationFrame(animId);
    } else {
      if (!audio.src) load(cur);
      audio.play();
      playBtn.textContent = '❚❚';
      draw();
    }
    playing = !playing;
  };

  stopBtn.onclick = function () {
    if (!audio) return;
    audio.pause();
    audio.currentTime = 0;
    playing = false;
    playBtn.textContent = '▶';
    cancelAnimationFrame(animId);
    cx.clearRect(0, 0, cvs.width, cvs.height);
    timeEl.textContent = '0:00';
  };

  muteBtn.onclick = function () {
    if (!audio) return;
    muted = !muted;
    audio.muted = muted;
    muteBtn.textContent = muted ? '🔇' : '🔊';
  };
}

document.addEventListener('DOMContentLoaded', function () {
  initNav();
  initActiveLink();
  initSmoothScroll();
  renderFechas();
  initSpotifyLazy();
  initNewsletter();
  initContact();
  initVideoShuffle();
  initVideoModal();
  initFog();
  initShareButtons();
  initNavScroll();
  initMiniPlayer();

  // Visit counter
  var counterEl = document.getElementById('visitCounter');
  if (counterEl) {
    fetch('visits.json?t=' + Date.now())
      .then(function (r) { return r.json(); })
      .then(function (data) {
        counterEl.textContent = data.visits;
        localStorage.setItem('bm_visits', data.visits);
      })
      .catch(function () {
        var count = parseInt(localStorage.getItem('bm_visits') || '1', 10);
        counterEl.textContent = count;
      });
  }
});