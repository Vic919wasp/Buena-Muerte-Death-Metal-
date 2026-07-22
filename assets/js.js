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
           '<td class="btt"><a href="' + (f.link || '#') + '" target="_blank" rel="noopener">TICKETS ›</a></td></tr>';
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
   [08] Newsletter / Contact (handlers fake sin backend)
   ============================================================ */
function initForms() {
  qsa('form[data-fake]').forEach(function (form) {
    form.addEventListener('submit', function (ev) {
      ev.preventDefault();
      var note = qs('.form-success', form) || qs('.newsletter-form__note');
      if (note) {
        note.textContent = '✔ Recibido. La banda confirmará su respuesta a la brevedad. †';
        note.classList.add('form-success');
      }
      form.reset();
    });
  });
}

/* ============================================================
   Inicialización global
   ============================================================ */
// Carousel + auto-play random
function initCarousels() {
  document.querySelectorAll('[data-carousel]').forEach(function (carousel) {
    var track = carousel.querySelector('.carousel__track');
    var slides = carousel.querySelectorAll('.carousel__slide');
    var current = 0;
    var timer = null;
    var paused = false;

    function getSlideLeft(index) {
      return slides[index].offsetLeft - parseInt(getComputedStyle(track).paddingLeft);
    }

    function showSlide(index) {
      current = (index + slides.length) % slides.length;
      track.scrollTo({ left: getSlideLeft(current), behavior: 'smooth' });
    }

    function randomDelay() {
      return 3000 + Math.random() * 5000;
    }

    function startAuto() {
      stopAuto();
      if (!paused) {
        timer = setTimeout(function () {
          showSlide(current + 1);
          startAuto();
        }, randomDelay());
      }
    }

    function stopAuto() {
      if (timer) { clearTimeout(timer); timer = null; }
    }

    // Botones manuales
    carousel.querySelector('.carousel__btn--prev').addEventListener('click', function () {
      showSlide(current - 1);
      startAuto();
    });
    carousel.querySelector('.carousel__btn--next').addEventListener('click', function () {
      showSlide(current + 1);
      startAuto();
    });

    // Teclado
    carousel.addEventListener('keydown', function (e) {
      if (e.key === 'ArrowLeft') { showSlide(current - 1); startAuto(); }
      if (e.key === 'ArrowRight') { showSlide(current + 1); startAuto(); }
    });

    // Hover pausa
    carousel.addEventListener('mouseenter', function () { paused = true; stopAuto(); });
    carousel.addEventListener('mouseleave', function () { paused = false; startAuto(); });

    // Iniciar
    startAuto();
  });
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
  var MAX = 6;

  function resize() {
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
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

document.addEventListener('DOMContentLoaded', function () {
  initNav();
  initActiveLink();
  initSmoothScroll();
  renderFechas();
  initSpotifyLazy();
  initForms();
  initCarousels();
  initVideoModal();
  initFog();

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