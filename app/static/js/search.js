// City autocomplete for search form
const CITIES = [
  'Beograd', 'Novi Sad', 'Niš', 'Kragujevac', 'Subotica',
  'Zrenjanin', 'Pančevo', 'Čačak', 'Novi Pazar', 'Kruševac',
  'Vranje', 'Šabac', 'Smederevo', 'Valjevo', 'Leskovac',
  'Požarevac', 'Zaječar', 'Kikinda', 'Sombor', 'Pirot',
];

function initAutocomplete(inputId) {
  const input = document.getElementById(inputId);
  if (!input) return;

  const list = document.createElement('ul');
  list.className = 'autocomplete-list';
  input.parentNode.style.position = 'relative';
  input.parentNode.appendChild(list);

  input.addEventListener('input', () => {
    const val = input.value.trim().toLowerCase();
    list.innerHTML = '';
    if (!val || val.length < 1) return;

    const matches = CITIES.filter(c => c.toLowerCase().startsWith(val)).slice(0, 6);
    matches.forEach(city => {
      const li = document.createElement('li');
      li.textContent = city;
      li.addEventListener('click', () => {
        input.value = city;
        list.innerHTML = '';
      });
      list.appendChild(li);
    });
  });

  document.addEventListener('click', e => {
    if (!input.parentNode.contains(e.target)) list.innerHTML = '';
  });
}

document.addEventListener('DOMContentLoaded', () => {
  initAutocomplete('od');
  initAutocomplete('do');
});
