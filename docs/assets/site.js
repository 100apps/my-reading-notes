(() => {
  const root = document.documentElement;
  const savedTheme = localStorage.getItem('reading-theme');
  if (savedTheme) root.dataset.theme = savedTheme;

  document.querySelectorAll('[data-theme-toggle]').forEach(button => {
    button.addEventListener('click', () => {
      const next = root.dataset.theme === 'dark' ? 'light' : 'dark';
      root.dataset.theme = next;
      localStorage.setItem('reading-theme', next);
    });
  });

  document.querySelectorAll('a[href^="http"]').forEach(link => {
    link.target = '_blank';
    link.rel = 'noopener noreferrer';
  });

  const search = document.querySelector('[data-search]');
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

  const menuButton = document.querySelector('[data-menu-toggle]');
  menuButton?.addEventListener('click', () => {
    const open = document.body.classList.toggle('menu-open');
    menuButton.setAttribute('aria-expanded', String(open));
  });

  const headings = [...document.querySelectorAll('.paper h2, .paper h3')];
  const toc = document.querySelector('#toc');
  const tocLinks = new Map();
  if (toc) {
    headings.forEach(heading => {
      const link = document.createElement('a');
      link.href = `#${heading.id}`;
      link.textContent = heading.textContent;
      link.className = `level-${heading.tagName.slice(1)}`;
      link.addEventListener('click', () => {
        document.body.classList.remove('menu-open');
        menuButton?.setAttribute('aria-expanded', 'false');
      });
      toc.append(link);
      tocLinks.set(heading, link);
    });
    const observer = new IntersectionObserver(entries => {
      const visible = entries.filter(entry => entry.isIntersecting).sort((a, b) => a.boundingClientRect.top - b.boundingClientRect.top)[0];
      if (!visible) return;
      tocLinks.forEach(link => link.classList.remove('active'));
      tocLinks.get(visible.target)?.classList.add('active');
    }, { rootMargin: '-12% 0px -72% 0px' });
    headings.forEach(heading => observer.observe(heading));
  }

  const progress = document.querySelector('#progress');
  if (progress) {
    const updateProgress = () => {
      const max = document.documentElement.scrollHeight - innerHeight;
      progress.style.width = `${max > 0 ? (scrollY / max) * 100 : 0}%`;
    };
    addEventListener('scroll', updateProgress, { passive: true });
    addEventListener('resize', updateProgress);
    updateProgress();
  }
})();
