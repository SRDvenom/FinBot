const API_URL = '/api/chat';  // Now relative to current domain since we're serving from Flask

const chat = document.getElementById('chat');
const form = document.getElementById('form');
const input = document.getElementById('input');
const sendBtn = document.getElementById('sendBtn');
const clearBtn = document.getElementById('clearBtn');
const examplesBtn = document.getElementById('examplesBtn');
const examplesEl = document.getElementById('examples');

function createMessageEl({role='bot', text='', meta=''}){
  const wrap = document.createElement('div');
  wrap.className = 'message';

  const avatar = document.createElement('div');
  avatar.className = 'avatar ' + (role === 'user' ? 'user' : 'bot');
  avatar.textContent = role === 'user' ? 'You' : 'FB';

  const bubble = document.createElement('div');
  bubble.className = 'bubble ' + (role === 'user' ? 'user' : 'bot');
  bubble.innerHTML = escapeHtml(text).replace(/\n/g,'<br>');

  wrap.appendChild(avatar);
  wrap.appendChild(bubble);

  if(meta){
    const m = document.createElement('div');
    m.className = 'meta';
    m.textContent = meta;
    wrap.appendChild(m);
  }
  return wrap;
}

function escapeHtml(unsafe) {
  return unsafe
       .replace(/&/g, "&amp;")
       .replace(/</g, "&lt;")
       .replace(/>/g, "&gt;")
       .replace(/"/g, "&quot;")
       .replace(/'/g, "&#039;");
}

function appendMessage(obj){
  const el = createMessageEl(obj);
  chat.appendChild(el);
  chat.scrollTop = chat.scrollHeight - chat.clientHeight;
}

function setTyping(on){
  const id = 'typing-indicator';
  let existing = document.getElementById(id);
  if(on){
    if(!existing){
      const el = createMessageEl({role:'bot', text:'Typing...', meta:'',});
      el.id = id;
      el.querySelector('.bubble').classList.add('typing');
      chat.appendChild(el);
      chat.scrollTop = chat.scrollHeight;
    }
  } else {
    if(existing) existing.remove();
  }
}

async function sendMessage(message){
  appendMessage({role:'user', text:message});
  input.value = '';
  setTyping(true);

  try{
    const res = await fetch(API_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message })
    });

    if(!res.ok){
      throw new Error(`Server error ${res.status}`);
    }

    const data = await res.json();
    setTyping(false);
    if(data && data.response){
      appendMessage({role:'bot', text:data.response});
    } else if(data && data.error){
      appendMessage({role:'bot', text:'Error: ' + data.error});
    } else {
      appendMessage({role:'bot', text:'No response from server.'});
    }
  }catch(err){
    setTyping(false);
    appendMessage({role:'bot', text:'Network or server error: ' + err.message});
  }
}

form.addEventListener('submit', (e)=>{
  e.preventDefault();
  const text = input.value.trim();
  if(!text) return;
  sendMessage(text);
});

input.addEventListener('keydown', (e)=>{
  if(e.key === 'Enter' && !e.shiftKey){
    e.preventDefault();
    form.requestSubmit();
  }
});

clearBtn.addEventListener('click', ()=>{
  chat.innerHTML = '';
});

examplesBtn.addEventListener('click', ()=>{
  examplesEl.classList.toggle('hidden');
});

document.querySelectorAll('.examples .example').forEach(btn=>{
  btn.addEventListener('click', ()=>{
    const q = btn.textContent.trim();
    input.value = q;
    input.focus();
  });
});

// Small UX: prefill with a friendly welcome message from bot
appendMessage({role:'bot', text:'Hello! I can fetch stock prices, calculate EMI/SIP, or provide general financial advice. Try an example below.'});