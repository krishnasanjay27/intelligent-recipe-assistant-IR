import React from "react";
import RecipeCard from "./RecipeCard";

export default function RecipeList({ results, loading }) {
  if (loading) {
  return (
    <div style={{ textAlign: "center", marginTop: "30px" }}>
      <div className="loading-spinner"></div>
      <p>Fetching recipes...</p>
    </div>
  );
}


  if (!results || results.length === 0) {
    return <div className="no-results">No results yet</div>;
  }

  return (
    <div className="results-grid">
      {results.map((recipe, index) => (
        <RecipeCard key={index} recipe={recipe} />
      ))}
    </div>
  );
}
