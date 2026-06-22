<template>
  <footer class="footer">
    <div class="container">
      <!-- Top: logo + tagline -->
      <div class="footer-top">
        <span class="brand-wordmark footer-wordmark">Quebec</span>
        <span class="footer-pipe" aria-hidden="true">|</span>
        <span class="footer-tagline">Software independente</span>
      </div>

      <!-- Divider -->
      <hr class="footer-rule" />

      <!-- Bottom: copyright + social -->
      <div class="footer-bottom">
        <p class="footer-copy mono">© 2026 Quebec. Todos os direitos reservados.</p>

        <div class="footer-social">
          <!-- LinkedIn -->
          <a
            href="https://linkedin.com/company/quebec-studio"
            target="_blank"
            rel="noopener noreferrer"
            class="social-link"
            aria-label="LinkedIn"
          >
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" aria-hidden="true">
              <rect x="2" y="2" width="20" height="20" rx="4" stroke="currentColor" stroke-width="1.5"/>
              <path d="M7 10v7M7 7v.5" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
              <path d="M11 17v-4c0-1.657 1.343-3 3-3s3 1.343 3 3v4" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
              <path d="M11 10v7" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
            </svg>
          </a>

          <!-- GitHub -->
          <a
            href="https://github.com/quebec-studio"
            target="_blank"
            rel="noopener noreferrer"
            class="social-link"
            aria-label="GitHub"
          >
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" aria-hidden="true">
              <path d="M9 19c-5 1.5-5-2.5-7-3m14 6v-3.87a3.37 3.37 0 0 0-.94-2.61c3.14-.35 6.44-1.54 6.44-7A5.44 5.44 0 0 0 20 4.77 5.07 5.07 0 0 0 19.91 1S18.73.65 16 2.48a13.38 13.38 0 0 0-7 0C6.27.65 5.09 1 5.09 1A5.07 5.07 0 0 0 5 4.77a5.44 5.44 0 0 0-1.5 3.78c0 5.42 3.3 6.61 6.44 7A3.37 3.37 0 0 0 9 18.13V22" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </a>
        </div>
      </div>
    </div>
  </footer>
</template>

<style scoped>
.footer {
  border-top: 1px solid var(--border);
  padding: 32px 0 28px;
}

.footer-top {
  display: flex;
  align-items: center;
  padding-bottom: 24px;
}

.footer-wordmark {
  font-size: 1rem;
  color: var(--ink);
  letter-spacing: 0.14em;
}

.footer-pipe {
  color: var(--border);
  font-weight: 300;
  margin: 0 16px;
  font-size: 1.1rem;
  line-height: 1;
}

.footer-tagline {
  font-size: 0.82rem;
  color: var(--ink-2);
}

.footer-rule {
  border: none;
  border-top: 1px solid var(--border);
  margin: 0 0 20px;
}

.footer-bottom {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}

.footer-copy {
  font-size: 0.68rem;
  letter-spacing: 0.04em;
  color: var(--ink-3);
}

.footer-social {
  display: flex;
  align-items: center;
  gap: 12px;
}

.social-link {
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--ink-3);
  transition: color 0.18s;
}

.social-link:hover {
  color: var(--ink-2);
}

@media (max-width: 600px) {
  .footer-bottom {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }
}
</style>
