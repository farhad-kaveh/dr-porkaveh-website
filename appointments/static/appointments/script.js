const menuBtn=document.querySelector('.menu-btn');
const nav=document.querySelector('.nav');
if(menuBtn){menuBtn.addEventListener('click',()=>{const open=nav.classList.toggle('open');menuBtn.setAttribute('aria-expanded',open?'true':'false')})}
document.querySelectorAll('.nav a').forEach(a=>a.addEventListener('click',()=>nav.classList.remove('open')));

// Portfolio category filter
(function () {
  const buttons = document.querySelectorAll('.case-filter');
  const groups = document.querySelectorAll('.case-group');
  if (!buttons.length || !groups.length) return;
  buttons.forEach((button) => {
    button.addEventListener('click', () => {
      const filter = button.dataset.filter;
      buttons.forEach((b) => b.classList.toggle('is-active', b === button));
      groups.forEach((group) => {
        group.hidden = filter !== 'all' && group.dataset.caseGroup !== filter;
      });
      const cases = document.getElementById('cases');
      if (cases) cases.scrollIntoView({ behavior: 'smooth', block: 'start' });
    });
  });
})();
