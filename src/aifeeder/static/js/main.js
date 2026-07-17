// AIFeeder client JS. Sidebar collapse + loading-page fly-out + note-panel close
// + reader text-selection → floating "+ Note" popup.

(() => {
    // ---------- sidebar collapse (both top chevron + expand-handle tab) ----------
    const shell = document.querySelector('.shell');
    if (shell) {
        document.querySelectorAll('[data-sidebar-toggle]').forEach((btn) => {
            btn.addEventListener('click', () => {
                const collapsed = shell.getAttribute('data-sidebar-collapsed') === 'true';
                shell.setAttribute('data-sidebar-collapsed', collapsed ? 'false' : 'true');
            });
        });
    }

    // ---------- loading-page fly-out ----------
    const stage = document.querySelector('.loading-stage');
    if (stage) {
        // assign each circle a random outward fly direction
        stage.querySelectorAll('.circle').forEach((el) => {
            const angle = Math.random() * Math.PI * 2;
            const dist = 800 + Math.random() * 400;
            el.style.setProperty('--fx', `${Math.cos(angle) * dist}px`);
            el.style.setProperty('--fy', `${Math.sin(angle) * dist}px`);
        });
        stage.addEventListener('click', () => {
            stage.classList.add('fly-out');
            setTimeout(() => { window.location.href = '/home'; }, 720);
        });
    }

    // ---------- close-note-panel button (delegated; HTMX may swap in the panel) ----------
    document.addEventListener('click', (e) => {
        if (e.target.closest('[data-close-note-panel]')) {
            const slot = document.getElementById('note-panel-slot');
            if (slot) slot.innerHTML = '';
        }
        if (e.target.closest('[data-cancel-feedback]')) {
            const slot = document.getElementById('feedback-callout');
            if (slot) slot.innerHTML = '';
        }
    });

    // ---------- modal close: Esc + backdrop click + Cancel / X button ----------
    // If the backdrop carries `data-modal-needs-reload` (e.g. the ingest panel
    // after a source was just created), reload the page on close so the sidebar
    // reflects the new state. Otherwise just clear the slot.
    const closeModal = () => {
        const slot = document.getElementById('modal-slot');
        const backdrop = slot && slot.querySelector('[data-modal-backdrop]');
        const needsReload = backdrop && backdrop.hasAttribute('data-modal-needs-reload');
        if (slot) slot.innerHTML = '';
        if (needsReload) window.location.reload();
    };

    document.addEventListener('click', (e) => {
        // explicit close affordances (Cancel button, X button)
        if (e.target.closest('[data-modal-close]')) {
            closeModal();
            return;
        }
        // click on the backdrop itself (but NOT on the modal card or anything inside it)
        const backdrop = e.target.closest('[data-modal-backdrop]');
        if (backdrop && e.target === backdrop) {
            closeModal();
        }
    });

    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && document.querySelector('[data-modal-backdrop]')) {
            closeModal();
        }
    });

    // ---------- chip toggle (multi-select inside feedback callout) ----------
    document.addEventListener('click', (e) => {
        const chip = e.target.closest('.feedback-callout .chip');
        if (chip) chip.classList.toggle('selected');
    });

    // ---------- reader text selection → floating "+ Note" popup ----------
    const reader = document.querySelector('.reader');
    const popup = document.getElementById('selection-popup');
    if (reader && popup) {
        const itemId = popup.dataset.itemId;
        let currentQuote = '';

        const hidePopup = () => {
            popup.classList.remove('visible');
            currentQuote = '';
        };

        const showPopupForSelection = () => {
            const sel = window.getSelection();
            const text = sel ? sel.toString().trim() : '';
            if (!text || text.length < 3) {
                hidePopup();
                return;
            }
            // only show if the selection is inside the reader
            if (!sel.anchorNode || !reader.contains(sel.anchorNode)) {
                hidePopup();
                return;
            }
            const range = sel.getRangeAt(0);
            const rect = range.getBoundingClientRect();
            if (rect.width === 0 && rect.height === 0) {
                hidePopup();
                return;
            }
            currentQuote = text;
            // position above the centre of the selection, page-coordinates
            const popupWidthGuess = 160;
            const top = rect.top + window.scrollY - 44;
            const left = rect.left + window.scrollX + (rect.width / 2) - (popupWidthGuess / 2);
            popup.style.top = `${Math.max(top, 8)}px`;
            popup.style.left = `${Math.max(left, 8)}px`;
            popup.classList.add('visible');
        };

        reader.addEventListener('mouseup', () => {
            // Slight delay so the selection settles before we read it.
            setTimeout(showPopupForSelection, 0);
        });

        document.addEventListener('mousedown', (e) => {
            if (popup.contains(e.target)) return;
            if (e.target.closest('.reader')) return;
            hidePopup();
        });

        popup.querySelector('button').addEventListener('click', () => {
            if (!currentQuote || !window.htmx) return;
            const url = `/notes/${itemId}/panel?quote=${encodeURIComponent(currentQuote)}`;
            window.htmx.ajax('GET', url, '#note-panel-slot');
            hidePopup();
            // clear browser selection so the user sees the highlight cleanly when it lands
            window.getSelection().removeAllRanges();
        });
    }
})();
