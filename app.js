/* ===================================================
   JobAI — Main Application Logic
   =================================================== */

// ==================== STATE ====================
let state = {
  jobs: [],
  filteredJobs: [],
  applications: {}, // jobId -> status (wishlist/applied/interview/offer/rejected)
  resumeUploaded: false,
  resumeFile: null,
  detectedSkills: [],
  matchScores: {}, // jobId -> score (0-100)
  theme: 'dark',
  activeSection: 'dashboard',
};

// ==================== JOB DATA ====================
const JOBS_DATA = [
  {
    id: 1, title: "Senior Frontend Engineer", company: "Google", logo: "🟦",
    location: "Bangalore", type: "Full-time", category: "Engineering",
    salary: "₹40–60 LPA", experience: "5+ years", posted: "2 days ago",
    skills: ["React", "TypeScript", "Next.js", "GraphQL", "CSS", "Performance"],
    description: "Join our world-class frontend team to build products used by billions. You'll work on complex UI systems, improve performance at scale, and mentor junior engineers.",
    responsibilities: [
      "Design and implement scalable frontend systems",
      "Collaborate with design and backend teams",
      "Conduct code reviews and maintain high code standards",
      "Drive technical decisions and architecture"
    ],
    requirements: ["5+ years of React/TypeScript experience", "Experience with large-scale web apps", "Strong CS fundamentals", "Excellent communication skills"],
    aiReason: "Matches your React/TypeScript skills and frontend engineering background",
  },
  {
    id: 2, title: "ML Engineer", company: "OpenAI", logo: "⚫",
    location: "Remote", type: "Full-time", category: "Engineering",
    salary: "$180–250K", experience: "4+ years", posted: "1 day ago",
    skills: ["Python", "PyTorch", "LLMs", "CUDA", "Transformers", "MLOps"],
    description: "Work on cutting-edge language models and help shape the future of AI. You'll train, fine-tune, and deploy large-scale ML models.",
    responsibilities: [
      "Train and fine-tune large language models",
      "Design ML experiments and evaluations",
      "Optimize model performance and efficiency",
      "Collaborate with research teams"
    ],
    requirements: ["Strong Python and ML background", "Experience with PyTorch/TensorFlow", "Background in NLP or computer vision", "Research publication is a plus"],
    aiReason: "Perfect fit for your AI/ML skills and Python expertise",
  },
  {
    id: 3, title: "Product Designer", company: "Figma", logo: "🎨",
    location: "Remote", type: "Full-time", category: "Design",
    salary: "$130–160K", experience: "3+ years", posted: "3 days ago",
    skills: ["Figma", "Design Systems", "User Research", "Prototyping", "CSS"],
    description: "Shape the future of design tooling. Work with our product team to create intuitive, beautiful interfaces for millions of designers worldwide.",
    responsibilities: [
      "Design end-to-end product experiences",
      "Build and maintain design systems",
      "Conduct user research and usability testing",
      "Collaborate with engineers to ensure design quality"
    ],
    requirements: ["3+ years of product design experience", "Expert Figma proficiency", "Portfolio showcasing shipped products", "Strong communication skills"],
    aiReason: "Your design skills and Figma expertise make you a strong candidate",
  },
  {
    id: 4, title: "Data Scientist", company: "Netflix", logo: "🔴",
    location: "Mumbai", type: "Full-time", category: "Data",
    salary: "₹35–55 LPA", experience: "3+ years", posted: "5 days ago",
    skills: ["Python", "SQL", "Spark", "Statistics", "A/B Testing", "ML"],
    description: "Use data to drive decisions that affect 200M+ subscribers. You'll build models, run experiments, and create insights that directly influence Netflix's growth.",
    responsibilities: [
      "Build predictive models for content recommendations",
      "Design and analyze A/B tests",
      "Create dashboards and reports for leadership",
      "Partner with product and engineering teams"
    ],
    requirements: ["3+ years of data science experience", "Strong SQL and Python skills", "Experience with experimentation", "Statistical modeling expertise"],
    aiReason: "Your data analysis and Python skills align perfectly with this role",
  },
  {
    id: 5, title: "DevOps Engineer", company: "Razorpay", logo: "💳",
    location: "Bangalore", type: "Full-time", category: "Engineering",
    salary: "₹25–40 LPA", experience: "3+ years", posted: "1 week ago",
    skills: ["Kubernetes", "Docker", "AWS", "Terraform", "CI/CD", "Linux"],
    description: "Build and maintain the infrastructure powering India's leading payment platform. You'll work on high-availability systems processing millions of transactions.",
    responsibilities: [
      "Manage Kubernetes clusters and container infrastructure",
      "Build and improve CI/CD pipelines",
      "Monitor system performance and reliability",
      "Implement security best practices"
    ],
    requirements: ["Experience with Kubernetes and Docker", "Cloud infrastructure (AWS/GCP)", "Infrastructure as code (Terraform)", "Strong Linux knowledge"],
    aiReason: "Your cloud and DevOps skills match the requirements well",
  },
  {
    id: 6, title: "Full Stack Developer", company: "Swiggy", logo: "🧡",
    location: "Hyderabad", type: "Full-time", category: "Engineering",
    salary: "₹20–35 LPA", experience: "2+ years", posted: "4 days ago",
    skills: ["Node.js", "React", "PostgreSQL", "Redis", "AWS", "REST APIs"],
    description: "Work on one of India's most complex food-tech platforms. Build features that serve 50M+ hungry customers daily.",
    responsibilities: [
      "Develop new features for web and mobile apps",
      "Optimize database queries and API performance",
      "Write clean, testable code",
      "Participate in on-call rotations"
    ],
    requirements: ["2+ years of full-stack experience", "Proficiency in Node.js and React", "Database design skills", "API development experience"],
    aiReason: "Your full-stack skills and Node.js experience are a strong match",
  },
  {
    id: 7, title: "Backend Engineer", company: "Zepto", logo: "🟢",
    location: "Mumbai", type: "Full-time", category: "Engineering",
    salary: "₹18–30 LPA", experience: "2+ years", posted: "2 days ago",
    skills: ["Java", "Spring Boot", "Kafka", "MongoDB", "Microservices", "AWS"],
    description: "Build the backend systems for India's fastest growing quick-commerce platform. Work on high-throughput, low-latency systems.",
    responsibilities: [
      "Design and build microservices",
      "Optimize for scale and performance",
      "Build real-time data pipelines",
      "Collaborate with cross-functional teams"
    ],
    requirements: ["Strong Java/Spring Boot experience", "Distributed systems knowledge", "Event-driven architecture experience", "Cloud platform experience"],
    aiReason: "Excellent match for your backend and Java skills",
  },
  {
    id: 8, title: "Product Manager", company: "CRED", logo: "⚪",
    location: "Bangalore", type: "Full-time", category: "Product",
    salary: "₹30–50 LPA", experience: "4+ years", posted: "6 days ago",
    skills: ["Product Strategy", "Data Analysis", "User Research", "Roadmapping", "SQL"],
    description: "Define the vision and roadmap for CRED's financial products. Work closely with design, engineering, and business teams.",
    responsibilities: [
      "Define product vision and strategy",
      "Own product roadmap and prioritization",
      "Conduct market research and competitive analysis",
      "Define and track success metrics"
    ],
    requirements: ["4+ years of product management", "Strong analytical skills", "Experience in fintech preferred", "Excellent communication"],
    aiReason: "Your product sense and analytical skills make you a great fit",
  },
  {
    id: 9, title: "iOS Developer", company: "PhonePe", logo: "💜",
    location: "Bangalore", type: "Full-time", category: "Engineering",
    salary: "₹22–38 LPA", experience: "3+ years", posted: "3 days ago",
    skills: ["Swift", "Xcode", "UIKit", "SwiftUI", "Core Data", "REST APIs"],
    description: "Build high-quality iOS experiences for 400M+ PhonePe users. You'll work on features that touch everyday financial transactions.",
    responsibilities: [
      "Develop and maintain iOS applications",
      "Ensure app performance and reliability",
      "Collaborate with UX designers",
      "Write unit and integration tests"
    ],
    requirements: ["3+ years of iOS development", "Proficient in Swift", "Understanding of App Store guidelines", "Experience with payment apps preferred"],
    aiReason: "Your Swift and iOS expertise align well with this role",
  },
  {
    id: 10, title: "UI/UX Designer", company: "Meesho", logo: "🟡",
    location: "Bangalore", type: "Full-time", category: "Design",
    salary: "₹15–28 LPA", experience: "2+ years", posted: "1 week ago",
    skills: ["Figma", "UX Research", "Wireframing", "Prototyping", "Adobe XD"],
    description: "Design delightful experiences for India's next billion internet users. Help shape Meesho's visual identity and user journey.",
    responsibilities: [
      "Create user flows, wireframes, and prototypes",
      "Conduct user research and testing",
      "Maintain and evolve design systems",
      "Work closely with product and engineering"
    ],
    requirements: ["2+ years of UI/UX experience", "Figma proficiency", "Mobile-first design experience", "Strong portfolio"],
    aiReason: "Your UX and design skills are perfectly suited for this role",
  },
  {
    id: 11, title: "Android Developer", company: "Paytm", logo: "🔵",
    location: "Noida", type: "Full-time", category: "Engineering",
    salary: "₹18–32 LPA", experience: "2+ years", posted: "5 days ago",
    skills: ["Kotlin", "Java", "Android SDK", "Jetpack Compose", "MVVM", "Retrofit"],
    description: "Work on Paytm's massive Android app used by 300M+ users. Build features for payments, commerce, and financial services.",
    responsibilities: [
      "Develop Android features end-to-end",
      "Optimize app performance and memory",
      "Write comprehensive tests",
      "Participate in architecture decisions"
    ],
    requirements: ["2+ years Android development", "Kotlin expertise", "Experience with Jetpack libraries", "Understanding of payment flows preferred"],
    aiReason: "Your Android and Kotlin skills are a strong match",
  },
  {
    id: 12, title: "Marketing Manager", company: "Nykaa", logo: "🌸",
    location: "Mumbai", type: "Full-time", category: "Marketing",
    salary: "₹18–30 LPA", experience: "3+ years", posted: "1 week ago",
    skills: ["Digital Marketing", "SEO", "Content Strategy", "Analytics", "Social Media"],
    description: "Lead marketing campaigns for India's leading beauty e-commerce platform. Drive user acquisition and brand awareness.",
    responsibilities: [
      "Plan and execute digital marketing campaigns",
      "Manage social media and content strategy",
      "Analyze campaign performance",
      "Collaborate with influencer marketing team"
    ],
    requirements: ["3+ years in digital marketing", "Strong analytical skills", "Experience in e-commerce", "Creative thinking"],
    aiReason: "Your marketing and analytics skills match this opportunity well",
  },
];

// ==================== AI REASONS ==================== 
const AI_REASONS = [
  "Matches your React/TypeScript skills and frontend background",
  "Aligns with your Python and data science expertise",
  "Perfect for your problem-solving and backend skills",
  "Your cloud experience makes you an ideal candidate",
  "Matches your communication and leadership skills",
  "Your open source contributions stand out for this role",
  "Based on your recent activity and job search patterns",
  "Top companies in this space are actively hiring",
];

// ==================== INIT ====================
document.addEventListener('DOMContentLoaded', () => {
  state.jobs = JOBS_DATA;
  state.filteredJobs = [...JOBS_DATA];
  initParticles();
  renderJobs();
  renderAIRecommendations();
  updateStats();
  updateBadges();
  renderKanban();

  // Load saved state from localStorage
  loadSavedState();
});

// ==================== PARTICLES ====================
function initParticles() {
  const container = document.getElementById('bgParticles');
  for (let i = 0; i < 18; i++) {
    const p = document.createElement('div');
    p.className = 'particle';
    const size = Math.random() * 200 + 50;
    p.style.cssText = `
      width: ${size}px;
      height: ${size}px;
      left: ${Math.random() * 100}%;
      animation-duration: ${Math.random() * 20 + 15}s;
      animation-delay: ${Math.random() * 15}s;
      background: ${Math.random() > 0.5 ? '#6366f1' : '#a855f7'};
    `;
    container.appendChild(p);
  }
}

// ==================== SECTION NAVIGATION ====================
function showSection(name) {
  // Hide all sections
  document.querySelectorAll('.content-section').forEach(s => s.classList.remove('active'));
  // Deactivate all nav items
  document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
  // Show target section
  document.getElementById('section-' + name).classList.add('active');
  document.getElementById('nav-' + name).classList.add('active');

  // Update page title
  const titles = {
    dashboard: 'Dashboard',
    jobs: 'Job Listings',
    tracker: 'Apply Tracker',
    resume: 'Resume & Match',
    ai: 'AI Recommendations'
  };
  document.getElementById('pageTitle').textContent = titles[name] || name;

  state.activeSection = name;

  // Close sidebar on mobile
  if (window.innerWidth <= 900) {
    document.getElementById('sidebar').classList.remove('open');
  }

  // Refresh AI on section open
  if (name === 'ai') renderAIRecommendations();
}

// ==================== SIDEBAR TOGGLE ====================
function toggleSidebar() {
  document.getElementById('sidebar').classList.toggle('open');
}

// ==================== THEME TOGGLE ====================
function toggleTheme() {
  state.theme = state.theme === 'dark' ? 'light' : 'dark';
  document.documentElement.setAttribute('data-theme', state.theme);
  const icon = document.getElementById('themeIcon');
  if (state.theme === 'light') {
    icon.innerHTML = `<path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/>`;
  } else {
    icon.innerHTML = `<circle cx="12" cy="12" r="5"/><line x1="12" y1="1" x2="12" y2="3"/><line x1="12" y1="21" x2="12" y2="23"/><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/><line x1="1" y1="12" x2="3" y2="12"/><line x1="21" y1="12" x2="23" y2="12"/><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/>`;
  }
  localStorage.setItem('jobai_theme', state.theme);
}

// ==================== RENDER JOBS ====================
function renderJobs(jobs = state.filteredJobs) {
  const grid = document.getElementById('jobsGrid');
  const countEl = document.getElementById('jobsCount');
  document.getElementById('jobsBadge').textContent = jobs.length;
  countEl.textContent = `Showing ${jobs.length} of ${state.jobs.length} jobs`;

  if (jobs.length === 0) {
    grid.innerHTML = `<div style="grid-column:1/-1;text-align:center;padding:60px;color:var(--text-muted)"><div style="font-size:48px;margin-bottom:12px">🔍</div><p style="font-size:15px">No jobs found. Try different filters.</p></div>`;
    return;
  }

  grid.innerHTML = jobs.map(job => {
    const isApplied = state.applications[job.id] && state.applications[job.id] !== 'wishlist';
    const isSaved = state.applications[job.id] === 'wishlist';
    const matchScore = state.matchScores[job.id];
    const matchHigh = matchScore >= 80;

    return `
    <div class="job-card" id="jobcard-${job.id}" onclick="openJobModal(${job.id})">
      <div class="job-card-header">
        <div class="job-company-logo" style="background:${getCompanyBg(job.id)}">${job.logo}</div>
        <button class="job-bookmark ${isSaved ? 'saved' : ''}" id="bookmark-${job.id}"
          onclick="event.stopPropagation(); toggleSave(${job.id})"
          title="${isSaved ? 'Unsave' : 'Save job'}">
          ${isSaved ? '★' : '☆'}
        </button>
      </div>
      <div class="job-title">${job.title}</div>
      <div class="job-company">${job.company} · ${job.experience}</div>
      <div class="job-tags">
        <span class="job-tag location">📍 ${job.location}</span>
        <span class="job-tag type">${job.type}</span>
        <span class="job-tag salary">${job.salary}</span>
        ${job.skills.slice(0,2).map(s => `<span class="job-tag">${s}</span>`).join('')}
      </div>
      <div class="job-footer">
        <span class="job-posted">${job.posted}</span>
        ${matchScore ? `<span class="job-match-badge visible ${matchHigh ? 'high' : ''}">🎯 ${matchScore}% match</span>` : ''}
        <button class="apply-btn-card ${isApplied ? 'applied' : ''}"
          onclick="event.stopPropagation(); quickApply(${job.id})"
          id="applybtn-${job.id}">
          ${isApplied ? '✓ Applied' : 'Apply →'}
        </button>
      </div>
    </div>
  `}).join('');

  updateDashboard();
}

function getCompanyBg(id) {
  const bgs = [
    'rgba(99,102,241,0.15)', 'rgba(168,85,247,0.15)', 'rgba(236,72,153,0.15)',
    'rgba(245,158,11,0.15)', 'rgba(16,185,129,0.15)', 'rgba(59,130,246,0.15)',
    'rgba(239,68,68,0.15)', 'rgba(34,197,94,0.15)', 'rgba(14,165,233,0.15)',
    'rgba(251,146,60,0.15)', 'rgba(147,51,234,0.15)', 'rgba(244,63,94,0.15)',
  ];
  return bgs[(id - 1) % bgs.length];
}

// ==================== FILTER JOBS ====================
function filterJobs() {
  const category = document.getElementById('filterCategory').value;
  const location = document.getElementById('filterLocation').value;
  const type = document.getElementById('filterType').value;
  const search = document.getElementById('jobSearch').value.toLowerCase().trim();

  state.filteredJobs = state.jobs.filter(job => {
    if (category && job.category !== category) return false;
    if (location && !job.location.includes(location)) return false;
    if (type && job.type !== type) return false;
    if (search) {
      const haystack = `${job.title} ${job.company} ${job.skills.join(' ')} ${job.description}`.toLowerCase();
      if (!haystack.includes(search)) return false;
    }
    return true;
  });

  renderJobs();
}

// ==================== APPLY / SAVE ====================
function quickApply(jobId) {
  const job = state.jobs.find(j => j.id === jobId);
  if (!job) return;

  if (state.applications[jobId] && state.applications[jobId] !== 'wishlist') {
    showToast(`Already applied to ${job.title}`, 'info');
    return;
  }

  state.applications[jobId] = 'applied';
  saveState();
  renderJobs(state.filteredJobs);
  renderKanban();
  updateStats();
  updateBadges();
  showToast(`Applied to ${job.title} at ${job.company}! 🎉`, 'success');
  updateDashboard();
}

function toggleSave(jobId) {
  const job = state.jobs.find(j => j.id === jobId);
  if (state.applications[jobId] === 'wishlist') {
    delete state.applications[jobId];
    showToast(`Removed from wishlist`, 'info');
  } else if (!state.applications[jobId]) {
    state.applications[jobId] = 'wishlist';
    showToast(`Saved ${job.title} to wishlist ★`, 'success');
  }
  saveState();
  renderJobs(state.filteredJobs);
  renderKanban();
  updateBadges();
  updateDashboard();
}

// ==================== JOB MODAL ====================
function openJobModal(jobId) {
  const job = state.jobs.find(j => j.id === jobId);
  if (!job) return;

  const isApplied = state.applications[jobId] && state.applications[jobId] !== 'wishlist';
  const isSaved = state.applications[jobId] === 'wishlist';
  const matchScore = state.matchScores[jobId];

  document.getElementById('modalContent').innerHTML = `
    <div class="modal-header">
      <div class="modal-logo" style="background:${getCompanyBg(job.id)}">${job.logo}</div>
      <div>
        <div class="modal-job-title">${job.title}</div>
        <div class="modal-company">${job.company} · ${job.experience} experience</div>
        ${matchScore ? `<div style="margin-top:8px"><span class="job-match-badge visible ${matchScore >= 80 ? 'high' : ''}" style="display:inline-block">🎯 ${matchScore}% AI Match</span></div>` : ''}
      </div>
    </div>

    <div class="modal-tags">
      <span class="job-tag location">📍 ${job.location}</span>
      <span class="job-tag type">${job.type}</span>
      <span class="job-tag salary">${job.salary}</span>
      <span class="job-tag">${job.category}</span>
    </div>

    <div class="modal-section">
      <h4>About the Role</h4>
      <p>${job.description}</p>
    </div>

    <div class="modal-section">
      <h4>Responsibilities</h4>
      <ul>${job.responsibilities.map(r => `<li>${r}</li>`).join('')}</ul>
    </div>

    <div class="modal-section">
      <h4>Requirements</h4>
      <ul>${job.requirements.map(r => `<li>${r}</li>`).join('')}</ul>
    </div>

    <div class="modal-section">
      <h4>Skills</h4>
      <div class="job-tags">${job.skills.map(s => `<span class="job-tag">${s}</span>`).join('')}</div>
    </div>

    <div class="modal-actions">
      <button class="btn btn-primary" onclick="applyFromModal(${job.id})" id="modalApplyBtn" ${isApplied ? 'disabled style="opacity:0.6;cursor:not-allowed"' : ''}>
        ${isApplied ? '✓ Applied' : '🚀 Apply Now'}
      </button>
      <button class="btn btn-outline" onclick="toggleSaveModal(${job.id})" id="modalSaveBtn">
        ${isSaved ? '★ Saved' : '☆ Save Job'}
      </button>
      <button class="btn btn-outline btn-sm" onclick="changeStatus(${job.id})" style="margin-left:auto">
        📋 Update Status
      </button>
    </div>
  `;

  document.getElementById('jobModal').classList.add('open');
  document.body.style.overflow = 'hidden';
}

function applyFromModal(jobId) {
  quickApply(jobId);
  const btn = document.getElementById('modalApplyBtn');
  if (btn) {
    btn.textContent = '✓ Applied';
    btn.disabled = true;
    btn.style.opacity = '0.6';
    btn.style.cursor = 'not-allowed';
  }
}

function toggleSaveModal(jobId) {
  toggleSave(jobId);
  const btn = document.getElementById('modalSaveBtn');
  if (btn) {
    const isSaved = state.applications[jobId] === 'wishlist';
    btn.textContent = isSaved ? '★ Saved' : '☆ Save Job';
  }
}

function changeStatus(jobId) {
  const statuses = ['wishlist', 'applied', 'interview', 'offer', 'rejected'];
  const current = state.applications[jobId] || 'none';
  const labels = { wishlist:'💜 Wishlist', applied:'🔵 Applied', interview:'🟡 Interview', offer:'🟢 Offer', rejected:'🔴 Rejected' };

  const job = state.jobs.find(j => j.id === jobId);
  const statusHtml = statuses.map(s => `
    <button class="btn btn-outline btn-sm" style="margin:4px;${current===s?'border-color:var(--accent);background:rgba(99,102,241,0.1)':''}"
      onclick="setStatus(${jobId},'${s}')">
      ${labels[s]}
    </button>
  `).join('');

  // Show mini status picker inline in modal
  const actionsEl = document.querySelector('.modal-actions');
  const picker = document.createElement('div');
  picker.id = 'statusPicker';
  picker.style.cssText = 'padding:12px 0;border-top:1px solid var(--border);margin-top:12px;grid-column:1/-1;';
  picker.innerHTML = `<p style="font-size:12px;color:var(--text-muted);margin-bottom:8px;">Select status:</p>${statusHtml}`;

  const existing = document.getElementById('statusPicker');
  if (existing) existing.remove();
  actionsEl.insertAdjacentElement('afterend', picker);
}

function setStatus(jobId, status) {
  const job = state.jobs.find(j => j.id === jobId);
  state.applications[jobId] = status;
  saveState();
  renderKanban();
  updateStats();
  updateBadges();
  updateDashboard();
  renderJobs(state.filteredJobs);
  showToast(`${job.title} moved to ${status}`, 'success');
  const picker = document.getElementById('statusPicker');
  if (picker) picker.remove();
}

function closeModal(e) {
  if (e.target === document.getElementById('jobModal')) closeJobModal();
}
function closeJobModal() {
  document.getElementById('jobModal').classList.remove('open');
  document.body.style.overflow = '';
}

// ==================== KANBAN ====================
function renderKanban() {
  const statuses = ['wishlist', 'applied', 'interview', 'offer', 'rejected'];
  const colors = {
    wishlist: '#6366f1', applied: '#3b82f6', interview: '#f59e0b',
    offer: '#10b981', rejected: '#ef4444'
  };

  statuses.forEach(status => {
    const col = document.getElementById('col-' + status);
    const countEl = document.getElementById('count-' + status);
    const cards = Object.entries(state.applications)
      .filter(([, s]) => s === status)
      .map(([id]) => state.jobs.find(j => j.id === parseInt(id)))
      .filter(Boolean);

    countEl.textContent = cards.length;

    if (cards.length === 0) {
      col.innerHTML = `<div class="kanban-empty">Drop applications here</div>`;
    } else {
      col.innerHTML = cards.map(job => `
        <div class="kanban-card" onclick="openJobModal(${job.id})">
          <div class="kanban-card-title">${job.title}</div>
          <div class="kanban-card-company">${job.company}</div>
          <div class="kanban-card-footer">
            <span class="kanban-card-date">${job.posted}</span>
            <button class="kanban-remove" onclick="event.stopPropagation(); removeApplication(${job.id})" title="Remove">✕</button>
          </div>
        </div>
      `).join('');
    }
  });

  // Update tracker badge
  const total = Object.keys(state.applications).length;
  document.getElementById('trackerBadge').textContent = total;
}

function removeApplication(jobId) {
  const job = state.jobs.find(j => j.id === jobId);
  delete state.applications[jobId];
  saveState();
  renderKanban();
  renderJobs(state.filteredJobs);
  updateStats();
  updateBadges();
  updateDashboard();
  showToast(`Removed ${job.title} from tracker`, 'info');
}

// ==================== RESUME UPLOAD ====================
function handleFileUpload(event) {
  const file = event.target.files[0];
  if (!file) return;
  processResume(file);
}

function handleDragOver(e) {
  e.preventDefault();
  document.getElementById('uploadZone').classList.add('drag-over');
}

function handleDragLeave(e) {
  document.getElementById('uploadZone').classList.remove('drag-over');
}

function handleDrop(e) {
  e.preventDefault();
  document.getElementById('uploadZone').classList.remove('drag-over');
  const file = e.dataTransfer.files[0];
  if (file) processResume(file);
}

function processResume(file) {
  // Validate file type
  const allowed = ['application/pdf', 'application/msword', 
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 
    'text/plain'];
  if (!allowed.includes(file.type) && !file.name.match(/\.(pdf|doc|docx|txt)$/i)) {
    showToast('Please upload a PDF, DOC, DOCX, or TXT file', 'error');
    return;
  }

  state.resumeFile = file;
  state.resumeUploaded = true;

  // Show file info
  document.getElementById('resumeFileName').textContent = file.name;
  document.getElementById('resumeFileSize').textContent = formatFileSize(file.size);
  document.getElementById('resumeInfo').style.display = 'flex';
  document.getElementById('resumeInfo').style.flexDirection = 'column';

  // Simulate skill detection
  const allSkills = [
    'React', 'TypeScript', 'JavaScript', 'Python', 'Node.js', 'SQL',
    'AWS', 'Docker', 'Git', 'REST APIs', 'CSS', 'HTML', 'Next.js',
    'GraphQL', 'MongoDB', 'PostgreSQL', 'Figma', 'Machine Learning',
    'Data Analysis', 'Communication', 'Leadership', 'Agile/Scrum'
  ];
  state.detectedSkills = shuffleArray(allSkills).slice(0, Math.floor(Math.random() * 6) + 7);

  const skillsContainer = document.getElementById('detectedSkills');
  skillsContainer.innerHTML = '';
  state.detectedSkills.forEach((skill, i) => {
    setTimeout(() => {
      const tag = document.createElement('span');
      tag.className = 'skill-tag';
      tag.textContent = skill;
      skillsContainer.appendChild(tag);
    }, i * 80);
  });

  // Simulate AI match score computation
  showToast('Analyzing your resume...', 'info');
  simulateMatchScores();

  // Upload zone changes to success state
  document.getElementById('uploadZone').style.borderColor = 'var(--accent-green)';
  document.getElementById('uploadZone').style.background = 'rgba(16,185,129,0.05)';
  document.getElementById('uploadIconArea').innerHTML = `<div style="font-size:48px">✅</div>`;
  document.getElementById('uploadTextArea').innerHTML = `<p class="upload-title" style="color:var(--accent-green)">Resume uploaded!</p><p class="upload-sub">Click to replace</p>`;
}

function simulateMatchScores() {
  // Assign random but realistic match scores to each job
  state.jobs.forEach(job => {
    const base = 40 + Math.floor(Math.random() * 55);
    state.matchScores[job.id] = base;
  });

  // Calculate overall average
  const avg = Math.round(
    Object.values(state.matchScores).reduce((a, b) => a + b, 0) / state.jobs.length
  );

  // Animate score ring
  setTimeout(() => {
    animateScoreRing(avg);
    updateMatchedJobsList();
    renderJobs(state.filteredJobs);
    renderAIRecommendations();
    updateStats();
    showToast(`Resume analyzed! Average match score: ${avg}%`, 'success');
  }, 1500);
}

function animateScoreRing(score) {
  const circle = document.getElementById('scoreCircle');
  const text = document.getElementById('scoreText');
  const desc = document.getElementById('scoreDesc');
  const circumference = 314;
  const offset = circumference - (score / 100) * circumference;

  // Animate
  let current = 0;
  const interval = setInterval(() => {
    current = Math.min(current + 2, score);
    if (text) text.textContent = current + '%';
    const o = circumference - (current / 100) * circumference;
    if (circle) circle.style.strokeDashoffset = o;
    if (current >= score) clearInterval(interval);
  }, 20);

  if (desc) {
    if (score >= 80) desc.textContent = 'Excellent profile match! 🎉';
    else if (score >= 60) desc.textContent = 'Good match! Consider upskilling in a few areas.';
    else desc.textContent = 'Work on highlighted skills to improve your match.';
  }
}

function updateMatchedJobsList() {
  const list = document.getElementById('matchedJobsList');
  const sorted = [...state.jobs]
    .filter(j => state.matchScores[j.id])
    .sort((a, b) => state.matchScores[b.id] - state.matchScores[a.id])
    .slice(0, 8);

  list.innerHTML = sorted.map(job => `
    <div class="matched-job-item" onclick="openJobModal(${job.id})">
      <div class="mj-logo" style="background:${getCompanyBg(job.id)}">${job.logo}</div>
      <div class="mj-info">
        <div class="mj-title">${job.title}</div>
        <div class="mj-company">${job.company} · ${job.location}</div>
        <div class="mj-score-bar">
          <div class="score-bar-track">
            <div class="score-bar-fill" style="width:0%" data-width="${state.matchScores[job.id]}%"></div>
          </div>
          <span class="score-bar-label">${state.matchScores[job.id]}%</span>
        </div>
      </div>
    </div>
  `).join('');

  // Animate bars
  setTimeout(() => {
    document.querySelectorAll('.score-bar-fill').forEach(bar => {
      bar.style.width = bar.dataset.width;
    });
  }, 100);
}

function removeResume() {
  state.resumeUploaded = false;
  state.resumeFile = null;
  state.detectedSkills = [];
  state.matchScores = {};
  document.getElementById('resumeInfo').style.display = 'none';
  document.getElementById('resumeFile').value = '';
  document.getElementById('uploadZone').style.borderColor = '';
  document.getElementById('uploadZone').style.background = '';
  document.getElementById('uploadIconArea').innerHTML = `<svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/></svg>`;
  document.getElementById('uploadTextArea').innerHTML = `<p class="upload-title">Drop your resume here</p><p class="upload-sub">or click to browse — PDF, DOC, DOCX, TXT</p>`;
  document.getElementById('matchedJobsList').innerHTML = `<div class="empty-state"><div class="empty-icon">📂</div><p>Upload your resume to see matched jobs</p></div>`;
  renderJobs(state.filteredJobs);
  renderAIRecommendations();
  updateStats();
  showToast('Resume removed', 'info');
}

// ==================== AI RECOMMENDATIONS ====================
function renderAIRecommendations() {
  const grid = document.getElementById('aiGrid');

  // Sort by match score if resume uploaded, otherwise random
  let recommended;
  if (state.resumeUploaded && Object.keys(state.matchScores).length > 0) {
    recommended = [...state.jobs]
      .sort((a, b) => (state.matchScores[b.id] || 0) - (state.matchScores[a.id] || 0))
      .slice(0, 8);
  } else {
    recommended = shuffleArray([...state.jobs]).slice(0, 8);
  }

  grid.innerHTML = recommended.map((job, idx) => {
    const score = state.matchScores[job.id] || Math.floor(Math.random() * 40 + 55);
    const isApplied = state.applications[job.id] && state.applications[job.id] !== 'wishlist';
    const circumference = 2 * Math.PI * 22;
    const dashoffset = circumference - (score / 100) * circumference;
    const color = score >= 80 ? '#10b981' : score >= 60 ? '#6366f1' : '#f59e0b';

    return `
      <div class="ai-card" onclick="openJobModal(${job.id})">
        <span class="ai-reason-badge">🤖 AI Pick</span>
        <div class="ai-card-header">
          <svg class="ai-score-circle" viewBox="0 0 48 48">
            <circle cx="24" cy="24" r="22" fill="none" stroke="var(--border)" stroke-width="4"/>
            <circle cx="24" cy="24" r="22" fill="none" stroke="${color}" stroke-width="4"
              stroke-dasharray="${circumference}" stroke-dashoffset="${dashoffset}"
              stroke-linecap="round" transform="rotate(-90 24 24)"/>
            <text x="24" y="28" text-anchor="middle" fill="var(--text-primary)" font-size="10" font-weight="700">${score}%</text>
          </svg>
          <div class="ai-job-info">
            <div class="ai-job-title">${job.title}</div>
            <div class="ai-job-company">${job.logo} ${job.company}</div>
          </div>
        </div>

        <div class="ai-tags">
          <span class="job-tag location">📍 ${job.location}</span>
          <span class="job-tag salary">${job.salary}</span>
          <span class="job-tag type">${job.type}</span>
        </div>

        <div class="ai-reason">${job.aiReason || AI_REASONS[idx % AI_REASONS.length]}</div>

        <div class="ai-card-footer">
          <button class="btn btn-primary btn-sm ${isApplied ? 'applied' : ''}"
            onclick="event.stopPropagation(); quickApply(${job.id})"
            ${isApplied ? 'style="opacity:0.7;cursor:default"' : ''}>
            ${isApplied ? '✓ Applied' : '🚀 Quick Apply'}
          </button>
          <button class="btn btn-outline btn-sm" onclick="event.stopPropagation(); toggleSave(${job.id})">
            ${state.applications[job.id] === 'wishlist' ? '★' : '☆'} Save
          </button>
        </div>
      </div>
    `;
  }).join('');
}

function refreshAIRecommendations() {
  const grid = document.getElementById('aiGrid');
  grid.style.opacity = '0';
  grid.style.transform = 'translateY(10px)';
  grid.style.transition = 'all 0.3s ease';
  
  setTimeout(() => {
    renderAIRecommendations();
    grid.style.opacity = '1';
    grid.style.transform = 'translateY(0)';
    showToast('AI recommendations refreshed! 🤖', 'info');
  }, 400);
}

// ==================== STATS & DASHBOARD ====================
function updateStats() {
  const applied = Object.values(state.applications).filter(s => s !== 'wishlist').length;
  const interviews = Object.values(state.applications).filter(s => s === 'interview').length;
  const avgScore = state.resumeUploaded && Object.values(state.matchScores).length > 0
    ? Math.round(Object.values(state.matchScores).reduce((a, b) => a + b, 0) / Object.values(state.matchScores).length) + '%'
    : '–';

  animateNumber('statJobsVal', state.jobs.length);
  animateNumber('statAppliedVal', applied);
  animateNumber('statInterviewsVal', interviews);
  document.getElementById('statMatchVal').textContent = avgScore;
}

function animateNumber(id, target) {
  const el = document.getElementById(id);
  if (!el) return;
  const start = parseInt(el.textContent) || 0;
  const duration = 600;
  const step = (target - start) / (duration / 16);
  let current = start;
  const interval = setInterval(() => {
    current = Math.min(current + Math.max(step, 0.5), target);
    el.textContent = Math.round(current);
    if (Math.round(current) >= target) {
      el.textContent = target;
      clearInterval(interval);
    }
  }, 16);
}

function updateBadges() {
  const totalApps = Object.keys(state.applications).length;
  document.getElementById('trackerBadge').textContent = totalApps;
  document.getElementById('jobsBadge').textContent = state.filteredJobs.length;
}

function updateDashboard() {
  // Recent applications
  const recentEl = document.getElementById('recentActivity');
  const appliedJobs = Object.entries(state.applications)
    .filter(([, s]) => s !== 'wishlist')
    .slice(-5)
    .reverse();

  if (appliedJobs.length === 0) {
    recentEl.innerHTML = '<div class="empty-state-small"><span>No applications yet. Start applying!</span></div>';
  } else {
    const statusColors = { applied:'#3b82f6', interview:'#f59e0b', offer:'#10b981', rejected:'#ef4444' };
    recentEl.innerHTML = appliedJobs.map(([id, status]) => {
      const job = state.jobs.find(j => j.id === parseInt(id));
      if (!job) return '';
      return `
        <div class="activity-item">
          <div class="activity-dot" style="background:${statusColors[status] || '#6366f1'}"></div>
          <div class="activity-info">
            <div class="activity-title">${job.title}</div>
            <div class="activity-sub">${job.company} · ${job.posted}</div>
          </div>
          <span class="activity-status" style="background:${statusColors[status]}22;color:${statusColors[status]}">
            ${status.charAt(0).toUpperCase() + status.slice(1)}
          </span>
        </div>
      `;
    }).join('');
  }

  // Top matches
  const matchesEl = document.getElementById('topMatches');
  if (!state.resumeUploaded || Object.keys(state.matchScores).length === 0) {
    matchesEl.innerHTML = '<div class="empty-state-small"><span>Upload resume to see matches</span></div>';
  } else {
    const topJobs = [...state.jobs]
      .sort((a, b) => (state.matchScores[b.id] || 0) - (state.matchScores[a.id] || 0))
      .slice(0, 4);
    matchesEl.innerHTML = topJobs.map(job => `
      <div class="match-item" onclick="openJobModal(${job.id})">
        <div class="match-company-logo" style="background:${getCompanyBg(job.id)}">${job.logo}</div>
        <div class="match-info">
          <div class="match-title">${job.title}</div>
          <div class="match-company">${job.company}</div>
        </div>
        <span class="match-score-pill">🎯 ${state.matchScores[job.id]}%</span>
      </div>
    `).join('');
  }
}

// ==================== UTILS ====================
function formatFileSize(bytes) {
  if (bytes < 1024) return bytes + ' B';
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
}

function shuffleArray(arr) {
  const a = [...arr];
  for (let i = a.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [a[i], a[j]] = [a[j], a[i]];
  }
  return a;
}

function showToast(message, type = 'info') {
  const toast = document.getElementById('toast');
  const icons = { success: '✅', error: '❌', info: 'ℹ️' };
  toast.innerHTML = `<span>${icons[type]}</span><span>${message}</span>`;
  toast.className = `toast show ${type}`;
  clearTimeout(window._toastTimeout);
  window._toastTimeout = setTimeout(() => {
    toast.classList.remove('show');
  }, 3500);
}

// ==================== PERSISTENCE ====================
function saveState() {
  try {
    localStorage.setItem('jobai_applications', JSON.stringify(state.applications));
    localStorage.setItem('jobai_matchScores', JSON.stringify(state.matchScores));
  } catch(e) {}
}

function loadSavedState() {
  try {
    const apps = localStorage.getItem('jobai_applications');
    if (apps) state.applications = JSON.parse(apps);
    
    const scores = localStorage.getItem('jobai_matchScores');
    if (scores) {
      state.matchScores = JSON.parse(scores);
      state.resumeUploaded = Object.keys(state.matchScores).length > 0;
      if (state.resumeUploaded) {
        const avg = Math.round(Object.values(state.matchScores).reduce((a,b)=>a+b,0)/Object.values(state.matchScores).length);
        animateScoreRing(avg);
        updateMatchedJobsList();
      }
    }

    const theme = localStorage.getItem('jobai_theme');
    if (theme) {
      state.theme = theme;
      document.documentElement.setAttribute('data-theme', theme);
    }

    renderJobs();
    renderKanban();
    renderAIRecommendations();
    updateStats();
    updateBadges();
    updateDashboard();
  } catch(e) {}
}

// ==================== KEYBOARD SHORTCUTS ====================
document.addEventListener('keydown', (e) => {
  if (e.key === 'Escape') closeJobModal();
  if (e.ctrlKey || e.metaKey) {
    const shortcuts = { '1':'dashboard', '2':'jobs', '3':'tracker', '4':'resume', '5':'ai' };
    if (shortcuts[e.key]) { e.preventDefault(); showSection(shortcuts[e.key]); }
  }
});

// Close sidebar on outside click (mobile)
document.addEventListener('click', (e) => {
  const sidebar = document.getElementById('sidebar');
  const toggle = document.getElementById('menuToggle');
  if (window.innerWidth <= 900 && sidebar.classList.contains('open') &&
      !sidebar.contains(e.target) && !toggle.contains(e.target)) {
    sidebar.classList.remove('open');
  }
});
