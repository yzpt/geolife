function setDynamicHeight() {
    let vh = window.innerHeight * 0.01;
    document.documentElement.style.setProperty('--vh', `${vh}px`);
}

// Initial calculation
setDynamicHeight();

// Recalculate on resize
window.addEventListener('resize', setDynamicHeight);
