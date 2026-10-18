// Cyber Particle Network Canvas Animation
const canvas = document.getElementById('bg-canvas');
const ctx = canvas.getContext('2d');

let particles = [];
const particleCount = 45;

function resizeCanvas() {
  canvas.width = window.innerWidth;
  canvas.height = window.innerHeight;
}
window.addEventListener('resize', resizeCanvas);
resizeCanvas();

class Particle {
  constructor() {
    this.x = Math.random() * canvas.width;
    this.y = Math.random() * canvas.height;
    this.vx = (Math.random() - 0.5) * 0.6;
    this.vy = (Math.random() - 0.5) * 0.6;
    this.radius = Math.random() * 2 + 1;
  }

  update() {
    this.x += this.vx;
    this.y += this.vy;

    if (this.x < 0 || this.x > canvas.width) this.vx *= -1;
    if (this.y < 0 || this.y > canvas.height) this.vy *= -1;
  }

  draw() {
    ctx.beginPath();
    ctx.arc(this.x, this.y, this.radius, 0, Math.PI * 2);
    ctx.fillStyle = 'rgba(0, 240, 255, 0.4)';
    ctx.fill();
  }
}

for (let i = 0; i < particleCount; i++) {
  particles.push(new Particle());
}

function animateParticles() {
  ctx.clearRect(0, 0, canvas.width, canvas.height);

  for (let i = 0; i < particles.length; i++) {
    particles[i].update();
    particles[i].draw();

    for (let j = i + 1; j < particles.length; j++) {
      const dx = particles[i].x - particles[j].x;
      const dy = particles[i].y - particles[j].y;
      const dist = Math.sqrt(dx * dx + dy * dy);

      if (dist < 150) {
        ctx.beginPath();
        ctx.moveTo(particles[i].x, particles[i].y);
        ctx.lineTo(particles[j].x, particles[j].y);
        ctx.strokeStyle = `rgba(0, 240, 255, ${0.15 * (1 - dist / 150)})`;
        ctx.lineWidth = 1;
        ctx.stroke();
      }
    }
  }

  requestAnimationFrame(animateParticles);
}
animateParticles();

// Interactive Terminal Simulator
const terminalBody = document.getElementById('terminal-body');

const scenarios = {
  create_ppt: [
    { type: 'user', text: '🗣️ You: "Jarvis open PowerPoint and create a presentation on Big Bang"' },
    { type: 'action', text: '⚡ Executing Tool: create_presentation(topic="Big Bang", slide_count=5)' },
    { type: 'sys', text: '[INFO] Generating slides: Title, Inflation, CMB Radiation, Modern Evidence...' },
    { type: 'bot', text: '🤖 JARVIS: "Ji sir, maine Big Bang par 5 slides ki complete PowerPoint presentation create kar di hai aur PowerPoint open kar diya hai!"' }
  ],
  click_settings: [
    { type: 'user', text: '🗣️ You: "Jarvis, screen par Settings option par click karo"' },
    { type: 'action', text: '⚡ Executing Tool: click_option(target_name="Settings")' },
    { type: 'sys', text: '[VISION OCR] Scanning active display (1920x1080)... Target found at (520, 380).' },
    { type: 'bot', text: '🤖 JARVIS: "Settings option located on your display. Mouse cursor moved and clicked successfully."' }
  ],
  analyze_screen: [
    { type: 'user', text: '🗣️ You: "Jarvis, look at my screen and tell me what is open"' },
    { type: 'action', text: '⚡ Executing Tool: analyze_screen(query="What is currently active?")' },
    { type: 'sys', text: '[LLaVA VISION] Analyzing active frame... Terminal and Visual Studio Code detected.' },
    { type: 'bot', text: '🤖 JARVIS: "On your screen, you currently have Visual Studio Code open with the JARVIS project files, and a PowerShell terminal compiling the binary."' }
  ],
  find_files: [
    { type: 'user', text: '🗣️ You: "Jarvis, find my resume file on the computer"' },
    { type: 'action', text: '⚡ Executing Tool: search_computer_files(query="resume")' },
    { type: 'sys', text: '[INDEXER] Searched C:\\Users\\loq\\Documents and Desktop in 340ms.' },
    { type: 'bot', text: '🤖 JARVIS: "Found 2 files: Resume_2026.docx on your Desktop, and Software_Resume.pdf in Documents. Would you like me to open one?"' }
  ]
};

let isSimulating = false;

function simulateCommand(key) {
  if (isSimulating) return;
  const script = scenarios[key];
  if (!script) return;

  isSimulating = true;

  script.forEach((step, index) => {
    setTimeout(() => {
      const row = document.createElement('div');
      row.className = `log-row ${step.type}`;
      row.innerHTML = `<span>${step.text}</span>`;
      terminalBody.appendChild(row);
      terminalBody.scrollTop = terminalBody.scrollHeight;

      if (index === script.length - 1) {
        isSimulating = false;
      }
    }, (index + 1) * 600);
  });
}
