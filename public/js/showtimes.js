/** Member 2: movie details, reviews and choosing a cinema showtime. */
import {api, esc, money} from './api.js';
export async function showMovieDetails(state,nav,notify){
  const movieData=await api(`/movies/${state.movieId}`);
  const movie=movieData.movie;
  const app=document.getElementById('app');
  app.innerHTML=`<div class="breadcrumb"><button id="back-movies">Movies</button> / ${esc(movie.title)}</div><section class="panel"><div class="movie-detail"><div class="mini-art" style="--accent:${/^#[\da-f]{6}$/i.test(movie.accent)?movie.accent:'#67416f'}">${esc(movie.emoji)}</div><div><span class="eyebrow">FEATURED FILM</span><h1>${esc(movie.title)}</h1><p class="muted">${esc(movie.genre)} · ${movie.duration} minutes · ★ ${esc(movie.rating)}</p><p>${esc(movie.summary)}</p></div></div><hr style="border:0;border-top:1px solid #364057"><div class="row"><h2 style="margin:8px 0">Choose a Showtime</h2><span class="chip">VIP +70 EGP / seat</span></div><div class="field" style="max-width:260px"><label for="showday">Filter show date</label><input type="date" id="showday"></div><div id="show-list" class="show-grid"></div></section>
  <section class="section panel"><h2>Audience Reviews</h2><div id="reviews">${movieData.reviews.length?movieData.reviews.map(r=>`<div class="review"><strong>${'★'.repeat(r.stars)}${'☆'.repeat(5-r.stars)}</strong> · <b>${esc(r.name)}</b><p class="muted">${esc(r.comment)}</p></div>`).join(''):'<p class="muted">No reviews yet. Be the first!</p>'}</div><div id="review-form"></div></section>`;
  document.getElementById('back-movies').onclick=()=>nav('home');
  const day=document.getElementById('showday');day.min=new Date().toLocaleDateString('en-CA');
  async function loadShows(){
    const result=await api(`/showtimes?movie_id=${movie.id}&date=${encodeURIComponent(day.value)}`);
    document.getElementById('show-list').innerHTML=result.showtimes.length?result.showtimes.map(s=>`<button class="show-button" data-show="${s.id}"><strong>${esc(s.show_date)} · ${esc(s.show_time)}</strong><small>${esc(s.hall)} · ${money(s.base_price)} Standard</small></button>`).join(''):'<div class="empty">No showtimes on this date.</div>';
    document.querySelectorAll('[data-show]').forEach(b=>b.onclick=()=>{state.showtimeId=Number(b.dataset.show);state.selectedSeats=[];state.snackQty={};state.promo='';nav('seats');});
  }
  day.onchange=()=>loadShows().catch(e=>notify(e.message));
  await loadShows();
  const reviewForm=document.getElementById('review-form');
  if(state.user){reviewForm.innerHTML=`<h3>Rate this movie</h3><form id="review-form-inner"><div class="field"><label>Stars</label><select name="stars"><option value="5">★★★★★ (5)</option><option value="4">★★★★ (4)</option><option value="3">★★★ (3)</option><option value="2">★★ (2)</option><option value="1">★ (1)</option></select></div><div class="field"><label>Your review</label><textarea name="comment" required minlength="3" maxlength="500" rows="3" placeholder="What did you think?"></textarea></div><button class="primary">Save Review</button></form>`;
    document.getElementById('review-form-inner').onsubmit=async e=>{e.preventDefault();const form=new FormData(e.target);try{await api('/reviews',{movie_id:movie.id,stars:Number(form.get('stars')),comment:form.get('comment')});notify('Review saved.');await showMovieDetails(state,nav,notify);}catch(err){notify(err.message)}};
  } else reviewForm.innerHTML='<p class="muted">Log in to write a review.</p>';
}
