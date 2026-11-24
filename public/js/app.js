/** Main controller and navigation. Student project: designed for team-owned feature modules. */
import {api} from './api.js';
import {showCatalog} from './catalog.js';
import {showMovieDetails} from './showtimes.js';
import {showSeats} from './seats.js';
import {showCheckout,showBookings,showTicket} from './booking.js';
import {showAccount} from './account.js';
import {showAdmin} from './admin.js';

const state={user:null,movies:[],favorites:[],movieId:null,showtimeId:null,showtime:null,selectedSeats:[],snackQty:{},products:[],promo:'',quote:null,afterLogin:'home',ticket:null};
let toastTimeout;
function notify(message){const t=document.getElementById('toast');t.textContent=message;t.classList.remove('hidden');clearTimeout(toastTimeout);toastTimeout=setTimeout(()=>t.classList.add('hidden'),4200);}
function header(){document.querySelector('.admin-only').classList.toggle('hidden',state.user?.role!=='admin');document.getElementById('accountNav').innerHTML=state.user?`<span class="muted small">Hi, ${state.user.name.replace(/[&<>"']/g,'')}</span><button class="secondary tiny" id="logout-btn">Logout</button>`:'<button class="primary tiny" id="login-btn">Sign In</button>';const login=document.getElementById('login-btn');if(login)login.onclick=()=>navigate('login');const logout=document.getElementById('logout-btn');if(logout)logout.onclick=async()=>{try{await api('/auth/logout',{});state.user=null;state.favorites=[];notify('Signed out.');navigate('home');}catch(err){notify(err.message)}};}
async function navigate(page){
  document.getElementById('app').innerHTML='<div class="loading">Loading CineVerse…</div>';
  document.querySelectorAll('[data-nav]').forEach(b=>b.classList.toggle('active',b.dataset.nav===page));
  header();window.scrollTo({top:0,behavior:'smooth'});
  try{
    if(page==='home') await showCatalog(state,navigate,notify);
    else if(page==='favorites') {if(!state.user){state.afterLogin='favorites';return navigate('login');} await showCatalog(state,navigate,notify,true);}
    else if(page==='details') await showMovieDetails(state,navigate,notify);
    else if(page==='seats') await showSeats(state,navigate,notify);
    else if(page==='checkout') showCheckout(state,navigate,notify);
    else if(page==='bookings') await showBookings(state,navigate,notify);
    else if(page==='ticket') showTicket(state,navigate);
    else if(page==='login') showAccount(state,navigate,notify,()=>{const target=state.afterLogin||'home';state.afterLogin='home';header();navigate(target);});
    else if(page==='admin') await showAdmin(state,navigate,notify);
    else navigate('home');
  }catch(err){document.getElementById('app').innerHTML=`<div class="empty">Something went wrong. ${err.message.replace(/[&<>"']/g,'')}<div class="actions" style="justify-content:center"><button class="primary" id="retry">Back to movies</button></div></div>`;document.getElementById('retry').onclick=()=>navigate('home');notify(err.message);}
}
document.querySelectorAll('[data-nav]').forEach(b=>b.onclick=()=>navigate(b.dataset.nav));
document.getElementById('brand').onclick=e=>{e.preventDefault();navigate('home');};
(async()=>{try{const [u,m]=await Promise.all([api('/me'),api('/movies')]);state.user=u.user;state.movies=m.movies;if(state.user){const r=await api('/favorites');state.favorites=r.movie_ids;}header();navigate('home');}catch(err){document.getElementById('app').innerHTML='<div class="empty">Could not contact the local server. Run <code>python server.py</code> then open http://localhost:8000.</div>';notify(err.message);}})();
