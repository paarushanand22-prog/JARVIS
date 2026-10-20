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

function executeCustomCommand() {
  const inputEl = document.getElementById('terminal-custom-input');
  if (!inputEl) return;
  const val = inputEl.value.trim();
  if (!val) return;

  inputEl.value = '';

  // Add user row immediately
  const userRow = document.createElement('div');
  userRow.className = 'log-row user';
  userRow.innerHTML = `<span>🗣️ You: "${val}"</span>`;
  terminalBody.appendChild(userRow);
  terminalBody.scrollTop = terminalBody.scrollHeight;

  const low = val.toLowerCase();

  setTimeout(() => {
    let toolAction = null;
    let botReply = '';

    // Mathematical calculation evaluation
    const mathMatch = val.match(/^(?:what\s+is\s+|calculate\s+|solve\s+)?([0-9\s\+\-\*\/\^\.\(\)]+)$/i);
    let calculated = null;
    if (mathMatch && mathMatch[1] && /[0-9]/.test(mathMatch[1]) && /[\+\-\*\/]/.test(mathMatch[1])) {
      try {
        calculated = Function(`'use strict'; return (${mathMatch[1]})`)();
      } catch (e) {}
    }

    if (calculated !== null && !isNaN(calculated)) {
      botReply = `🤖 JARVIS: "The answer is ${calculated}, sir."`;
    } else if (low.includes('screen') || low.includes('look') || low.includes('see') || low.includes('window')) {
      toolAction = '⚡ Executing Tool: analyze_screen(query="Analyze active window and content")';
      botReply = '🤖 JARVIS: "Yes sir, on your active screen I can see your browser is open on the JARVIS official website, with the interactive demo running smoothly."';
    } else if (low.includes('ppt') || low.includes('presentation') || low.includes('slide')) {
      const topic = val.replace(/create|presentation|ppt|slide/gi, '').trim() || 'Modern AI';
      toolAction = `⚡ Executing Tool: create_presentation(topic="${topic}")`;
      botReply = `🤖 JARVIS: "Right away sir. Generating a formatted PowerPoint presentation deck on '${topic}' and launching Microsoft PowerPoint for you."`;
    } else if (low.includes('click') || low.includes('open') || low.includes('launch')) {
      const app = val.replace(/open|launch|click/gi, '').trim() || 'target';
      toolAction = `⚡ Executing Tool: open_application(app_name="${app}")`;
      botReply = `🤖 JARVIS: "Command received sir. Opening ${app} and locating coordinates on your display."`;
    } else if (low.includes('find') || low.includes('search') || low.includes('file')) {
      toolAction = '⚡ Executing Tool: search_computer_files(query="user files")';
      botReply = '🤖 JARVIS: "Scanned all drives in 280ms. Target file found and ready to open upon your command, sir."';
    } else if (low.includes('hi') || low.includes('hello') || low.includes('hey') || low.includes('how are you')) {
      botReply = '🤖 JARVIS: "Hello sir! I am fully operational and ready. How may I assist you with your computer today?"';
    } else if (low === 'yes' || low === 'yeah' || low === 'ok' || low === 'sure' || low === 'proceed') {
      botReply = '🤖 JARVIS: "Acknowledged, sir. Standing by for your next instruction."';
    } else if (low.includes('who are you') || low.includes('what are you')) {
      botReply = '🤖 JARVIS: "I am J.A.R.V.I.S., an autonomous desktop AI assistant running locally on Windows to control apps, analyze your screen, and automate tasks."';
    } else {
      botReply = `🤖 JARVIS: "Acknowledged sir: '${val}'. Processing instruction with local neural engine."`;
    }

    if (toolAction) {
      const actRow = document.createElement('div');
      actRow.className = 'log-row action';
      actRow.innerHTML = `<span>${toolAction}</span>`;
      terminalBody.appendChild(actRow);
      terminalBody.scrollTop = terminalBody.scrollHeight;
    }

    setTimeout(() => {
      const botRow = document.createElement('div');
      botRow.className = 'log-row bot';
      botRow.innerHTML = `<span>${botReply}</span>`;
      terminalBody.appendChild(botRow);
      terminalBody.scrollTop = terminalBody.scrollHeight;
    }, toolAction ? 450 : 150);
  }, 250);
}
