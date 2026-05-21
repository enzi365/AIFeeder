// AIFeeder client JS. Sidebar collapse + loading-page fly-out + note-panel close.

(() => {
    // ---------- sidebar collapse ----------
    const toggle = document.querySelector('[data-sidebar-toggle]');
    const shell = document.querySelector('.shell');
    if (toggle && shell) {
        toggle.addEventListener('click', () => {
            const collapsed = shell.getAttribute('data-sidebar-collapsed') === 'true';
            shell.setAttribute('data-sidebar-collapsed', collapsed ? 'false' : 'true');
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

    // ---------- chip toggle (multi-select inside feedback callout) ----------
    document.addEventListener('click', (e) => {
        const chip = e.target.closest('.feedback-callout .chip');
        if (chip) chip.classList.toggle('selected');
    });
})();
