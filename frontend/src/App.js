import React, { useState } from "react";
import SearchBar from "./components/SearchBar";
import RecipeList from "./components/RecipeList";
import "./App.css";

function App() {
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);

  return (
    <div className="App">
      <SearchBar setResults={setResults} setLoading={setLoading} />
      <RecipeList results={results} loading={loading} />
    </div>
  );
}

export default App;
