import React, { useState } from "react";
import { Clock, Star, Utensils, ChefHat, Leaf, Flame, ChevronDown, ChevronUp } from "lucide-react";

// Helper to parse Python list strings
function parseListString(s) {
  if (!s) return [];
  if (Array.isArray(s)) return s;
  try {
    const fixed = s.replace(/'/g, '"');
    return JSON.parse(fixed);
  } catch {
    // Fallback for simple comma-separated string that may have brackets/quotes
    return s.replace(/[\[\]']+/g, "").split(",").map((item) => item.trim()).filter(Boolean);
  }
}

export default function RecipeCard({ recipe }) {
  const [expanded, setExpanded] = useState(false);
  const ingredients = parseListString(recipe.ingredients);
  const steps = parseListString(recipe.steps);

  // Robust score calculation: 
  // 1. Convert score to a number.
  // 2. Default to 0 if null/undefined, or keep the number.
  // 3. Display N/A only if the recipe object itself is missing a score field.
  const scoreValue = typeof recipe.score === 'number' ? recipe.score : (recipe.score === undefined ? null : 0);

  return (
    <div className={`bg-white rounded-2xl shadow-sm hover:shadow-lg transition-all duration-300 border border-stone-100 overflow-hidden flex flex-col ${expanded ? 'row-span-2' : ''}`}>
      
      {/* Card Header */}
      <div className="p-6">
        <div className="flex justify-between items-start mb-2">
          <div className="flex items-center gap-2 text-amber-500 text-sm font-medium">
            <Star size={14} fill="currentColor" />
            {/* UPDATED: Display score as 0.0 if calculated as 0, or N/A if missing */}
            <span>
              {scoreValue === null
                ? "N/A"
                : scoreValue.toFixed(2)} {/* Displaying two decimal places for better score visibility */}
            </span>
          </div>
          <div className="flex items-center gap-1 text-stone-400 text-xs uppercase tracking-wider">
            <Clock size={14} />
            <span>{recipe.minutes} min</span>
          </div>
        </div>

        <h2 className="text-2xl font-serif text-stone-800 leading-tight mb-3">
          {recipe.name}
        </h2>

        {recipe.description && (
          <p className="text-stone-600 text-sm leading-relaxed line-clamp-3 mb-4">
            {recipe.description}
          </p>
        )}

        <div className="flex gap-4 text-xs text-stone-500 border-t border-stone-100 pt-4">
          <div className="flex items-center gap-1">
            <Utensils size={14} />
            {ingredients.length} Ingredients
          </div>
          <div className="flex items-center gap-1">
            <ChefHat size={14} />
            {steps.length} Steps
          </div>
        </div>
      </div>

      {/* Expanded Content */}
      <div className={`bg-stone-50 transition-all duration-500 ease-in-out overflow-hidden ${expanded ? 'max-h-[800px] opacity-100' : 'max-h-0 opacity-0'}`}>
        {/* Scrollable Container Added: max-h-[700px] overflow-y-auto */}
        <div className="p-6 pt-2 space-y-6 border-t border-stone-200/50 max-h-[700px] overflow-y-auto">
          <div>
            <h3 className="font-serif text-lg text-stone-800 mb-3 flex items-center gap-2">
              <Leaf size={16} className="text-green-600" /> Ingredients
            </h3>
            <ul className="grid grid-cols-1 gap-2">
              {ingredients.map((ing, i) => (
                <li key={i} className="text-sm text-stone-600 flex items-start gap-2">
                  <span className="w-1.5 h-1.5 rounded-full bg-green-400 mt-1.5 shrink-0"></span>
                  {ing}
                </li>
              ))}
            </ul>
          </div>

          <div>
            <h3 className="font-serif text-lg text-stone-800 mb-3 flex items-center gap-2">
              <Flame size={16} className="text-orange-500" /> Instructions
            </h3>
            <ol className="space-y-3">
              {steps.map((st, i) => (
                <li key={i} className="text-sm text-stone-600 flex gap-3">
                  <span className="font-serif font-bold text-stone-300 text-lg leading-none">{i + 1}</span>
                  <span className="leading-relaxed">{st}</span>
                </li>
              ))}
            </ol>
          </div>
        </div>
      </div>

      {/* Toggle Button */}
      <button 
        onClick={() => setExpanded(!expanded)}
        className="w-full p-3 text-sm font-medium text-stone-500 hover:text-stone-800 hover:bg-stone-50 transition-colors border-t border-stone-100 flex justify-center items-center gap-2"
      >
        {expanded ? (
          <>Collapse Recipe <ChevronUp size={16} /></>
        ) : (
          <>View Full Recipe <ChevronDown size={16} /></>
        )}
      </button>
    </div>
  );
}