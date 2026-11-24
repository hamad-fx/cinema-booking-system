/** Member 1: browse movies, filtering, favorites and review discovery. */
import {api, esc} from './api.js';

export async function showCatalog(state, nav, notify, favoritesOnly=false) {
  const app=document.getElementById('app');
  const favoritesOnlyIds = state.favorites || [];
  app.innerHTML=`${favoritesOnly?'':`<section class="hero"><div><span class="eyebrow">✦ THE CINEMA EXPERIENCE</span><h1>Big screen.<br><em>Big stories.</em></h1><p>Find your next favorite movie, pick the best seats, and own the moment.</p><button class="primary" id="explore">Explore Movies →</button></div><div class="hero-art" aria-hidden="true">🍿</div></section>`}
  <section class="section" id="catalog"><div class="title-row"><div><span class="eyebrow">Now showing</span><h2 class="section-title">${favoritesOnly?'My Favorites':'Movies at CineVerse'}</h2><p class="muted small">Sample films and demo showtimes.</p></div><span class="chip">🎟️ Book your experience</span></div>
  <div class="filters"><input id="movie-search" placeholder="Search movies by title..." aria-label="Search movies"><select id="movie-genre" aria-label="Filter by genre"><option value="">All Genres</option>${[...new Set(state.movies.map(m=>m.genre))].map(g=>`<option value="${esc(g)}">${esc(g)}</option>`).join('')}</select></div>
  <div id="movie-grid" class="grid"></div></section>`;
  if(document.getElementById('explore')) document.getElementById('explore').onclick=()=>document.getElementById('catalog').scrollIntoView({behavior:'smooth'});
  const grid=document.getElementById('movie-grid');
  function draw(){
    const search=document.getElementById('movie-search').value.trim().toLowerCase();
    const genre=document.getElementById('movie-genre').value;
    const movies=state.movies.filter(m=>m.title.toLowerCase().includes(search)&&(!genre||m.genre===genre)&&(!favoritesOnly||favoritesOnlyIds.includes(m.id)));
    grid.innerHTML=movies.length?movies.map(m=>`<article class="card"><div class="poster" style="--accent:${/^#[\da-f]{6}$/i.test(m.accent)?m.accent:'#704e6c'}"><span class="rating">★ ${esc(m.rating)}</span><span class="art">${esc(m.emoji)}</span><span class="poster-title">${esc(m.title)}</span></div><div class="card-body"><h3>${esc(m.title)}</h3><p class="muted small">${esc(m.genre)} · ${m.duration} min</p><p class="muted small">${esc(m.summary.slice(0,78))}${m.summary.length>78?'…':''}</p><div class="card-actions"><button class="primary" data-view="${m.id}">View & Book →</button><button class="iconbtn ${favoritesOnlyIds.includes(m.id)?'liked':''}" data-favorite="${m.id}" aria-label="Toggle favorite">${favoritesOnlyIds.includes(m.id)?'♥':'♡'}</button></div></div></article>`).join(''):`<div class="empty">${favoritesOnly?'No favorites yet — save movies using ♡.':'No movies match your search.'}</div>`;
    grid.querySelectorAll('[data-view]').forEach(b=>b.onclick=()=>{state.movieId=Number(b.dataset.view); nav('details');});
    grid.querySelectorAll('[data-favorite]').forEach(b=>b.onclick=async()=>{
      if(!state.user){notify('Log in to save favorites.');nav('login');return;}
      try {await api(`/favorites/${b.dataset.favorite}`,{}); const fresh=await api('/favorites');state.favorites=fresh.movie_ids; if(favoritesOnly) {showCatalog(state,nav,notify,true);} else draw();} catch(e){notify(e.message);}
    });
  }
  draw();
  document.getElementById('movie-search').oninput=draw;
  document.getElementById('movie-genre').onchange=draw;
}
