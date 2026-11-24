const galleryLinks = [...document.querySelectorAll('.gallery a')];
const viewer = document.querySelector('.lightbox');

if (viewer && typeof viewer.showModal === 'function' && galleryLinks.length) {
  const photo = viewer.querySelector('img');
  const caption = viewer.querySelector('figcaption');
  const close = viewer.querySelector('.lightbox-close');
  let active = 0;
  let opener;
  let backdropPointerDown = false;

  function displayPhoto(index) {
    active = (index + galleryLinks.length) % galleryLinks.length;
    const link = galleryLinks[active];
    photo.src = link.href;
    photo.alt = link.querySelector('img').alt;
    caption.textContent = link.dataset.caption;
  }

  galleryLinks.forEach((link, index) => {
    link.addEventListener('click', (event) => {
      if (event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return;
      event.preventDefault();
      opener = link;
      displayPhoto(index);
      viewer.showModal();
      close.focus();
    });
  });
  close.addEventListener('click', () => viewer.close());
  viewer.querySelector('.previous').addEventListener('click', () => displayPhoto(active - 1));
  viewer.querySelector('.next').addEventListener('click', () => displayPhoto(active + 1));
  viewer.addEventListener('pointerdown', (event) => {
    backdropPointerDown = event.target === viewer;
  });
  viewer.addEventListener('click', (event) => {
    if (event.target === viewer && backdropPointerDown) viewer.close();
    backdropPointerDown = false;
  });
  viewer.addEventListener('close', () => {
    backdropPointerDown = false;
    opener?.focus();
  });
  viewer.addEventListener('keydown', (event) => {
    if (event.key === 'ArrowLeft' || event.key === 'ArrowRight') {
      event.preventDefault();
      displayPhoto(active + (event.key === 'ArrowLeft' ? -1 : 1));
    }
  });
}
