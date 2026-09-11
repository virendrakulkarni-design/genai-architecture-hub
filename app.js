/**
 * GenAI Architecture Hub - Client Application
 * Expansive Responsive Layout Engine:
 * - Desktop: Sticky Left Sidebar Index + Wide Responsive Reader Pane (95% width utilization)
 * - Tablet/Mobile: Responsive single column with quick-jump pills & sticky toolbar
 * - Instant sidebar search filter
 * - Keyboard navigation (Left/Right Arrow)
 * - Dynamic Mermaid compilation
 */

let allPosts = [];
let currentIndex = 0;

document.addEventListener('DOMContentLoaded', async () => {
  // 1. Initialize Mermaid configuration
  mermaid.initialize({
    startOnLoad: false,
    theme: document.body.classList.contains('light-theme') ? 'default' : 'dark',
    themeVariables: {
      fontFamily: 'Inter, -apple-system, sans-serif',
      fontSize: '13.5px',
      primaryColor: '#0f172a',
      primaryTextColor: '#f8fafc',
      primaryBorderColor: '#10b981',
      lineColor: '#64748b'
    },
    securityLevel: 'loose'
  });

  // 2. Setup Theme
  initTheme();

  // 3. Load Posts Data
  await loadPosts();

  if (!allPosts || allPosts.length === 0) {
    document.getElementById('single-post-container').innerHTML = `<div class="empty-state">No dispatches available.</div>`;
    return;
  }

  // 4. Determine initial post from URL hash (e.g. #post-3)
  const hash = window.location.hash.replace('#', '');
  const hashIndex = allPosts.findIndex(p => p.id === hash);
  if (hashIndex !== -1) {
    currentIndex = hashIndex;
  }

  // 5. Initialize Navigation & Controls
  renderSidebarList(allPosts);
  renderMobilePills();
  initDropdown();
  initToolbarButtons();
  initBottomCards();
  initKeyboardNav();
  initSidebarSearch();

  // 6. Display active post
  showPost(currentIndex, false);

  // 7. Track Hub Visitor Telemetry
  initVisitorTracking();
});

/**
 * Load Posts from window.POSTS_DATA or fetch('data/posts.json')
 */
async function loadPosts() {
  if (window.POSTS_DATA && Array.isArray(window.POSTS_DATA)) {
    allPosts = window.POSTS_DATA;
    return;
  }

  try {
    const res = await fetch('data/posts.json');
    if (res.ok) {
      allPosts = await res.json();
    }
  } catch (err) {
    console.warn("Could not fetch data/posts.json, relying on inline data if available", err);
  }
}

/**
 * Display Single Post at index
 */
async function showPost(index, shouldScroll = true) {
  if (index < 0 || index >= allPosts.length) return;
  currentIndex = index;
  const post = allPosts[currentIndex];

  const container = document.getElementById('single-post-container');
  if (!container) return;

  const isLatest = (currentIndex === allPosts.length - 1);

  // Render Post HTML
  container.innerHTML = `
    <article id="${post.id}" class="post-card">
      <div class="post-header">
        <div class="post-meta">
          <span class="difficulty-badge ${post.levelClass || 'level-1'}">${escapeHtml(post.level)}</span>
          ${isLatest ? '<span class="badge-latest">LATEST DISPATCH</span>' : ''}
          ${post.publishedAt ? `<span class="post-date">Published: ${escapeHtml(post.publishedAt)}</span>` : ''}
          <span class="read-time">${escapeHtml(post.readTime)}</span>
          <span class="target-role">Audience: ${escapeHtml(post.audience)}</span>
        </div>
        <h2 class="post-title">${escapeHtml(post.title)}</h2>
        <p class="post-lead">${escapeHtml(post.lead)}</p>
        
        <div class="action-bar">
          <button class="btn-copy-slack" onclick="copyPostMarkdown('${post.id}')">
            Copy Post for Slack / Teams / Confluence
          </button>
        </div>
      </div>

      <div class="post-body">
        <!-- Reality Check Stats Box -->
        <div class="stat-callout ${post.stats.type || 'info'}">
          <div class="stat-icon">${getStatIcon(post.stats.type)}</div>
          <div class="stat-text">
            <strong>${escapeHtml(post.stats.title)}</strong>
            <ul>
              ${post.stats.items.map(item => `<li>${item}</li>`).join('')}
            </ul>
          </div>
        </div>

        <!-- 60-Second Mental Model -->
        <h3>${escapeHtml(post.mentalModel.title)}</h3>
        <p>${post.mentalModel.text}</p>

        <!-- Architecture Diagram -->
        <div class="diagram-wrapper">
          <div class="mermaid">
${post.diagram}
          </div>
          <span class="diagram-caption">${escapeHtml(post.diagramCaption)}</span>
        </div>

        <!-- Code Block -->
        <div class="code-wrapper">
          <div class="code-header">
            <span>${escapeHtml(post.codeTitle)}</span>
            <button class="btn-copy-code" onclick="copySnippet(this)">Copy</button>
          </div>
          <pre><code>${escapeHtml(post.codeContent)}</code></pre>
        </div>

        <!-- Key Takeaways -->
        <div class="takeaway-box">
          <h4>${escapeHtml(post.takeaway.title)}</h4>
          <ol>
            ${post.takeaway.items.map(item => `<li>${item}</li>`).join('')}
          </ol>
          <p class="takeaway-badge">${escapeHtml(post.takeaway.badge)}</p>
        </div>
      </div>
    </article>
  `;

  // Compile Mermaid Diagram for this post
  try {
    await mermaid.run({
      nodes: container.querySelectorAll('.mermaid')
    });
  } catch (err) {
    console.warn("Mermaid compile notice:", err);
  }

  // Update UI Navigation States
  updateNavigationState();

  // Update URL hash without reload
  history.replaceState(null, null, `#${post.id}`);

  // Scroll to top of article if user navigated
  if (shouldScroll) {
    const toolbar = document.querySelector('.reader-toolbar-sticky');
    const offset = toolbar ? toolbar.offsetHeight + 40 : 80;
    const top = container.getBoundingClientRect().top + window.pageYOffset - offset;
    window.scrollTo({ top, behavior: 'smooth' });
  }
}

/**
 * Update Nav State across Toolbar, Sidebar, and Bottom Cards
 */
function updateNavigationState() {
  const total = allPosts.length;
  const post = allPosts[currentIndex];

  // 1. Counter badge & Dropdown
  const counter = document.getElementById('postCounter');
  if (counter) counter.textContent = `Dispatch ${currentIndex + 1} of ${total}`;

  const dropdown = document.getElementById('postDropdown');
  if (dropdown) dropdown.value = currentIndex;

  // 2. Toolbar buttons
  const prevBtn = document.getElementById('prevBtnTop');
  const nextBtn = document.getElementById('nextBtnTop');
  if (prevBtn) prevBtn.disabled = (currentIndex === 0);
  if (nextBtn) nextBtn.disabled = (currentIndex === total - 1);

  // 3. Left Sidebar Active Highlight
  document.querySelectorAll('.sidebar-item').forEach((item) => {
    const itemIndex = parseInt(item.getAttribute('data-index'), 10);
    const isActive = (itemIndex === currentIndex);
    item.classList.toggle('active', isActive);
    if (isActive) {
      item.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }
  });

  // 4. Mobile Pills Active State
  document.querySelectorAll('#mobileLevelTabs .tab-btn').forEach((btn, idx) => {
    btn.classList.toggle('active', idx === currentIndex);
  });

  // 5. Bottom Next/Prev Navigation Cards
  const prevCard = document.getElementById('footerPrevCard');
  const nextCard = document.getElementById('footerNextCard');
  const prevTitle = document.getElementById('footerPrevTitle');
  const nextTitle = document.getElementById('footerNextTitle');

  if (currentIndex > 0) {
    prevCard.classList.remove('disabled');
    prevTitle.textContent = allPosts[currentIndex - 1].title;
  } else {
    prevCard.classList.add('disabled');
    prevTitle.textContent = "You're at the first dispatch";
  }

  if (currentIndex < total - 1) {
    nextCard.classList.remove('disabled');
    nextTitle.textContent = allPosts[currentIndex + 1].title;
  } else {
    nextCard.classList.add('disabled');
    nextTitle.textContent = "You're at the latest dispatch";
  }
}

/**
 * Render Sidebar Dispatch List
 */
function renderSidebarList(posts) {
  const listContainer = document.getElementById('sidebarList');
  const countBadge = document.getElementById('sidebarPostCount');
  if (!listContainer) return;

  if (countBadge) {
    countBadge.textContent = `${posts.length} dispatches`;
  }

  if (posts.length === 0) {
    listContainer.innerHTML = `<div style="padding: 16px; color: var(--text-muted); font-size: 13px;">No dispatches found</div>`;
    return;
  }

  listContainer.innerHTML = posts.map((post) => {
    const originalIndex = allPosts.findIndex(p => p.id === post.id);
    const shortLevel = post.level.split(':')[0] || `LEVEL ${originalIndex + 1}`;
    const isLatest = (originalIndex === allPosts.length - 1);
    return `
      <div class="sidebar-item ${originalIndex === currentIndex ? 'active' : ''}" data-index="${originalIndex}" onclick="showPost(${originalIndex})">
        <div class="sidebar-item-top">
          <span class="sidebar-item-level">${escapeHtml(shortLevel)}</span>
          ${isLatest ? '<span class="sidebar-latest-tag">LATEST</span>' : ''}
        </div>
        <div class="sidebar-item-title">${escapeHtml(post.title)}</div>
        <div class="sidebar-item-meta">
          <span>${escapeHtml(post.readTime)}</span>
          ${post.publishedAt ? `<span class="sidebar-item-date">${escapeHtml(post.publishedAt)}</span>` : ''}
        </div>
      </div>
    `;
  }).join('');
}

/**
 * Render Mobile / Tablet Level Pills
 */
function renderMobilePills() {
  const container = document.getElementById('mobileLevelTabs');
  if (!container) return;

  container.innerHTML = allPosts.map((post, idx) => {
    const shortLabel = post.level.split(':')[1]?.trim() || post.title.slice(0, 14);
    return `
      <button class="tab-btn ${idx === currentIndex ? 'active' : ''}" onclick="showPost(${idx})">
        <span class="tab-num">L${idx + 1}</span>
        <span class="tab-label">${escapeHtml(shortLabel)}</span>
      </button>
    `;
  }).join('');
}

/**
 * Initialize Dropdown Menu
 */
function initDropdown() {
  const dropdown = document.getElementById('postDropdown');
  if (!dropdown) return;

  dropdown.innerHTML = allPosts.map((p, idx) => `
    <option value="${idx}">L${idx + 1}: ${escapeHtml(p.title)}</option>
  `).join('');

  dropdown.addEventListener('change', (e) => {
    showPost(parseInt(e.target.value, 10));
  });
}

/**
 * Initialize Toolbar Buttons
 */
function initToolbarButtons() {
  const prevBtn = document.getElementById('prevBtnTop');
  const nextBtn = document.getElementById('nextBtnTop');

  if (prevBtn) {
    prevBtn.addEventListener('click', () => {
      if (currentIndex > 0) showPost(currentIndex - 1);
    });
  }

  if (nextBtn) {
    nextBtn.addEventListener('click', () => {
      if (currentIndex < allPosts.length - 1) showPost(currentIndex + 1);
    });
  }
}

/**
 * Initialize Bottom Navigation Cards
 */
function initBottomCards() {
  const prevCard = document.getElementById('footerPrevCard');
  const nextCard = document.getElementById('footerNextCard');

  if (prevCard) {
    prevCard.addEventListener('click', () => {
      if (currentIndex > 0) showPost(currentIndex - 1);
    });
  }

  if (nextCard) {
    nextCard.addEventListener('click', () => {
      if (currentIndex < allPosts.length - 1) showPost(currentIndex + 1);
    });
  }
}

/**
 * Keyboard Navigation (Left / Right Arrow Keys)
 */
function initKeyboardNav() {
  window.addEventListener('keydown', (e) => {
    if (e.target && (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA' || e.target.tagName === 'SELECT')) {
      return;
    }

    if (e.key === 'ArrowLeft') {
      if (currentIndex > 0) {
        showPost(currentIndex - 1);
        showToast("← Previous Dispatch");
      }
    } else if (e.key === 'ArrowRight') {
      if (currentIndex < allPosts.length - 1) {
        showPost(currentIndex + 1);
        showToast("Next Dispatch →");
      }
    }
  });
}

/**
 * Sidebar Search & Filter
 */
function initSidebarSearch() {
  const searchInput = document.getElementById('searchInput');
  if (!searchInput) return;

  searchInput.addEventListener('input', (e) => {
    const q = e.target.value.toLowerCase().trim();
    if (!q) {
      renderSidebarList(allPosts);
      return;
    }

    const filtered = allPosts.filter(p => 
      p.title.toLowerCase().includes(q) ||
      p.lead.toLowerCase().includes(q) ||
      p.level.toLowerCase().includes(q) ||
      (p.mentalModel && p.mentalModel.text.toLowerCase().includes(q))
    );

    renderSidebarList(filtered);
  });
}

function getStatIcon(type) {
  switch (type) {
    case 'danger': return 'CRITICAL IMPACT';
    case 'success': return 'BENCHMARK METRIC';
    case 'warning': return 'SYSTEM WARNING';
    default: return 'ENGINEERING DATA';
  }
}

/**
 * Copy Code Snippet
 */
function copySnippet(button) {
  const pre = button.closest('.code-wrapper').querySelector('pre code');
  if (!pre) return;
  
  navigator.clipboard.writeText(pre.innerText).then(() => {
    const originalText = button.innerText;
    button.innerText = 'Copied';
    setTimeout(() => {
      button.innerText = originalText;
    }, 2000);
    showToast("Code snippet copied to clipboard");
  }).catch(err => {
    console.error("Failed to copy snippet: ", err);
  });
}

/**
 * Copy Post for Slack / Teams / Confluence
 */
function copyPostMarkdown(postId) {
  const post = allPosts.find(p => p.id === postId);
  if (!post) return;

  const statsText = post.stats.items.map(i => `• ${stripHtml(i)}`).join('\n');
  const takeawayText = post.takeaway.items.map((it, idx) => `${idx + 1}. ${stripHtml(it)}`).join('\n');

  const markdown = `*GenAI Architectural Dispatch | ${post.level}*
═══════════════════════════════════════════════════════════════
*${post.title}*
${post.publishedAt ? `Published: ${post.publishedAt}\n` : ''}
${post.lead}

*${post.stats.title}*
${statsText}

*${post.mentalModel.title}*
${stripHtml(post.mentalModel.text)}

*PRODUCTION CODE / IMPLEMENTATION:*
\`\`\`
${post.codeContent}
\`\`\`

*${post.takeaway.title}*
${takeawayText}

*Key Takeaway:* ${post.takeaway.badge}
`;

  navigator.clipboard.writeText(markdown).then(() => {
    showToast(`Copied "${post.title.slice(0, 22)}..." ready for Slack/Teams`);
  }).catch(err => {
    console.error("Copy failed: ", err);
  });
}

function stripHtml(html) {
  const tmp = document.createElement("DIV");
  tmp.innerHTML = html;
  return tmp.textContent || tmp.innerText || "";
}

function escapeHtml(text) {
  if (!text) return "";
  return text
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

/**
 * Theme Manager
 */
function initTheme() {
  const themeToggle = document.getElementById('themeToggle');
  const savedTheme = localStorage.getItem('genai-hub-theme');
  
  if (savedTheme === 'light') {
    document.body.classList.add('light-theme');
  }

  if (themeToggle) {
    themeToggle.addEventListener('click', () => {
      document.body.classList.toggle('light-theme');
      const isLight = document.body.classList.contains('light-theme');
      localStorage.setItem('genai-hub-theme', isLight ? 'light' : 'dark');
      showToast(isLight ? "Switched to Light Theme" : "Switched to Dark Theme");
      showPost(currentIndex, false);
    });
  }
}

/**
 * Visitor Telemetry Tracker
 */
function initVisitorTracking() {
  try {
    const visitsKey = 'genai_hub_total_visits';
    let visits = parseInt(localStorage.getItem(visitsKey) || '0', 10);
    visits += 1;
    localStorage.setItem(visitsKey, visits.toString());

    const badge = document.querySelector('.visitor-tracker-badge');
    if (badge) {
      badge.title = `Total visits tracked on this device: ${visits}. Live hub telemetry.`;
    }
  } catch (e) {
    // Graceful fallback for sandboxed/restricted iframe environments
  }
}
