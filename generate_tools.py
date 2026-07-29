"""
Finance ToolBox — Tool Page Generator
Reads tools_config.json and generates complete HTML pages.
"""
import json, os, hashlib, re
from datetime import datetime

ROOT = os.path.dirname(os.path.abspath(__file__))
SITE_URL = "https://toolboxes.top"
GA_ID = "G-SZY7VH3RXK"

# ── Shared HTML components ─────────────────────────────

NAV = '''
<nav class="nav">
<div class="container">
<a href="index.html" class="nav-logo"><div class="nav-logo-icon"><i class="fas fa-calculator"></i></div>Finance ToolBox</a>
<div class="nav-links" id="navLinks">
<a href="index.html">Home</a>
<a href="about.html">About</a>
<a href="contact.html">Contact</a>
</div>
<button class="theme-toggle" id="themeToggle" aria-label="Toggle theme"><i class="fas fa-moon"></i></button>
<button class="mobile-menu-btn" id="mobileMenuBtn" aria-label="Menu"><i class="fas fa-bars"></i></button>
</div>
</nav>'''

FOOTER = '''
<footer class="footer">
<div class="container">
<div class="footer-grid">
<div class="footer-col">
<h4>Finance ToolBox</h4>
<p style="color:var(--text-secondary);font-size:.88rem;">Free financial calculators for loans, investments, budgeting, and more. Make smarter money decisions.</p>
</div>
<div class="footer-col">
<h4>Calculators</h4>
<a href="loan-calculator.html">Loan Calculator</a>
<a href="mortgage-calculator.html">Mortgage Calculator</a>
<a href="compound-interest-calculator.html">Compound Interest</a>
<a href="budget-calculator.html">Budget Calculator</a>
<a href="index.html">View All (29)</a>
</div>
<div class="footer-col">
<h4>Company</h4>
<a href="about.html">About Us</a>
<a href="contact.html">Contact</a>
<a href="privacy.html">Privacy Policy</a>
<a href="terms.html">Terms of Service</a>
</div>
</div>
<div class="footer-bottom">
<span>&copy; 2026 Finance ToolBox. All rights reserved.</span>
<span>Smart financial calculators for everyone.</span>
</div>
</div>
</footer>'''

MODAL = ''

CF_ANALYTICS = "<script defer src='https://static.cloudflareinsights.com/beacon.min.js' data-cf-beacon='{\"token\": \"9cdb1d83529f44749dc930864bab3884\"}'></script>"

# ── Tool logic templates ───────────────────────────────

TOOL_SCRIPTS = {}

TOOL_SCRIPTS["loan-calculator"] = '''
function calcLoan() {
  var a=parseFloat(document.getElementById('loanAmount').value);
  var r=parseFloat(document.getElementById('loanRate').value)/100/12;
  var n=parseInt(document.getElementById('loanTerm').value)*12;
  if(isNaN(a)||isNaN(r)||isNaN(n)||a<=0||n<=0){showToast('Please enter valid loan values.');return;}
  if(r<=0){showToast('Interest rate must be >0.');return;}
  var p=a*r*Math.pow(1+r,n)/(Math.pow(1+r,n)-1);
  if(!isFinite(p)){showToast('Invalid result.');return;}
  document.getElementById('loanPayment').textContent='$'+p.toFixed(2);
  document.getElementById('loanTotal').textContent='$'+(p*n).toFixed(2);
  document.getElementById('loanInterest').textContent='$'+(p*n-a).toFixed(2);
}
'''

TOOL_SCRIPTS["mortgage-calculator"] = '''
function calcMortgage() {
  var p=parseFloat(document.getElementById('mortPrice').value);
  var d=parseFloat(document.getElementById('mortDown').value)||0;
  var r=parseFloat(document.getElementById('mortRate').value)/100/12;
  var n=parseInt(document.getElementById('mortTerm').value)*12;
  var t=parseFloat(document.getElementById('mortTax').value)||0;
  var i=parseFloat(document.getElementById('mortIns').value)||0;
  var m=parseFloat(document.getElementById('mortPmi').value)||0;
  if(isNaN(p)||isNaN(r)||isNaN(n)||p<=0){showToast('Please enter valid values.');return;}
  if(r<=0){showToast('Rate must be >0.');return;}
  var la=p-d;if(la<=0){showToast('Down payment exceeds price.');return;}
  var pm=la*r*Math.pow(1+r,n)/(Math.pow(1+r,n)-1);
  var total=pm+t/12+i/12+m/12;
  document.getElementById('mortPayment').textContent='$'+total.toFixed(2);
  document.getElementById('mortPrincipal').textContent='$'+pm.toFixed(2);
  document.getElementById('mortTaxIns').textContent='$'+(t/12+i/12+m/12).toFixed(2);
  document.getElementById('mortDownPct').textContent=(d/p*100).toFixed(1)+'%';
}
'''

TOOL_SCRIPTS["auto-loan-calculator"] = '''
function calcAutoLoan() {
  var p=parseFloat(document.getElementById('autoPrice').value);
  var d=parseFloat(document.getElementById('autoDown').value)||0;
  var t=parseFloat(document.getElementById('autoTrade').value)||0;
  var r=parseFloat(document.getElementById('autoRate').value)/100/12;
  var n=parseInt(document.getElementById('autoTerm').value);
  if(isNaN(p)||isNaN(r)||isNaN(n)||p<=0||n<=0){showToast('Please enter valid values.');return;}
  var la=p-d-t;if(la<=0){showToast('Down+trade exceeds price.');return;}
  if(r<=0){showToast('Rate must be >0.');return;}
  var pm=la*r*Math.pow(1+r,n)/(Math.pow(1+r,n)-1);
  document.getElementById('autoPayment').textContent='$'+pm.toFixed(2);
  document.getElementById('autoTotal').textContent='$'+(pm*n).toFixed(2);
  document.getElementById('autoInterest').textContent='$'+(pm*n-la).toFixed(2);
}
'''

TOOL_SCRIPTS["amortization-calculator"] = '''
function calcAmortization() {
  var a=parseFloat(document.getElementById('amorAmount').value);
  var r=parseFloat(document.getElementById('amorRate').value)/100/12;
  var n=parseInt(document.getElementById('amorTerm').value)*12;
  if(isNaN(a)||isNaN(r)||isNaN(n)||a<=0||n<=0){showToast('Please enter valid values.');return;}
  if(r<=0){showToast('Rate must be >0.');return;}
  var p=a*r*Math.pow(1+r,n)/(Math.pow(1+r,n)-1);
  if(!isFinite(p)){showToast('Invalid result.');return;}
  var b=a,rows='',ti=0,mx=Math.min(n,360);
  for(var i=1;i<=mx;i++){var ip=b*r;var pp=p-ip;b-=pp;if(b<0)b=0;ti+=ip;
    rows+='<tr><td>'+i+'</td><td>$'+p.toFixed(2)+'</td><td>$'+pp.toFixed(2)+'</td><td>$'+ip.toFixed(2)+'</td><td>$'+b.toFixed(2)+'</td></tr>';
    if(b<=0)break;}
  document.getElementById('amorPayment').textContent='$'+p.toFixed(2);
  document.getElementById('amorInterest').textContent='$'+ti.toFixed(2);
  document.getElementById('amorBody').innerHTML=rows;
}
'''

TOOL_SCRIPTS["debt-payoff-calculator"] = '''
function addDebtRow(){var c=document.getElementById('debtRows'),i=c.children.length,d=document.createElement('div');
  d.className='debt-row';d.style.cssText='display:grid;grid-template-columns:1fr 1fr 1fr;gap:6px;margin-bottom:6px;';
  d.innerHTML='<input type="text" class="debt-name" placeholder="Name" style="padding:6px;border:1px solid var(--border);border-radius:var(--radius);background:var(--bg-primary);color:var(--text-primary);">'
  +'<input type="number" class="debt-balance" placeholder="Balance" step="0.01" min="0" style="padding:6px;border:1px solid var(--border);border-radius:var(--radius);background:var(--bg-primary);color:var(--text-primary);">'
  +'<input type="number" class="debt-rate" placeholder="APR %" step="0.1" style="padding:6px;border:1px solid var(--border);border-radius:var(--radius);background:var(--bg-primary);color:var(--text-primary);">';
  c.appendChild(d);}
function calcDebtPayoff(){var rows=document.querySelectorAll('.debt-row'),ex=parseFloat(document.getElementById('debtExtra').value)||0,debs=[];
  for(var i=0;i<rows.length;i++){var n=rows[i].querySelector('.debt-name').value||'Debt '+(i+1),b=parseFloat(rows[i].querySelector('.debt-balance').value),r=parseFloat(rows[i].querySelector('.debt-rate').value);
    if(isNaN(b)||isNaN(r)||b<=0)continue;debs.push({name:n,balance:b,rate:r/100/12,min:Math.max(b*0.02,25)});}
  if(debs.length===0){showToast('Enter at least one debt.');return;}
  function sim(arr){var rem=[];for(var i=0;i<arr.length;i++)rem.push({b:arr[i].balance,r:arr[i].rate,m:arr[i].min});
    var mo=0,ti=0,tm=0;for(var i=0;i<rem.length;i++)tm+=rem[i].m;
    for(var m=0;m<600;m++){var av=tm+ex;for(var i=0;i<rem.length;i++){var ip=rem[i].b*rem[i].r;ti+=ip;rem[i].b+=ip;}
      for(var i=0;i<rem.length;i++){var pay=Math.min(rem[i].m,rem[i].b);rem[i].b-=pay;av-=pay;}
      for(var i=0;i<rem.length;i++){if(rem[i].b>0.01&&av>0){var ep=Math.min(av,rem[i].b);rem[i].b-=ep;av-=ep;}}
      rem=rem.filter(function(d){return d.b>0.01;});mo=m+1;if(rem.length===0)break;}
    return{months:mo,interest:ti};}
  var sb=debs.slice().sort(function(a,b){return a.balance-b.balance;}),sr=sim(sb);
  var av=debs.slice().sort(function(a,b){return b.rate-a.rate;}),ar=sim(av);
  document.getElementById('debtSnowMonths').textContent=sr.months;
  document.getElementById('debtSnowInterest').textContent='$'+sr.interest.toFixed(2);
  document.getElementById('debtAvaMonths').textContent=ar.months;
  document.getElementById('debtAvaInterest').textContent='$'+ar.interest.toFixed(2);
}
'''

TOOL_SCRIPTS["refinance-calculator"] = '''
function calcRefinance() {
  var b=parseFloat(document.getElementById('refiBalance').value);
  var cr=parseFloat(document.getElementById('refiCurRate').value)/100/12;
  var ct=parseInt(document.getElementById('refiCurTerm').value)*12;
  var nr=parseFloat(document.getElementById('refiNewRate').value)/100/12;
  var nt=parseInt(document.getElementById('refiNewTerm').value)*12;
  var c=parseFloat(document.getElementById('refiCosts').value)||0;
  if(isNaN(b)||isNaN(cr)||isNaN(ct)||isNaN(nr)||isNaN(nt)||b<=0){showToast('Please enter valid values.');return;}
  if(cr<=0){showToast('Current rate must be >0.');return;}
  var cp=b*cr*Math.pow(1+cr,ct)/(Math.pow(1+cr,ct)-1);
  if(!isFinite(cp)){showToast('Invalid current rate.');return;}
  var np=nr>0?b*nr*Math.pow(1+nr,nt)/(Math.pow(1+nr,nt)-1):b/nt;
  var ms=cp-np,be=ms>0?Math.ceil(c/ms):'N/A',ts=ms>0?'$'+(ms*nt-c).toFixed(2):'$0.00';
  document.getElementById('refiCurPay').textContent='$'+cp.toFixed(2);
  document.getElementById('refiNewPay').textContent='$'+np.toFixed(2);
  document.getElementById('refiSavings').textContent='$'+ms.toFixed(2);
  document.getElementById('refiBreakEven').textContent=be;
  document.getElementById('refiTotalSave').textContent=ts;
}
'''

TOOL_SCRIPTS["dti-calculator"] = '''
function calcDTI() {
  var inc=parseFloat(document.getElementById('dtiIncome').value);
  var mort=parseFloat(document.getElementById('dtiMortgage').value)||0;
  var other=parseFloat(document.getElementById('dtiOther').value)||0;
  if(isNaN(inc)||inc<=0){showToast('Enter valid monthly income.');return;}
  var fe=mort/inc*100,be=(mort+other)/inc*100;
  document.getElementById('dtiFront').textContent=fe.toFixed(1)+'%';
  document.getElementById('dtiBack').textContent=be.toFixed(1)+'%';
  var s='Excellent',c='status-high';
  if(be>43){s='Too High';c='status-low';}else if(be>36){s='High';c='status-medium';}else if(be>28){s='Fair';c='status-medium';}
  document.getElementById('dtiStatus').innerHTML='<span class="status-badge '+c+'">'+s+'</span>';
}
'''

TOOL_SCRIPTS["compound-interest-calculator"] = '''
function calcCompound() {
  var p=parseFloat(document.getElementById('compPrincipal').value);
  var m=parseFloat(document.getElementById('compMonthly').value)||0;
  var r=parseFloat(document.getElementById('compRate').value)/100;
  var y=parseInt(document.getElementById('compYears').value);
  var f=document.getElementById('compFreq').value;
  if(isNaN(p)||isNaN(r)||isNaN(y)||y<=0){showToast('Please enter valid values.');return;}
  var n=f==='daily'?365:f==='monthly'?12:f==='quarterly'?4:1;
  var t=p,tc=p;
  for(var i=0;i<y*n;i++){t+=m*(12/n);tc+=m*(12/n);t*=(1+r/n);}
  document.getElementById('compTotal').textContent='$'+t.toFixed(2);
  document.getElementById('compContrib').textContent='$'+tc.toFixed(2);
  document.getElementById('compEarnings').textContent='$'+(t-tc).toFixed(2);
}
'''

TOOL_SCRIPTS["investment-calculator"] = '''
function calcInvestment() {
  var i=parseFloat(document.getElementById('invInitial').value);
  var m=parseFloat(document.getElementById('invMonthly').value)||0;
  var r=parseFloat(document.getElementById('invRate').value)/100;
  var y=parseInt(document.getElementById('invYears').value);
  if(isNaN(i)||isNaN(r)||isNaN(y)||y<=0){showToast('Please enter valid values.');return;}
  var t=i,tc=i;
  for(var mo=0;mo<y*12;mo++){t+=m;tc+=m;t*=(1+r/12);}
  document.getElementById('invFinal').textContent='$'+t.toFixed(2);
  document.getElementById('invContrib').textContent='$'+tc.toFixed(2);
  document.getElementById('invEarnings').textContent='$'+(t-tc).toFixed(2);
}
'''

TOOL_SCRIPTS["retirement-calculator"] = '''
function calcRetirement() {
  var age=parseInt(document.getElementById('retAge').value);
  var ra=parseInt(document.getElementById('retRetireAge').value);
  var sv=parseFloat(document.getElementById('retSavings').value);
  var mo=parseFloat(document.getElementById('retMonthly').value)||0;
  var r=parseFloat(document.getElementById('retRate').value)/100;
  var di=parseFloat(document.getElementById('retDesired').value);
  if(isNaN(age)||isNaN(ra)||isNaN(sv)||isNaN(r)||isNaN(di)){showToast('Please enter valid values.');return;}
  var yrs=ra-age;if(yrs<=0){showToast('Retirement age must be after current age.');return;}
  var t=sv;for(var i=0;i<yrs*12;i++){t+=mo;t*=(1+r/12);}
  var ai=t*0.04;
  document.getElementById('retProjected').textContent='$'+t.toFixed(2);
  document.getElementById('retIncome').textContent='$'+ai.toFixed(2);
  document.getElementById('retStatus').innerHTML=ai>=di?'<span class="status-badge status-high">On Track!</span>':'<span class="status-badge status-low">Shortfall</span>';
}
'''

TOOL_SCRIPTS["stock-profit-calculator"] = '''
function calcStockProfit() {
  var bp=parseFloat(document.getElementById('stockBuy').value);
  var sp=parseFloat(document.getElementById('stockSell').value);
  var sh=parseFloat(document.getElementById('stockShares').value);
  var com=parseFloat(document.getElementById('stockComm').value)||0;
  if(isNaN(bp)||isNaN(sp)||isNaN(sh)||bp<=0||sh<=0){showToast('Please enter valid values.');return;}
  var totalCost=bp*sh+com,totalProceeds=sp*sh-com;
  var profit=totalProceeds-totalCost,roi=(profit/totalCost)*100;
  document.getElementById('stockProfit').textContent='$'+profit.toFixed(2);
  document.getElementById('stockROI').textContent=roi.toFixed(2)+'%';
  document.getElementById('stockNet').textContent='$'+totalProceeds.toFixed(2);
  document.getElementById('stockCost').textContent='$'+totalCost.toFixed(2);
}
'''

TOOL_SCRIPTS["savings-goal-calculator"] = '''
function calcSavingsGoal() {
  var g=parseFloat(document.getElementById('sgGoal').value);
  var cur=parseFloat(document.getElementById('sgCurrent').value)||0;
  var mo=parseInt(document.getElementById('sgMonths').value);
  var r=parseFloat(document.getElementById('sgRate').value)/100/12;
  if(isNaN(g)||isNaN(mo)||g<=0||mo<=0||isNaN(r)){showToast('Please enter valid values.');return;}
  var needed=g-cur;
  if(needed<=0){showToast('You already reached your goal!');return;}
  var pmt=r>0?needed*r*Math.pow(1+r,mo)/(Math.pow(1+r,mo)-1):needed/mo;
  document.getElementById('sgMonthly').textContent='$'+pmt.toFixed(2);
  document.getElementById('sgTotal').textContent='$'+(pmt*mo).toFixed(2);
  document.getElementById('sgEarned').textContent='$'+(pmt*mo-needed).toFixed(2);
}
'''

TOOL_SCRIPTS["dividend-calculator"] = '''
function calcDividend() {
  var sp=parseFloat(document.getElementById('divPrice').value);
  var dps=parseFloat(document.getElementById('divDPS').value);
  var sh=parseFloat(document.getElementById('divShares').value);
  var gr=parseFloat(document.getElementById('divGrowth').value)/100||0;
  if(isNaN(sp)||isNaN(dps)||isNaN(sh)||sp<=0||sh<=0){showToast('Please enter valid values.');return;}
  var yieldPct=(dps/sp)*100,annual=dps*sh;
  var proj5=0;for(var y=1;y<=5;y++){proj5+=annual*Math.pow(1+gr,y);}
  document.getElementById('divYield').textContent=yieldPct.toFixed(2)+'%';
  document.getElementById('divAnnual').textContent='$'+annual.toFixed(2);
  document.getElementById('divMonthly').textContent='$'+(annual/12).toFixed(2);
  document.getElementById('divProjected').textContent='$'+proj5.toFixed(2);
}
'''

TOOL_SCRIPTS["crypto-profit-calculator"] = '''
function calcCryptoProfit() {
  var bp=parseFloat(document.getElementById('cryptoBuy').value);
  var sp=parseFloat(document.getElementById('cryptoSell').value);
  var qty=parseFloat(document.getElementById('cryptoQty').value);
  var fee=parseFloat(document.getElementById('cryptoFee').value)||0;
  if(isNaN(bp)||isNaN(sp)||isNaN(qty)||bp<=0||qty<=0){showToast('Please enter valid values.');return;}
  var totalCost=bp*qty+fee,totalProceeds=sp*qty-fee;
  var profit=totalProceeds-totalCost,roi=(profit/totalCost)*100;
  document.getElementById('cryptoProfit').textContent='$'+profit.toFixed(2);
  document.getElementById('cryptoROI').textContent=roi.toFixed(2)+'%';
  document.getElementById('cryptoNet').textContent='$'+totalProceeds.toFixed(2);
}
'''

TOOL_SCRIPTS["budget-calculator"] = '''
function calcBudget() {
  var inc=parseFloat(document.getElementById('budgetIncome').value);
  if(isNaN(inc)||inc<=0){showToast('Please enter valid monthly income.');return;}
  document.getElementById('budgetNeeds').textContent='$'+(inc*0.5).toFixed(2);
  document.getElementById('budgetWants').textContent='$'+(inc*0.3).toFixed(2);
  document.getElementById('budgetSavings').textContent='$'+(inc*0.2).toFixed(2);
}
'''

TOOL_SCRIPTS["salary-calculator"] = '''
function calcSalary() {
  var mode=document.querySelector('input[name="salMode"]:checked').value;
  var val=parseFloat(document.getElementById('salValue').value);
  var hrs=parseFloat(document.getElementById('salHours').value)||40;
  var dys=parseFloat(document.getElementById('salDays').value)||5;
  if(isNaN(val)||val<=0){showToast('Please enter a salary value.');return;}
  var hourly,weekly,monthly,annual;
  if(mode==='hourly'){hourly=val;weekly=val*hrs;monthly=weekly*52/12;annual=weekly*52;}
  else if(mode==='weekly'){weekly=val;hourly=val/hrs;monthly=val*52/12;annual=val*52;}
  else if(mode==='monthly'){monthly=val;weekly=val*12/52;hourly=weekly/hrs;annual=val*12;}
  else{annual=val;weekly=val/52;hourly=weekly/hrs;monthly=val/12;}
  document.getElementById('salHourly').textContent='$'+hourly.toFixed(2);
  document.getElementById('salWeekly').textContent='$'+weekly.toFixed(2);
  document.getElementById('salMonthly').textContent='$'+monthly.toFixed(2);
  document.getElementById('salAnnual').textContent='$'+annual.toFixed(2);
}
'''

TOOL_SCRIPTS["bill-split-calculator"] = '''
function calcBillSplit() {
  var total=parseFloat(document.getElementById('billTotal').value);
  var ppl=parseInt(document.getElementById('billPeople').value);
  var tip=parseFloat(document.getElementById('billTip').value)||0;
  if(isNaN(total)||isNaN(ppl)||total<=0||ppl<=0){showToast('Please enter valid values.');return;}
  var tipAmt=total*tip/100,grand=total+tipAmt,each=grand/ppl;
  document.getElementById('billTipAmt').textContent='$'+tipAmt.toFixed(2);
  document.getElementById('billGrand').textContent='$'+grand.toFixed(2);
  document.getElementById('billEach').textContent='$'+each.toFixed(2);
}
'''

TOOL_SCRIPTS["tip-calculator"] = '''
function calcTip() {
  var bill=parseFloat(document.getElementById('tipBill').value);
  var pct=parseFloat(document.getElementById('tipPct').value);
  var ppl=parseInt(document.getElementById('tipPeople').value)||1;
  if(isNaN(bill)||isNaN(pct)||bill<=0){showToast('Please enter the bill amount.');return;}
  var tip=bill*pct/100,total=bill+tip,each=total/ppl;
  document.getElementById('tipAmount').textContent='$'+tip.toFixed(2);
  document.getElementById('tipTotal').textContent='$'+total.toFixed(2);
  document.getElementById('tipEach').textContent='$'+each.toFixed(2);
}
'''

TOOL_SCRIPTS["inflation-calculator"] = '''
var CPI_DATA={1913:9.9,1914:10,1915:10.1,1916:10.9,1917:12.8,1918:15.1,1919:17.3,1920:20,1921:17.9,1922:16.8,1923:17.1,1924:17.1,1925:17.5,1926:17.7,1927:17.4,1928:17.1,1929:17.1,1930:16.7,1931:15.2,1932:13.7,1933:13,1934:13.4,1935:13.7,1936:13.9,1937:14.4,1938:14.1,1939:13.9,1940:14,1941:14.7,1942:16.3,1943:17.3,1944:17.6,1945:18,1946:19.5,1947:22.3,1948:24.1,1949:23.8,1950:24.1,1951:26,1952:26.5,1953:26.7,1954:26.9,1955:26.8,1956:27.2,1957:28.1,1958:28.9,1959:29.1,1960:29.6,1961:29.9,1962:30.2,1963:30.6,1964:31,1965:31.5,1966:32.4,1967:33.4,1968:34.8,1969:36.7,1970:38.8,1971:40.5,1972:41.8,1973:44.4,1974:49.3,1975:53.8,1976:56.9,1977:60.6,1978:65.2,1979:72.6,1980:82.4,1981:90.9,1982:96.5,1983:99.6,1984:103.9,1985:107.6,1986:109.6,1987:113.6,1988:118.3,1989:124,1990:130.7,1991:136.2,1992:140.3,1993:144.5,1994:148.2,1995:152.4,1996:156.9,1997:160.5,1998:163,1999:166.6,2000:172.2,2001:177.1,2002:179.9,2003:184,2004:188.9,2005:195.3,2006:201.6,2007:207.3,2008:215.3,2009:214.5,2010:218.1,2011:224.9,2012:229.6,2013:233,2014:236.7,2015:237,2016:240,2017:245.1,2018:251.1,2019:255.7,2020:258.8,2021:271,2022:292.7,2023:304.7,2024:314.8,2025:322.5};
function calcInflation() {
  var amt=parseFloat(document.getElementById('infAmount').value);
  var sy=parseInt(document.getElementById('infStartYear').value);
  var ey=parseInt(document.getElementById('infEndYear').value);
  if(isNaN(amt)||isNaN(sy)||isNaN(ey)||amt<=0){showToast('Please enter valid values.');return;}
  if(!CPI_DATA[sy]||!CPI_DATA[ey]){showToast('CPI data not available for those years.');return;}
  var adj=amt*CPI_DATA[ey]/CPI_DATA[sy];
  var change=((adj-amt)/amt)*100;
  document.getElementById('infResult').innerHTML='$'+amt.toFixed(2)+' in '+sy+' is worth <strong>$'+adj.toFixed(2)+'</strong> in '+ey;
  document.getElementById('infChange').textContent=change.toFixed(2)+'% total inflation';
}
'''

TOOL_SCRIPTS["income-tax-calculator"] = '''
function calcIncomeTax() {
  var inc=parseFloat(document.getElementById('taxIncome').value);
  var status=document.getElementById('taxStatus').value;
  var ded=parseFloat(document.getElementById('taxDed').value)||0;
  if(isNaN(inc)||inc<=0){showToast('Please enter valid income.');return;}
  var stdDed=status==='single'?14600:status==='married'?29200:21900;
  var totalDed=Math.max(stdDed,ded);
  var taxable=Math.max(0,inc-totalDed);
  var brackets=status==='single'?[[11600,.1],[47150,.12],[100525,.22],[191950,.24],[243725,.32],[609350,.35],[Infinity,.37]]
    :status==='married'?[[23200,.1],[94300,.12],[201050,.22],[383900,.24],[487450,.32],[731200,.35],[Infinity,.37]]
    :[[16550,.1],[63100,.12],[100525,.22],[191950,.24],[243725,.32],[609350,.35],[Infinity,.37]];
  var tax=0,prev=0;
  for(var i=0;i<brackets.length;i++){var br=brackets[i];if(taxable>prev){var incInBracket=Math.min(taxable,br[0])-prev;if(incInBracket>0)tax+=incInBracket*br[1];}prev=br[0];}
  document.getElementById('taxGross').textContent='$'+inc.toFixed(2);
  document.getElementById('taxDeduction').textContent='$'+totalDed.toFixed(2);
  document.getElementById('taxTaxable').textContent='$'+taxable.toFixed(2);
  document.getElementById('taxTotal').textContent='$'+tax.toFixed(2);
  document.getElementById('taxRate').textContent=(tax/inc*100).toFixed(1)+'%';
}
'''

TOOL_SCRIPTS["sales-tax-calculator"] = '''
function calcSalesTax() {
  var price=parseFloat(document.getElementById('stPrice').value);
  var rate=parseFloat(document.getElementById('stRate').value);
  if(isNaN(price)||isNaN(rate)||price<0){showToast('Please enter valid values.');return;}
  var tax=price*rate/100,total=price+tax;
  document.getElementById('stTax').textContent='$'+tax.toFixed(2);
  document.getElementById('stTotal').textContent='$'+total.toFixed(2);
  document.getElementById('stPct').textContent=rate+'%';
}
'''

TOOL_SCRIPTS["capital-gains-calculator"] = '''
function calcCapGains() {
  var bp=parseFloat(document.getElementById('cgBuy').value);
  var sp=parseFloat(document.getElementById('cgSell').value);
  var held=document.getElementById('cgHeld').value;
  var inc=parseFloat(document.getElementById('cgIncome').value)||0;
  if(isNaN(bp)||isNaN(sp)||bp<=0){showToast('Please enter valid values.');return;}
  var gain=sp-bp;
  if(held==='short'){var rate=inc<=11600?.1:inc<=47150?.12:inc<=100525?.22:inc<=191950?.24:inc<=243725?.32:inc<=609350?.35:.37;var tax=gain*rate;var label='Short-Term ('+(rate*100).toFixed(0)+'%)';}
  else{var rate=inc<=47025?0:inc<=518900?.15:.2;var tax=Math.max(0,gain*rate);var label='Long-Term ('+(rate*100).toFixed(0)+'%)';}
  document.getElementById('cgGain').textContent='$'+gain.toFixed(2);
  document.getElementById('cgTax').textContent='$'+tax.toFixed(2);
  document.getElementById('cgType').textContent=label;
  document.getElementById('cgNet').textContent='$'+(gain-tax).toFixed(2);
}
'''

TOOL_SCRIPTS["vat-calculator"] = '''
function calcVAT() {
  var price=parseFloat(document.getElementById('vatPrice').value);
  var rate=parseFloat(document.getElementById('vatRate').value);
  var mode=document.querySelector('input[name="vatMode"]:checked').value;
  if(isNaN(price)||isNaN(rate)||price<0){showToast('Please enter valid values.');return;}
  if(mode==='exclusive'){var vat=price*rate/100,total=price+vat;
    document.getElementById('vatExclusive').textContent='$'+price.toFixed(2);
    document.getElementById('vatTax').textContent='$'+vat.toFixed(2);
    document.getElementById('vatInclusive').textContent='$'+total.toFixed(2);}
  else{var exPrice=price/(1+rate/100),vat=price-exPrice;
    document.getElementById('vatExclusive').textContent='$'+exPrice.toFixed(2);
    document.getElementById('vatTax').textContent='$'+vat.toFixed(2);
    document.getElementById('vatInclusive').textContent='$'+price.toFixed(2);}
}
'''

TOOL_SCRIPTS["property-tax-calculator"] = '''
function calcPropertyTax() {
  var val=parseFloat(document.getElementById('ptValue').value);
  var rate=parseFloat(document.getElementById('ptRate').value);
  if(isNaN(val)||isNaN(rate)||val<=0){showToast('Please enter valid values.');return;}
  var annual=val*rate/100,monthly=annual/12;
  document.getElementById('ptAnnual').textContent='$'+annual.toFixed(2);
  document.getElementById('ptMonthly').textContent='$'+monthly.toFixed(2);
  document.getElementById('ptFiveYear').textContent='$'+(annual*5).toFixed(2);
}
'''

TOOL_SCRIPTS["currency-converter"] = '''
var FX_RATES={USD:1,EUR:0.92,GBP:0.79,JPY:149.5,CNY:7.24,CAD:1.36,AUD:1.53,CHF:0.88,INR:83.1,MXN:17.05,BRL:4.95,KRW:1320,SGD:1.34,NZD:1.65,SEK:10.45,NOK:10.55,DKK:6.88,TRY:30.2,ZAR:18.5,PLN:4.02,THB:35.5,MYR:4.68,PHP:56.2,IDR:15600,VND:24600};
function convertCurrency(){var a=parseFloat(document.getElementById('fxAmount').value);
  var f=document.getElementById('fxFrom').value,t=document.getElementById('fxTo').value;
  if(isNaN(a)||a<=0){showToast('Enter a valid amount.');return;}
  var usd=a/FX_RATES[f],conv=usd*FX_RATES[t];
  document.getElementById('fxResult').textContent=a.toFixed(2)+' '+f+' = '+conv.toFixed(2)+' '+t;
  document.getElementById('fxRate').textContent='1 '+f+' = '+(FX_RATES[t]/FX_RATES[f]).toFixed(4)+' '+t;
}function swapCurrency(){var f=document.getElementById('fxFrom'),t=document.getElementById('fxTo');var tmp=f.value;f.value=t.value;t.value=tmp;convertCurrency();}
'''

TOOL_SCRIPTS["fraction-calculator"] = '''
function gcd(a,b){a=Math.abs(a);b=Math.abs(b);while(b){var t=b;b=a%b;a=t;}return a;}
function calcFraction(){var n1=parseInt(document.getElementById('fracNum1').value),d1=parseInt(document.getElementById('fracDen1').value);
  var n2=parseInt(document.getElementById('fracNum2').value),d2=parseInt(document.getElementById('fracDen2').value);
  var op=document.querySelector('input[name="fracOp"]:checked').value;
  if(isNaN(n1)||isNaN(d1)||isNaN(n2)||isNaN(d2)||d1===0||d2===0){showToast('Enter valid fractions (denominator cannot be 0).');return;}
  var num,den;if(op==='add'){num=n1*d2+n2*d1;den=d1*d2;}
  else if(op==='sub'){num=n1*d2-n2*d1;den=d1*d2;}
  else if(op==='mul'){num=n1*n2;den=d1*d2;}
  else{num=n1*d2;den=d1*n2;}
  if(den<0){num=-num;den=-den;}
  var g=gcd(num,den),simpNum=num/g,simpDen=den/g,dec=simpNum/simpDen;
  document.getElementById('fracResult').textContent=simpNum+'/'+simpDen;
  document.getElementById('fracDecimal').textContent=dec.toFixed(4);
  document.getElementById('fracMixed').textContent=simpDen!==1?Math.floor(simpNum/simpDen)+' '+Math.abs(simpNum%simpDen)+'/'+simpDen:simpNum;
}
'''

TOOL_SCRIPTS["percentage-calculator"] = '''
function calcPercentage() {
  var mode=document.querySelector('input[name="pctMode"]:checked').value;
  var v1=parseFloat(document.getElementById('pctVal1').value);
  var v2=parseFloat(document.getElementById('pctVal2').value);
  if(isNaN(v1)||isNaN(v2)){showToast('Please enter both values.');return;}
  var result='',steps='';
  if(mode==='pct-of'){var r=v1/100*v2;result=v1+'% of '+v2+' = <strong>'+r.toFixed(2)+'</strong>';steps=v1+'/100 x '+v2+' = '+r.toFixed(2);}
  else if(mode==='what-pct'){var r=v1/v2*100;result=v1+' is <strong>'+r.toFixed(2)+'%</strong> of '+v2;steps=v1+'/'+v2+' x 100 = '+r.toFixed(2)+'%';}
  else{if(v1===0){showToast('Original cannot be 0 for % change.');return;}var r=(v2-v1)/v1*100;var dir=r>=0?'increase':'decrease';result='Change: <strong>'+r.toFixed(2)+'%</strong> ('+dir+')';steps='('+v2+'-'+v1+')/'+v1+' x 100 = '+r.toFixed(2)+'%';}
  document.getElementById('pctResult').innerHTML=result;
  document.getElementById('pctSteps').textContent=steps;
}function clearPct(){document.getElementById('pctVal1').value='';document.getElementById('pctVal2').value='';document.getElementById('pctResult').innerHTML='';document.getElementById('pctSteps').textContent='';}
'''

TOOL_SCRIPTS["time-calculator"] = '''
function calcTime() {
  var op=document.querySelector('input[name="timeOp"]:checked').value;
  var h1=parseInt(document.getElementById('timeH1').value)||0,m1=parseInt(document.getElementById('timeM1').value)||0,s1=parseInt(document.getElementById('timeS1').value)||0;
  var h2=parseInt(document.getElementById('timeH2').value)||0,m2=parseInt(document.getElementById('timeM2').value)||0,s2=parseInt(document.getElementById('timeS2').value)||0;
  var t1=h1*3600+m1*60+s1,t2=h2*3600+m2*60+s2;
  var tr=op==='add'?t1+t2:t1-t2;if(tr<0)tr=0;
  var rh=Math.floor(tr/3600),rm=Math.floor((tr%3600)/60),rs=tr%60;
  document.getElementById('timeResult').textContent=rh+'h '+rm+'m '+rs+'s';
  document.getElementById('timeHours').textContent=tr/3600;
  document.getElementById('timeMinutes').textContent=tr/60;
  document.getElementById('timeSeconds').textContent=tr;
}
'''

TOOL_SCRIPTS["roi-calculator"] = '''
function calcROI() {
  var inv=parseFloat(document.getElementById('roiInvested').value);
  var ret=parseFloat(document.getElementById('roiReturn').value);
  var yrs=parseFloat(document.getElementById('roiYears').value)||1;
  if(isNaN(inv)||isNaN(ret)||inv<=0||yrs<=0){showToast('Please enter valid values.');return;}
  var profit=ret-inv,roi=(profit/inv)*100,annual=Math.pow(ret/inv,1/yrs)-1;
  document.getElementById('roiProfit').textContent='$'+profit.toFixed(2);
  document.getElementById('roiPct').textContent=roi.toFixed(2)+'%';
  document.getElementById('roiAnnual').textContent=(annual*100).toFixed(2)+'%';
}
'''

TOOL_SCRIPTS["net-worth-calculator"] = '''
function calcNetWorth() {
  var cash=parseFloat(document.getElementById('nwCash').value)||0;
  var inv=parseFloat(document.getElementById('nwInvestments').value)||0;
  var prop=parseFloat(document.getElementById('nwProperty').value)||0;
  var veh=parseFloat(document.getElementById('nwVehicle').value)||0;
  var other=parseFloat(document.getElementById('nwOther').value)||0;
  var mort=parseFloat(document.getElementById('nwMortgage').value)||0;
  var loans=parseFloat(document.getElementById('nwLoans').value)||0;
  var cards=parseFloat(document.getElementById('nwCards').value)||0;
  var odebt=parseFloat(document.getElementById('nwOtherDebt').value)||0;
  var assets=cash+inv+prop+veh+other,liab=mort+loans+cards+odebt;
  document.getElementById('nwAssets').textContent='$'+assets.toFixed(2);
  document.getElementById('nwLiabilities').textContent='$'+liab.toFixed(2);
  document.getElementById('nwNetWorth').textContent='$'+(assets-liab).toFixed(2);
}
'''

TOOL_SCRIPTS["college-savings-calculator"] = '''
function calcCollegeSavings() {
  var age=parseInt(document.getElementById('csAge').value);
  var start=parseInt(document.getElementById('csStart').value);
  var cost=parseFloat(document.getElementById('csCost').value);
  var inf=parseFloat(document.getElementById('csInflation').value)/100||0.05;
  var cur=parseFloat(document.getElementById('csCurrent').value)||0;
  var mo=parseFloat(document.getElementById('csMonthly').value)||0;
  var r=parseFloat(document.getElementById('csRate').value)/100/12||0.06/12;
  if(isNaN(age)||isNaN(start)||isNaN(cost)||age<0||start<=age){showToast('Please enter valid values. College age must be after current age.');return;}
  var yrs=start-age,futureCost=cost*Math.pow(1+inf,yrs);
  var t=cur;for(var i=0;i<yrs*12;i++){t+=mo;t*=(1+r);}
  document.getElementById('csFutureCost').textContent='$'+futureCost.toFixed(2);
  document.getElementById('csProjected').textContent='$'+t.toFixed(2);
  document.getElementById('csGap').innerHTML=t>=futureCost?'<span class="status-badge status-high">On Track!</span>':'<span class="status-badge status-low">Shortfall: $'+(futureCost-t).toFixed(2)+'</span>';
}
'''

TOOL_SCRIPTS["retirement-expense-calculator"] = '''
function calcRetExpense() {
  var housing=parseFloat(document.getElementById('reHousing').value)||0;
  var food=parseFloat(document.getElementById('reFood').value)||0;
  var health=parseFloat(document.getElementById('reHealth').value)||0;
  var transport=parseFloat(document.getElementById('reTransport').value)||0;
  var utils=parseFloat(document.getElementById('reUtils').value)||0;
  var enter=parseFloat(document.getElementById('reEntertainment').value)||0;
  var other=parseFloat(document.getElementById('reOther').value)||0;
  var pct=parseFloat(document.getElementById('rePct').value)/100||0.8;
  var current=housing+food+health+transport+utils+enter+other;
  var retirement=current*pct;
  document.getElementById('reCurrent').textContent='$'+current.toFixed(2);
  document.getElementById('reRetirement').textContent='$'+retirement.toFixed(2);
  document.getElementById('reAnnual').textContent='$'+(retirement*12).toFixed(2);
}
'''
# ── HTML page builder ──────────────────────────────────

def build_seo_html(sections):
    html = ''
    for sec in sections:
        tag = sec['h']
        if tag == 'ul':
            items = sec.get('items', [])
            lis = ''.join(f'<li>{item}</li>' for item in items)
            html += f'<{tag}>{lis}</{tag}>'
        else:
            html += f'<{tag}>{sec["text"]}</{tag}>'
    return html

def generate_tool_page(tool):
    slug = tool['slug']
    name = tool['name']
    desc = tool['description']
    howto = tool['how_to_use']
    meta = tool['meta_desc']
    seo_title = tool['seo_title']
    seo_html = build_seo_html(tool['seo_sections'])
    script = TOOL_SCRIPTS.get(slug, '// No JS logic defined')

    js_slug = slug.replace('-', '')
    today = datetime.now().strftime("%B %d, %Y")

    return f'''<!DOCTYPE html>
<html lang="en" data-theme="light">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{name} - Finance ToolBox</title>
<meta name="description" content="{meta}">
<script type="application/ld+json">{{"@context":"https://schema.org","@type":"WebApplication","name":"{name}","description":"{meta}","applicationCategory":"Utilities","operatingSystem":"Any"}}</script>
<link rel="stylesheet" href="style.css">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
<link rel="icon" href="favicon.svg">
<link rel="apple-touch-icon" href="apple-touch-icon.svg">
<script async src="https://www.googletagmanager.com/gtag/js?id={GA_ID}"></script>
<script>
window.dataLayer = window.dataLayer || [];
function gtag(){{dataLayer.push(arguments);}}
gtag('js', new Date());
gtag('config', '{GA_ID}');
</script>
</head>
<body>
{NAV}

<div class="page-header">
<div class="container">
<div class="breadcrumb"><a href="index.html">Home</a> / {name}</div>
<h1>{name}</h1>
<p>{desc}</p>
</div>
</div>

<div class="container">
<div class="tool-layout">
<div class="tool-card-interface">
<h2>{name}</h2>

<p style="color:var(--text-secondary);font-size:.9rem;margin-bottom:18px;">{howto}</p>

<div class="tool-interface" id="toolInterface-{slug}">
  __TOOL_INTERFACE__
</div>

<div id="toolOutput" class="mt-16"></div>
</div>

<div class="ad-placeholder ad-inline" id="ad-banner-bottom"></div>

<div class="seo-content">
<h2>{seo_title}</h2>
{seo_html}
</div>
</div>

{FOOTER}
{MODAL}

<script src="main.js"></script>
<script>
// === {name} — Tool Logic ===
{script}
</script>
{CF_ANALYTICS}
</body>
</html>'''

def get_tool_interface(slug):
    """Return tool-specific form HTML."""
    interfaces = {
        "loan-calculator": '''
<div class="form-row-2">
<div class="form-group"><label>Loan Amount ($)</label><input type="number" id="loanAmount" placeholder="e.g. 10000" step="100"></div>
<div class="form-group"><label>Annual Interest Rate (%)</label><input type="number" id="loanRate" placeholder="e.g. 5.5" step="0.1"></div>
<div class="form-group"><label>Loan Term (years)</label><input type="number" id="loanTerm" placeholder="e.g. 5" min="1"></div>
</div>
<div class="result-actions"><button class="btn btn-primary" onclick="calcLoan()"><i class="fas fa-calculator"></i> Calculate</button></div>
<div class="mt-16" style="display:grid;grid-template-columns:repeat(3,1fr);gap:12px;">
<div style="background:var(--bg-secondary);border-radius:var(--radius);padding:14px;text-align:center;"><div style="font-size:1.6rem;font-weight:700;color:var(--primary)" id="loanPayment">$0.00</div><div style="font-size:.8rem;color:var(--text-muted)">Monthly Payment</div></div>
<div style="background:var(--bg-secondary);border-radius:var(--radius);padding:14px;text-align:center;"><div style="font-size:1.6rem;font-weight:700;color:var(--secondary)" id="loanTotal">$0.00</div><div style="font-size:.8rem;color:var(--text-muted)">Total Paid</div></div>
<div style="background:var(--bg-secondary);border-radius:var(--radius);padding:14px;text-align:center;"><div style="font-size:1.6rem;font-weight:700;color:var(--accent)" id="loanInterest">$0.00</div><div style="font-size:.8rem;color:var(--text-muted)">Total Interest</div></div>
</div>
''',
        "mortgage-calculator": '''
<div class="form-row-2">
<div class="form-group"><label>Home Price ($)</label><input type="number" id="mortPrice" placeholder="e.g. 300000" step="1000"></div>
<div class="form-group"><label>Down Payment ($)</label><input type="number" id="mortDown" placeholder="e.g. 60000" step="1000"></div>
<div class="form-group"><label>Annual Interest Rate (%)</label><input type="number" id="mortRate" placeholder="e.g. 6.5" step="0.1"></div>
<div class="form-group"><label>Loan Term (years)</label><input type="number" id="mortTerm" placeholder="e.g. 30" min="1"></div>
<div class="form-group"><label>Annual Property Tax ($)</label><input type="number" id="mortTax" placeholder="e.g. 3600" step="100"></div>
<div class="form-group"><label>Annual Insurance ($)</label><input type="number" id="mortIns" placeholder="e.g. 1200" step="100"></div>
<div class="form-group"><label>Monthly PMI ($)</label><input type="number" id="mortPmi" placeholder="e.g. 150" step="10"></div>
</div>
<div class="result-actions"><button class="btn btn-primary" onclick="calcMortgage()"><i class="fas fa-calculator"></i> Calculate</button></div>
<div class="mt-16" style="display:grid;grid-template-columns:repeat(2,1fr);gap:12px;">
<div style="background:var(--bg-secondary);border-radius:var(--radius);padding:14px;text-align:center;"><div style="font-size:1.6rem;font-weight:700;color:var(--primary)" id="mortPayment">$0.00</div><div style="font-size:.8rem;color:var(--text-muted)">Total Monthly Payment</div></div>
<div style="background:var(--bg-secondary);border-radius:var(--radius);padding:14px;text-align:center;"><div style="font-size:1.2rem;font-weight:700;color:var(--secondary)" id="mortPrincipal">$0.00</div><div style="font-size:.8rem;color:var(--text-muted)">Principal & Interest</div></div>
<div style="background:var(--bg-secondary);border-radius:var(--radius);padding:14px;text-align:center;"><div style="font-size:1.2rem;font-weight:700;color:var(--accent)" id="mortTaxIns">$0.00</div><div style="font-size:.8rem;color:var(--text-muted)">Tax, Insurance & PMI</div></div>
<div style="background:var(--bg-secondary);border-radius:var(--radius);padding:14px;text-align:center;"><div style="font-size:1.2rem;font-weight:700;color:var(--icon-1)" id="mortDownPct">0%</div><div style="font-size:.8rem;color:var(--text-muted)">Down Payment %</div></div>
</div>
''',
        "auto-loan-calculator": '''
<div class="form-row-2">
<div class="form-group"><label>Vehicle Price ($)</label><input type="number" id="autoPrice" placeholder="e.g. 35000" step="1000"></div>
<div class="form-group"><label>Down Payment ($)</label><input type="number" id="autoDown" placeholder="e.g. 5000" step="500"></div>
<div class="form-group"><label>Trade-In Value ($)</label><input type="number" id="autoTrade" placeholder="e.g. 3000" step="500"></div>
<div class="form-group"><label>Annual Interest Rate (%)</label><input type="number" id="autoRate" placeholder="e.g. 6.9" step="0.1"></div>
<div class="form-group"><label>Loan Term (months)</label><input type="number" id="autoTerm" placeholder="e.g. 60" min="1" max="84"></div>
</div>
<div class="result-actions"><button class="btn btn-primary" onclick="calcAutoLoan()"><i class="fas fa-calculator"></i> Calculate</button></div>
<div class="mt-16" style="display:grid;grid-template-columns:repeat(3,1fr);gap:12px;">
<div style="background:var(--bg-secondary);border-radius:var(--radius);padding:14px;text-align:center;"><div style="font-size:1.6rem;font-weight:700;color:var(--primary)" id="autoPayment">$0.00</div><div style="font-size:.8rem;color:var(--text-muted)">Monthly Payment</div></div>
<div style="background:var(--bg-secondary);border-radius:var(--radius);padding:14px;text-align:center;"><div style="font-size:1.2rem;font-weight:700;color:var(--secondary)" id="autoTotal">$0.00</div><div style="font-size:.8rem;color:var(--text-muted)">Total Cost</div></div>
<div style="background:var(--bg-secondary);border-radius:var(--radius);padding:14px;text-align:center;"><div style="font-size:1.2rem;font-weight:700;color:var(--accent)" id="autoInterest">$0.00</div><div style="font-size:.8rem;color:var(--text-muted)">Total Interest</div></div>
</div>
''',
        "amortization-calculator": '''
<div class="form-row-2">
<div class="form-group"><label>Loan Amount ($)</label><input type="number" id="amorAmount" placeholder="e.g. 200000" step="1000"></div>
<div class="form-group"><label>Annual Interest Rate (%)</label><input type="number" id="amorRate" placeholder="e.g. 5.5" step="0.1"></div>
<div class="form-group"><label>Loan Term (years)</label><input type="number" id="amorTerm" placeholder="e.g. 30" min="1"></div>
</div>
<div class="result-actions"><button class="btn btn-primary" onclick="calcAmortization()"><i class="fas fa-table"></i> Generate Schedule</button></div>
<div class="mt-16" style="display:grid;grid-template-columns:repeat(2,1fr);gap:12px;">
<div style="background:var(--bg-secondary);border-radius:var(--radius);padding:14px;text-align:center;"><div style="font-size:1.4rem;font-weight:700;color:var(--primary)" id="amorPayment">$0.00</div><div style="font-size:.8rem;color:var(--text-muted)">Monthly Payment</div></div>
<div style="background:var(--bg-secondary);border-radius:var(--radius);padding:14px;text-align:center;"><div style="font-size:1.4rem;font-weight:700;color:var(--accent)" id="amorInterest">$0.00</div><div style="font-size:.8rem;color:var(--text-muted)">Total Interest</div></div>
</div>
<div class="hint mb-8">Amortization schedule (up to 360 payments):</div>
<div style="overflow-x:auto;max-height:400px;overflow-y:auto;border:1px solid var(--border);border-radius:var(--radius);">
<table style="width:100%;font-size:.85rem;"><thead><tr><th>#</th><th>Payment</th><th>Principal</th><th>Interest</th><th>Balance</th></tr></thead>
<tbody id="amorBody"></tbody></table></div>
''',
        "debt-payoff-calculator": '''
<div class="form-group">
<label>Your Debts</label>
<div id="debtRows">
<div class="debt-row" style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:6px;margin-bottom:6px;">
<input type="text" class="debt-name" placeholder="Name" style="padding:6px;border:1px solid var(--border);border-radius:var(--radius);background:var(--bg-primary);color:var(--text-primary);">
<input type="number" class="debt-balance" placeholder="Balance" step="0.01" min="0" style="padding:6px;border:1px solid var(--border);border-radius:var(--radius);background:var(--bg-primary);color:var(--text-primary);">
<input type="number" class="debt-rate" placeholder="APR %" step="0.1" style="padding:6px;border:1px solid var(--border);border-radius:var(--radius);background:var(--bg-primary);color:var(--text-primary);">
</div>
</div>
<button class="btn btn-secondary btn-sm" onclick="addDebtRow()"><i class="fas fa-plus"></i> Add Debt</button>
</div>
<div class="form-group"><label>Extra Monthly Payment ($)</label><input type="number" id="debtExtra" placeholder="e.g. 100" step="10"></div>
<div class="result-actions"><button class="btn btn-primary" onclick="calcDebtPayoff()"><i class="fas fa-calculator"></i> Compare Strategies</button></div>
<div class="mt-16" style="display:grid;grid-template-columns:repeat(2,1fr);gap:12px;">
<div style="background:var(--bg-secondary);border-radius:var(--radius);padding:14px;text-align:center;"><div style="font-size:1.2rem;font-weight:700;color:var(--primary)">Snowball</div><div style="font-size:1rem;font-weight:700" id="debtSnowMonths">-</div><div style="font-size:.8rem;color:var(--text-muted)">Months to Payoff</div><div style="font-size:1rem;font-weight:700" id="debtSnowInterest">$0</div><div style="font-size:.8rem;color:var(--text-muted)">Total Interest</div></div>
<div style="background:var(--bg-secondary);border-radius:var(--radius);padding:14px;text-align:center;"><div style="font-size:1.2rem;font-weight:700;color:var(--secondary)">Avalanche</div><div style="font-size:1rem;font-weight:700" id="debtAvaMonths">-</div><div style="font-size:.8rem;color:var(--text-muted)">Months to Payoff</div><div style="font-size:1rem;font-weight:700" id="debtAvaInterest">$0</div><div style="font-size:.8rem;color:var(--text-muted)">Total Interest</div></div>
</div>
''',
        "refinance-calculator": '''
<div class="form-row-2">
<div class="form-group"><label>Current Loan Balance ($)</label><input type="number" id="refiBalance" placeholder="e.g. 250000" step="1000"></div>
<div class="form-group"><label>Current Rate (%)</label><input type="number" id="refiCurRate" placeholder="e.g. 7.5" step="0.1"></div>
<div class="form-group"><label>Remaining Term (years)</label><input type="number" id="refiCurTerm" placeholder="e.g. 25" min="1"></div>
<div class="form-group"><label>New Rate (%)</label><input type="number" id="refiNewRate" placeholder="e.g. 5.5" step="0.1"></div>
<div class="form-group"><label>New Term (years)</label><input type="number" id="refiNewTerm" placeholder="e.g. 30" min="1"></div>
<div class="form-group"><label>Closing Costs ($)</label><input type="number" id="refiCosts" placeholder="e.g. 5000" step="500"></div>
</div>
<div class="result-actions"><button class="btn btn-primary" onclick="calcRefinance()"><i class="fas fa-calculator"></i> Calculate</button></div>
<div class="mt-16" style="display:grid;grid-template-columns:repeat(5,1fr);gap:8px;">
<div style="background:var(--bg-secondary);border-radius:var(--radius);padding:12px;text-align:center;"><div style="font-weight:700;color:var(--primary)" id="refiCurPay">$0</div><div style="font-size:.75rem;color:var(--text-muted)">Current Payment</div></div>
<div style="background:var(--bg-secondary);border-radius:var(--radius);padding:12px;text-align:center;"><div style="font-weight:700;color:var(--secondary)" id="refiNewPay">$0</div><div style="font-size:.75rem;color:var(--text-muted)">New Payment</div></div>
<div style="background:var(--bg-secondary);border-radius:var(--radius);padding:12px;text-align:center;"><div style="font-weight:700;color:var(--accent)" id="refiSavings">$0</div><div style="font-size:.75rem;color:var(--text-muted)">Monthly Savings</div></div>
<div style="background:var(--bg-secondary);border-radius:var(--radius);padding:12px;text-align:center;"><div style="font-weight:700;color:var(--icon-1)" id="refiBreakEven">-</div><div style="font-size:.75rem;color:var(--text-muted)">Break-Even (months)</div></div>
<div style="background:var(--bg-secondary);border-radius:var(--radius);padding:12px;text-align:center;"><div style="font-weight:700;color:var(--icon-4)" id="refiTotalSave">$0</div><div style="font-size:.75rem;color:var(--text-muted)">Total Savings</div></div>
</div>
''',
        "dti-calculator": '''
<div class="form-row-2">
<div class="form-group"><label>Monthly Gross Income ($)</label><input type="number" id="dtiIncome" placeholder="e.g. 6000" step="500"></div>
<div class="form-group"><label>Monthly Housing Costs ($)</label><input type="number" id="dtiMortgage" placeholder="e.g. 1800" step="100"></div>
<div class="form-group"><label>Other Monthly Debt Payments ($)</label><input type="number" id="dtiOther" placeholder="e.g. 600" step="50"></div>
</div>
<div class="result-actions"><button class="btn btn-primary" onclick="calcDTI()"><i class="fas fa-calculator"></i> Calculate DTI</button></div>
<div class="mt-16" style="display:grid;grid-template-columns:repeat(3,1fr);gap:12px;">
<div style="background:var(--bg-secondary);border-radius:var(--radius);padding:14px;text-align:center;"><div style="font-size:1.6rem;font-weight:700;color:var(--primary)" id="dtiFront">0%</div><div style="font-size:.8rem;color:var(--text-muted)">Front-End DTI (Housing)</div></div>
<div style="background:var(--bg-secondary);border-radius:var(--radius);padding:14px;text-align:center;"><div style="font-size:1.6rem;font-weight:700;color:var(--secondary)" id="dtiBack">0%</div><div style="font-size:.8rem;color:var(--text-muted)">Back-End DTI (Total)</div></div>
<div style="background:var(--bg-secondary);border-radius:var(--radius);padding:14px;text-align:center;"><div style="font-size:1.2rem;font-weight:700" id="dtiStatus"><span class="status-badge status-medium">-</span></div><div style="font-size:.8rem;color:var(--text-muted)">Status</div></div>
</div>
''',
        "compound-interest-calculator": '''
<div class="form-row-2">
<div class="form-group"><label>Initial Investment ($)</label><input type="number" id="compPrincipal" placeholder="e.g. 10000" step="1000"></div>
<div class="form-group"><label>Monthly Contribution ($)</label><input type="number" id="compMonthly" placeholder="e.g. 500" step="50"></div>
<div class="form-group"><label>Annual Return Rate (%)</label><input type="number" id="compRate" placeholder="e.g. 8" step="0.5"></div>
<div class="form-group"><label>Time Period (years)</label><input type="number" id="compYears" placeholder="e.g. 20" min="1"></div>
<div class="form-group"><label>Compound Frequency</label><select id="compFreq" style="padding:8px;border:1px solid var(--border);border-radius:var(--radius);background:var(--bg-primary);color:var(--text-primary);width:100%;">
<option value="monthly">Monthly</option><option value="quarterly">Quarterly</option><option value="yearly">Yearly</option><option value="daily">Daily</option></select></div>
</div>
<div class="result-actions"><button class="btn btn-primary" onclick="calcCompound()"><i class="fas fa-calculator"></i> Calculate</button></div>
<div class="mt-16" style="display:grid;grid-template-columns:repeat(3,1fr);gap:12px;">
<div style="background:var(--bg-secondary);border-radius:var(--radius);padding:14px;text-align:center;"><div style="font-size:1.6rem;font-weight:700;color:var(--primary)" id="compTotal">$0.00</div><div style="font-size:.8rem;color:var(--text-muted)">Future Value</div></div>
<div style="background:var(--bg-secondary);border-radius:var(--radius);padding:14px;text-align:center;"><div style="font-size:1.2rem;font-weight:700;color:var(--secondary)" id="compContrib">$0.00</div><div style="font-size:.8rem;color:var(--text-muted)">Total Contributions</div></div>
<div style="background:var(--bg-secondary);border-radius:var(--radius);padding:14px;text-align:center;"><div style="font-size:1.2rem;font-weight:700;color:var(--accent)" id="compEarnings">$0.00</div><div style="font-size:.8rem;color:var(--text-muted)">Total Earnings</div></div>
</div>
''',
        "investment-calculator": '''
<div class="form-row-2">
<div class="form-group"><label>Initial Investment ($)</label><input type="number" id="invInitial" placeholder="e.g. 50000" step="1000"></div>
<div class="form-group"><label>Monthly Addition ($)</label><input type="number" id="invMonthly" placeholder="e.g. 1000" step="100"></div>
<div class="form-group"><label>Expected Return Rate (%)</label><input type="number" id="invRate" placeholder="e.g. 7" step="0.5"></div>
<div class="form-group"><label>Investment Period (years)</label><input type="number" id="invYears" placeholder="e.g. 15" min="1"></div>
</div>
<div class="result-actions"><button class="btn btn-primary" onclick="calcInvestment()"><i class="fas fa-calculator"></i> Calculate</button></div>
<div class="mt-16" style="display:grid;grid-template-columns:repeat(3,1fr);gap:12px;">
<div style="background:var(--bg-secondary);border-radius:var(--radius);padding:14px;text-align:center;"><div style="font-size:1.6rem;font-weight:700;color:var(--primary)" id="invFinal">$0.00</div><div style="font-size:.8rem;color:var(--text-muted)">Final Value</div></div>
<div style="background:var(--bg-secondary);border-radius:var(--radius);padding:14px;text-align:center;"><div style="font-size:1.2rem;font-weight:700;color:var(--secondary)" id="invContrib">$0.00</div><div style="font-size:.8rem;color:var(--text-muted)">Total Contributions</div></div>
<div style="background:var(--bg-secondary);border-radius:var(--radius);padding:14px;text-align:center;"><div style="font-size:1.2rem;font-weight:700;color:var(--accent)" id="invEarnings">$0.00</div><div style="font-size:.8rem;color:var(--text-muted)">Total Earnings</div></div>
</div>
''',
        "retirement-calculator": '''
<div class="form-row-2">
<div class="form-group"><label>Current Age</label><input type="number" id="retAge" placeholder="e.g. 30" min="18"></div>
<div class="form-group"><label>Desired Retirement Age</label><input type="number" id="retRetireAge" placeholder="e.g. 65" min="30"></div>
<div class="form-group"><label>Current Savings ($)</label><input type="number" id="retSavings" placeholder="e.g. 50000" step="1000"></div>
<div class="form-group"><label>Monthly Contribution ($)</label><input type="number" id="retMonthly" placeholder="e.g. 1000" step="100"></div>
<div class="form-group"><label>Expected Return Rate (%)</label><input type="number" id="retRate" placeholder="e.g. 7" step="0.5"></div>
<div class="form-group"><label>Desired Annual Income ($)</label><input type="number" id="retDesired" placeholder="e.g. 60000" step="5000"></div>
</div>
<div class="result-actions"><button class="btn btn-primary" onclick="calcRetirement()"><i class="fas fa-calculator"></i> Calculate</button></div>
<div class="mt-16" style="display:grid;grid-template-columns:repeat(3,1fr);gap:12px;">
<div style="background:var(--bg-secondary);border-radius:var(--radius);padding:14px;text-align:center;"><div style="font-size:1.4rem;font-weight:700;color:var(--primary)" id="retProjected">$0</div><div style="font-size:.8rem;color:var(--text-muted)">Projected Savings</div></div>
<div style="background:var(--bg-secondary);border-radius:var(--radius);padding:14px;text-align:center;"><div style="font-size:1.4rem;font-weight:700;color:var(--secondary)" id="retIncome">$0</div><div style="font-size:.8rem;color:var(--text-muted)">Annual Income (4% Rule)</div></div>
<div style="background:var(--bg-secondary);border-radius:var(--radius);padding:14px;text-align:center;"><div style="font-size:1.2rem;font-weight:700" id="retStatus">-</div><div style="font-size:.8rem;color:var(--text-muted)">Status</div></div>
</div>
''',
        "stock-profit-calculator": '''
<div class="form-row-2">
<div class="form-group"><label>Buy Price Per Share ($)</label><input type="number" id="stockBuy" placeholder="e.g. 50" step="0.01"></div>
<div class="form-group"><label>Sell Price Per Share ($)</label><input type="number" id="stockSell" placeholder="e.g. 75" step="0.01"></div>
<div class="form-group"><label>Number of Shares</label><input type="number" id="stockShares" placeholder="e.g. 100" min="1"></div>
<div class="form-group"><label>Commission ($)</label><input type="number" id="stockComm" placeholder="e.g. 9.99" step="0.01"></div>
</div>
<div class="result-actions"><button class="btn btn-primary" onclick="calcStockProfit()"><i class="fas fa-calculator"></i> Calculate</button></div>
<div class="mt-16" style="display:grid;grid-template-columns:repeat(4,1fr);gap:8px;">
<div style="background:var(--bg-secondary);border-radius:var(--radius);padding:12px;text-align:center;"><div style="font-weight:700;color:var(--primary)" id="stockProfit">$0</div><div style="font-size:.75rem;color:var(--text-muted)">Profit/Loss</div></div>
<div style="background:var(--bg-secondary);border-radius:var(--radius);padding:12px;text-align:center;"><div style="font-weight:700;color:var(--secondary)" id="stockROI">0%</div><div style="font-size:.75rem;color:var(--text-muted)">ROI</div></div>
<div style="background:var(--bg-secondary);border-radius:var(--radius);padding:12px;text-align:center;"><div style="font-weight:700;color:var(--accent)" id="stockNet">$0</div><div style="font-size:.75rem;color:var(--text-muted)">Net Proceeds</div></div>
<div style="background:var(--bg-secondary);border-radius:var(--radius);padding:12px;text-align:center;"><div style="font-weight:700;color:var(--icon-1)" id="stockCost">$0</div><div style="font-size:.75rem;color:var(--text-muted)">Total Cost</div></div>
</div>
''',
        "savings-goal-calculator": '''
<div class="form-row-2">
<div class="form-group"><label>Savings Goal ($)</label><input type="number" id="sgGoal" placeholder="e.g. 50000" step="1000"></div>
<div class="form-group"><label>Current Savings ($)</label><input type="number" id="sgCurrent" placeholder="e.g. 5000" step="500"></div>
<div class="form-group"><label>Timeframe (months)</label><input type="number" id="sgMonths" placeholder="e.g. 60" min="1"></div>
<div class="form-group"><label>Annual Interest Rate (%)</label><input type="number" id="sgRate" placeholder="e.g. 2.5" step="0.1"></div>
</div>
<div class="result-actions"><button class="btn btn-primary" onclick="calcSavingsGoal()"><i class="fas fa-calculator"></i> Calculate</button></div>
<div class="mt-16" style="display:grid;grid-template-columns:repeat(3,1fr);gap:12px;">
<div style="background:var(--bg-secondary);border-radius:var(--radius);padding:14px;text-align:center;"><div style="font-size:1.6rem;font-weight:700;color:var(--primary)" id="sgMonthly">$0</div><div style="font-size:.8rem;color:var(--text-muted)">Monthly Savings Needed</div></div>
<div style="background:var(--bg-secondary);border-radius:var(--radius);padding:14px;text-align:center;"><div style="font-size:1.2rem;font-weight:700;color:var(--secondary)" id="sgTotal">$0</div><div style="font-size:.8rem;color:var(--text-muted)">Total Saved</div></div>
<div style="background:var(--bg-secondary);border-radius:var(--radius);padding:14px;text-align:center;"><div style="font-size:1.2rem;font-weight:700;color:var(--accent)" id="sgEarned">$0</div><div style="font-size:.8rem;color:var(--text-muted)">Interest Earned</div></div>
</div>
''',
        "dividend-calculator": '''
<div class="form-row-2">
<div class="form-group"><label>Stock Price ($)</label><input type="number" id="divPrice" placeholder="e.g. 150" step="0.01"></div>
<div class="form-group"><label>Annual Dividend Per Share ($)</label><input type="number" id="divDPS" placeholder="e.g. 3.50" step="0.01"></div>
<div class="form-group"><label>Number of Shares</label><input type="number" id="divShares" placeholder="e.g. 200" min="1"></div>
<div class="form-group"><label>Dividend Growth Rate (%)</label><input type="number" id="divGrowth" placeholder="e.g. 5" step="0.5"></div>
</div>
<div class="result-actions"><button class="btn btn-primary" onclick="calcDividend()"><i class="fas fa-calculator"></i> Calculate</button></div>
<div class="mt-16" style="display:grid;grid-template-columns:repeat(4,1fr);gap:8px;">
<div style="background:var(--bg-secondary);border-radius:var(--radius);padding:12px;text-align:center;"><div style="font-weight:700;color:var(--primary)" id="divYield">0%</div><div style="font-size:.75rem;color:var(--text-muted)">Dividend Yield</div></div>
<div style="background:var(--bg-secondary);border-radius:var(--radius);padding:12px;text-align:center;"><div style="font-weight:700;color:var(--secondary)" id="divAnnual">$0</div><div style="font-size:.75rem;color:var(--text-muted)">Annual Income</div></div>
<div style="background:var(--bg-secondary);border-radius:var(--radius);padding:12px;text-align:center;"><div style="font-weight:700;color:var(--accent)" id="divMonthly">$0</div><div style="font-size:.75rem;color:var(--text-muted)">Monthly Income</div></div>
<div style="background:var(--bg-secondary);border-radius:var(--radius);padding:12px;text-align:center;"><div style="font-weight:700;color:var(--icon-1)" id="divProjected">$0</div><div style="font-size:.75rem;color:var(--text-muted)">5-Year Projected Income</div></div>
</div>
''',
        "crypto-profit-calculator": '''
<div class="form-row-2">
<div class="form-group"><label>Buy Price Per Coin ($)</label><input type="number" id="cryptoBuy" placeholder="e.g. 30000" step="100"></div>
<div class="form-group"><label>Sell Price Per Coin ($)</label><input type="number" id="cryptoSell" placeholder="e.g. 45000" step="100"></div>
<div class="form-group"><label>Quantity (coins)</label><input type="number" id="cryptoQty" placeholder="e.g. 0.5" step="0.01"></div>
<div class="form-group"><label>Total Trading Fee ($)</label><input type="number" id="cryptoFee" placeholder="e.g. 50" step="1"></div>
</div>
<div class="result-actions"><button class="btn btn-primary" onclick="calcCryptoProfit()"><i class="fas fa-calculator"></i> Calculate</button></div>
<div class="mt-16" style="display:grid;grid-template-columns:repeat(3,1fr);gap:12px;">
<div style="background:var(--bg-secondary);border-radius:var(--radius);padding:14px;text-align:center;"><div style="font-size:1.6rem;font-weight:700;color:var(--primary)" id="cryptoProfit">$0</div><div style="font-size:.8rem;color:var(--text-muted)">Profit/Loss</div></div>
<div style="background:var(--bg-secondary);border-radius:var(--radius);padding:14px;text-align:center;"><div style="font-size:1.4rem;font-weight:700;color:var(--secondary)" id="cryptoROI">0%</div><div style="font-size:.8rem;color:var(--text-muted)">ROI</div></div>
<div style="background:var(--bg-secondary);border-radius:var(--radius);padding:14px;text-align:center;"><div style="font-size:1.4rem;font-weight:700;color:var(--accent)" id="cryptoNet">$0</div><div style="font-size:.8rem;color:var(--text-muted)">Net Proceeds</div></div>
</div>
''',
        "budget-calculator": '''
<div class="form-group">
<label>Monthly After-Tax Income ($)</label>
<input type="number" id="budgetIncome" placeholder="e.g. 5000" step="100">
<div class="hint">Enter your take-home pay after taxes and deductions.</div>
</div>
<div class="result-actions"><button class="btn btn-primary" onclick="calcBudget()"><i class="fas fa-calculator"></i> Calculate Budget</button></div>
<div class="mt-16" style="display:grid;grid-template-columns:repeat(3,1fr);gap:12px;">
<div style="background:var(--bg-secondary);border-radius:var(--radius);padding:14px;text-align:center;"><div style="font-size:1.6rem;font-weight:700;color:var(--primary)" id="budgetNeeds">$0</div><div style="font-size:.8rem;color:var(--text-muted)">Needs (50%)</div><div class="hint" style="font-size:.75rem;">Housing, food, utilities</div></div>
<div style="background:var(--bg-secondary);border-radius:var(--radius);padding:14px;text-align:center;"><div style="font-size:1.6rem;font-weight:700;color:var(--secondary)" id="budgetWants">$0</div><div style="font-size:.8rem;color:var(--text-muted)">Wants (30%)</div><div class="hint" style="font-size:.75rem;">Entertainment, dining out</div></div>
<div style="background:var(--bg-secondary);border-radius:var(--radius);padding:14px;text-align:center;"><div style="font-size:1.6rem;font-weight:700;color:var(--accent)" id="budgetSavings">$0</div><div style="font-size:.8rem;color:var(--text-muted)">Savings (20%)</div><div class="hint" style="font-size:.75rem;">Debt, investing, goals</div></div>
</div>
''',
        "salary-calculator": '''
<div class="form-group">
<label>Enter Salary</label>
<div style="display:flex;gap:10px;flex-wrap:wrap;margin-top:6px;">
<label class="btn btn-secondary btn-sm" style="cursor:pointer"><input type="radio" name="salMode" value="hourly" checked style="display:none"> Hourly</label>
<label class="btn btn-secondary btn-sm" style="cursor:pointer"><input type="radio" name="salMode" value="weekly" style="display:none"> Weekly</label>
<label class="btn btn-secondary btn-sm" style="cursor:pointer"><input type="radio" name="salMode" value="monthly" style="display:none"> Monthly</label>
<label class="btn btn-secondary btn-sm" style="cursor:pointer"><input type="radio" name="salMode" value="annual" style="display:none"> Annual</label>
</div>
</div>
<div class="form-row-2">
<div class="form-group"><label>Value ($)</label><input type="number" id="salValue" placeholder="e.g. 25" step="0.5"></div>
<div class="form-group"><label>Hours per Week</label><input type="number" id="salHours" value="40" min="1" max="168"></div>
<div class="form-group"><label>Days per Week</label><input type="number" id="salDays" value="5" min="1" max="7"></div>
</div>
<div class="result-actions"><button class="btn btn-primary" onclick="calcSalary()"><i class="fas fa-calculator"></i> Convert</button></div>
<div class="mt-16" style="display:grid;grid-template-columns:repeat(4,1fr);gap:8px;">
<div style="background:var(--bg-secondary);border-radius:var(--radius);padding:12px;text-align:center;"><div style="font-weight:700;color:var(--primary)" id="salHourly">$0</div><div style="font-size:.75rem;color:var(--text-muted)">Hourly</div></div>
<div style="background:var(--bg-secondary);border-radius:var(--radius);padding:12px;text-align:center;"><div style="font-weight:700;color:var(--secondary)" id="salWeekly">$0</div><div style="font-size:.75rem;color:var(--text-muted)">Weekly</div></div>
<div style="background:var(--bg-secondary);border-radius:var(--radius);padding:12px;text-align:center;"><div style="font-weight:700;color:var(--accent)" id="salMonthly">$0</div><div style="font-size:.75rem;color:var(--text-muted)">Monthly</div></div>
<div style="background:var(--bg-secondary);border-radius:var(--radius);padding:12px;text-align:center;"><div style="font-weight:700;color:var(--icon-1)" id="salAnnual">$0</div><div style="font-size:.75rem;color:var(--text-muted)">Annual</div></div>
</div>
''',
        "bill-split-calculator": '''
<div class="form-row-2">
<div class="form-group"><label>Total Bill ($)</label><input type="number" id="billTotal" placeholder="e.g. 85.50" step="0.01"></div>
<div class="form-group"><label>Number of People</label><input type="number" id="billPeople" placeholder="e.g. 4" min="1"></div>
<div class="form-group"><label>Tip Percentage (%)</label><input type="number" id="billTip" placeholder="e.g. 18" step="1"></div>
</div>
<div class="result-actions"><button class="btn btn-primary" onclick="calcBillSplit()"><i class="fas fa-calculator"></i> Split Bill</button></div>
<div class="mt-16" style="display:grid;grid-template-columns:repeat(3,1fr);gap:12px;">
<div style="background:var(--bg-secondary);border-radius:var(--radius);padding:14px;text-align:center;"><div style="font-size:1.2rem;font-weight:700;color:var(--primary)" id="billTipAmt">$0</div><div style="font-size:.8rem;color:var(--text-muted)">Tip Amount</div></div>
<div style="background:var(--bg-secondary);border-radius:var(--radius);padding:14px;text-align:center;"><div style="font-size:1.2rem;font-weight:700;color:var(--secondary)" id="billGrand">$0</div><div style="font-size:.8rem;color:var(--text-muted)">Total with Tip</div></div>
<div style="background:var(--bg-secondary);border-radius:var(--radius);padding:14px;text-align:center;"><div style="font-size:1.6rem;font-weight:700;color:var(--accent)" id="billEach">$0</div><div style="font-size:.8rem;color:var(--text-muted)">Per Person</div></div>
</div>
''',
        "tip-calculator": '''
<div class="form-row-2">
<div class="form-group"><label>Bill Amount ($)</label><input type="number" id="tipBill" placeholder="e.g. 65.00" step="0.01"></div>
<div class="form-group"><label>Tip Percentage (%)</label>
<select id="tipPct" style="padding:8px;border:1px solid var(--border);border-radius:var(--radius);background:var(--bg-primary);color:var(--text-primary);width:100%;">
<option value="10">10%</option><option value="15" selected>15%</option><option value="18">18%</option><option value="20">20%</option><option value="25">25%</option></select></div>
<div class="form-group"><label>Split Between</label><input type="number" id="tipPeople" value="1" min="1" placeholder="1"></div>
</div>
<div class="result-actions"><button class="btn btn-primary" onclick="calcTip()"><i class="fas fa-calculator"></i> Calculate</button></div>
<div class="mt-16" style="display:grid;grid-template-columns:repeat(3,1fr);gap:12px;">
<div style="background:var(--bg-secondary);border-radius:var(--radius);padding:14px;text-align:center;"><div style="font-size:1.4rem;font-weight:700;color:var(--primary)" id="tipAmount">$0</div><div style="font-size:.8rem;color:var(--text-muted)">Tip Amount</div></div>
<div style="background:var(--bg-secondary);border-radius:var(--radius);padding:14px;text-align:center;"><div style="font-size:1.4rem;font-weight:700;color:var(--secondary)" id="tipTotal">$0</div><div style="font-size:.8rem;color:var(--text-muted)">Total Bill</div></div>
<div style="background:var(--bg-secondary);border-radius:var(--radius);padding:14px;text-align:center;"><div style="font-size:1.4rem;font-weight:700;color:var(--accent)" id="tipEach">$0</div><div style="font-size:.8rem;color:var(--text-muted)">Per Person</div></div>
</div>
''',
        "inflation-calculator": '''
<div class="form-row-2">
<div class="form-group"><label>Amount ($)</label><input type="number" id="infAmount" placeholder="e.g. 100" step="1"></div>
<div class="form-group"><label>Start Year</label><select id="infStartYear" style="padding:8px;border:1px solid var(--border);border-radius:var(--radius);background:var(--bg-primary);color:var(--text-primary);width:100%;"><option value="1913">1913</option>
<option value="1914">1914</option>
<option value="1915">1915</option>
<option value="1916">1916</option>
<option value="1917">1917</option>
<option value="1918">1918</option>
<option value="1919">1919</option>
<option value="1920">1920</option>
<option value="1921">1921</option>
<option value="1922">1922</option>
<option value="1923">1923</option>
<option value="1924">1924</option>
<option value="1925">1925</option>
<option value="1926">1926</option>
<option value="1927">1927</option>
<option value="1928">1928</option>
<option value="1929">1929</option>
<option value="1930">1930</option>
<option value="1931">1931</option>
<option value="1932">1932</option>
<option value="1933">1933</option>
<option value="1934">1934</option>
<option value="1935">1935</option>
<option value="1936">1936</option>
<option value="1937">1937</option>
<option value="1938">1938</option>
<option value="1939">1939</option>
<option value="1940">1940</option>
<option value="1941">1941</option>
<option value="1942">1942</option>
<option value="1943">1943</option>
<option value="1944">1944</option>
<option value="1945">1945</option>
<option value="1946">1946</option>
<option value="1947">1947</option>
<option value="1948">1948</option>
<option value="1949">1949</option>
<option value="1950">1950</option>
<option value="1951">1951</option>
<option value="1952">1952</option>
<option value="1953">1953</option>
<option value="1954">1954</option>
<option value="1955">1955</option>
<option value="1956">1956</option>
<option value="1957">1957</option>
<option value="1958">1958</option>
<option value="1959">1959</option>
<option value="1960">1960</option>
<option value="1961">1961</option>
<option value="1962">1962</option>
<option value="1963">1963</option>
<option value="1964">1964</option>
<option value="1965">1965</option>
<option value="1966">1966</option>
<option value="1967">1967</option>
<option value="1968">1968</option>
<option value="1969">1969</option>
<option value="1970">1970</option>
<option value="1971">1971</option>
<option value="1972">1972</option>
<option value="1973">1973</option>
<option value="1974">1974</option>
<option value="1975">1975</option>
<option value="1976">1976</option>
<option value="1977">1977</option>
<option value="1978">1978</option>
<option value="1979">1979</option>
<option value="1980">1980</option>
<option value="1981">1981</option>
<option value="1982">1982</option>
<option value="1983">1983</option>
<option value="1984">1984</option>
<option value="1985">1985</option>
<option value="1986">1986</option>
<option value="1987">1987</option>
<option value="1988">1988</option>
<option value="1989">1989</option>
<option value="1990">1990</option>
<option value="1991">1991</option>
<option value="1992">1992</option>
<option value="1993">1993</option>
<option value="1994">1994</option>
<option value="1995">1995</option>
<option value="1996">1996</option>
<option value="1997">1997</option>
<option value="1998">1998</option>
<option value="1999">1999</option>
<option value="2000">2000</option>
<option value="2001">2001</option>
<option value="2002">2002</option>
<option value="2003">2003</option>
<option value="2004">2004</option>
<option value="2005">2005</option>
<option value="2006">2006</option>
<option value="2007">2007</option>
<option value="2008">2008</option>
<option value="2009">2009</option>
<option value="2010">2010</option>
<option value="2011">2011</option>
<option value="2012">2012</option>
<option value="2013">2013</option>
<option value="2014">2014</option>
<option value="2015">2015</option>
<option value="2016">2016</option>
<option value="2017">2017</option>
<option value="2018">2018</option>
<option value="2019">2019</option>
<option value="2020">2020</option>
<option value="2021">2021</option>
<option value="2022">2022</option>
<option value="2023">2023</option>
<option value="2024">2024</option>
<option value="2025">2025</option></select></div>
<div class="form-group"><label>End Year</label><select id="infEndYear" style="padding:8px;border:1px solid var(--border);border-radius:var(--radius);background:var(--bg-primary);color:var(--text-primary);width:100%;"><option value="1913">1913</option>
<option value="1914">1914</option>
<option value="1915">1915</option>
<option value="1916">1916</option>
<option value="1917">1917</option>
<option value="1918">1918</option>
<option value="1919">1919</option>
<option value="1920">1920</option>
<option value="1921">1921</option>
<option value="1922">1922</option>
<option value="1923">1923</option>
<option value="1924">1924</option>
<option value="1925">1925</option>
<option value="1926">1926</option>
<option value="1927">1927</option>
<option value="1928">1928</option>
<option value="1929">1929</option>
<option value="1930">1930</option>
<option value="1931">1931</option>
<option value="1932">1932</option>
<option value="1933">1933</option>
<option value="1934">1934</option>
<option value="1935">1935</option>
<option value="1936">1936</option>
<option value="1937">1937</option>
<option value="1938">1938</option>
<option value="1939">1939</option>
<option value="1940">1940</option>
<option value="1941">1941</option>
<option value="1942">1942</option>
<option value="1943">1943</option>
<option value="1944">1944</option>
<option value="1945">1945</option>
<option value="1946">1946</option>
<option value="1947">1947</option>
<option value="1948">1948</option>
<option value="1949">1949</option>
<option value="1950">1950</option>
<option value="1951">1951</option>
<option value="1952">1952</option>
<option value="1953">1953</option>
<option value="1954">1954</option>
<option value="1955">1955</option>
<option value="1956">1956</option>
<option value="1957">1957</option>
<option value="1958">1958</option>
<option value="1959">1959</option>
<option value="1960">1960</option>
<option value="1961">1961</option>
<option value="1962">1962</option>
<option value="1963">1963</option>
<option value="1964">1964</option>
<option value="1965">1965</option>
<option value="1966">1966</option>
<option value="1967">1967</option>
<option value="1968">1968</option>
<option value="1969">1969</option>
<option value="1970">1970</option>
<option value="1971">1971</option>
<option value="1972">1972</option>
<option value="1973">1973</option>
<option value="1974">1974</option>
<option value="1975">1975</option>
<option value="1976">1976</option>
<option value="1977">1977</option>
<option value="1978">1978</option>
<option value="1979">1979</option>
<option value="1980">1980</option>
<option value="1981">1981</option>
<option value="1982">1982</option>
<option value="1983">1983</option>
<option value="1984">1984</option>
<option value="1985">1985</option>
<option value="1986">1986</option>
<option value="1987">1987</option>
<option value="1988">1988</option>
<option value="1989">1989</option>
<option value="1990">1990</option>
<option value="1991">1991</option>
<option value="1992">1992</option>
<option value="1993">1993</option>
<option value="1994">1994</option>
<option value="1995">1995</option>
<option value="1996">1996</option>
<option value="1997">1997</option>
<option value="1998">1998</option>
<option value="1999">1999</option>
<option value="2000">2000</option>
<option value="2001">2001</option>
<option value="2002">2002</option>
<option value="2003">2003</option>
<option value="2004">2004</option>
<option value="2005">2005</option>
<option value="2006">2006</option>
<option value="2007">2007</option>
<option value="2008">2008</option>
<option value="2009">2009</option>
<option value="2010">2010</option>
<option value="2011">2011</option>
<option value="2012">2012</option>
<option value="2013">2013</option>
<option value="2014">2014</option>
<option value="2015">2015</option>
<option value="2016">2016</option>
<option value="2017">2017</option>
<option value="2018">2018</option>
<option value="2019">2019</option>
<option value="2020">2020</option>
<option value="2021">2021</option>
<option value="2022">2022</option>
<option value="2023">2023</option>
<option value="2024">2024</option>
<option value="2025" selected>2025</option></select></div>
</div>
<div class="result-actions"><button class="btn btn-primary" onclick="calcInflation()"><i class="fas fa-calculator"></i> Calculate</button></div>
<div class="result-box" id="infResult" style="font-size:1.2rem;text-align:center;"></div>
<p class="hint mt-8" id="infChange" style="text-align:center;"></p>
''',
        "income-tax-calculator": '''
<div class="form-row-2">
<div class="form-group"><label>Annual Income ($)</label><input type="number" id="taxIncome" placeholder="e.g. 75000" step="1000"></div>
<div class="form-group"><label>Filing Status</label><select id="taxStatus" style="padding:8px;border:1px solid var(--border);border-radius:var(--radius);background:var(--bg-primary);color:var(--text-primary);width:100%;">
<option value="single">Single</option><option value="married">Married Filing Jointly</option><option value="head">Head of Household</option></select></div>
<div class="form-group"><label>Total Deductions ($, 0 = use standard)</label><input type="number" id="taxDed" placeholder="e.g. 0" step="100"></div>
</div>
<div class="result-actions"><button class="btn btn-primary" onclick="calcIncomeTax()"><i class="fas fa-calculator"></i> Calculate Tax</button></div>
<div class="mt-16" style="display:grid;grid-template-columns:repeat(5,1fr);gap:8px;">
<div style="background:var(--bg-secondary);border-radius:var(--radius);padding:10px;text-align:center;"><div style="font-weight:700;color:var(--primary)" id="taxGross">$0</div><div style="font-size:.7rem;color:var(--text-muted)">Gross Income</div></div>
<div style="background:var(--bg-secondary);border-radius:var(--radius);padding:10px;text-align:center;"><div style="font-weight:700;color:var(--secondary)" id="taxDeduction">$0</div><div style="font-size:.7rem;color:var(--text-muted)">Deductions</div></div>
<div style="background:var(--bg-secondary);border-radius:var(--radius);padding:10px;text-align:center;"><div style="font-weight:700;color:var(--accent)" id="taxTaxable">$0</div><div style="font-size:.7rem;color:var(--text-muted)">Taxable Income</div></div>
<div style="background:var(--bg-secondary);border-radius:var(--radius);padding:10px;text-align:center;"><div style="font-weight:700;color:var(--icon-1)" id="taxTotal">$0</div><div style="font-size:.7rem;color:var(--text-muted)">Estimated Tax</div></div>
<div style="background:var(--bg-secondary);border-radius:var(--radius);padding:10px;text-align:center;"><div style="font-weight:700;color:var(--icon-4)" id="taxRate">0%</div><div style="font-size:.7rem;color:var(--text-muted)">Effective Rate</div></div>
</div>
''',
        "sales-tax-calculator": '''
<div class="form-row-2">
<div class="form-group"><label>Purchase Price ($)</label><input type="number" id="stPrice" placeholder="e.g. 99.99" step="0.01"></div>
<div class="form-group"><label>Sales Tax Rate (%)</label><input type="number" id="stRate" placeholder="e.g. 8.25" step="0.25"></div>
</div>
<div class="result-actions"><button class="btn btn-primary" onclick="calcSalesTax()"><i class="fas fa-calculator"></i> Calculate</button></div>
<div class="mt-16" style="display:grid;grid-template-columns:repeat(3,1fr);gap:12px;">
<div style="background:var(--bg-secondary);border-radius:var(--radius);padding:14px;text-align:center;"><div style="font-size:1.4rem;font-weight:700;color:var(--primary)" id="stTax">$0</div><div style="font-size:.8rem;color:var(--text-muted)">Sales Tax</div></div>
<div style="background:var(--bg-secondary);border-radius:var(--radius);padding:14px;text-align:center;"><div style="font-size:1.4rem;font-weight:700;color:var(--secondary)" id="stTotal">$0</div><div style="font-size:.8rem;color:var(--text-muted)">Total Cost</div></div>
<div style="background:var(--bg-secondary);border-radius:var(--radius);padding:14px;text-align:center;"><div style="font-size:1.2rem;font-weight:700;color:var(--accent)" id="stPct">0%</div><div style="font-size:.8rem;color:var(--text-muted)">Tax Rate</div></div>
</div>
''',
        "capital-gains-calculator": '''
<div class="form-row-2">
<div class="form-group"><label>Purchase Price ($)</label><input type="number" id="cgBuy" placeholder="e.g. 10000" step="100"></div>
<div class="form-group"><label>Sale Price ($)</label><input type="number" id="cgSell" placeholder="e.g. 15000" step="100"></div>
<div class="form-group"><label>Holding Period</label><select id="cgHeld" style="padding:8px;border:1px solid var(--border);border-radius:var(--radius);background:var(--bg-primary);color:var(--text-primary);width:100%;">
<option value="long">Long-Term (Over 1 Year)</option><option value="short">Short-Term (1 Year or Less)</option></select></div>
<div class="form-group"><label>Annual Taxable Income ($)</label><input type="number" id="cgIncome" placeholder="e.g. 80000" step="1000"></div>
</div>
<div class="result-actions"><button class="btn btn-primary" onclick="calcCapGains()"><i class="fas fa-calculator"></i> Calculate</button></div>
<div class="mt-16" style="display:grid;grid-template-columns:repeat(4,1fr);gap:8px;">
<div style="background:var(--bg-secondary);border-radius:var(--radius);padding:12px;text-align:center;"><div style="font-weight:700;color:var(--primary)" id="cgGain">$0</div><div style="font-size:.75rem;color:var(--text-muted)">Total Gain</div></div>
<div style="background:var(--bg-secondary);border-radius:var(--radius);padding:12px;text-align:center;"><div style="font-weight:700;color:var(--secondary)" id="cgTax">$0</div><div style="font-size:.75rem;color:var(--text-muted)">Tax Owed</div></div>
<div style="background:var(--bg-secondary);border-radius:var(--radius);padding:12px;text-align:center;"><div style="font-weight:700;color:var(--accent)" id="cgType">-</div><div style="font-size:.75rem;color:var(--text-muted)">Tax Type</div></div>
<div style="background:var(--bg-secondary);border-radius:var(--radius);padding:12px;text-align:center;"><div style="font-weight:700;color:var(--icon-1)" id="cgNet">$0</div><div style="font-size:.75rem;color:var(--text-muted)">After-Tax Profit</div></div>
</div>
''',
        "vat-calculator": '''
<div class="form-group">
<label>Calculation Mode</label>
<div style="display:flex;gap:10px;flex-wrap:wrap;margin-top:6px;">
<label class="btn btn-secondary btn-sm" style="cursor:pointer"><input type="radio" name="vatMode" value="exclusive" checked style="display:none"> Add VAT (Price excl. VAT)</label>
<label class="btn btn-secondary btn-sm" style="cursor:pointer"><input type="radio" name="vatMode" value="inclusive" style="display:none"> Remove VAT (Price incl. VAT)</label>
</div>
</div>
<div class="form-row-2">
<div class="form-group"><label>Price ($)</label><input type="number" id="vatPrice" placeholder="e.g. 100" step="0.01"></div>
<div class="form-group"><label>VAT Rate (%)</label><input type="number" id="vatRate" value="20" placeholder="e.g. 20" step="0.5"></div>
</div>
<div class="result-actions"><button class="btn btn-primary" onclick="calcVAT()"><i class="fas fa-calculator"></i> Calculate</button></div>
<div class="mt-16" style="display:grid;grid-template-columns:repeat(3,1fr);gap:12px;">
<div style="background:var(--bg-secondary);border-radius:var(--radius);padding:14px;text-align:center;"><div style="font-size:1.4rem;font-weight:700;color:var(--primary)" id="vatExclusive">$0</div><div style="font-size:.8rem;color:var(--text-muted)">Price Excl. VAT</div></div>
<div style="background:var(--bg-secondary);border-radius:var(--radius);padding:14px;text-align:center;"><div style="font-size:1.4rem;font-weight:700;color:var(--secondary)" id="vatTax">$0</div><div style="font-size:.8rem;color:var(--text-muted)">VAT Amount</div></div>
<div style="background:var(--bg-secondary);border-radius:var(--radius);padding:14px;text-align:center;"><div style="font-size:1.4rem;font-weight:700;color:var(--accent)" id="vatInclusive">$0</div><div style="font-size:.8rem;color:var(--text-muted)">Price Incl. VAT</div></div>
</div>
''',
        "property-tax-calculator": '''
<div class="form-row-2">
<div class="form-group"><label>Property Value ($)</label><input type="number" id="ptValue" placeholder="e.g. 350000" step="10000"></div>
<div class="form-group"><label>Tax Rate (%)</label><input type="number" id="ptRate" placeholder="e.g. 1.25" step="0.05"></div>
</div>
<div class="result-actions"><button class="btn btn-primary" onclick="calcPropertyTax()"><i class="fas fa-calculator"></i> Calculate</button></div>
<div class="mt-16" style="display:grid;grid-template-columns:repeat(3,1fr);gap:12px;">
<div style="background:var(--bg-secondary);border-radius:var(--radius);padding:14px;text-align:center;"><div style="font-size:1.6rem;font-weight:700;color:var(--primary)" id="ptAnnual">$0</div><div style="font-size:.8rem;color:var(--text-muted)">Annual Tax</div></div>
<div style="background:var(--bg-secondary);border-radius:var(--radius);padding:14px;text-align:center;"><div style="font-size:1.4rem;font-weight:700;color:var(--secondary)" id="ptMonthly">$0</div><div style="font-size:.8rem;color:var(--text-muted)">Monthly Cost</div></div>
<div style="background:var(--bg-secondary);border-radius:var(--radius);padding:14px;text-align:center;"><div style="font-size:1.2rem;font-weight:700;color:var(--accent)" id="ptFiveYear">$0</div><div style="font-size:.8rem;color:var(--text-muted)">Over 5 Years</div></div>
</div>
''',
        "currency-converter": '''
<div class="form-row-2">
<div class="form-group"><label>Amount</label><input type="number" id="fxAmount" placeholder="e.g. 100" step="1"></div>
<div class="form-group"><label>From</label><select id="fxFrom" style="padding:8px;border:1px solid var(--border);border-radius:var(--radius);background:var(--bg-primary);color:var(--text-primary);width:100%;">
<option value="USD">USD - US Dollar</option><option value="EUR">EUR - Euro</option><option value="GBP">GBP - British Pound</option><option value="JPY">JPY - Japanese Yen</option><option value="CNY">CNY - Chinese Yuan</option><option value="CAD">CAD - Canadian Dollar</option><option value="AUD">AUD - Australian Dollar</option><option value="INR">INR - Indian Rupee</option><option value="KRW">KRW - South Korean Won</option><option value="SGD">SGD - Singapore Dollar</option></select></div>
<div class="form-group"><label>To</label><select id="fxTo" style="padding:8px;border:1px solid var(--border);border-radius:var(--radius);background:var(--bg-primary);color:var(--text-primary);width:100%;">
<option value="EUR">EUR - Euro</option><option value="USD" selected>USD - US Dollar</option><option value="GBP">GBP - British Pound</option><option value="JPY">JPY - Japanese Yen</option><option value="CNY">CNY - Chinese Yuan</option><option value="CAD">CAD - Canadian Dollar</option><option value="AUD">AUD - Australian Dollar</option><option value="INR">INR - Indian Rupee</option><option value="KRW">KRW - South Korean Won</option><option value="SGD">SGD - Singapore Dollar</option></select></div>
</div>
<div class="result-actions">
<button class="btn btn-primary" onclick="convertCurrency()"><i class="fas fa-exchange-alt"></i> Convert</button>
<button class="btn btn-secondary btn-sm" onclick="swapCurrency()"><i class="fas fa-arrows-alt-h"></i> Swap</button>
</div>
<div class="result-box" id="fxResult" style="font-size:1.3rem;text-align:center;"></div>
<p class="hint mt-8" id="fxRate" style="text-align:center;"></p>
''',
        "fraction-calculator": '''
<div class="form-group">
<label>Operation</label>
<div style="display:flex;gap:10px;flex-wrap:wrap;margin-top:6px;">
<label class="btn btn-secondary btn-sm" style="cursor:pointer"><input type="radio" name="fracOp" value="add" checked style="display:none"> +</label>
<label class="btn btn-secondary btn-sm" style="cursor:pointer"><input type="radio" name="fracOp" value="sub" style="display:none"> -</label>
<label class="btn btn-secondary btn-sm" style="cursor:pointer"><input type="radio" name="fracOp" value="mul" style="display:none"> x</label>
<label class="btn btn-secondary btn-sm" style="cursor:pointer"><input type="radio" name="fracOp" value="div" style="display:none"> /</label>
</div>
</div>
<div class="form-row-2">
<div class="form-group"><label>First Fraction</label><div style="display:flex;gap:8px;align-items:center;"><input type="number" id="fracNum1" placeholder="Num" style="width:80px;padding:8px;border:1px solid var(--border);border-radius:var(--radius);background:var(--bg-primary);color:var(--text-primary);"> <span style="font-size:1.2rem;">/</span> <input type="number" id="fracDen1" placeholder="Den" value="1" style="width:80px;padding:8px;border:1px solid var(--border);border-radius:var(--radius);background:var(--bg-primary);color:var(--text-primary);"></div></div>
<div class="form-group"><label>Second Fraction</label><div style="display:flex;gap:8px;align-items:center;"><input type="number" id="fracNum2" placeholder="Num" style="width:80px;padding:8px;border:1px solid var(--border);border-radius:var(--radius);background:var(--bg-primary);color:var(--text-primary);"> <span style="font-size:1.2rem;">/</span> <input type="number" id="fracDen2" placeholder="Den" value="1" style="width:80px;padding:8px;border:1px solid var(--border);border-radius:var(--radius);background:var(--bg-primary);color:var(--text-primary);"></div></div>
</div>
<div class="result-actions"><button class="btn btn-primary" onclick="calcFraction()"><i class="fas fa-calculator"></i> Calculate</button></div>
<div class="mt-16" style="display:grid;grid-template-columns:repeat(3,1fr);gap:12px;">
<div style="background:var(--bg-secondary);border-radius:var(--radius);padding:14px;text-align:center;"><div style="font-size:1.6rem;font-weight:700;color:var(--primary)" id="fracResult">-</div><div style="font-size:.8rem;color:var(--text-muted)">Result (simplified)</div></div>
<div style="background:var(--bg-secondary);border-radius:var(--radius);padding:14px;text-align:center;"><div style="font-size:1.2rem;font-weight:700;color:var(--secondary)" id="fracDecimal">-</div><div style="font-size:.8rem;color:var(--text-muted)">Decimal</div></div>
<div style="background:var(--bg-secondary);border-radius:var(--radius);padding:14px;text-align:center;"><div style="font-size:1.2rem;font-weight:700;color:var(--accent)" id="fracMixed">-</div><div style="font-size:.8rem;color:var(--text-muted)">Mixed Number</div></div>
</div>
''',
        "percentage-calculator": '''
<div class="form-group">
<label>Calculation Mode</label>
<div style="display:flex;gap:10px;flex-wrap:wrap;margin-top:6px;">
<label class="btn btn-secondary btn-sm" style="cursor:pointer"><input type="radio" name="pctMode" value="pct-of" checked onchange="clearPct()" style="display:none"> X% of Y</label>
<label class="btn btn-secondary btn-sm" style="cursor:pointer"><input type="radio" name="pctMode" value="what-pct" onchange="clearPct()" style="display:none"> X is what % of Y</label>
<label class="btn btn-secondary btn-sm" style="cursor:pointer"><input type="radio" name="pctMode" value="pct-change" onchange="clearPct()" style="display:none"> % Change</label>
</div>
</div>
<div class="form-row-2">
<div class="form-group"><label>Value 1 (X)</label><input type="number" id="pctVal1" placeholder="e.g. 15"></div>
<div class="form-group"><label>Value 2 (Y)</label><input type="number" id="pctVal2" placeholder="e.g. 200"></div>
</div>
<div class="result-actions">
<button class="btn btn-primary" onclick="calcPercentage()"><i class="fas fa-calculator"></i> Calculate</button>
<button class="btn btn-secondary btn-sm" onclick="clearPct()"><i class="fas fa-times"></i> Clear</button>
</div>
<div class="result-box" id="pctResult" style="font-size:1.3rem;text-align:center;"></div>
<p class="hint mt-8" id="pctSteps" style="text-align:center;"></p>
''',
        "time-calculator": '''
<div class="form-group">
<label>Operation</label>
<div style="display:flex;gap:10px;flex-wrap:wrap;margin-top:6px;">
<label class="btn btn-secondary btn-sm" style="cursor:pointer"><input type="radio" name="timeOp" value="add" checked style="display:none"> Add</label>
<label class="btn btn-secondary btn-sm" style="cursor:pointer"><input type="radio" name="timeOp" value="sub" style="display:none"> Subtract</label>
</div>
</div>
<div class="form-row-2">
<div class="form-group"><label>Time 1</label><div style="display:flex;gap:6px;"><input type="number" id="timeH1" placeholder="H" min="0" style="width:60px;padding:8px;border:1px solid var(--border);border-radius:var(--radius);background:var(--bg-primary);color:var(--text-primary);">h <input type="number" id="timeM1" placeholder="M" min="0" max="59" style="width:60px;padding:8px;border:1px solid var(--border);border-radius:var(--radius);background:var(--bg-primary);color:var(--text-primary);">m <input type="number" id="timeS1" placeholder="S" min="0" max="59" style="width:60px;padding:8px;border:1px solid var(--border);border-radius:var(--radius);background:var(--bg-primary);color:var(--text-primary);">s</div></div>
<div class="form-group"><label>Time 2</label><div style="display:flex;gap:6px;"><input type="number" id="timeH2" placeholder="H" min="0" style="width:60px;padding:8px;border:1px solid var(--border);border-radius:var(--radius);background:var(--bg-primary);color:var(--text-primary);">h <input type="number" id="timeM2" placeholder="M" min="0" max="59" style="width:60px;padding:8px;border:1px solid var(--border);border-radius:var(--radius);background:var(--bg-primary);color:var(--text-primary);">m <input type="number" id="timeS2" placeholder="S" min="0" max="59" style="width:60px;padding:8px;border:1px solid var(--border);border-radius:var(--radius);background:var(--bg-primary);color:var(--text-primary);">s</div></div>
</div>
<div class="result-actions"><button class="btn btn-primary" onclick="calcTime()"><i class="fas fa-calculator"></i> Calculate</button></div>
<div class="mt-16" style="display:grid;grid-template-columns:repeat(4,1fr);gap:8px;">
<div style="background:var(--bg-secondary);border-radius:var(--radius);padding:12px;text-align:center;"><div style="font-weight:700;font-size:1.4rem;color:var(--primary)" id="timeResult">-</div><div style="font-size:.75rem;color:var(--text-muted)">Duration (H:M:S)</div></div>
<div style="background:var(--bg-secondary);border-radius:var(--radius);padding:12px;text-align:center;"><div style="font-weight:700;color:var(--secondary)" id="timeHours">-</div><div style="font-size:.75rem;color:var(--text-muted)">Hours</div></div>
<div style="background:var(--bg-secondary);border-radius:var(--radius);padding:12px;text-align:center;"><div style="font-weight:700;color:var(--accent)" id="timeMinutes">-</div><div style="font-size:.75rem;color:var(--text-muted)">Minutes</div></div>
<div style="background:var(--bg-secondary);border-radius:var(--radius);padding:12px;text-align:center;"><div style="font-weight:700;color:var(--icon-1)" id="timeSeconds">-</div><div style="font-size:.75rem;color:var(--text-muted)">Seconds</div></div>
</div>
''',
        "roi-calculator": '''
<div class="form-row-2">
<div class="form-group"><label>Amount Invested ($)</label><input type="number" id="roiInvested" placeholder="e.g. 10000" step="500"></div>
<div class="form-group"><label>Total Return Received ($)</label><input type="number" id="roiReturn" placeholder="e.g. 15000" step="500"></div>
<div class="form-group"><label>Investment Period (years)</label><input type="number" id="roiYears" placeholder="e.g. 3" min="1" step="0.5"></div>
</div>
<div class="result-actions"><button class="btn btn-primary" onclick="calcROI()"><i class="fas fa-calculator"></i> Calculate ROI</button></div>
<div class="mt-16" style="display:grid;grid-template-columns:repeat(3,1fr);gap:12px;">
<div style="background:var(--bg-secondary);border-radius:var(--radius);padding:14px;text-align:center;"><div style="font-size:1.6rem;font-weight:700;color:var(--primary)" id="roiProfit">$0</div><div style="font-size:.8rem;color:var(--text-muted)">Net Profit</div></div>
<div style="background:var(--bg-secondary);border-radius:var(--radius);padding:14px;text-align:center;"><div style="font-size:1.6rem;font-weight:700;color:var(--secondary)" id="roiPct">0%</div><div style="font-size:.8rem;color:var(--text-muted)">Total ROI</div></div>
<div style="background:var(--bg-secondary);border-radius:var(--radius);padding:14px;text-align:center;"><div style="font-size:1.2rem;font-weight:700;color:var(--accent)" id="roiAnnual">0%</div><div style="font-size:.8rem;color:var(--text-muted)">Annualized ROI</div></div>
</div>
''',
        "net-worth-calculator": '''
<div class="form-group"><label style="font-weight:700;color:var(--primary)">Assets</label></div>
<div class="form-row-2">
<div class="form-group"><label>Cash & Bank Accounts ($)</label><input type="number" id="nwCash" placeholder="e.g. 10000" step="1000"></div>
<div class="form-group"><label>Investments ($)</label><input type="number" id="nwInvestments" placeholder="e.g. 50000" step="5000"></div>
<div class="form-group"><label>Property Value ($)</label><input type="number" id="nwProperty" placeholder="e.g. 300000" step="10000"></div>
<div class="form-group"><label>Vehicle Value ($)</label><input type="number" id="nwVehicle" placeholder="e.g. 20000" step="5000"></div>
<div class="form-group"><label>Other Assets ($)</label><input type="number" id="nwOther" placeholder="e.g. 5000" step="1000"></div>
</div>
<div class="form-group"><label style="font-weight:700;color:var(--accent)">Liabilities</label></div>
<div class="form-row-2">
<div class="form-group"><label>Mortgage Balance ($)</label><input type="number" id="nwMortgage" placeholder="e.g. 200000" step="10000"></div>
<div class="form-group"><label>Other Loans ($)</label><input type="number" id="nwLoans" placeholder="e.g. 15000" step="1000"></div>
<div class="form-group"><label>Credit Card Debt ($)</label><input type="number" id="nwCards" placeholder="e.g. 3000" step="500"></div>
<div class="form-group"><label>Other Debts ($)</label><input type="number" id="nwOtherDebt" placeholder="e.g. 2000" step="500"></div>
</div>
<div class="result-actions"><button class="btn btn-primary" onclick="calcNetWorth()"><i class="fas fa-calculator"></i> Calculate Net Worth</button></div>
<div class="mt-16" style="display:grid;grid-template-columns:repeat(3,1fr);gap:12px;">
<div style="background:var(--bg-secondary);border-radius:var(--radius);padding:14px;text-align:center;"><div style="font-size:1.6rem;font-weight:700;color:var(--primary)" id="nwAssets">$0</div><div style="font-size:.8rem;color:var(--text-muted)">Total Assets</div></div>
<div style="background:var(--bg-secondary);border-radius:var(--radius);padding:14px;text-align:center;"><div style="font-size:1.6rem;font-weight:700;color:var(--accent)" id="nwLiabilities">$0</div><div style="font-size:.8rem;color:var(--text-muted)">Total Liabilities</div></div>
<div style="background:var(--bg-secondary);border-radius:var(--radius);padding:14px;text-align:center;"><div style="font-size:1.8rem;font-weight:700;color:var(--secondary)" id="nwNetWorth">$0</div><div style="font-size:.8rem;color:var(--text-muted)">Net Worth</div></div>
</div>
''',
        "college-savings-calculator": '''
<div class="form-row-2">
<div class="form-group"><label>Child's Current Age</label><input type="number" id="csAge" placeholder="e.g. 5" min="0"></div>
<div class="form-group"><label>College Start Age</label><input type="number" id="csStart" placeholder="e.g. 18" min="1"></div>
<div class="form-group"><label>Current Annual College Cost ($)</label><input type="number" id="csCost" placeholder="e.g. 25000" step="1000"></div>
<div class="form-group"><label>Expected Inflation Rate (%)</label><input type="number" id="csInflation" value="5" placeholder="e.g. 5" step="0.5"></div>
<div class="form-group"><label>Current Savings ($)</label><input type="number" id="csCurrent" placeholder="e.g. 5000" step="1000"></div>
<div class="form-group"><label>Monthly Contribution ($)</label><input type="number" id="csMonthly" placeholder="e.g. 300" step="50"></div>
<div class="form-group"><label>Expected Investment Return (%)</label><input type="number" id="csRate" value="6" placeholder="e.g. 6" step="0.5"></div>
</div>
<div class="result-actions"><button class="btn btn-primary" onclick="calcCollegeSavings()"><i class="fas fa-calculator"></i> Calculate</button></div>
<div class="mt-16" style="display:grid;grid-template-columns:repeat(3,1fr);gap:12px;">
<div style="background:var(--bg-secondary);border-radius:var(--radius);padding:14px;text-align:center;"><div style="font-size:1.4rem;font-weight:700;color:var(--primary)" id="csFutureCost">$0</div><div style="font-size:.8rem;color:var(--text-muted)">Projected College Cost</div></div>
<div style="background:var(--bg-secondary);border-radius:var(--radius);padding:14px;text-align:center;"><div style="font-size:1.4rem;font-weight:700;color:var(--secondary)" id="csProjected">$0</div><div style="font-size:.8rem;color:var(--text-muted)">Projected Savings</div></div>
<div style="background:var(--bg-secondary);border-radius:var(--radius);padding:14px;text-align:center;"><div style="font-size:1.2rem;font-weight:700" id="csGap">-</div><div style="font-size:.8rem;color:var(--text-muted)">Status</div></div>
</div>
''',
        "retirement-expense-calculator": '''
<div class="form-row-2">
<div class="form-group"><label>Current Housing ($/month)</label><input type="number" id="reHousing" placeholder="e.g. 1800" step="100"></div>
<div class="form-group"><label>Current Food ($/month)</label><input type="number" id="reFood" placeholder="e.g. 600" step="50"></div>
<div class="form-group"><label>Current Healthcare ($/month)</label><input type="number" id="reHealth" placeholder="e.g. 300" step="50"></div>
<div class="form-group"><label>Current Transportation ($/month)</label><input type="number" id="reTransport" placeholder="e.g. 400" step="50"></div>
<div class="form-group"><label>Current Utilities ($/month)</label><input type="number" id="reUtils" placeholder="e.g. 250" step="50"></div>
<div class="form-group"><label>Current Entertainment ($/month)</label><input type="number" id="reEntertainment" placeholder="e.g. 300" step="50"></div>
<div class="form-group"><label>Other Current Expenses ($/month)</label><input type="number" id="reOther" placeholder="e.g. 500" step="50"></div>
<div class="form-group"><label>Retirement Income %</label><input type="number" id="rePct" value="80" placeholder="e.g. 80" min="0" max="100"></div>
</div>
<div class="result-actions"><button class="btn btn-primary" onclick="calcRetExpense()"><i class="fas fa-calculator"></i> Calculate</button></div>
<div class="mt-16" style="display:grid;grid-template-columns:repeat(3,1fr);gap:12px;">
<div style="background:var(--bg-secondary);border-radius:var(--radius);padding:14px;text-align:center;"><div style="font-size:1.4rem;font-weight:700;color:var(--primary)" id="reCurrent">$0</div><div style="font-size:.8rem;color:var(--text-muted)">Current Monthly Expenses</div></div>
<div style="background:var(--bg-secondary);border-radius:var(--radius);padding:14px;text-align:center;"><div style="font-size:1.4rem;font-weight:700;color:var(--secondary)" id="reRetirement">$0</div><div style="font-size:.8rem;color:var(--text-muted)">Est. Retirement Monthly</div></div>
<div style="background:var(--bg-secondary);border-radius:var(--radius);padding:14px;text-align:center;"><div style="font-size:1.2rem;font-weight:700;color:var(--accent)" id="reAnnual">$0</div><div style="font-size:.8rem;color:var(--text-muted)">Annual Retirement Need</div></div>
</div>
''',
    }
    return interfaces.get(slug, '<p>Tool interface coming soon.</p>')


# ── Main ────────────────────────────────────────────────

def main():
    with open(os.path.join(ROOT, 'tools_config.json'), 'r', encoding='utf-8') as f:
        tools = json.load(f)

    print(f"Generating {len(tools)} tool pages...\n")

    for tool in tools:
        slug = tool['slug']
        html_template = generate_tool_page(tool)
        interface_html = get_tool_interface(slug)
        full_html = html_template.replace('__TOOL_INTERFACE__', interface_html)

        out_path = os.path.join(ROOT, slug + '.html')
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(full_html)

        size_kb = os.path.getsize(out_path) / 1024
        print(f"  OK {slug}.html ({size_kb:.1f} KB)")

    print(f"\nDone! Generated {len(tools)} tool pages in {ROOT}")

if __name__ == '__main__':
    main()
