import React from "react";

// Convert Python-style list string → JS array
function parseListString(s) {
  if (!s) return [];
  if (Array.isArray(s)) return s;

  try {
    // Convert single quotes → double quotes for JSON.parse
    const fixed = s.replace(/'/g, '"');
    return JSON.parse(fixed);
  } catch {
    // Fallback split
    return s
      .replace(/[\[\]']+/g, "")
      .split(",")
      .map((item) => item.trim())
      .filter(Boolean);
  }
}

export default function RecipeCard({ recipe }) {
  const ingredients = parseListString(recipe.ingredients);
  const steps = parseListString(recipe.steps);

  return (
    <div className="recipe-card">
      <h2>{recipe.name}</h2>

      <div className="recipe-meta">
        <span>{recipe.minutes} minutes</span>
        <span>Score: {recipe.score.toFixed(3)}</span>
      </div>

      {recipe.description && (
        <p className="recipe-description">{recipe.description}</p>
      )}

      <div className="recipe-sections">
        <div>
          <h3>Ingredients</h3>
          <ul>
            {ingredients.map((ing, i) => (
              <li key={i}>{ing}</li>
            ))}
          </ul>
        </div>

        <div>
          <h3>Steps</h3>
          <ol>
            {steps.map((st, i) => (
              <li key={i}>{st}</li>
            ))}
          </ol>
        </div>
      </div>
    </div>
  );
}
