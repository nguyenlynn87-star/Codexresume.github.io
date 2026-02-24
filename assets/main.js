async function loadResume() {
  const response = await fetch('./assets/resume.json');
  const resume = await response.json();

  document.getElementById('name').textContent = resume.name || '';
  document.getElementById('headline').textContent = resume.headline || '';
  document.getElementById('summary').textContent = resume.summary || '';

  const emailBtn = document.getElementById('email-btn');
  if (resume.contact?.email) {
    emailBtn.href = `mailto:${resume.contact.email}`;
  }

  const skillsGrid = document.getElementById('skills-grid');
  (resume.skills || []).forEach((group) => {
    const card = document.createElement('article');
    card.className = 'card reveal';
    card.innerHTML = `<h3>${group.category}</h3><div class="chips"></div>`;
    const chips = card.querySelector('.chips');
    (group.items || []).forEach((item) => {
      const chip = document.createElement('span');
      chip.className = 'chip';
      chip.textContent = item;
      chips.appendChild(chip);
    });
    skillsGrid.appendChild(card);
  });

  const experienceList = document.getElementById('experience-list');
  (resume.experience || []).forEach((job) => {
    const card = document.createElement('article');
    card.className = 'card reveal';
    const highlights = (job.highlights || []).map((h) => `<li>${h}</li>`).join('');
    card.innerHTML = `
      <h3>${job.title} · ${job.company}</h3>
      <p class="meta">${job.dates || ''}</p>
      <ul>${highlights}</ul>
    `;
    experienceList.appendChild(card);
  });

  const educationList = document.getElementById('education-list');
  (resume.education || []).forEach((edu) => {
    const card = document.createElement('article');
    card.className = 'card reveal';
    card.innerHTML = `
      <h3>${edu.school || ''}</h3>
      <p>${edu.degree || ''}</p>
      <p class="meta">${edu.dates || ''}</p>
    `;
    educationList.appendChild(card);
  });

  const contactCard = document.getElementById('contact-card');
  const { phone, email, linkedin } = resume.contact || {};
  contactCard.innerHTML = `
    <p><strong>Phone:</strong> ${phone ? `<a href="tel:${phone.replaceAll('.', '')}">${phone}</a>` : ''}</p>
    <p><strong>Email:</strong> ${email ? `<a href="mailto:${email}">${email}</a>` : ''}</p>
    <p><strong>LinkedIn:</strong> ${linkedin ? `<a href="${linkedin}">${linkedin}</a>` : ''}</p>
  `;

  setupReveal();
}

function setupReveal() {
  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
    document.querySelectorAll('.reveal').forEach((el) => el.classList.add('in-view'));
    return;
  }

  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add('in-view');
          observer.unobserve(entry.target);
        }
      });
    },
    { threshold: 0.12 }
  );

  document.querySelectorAll('.reveal').forEach((el) => observer.observe(el));
}

loadResume();
