let state = {
  notes: [],
  total: 0,
  page: 1,
  pageSize: 10,
  sort: 'created_desc',
  searchQuery: ''
};

async function fetchJSON(url, options) {
  const res = await fetch(url, options);
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

async function loadNotes() {
  const list = document.getElementById('notes');
  list.innerHTML = '';
  
  const params = new URLSearchParams({
    page: state.page,
    page_size: state.pageSize,
    sort: state.sort
  });
  
  let url = `/notes/?${params}`;
  if (state.searchQuery) {
    url = `/notes/search/?${params}&q=${encodeURIComponent(state.searchQuery)}`;
  }
  
  const data = await fetchJSON(url);
  state.notes = data.items;
  state.total = data.total;
  
  updateResultCount();
  updatePaginationControls();
  
  for (const n of state.notes) {
    const li = document.createElement('li');
    li.textContent = `${n.title}: ${n.content}`;
    list.appendChild(li);
  }
}

function updateResultCount() {
  const countEl = document.getElementById('result-count');
  if (countEl) {
    countEl.textContent = `Showing ${state.notes.length} of ${state.total} notes`;
  }
}

function updatePaginationControls() {
  const prevBtn = document.getElementById('prev-page');
  const nextBtn = document.getElementById('next-page');
  const pageInfo = document.getElementById('page-info');
  
  if (prevBtn) prevBtn.disabled = state.page <= 1;
  if (nextBtn) nextBtn.disabled = state.page * state.pageSize >= state.total;
  if (pageInfo) pageInfo.textContent = `Page ${state.page}`;
}

let searchDebounceTimer = null;

async function loadActions() {
  const list = document.getElementById('actions');
  list.innerHTML = '';
  const items = await fetchJSON('/action-items/');
  for (const a of items) {
    const li = document.createElement('li');
    li.textContent = `${a.description} [${a.completed ? 'done' : 'open'}]`;
    if (!a.completed) {
      const btn = document.createElement('button');
      btn.textContent = 'Complete';
      btn.onclick = async () => {
        await fetchJSON(`/action-items/${a.id}/complete`, { method: 'PUT' });
        loadActions();
      };
      li.appendChild(btn);
    }
    list.appendChild(li);
  }
}

window.addEventListener('DOMContentLoaded', () => {
  const noteSearch = document.getElementById('note-search');
  if (noteSearch) {
    noteSearch.addEventListener('input', (e) => {
      clearTimeout(searchDebounceTimer);
      searchDebounceTimer = setTimeout(() => {
        state.searchQuery = e.target.value;
        state.page = 1;
        loadNotes();
      }, 300);
    });
  }
  
  const sortSelect = document.getElementById('sort-select');
  if (sortSelect) {
    sortSelect.addEventListener('change', (e) => {
      state.sort = e.target.value;
      state.page = 1;
      loadNotes();
    });
  }
  
  const prevBtn = document.getElementById('prev-page');
  if (prevBtn) {
    prevBtn.addEventListener('click', () => {
      if (state.page > 1) {
        state.page--;
        loadNotes();
      }
    });
  }
  
  const nextBtn = document.getElementById('next-page');
  if (nextBtn) {
    nextBtn.addEventListener('click', () => {
      state.page++;
      loadNotes();
    });
  }

  document.getElementById('note-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const title = document.getElementById('note-title').value;
    const content = document.getElementById('note-content').value;
    await fetchJSON('/notes/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ title, content }),
    });
    e.target.reset();
    loadNotes();
  });

  document.getElementById('action-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const description = document.getElementById('action-desc').value;
    await fetchJSON('/action-items/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ description }),
    });
    e.target.reset();
    loadActions();
  });

  loadNotes();
  loadActions();
});
