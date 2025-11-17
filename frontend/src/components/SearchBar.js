import React, { useState } from "react";
import axios from "axios";

function SearchBar({ setResults, setLoading }) {
  const [query, setQuery] = useState("");
  const [diet, setDiet] = useState([]);
  const [cuisine, setCuisine] = useState("");
  const [maxTime, setMaxTime] = useState(60);

  const handleSearch = async () => {
    setLoading(true);
    try {
      const payload = {
        query: query,
        diet: diet.length > 0 ? diet : null,
        cuisine: cuisine || null,
        max_time: maxTime,
        top_k: 20
      };

      const response = await axios.post("http://127.0.0.1:8000/search", payload);
      setResults(response.data.results || []);
    } catch (err) {
      console.error("Search error:", err);
      setResults([]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="search-container">
      <h1>Intelligent Recipe Assistant</h1>

      <input
        className="query-input"
        type="text"
        placeholder="Enter ingredients (e.g., spinach rice)"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
      />

      <div className="controls-row">
        <select value={cuisine} onChange={(e) => setCuisine(e.target.value)}>
          <option value="">All Cuisines</option>
          <option value="indian">Indian</option>
          <option value="italian">Italian</option>
          <option value="chinese">Chinese</option>
          <option value="mexican">Mexican</option>
        </select>

        <select
          multiple
          onChange={(e) =>
            setDiet(Array.from(e.target.selectedOptions, opt => opt.value))
          }
        >
          <option value="vegetarian">Vegetarian</option>
          <option value="vegan">Vegan</option>
          <option value="gluten-free">Gluten-Free</option>
        </select>

        <label>Max Time: {maxTime} min</label>
        <input
          type="range"
          min="5"
          max="120"
          value={maxTime}
          onChange={(e) => setMaxTime(Number(e.target.value))}
        />
      </div>

      <button className="search-btn" onClick={handleSearch}>
        Search
      </button>
    </div>
  );
}

export default SearchBar;
