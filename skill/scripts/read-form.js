(()=>{const nums=[...document.querySelectorAll('input[type=number]')];const tas=[...document.querySelectorAll('textarea')];const heads=[...document.querySelectorAll('h1,h2,h3,h4,h5')].map(h=>h.innerText.trim()).filter(Boolean);
const lab=el=>{let c=el;for(let i=0;i<4&&c;i++){c=c.parentElement;const t=(c.innerText||'').split('\n')[0].trim();if(t)return t}return '?'};
return 'HEADS: '+heads.join(' | ')+'\n'+nums.map(n=>lab(n)+'='+n.value).join(', ')+'\nNOTES:\n'+tas.map((t,i)=>i+': '+t.value.replace(/\n+/g,' / ')).join('\n')})()
