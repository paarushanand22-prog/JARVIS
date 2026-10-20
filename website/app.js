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

async function executeCustomCommand() {
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

  // 1. Check for Exclusive Desktop Action Features (simulated tool execution demo)
  if (low.includes('screen') || low.includes('look') || low.includes('see') || low.includes('window')) {
    const actRow = document.createElement('div');
    actRow.className = 'log-row action';
    actRow.innerHTML = `<span>⚡ Executing Tool: analyze_screen(query="Analyze active window and content")</span>`;
    terminalBody.appendChild(actRow);
    terminalBody.scrollTop = terminalBody.scrollHeight;

    setTimeout(() => {
      const botRow = document.createElement('div');
      botRow.className = 'log-row bot';
      botRow.innerHTML = `<span>🤖 JARVIS: "Yes sir, on your active screen I can see your browser is open on the JARVIS official website, with the interactive terminal running smoothly."</span>`;
      terminalBody.appendChild(botRow);
      terminalBody.scrollTop = terminalBody.scrollHeight;
    }, 500);
    return;
  }

  if (low.includes('ppt') || low.includes('presentation') || low.includes('slide')) {
    const topic = val.replace(/create|presentation|ppt|slide/gi, '').trim() || 'Modern AI';
    const actRow = document.createElement('div');
    actRow.className = 'log-row action';
    actRow.innerHTML = `<span>⚡ Executing Tool: create_presentation(topic="${topic}")</span>`;
    terminalBody.appendChild(actRow);
    terminalBody.scrollTop = terminalBody.scrollHeight;

    setTimeout(() => {
      const botRow = document.createElement('div');
      botRow.className = 'log-row bot';
      botRow.innerHTML = `<span>🤖 JARVIS: "Right away sir. Generating a formatted PowerPoint presentation deck on '${topic}' and launching Microsoft PowerPoint for you."</span>`;
      terminalBody.appendChild(botRow);
      terminalBody.scrollTop = terminalBody.scrollHeight;
    }, 500);
    return;
  }

  if (low.includes('click') || low.includes('open') || low.includes('launch')) {
    const app = val.replace(/open|launch|click/gi, '').trim() || 'target';
    const actRow = document.createElement('div');
    actRow.className = 'log-row action';
    actRow.innerHTML = `<span>⚡ Executing Tool: open_application(app_name="${app}")</span>`;
    terminalBody.appendChild(actRow);
    terminalBody.scrollTop = terminalBody.scrollHeight;

    setTimeout(() => {
      const botRow = document.createElement('div');
      botRow.className = 'log-row bot';
      botRow.innerHTML = `<span>🤖 JARVIS: "Command received sir. Opening ${app} and locating coordinates on your display."</span>`;
      terminalBody.appendChild(botRow);
      terminalBody.scrollTop = terminalBody.scrollHeight;
    }, 450);
    return;
  }

  if (low.includes('find') || low.includes('search') || low.includes('file')) {
    const actRow = document.createElement('div');
    actRow.className = 'log-row action';
    actRow.innerHTML = `<span>⚡ Executing Tool: search_computer_files(query="user files")</span>`;
    terminalBody.appendChild(actRow);
    terminalBody.scrollTop = terminalBody.scrollHeight;

    setTimeout(() => {
      const botRow = document.createElement('div');
      botRow.className = 'log-row bot';
      botRow.innerHTML = `<span>🤖 JARVIS: "Scanned all drives in 280ms. Target file found and ready to open upon your command, sir."</span>`;
      terminalBody.appendChild(botRow);
      terminalBody.scrollTop = terminalBody.scrollHeight;
    }, 450);
    return;
  }

  // 2. Math Calculations
  const mathMatch = val.match(/^(?:what\s+is\s+|calculate\s+|solve\s+)?([0-9\s\+\-\*\/\^\.\(\)]+)$/i);
  if (mathMatch && mathMatch[1] && /[0-9]/.test(mathMatch[1]) && /[\+\-\*\/]/.test(mathMatch[1])) {
    try {
      const calculated = Function(`'use strict'; return (${mathMatch[1]})`)();
      if (!isNaN(calculated)) {
        const botRow = document.createElement('div');
        botRow.className = 'log-row bot';
        botRow.innerHTML = `<span>🤖 JARVIS: "The answer is ${calculated}, sir."</span>`;
        terminalBody.appendChild(botRow);
        terminalBody.scrollTop = terminalBody.scrollHeight;
        return;
      }
    } catch (e) {}
  }

  // 3. Real Instant Answer for ANY user question!
  const thinkingRow = document.createElement('div');
  thinkingRow.className = 'log-row sys';
  thinkingRow.innerHTML = `<span>[NEURAL CORE] Analyzing question...</span>`;
  terminalBody.appendChild(thinkingRow);
  terminalBody.scrollTop = terminalBody.scrollHeight;

  try {
    let answer = '';

    // Step A: Clean search query by removing question prefixes
    const cleanQuery = val.replace(/^(what is|who is|what are|explain|tell me about|define|describe|why is|how does)\s+/i, '').replace(/['"?\.]+/g, '').trim();

    // Step B: Query Wikipedia Search + Page Summary REST API (Fast, Reliable, Zero Auth, Full CORS)
    try {
      const searchUrl = `https://en.wikipedia.org/w/api.php?action=opensearch&search=${encodeURIComponent(cleanQuery || val)}&limit=1&format=json&origin=*`;
      const searchRes = await fetch(searchUrl);
      const searchData = await searchRes.json();
      const bestTitle = (searchData && searchData[1] && searchData[1][0]) ? searchData[1][0] : cleanQuery;

      if (bestTitle) {
        const summaryUrl = `https://en.wikipedia.org/api/rest_v1/page/summary/${encodeURIComponent(bestTitle.replace(/\s+/g, '_'))}`;
        const sumRes = await fetch(summaryUrl);
        if (sumRes.ok) {
          const sumData = await sumRes.json();
          if (sumData && sumData.extract) {
            // Pick first 2 sentences for a crisp, direct answer
            const sentences = sumData.extract.split(/(?<=[.!?])\s+/).slice(0, 2).join(' ');
            answer = `Sir, ${sentences}`;
          }
        }
      }
    } catch (e) {
      console.warn('Wiki query error:', e);
    }

    // Step C: Try in-browser AI provider if available
    if (!answer && window.puter && window.puter.ai) {
      try {
        const aiPrompt = `Answer this question in 2 polite, concise sentences as JARVIS: "${val}"`;
        const res = await puter.ai.chat(aiPrompt);
        if (res) answer = res.toString().trim();
      } catch (e) {}
    }

    if (!answer) {
      answer = `Sir, I have processed '${val}'. To interact directly with open apps and execute live desktop tasks on this topic, use the full JARVIS Commercial Edition.`;
    }

    thinkingRow.remove();
    const botRow = document.createElement('div');
    botRow.className = 'log-row bot';
    botRow.innerHTML = `<span>🤖 JARVIS: "${answer}"</span>`;
    terminalBody.appendChild(botRow);
    terminalBody.scrollTop = terminalBody.scrollHeight;

  } catch (err) {
    thinkingRow.remove();
    const botRow = document.createElement('div');
    botRow.className = 'log-row bot';
    botRow.innerHTML = `<span>🤖 JARVIS: "Standing by to assist you, sir. How else may I help?"</span>`;
    terminalBody.appendChild(botRow);
    terminalBody.scrollTop = terminalBody.scrollHeight;
  }
}
