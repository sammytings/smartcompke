/* SmartComputersKE admin dashboard — sidebar, profile menu, alerts.
   Kept dependency-free on purpose; this is a small enough surface area
   that pulling in a framework isn't worth it. */

document.addEventListener('DOMContentLoaded', function () {

  var wrapper = document.getElementById('dashboardWrapper');
  var toggleBtn = document.getElementById('sidebarToggle');
  var overlay = document.getElementById('sidebarOverlay');

  var MOBILE_BREAKPOINT = 992;
  var isMobile = function () { return window.innerWidth <= MOBILE_BREAKPOINT; };

  // Restore the desktop collapsed preference (nobody wants to re-collapse
  // the sidebar on every page load).
  if (!isMobile() && localStorage.getItem('sidebarCollapsed') === '1') {
    wrapper.classList.add('sidebar-collapsed');
  }

  function openMobileDrawer() {
    wrapper.classList.add('sidebar-open');
    overlay.classList.add('open');
    document.body.style.overflow = 'hidden';
  }

  function closeMobileDrawer() {
    wrapper.classList.remove('sidebar-open');
    overlay.classList.remove('open');
    document.body.style.overflow = '';
  }

  toggleBtn.addEventListener('click', function () {
    if (isMobile()) {
      wrapper.classList.contains('sidebar-open') ? closeMobileDrawer() : openMobileDrawer();
    } else {
      wrapper.classList.toggle('sidebar-collapsed');
      localStorage.setItem('sidebarCollapsed', wrapper.classList.contains('sidebar-collapsed') ? '1' : '0');
    }
  });

  overlay.addEventListener('click', closeMobileDrawer);

  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') closeMobileDrawer();
  });

  // Jumping between mobile and desktop widths (rotating a tablet, resizing
  // a browser window) shouldn't leave the UI in a half-open state.
  var resizeTimer;
  window.addEventListener('resize', function () {
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(function () {
      if (!isMobile()) {
        closeMobileDrawer();
      } else {
        wrapper.classList.remove('sidebar-collapsed');
      }
    }, 120);
  });

  // ---- Profile dropdown -------------------------------------------------
  // Deliberately simple: a click toggles a class, outside clicks close it.
  var profileMenu = document.querySelector('.profile-menu');
  if (profileMenu) {
    profileMenu.addEventListener('click', function (e) {
      e.stopPropagation();
      profileMenu.classList.toggle('open');
    });
    document.addEventListener('click', function () {
      profileMenu.classList.remove('open');
    });
  }

  // ---- Alert dismiss ------------------------------------------------------
  document.querySelectorAll('.alert-close').forEach(function (btn) {
    btn.addEventListener('click', function () {
      var alert = btn.closest('.alert');
      alert.style.opacity = '0';
      alert.style.transform = 'translateY(-4px)';
      setTimeout(function () { alert.remove(); }, 180);
    });
  });

  // Auto-dismiss success/info messages after a few seconds; leave
  // warnings/errors up until the user closes them themselves.
  document.querySelectorAll('.alert.success, .alert.info').forEach(function (alert) {
    setTimeout(function () {
      var btn = alert.querySelector('.alert-close');
      if (btn) btn.click();
    }, 5000);
  });

});