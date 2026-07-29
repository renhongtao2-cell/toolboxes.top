/**
 * ToolBoxHub Affiliate Recommendations v2
 * Amazon Associates — Tag: globalgamegui-20
 * Matches relevant products to each calculator type
 */
(function() {
  var TAG = 'globalgamegui-20';
  var DISCLOSURE = 'As an Amazon Associate we earn from qualifying purchases.';

  // Products mapped to page types (Amazon ASINs)
  var PRODUCTS = {
    'mortgage'  : { asin: 'B0DS6YLWSF', name: 'HP 12C Financial Calculator', desc: 'The standard for mortgage professionals — used by loan officers nationwide' },
    'loan'      : { asin: 'B0B5GF6Z5B', name: 'TI BA II Plus Financial Calculator', desc: 'Approved for major finance exams, handles NPV/IRR/amortization' },
    'compound'  : { asin: 'B09KVPZ3LK', name: 'Sharp EL-738 Financial Calculator', desc: 'Built-in compound interest and TVM functions for investors' },
    'invest'    : { asin: 'B0BRX5C6MY', name: 'Casio FC-200V Financial Calculator', desc: 'Business and investment analysis with 225+ functions' },
    'budget'    : { asin: 'B0BN5SYKXN', name: 'Paperfeel Budget Planner 2026', desc: 'Dated monthly planner with bill organizer — track every dollar' },
    'tax'       : { asin: 'B0CG7QY6WB', name: 'TurboTax Deluxe 2025', desc: 'State + Federal e-file — maximize your refund with guided preparation' },
    'retire'    : { asin: 'B09FZQ4G7V', name: 'Retirement Budget Calculator Notebook', desc: 'Track retirement savings, expenses, and withdrawal strategies' },
    'debt'      : { asin: 'B0C7Q891W7', name: 'Debt Payoff Planner', desc: 'Track multiple debts with snowball/avalanche methods — 12 month undated' },
    'crypto'    : { asin: 'B09XS4WKJR', name: 'Ledger Nano X Crypto Hardware Wallet', desc: 'Secure your crypto portfolio — cold storage for 5500+ coins' },
    'savings'   : { asin: 'B0DP8LM9NG', name: 'Money Saving Challenge Binder', desc: '100 envelope challenge system with trackers for annual goals' },
    'salary'    : { asin: 'B0BNT5156F', name: 'Salary Negotiation Workbook', desc: 'Step-by-step guide to negotiating your next offer' },
    'stock'     : { asin: 'B07GPS8R3K', name: 'Stock Research Notebook', desc: 'Track earnings, dividends, and portfolio performance in one place' },
    'capital'   : { asin: 'B08ZYGMMR3', name: 'Tax-Loss Harvesting Guide', desc: 'Step-by-step capital gains optimization strategies' },
    'property'  : { asin: 'B0DS6YLWSF', name: 'HP 12C Financial Calculator', desc: 'The standard for mortgage professionals — used by loan officers nationwide' },
  };

  // General office/home products (shown on all pages)
  var OFFICE_PICKS = [
    { asin: 'B086XKF35C', name: 'Texas Instruments BA II Plus', desc: 'Standard financial calculator' },
    { asin: 'B07T5BGMGZ', name: 'Catalina 8-Digit Desktop Calculator', desc: 'Large display, dual power' },
    { asin: 'B08N36ZLJJ', name: 'EXPO Dry Erase Board 36"x24"', desc: 'Plan budgets and track goals' },
    { asin: 'B07PW9VBZ3', name: 'Five Star Spiral Notebook 6-Pack', desc: 'College ruled, 100 sheets each' },
  ];

  function getPageType() {
    var path = window.location.pathname.split('/').pop().replace('.html', '').toLowerCase();
    if (/mortgage|home/.test(path)) return 'mortgage';
    if (/loan/.test(path) && !/auto/.test(path) && !/student/.test(path)) return 'loan';
    if (/compound/.test(path)) return 'compound';
    if (/invest|roi/.test(path)) return 'invest';
    if (/budget/.test(path)) return 'budget';
    if (/income-tax|sales-tax|capital-gains|vat/.test(path)) return 'tax';
    if (/retire/.test(path)) return 'retire';
    if (/debt/.test(path)) return 'debt';
    if (/crypto/.test(path)) return 'crypto';
    if (/college-savings|savings-goal/.test(path)) return 'savings';
    if (/salary/.test(path)) return 'salary';
    if (/stock/.test(path)) return 'stock';
    if (/capital/.test(path)) return 'capital';
    if (/property/.test(path)) return 'property';
    return 'loan';
  }

  function buildProductCard(prod) {
    var url = 'https://www.amazon.com/dp/' + prod.asin + '?tag=' + TAG;
    return '<a href="' + url + '" rel="sponsored nofollow" target="_blank" ' +
      'style="display:flex;align-items:center;gap:12px;padding:12px;border:1px solid var(--border,#e5e7eb);border-radius:10px;text-decoration:none;color:inherit;transition:border-color .2s;" ' +
      'onmouseover="this.style.borderColor=\'#ff9900\'" onmouseout="this.style.borderColor=\'var(--border,#e5e7eb)\'">' +
      '<div style="flex:1;min-width:0;">' +
      '<strong style="font-size:.88rem;">' + prod.name + '</strong>' +
      '<br><span style="font-size:.78rem;color:var(--text-secondary,#6b7280);">' + prod.desc + '</span>' +
      '</div>' +
      '<span style="flex-shrink:0;padding:6px 16px;background:#ff9900;color:#000;border-radius:6px;font-weight:700;font-size:.8rem;white-space:nowrap;">Check Price →</span>' +
      '</a>';
  }

  function addRecommendations() {
    var type = getPageType();
    var mainProd = PRODUCTS[type] || PRODUCTS['loan'];
    var target = document.querySelector('.seo-content') || document.querySelector('.tool-card-interface') || document.querySelector('.tool-layout');
    if (!target) return;

    // ── Primary product recommendation ──
    var section = document.createElement('div');
    section.style.cssText = 'margin:2rem 0;padding:1.5rem;background:var(--bg-card,#f9fafb);border:1px solid var(--border,#e5e7eb);border-radius:12px;';
    section.innerHTML =
      '<div style="margin-bottom:1rem;">' +
      '  <h3 style="margin:0;font-size:1rem;">🛒 Recommended Tool</h3>' +
      '  <p style="margin:4px 0 0 0;font-size:.82rem;color:var(--text-secondary,#6b7280);">' + DISCLOSURE + '</p>' +
      '</div>' +
      buildProductCard(mainProd);
    target.parentNode.insertBefore(section, target.nextSibling);

    // ── Quick office/home picks ──
    var officeSection = document.createElement('div');
    officeSection.style.cssText = 'margin:1.5rem 0;padding:1rem 1.5rem;background:var(--bg-card,#f9fafb);border:1px solid var(--border,#e5e7eb);border-radius:12px;';
    officeSection.innerHTML =
      '<h4 style="margin:0 0 10px 0;font-size:.9rem;">📋 Popular Office & Home Picks</h4>' +
      '<div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:8px;">' +
      OFFICE_PICKS.map(function(p) {
        return '<a href="https://www.amazon.com/dp/' + p.asin + '?tag=' + TAG + '" rel="sponsored nofollow" target="_blank" ' +
          'style="display:block;padding:10px;border:1px solid var(--border,#e5e7eb);border-radius:8px;text-decoration:none;color:inherit;transition:border-color .2s;" ' +
          'onmouseover="this.style.borderColor=\'#ff9900\'" onmouseout="this.style.borderColor=\'var(--border,#e5e7eb)\'">' +
          '<strong style="font-size:.8rem;">' + p.name + '</strong>' +
          '<br><span style="font-size:.72rem;color:var(--text-secondary,#6b7280);">' + p.desc + '</span>' +
          '</a>';
      }).join('') +
      '</div>' +
      '<p style="margin:.5rem 0 0;font-size:.7rem;color:var(--text-secondary,#9ca3af);"><em>' + DISCLOSURE + '</em></p>';
    section.parentNode.insertBefore(officeSection, section.nextSibling);
  }

  // ── Amazon link conversion ──
  document.querySelectorAll('a[href*="amazon.com"]').forEach(function(a) {
    try {
      var url = new URL(a.href);
      url.searchParams.set('tag', TAG);
      a.href = url.toString();
    } catch(e) {}
  });

  // ── Run after DOM ready ──
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', addRecommendations);
  } else {
    addRecommendations();
  }
})();
