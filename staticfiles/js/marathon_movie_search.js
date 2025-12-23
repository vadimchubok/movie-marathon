const searchInput = document.getElementById("movieSearch");
const results = document.getElementById("searchResults");
const selected = document.getElementById("selectedMovies");
const inputs = document.getElementById("movieInputs");

const selectedIds = new Set();

searchInput.addEventListener("input", async () => {
  const q = searchInput.value.trim();
  results.innerHTML = "";

  if (q.length < 2) return;

  const res = await fetch(`/movies/search/?q=${q}`);
  const movies = await res.json();

  movies.forEach(movie => {
    const item = document.createElement("button");
    item.type = "button";
    item.className = "list-group-item list-group-item-action";
    item.textContent = `${movie.title} (${movie.year})`;

    item.onclick = () => addMovie(movie);
    results.appendChild(item);
  });
});

function addMovie(movie) {
  if (selectedIds.has(movie.id)) return;
  selectedIds.add(movie.id);

  const li = document.createElement("li");
  li.className = "list-group-item";

  li.innerHTML = `
    <span>${movie.title} (${movie.year})</span>
    <button type="button" class="btn btn-sm btn-outline-danger">✕</button>
  `;

  li.querySelector("button").onclick = () => {
    selectedIds.delete(movie.id);
    li.remove();
    document.getElementById(`movie-${movie.id}`).remove();
  };

  selected.appendChild(li);

  const input = document.createElement("input");
  input.type = "hidden";
  input.name = "movies";
  input.value = movie.id;
  input.id = `movie-${movie.id}`;
  inputs.appendChild(input);

  results.innerHTML = "";
  searchInput.value = "";
}
