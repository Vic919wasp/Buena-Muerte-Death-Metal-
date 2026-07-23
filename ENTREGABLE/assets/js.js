/* ============================================================
   CONTEXTO: JS compartido del sitio multi-page de Buena Muerte.
             Nav mobile toggle, scroll-header shadow, active nav
             link en scroll, smooth-scroll con offset, uptime
             clock opcional, form handlers fake (newsletter/contact),
             carga lazy de Spotify embeds y render de fechas FECHAS[].
   ============================================================
   ÍNDICE DE SECCIONES
   [01] Helpers               - línea 27
   [02] Datos editables       - línea 20
   [03] Nav / toggle mobile   - línea 57
   [04] Active link scroll    - línea 83
   [05] Smooth scroll anchor  - línea 104
   [06] Tour render           - línea 120
   [07] Spotify lazy load     - línea 154
   [08] Newsletter form       - línea 173
   [09] Share buttons         - línea 217
   [10] Fog                   - línea 291
   [11] Nav scroll mobile     - línea 358
   ============================================================ */

/* EDITAR acá para cargar fechas. Vacío = estado cero visible.
   Campos: dia, mes, anio, lugar, ciudad, link (tickets, opcional),
           fotos (array de URLs, opcional), mapa (URL embed Google Maps, opcional),
           transporte (string, opcional), descripcion (string, opcional).
           Si link está vacío, se muestra WhatsApp. */
var WHATSAPP_CANTANTE = '5491164377706';
var FECHAS = [
  {
    dia: '02',
    mes: 'AGO',
    anio: '2026',
    lugar: 'Reventados Bar',
    ciudad: 'Quilmes, GBA',
    link: '#',
    transporte: 'Colectivo 98, Tren Roca',
    fotos: ['assets/posts/post-01.jpg']
  },
  {
    dia: '22',
    mes: 'JUL',
    anio: '2026',
    lugar: 'GIER MUSIC CLUB',
    ciudad: 'CABA',
    mapa: 'https://maps.google.com/maps?q=av.+alvarez+thomas+1078+CABA&output=embed',
    fotos: ['assets/tour/Fecha Brutal death en Gier.jpeg']
  }
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
  var container = qs('#tourTable');
  var head  = qs('#tourHeader');
  if (!empty || !container) { return; }
  if (!FECHAS.length) { return; }
  empty.style.display = 'none';
  container.style.display = 'block';
  if (head) { head.textContent = FECHAS.length + ' fecha' + (FECHAS.length === 1 ? '' : 's') + ' confirmada' + (FECHAS.length === 1 ? '' : 's'); }
  container.innerHTML = FECHAS.map(function (f, i) {
    var cta = '';
    if (f.link && f.link !== '#') {
      cta = '<a href="' + f.link + '" target="_blank" rel="noopener" class="tour-card__btn">ENTRADAS ›</a>';
    } else {
      var waUrl = 'https://wa.me/' + WHATSAPP_CANTANTE + '?text=' + encodeURIComponent('Hola Favio!, quiero entradas para el show de ' + f.lugar + ' ' + f.dia + '/' + f.mes + '/' + f.anio + '!!!');
      cta = '<a href="' + waUrl + '" target="_blank" rel="noopener" class="tour-card__btn tour-card__btn--wa">CONSULTAR POR WHATSAPP ›</a>';
    }
    var fotos = '';
    if (f.fotos && f.fotos.length) {
      fotos = '<div class="tour-card__fotos">' + f.fotos.map(function (url) {
        return '<a href="' + url + '" target="_blank" rel="noopener"><img src="' + url + '" loading="lazy" alt="Promo ' + f.lugar + '"></a>';
      }).join('') + '</div>';
    }
    var mapa = '';
    if (f.mapa) {
      var mapaLink = f.mapa.replace(/&output=embed/, '').replace(/output=embed&?/, '');
      mapa = '<div class="tour-card__mapa">' +
        '<iframe src="' + f.mapa + '" loading="lazy" allowfullscreen title="Ubicación de ' + f.lugar + '"></iframe>' +
        '<a href="' + mapaLink + '" target="_blank" rel="noopener" class="tour-card__mapa-link">Abrir en Google Maps ↗</a>' +
        '</div>';
    }
    var transporte = '';
    if (f.transporte) {
      transporte = '<div class="tour-card__transporte">Cómo llegar: ' + f.transporte + '</div>';
    }
    var shareText = '🎵 *' + f.lugar + '*\n' +
      '📍 ' + (f.ciudad || '') + '\n' +
      '📅 ' + f.dia + '/' + f.mes + '/' + f.anio + '\n' +
      (f.descripcion ? '\n📝 ' + f.descripcion + '\n' : '') +
      (f.transporte ? '\n🚌 ' + f.transporte + '\n' : '') +
      (f.mapa ? '\n🗺️ Ver ubicación: ' + mapaLink + '\n' : '') +
      '\n🎫 Entradas / Info:\nhttps://wa.me/' + WHATSAPP_CANTANTE;
    var shareUrl = 'https://wa.me/' + WHATSAPP_CANTANTE + '?text=' + encodeURIComponent(shareText);
    var share = '<a href="#" class="tour-card__btn tour-card__btn--wa" onclick="shareFecha(event, ' + i + ')">COMPARTIR FECHA ›</a>';
    return '<div class="tour-card">' +
      '<div class="tour-card__fecha"><b>' + f.dia + '</b><br><span>' + (f.mes || '') + ' ' + (f.anio || '') + '</span></div>' +
      '<div class="tour-card__info">' +
        '<div class="tour-card__lugar">' + f.lugar + '<span>' + (f.ciudad || '') + '</span></div>' +
        cta + share + fotos + mapa + transporte +
      '</div>' +
    '</div>';
  }).join('');
}

/* Generar flyer compuesto: foto + barra de texto al pie + mapa */
function generarFlyer(imageUrl, info, mapaUrl) {
  var W = 1080, H = Math.round(W * 1.35);
  var BAR_H = Math.round(H * 0.30);
  var canvas = document.createElement('canvas');
  canvas.width = W; canvas.height = H;
  var ctx = canvas.getContext('2d');
  return new Promise(function (resolve, reject) {
    var img = new Image();
    img.crossOrigin = 'anonymous';
    img.onload = function () {
      var imgR = img.width / img.height, canR = W / H;
      var sx, sy, sw, sh;
      if (imgR > canR) { sh = img.height; sw = sh * canR; sx = (img.width - sw) / 2; sy = 0; }
      else { sw = img.width; sh = sw / canR; sx = 0; sy = (img.height - sh) / 2; }
      ctx.drawImage(img, sx, sy, sw, sh, 0, 0, W, H);
      ctx.fillStyle = 'rgba(0,0,0,0.75)';
      ctx.fillRect(0, H - BAR_H, W, BAR_H);
      ctx.fillStyle = '#fff';
      ctx.textAlign = 'center';
      var y = H - BAR_H + Math.round(H * 0.035);
      var s1 = Math.round(W * 0.07);
      ctx.font = 'bold ' + s1 + 'px sans-serif';
      ctx.fillText(info.lugar, W / 2, y += s1);
      var s2 = Math.round(W * 0.048);
      ctx.font = s2 + 'px sans-serif';
      ctx.fillText(info.ciudad || '', W / 2, y += s2 * 1.5);
      ctx.font = 'bold ' + s2 + 'px sans-serif';
      ctx.fillText(info.dia + ' ' + info.mes + ' ' + info.anio, W / 2, y += s2 * 1.5);
      if (info.transporte) {
        var s3 = Math.round(W * 0.036);
        ctx.font = s3 + 'px sans-serif';
        ctx.fillStyle = '#bbb';
        ctx.fillText('🚌 ' + info.transporte, W / 2, y += s2 * 1.4);
      }
      if (mapaUrl) {
        var s4 = Math.round(W * 0.032);
        ctx.font = s4 + 'px sans-serif';
        ctx.fillStyle = '#9cf';
        ctx.fillText('🗺️ ' + mapaUrl, W / 2, y += s2 * 1.3);
      }
      ctx.fillStyle = '#ccc';
      var s5 = Math.round(W * 0.032);
      ctx.font = s5 + 'px sans-serif';
      ctx.fillText('🎫 Entradas / Info: wa.me/' + WHATSAPP_CANTANTE, W / 2, y += s2 * 1.4);
      canvas.toBlob(function (blob) {
        if (!blob) { reject(new Error('toBlob failed')); return; }
        resolve(new File([blob], 'flyer-' + info.dia + info.mes + '.jpg', { type: 'image/jpeg' }));
      }, 'image/jpeg', 0.92);
    };
    img.onerror = function () { reject(new Error('image failed')); };
    img.src = imageUrl;
  });
}

/* Compartir fecha: flyer compuesto + mapa */
function shareFecha(e, idx) {
  e.preventDefault();
  var f = FECHAS[idx];
  if (!f) return;
  var imgUrl = (f.fotos && f.fotos.length) ? f.fotos[0] : '';
  var mapaLink = f.mapa ? f.mapa.replace(/&output=embed/, '').replace(/output=embed&?/, '') : '';
  var msgText = '🎵 *' + f.lugar + '*\n📍 ' + (f.ciudad || '') + '\n📅 ' + f.dia + '/' + f.mes + '/' + f.anio +
    (f.descripcion ? '\n📝 ' + f.descripcion : '') +
    (f.transporte ? '\n🚌 ' + f.transporte : '') +
    (mapaLink ? '\n🗺️ Ver ubicación: ' + mapaLink : '') +
    '\n\n🎫 Entradas / Info:\nhttps://wa.me/' + WHATSAPP_CANTANTE;
  var waUrl = 'https://wa.me/' + WHATSAPP_CANTANTE + '?text=' + encodeURIComponent(msgText);

  if (!imgUrl) {
    location.href = waUrl;
    return;
  }

  var info = { lugar: f.lugar, ciudad: f.ciudad, dia: f.dia, mes: f.mes, anio: f.anio, transporte: f.transporte || '' };

  generarFlyer(imgUrl, info, mapaLink).then(function (file) {
    if (navigator.share && navigator.canShare) {
      var data = { files: [file], text: msgText };
      if (navigator.canShare(data)) {
        return navigator.share(data).then(function () {}).catch(function () {});
      }
    }
    var a = document.createElement('a');
    a.href = URL.createObjectURL(file);
    a.download = file.name;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(a.href);
    location.href = waUrl;
  }).catch(function () {
    location.href = waUrl;
  });
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
  var API = 'http://127.0.0.1:5000';
  form.addEventListener('submit', function (ev) {
    ev.preventDefault();
    var input = qs('input[name="email"]', form);
    var note = qs('.newsletter-form__note', form);
    var email = (input.value || '').trim().toLowerCase();
    if (!email || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      if (note) { note.textContent = 'Ingresá un email válido.'; note.style.color = '#c00'; }
      return;
    }
    fetch(API + '/api/subscribe', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email: email })
    }).then(function (r) { return r.json(); }).then(function (data) {
      if (data.ok) {
        if (note) {
          note.textContent = '✔ Suscripto. Próximamente recibirás novedades de la banda. †';
          note.style.color = '#4a0f0d';
          note.classList.add('form-success');
        }
        form.reset();
      } else {
        if (note) { note.textContent = data.error || 'Error al suscribirse.'; note.style.color = '#c00'; }
      }
    }).catch(function () {
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
  });
}

/* ============================================================
   [09] Share buttons — copy URL to clipboard
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
// Video inline play — preload + 1s cruce
var currentVideoPlayer = null;
var currentVideoThumb = null;

function initVideoInline() {
  // Bind click para play inline
  document.querySelectorAll('.video-thumb[data-video]').forEach(function (el) {
    if (el.dataset.bound) return;
    el.dataset.bound = '1';
    el.addEventListener('click', function () {
      var videoId = el.dataset.video;
      var oldPlayer = currentVideoPlayer;
      var oldThumb = currentVideoThumb;
      var player = document.createElement('div');
      player.className = 'video-inline-player';
      player.innerHTML = '<iframe src="https://www.youtube.com/embed/' + videoId + '?autoplay=1&rel=0&enablejsapi=1" allow="autoplay; encrypted-media" allowfullscreen></iframe>';
      el.style.display = 'none';
      el.parentNode.insertBefore(player, el.nextSibling);
      currentVideoPlayer = player;
      currentVideoThumb = el;
      if (oldPlayer) {
        setTimeout(function () {
          oldPlayer.remove();
          if (oldThumb) oldThumb.style.display = '';
        }, 1000);
      }
    });
    el.addEventListener('keydown', function (e) {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        el.click();
      }
    });
  });
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
   [11] Nav scroll infinito mobile + touch + mouse drag
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
      pos += speed;
      var half = track.scrollWidth / 2;
      if (pos >= half) pos = 0;
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

document.addEventListener('DOMContentLoaded', function () {
  initNav();
  initActiveLink();
  initSmoothScroll();
  renderFechas();
  initSpotifyLazy();
  initNewsletter();
  initVideoInline();
  initFog();
  initShareButtons();
  initNavScroll();

  // Visit counter
  var counterEl = document.getElementById('visitCounter');
  if (counterEl) {
    var API = 'http://127.0.0.1:5000';
    fetch(API + '/api/visit', { method: 'POST' })
      .then(function (r) { return r.json(); })
      .then(function (data) {
        counterEl.textContent = data.visits;
        localStorage.setItem('bm_visits', data.visits);
      })
      .catch(function () {
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
      });
  }
});