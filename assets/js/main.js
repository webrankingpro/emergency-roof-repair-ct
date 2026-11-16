/* Progressive-enhancement layer: mobile menu, click-driven dropdowns, temporary form.
   Dropdowns are disclosure buttons (aria-expanded + aria-controls), never hover-only. */
(() => {
  const root = document.documentElement;
  root.classList.remove('no-js');
  root.classList.add('js');

  const menuButton = document.querySelector('.nav-toggle');
  const nav = document.querySelector('#primary-nav');
  const DESKTOP = '(min-width: 1101px) and (min-height: 561px)';
  const NAV_DESKTOP = '(min-width: 1101px)';
  let closeAll = () => false;

  if (nav) {
    const groups = Array.from(nav.querySelectorAll('.nav-group'));
    const panelOf = (btn) => document.getElementById(btn.getAttribute('aria-controls'));
    const isOpen = (btn) => btn.getAttribute('aria-expanded') === 'true';
    const setOpen = (btn, open) => {
      const panel = panelOf(btn);
      btn.setAttribute('aria-expanded', String(open));
      if (panel) panel.hidden = !open;
    };

    /* Keep the panel (and its flyout) inside the viewport. */
    const placePanel = (group) => {
      const panel = group.querySelector(':scope > .dropdown-panel');
      if (!panel || panel.hidden) return;
      panel.style.left = '';
      panel.classList.remove('flyout-left');
      if (!window.matchMedia(NAV_DESKTOP).matches) return;
      const r = panel.getBoundingClientRect();
      const overflow = r.right - (window.innerWidth - 12);
      if (overflow > 0) panel.style.left = `${-overflow}px`;
    };
    const placeFlyout = (townBtn) => {
      const panel = townBtn.closest('.dropdown-panel');
      const sub = panelOf(townBtn);
      if (!panel || !sub) return;
      panel.classList.remove('flyout-left');
      if (!window.matchMedia(DESKTOP).matches) return;
      const need = sub.offsetWidth + 16;
      if (panel.getBoundingClientRect().right + need > window.innerWidth) panel.classList.add('flyout-left');
    };

    const closeTowns = (scope, except) => {
      scope.querySelectorAll('.town-trigger').forEach((b) => {
        if (b !== except && isOpen(b)) setOpen(b, false);
      });
    };
    const closeGroup = (group) => {
      const trigger = group.querySelector(':scope > .nav-trigger');
      if (!trigger || !isOpen(trigger)) return false;
      closeTowns(group);
      setOpen(trigger, false);
      const panel = panelOf(trigger);
      if (panel) { panel.style.left = ''; panel.classList.remove('flyout-left'); }
      return true;
    };
    closeAll = (except) => {
      let closed = false;
      groups.forEach((g) => { if (g !== except && closeGroup(g)) closed = true; });
      return closed;
    };
    const visibleItems = (panel) => Array.from(panel.querySelectorAll('a[href], button'))
      .filter((el) => !el.closest('[hidden]') && el.offsetParent !== null);

    groups.forEach((group) => {
      const trigger = group.querySelector(':scope > .nav-trigger');
      if (!trigger) return;
      setOpen(trigger, false);
      trigger.addEventListener('click', () => {
        const open = !isOpen(trigger);
        closeAll(open ? group : null);
        if (!open) closeTowns(group);
        setOpen(trigger, open);
        if (open) placePanel(group);
      });
      group.querySelectorAll('.town-trigger').forEach((town) => {
        setOpen(town, false);
        town.addEventListener('click', () => {
          const open = !isOpen(town);
          closeTowns(group, open ? town : null);
          setOpen(town, open);
          if (open) placeFlyout(town);
        });
      });
      /* Tabbing out of an open dropdown closes it. */
      group.addEventListener('focusout', (event) => {
        /* Only for the floating desktop panels: in the stacked mobile menu, collapsing on blur
           would shift the layout under a tap. */
        if (!window.matchMedia(NAV_DESKTOP).matches) return;
        if (event.relatedTarget && !group.contains(event.relatedTarget)) closeGroup(group);
      });
    });

    /* Outside click / tap closes every dropdown. */
    document.addEventListener('click', (event) => {
      if (!event.target.closest('.nav-group')) closeAll();
    });

    /* Choosing a navigation link closes dropdowns (and the mobile menu). */
    nav.addEventListener('click', (event) => {
      if (event.target.closest('a')) {
        closeAll();
        setMenu(false);
      }
    });

    /* Keyboard: Escape, arrows. */
    nav.addEventListener('keydown', (event) => {
      const group = event.target.closest('.nav-group');
      if (!group) return;
      const trigger = group.querySelector(':scope > .nav-trigger');
      const panel = panelOf(trigger);
      const key = event.key;
      if (key === 'ArrowDown' && event.target === trigger) {
        event.preventDefault();
        if (!isOpen(trigger)) { closeAll(group); setOpen(trigger, true); placePanel(group); }
        const first = visibleItems(panel)[0];
        if (first) first.focus();
        return;
      }
      if (!panel || panel.hidden || !panel.contains(event.target)) return;
      if (key === 'ArrowDown' || key === 'ArrowUp') {
        event.preventDefault();
        const items = visibleItems(panel);
        const i = items.indexOf(event.target);
        const next = key === 'ArrowDown' ? items[(i + 1) % items.length] : items[(i - 1 + items.length) % items.length];
        if (next) next.focus();
      } else if (key === 'ArrowRight' && event.target.classList.contains('town-trigger')) {
        event.preventDefault();
        closeTowns(group, event.target);
        setOpen(event.target, true);
        placeFlyout(event.target);
        const link = visibleItems(panelOf(event.target))[0];
        if (link) link.focus();
      } else if (key === 'ArrowLeft' && event.target.closest('.town-submenu')) {
        event.preventDefault();
        const owner = group.querySelector(`.town-trigger[aria-controls="${event.target.closest('.town-submenu').id}"]`);
        if (owner) { setOpen(owner, false); owner.focus(); }
      }
    });

    window.addEventListener('resize', () => {
      groups.forEach(placePanel);
    }, { passive: true });
  }

  const setMenu = (open) => {
    if (!menuButton || !nav) return;
    menuButton.setAttribute('aria-expanded', String(open));
    menuButton.setAttribute('aria-label', open ? 'Close navigation' : 'Open navigation');
    nav.classList.toggle('is-open', open);
    document.body.classList.toggle('nav-open', open);
    if (!open) closeAll();
  };

  if (menuButton && nav) {
    menuButton.addEventListener('click', () => setMenu(menuButton.getAttribute('aria-expanded') !== 'true'));
    document.addEventListener('keydown', (event) => {
      if (event.key !== 'Escape') return;
      const openTrigger = nav.querySelector('.nav-trigger[aria-expanded="true"]');
      if (openTrigger) {
        /* Escape closes the open dropdown and returns focus to its button. */
        closeAll();
        openTrigger.focus();
        return;
      }
      if (menuButton.getAttribute('aria-expanded') === 'true') {
        setMenu(false);
        menuButton.focus();
      }
    });
    window.addEventListener('resize', () => {
      if (window.matchMedia(NAV_DESKTOP).matches) setMenu(false);
    }, { passive: true });
  } else if (nav) {
    document.addEventListener('keydown', (event) => {
      if (event.key !== 'Escape') return;
      const openTrigger = nav.querySelector('.nav-trigger[aria-expanded="true"]');
      if (openTrigger) {
        closeAll();
        openTrigger.focus();
      }
    });
  }

  document.querySelectorAll('[data-temp-form]').forEach((form) => {
    form.addEventListener('submit', (event) => {
      event.preventDefault();
      const message = form.querySelector('[data-form-message]');
      if (message) {
        message.textContent = 'This form is not connected yet. Please call +92 304 6734508.';
        message.hidden = false;
      }
    });
  });
})();
