(function(){const b=document.getElementById("themeToggle");if(!b)return;const root=document.documentElement;
function sync(){const d=root.getAttribute("data-theme")==="dark";b.setAttribute("aria-pressed",String(d));b.querySelector("span").textContent=d?"Dark mode: on":"Dark mode: off";b.setAttribute("aria-label",d?"Dark mode is on. Switch to light mode":"Dark mode is off. Switch to dark mode")}
b.addEventListener("click",()=>{const t=root.getAttribute("data-theme")==="dark"?"light":"dark";root.setAttribute("data-theme",t);try{localStorage.setItem("theme",t)}catch(e){}sync();document.dispatchEvent(new CustomEvent("themechange",{detail:t}))});
sync()})();
