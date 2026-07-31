/* =====================================================================
   SMARTCOMPUTERSKE — SITE SCRIPT
   ===================================================================== */
document.addEventListener('DOMContentLoaded', function () {

  /* ---------- Cart drawer ---------- */
  const cartOpenBtn = document.getElementById('cartOpenBtn');
  const navCartBtn = document.getElementById('navCartBtn');
  const cartCloseBtn = document.getElementById('cartCloseBtn');
  const cartDrawer = document.getElementById('cartDrawer');
  const cartOverlay = document.getElementById('cartOverlay');
  function openCart () { cartDrawer && cartDrawer.classList.add('open'); cartOverlay && cartOverlay.classList.add('open'); }
  function closeCart () { cartDrawer && cartDrawer.classList.remove('open'); cartOverlay && cartOverlay.classList.remove('open'); }
  cartOpenBtn && cartOpenBtn.addEventListener('click', openCart);
  navCartBtn && navCartBtn.addEventListener('click', openCart);
  cartCloseBtn && cartCloseBtn.addEventListener('click', closeCart);
  cartOverlay && cartOverlay.addEventListener('click', closeCart);

  /* ---------- Mobile category nav ---------- */
  const menuToggle = document.getElementById('menuToggle');
  const catStrip = document.getElementById('catStrip');
  menuToggle && menuToggle.addEventListener('click', function () {
    catStrip.classList.toggle('collapsed');
    menuToggle.setAttribute('aria-expanded', String(!catStrip.classList.contains('collapsed')));
  });
  // Tap-to-open mega menus on touch/mobile
  document.querySelectorAll('.cat-item > .cat-trigger').forEach(function (trigger) {
    trigger.addEventListener('click', function (e) {
      if (window.innerWidth > 820) return;
      e.preventDefault();
      trigger.closest('.cat-item').classList.toggle('open');
    });
  });

  /* ---------- Toast ---------- */
  const toast = document.getElementById('toast');
  window.showToast = function (msg) {
    if (!toast) return;
    if (msg) toast.lastChild.textContent = ' ' + msg;
    toast.classList.add('show');
    clearTimeout(window._toastTimer);
    window._toastTimer = setTimeout(function () { toast.classList.remove('show'); }, 1800);
  };
  document.querySelectorAll('.btn-cart-add').forEach(function (btn) {
    btn.addEventListener('click', function () { window.showToast('Added to cart'); });
  });

  /* ---------- Wishlist toggle ---------- */
  document.querySelectorAll('.wish-toggle, .wish-btn-lg').forEach(function (btn) {
    btn.addEventListener('click', function (e) {
      e.stopPropagation();
      btn.classList.toggle('active');
      window.showToast(btn.classList.contains('active') ? 'Added to wishlist' : 'Removed from wishlist');
    });
  });

  /* ---------- Hero image slider ---------- */
  (function () {
    const slides = document.querySelectorAll('#heroSlider .hero-slide');
    const dots = document.querySelectorAll('#heroDots button');
    if (!slides.length) return;
    let current = 0, timer;
    function goTo (i) {
      slides[current].classList.remove('active');
      dots[current] && dots[current].classList.remove('active');
      current = i;
      slides[current].classList.add('active');
      dots[current] && dots[current].classList.add('active');
    }
    function next () { goTo((current + 1) % slides.length); }
    function startAuto () { timer = setInterval(next, 4200); }
    function stopAuto () { clearInterval(timer); }
    dots.forEach(function (dot, i) {
      dot.addEventListener('click', function () { stopAuto(); goTo(i); startAuto(); });
    });
    if (slides.length > 1) startAuto();
  })();

  /* ---------- VAT toggle ----------
     Prices are marked up as:
     <span class="vat-price" data-base="12345">KSh 12,345</span>
     data-base is always the VAT-EXCLUSIVE price in KES.
     Toggle switches the *display* between inclusive / exclusive. */
  const VAT_RATE = 0.16;
  const vatSwitch = document.getElementById('vatSwitch');
  const vatLabel = document.getElementById('vatLabel');

  function formatKES (n) {
    return 'KSh ' + Math.round(n).toLocaleString('en-KE');
  }
  function applyVatDisplay (inclusive) {
    document.querySelectorAll('.vat-price').forEach(function (el) {
      const base = parseFloat(el.getAttribute('data-base'));
      if (isNaN(base)) return;
      el.textContent = formatKES(inclusive ? base * (1 + VAT_RATE) : base);
    });
    document.querySelectorAll('.vat-note').forEach(function (el) {
      el.textContent = inclusive ? 'Price includes 16% VAT' : 'Price excludes 16% VAT';
    });
    localStorage.setItem('sck_vat_inclusive', inclusive ? '1' : '0');
  }
  if (vatSwitch) {
    let inclusive = localStorage.getItem('sck_vat_inclusive') !== '0';
    function render () {
      vatSwitch.classList.toggle('on', inclusive);
      vatLabel.textContent = inclusive ? 'Prices incl. VAT' : 'Prices excl. VAT';
      applyVatDisplay(inclusive);
    }
    vatSwitch.addEventListener('click', function () { inclusive = !inclusive; render(); });
    render();
  }

  /* ---------- Delivery fee calculator ---------- */
  const DELIVERY_DATA = {
    'Nairobi': {
      towns: {
        'Nairobi CBD': { areas: ['CBD Core', 'Upper Hill', 'Community'], fee: 0, eta: 'Same day' },
        'Westlands': { areas: ['Westlands', 'Parklands', 'Sarit'], fee: 200, eta: 'Same day' },
        'Kasarani': { areas: ['Kasarani', 'Roysambu', 'Mwiki'], fee: 300, eta: 'Same day' },
        'Embakasi': { areas: ['Embakasi', 'Pipeline', 'Utawala'], fee: 350, eta: 'Same day' }
      }
    },
    'Kiambu': {
      towns: {
        'Thika': { areas: ['Thika Town', 'Makongeni'], fee: 600, eta: '1 business day' },
        'Ruiru': { areas: ['Ruiru Town', 'Kimbo'], fee: 450, eta: '1 business day' }
      }
    },
    'Mombasa': {
      towns: {
        'Mombasa Island': { areas: ['Old Town', 'Nyali'], fee: 900, eta: '2 business days' },
        'Likoni': { areas: ['Likoni'], fee: 950, eta: '2 business days' }
      }
    },
    'Kisumu': {
      towns: {
        'Kisumu Central': { areas: ['Milimani', 'Kondele'], fee: 900, eta: '2 business days' }
      }
    },
    'Nakuru': {
      towns: {
        'Nakuru Town': { areas: ['Section 58', 'Milimani'], fee: 750, eta: '2 business days' }
      }
    }
  };

  const countySel = document.getElementById('deliveryCounty');
  const townSel = document.getElementById('deliveryTown');
  const areaSel = document.getElementById('deliveryArea');
  const deliveryResult = document.getElementById('deliveryResult');

  if (countySel) {
    Object.keys(DELIVERY_DATA).forEach(function (county) {
      const opt = document.createElement('option');
      opt.value = county; opt.textContent = county;
      countySel.appendChild(opt);
    });

    function resetSelect (sel, placeholder) {
      sel.innerHTML = '<option value="">' + placeholder + '</option>';
      sel.disabled = true;
    }

    countySel.addEventListener('change', function () {
      resetSelect(townSel, 'Select town');
      resetSelect(areaSel, 'Select area');
      deliveryResult.classList.remove('show');
      const county = DELIVERY_DATA[countySel.value];
      if (!county) return;
      townSel.disabled = false;
      Object.keys(county.towns).forEach(function (town) {
        const opt = document.createElement('option');
        opt.value = town; opt.textContent = town;
        townSel.appendChild(opt);
      });
    });

    townSel.addEventListener('change', function () {
      resetSelect(areaSel, 'Select area');
      deliveryResult.classList.remove('show');
      const county = DELIVERY_DATA[countySel.value];
      const town = county && county.towns[townSel.value];
      if (!town) return;
      areaSel.disabled = false;
      town.areas.forEach(function (area) {
        const opt = document.createElement('option');
        opt.value = area; opt.textContent = area;
        areaSel.appendChild(opt);
      });
    });

    areaSel.addEventListener('change', function () {
      const county = DELIVERY_DATA[countySel.value];
      const town = county && county.towns[townSel.value];
      if (!town || !areaSel.value) { deliveryResult.classList.remove('show'); return; }
      deliveryResult.querySelector('.fee').textContent = town.fee === 0 ? 'Free' : formatKES(town.fee);
      deliveryResult.querySelector('.eta').textContent = town.eta;
      deliveryResult.classList.add('show');
    });
  }

  /* ---------- Filters sidebar (shop page) ---------- */
  document.querySelectorAll('.filter-toggle').forEach(function (btn) {
    btn.addEventListener('click', function () {
      btn.closest('.filter-group').classList.toggle('collapsed');
    });
  });
  const filterToggleMobile = document.getElementById('filterToggleMobile');
  const filtersSidebar = document.getElementById('filtersSidebar');
  filterToggleMobile && filterToggleMobile.addEventListener('click', function () {
    filtersSidebar.classList.toggle('open');
  });
  document.querySelectorAll('.color-swatch').forEach(function (sw) {
    sw.addEventListener('click', function () { sw.classList.toggle('selected'); });
  });

  /* ---------- Product gallery (product detail page) ---------- */
  const galleryMainImg = document.querySelector('#galleryMain img');
  document.querySelectorAll('.gallery-thumb').forEach(function (thumb) {
    thumb.addEventListener('click', function () {
      document.querySelectorAll('.gallery-thumb').forEach(function (t) { t.classList.remove('active'); });
      thumb.classList.add('active');
      if (galleryMainImg) galleryMainImg.src = thumb.querySelector('img').src;
    });
  });

  /* ---------- Tabs (product detail page) ---------- */
  document.querySelectorAll('.tab-btn').forEach(function (btn) {
    btn.addEventListener('click', function () {
      const target = btn.getAttribute('data-tab');
      document.querySelectorAll('.tab-btn').forEach(function (b) { b.classList.remove('active'); });
      document.querySelectorAll('.tab-panel').forEach(function (p) { p.classList.remove('active'); });
      btn.classList.add('active');
      document.getElementById(target).classList.add('active');
    });
  });

  /* ---------- Quantity stepper ---------- */
  document.querySelectorAll('.qty-stepper').forEach(function (stepper) {
    const input = stepper.querySelector('input');
    stepper.querySelector('.qty-minus').addEventListener('click', function () {
      input.value = Math.max(1, parseInt(input.value || '1', 10) - 1);
    });
    stepper.querySelector('.qty-plus').addEventListener('click', function () {
      input.value = parseInt(input.value || '1', 10) + 1;
    });
  });

  /* ---------- Search autocomplete ---------- */
  const searchInput = document.getElementById('siteSearchInput');
  const searchPanel = document.getElementById('searchPanel');
  if (searchInput && searchPanel) {
    searchInput.addEventListener('focus', function () { searchPanel.classList.add('open'); });
    document.addEventListener('click', function (e) {
      if (!searchPanel.contains(e.target) && e.target !== searchInput) {
        searchPanel.classList.remove('open');
      }
    });
  }
});
<script>

document.querySelectorAll(".compare-btn").forEach(button=>{

button.addEventListener("click",function(e){

e.preventDefault();

fetch(this.href)

.then(response=>response.json())

.then(data=>{

document.getElementById("compareCount").innerText=data.count;

if(data.added){

this.style.background="#0d6efd";

this.style.color="white";

}

});

});

});

</script>