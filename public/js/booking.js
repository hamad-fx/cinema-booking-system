/** Member 4: checkout, server-persisted bookings, cancellations, printable tickets. */
import {api,esc,money} from './api.js';

export function showCheckout(state,nav,notify){
  if(!state.user){state.afterLogin='checkout';nav('login');return;}
  if(!state.showtime||!state.selectedSeats.length){nav('home');return;}
  const s=state.showtime,q=state.quote;
  document.getElementById('app').innerHTML=`<div class="breadcrumb"><button id="back-seats">Choose seats</button> / Checkout</div><section class="checkout-box"><span class="eyebrow">Almost there!</span><h1>Complete Your Booking</h1><div class="two-col section"><div class="panel"><h2>Customer Details</h2><div class="field"><label>Name</label><input value="${esc(state.user.name)}" disabled></div><div class="field"><label>Email</label><input value="${esc(state.user.email)}" disabled></div><div class="notice">Demo checkout — no real card payment or charge occurs. All bookings are stored on this application's SQLite server database.</div><form id="confirm-form"><label style="display:flex;gap:10px;align-items:flex-start"><input type="checkbox" id="agree" required style="margin-top:6px"><span class="small">I understand this is a university demo and the booking does not grant admission to a real cinema.</span></label><div class="actions"><button class="primary" id="confirm-booking" type="submit">Confirm Demo Booking →</button></div></form></div><aside class="panel"><h2>Order Summary</h2><div class="line"><span>Movie</span><strong>${esc(s.movie_title)}</strong></div><div class="line"><span>Show</span><strong>${esc(s.show_date)} ${esc(s.show_time)}</strong></div><div class="line"><span>Hall</span><strong>${esc(s.hall)}</strong></div><div class="line"><span>Seats</span><strong>${esc(state.selectedSeats.slice().sort().join(', '))}</strong></div><div class="line"><span>Tickets</span><strong>${money(q.tickets)}</strong></div><div class="line"><span>Snacks</span><strong>${money(q.snacks)}</strong></div><div class="line"><span>Discount</span><strong>−${money(q.discount)}</strong></div><div class="line"><strong>Total</strong><strong class="price">${money(q.total)}</strong></div></aside></div></section>`;
  document.getElementById('back-seats').onclick=()=>nav('seats');
  document.getElementById('confirm-form').onsubmit=async e=>{e.preventDefault();const btn=document.getElementById('confirm-booking');btn.disabled=true;btn.textContent='Confirming…';try{
    const snacks=state.products.filter(p=>state.snackQty[p.id]>0).map(p=>({id:p.id,quantity:state.snackQty[p.id]}));
    const result=await api('/bookings',{showtime_id:state.showtimeId,seats:state.selectedSeats,snacks,promo:state.promo});
    state.lastBookingCode=result.booking.code;state.selectedSeats=[];notify('Booking confirmed!');nav('bookings');
  } catch(err){notify(err.message);btn.disabled=false;btn.textContent='Confirm Demo Booking →';}};
}

export async function showBookings(state,nav,notify){
  if(!state.user){state.afterLogin='bookings';nav('login');return;}
  const result=await api('/bookings');
  document.getElementById('app').innerHTML=`<section class="section"><span class="eyebrow">My account</span><h1 class="section-title">My Bookings</h1><p class="muted">View your tickets and cancel eligible demo bookings.</p><div class="booking-list">${result.bookings.length?result.bookings.map(b=>`<article class="booking"><div class="row"><h3>${esc(b.movie_emoji)} ${esc(b.movie_title)}</h3><span class="status ${b.status==='cancelled'?'cancelled':''}">${esc(b.status)}</span></div><p class="muted">${esc(b.show_date)} · ${esc(b.show_time)} · ${esc(b.hall)}</p><div class="line"><span>Booking ${esc(b.code)}</span><strong>${money(b.total)}</strong></div><div class="line"><span>Seats</span><strong>${esc(b.seats.join(', ')||'Released')}</strong></div><div class="actions"><button class="secondary" data-ticket="${b.id}">View Ticket</button>${b.status==='confirmed'?`<button class="danger" data-cancel="${b.id}">Cancel Booking</button>`:''}</div></article>`).join(''):'<div class="empty">No bookings yet. Your next movie adventure starts here!</div>'}</div><button class="primary" id="more-movies">Explore Movies →</button></section>`;
  document.getElementById('more-movies').onclick=()=>nav('home');
  document.querySelectorAll('[data-ticket]').forEach(btn=>btn.onclick=()=>{state.ticket=result.bookings.find(b=>b.id===Number(btn.dataset.ticket));nav('ticket');});

document.querySelectorAll('[data-cancel]').forEach(btn => {
  btn.onclick = async () => {
    if (!confirm('Cancel this booking? Seats will be released.')) return;

    btn.disabled = true;
    btn.textContent = 'Cancelling…';

    try {
      await api(`/bookings/${btn.dataset.cancel}/cancel`, {});

      notify('Booking cancelled.');
      await showBookings(state, nav, notify);

    } catch (e) {
      notify(e.message);
      btn.disabled = false;
      btn.textContent = 'Cancel Booking';
    }
  };
});
}

export function showTicket(state,nav){
  const b=state.ticket;if(!b){nav('bookings');return;}
  document.getElementById('app').innerHTML=`<section class="section"><div class="title-row no-print"><h1>🎟️ Your E-Ticket</h1><button class="secondary" id="ticket-back">← My Bookings</button></div><article class="ticket"><span class="eyebrow">CINEVERSE · DEMO TICKET</span><h1>${esc(b.movie_title)}</h1><p class="muted">${esc(b.show_date)} · ${esc(b.show_time)}</p><div class="ticket-dash"></div><div class="line"><span>Hall</span><strong>${esc(b.hall)}</strong></div><div class="line"><span>Seats</span><strong>${esc(b.seats.join(', ')||'Cancelled')}</strong></div><div class="line"><span>Guest</span><strong>${esc(b.guest_name)}</strong></div><div class="line"><span>Status</span><strong>${esc(b.status)}</strong></div><div class="line"><span>Paid (Demo)</span><strong>${money(b.total)}</strong></div><div class="ticket-dash"></div><p class="muted small" style="text-align:center">Booking reference</p><div class="ticket-code">${esc(b.code)}</div>${b.status==='confirmed'?`<div style="text-align:center;margin:16px 0"><img src="/api/bookings/${b.id}/qr" width="160" height="160" alt="QR code for demo ticket" style="border:10px solid white"></div>`:''}<p class="muted small" style="text-align:center">Not valid for admission · No real payment</p></article><div class="actions no-print" style="justify-content:center"><button class="primary" id="print-ticket">Print Ticket</button></div></section>`;
  document.getElementById('ticket-back').onclick=()=>nav('bookings');
  document.getElementById('print-ticket').onclick=()=>window.print();
}
