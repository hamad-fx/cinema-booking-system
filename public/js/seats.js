/** Member 3: interactive seat map, selection rules, server-sourced availability and pricing. */
import {api,esc,money} from './api.js';

export function calculatePreview(show, seats, products, quantities, code){
  const ticketTotal=seats.reduce((sum,seat)=>sum+show.base_price+('EF'.includes(seat[0])?70:0),0);
  const foodTotal=products.reduce((sum,s)=>sum+s.price*(quantities[s.id]||0),0);
  const percent=code==='CINE10'?10:code==='STUDENT15'?15:0;
  const discount=Math.floor((ticketTotal+foodTotal)*percent/100);
  return {tickets:ticketTotal,snacks:foodTotal,discount,total:ticketTotal+foodTotal-discount};
}

export async function showSeats(state,nav,notify){
  const [{showtime,occupied},snackData]=await Promise.all([api(`/showtimes/${state.showtimeId}/seats`),api('/snacks')]);
  state.showtime=showtime;state.products=snackData.snacks;
  const taken=new Set(occupied);
  state.selectedSeats=state.selectedSeats.filter(s=>!taken.has(s));
  const app=document.getElementById('app');
  app.innerHTML=`<div class="breadcrumb"><button id="back-details">Movie details</button> / Choose seats</div><div class="row"><div><span class="eyebrow">THE BEST SEAT IN THE HOUSE</span><h1>${esc(showtime.movie_title)}</h1><p class="muted">${esc(showtime.hall)} · ${esc(showtime.show_date)} · ${esc(showtime.show_time)}</p></div><span class="chip">Maximum 8 seats per booking</span></div>
  <section class="two-col section"><div class="panel"><div class="row" style="justify-content:space-between">
  <h2>Select Your Seats</h2>
  <button id="clear-seats" class="secondary" disabled>
    Clear Selection
  </button>
</div><div class="seat-screen">CINEMA SCREEN</div><div class="seatrows" id="seat-map"></div><div class="legend"><span><i class="swatch" style="background:#708098"></i>Available</span><span><i class="swatch" style="background:#bb9350"></i>VIP</span><span><i class="swatch" style="background:#ef475e"></i>Selected</span><span><i class="swatch" style="background:#303747"></i>Booked</span></div></div>
  <aside class="panel sticky-side"><h2>Booking Summary</h2><div class="line"><span>Selected seats</span><strong id="selected-label">None</strong></div><div class="line"><span>Tickets</span><strong id="ticket-price">0 EGP</strong></div><h3 style="margin-top:21px">🍿 Snacks & Drinks</h3><div class="snacks" id="snacks"></div><div class="line"><span>Snacks</span><strong id="snack-price">0 EGP</strong></div><div class="field"><label for="promo">Promo code (CINE10 / STUDENT15)</label><div class="row"><input id="promo" placeholder="Optional" maxlength="20" style="flex:1;min-width:90px"><button class="secondary" id="apply-promo">Apply</button></div></div><div class="line"><span>Discount</span><strong id="discount-price">0 EGP</strong></div><div class="line"><strong>Total</strong><span class="price" id="full-price">0 EGP</span></div><div class="actions"><button id="continue" class="primary" disabled>Proceed to Checkout →</button></div><p class="muted small">Prices are calculated again on the server when you confirm.</p></aside></section>`;
  document.getElementById('back-details').onclick=()=>nav('details');
  const seatMap=document.getElementById('seat-map');
  document.getElementById('clear-seats').onclick = () => {
  state.selectedSeats = [];
  renderMap();
  update();
  notify('Seat selection cleared.');
};
  function renderMap(){seatMap.innerHTML='ABCDEF'.split('').map(row=>`<div class="seatrow"><span class="seatlabel">${row}</span>${Array.from({length:8},(_,i)=>{const s=`${row}${i+1}`,blocked=taken.has(s);return `${i===4?'<span class="aisle"></span>':''}<button title="Seat ${s}" aria-label="Seat ${s}" aria-pressed="${state.selectedSeats.includes(s)}" class="seat ${'EF'.includes(row)?'vip':''} ${blocked?'occupied':''} ${state.selectedSeats.includes(s)?'selected':''}" ${blocked?'disabled':''} data-seat="${s}">${i+1}</button>`;}).join('')}</div>`).join('');
    seatMap.querySelectorAll('[data-seat]').forEach(btn=>btn.onclick=()=>{const s=btn.dataset.seat;if(state.selectedSeats.includes(s))state.selectedSeats=state.selectedSeats.filter(x=>x!==s);else if(state.selectedSeats.length<8)state.selectedSeats.push(s);else return notify('Maximum 8 seats per booking.');renderMap();update();});}
  const food=document.getElementById('snacks');
  function renderSnacks(){food.innerHTML=state.products.map(p=>`<div class="snack"><div>${esc(p.emoji)} <b>${esc(p.name)}</b><br><span class="muted small">${money(p.price)}</span></div><div class="counter"><button data-snack="${p.id}" data-delta="-1" aria-label="Remove ${esc(p.name)}">−</button><b>${state.snackQty[p.id]||0}</b><button data-snack="${p.id}" data-delta="1" aria-label="Add ${esc(p.name)}">+</button></div></div>`).join('');food.querySelectorAll('[data-snack]').forEach(b=>b.onclick=()=>{const k=b.dataset.snack;state.snackQty[k]=Math.max(0,Math.min(10,(state.snackQty[k]||0)+Number(b.dataset.delta)));renderSnacks();update();});}
  function update(){const q=calculatePreview(showtime,state.selectedSeats,state.products,state.snackQty,state.promo);state.quote=q;document.getElementById('selected-label').textContent=state.selectedSeats.slice().sort().join(', ')||'None';document.getElementById('ticket-price').textContent=money(q.tickets);document.getElementById('snack-price').textContent=money(q.snacks);document.getElementById('discount-price').textContent='−'+money(q.discount);document.getElementById('full-price').textContent=money(q.total);document.getElementById('continue').disabled =
  !state.selectedSeats.length;

document.getElementById('clear-seats').disabled =
  !state.selectedSeats.length;
}
  document.getElementById('apply-promo').onclick=()=>{const code=document.getElementById('promo').value.trim().toUpperCase();if(code&&!['CINE10','STUDENT15'].includes(code))return notify('Invalid promo code.');state.promo=code;notify(code?`${code} applied`:'Promo cleared');update();};
  document.getElementById('continue').onclick=()=>{if(!state.user){state.afterLogin='checkout';notify('Please sign in before checkout.');nav('login');}else nav('checkout');};
  renderMap();renderSnacks();update();
}
