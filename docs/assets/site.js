(() => {
  const root = document.documentElement;
  const readPreference = key => {
    try { return localStorage.getItem(key); } catch { return null; }
  };
  const savePreference = (key, value) => {
    try { localStorage.setItem(key, value); } catch { /* Reading works without storage. */ }
  };
  const savedTheme = readPreference('reading-theme');
  root.dataset.theme = ['light', 'dark'].includes(savedTheme)
    ? savedTheme : (matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');

  function updateThemeButtons() {
    document.querySelectorAll('[data-theme-toggle]').forEach(button => {
      button.textContent = root.dataset.theme === 'dark' ? '浅色' : '深色';
      button.setAttribute('aria-label', `切换到${button.textContent}阅读主题`);
    });
  }
  updateThemeButtons();

  document.querySelectorAll('[data-theme-toggle]').forEach(button => {
    button.addEventListener('click', () => {
      const next = root.dataset.theme === 'dark' ? 'light' : 'dark';
      root.dataset.theme = next;
      savePreference('reading-theme', next);
      updateThemeButtons();
    });
  });

  document.querySelectorAll('a[href^="http"]').forEach(link => {
    link.target = '_blank';
    link.rel = 'noopener noreferrer';
  });

  const search = document.querySelector('input[data-search]');
  const cards = [...document.querySelectorAll('[data-book-card]')];
  const filters = [...document.querySelectorAll('[data-filter]')];
  const empty = document.querySelector('[data-empty]');
  let category = '全部';

  function updateCards() {
    if (!cards.length) return;
    const query = (search?.value || '').trim().toLowerCase();
    let visible = 0;
    cards.forEach(card => {
      const categoryMatch = category === '全部' || card.dataset.category === category;
      const textMatch = !query || card.dataset.search.includes(query);
      const show = categoryMatch && textMatch;
      card.hidden = !show;
      if (show) visible += 1;
    });
    if (empty) empty.hidden = visible !== 0;
  }

  search?.addEventListener('input', updateCards);
  filters.forEach(button => button.addEventListener('click', () => {
    category = button.dataset.filter;
    filters.forEach(item => item.classList.toggle('active', item === button));
    updateCards();
  }));

  const paper = document.querySelector('.paper');
  const headings = [...document.querySelectorAll('.paper h2, .paper h3')];
  const tocLinks = [...document.querySelectorAll('#toc a')];
  const tocDetails = document.querySelector('.reader-toc');
  const tocScroll = document.querySelector('.toc-content');
  const wideScreen = matchMedia('(min-width: 1024px)');
  const reducedMotion = matchMedia('(prefers-reduced-motion: reduce)');
  const progress = document.querySelector('#progress');
  let activeIndex = -1;
  let framePending = false;

  function updateReadingPosition() {
    framePending = false;
    if (!paper) return;
    const rect = paper.getBoundingClientRect();
    const distance = Math.max(1, rect.height - innerHeight);
    if (progress) progress.style.width = `${Math.max(0, Math.min(1, -rect.top / distance)) * 100}%`;
    let nextIndex = -1;
    for (let index = 0; index < headings.length; index += 1) {
      if (headings[index].getBoundingClientRect().top > Math.max(32, innerHeight * .18)) break;
      nextIndex = index;
    }
    if (nextIndex === activeIndex) return;
    tocLinks[activeIndex]?.classList.remove('active');
    tocLinks[activeIndex]?.removeAttribute('aria-current');
    activeIndex = nextIndex;
    const current = tocLinks[activeIndex];
    current?.classList.add('active');
    current?.setAttribute('aria-current', 'location');
    // Move only the desktop outline's own scroll area, never the document.
    if (current && wideScreen.matches && tocDetails?.open && tocScroll &&
        !tocScroll.matches(':hover, :focus-within')) {
      const linkRect = current.getBoundingClientRect();
      const panelRect = tocScroll.getBoundingClientRect();
      if (linkRect.top < panelRect.top || linkRect.bottom > panelRect.bottom) {
        tocScroll.scrollTop += linkRect.top - panelRect.top - panelRect.height / 3;
      }
    }
  }

  function scheduleReadingPosition() {
    if (!framePending) {
      framePending = true;
      requestAnimationFrame(updateReadingPosition);
    }
  }

  function scrollToElement(element) {
    element.focus({ preventScroll: true });
    element.scrollIntoView({ block: 'start', behavior: reducedMotion.matches ? 'auto' : 'smooth' });
  }

  if (tocDetails) {
    const adaptOutline = () => {
      tocDetails.open = wideScreen.matches;
      scheduleReadingPosition();
    };
    adaptOutline();
    wideScreen.addEventListener('change', adaptOutline);
    tocDetails.addEventListener('toggle', scheduleReadingPosition);
    tocDetails.addEventListener('keydown', event => {
      if (event.key === 'Escape' && tocDetails.open) {
        tocDetails.open = false;
        tocDetails.querySelector('summary').focus();
      }
    });

    tocLinks.forEach(link => link.addEventListener('click', event => {
      if (event.button || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
      const target = document.getElementById(decodeURIComponent(link.hash.slice(1)));
      if (!target) return;
      event.preventDefault();
      if (!wideScreen.matches) tocDetails.open = false;
      // Closing the inline outline changes the target's document position.
      requestAnimationFrame(() => {
        history.pushState(null, '', link.hash);
        scrollToElement(target);
      });
    }));

    document.querySelectorAll('a[href="#reader-toc"]').forEach(link => {
      link.addEventListener('click', event => {
        if (event.button || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
        event.preventDefault();
        tocDetails.open = true;
        requestAnimationFrame(() => scrollToElement(tocDetails.querySelector('summary')));
      });
    });
  }

  const decrease = document.querySelector('[data-font-decrease]');
  const increase = document.querySelector('[data-font-increase]');
  const fontLabel = document.querySelector('[data-font-label]');
  const savedSize = Number(readPreference('reading-font-size'));
  let fontSize = [16, 18, 20, 22, 24].includes(savedSize) ? savedSize : 18;

  function updateFontSize() {
    root.style.setProperty('--reading-size', `${fontSize}px`);
    if (fontLabel) fontLabel.textContent = `${fontSize}`;
    if (decrease) decrease.disabled = fontSize <= 16;
    if (increase) increase.disabled = fontSize >= 24;
    scheduleReadingPosition();
  }

  if (paper) {
    document.querySelector('[data-reading-settings]').hidden = false;
    updateFontSize();
    decrease?.addEventListener('click', () => {
      fontSize = Math.max(16, fontSize - 2);
      updateFontSize();
      savePreference('reading-font-size', String(fontSize));
    });
    increase?.addEventListener('click', () => {
      fontSize = Math.min(24, fontSize + 2);
      updateFontSize();
      savePreference('reading-font-size', String(fontSize));
    });
    addEventListener('scroll', scheduleReadingPosition, { passive: true });
    addEventListener('resize', scheduleReadingPosition);
    addEventListener('load', scheduleReadingPosition);
    if ('ResizeObserver' in window) new ResizeObserver(scheduleReadingPosition).observe(paper);
    scheduleReadingPosition();
  }
})();
