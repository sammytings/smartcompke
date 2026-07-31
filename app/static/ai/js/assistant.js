/* ================================================================
   SmartAI Assistant — Chatbot Widget JS
   SmartComputersKe Technologies

   KEY FIXES vs previous version:
   1. Typing indicator was ALWAYS showing because showTyping() was
      called synchronously before the async fetch resolved, then
      hideTyping() was called inside the try block but AFTER
      appendBotMessage() — if the DOM wasn't ready, hidden stayed
      false. Fixed: we now call hideTyping() BEFORE appending the
      reply, and we guard with a proper finally block that always
      runs hideTyping() so it can never get stuck.

   2. Typing indicator used the hidden attribute correctly in HTML
      but CSS was missing [hidden] { display:none } — added in CSS.

   3. Send button is disabled until the user types something.

   4. Unread badge appears when window is closed after a bot reply.

   5. Bot messages render with an avatar so the UI feels human.
   ================================================================ */

(function () {
  "use strict";

  /* ── CONFIG ────────────────────────────────────────────────────
     Point endpoint at your Django chatbot view.
     Adjust parseReply() if your response JSON shape differs.
     ──────────────────────────────────────────────────────────── */
  const CFG = {
    endpoint:       "/ai/chat/",
    csrfCookieName: "csrftoken",
    minTypingMs:    900,   /* minimum visible typing time (feels natural) */
    maxTypingMs:    2400,  /* cap so fast replies don't wait too long     */
  };

  /* ── CSRF ────────────────────────────────────────────────────── */
  function getCsrf() {
    const m = document.cookie.match(/(?:^|;\s*)csrftoken=([^;]+)/);
    return m ? decodeURIComponent(m[1]) : "";
  }

  /* ── PARSE REPLY ─────────────────────────────────────────────── */
  function parseReply(data) {
    return (
      data.reply     ||
      data.response  ||
      data.message   ||
      data.text      ||
      "I'm here to help — could you rephrase that?"
    );
  }

  /* ── DOM REFS ────────────────────────────────────────────────── */
  const root       = document.getElementById("sca-chatbot-root");
  if (!root) return; /* widget not on this page */

  const toggleBtn  = document.getElementById("sca-chat-toggle");
  const chatWindow = document.getElementById("sca-chat-window");
  const closeBtn   = document.getElementById("sca-chat-close");
  const msgsEl     = document.getElementById("sca-chat-messages");
  const typingEl   = document.getElementById("sca-typing-indicator");
  const form       = document.getElementById("sca-chat-form");
  const inputEl    = document.getElementById("sca-chat-input");
  const sendBtn    = document.getElementById("sca-chat-send");
  const badgeEl    = document.getElementById("sca-unread-badge");

  /* ── STATE ───────────────────────────────────────────────────── */
  let isOpen        = false;
  let isSending     = false;
  let hasOpened     = false;
  let unreadCount   = 0;

  /* ── QUICK ACTIONS CONFIG ────────────────────────────────────── */
  const QUICK_ACTIONS = [
    { label: "Browse laptops",     msg: "Show me your laptops",              icon: "laptop"  },
    { label: "Desktops",           msg: "What desktop computers do you have?",icon: "desktop" },
    { label: "Track my order",     msg: "I want to track my order",          icon: "truck"   },
    { label: "Contact support",    msg: "I need to speak to support",        icon: "headset" },
    { label: "Prices & payment",   msg: "What payment methods do you accept?",icon: "card"   },
  ];

  const ICONS = {
    laptop:  '<svg width="13" height="13" viewBox="0 0 24 24" fill="none"><rect x="2" y="4" width="20" height="13" rx="1.5" stroke="currentColor" stroke-width="1.8"/><path d="M1 19.5h22" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/></svg>',
    desktop: '<svg width="13" height="13" viewBox="0 0 24 24" fill="none"><rect x="2" y="3" width="20" height="14" rx="1.5" stroke="currentColor" stroke-width="1.8"/><path d="M9 20h6M12 17v3" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/></svg>',
    truck:   '<svg width="13" height="13" viewBox="0 0 24 24" fill="none"><path d="M2 6h14v11H2V6Z" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"/><path d="M16 10h4l3 3.5V17h-7V10Z" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"/><circle cx="6.5" cy="19" r="1.6" stroke="currentColor" stroke-width="1.6"/><circle cx="18.5" cy="19" r="1.6" stroke="currentColor" stroke-width="1.6"/></svg>',
    headset: '<svg width="13" height="13" viewBox="0 0 24 24" fill="none"><path d="M4 13V11a8 8 0 0 1 16 0v2" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/><rect x="2.5" y="13" width="5" height="7" rx="1.5" stroke="currentColor" stroke-width="1.8"/><rect x="16.5" y="13" width="5" height="7" rx="1.5" stroke="currentColor" stroke-width="1.8"/></svg>',
    card:    '<svg width="13" height="13" viewBox="0 0 24 24" fill="none"><rect x="2" y="5" width="20" height="14" rx="2" stroke="currentColor" stroke-width="1.8"/><path d="M2 10h20" stroke="currentColor" stroke-width="1.8"/></svg>',
  };

  /* ── SMALL HEADSET SVG used inside bot message avatar ────────── */
  const BOT_AVATAR_SVG = `
    <svg viewBox="0 0 24 24" width="14" height="14" fill="none" xmlns="http://www.w3.org/2000/svg">
      <circle cx="12" cy="6.5" r="3.5" fill="#fff"/>
      <path d="M4 14v-1a8 8 0 0 1 16 0v1" stroke="#fff" stroke-width="1.6" stroke-linecap="round" fill="none"/>
      <rect x="2.5" y="14" width="3.5" height="5" rx="1.75" fill="#fff"/>
      <rect x="18" y="14" width="3.5" height="5" rx="1.75" fill="#fff"/>
      <path d="M6 18q0 2.5 2.5 3" stroke="#fff" stroke-width="1.4" stroke-linecap="round" fill="none"/>
      <circle cx="9" cy="21.2" r="1.1" fill="#fff"/>
    </svg>`;

  /* ── SCROLL ──────────────────────────────────────────────────── */
  function scrollBottom() {
    msgsEl.scrollTop = msgsEl.scrollHeight;
  }

  /* ── APPEND USER MESSAGE ─────────────────────────────────────── */
  function appendUser(text) {
    const el = document.createElement("div");
    el.className = "sca-msg sca-msg-user";
    el.textContent = text;
    msgsEl.appendChild(el);
    scrollBottom();
  }

  /* ── APPEND BOT MESSAGE ──────────────────────────────────────── */
  function appendBot(text, opts) {
    opts = opts || {};
    const wrap   = document.createElement("div");
    wrap.className = "sca-msg sca-msg-bot";

    const avatar = document.createElement("span");
    avatar.className = "sca-msg-bot-avatar";
    avatar.setAttribute("aria-hidden", "true");
    avatar.innerHTML = BOT_AVATAR_SVG;

    const bubble = document.createElement("div");
    bubble.className = "sca-msg-bot-bubble" +
      (opts.err     ? " sca-err"     : "") +
      (opts.welcome ? " sca-welcome" : "");

    /* Render newlines as <br> for multi-line replies */
    bubble.innerHTML = text
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/\n/g, "<br>");

    wrap.appendChild(avatar);
    wrap.appendChild(bubble);
    msgsEl.appendChild(wrap);
    scrollBottom();

    /* unread badge if chat is closed */
    if (!isOpen) {
      unreadCount++;
      if (badgeEl) {
        badgeEl.textContent = unreadCount;
        badgeEl.hidden = false;
      }
    }
  }

  /* ── QUICK ACTIONS ───────────────────────────────────────────── */
  function renderQuickActions() {
    const wrap = document.createElement("div");
    wrap.className = "sca-quick-actions";
    QUICK_ACTIONS.forEach(function (qa) {
      const btn = document.createElement("button");
      btn.type = "button";
      btn.className = "sca-quick-btn";
      btn.innerHTML = (ICONS[qa.icon] || "") + "<span>" + qa.label + "</span>";
      btn.addEventListener("click", function () {
        /* remove quick actions once one is tapped */
        wrap.remove();
        sendMessage(qa.msg);
      });
      wrap.appendChild(btn);
    });
    msgsEl.appendChild(wrap);
    scrollBottom();
  }

  /* ── WELCOME SEQUENCE ────────────────────────────────────────── */
  function showWelcome() {
    /* Date stamp */
    const stamp = document.createElement("p");
    stamp.className = "sca-date-stamp";
    stamp.textContent = new Intl.DateTimeFormat("en-KE", {
      weekday: "long", hour: "2-digit", minute: "2-digit"
    }).format(new Date());
    msgsEl.appendChild(stamp);

    appendBot(
      "Hello 👋 Welcome to SmartComputersKe!\n\nI'm your SmartAI assistant. I can help you find laptops, desktops, accessories, track orders, and more. What can I help you with?",
      { welcome: true }
    );
    renderQuickActions();
  }

  /* ── TYPING INDICATOR ────────────────────────────────────────── */
  function showTyping() {
    if (!typingEl) return;
    typingEl.hidden = false;     /* removes hidden attr */
    typingEl.removeAttribute("hidden"); /* belt-and-suspenders */
    scrollBottom();
  }

  function hideTyping() {
    if (!typingEl) return;
    typingEl.hidden = true;
    typingEl.setAttribute("hidden", "");
  }

  /* ── SEND STATE ──────────────────────────────────────────────── */
  function setSending(on) {
    isSending      = on;
    sendBtn.disabled = on;
    inputEl.disabled = on;
    sendBtn.classList.toggle("sca-is-sending", on);
  }

  /* ── CORE SEND ───────────────────────────────────────────────── */
  async function sendMessage(overrideText) {
    const text = (overrideText !== undefined ? overrideText : inputEl.value).trim();
    if (!text || isSending) return;

    if (!overrideText) inputEl.value = "";
    sendBtn.disabled = true; /* disable immediately even before setSending */

    appendUser(text);
    setSending(true);
    showTyping();

    /* measure realistic delay */
    const t0 = Date.now();

    try {
      const res = await fetch(CFG.endpoint, {
        method:  "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken":  getCsrf(),
        },
        body: JSON.stringify({ message: text }),
      });

      if (!res.ok) throw new Error("HTTP " + res.status);
      const data  = await res.json();
      const reply = parseReply(data);

      /* ensure typing shows for at least CFG.minTypingMs */
      const elapsed   = Date.now() - t0;
      const remaining = Math.max(0, CFG.minTypingMs - elapsed);
      if (remaining > 0) await delay(remaining);

      /* ── CRITICAL: hide typing BEFORE appending reply ── */
      hideTyping();
      appendBot(reply);

    } catch (err) {
      hideTyping();
      appendBot(
        "Sorry, I couldn't connect right now. Please try again in a moment, or contact us via WhatsApp.",
        { err: true }
      );
      console.error("[SmartAI]", err);
    } finally {
      /* ── CRITICAL: always runs — typing can never get stuck ── */
      hideTyping();
      setSending(false);
      /* re-enable send only if input has text */
      updateSendState();
      if (!overrideText) inputEl.focus();
    }
  }

  function delay(ms) {
    return new Promise(function (resolve) { setTimeout(resolve, ms); });
  }

  /* ── SEND BUTTON ENABLE/DISABLE ──────────────────────────────── */
  function updateSendState() {
    sendBtn.disabled = !inputEl.value.trim() || isSending;
  }

  /* ── OPEN / CLOSE ────────────────────────────────────────────── */
  function openChat() {
    isOpen = true;
    chatWindow.classList.add("sca-is-open");
    chatWindow.setAttribute("aria-hidden", "false");
    toggleBtn.classList.add("sca-is-open");
    toggleBtn.setAttribute("aria-expanded", "true");
    toggleBtn.setAttribute("aria-label", "Close SmartAI Assistant");

    /* clear unread */
    unreadCount = 0;
    if (badgeEl) badgeEl.hidden = true;

    if (!hasOpened) {
      hasOpened = true;
      showWelcome();
    }

    setTimeout(function () { inputEl.focus(); }, 220);
  }

  function closeChat() {
    isOpen = false;
    chatWindow.classList.remove("sca-is-open");
    chatWindow.setAttribute("aria-hidden", "true");
    toggleBtn.classList.remove("sca-is-open");
    toggleBtn.setAttribute("aria-expanded", "false");
    toggleBtn.setAttribute("aria-label", "Open SmartAI Assistant");
  }

  function toggleChat() {
    isOpen ? closeChat() : openChat();
  }

  /* ── EVENT WIRING ────────────────────────────────────────────── */
  toggleBtn.addEventListener("click", toggleChat);
  closeBtn.addEventListener("click", closeChat);

  form.addEventListener("submit", function (e) {
    e.preventDefault();
    sendMessage();
  });

  inputEl.addEventListener("input", updateSendState);
  inputEl.addEventListener("keydown", function (e) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  });

  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape" && isOpen) closeChat();
  });

  /* initial send button state */
  updateSendState();
/* ==========================================================
   PUBLIC API
========================================================== */

window.openAIAssistant = openChat;
window.closeAIAssistant = closeChat;
window.toggleAIAssistant = toggleChat;

window.aiAssistant = {
    open: openChat,
    close: closeChat,
    toggle: toggleChat
};
})();