/** Shared API helpers; requests stay same-origin and authenticate via HttpOnly session cookie. */
export const esc = value => String(value ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
export const money = value => `${Number(value || 0).toLocaleString('en-EG')} EGP`;
export async function api(path, payload) {
  const options = {credentials: 'same-origin', headers:{}};
  if (payload !== undefined) { options.method='POST'; options.headers['Content-Type']='application/json'; options.body=JSON.stringify(payload); }
  const res = await fetch(`/api${path}`, options);
  let data;
  try { data = await res.json(); } catch { throw new Error('Server unavailable. Try again.'); }
  if (!res.ok) throw new Error(data.error || 'Request failed');
  return data;
}
export const tomorrow = () => { const d = new Date(); d.setDate(d.getDate()+1); return `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}-${String(d.getDate()).padStart(2,'0')}`; };
export const cap = (str,n=150) => esc(String(str || '').slice(0,n));
